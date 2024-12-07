"""View function definitions for the website."""

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from .forms import RegistrationForm

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
            form.save()
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
