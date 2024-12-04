"""Model definitions for the website."""

from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import CustomUserManager

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
