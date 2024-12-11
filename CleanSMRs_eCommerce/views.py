"""View function definitions for the website."""

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import (
    BadRequest,
    ObjectDoesNotExist,
    PermissionDenied,
)
from django.shortcuts import redirect, render
from django.urls import Resolver404

from .auth import send_verification_token
from .forms import RegistrationForm
from .models import ActivationToken, CustomUser, Product

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
