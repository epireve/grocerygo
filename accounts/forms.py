from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.core.exceptions import ValidationError
from .models import UserProfile
import re


class UserRegistrationForm(UserCreationForm):
    """Form for user registration with custom fields and styling"""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm",
                "placeholder": "Email address",
                "autocomplete": "email",
            }
        ),
    )

    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm",
                "placeholder": "First name",
                "autocomplete": "given-name",
            }
        ),
    )

    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm",
                "placeholder": "Last name",
                "autocomplete": "family-name",
            }
        ),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize username field
        self.fields["username"].widget.attrs.update(
            {
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm",
                "placeholder": "Username",
                "autocomplete": "username",
            }
        )
        # Customize password fields
        self.fields["password1"].widget.attrs.update(
            {
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm",
                "placeholder": "Password",
                "autocomplete": "new-password",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm",
                "placeholder": "Confirm password",
                "autocomplete": "new-password",
            }
        )

        # Enhanced password help text for better security guidance
        self.fields["password1"].help_text = (
            "<ul class='text-xs text-gray-500 mt-1 list-disc list-inside'>"
            "<li>Your password must contain at least 10 characters</li>"
            "<li>Your password can't be entirely numeric</li>"
            "<li>Your password can't be a commonly used password</li>"
            "<li>Your password can't be too similar to your other personal information</li>"
            "<li>Use a mix of letters, numbers, and symbols for stronger security</li>"
            "</ul>"
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get("password1")

        # Check for password strength beyond Django's default validators
        if password:
            # Check for mixed case letters
            if not (
                any(c.islower() for c in password)
                and any(c.isupper() for c in password)
            ):
                raise ValidationError(
                    "Password must contain both uppercase and lowercase letters."
                )

            # Check for at least one special character
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                raise ValidationError(
                    'Password must contain at least one special character (!@#$%^&*(),.?":{}|<>).'
                )

            # Check for at least one number
            if not any(c.isdigit() for c in password):
                raise ValidationError("Password must contain at least one number.")

        return password


class CustomLoginForm(AuthenticationForm):
    """Custom login form with styled fields"""

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm",
                "placeholder": "Username",
                "autocomplete": "username",
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm",
                "placeholder": "Password",
                "autocomplete": "current-password",
            }
        )
    )


class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form with styled email field"""

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm",
                "placeholder": "Email address",
                "autocomplete": "email",
            }
        )
    )


class CustomSetPasswordForm(SetPasswordForm):
    """Custom set password form with styled password fields"""

    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm",
                "placeholder": "New password",
                "autocomplete": "new-password",
            }
        )
    )

    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm",
                "placeholder": "Confirm new password",
                "autocomplete": "new-password",
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Enhanced password help text for better security guidance
        self.fields["new_password1"].help_text = (
            "<ul class='text-xs text-gray-500 mt-1 list-disc list-inside'>"
            "<li>Your password must contain at least 10 characters</li>"
            "<li>Your password can't be entirely numeric</li>"
            "<li>Your password can't be a commonly used password</li>"
            "<li>Your password can't be too similar to your other personal information</li>"
            "<li>Use a mix of letters, numbers, and symbols for stronger security</li>"
            "</ul>"
        )

    def clean_new_password1(self):
        password = self.cleaned_data.get("new_password1")

        # Check for password strength beyond Django's default validators
        if password:
            # Check for mixed case letters
            if not (
                any(c.islower() for c in password)
                and any(c.isupper() for c in password)
            ):
                raise ValidationError(
                    "Password must contain both uppercase and lowercase letters."
                )

            # Check for at least one special character
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                raise ValidationError(
                    'Password must contain at least one special character (!@#$%^&*(),.?":{}|<>).'
                )

            # Check for at least one number
            if not any(c.isdigit() for c in password):
                raise ValidationError("Password must contain at least one number.")

        return password
