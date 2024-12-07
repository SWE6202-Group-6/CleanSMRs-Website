"""Custom token-related functionality."""

from django.contrib.auth.tokens import PasswordResetTokenGenerator


class ActivationTokenGenerator(PasswordResetTokenGenerator):
    """Custom activation token generator class."""

    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.is_active}"


activation_token = ActivationTokenGenerator()
