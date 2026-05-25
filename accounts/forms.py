"""Authentication forms for approval-gated login."""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

User = get_user_model()

_BASE_INPUT_CLASS = (
    "block w-full rounded-md border border-slate-300 bg-white px-3 py-2 "
    "text-sm text-slate-800 placeholder:text-slate-400 "
    "focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-200"
)


class ApprovedUserAuthenticationForm(AuthenticationForm):
    """
    Login form that allows only approved (active) users.

    Inactive accounts are treated as "pending administrator approval" and
    receive a clear message instead of the generic "invalid credentials".
    """

    error_messages = {
        **AuthenticationForm.error_messages,
        "inactive": "This account is pending administrator approval.",
        "invalid_login": "Incorrect username or password.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": _BASE_INPUT_CLASS, "autocomplete": "username", "placeholder": "Username"}
        )
        self.fields["password"].widget.attrs.update(
            {"class": _BASE_INPUT_CLASS, "autocomplete": "current-password", "placeholder": "Password"}
        )

    def clean(self):
        """
        Override the base flow so an existing-but-inactive user is rejected
        with a dedicated "pending approval" message rather than the generic
        invalid-credentials response.
        """
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            try:
                candidate = User._default_manager.get_by_natural_key(username)
            except User.DoesNotExist:
                candidate = None

            if candidate is not None and candidate.check_password(password) and not candidate.is_active:
                raise ValidationError(self.error_messages["inactive"], code="inactive")

        return super().clean()

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(self.error_messages["inactive"], code="inactive")
