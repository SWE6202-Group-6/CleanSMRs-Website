"""Custom authentication-related functionality."""

from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_verification_token(user, token, base_url):
    """Generates and sends an email verification token to the specified user.

    Args:
        user (CustomUser): The new user to send the verification link to.
        token (str): The verification token to send.
        base_url (str): The site base domain to use in the verification link.

    Returns:
        bool: True if the email was sent successfully, otherwise False.
    """
    subject = "CleanSMRs: Activate your account"
    message = render_to_string(
        "activation_email.html",
        {
            "name": user.get_full_name(),
            "base_url": base_url,
            "token": token,
        },
    )
    email = EmailMessage(subject, message, to=[user.email])

    return email.send()
