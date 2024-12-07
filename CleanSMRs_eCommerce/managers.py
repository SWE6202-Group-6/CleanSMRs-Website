"""Definition of custom managers."""

from django.contrib.auth.base_user import BaseUserManager


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
