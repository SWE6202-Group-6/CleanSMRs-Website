"""Tests related to the payment functionality."""

import json
from unittest.mock import MagicMock, patch

import stripe
from django.test import RequestFactory, TestCase

from CleanSMRs_eCommerce.payments import process_order
from CleanSMRs_eCommerce.views import stripe_webhook_handler


class ProcessOrderTest(TestCase):
    """Tests for the Stripe order processor."""

    @patch("CleanSMRs_eCommerce.payments.stripe.checkout.Session.retrieve")
    @patch("CleanSMRs_eCommerce.payments.Product")
    @patch("CleanSMRs_eCommerce.payments.CustomUser")
    @patch("CleanSMRs_eCommerce.payments.Order")
    @patch("CleanSMRs_eCommerce.payments.Subscription")
    def test_process_order_success(
        self,
        mock_subscription,
        mock_order,
        mock_custom_user,
        mock_product,
        mock_retrieve,
    ):
        """Tests processing an order when the status is paid."""

        # Mock the Stripe checkout session
        mock_session = MagicMock()
        mock_session.payment_status = "paid"
        mock_session.metadata = {"product_id": 1, "user_id": 1}
        mock_session.amount_total = 1000  # Amount in cents
        mock_retrieve.return_value = mock_session

        mock_product.objects.get.return_value = MagicMock(
            type="data_access", plan="basic"
        )
        mock_custom_user.objects.get.return_value = MagicMock()

        result = process_order("session_id")

        self.assertTrue(result)
        mock_retrieve.assert_called_once_with("session_id")
        mock_product.objects.get.assert_called_once_with(pk=1)
        mock_custom_user.objects.get.assert_called_once_with(pk=1)
        mock_order.objects.create.assert_called_once()
        mock_subscription.objects.create_subscription.assert_called_once()

    @patch("CleanSMRs_eCommerce.payments.stripe.checkout.Session.retrieve")
    def test_process_order_payment_failed(self, mock_retrieve):
        # Mock the Stripe checkout session with failed payment
        mock_session = MagicMock()
        mock_session.payment_status = "unpaid"
        mock_retrieve.return_value = mock_session

        result = process_order("session_id")

        self.assertFalse(result)
        mock_retrieve.assert_called_once_with("session_id")


class StripeWebhookHandlerTests(TestCase):
    """Tests for the Stripe webhook handler. Simulating the success path is
    a bit tricky and largely covered by the above tests, so these tests focus
    on the unhappy path."""

    def setUp(self):
        """Sets up the RequestFactory."""

        self.factory = RequestFactory()
        self.url = "/stripe_webhook/"

    @patch("CleanSMRs_eCommerce.views.settings.STRIPE_ENABLED", True)
    @patch(
        "CleanSMRs_eCommerce.views.settings.STRIPE_WEBHOOK_SECRET",
        "whsec_testsecret",
    )
    @patch("CleanSMRs_eCommerce.views.stripe.Webhook.construct_event")
    def test_stripe_webhook_handler_value_error(self, mock_construct_event):
        """Tests the handler when a ValueError is raised to ensure that the API
        returns a 400 status code to Stripe."""

        mock_construct_event.side_effect = ValueError
        request = self.factory.post(
            self.url, data=json.dumps({}), content_type="application/json"
        )
        request.META["HTTP_STRIPE_SIGNATURE"] = "test_signature"

        response = stripe_webhook_handler(request)
        self.assertEqual(response.status_code, 400)

    @patch("CleanSMRs_eCommerce.views.settings.STRIPE_ENABLED", True)
    @patch(
        "CleanSMRs_eCommerce.views.settings.STRIPE_WEBHOOK_SECRET",
        "whsec_testsecret",
    )
    @patch("CleanSMRs_eCommerce.views.stripe.Webhook.construct_event")
    def test_stripe_webhook_handler_signature_verification_error(
        self, mock_construct_event
    ):
        """Tests the handler when a SignatureVerificationError is raised to
        ensure that the API returns a 400 status code to Stripe."""

        mock_construct_event.side_effect = (
            stripe.error.SignatureVerificationError(
                "Invalid signature", "header", "payload"
            )
        )
        request = self.factory.post(
            self.url, data=json.dumps({}), content_type="application/json"
        )
        request.META["HTTP_STRIPE_SIGNATURE"] = "test_signature"

        response = stripe_webhook_handler(request)
        self.assertEqual(response.status_code, 400)
