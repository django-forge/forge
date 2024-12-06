import base64
import logging

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponse, StreamingHttpResponse
from django.utils.functional import cached_property
from django.views.generic import DetailView, ListView

from github import get_github_session
from projects.models import Project
from users.models import User

from .models import Package

logger = logging.getLogger(__name__)


def is_authenticated_user(http_username, http_password):
    try:
        user = User.objects.get(username=http_username, packages_token=http_password)
    except (User.DoesNotExist, ValidationError):
        # Invalid uuids can throw a validation error
        return False

    has_active_projects = Project.objects.filter(
        status="active",
        team_id__in=user.teams.values_list("id", flat=True),
    ).exists()

    return has_active_projects


def is_authenticated_project(http_username, http_password):
    try:
        Project.objects.get(
            name=http_username, packages_token=http_password, status="active"
        )
    except (Project.DoesNotExist, ValidationError):
        # Invalid uuids can throw a validation error
        return False

    return True


def is_authenticated(request):
    if request.user.is_authenticated:
        return True

    auth_header = request.META.get("HTTP_AUTHORIZATION", "")
    if auth_header:
        auth_type, auth_value = auth_header.split(" ", 1)
        if auth_type == "Basic":
            username, password = (
                base64.b64decode(auth_value).decode("utf-8").split(":", 1)
            )
            if username and password:
                # Can authenticate as a user (development)
                if is_authenticated_user(username, password):
                    logger.info(f"packages_auth username={username}")
                    return True

                # Or as a project (deployment)
                if is_authenticated_project(username, password):
                    logger.info(f"packages_auth project={username}")
                    return True

    return False


class PypiPackageListView(ListView):
    model = Package
    template_name = "packages/pypi_list.html"

    def get(self, request, *args, **kwargs):
        if not is_authenticated(request):
            return HttpResponse("Unauthorized", status=401)

        return super().get(request, *args, **kwargs)


class PypiPackageDetailView(DetailView):
    model = Package
    template_name = "packages/pypi_detail.html"
    slug_field = "name"
    slug_url_kwarg = "name"

    def get(self, request, *args, **kwargs):
        if not is_authenticated(request):
            return HttpResponse("Unauthorized", status=401)

        return super().get(request, *args, **kwargs)

    @cached_property
    def github_session(self):
        return get_github_session()

    @cached_property
    def github_assets(self):
        repo_full_name = self.get_object().repo_full_name
        cache_key = f"{repo_full_name}:assets"

        # Use the cached assets if we have them
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        response = self.github_session.get(
            f"https://api.github.com/repos/{repo_full_name}/releases",
            params={"per_page": 100},
        )
        response.raise_for_status()

        assets = []

        for release in response.json():
            for asset in release["assets"]:
                assets.append(
                    {
                        "url": asset["browser_download_url"],
                        "filename": asset["name"],
                        "api_url": asset["url"],
                    }
                )

        # Cache for 5 minutes across requests
        cache.set(cache_key, assets, timeout=60 * 5)

        return assets

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assets"] = self.github_assets
        return context


class PypiPackageFilenameView(PypiPackageDetailView):
    def get(self, request, *args, **kwargs):
        if not is_authenticated(request):
            return HttpResponse("Unauthorized", status=401)

        try:
            asset = [
                x
                for x in self.github_assets
                if x["filename"] == self.kwargs["filename"]
            ][0]
        except IndexError:
            raise Http404("File not found")

        response = self.github_session.get(
            asset["api_url"],
            headers={"Accept": "application/octet-stream"},
            stream=True,
        )

        return StreamingHttpResponse(
            response.raw,
            content_type=response.headers.get("content-type"),
            status=response.status_code,
            reason=response.reason,
            headers={
                "Content-Disposition": response.headers.get("content-disposition"),
                "Content-Length": response.headers.get("content-length"),
                "Last-Modified": response.headers.get("last-modified"),
                "ETag": response.headers.get("etag"),
            },
        )
