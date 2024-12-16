"""View function definitions for the website."""

import stripe
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import (
    BadRequest,
    ObjectDoesNotExist,
    PermissionDenied,
)
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import Resolver404
from django.views.decorators.csrf import csrf_exempt

from .auth import send_verification_token
from .forms import RegistrationForm
from .models import ActivationToken, CustomUser, Product
from .payments import process_order

# Set the Stripe API key.
stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.


def index(request):
    """Renders the index page.

    Args:
        request (Request): The request object.

    Returns:
        HttpResponse: A HTTP response rendering the index template.
    """

    return render(request, "index.html")


def register(request):
    """Renders the registration page and handles registration requests.

    Args:
        request (Request): The request object.

    Returns:
        HttpResponse: A HTTP response rendering the registration template.
    """

    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Disable the user until we verify their email.
            user.is_active = False
            user.save()

            # Add the user to the default group.
            default_group = Group.objects.get(name="Site User")
            default_group.user_set.add(user)

            if settings.EMAIL_ENABLED is False:
                # If email is disabled, we can't send a verification email, so
                # we should make sure the user is activated.
                user.is_active = True
                user.save()
            else:
                domain = get_current_site(request).domain
                protocol = "https" if request.is_secure() else "http"
                base_url = f"{protocol}://{domain}"
                activation_token = ActivationToken.objects.create_token(user)
                activation_token.save()
                send_verification_token(user, str(activation_token), base_url)

            return render(
                request,
                "generic_message.html",
                {
                    "heading": "Registration Successful",
                    "message": "Your account has been successfully created. Please check your email to activate your account.",
                    "link": "login",
                    "link_text": "Log in",
                },
            )
    else:
        form = RegistrationForm()

    status_code = 400 if form.errors else 200
    return render(request, "register.html", {"form": form}, status=status_code)


def log_in(request):
    """Renders the login view and handles login requests.

    Args:
        request (Request): The request object.

    Returns:
        HttpResponse: A HTTP response rendnering the login template.
    """

    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("index")
    else:
        form = AuthenticationForm()

    status_code = 400 if form.errors else 200
    return render(request, "login.html", {"form": form}, status=status_code)


@login_required
def log_out(request):
    """Logs out the current user.

    Args:
        request (Request): The request object.

    Returns:
        HttpResponse: A HTTP response redirecting to the index page.
    """

    logout(request)
    return redirect("index")


def products_view(request):
    """Renders the products view with all products retrieved from the database.

    Args:
        request (Request): The request object.

    Returns:
        HttpResponse: An HTTP response rendering the products template.
    """

    products = Product.objects.all()
    return render(request, "products.html", {"products": products})


def product_view(request, product_id):
    """Renders a single product.

    Args:
        request (Request): The request object.
        product_id (int): The ID of the product to view.

    Returns:
        HttpResponse: An HTTP response rendering the products template.
    """

    product = Product.objects.get(pk=product_id)
    return render(request, "product.html", {"product": product})


@login_required
def create_checkout_session(request, product_id):
    """Creates a new Stripe checkout session for the given product and redirects
    the user to the Stripe purchase page.

    Args:
        request (Request): The request object.
        product_id (int): The ID of the product to purchase.

    Returns:
        HttpResponse: An HTTP response redirecting the user to the Stripe.
    """

    product = Product.objects.get(pk=product_id)
    user = CustomUser.objects.get(pk=request.user.id)

    # Create a Stripe checkout session.
    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                # This identifies the product in Stripe.
                "price": product.stripe_price_id,
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=f"{settings.STRIPE_SUCCESS_URL}",
        cancel_url=f"{settings.STRIPE_CANCEL_URL}",
        # Ensure that the session has an ID that we can use to look up the order
        metadata={
            "product_id": product.id,
            "user_id": user.id,
        },
    )

    return redirect(checkout_session.url, code=303)


@csrf_exempt
def stripe_webhook_handler(request):
    """Handles incoming webhook requests from Stripe for processing purchase
    updates. This will be called by Stripe when a purchase is completed or when
    an asynchronous payment is successful after the purchase.

    Args:
        request (Request): The request object.

    Returns:
        HttpResponse: An HTTP response indicating success or failure for Stripe.
    """

    if not settings.STRIPE_ENABLED:
        # For local testing without purchasing enabled, we can just return 200
        # to indicate success and continue without processing.
        return HttpResponse(status=200)

    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if (
        event["type"] == "checkout.session.completed"
        or event["type"] == "checkout.session.async_payment_succeeded"
    ):
        process_order(event["data"]["object"]["id"])

    return HttpResponse(status=200)


@login_required
def checkout_success(request):
    """View that renders the success page after purchasing an item.

    Args:
        request (Request): The request object.

    Returns:
        HttpResponse: An HttpResponse rendering the success page.
    """

    return render(
        request,
        "generic_message.html",
        {
            "heading": "Order Complete",
            "message": "Your order has been successfully completed.",
            "link": "index",
            "link_text": "Return to the homepage",
        },
    )


@login_required
def checkout_cancel(request):
    """View that renders the cancellation page after cancelling the purchase
    process.

    Args:
        request (Request): The request object.

    Returns:
        HttpResponse: An HttpResponse rendering the cancellation page.
    """

    return render(
        request,
        "generic_message.html",
        {
            "heading": "Cancelled",
            "message": "Ordering cancelled. You won't be charged.",
            "link": "index",
            "link_text": "Return to the homepage",
        },
    )


def activate(request, token):
    """Attempts to activate a user's account using an activation token.

    Args:
        request (Request): The request object.
        encoded_id (str): A Base64-encoded user ID.
        token (str): An activation token.

    Returns:
        HttpResponse: A HTTP response with a redirect.
    """

    # If the user is logged in, they must have already activated their account.
    if request.user.is_authenticated:
        return redirect("index")

    # Check to see if the activation token exists in the database.
    try:
        activation_token = ActivationToken.objects.get(pk=token)
        user = activation_token.user
    except (ValueError, ObjectDoesNotExist):
        user = None

    if user is None:
        raise BadRequest("Invalid activation token.")

    if activation_token.activated_at is not None:
        # The token has already been activated.
        raise BadRequest("Invalid activation token.")

    if activation_token.check_token(token):
        # Activate the user.
        user.is_active = True
        user.save()

        # Mark the token as activated.
        activation_token.set_activated()
        activation_token.save()

        return render(
            request,
            "generic_message.html",
            {
                "heading": "Activation Successful",
                "message": "Your account has been successfully activated. You can now log in.",
                "link": "login",
                "link_text": "Log in",
            },
        )

    # Some other error occurred.
    raise BadRequest("Invalid activation token.")


def error_view(request, exception=None):
    """Renders a custom error page when an appropriate exception is thrown.

    Args:
        request (Request): The request object.
        exception (Exception): An exception.

    Returns:
        HttpResponse: An HTTP response that renders an error.
    """
    error_message = None

    if isinstance(exception, BadRequest):
        status_code = 400
    elif isinstance(exception, PermissionDenied):
        status_code = 403
        error_message = "You do not have permission to access this page."
    elif isinstance(exception, ObjectDoesNotExist) or isinstance(
        exception, Resolver404
    ):
        status_code = 404
        error_message = "The requested resource could not be found."
    else:
        status_code = 500
        error_message = "An error occurred while processing your request."

    return render(
        request,
        "error.html",
        {
            "error_message": (
                error_message if error_message is not None else str(exception)
            )
        },
        status=status_code,
    )
