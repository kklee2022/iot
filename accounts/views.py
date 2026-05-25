"""Authentication views for the IoT platform."""
from django.contrib.auth.views import LoginView, LogoutView

from .forms import ApprovedUserAuthenticationForm


class ApprovedUserLoginView(LoginView):
    """Login view that only admits approved (active) users."""

    template_name = "accounts/login.html"
    authentication_form = ApprovedUserAuthenticationForm
    redirect_authenticated_user = True


class PlatformLogoutView(LogoutView):
    """Logout view that always returns to the login page."""

    http_method_names = ["get", "post", "options"]
