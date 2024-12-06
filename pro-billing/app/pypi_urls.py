from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("", include("packages.urls")),
    path(
        "favicon.ico",
        RedirectView.as_view(url="https://www.forgepackages.com/favicon.ico"),
    ),
]
