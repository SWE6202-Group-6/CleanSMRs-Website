"""Custom authentication-related functionality."""

from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from .models import ActivationToken


def send_verification_token(user, base_url):
    """Generates and sends an email verification token to the specified user.

    Args:
        user (CustomUser): The new user to send the verification link to.
        base_url (str): The site base domain to use in the verification link.

    Returns:
        bool: True if the email was sent successfully, otherwise False.
    """
    activation_token = ActivationToken.objects.create_token(user)
    activation_token.save()

    subject = "CleanSMRs: Activate your account"
    message = render_to_string(
        "activation_email.html",
        {
            "name": user.get_full_name(),
            "base_url": base_url,
            "token": str(activation_token),
        },
    )
    email = EmailMessage(subject, message, to=[user.email])

    return email.send()
