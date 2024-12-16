"""Model definitions for the website."""

import uuid
from datetime import datetime, timezone

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError

from .managers import (
    ActivationTokenManager,
    CustomUserManager,
    SubscriptionManager,
)

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
        return f"{self.first_name} {self.last_name} ({self.email})"


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


class Plan(models.Model):
    """Model that represents a subscription plan."""

    PLAN_CHOICES = [
        (12, "1 year"),
        (24, "2 years"),
        (36, "3 years"),
    ]

    name = models.CharField(max_length=255, blank=True, null=False)
    duration_months = models.IntegerField(
        blank=True, choices=PLAN_CHOICES, null=False, verbose_name="Duration"
    )

    objects = models.Manager()

    def __str__(self):
        return str(self.name)


class Product(models.Model):
    """Model that represents a product for sale on the website."""

    PRODUCT_TYPES = [
        ("physical_product", "Physical Product"),
        ("data_access", "Data Access"),
    ]

    name = models.CharField(max_length=255, blank=True, null=False)
    description = models.TextField(blank=True, null=False)
    type = models.CharField(
        max_length=20, choices=PRODUCT_TYPES, blank=True, null=False
    )
    price = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=False
    )
    image_path = models.CharField(max_length=255, blank=True, null=True)
    plan = models.OneToOneField(
        Plan, on_delete=models.CASCADE, null=True, verbose_name="Plan"
    )
    stripe_price_id = models.CharField(
        max_length=50, blank=True, null=False, verbose_name="Stripe Price ID"
    )

    def clean(self):
        if self.type == "data_access" and self.plan_id is None:
            raise ValidationError("Data access products must have a plan ID.")

    def __str__(self):
        return str(self.name)


class Order(models.Model):
    """Model that represents an order placed by a user."""

    ORDER_STATUSES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    order_number = models.CharField(max_length=40, blank=True, null=False)
    date_placed = models.DateTimeField(auto_now_add=True, null=False)
    status = models.CharField(
        max_length=20, choices=ORDER_STATUSES, blank=True, null=False
    )
    order_total = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=False
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=False, verbose_name="Product"
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)

    objects = models.Manager()

    def save(self, *args, **kwargs):
        """Generates an order number using a UUID if one is not provided."""
        if not self.order_number:
            self.order_number = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.order_number)


class Subscription(models.Model):
    """Model that represents a subscription to a data access plan."""

    plan = models.ForeignKey(
        Plan, on_delete=models.CASCADE, null=False, verbose_name="Plan"
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=False, verbose_name="User"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, null=False, verbose_name="Order"
    )
    start_date = models.DateTimeField(auto_now_add=True, null=False)
    end_date = models.DateTimeField(null=False)

    objects = SubscriptionManager()
