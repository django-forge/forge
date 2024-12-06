from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils import timezone
from django.views import generic

import stripe
from forgestripe.views import StripeCheckoutView, StripePortalView

from views import BaseLoggedInViewMixin

from .models import Project


class ProjectQuerysetMixin:
    def get_queryset(self):
        team_ids = self.request.user.teams.values_list("id", flat=True)
        return super().get_queryset().filter(team_id__in=team_ids)


class ProjectDetailMixin(ProjectQuerysetMixin):
    model = Project
    slug_field = "uuid"
    slug_url_kwarg = "uuid"


class ProjectCreateView(BaseLoggedInViewMixin, generic.CreateView):
    model = Project
    fields = ["name"]
    html_title = "Start a new project"

    def form_valid(self, form):
        form.instance.team = self.request.user.teams.first()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("projects:terms", kwargs={"uuid": self.object.uuid})


class ProjectTokenView(BaseLoggedInViewMixin, ProjectDetailMixin, generic.DetailView):
    template_name = "projects/project_token.html"

    def get_html_title(self):
        return f"{self.object} token"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if not obj.is_active:
            raise PermissionDenied("Project is not active")

        return obj


class ProjectTermsView(BaseLoggedInViewMixin, ProjectDetailMixin, generic.UpdateView):
    fields = ["github_usernames"]
    template_name = "projects/project_terms.html"
    html_title = "License terms"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # For now we'll make this look like a single value field
        form.fields["github_usernames"].label = "GitHub username"
        form.fields["github_usernames"].widget.attrs["required"] = True
        form.fields[
            "github_usernames"
        ].help_text = "The user who will be invited to the private Forge repos."
        return form

    def form_valid(self, form):
        form.instance.terms_accepted_at = timezone.now()
        form.instance.terms_accepted_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("projects:checkout", kwargs={"uuid": self.object.uuid})


class ProjectCheckoutView(
    BaseLoggedInViewMixin, ProjectDetailMixin, StripeCheckoutView, generic.DetailView
):
    html_title = "Checkout"

    def get(self, request, *args, **kwargs):
        """Adding a get so we can redirect straight to checkout from other forms"""
        return self.get_redirect_response(request)

    def get_checkout_session_kwargs(self, request):
        project = self.get_object()

        redirect_url = request.build_absolute_uri("/")

        team = project.team
        team_stripe_info = {
            "name": team.name,
            "metadata": {"team_uuid": team.uuid},
        }

        if team.stripe_id:
            stripe.Customer.modify(team.stripe_id, **team_stripe_info)
            customer = team.stripe_id
        else:
            customer = stripe.Customer.create(**team_stripe_info)
            team.stripe_id = customer.id
            team.save()

        return {
            "customer": customer,
            "success_url": redirect_url + "?stripe=success",
            "cancel_url": redirect_url + "?stripe=cancel",
            "mode": "subscription",
            "client_reference_id": project.uuid,
            "payment_method_types": ["card"],
            "allow_promotion_codes": True,
            "line_items": [
                {
                    "price": settings.STRIPE_PRICE_ID,
                    "quantity": 1,
                }
            ],
        }


class ProjectPortalView(
    BaseLoggedInViewMixin, ProjectDetailMixin, StripePortalView, generic.DetailView
):
    html_title = "Portal"

    def get_portal_session_kwargs(self, request):
        project = self.get_object()

        return_url = request.build_absolute_uri("/")

        return {
            "customer": project.team.stripe_id,
            "return_url": return_url,
        }


class ProjectListView(BaseLoggedInViewMixin, ProjectQuerysetMixin, generic.ListView):
    model = Project
    context_object_name = "projects"
    html_title = "Projects"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "stripe" in self.request.GET:
            context["stripe_status"] = self.request.GET["stripe"]
        return context
