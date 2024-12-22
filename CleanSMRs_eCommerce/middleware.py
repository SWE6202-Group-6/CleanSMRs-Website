from django.shortcuts import redirect
from django.urls import reverse

from .models import UserOTP


class TwoFactorAuthenticationMiddleware:
    """Middleware to enforce two-factor authentication for users."""

    EXCLUDED_PATHS = [
        reverse("setup_2fa"),
        reverse("logout"),
        reverse("verify_otp"),
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # We only want to trigger this if the user is authenticated and has
        # activated their account.
        if request.user.is_authenticated and request.user.is_active:
            # For the time being, only Site Users (created through registration)
            # will be required to use 2FA. We can add this to other groups and
            # admin users later.
            if request.user.groups.filter(name="Site User").exists():
                try:
                    # Attempt to get the user's OTP secret record.
                    user_otp = UserOTP.objects.get(user=request.user)
                    if (
                        user_otp.validated_at is None
                        and request.path not in self.EXCLUDED_PATHS
                    ):
                        # If the user has not yet validated their OTP, redirect
                        # them to the setup page.
                        return redirect(reverse("setup_2fa"))
                    elif (
                        user_otp.validated_at is not None
                        and not request.session.get("otp_verified", False)
                    ):
                        # If the user has validated their OTP but has not yet
                        # provided an OTP code in the session, redirect them to
                        # the verification page if they're not already on it.
                        if request.path != reverse("verify_otp"):
                            return redirect(reverse("verify_otp"))
                except UserOTP.DoesNotExist:
                    # If the user does not have an OTP secret, redirect them to
                    # the setup page if they're not already on it.
                    if request.path != reverse("setup_2fa"):
                        return redirect(reverse("setup_2fa"))

        response = self.get_response(request)
        return response
