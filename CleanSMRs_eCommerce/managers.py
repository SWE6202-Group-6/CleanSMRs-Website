"""Definition of custom managers."""

from datetime import datetime, timedelta, timezone

from django.contrib.auth.base_user import BaseUserManager
from django.db import models

from .tokens import ActivationTokenGenerator


class CustomUserManager(BaseUserManager):
    """A custom user manager for the application to use the email as the
    username rather than having both username and email fields."""

    def create_user(self, email, password, **fields):
        """Creates a new user with the provided details.

        Args:
            email (str): The user's email address.
            password (str): The user's password.

        Raises:
            ValueError: If the email address is not provided.

        Returns:
            CustomUserManager: The newly created user.
        """

        if not email:
            raise ValueError("The email field is required.")

        email = self.normalize_email(email)
        user = self.model(email=email, **fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password, **fields):
        """Creates a new superuser with the provided details.

        Args:
            email (str): The superuser's email address.
            password (str): The superuser's password.

        Returns:
            CustomUserManager: The newly created superuser.
        """

        fields.setdefault("is_staff", True)
        fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **fields)


class ActivationTokenManager(models.Manager):
    """Custom manager for ActivationToken model."""

    def create_token(self, user):
        """Creates a new instance of an ActivationToken.

        Args:
            user (CustomUser): The user to generate an activation token for.

        Returns:
            ActivationToken: The newly-created activation token.
        """
        token = ActivationTokenGenerator().make_token(user)
        activation_token = self.create(token=token, user=user)
        return activation_token


class SubscriptionManager(models.Manager):
    """Custom manager for Subscription model."""

    def create_subscription(self, user, plan, order):
        """Creates a new subscription for a user.

        Args:
            user (CustomUser): The user to create the subscription for.
            plan (Plan): The type of plan to use for the subscription.
            order (Order): The order associated with the subscription.
        """

        subscription = self.create(
            user=user,
            plan=plan,
            order=order,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
            + timedelta(weeks=(plan.duration_months / 12) * 52),
        )

        return subscription
