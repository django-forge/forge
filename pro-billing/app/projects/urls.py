from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path(
        "detail/<uuid:uuid>/checkout/",
        views.ProjectCheckoutView.as_view(),
        name="checkout",
    ),
    path(
        "detail/<uuid:uuid>/portal/",
        views.ProjectPortalView.as_view(),
        name="portal",
    ),
    path(
        "detail/<uuid:uuid>/terms/",
        views.ProjectTermsView.as_view(),
        name="terms",
    ),
    path(
        "detail/<uuid:uuid>/token/",
        views.ProjectTokenView.as_view(),
        name="token",
    ),
    path("create/", views.ProjectCreateView.as_view(), name="create"),
    path("", views.ProjectListView.as_view(), name="list"),
]
