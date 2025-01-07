"""URL definitions for the website."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", views.log_in, name="login"),
    path("logout/", views.log_out, name="logout"),
    path("activate/<token>", views.activate, name="activate"),
    path('account/', views.account_view, name='account'),
    path('account/edit/', views.edit_form, name='edit'),
    path("setup-2fa", views.setup_2fa, name="setup_2fa"),
    path("verify-otp", views.verify_otp, name="verify_otp"),
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
    path("my-data/", views.my_data_view, name="my_data"),
]
