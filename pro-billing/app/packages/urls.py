from django.urls import path

from . import views

app_name = "packages"

urlpatterns = [
    path(
        "<slug:name>/<str:filename>",  # No slash (IsADirectory error in Poetry)
        views.PypiPackageFilenameView.as_view(),
        name="pypi_filename",
    ),
    path("<slug:name>/", views.PypiPackageDetailView.as_view(), name="pypi_detail"),
    path("", views.PypiPackageListView.as_view()),
]
