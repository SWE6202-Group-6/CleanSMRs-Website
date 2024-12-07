"""Custom token-related functionality."""

import binascii
import secrets

from django.contrib.auth.tokens import PasswordResetTokenGenerator


class ActivationTokenGenerator(PasswordResetTokenGenerator):
    """Custom activation token generator class."""

    def _make_hash_value(self, user, timestamp):
        token = binascii.hexlify(secrets.token_bytes(32)).decode()
        return f"{token}{user.pk}{timestamp}"


activation_token = ActivationTokenGenerator()
