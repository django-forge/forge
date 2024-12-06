from django.views.generic import UpdateView
from views import BaseLoggedInMixin

from .models import User


class MyAccountView(BaseLoggedInMixin, UpdateView):
    html_title = "My account"
    model = User
    fields = ("username", "email", "first_name", "last_name")
    success_url = "."

    def get_object(self, queryset=None):
        return self.request.user
