"""Model definitions for the website."""

from datetime import datetime, timezone

from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import ActivationTokenManager, CustomUserManager

# Create your models here.


class CustomUser(AbstractUser):
    """Custom user class that uses the email address as the username."""

    username = None
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=255, blank=True, null=False)
    city = models.CharField(max_length=255, blank=True, null=False)
    country = models.CharField(max_length=255, blank=True, null=False)
    postal_code = models.CharField(max_length=20, blank=True, null=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "address",
        "country",
        "postal_code",
    ]

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class ActivationToken(models.Model):
    """Model that represents an activation token for a user account."""

    token = models.CharField(max_length=64, primary_key=True, null=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    activated_at = models.DateTimeField(default=None, null=True)

    objects = ActivationTokenManager()

    def check_token(self, token):
        """Checks whether the provided token matches this token.

        Args:
            token (str): The token to check.

        Returns:
            bool: True if the tokens match, otherwise false.
        """

        return str(self.token) == token

    def set_activated(self):
        """Marks the token as activated at the current time."""
        self.activated_at = datetime.now(timezone.utc)

    def __str__(self):
        return str(self.token)
