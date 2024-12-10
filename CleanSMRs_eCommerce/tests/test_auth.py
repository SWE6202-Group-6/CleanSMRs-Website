"""Tests related to registration, login and email confirmation."""

from datetime import datetime, timezone
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from CleanSMRs_eCommerce.models import ActivationToken

CustomUser = get_user_model()


class RegisterViewTest(TestCase):
    """Tests for the registration view."""

    def setUp(self):
        self.client = Client()

    @patch("CleanSMRs_eCommerce.views.get_current_site")
    @patch("CleanSMRs_eCommerce.views.send_verification_token")
    @override_settings(EMAIL_ENABLED=True)
    def test_register_view_post_success(
        self, mock_send_verification_token, mock_get_current_site
    ):
        """Tests that registration with valid details is successful and sends a
        verification email with a token to the user.

        Args:
            mock_settings: Mock for the Django settings.
            mock_send_verification_token: Mock for the send_verification_token function.
            mock_get_current_site: Mock for the get_current_site function.
        """

        mock_get_current_site.return_value.domain = "example.com"

        response = self.client.post(
            reverse("register"),
            {
                "first_name": "New",
                "last_name": "User",
                "email": "newuser@example.com",
                "password1": "P@$$w0rd!",
                "password2": "P@$$w0rd!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "generic_message.html")
        mock_send_verification_token.assert_called_once()

        # Confirm that a user was created and is inactive.
        user = CustomUser.objects.get(email="newuser@example.com")
        self.assertIsNotNone(user)
        self.assertFalse(user.is_active)

        # Check that an activation token was created for the user.
        activation_token = ActivationToken.objects.get(user=user)
        self.assertIsNotNone(activation_token)
        self.assertIsNone(activation_token.activated_at)

    def test_register_view_post_invalid(self):
        """Tests that registration with invalid details does not create a
        new user and returns the registration form with errors."""

        response = self.client.post(
            reverse("register"),
            {
                "first_name": "New",
                "last_name": "User",
                "email": "invalid-email",
                "password1": "P@$$w0rd!",
                "password2": "different_password",
            },
        )

        # Assert that the response is a Bad Request status code and the
        # registration form is rendered.
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "register.html")

        # Confirm that no user was created.
        with self.assertRaises(CustomUser.DoesNotExist):
            CustomUser.objects.get(email="invalid-email")

        # Check that the form contains errors for the invalid fields.
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("email", form.errors)
        self.assertIn("password2", form.errors)

    @patch("CleanSMRs_eCommerce.views.send_verification_token")
    @override_settings(EMAIL_ENABLED=False)
    def test_register_view_post_email_disabled(
        self, mock_send_verification_token
    ):
        """Tests that registration with valid details is successful and the user
        is activated immediately if email is disabled for the website."""

        response = self.client.post(
            reverse("register"),
            {
                "first_name": "New",
                "last_name": "User",
                "email": "newuser@example.com",
                "password1": "P@$$w0rd!",
                "password2": "P@$$w0rd!",
            },
        )

        # Check that the response is a success status code, the generic
        # message template is rendered and no verification token email is sent.
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "generic_message.html")
        mock_send_verification_token.assert_not_called()

        # Confirm that a user was created and is active.
        user = CustomUser.objects.get(email="newuser@example.com")
        self.assertIsNotNone(user)
        self.assertTrue(user.is_active)

        # Check that no activation token was created for the user.
        with self.assertRaises(ObjectDoesNotExist):
            ActivationToken.objects.get(user=user)


class LoginViewTest(TestCase):
    """Tests for the login view."""

    def setUp(self):
        self.client = Client()

    def test_login_view_get(self):
        """Tests that the login view is rendered successfully when accessed
        via a GET request."""

        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

    def test_login_view_post_success(self):
        """Tests that a user can log in successfully with valid credentials."""

        user = CustomUser.objects.create_user(
            first_name="Test",
            last_name="User",
            email="testuser@example.com",
            password="P@$$w0rd!",
        )

        response = self.client.post(
            reverse("login"),
            {
                "username": user.email,
                "password": "P@$$w0rd!",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))

    def test_login_view_post_invalid_credentials(self):
        """Tests that login fails if credentials are invalid and that the form
        is returned with errors."""

        user = CustomUser.objects.create_user(
            first_name="Test",
            last_name="User",
            email="testuser@example.com",
            password="P@$$w0rd!",
        )

        response = self.client.post(
            reverse("login"),
            {
                "username": user.email,
                "password": "wrong-password",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "login.html")
        form = response.context["form"]
        self.assertTrue(form.errors)

    def test_login_view_post_user_not_activated(self):
        """Tests that login fails if the user account is not activated and
        the form is returned with errors."""

        user = CustomUser.objects.create_user(
            first_name="Test",
            last_name="User",
            email="testuser@example.com",
            password="P@$$w0rd!",
            is_active=False,
        )

        response = self.client.post(
            reverse("login"),
            {
                "username": user.email,
                "password": "P@$$w0rd!",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "login.html")
        form = response.context["form"]
        self.assertTrue(form.errors)


class ActivateViewTest(TestCase):
    """Tests for the account activation view."""

    def setUp(self):
        self.client = Client()

    def test_activate_view_get_valid_token(self):
        """Tests that the account activation view is rendered successfully and
        the user account is activated when a valid token is provided."""

        user = CustomUser.objects.create_user(
            first_name="Test",
            last_name="User",
            email="testuser@example.com",
            password="P@$$w0rd!",
        )

        activation_token = ActivationToken.objects.create_token(user)

        response = self.client.get(
            reverse("activate", kwargs={"token": activation_token.token})
        )

        db_user = CustomUser.objects.get(email=user.email)
        db_token = ActivationToken.objects.get(user=db_user)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "generic_message.html")
        self.assertTrue(db_user.is_active)
        self.assertIsNotNone(db_token.activated_at)

    def test_activate_view_get_invalid_token(self):
        """Tests that the account activation view returns a 400 error when an
        invalid token is provided."""

        user = CustomUser.objects.create_user(
            first_name="Test",
            last_name="User",
            email="testuser@example.com",
            password="P@$$w0rd!",
            is_active=False,
        )

        ActivationToken.objects.create_token(user)

        response = self.client.get(
            reverse("activate", kwargs={"token": "invalid-token"})
        )

        db_user = CustomUser.objects.get(email=user.email)
        db_token = ActivationToken.objects.get(user=db_user)

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "error.html")
        self.assertFalse(db_user.is_active)
        self.assertIsNone(db_token.activated_at)

    def test_activate_view_get_already_activated(self):
        """Tests that the account activation view returns a 400 error when an
        already activated token is provided."""

        user = CustomUser.objects.create_user(
            first_name="Test",
            last_name="User",
            email="testuser@example.com",
            password="P@$$w0rd!",
            is_active=True,
        )

        activation_token = ActivationToken.objects.create_token(user)
        activation_token.activated_at = datetime.now(timezone.utc)
        activation_token.save()

        response = self.client.get(
            reverse("activate", kwargs={"token": activation_token.token})
        )

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "error.html")
