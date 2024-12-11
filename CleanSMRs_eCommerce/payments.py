import uuid

import stripe
from django.conf import settings

from .models import CustomUser, Order, Product, Subscription

# Get the Stripe API key from settings.
stripe.api_key = settings.STRIPE_SECRET_KEY


def process_order(session_id):
    """Process an order after a successful Stripe checkout session.

    Args:
        session_id (str): The ID of the Stripe checkout session.

    Returns:
        bool: True if the order was processed successfully (i.e., payment was
        completed and the order was created), False otherwise.
    """

    # Get the checkout session from Stripe using the checkout session ID.
    checkout_session = stripe.checkout.Session.retrieve(session_id)

    # We only want to create the order and subscription if the payment was
    # successful.
    #
    # TODO: This should really be a subscription rather than a one-off product,
    # but due to time constraints it's implemented as a one-off product for now
    # and renewal isn't supported - after expiry, a user must purchase a new
    # subscription.
    if checkout_session.payment_status == "paid":
        product_id = checkout_session.metadata["product_id"]
        user_id = checkout_session.metadata["user_id"]

        product = Product.objects.get(pk=product_id)
        user = CustomUser.objects.get(pk=user_id)

        # Create a unique order.
        order_number = str(uuid.uuid4())

        # Create the order record and set it as completed. Ordinarily we'd
        # create this at a different point and set it pending, but for the sake
        # of time and simplicity, it's an all-in-one operation here.
        order = Order.objects.create(
            product=product,
            user=user,
            order_number=order_number,
            status="completed",
            # Stripe stores the amount in the smallest unit (e.g. pence, cents).
            order_total=checkout_session.amount_total / 100,
        )

        # If the product is a data access product, create a subscription for the
        # user.
        if product.type == "data_access":
            Subscription.objects.create_subscription(
                user=user, plan=product.plan, order=order
            )

        return True

    return False
