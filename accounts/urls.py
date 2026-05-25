"""URL routes for the accounts app."""
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.ApprovedUserLoginView.as_view(), name="login"),
    path("logout/", views.PlatformLogoutView.as_view(), name="logout"),
]
