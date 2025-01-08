"""Form definitions for the website."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator

from .models import CustomUser


class RegistrationForm(UserCreationForm):
    """Registration form for creating a new user."""

    email = forms.EmailField()

    class Meta:
        """Meta class for the RegistrationForm class."""

        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "email",
            "address",
            "city",
            "country",
            "postal_code",
            "password1",
            "password2",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"required": True}),
            "last_name": forms.TextInput(attrs={"required": True}),
            "email": forms.EmailInput(attrs={"required": True}),
            "address": forms.TextInput(attrs={"required": False}),
            "city": forms.TextInput(attrs={"required": False}),
            "country": forms.TextInput(attrs={"required": False}),
            "postal_code": forms.TextInput(attrs={"required": False}),
        }

    def clean_email(self):
        """Validates that the email is unique."""

        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already in use")
        return email


class EditForm(forms.ModelForm):
    """Registration form for creating a new user."""
    class Meta:
        """Meta class for the RegistrationForm class."""
        
        # first_name = forms.CharField()
        # last_name = forms.CharField()
        # address = forms.CharField()
        # city = forms.CharField()
        # country = forms.CharField()
        # postal_code = forms.CharField()
    
        model = CustomUser
        fields = [
                    "first_name",
                    "last_name",
                    "address",
                    "city",
                    "country",
                    "postal_code",
                ]

        widgets = {
            "first_name": forms.TextInput(attrs={"required": False}),
            "last_name": forms.TextInput(attrs={"required": False}),
            "address": forms.TextInput(attrs={"required": False}),
            "city": forms.TextInput(attrs={"required": False}),
            "country": forms.TextInput(attrs={"required": False}),
            "postal_code": forms.TextInput(attrs={"required": False}),
        }


class OTPForm(forms.Form):
    """Form for accepting an OTP code."""

    otp = forms.CharField(
        max_length=6,
        min_length=6,
        validators=[
            RegexValidator(r"^\d{6}$", "Only numeric input is allowed.")
        ],
        widget=forms.TextInput(
            attrs={"placeholder": "OTP Code", "autofocus": True}
        ),
        label="",
    )
