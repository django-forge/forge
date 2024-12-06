from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from forms import SignupForm
from teams.models import Team, TeamMembership, TeamRoles


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


class BaseLoggedInMixin(LoginRequiredMixin, HTMLTitleMixin):
    html_title_suffix = " | Built with Forge"


class HomeView(BaseLoggedInMixin, TemplateView):
    html_title = "Home"
    template_name = "home.html"


class SignupView(CreateView):
    html_title = "Sign up"
    form_class = SignupForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()

        # Create a "Personal" team for the new user
        team = Team.objects.create(name=user.username)
        TeamMembership.objects.create(user=user, team=team, role=TeamRoles.ADMIN)

        return super().form_valid(form)
