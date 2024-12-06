"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

import views
from users.views import SignupView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("impersonate/", include("forgeimpersonate.urls")),
    path("signup/", SignupView.as_view(), name="signup"),
    path("quickstart.py", views.QuickstartRedirectView.as_view()),
    path("pypi/", include("packages.urls")),
    path("", include("django.contrib.auth.urls")),
    path("", include("projects.urls")),
    path("stripe-webhook/", views.StripeWebhookView.as_view()),
    path(
        "favicon.ico",
        RedirectView.as_view(url="https://www.forgepackages.com/favicon.ico"),
    ),
]
