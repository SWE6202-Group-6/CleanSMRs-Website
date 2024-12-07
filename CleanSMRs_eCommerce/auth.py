"""Custom authentication-related functionality."""

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import activation_token


def send_verification_token(user, base_url):
    """Generates and sends an email verification token to the specified user.

    Args:
        user (CustomUser): The new user to send the verification link to.
        base_url (str): The site base domain to use in the verification link.

    Returns:
        bool: True if the email was sent successfully, otherwise False.
    """
    token = activation_token.make_token(user)

    subject = "CleanSMRs: Activate your account"
    message = render_to_string(
        "activation_email.html",
        {
            "name": user.get_full_name(),
            "base_url": base_url,
            "user_id": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": token,
        },
    )
    email = EmailMessage(subject, message, to=[user.email])

    return email.send()
