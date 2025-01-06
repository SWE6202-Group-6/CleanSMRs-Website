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
]
