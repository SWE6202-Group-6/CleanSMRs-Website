"""View function definitions for the website."""

from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect, render
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from .auth import send_verification_token
from .forms import RegistrationForm
from .tokens import activation_token

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

            # Make sure that the user isn't activated yet
            user.is_active = False
            user.save()

            domain = get_current_site(request).domain
            protocol = "https" if request.is_secure() else "http"
            base_url = f"{protocol}://{domain}"

            send_verification_token(user, base_url)

            return redirect("index")
    else:
        form = RegistrationForm()

    return render(request, "register.html", {"form": form})


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
            if not user.is_active:
                # TODO: Add a page for unactivated users.
                return redirect("index")

            login(request, user)
            return redirect("index")
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})


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


def activate(request, encoded_id, token):
    """Attempts to activate a user's account using an activation token.

    Args:
        request (Request): The request object.
        encoded_id (str): A Base64-encoded user ID.
        token (str): An activation token.

    Returns:
        HttpResponse: A HTTP response with a redirect.
    """

    if request.user.is_authenticated:
        return redirect("index")

    user_model = get_user_model()

    try:
        user_id = force_str(urlsafe_base64_decode(encoded_id))
        user = user_model.objects.get(pk=user_id)
    except (ValueError, user_model.DoesNotExist):
        # TODO: Add a page for failed activation.
        user = None

    if user is not None and user.is_active:
        # The user has already activated their account, so we can just send them
        # to the index page.
        return redirect("index")

    if user is not None and activation_token.check_token(user, token):
        # Activate the user.
        user.is_active = True
        user.save()

        return redirect("index")

    # TODO: Add a page for failed activation.
    return redirect("index")
