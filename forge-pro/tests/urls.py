from django.urls import path
from django.views.generic import TemplateView


class ErrorView(TemplateView):
    template_name = "base.html"

    def get_context_data(self, **kwargs):
        raise Exception("Test!")


urlpatterns = [
    path("error/", ErrorView.as_view()),
]
