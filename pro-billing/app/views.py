from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views import View

from forgegoogleanalytics.events import GoogleAnalyticsEvent
from forgestripe.views import StripeWebhookView

from projects.models import Project


class HTMLTitleMixin:
    html_title = ""
    html_title_prefix = ""
    html_title_suffix = ""
    html_title_required = True

    def get_html_title(self):
        """
        Return the class title attr by default,
        but can customize this by overriding
        """
        return self.html_title

    def get_html_title_required(self):
        return self.html_title_required

    def get_html_title_prefix(self):
        return self.html_title_prefix

    def get_html_title_suffix(self):
        return self.html_title_suffix

    def generate_html_title(self):
        title = self.get_html_title()

        if not title and self.get_html_title_required():
            raise ValueError("HTMLTitleMixin requires an html_title")

        return self.get_html_title_prefix() + title + self.get_html_title_suffix()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["html_title"] = self.generate_html_title()
        return context


class BaseLoggedInViewMixin(LoginRequiredMixin, HTMLTitleMixin):
    pass


class StripeWebhookView(StripeWebhookView):
    def handle_stripe_event(self, event):
        if event.type == "checkout.session.completed":
            project_uuid = event.data.object.client_reference_id
            project = Project.objects.get(uuid=project_uuid)
            project.stripe_id = event.data.object.subscription
            project.save()

            project.sync_stripe()

            project.invite_github_usernames()

        elif event.type == "customer.subscription.deleted":
            subscription_id = event.data.object.id
            project = Project.objects.get(stripe_id=subscription_id)
            project.stripe_id = ""
            project.save()

            project.sync_stripe()

            project.remove_github_usernames()


class QuickstartRedirectView(View):
    def get(self, request, *args, **kwargs):
        GoogleAnalyticsEvent(
            name="quickstart",
            params={
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            },
        ).send(request=request)
        return HttpResponseRedirect(
            "https://raw.githubusercontent.com/forgepackages/forge/master/quickstart.py"
        )
