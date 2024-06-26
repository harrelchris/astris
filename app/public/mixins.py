from django.conf import settings
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy


class LoggedInRedirectMixin(AccessMixin):
    """Verify that the current user is not authenticated."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse_lazy(settings.LOGIN_REDIRECT_URL))
        return super().dispatch(request, *args, **kwargs)
