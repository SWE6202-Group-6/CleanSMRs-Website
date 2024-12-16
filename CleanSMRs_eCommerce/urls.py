"""URL definitions for the website."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", views.log_in, name="login"),
    path("logout/", views.log_out, name="logout"),
    path("activate/<token>", views.activate, name="activate"),
    path("products/", views.products_view, name="products"),
    path("products/<int:product_id>", views.product_view, name="product"),
    path(
        "checkout/<int:product_id>",
        views.create_checkout_session,
        name="checkout",
    ),
    path("success/", views.checkout_success, name="success"),
    path("cancel/", views.checkout_cancel, name="cancel"),
    path(
        "stripe_webhook/", views.stripe_webhook_handler, name="stripe_webhook"
    ),
]
