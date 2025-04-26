from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
)
from .models import UserProfile


class UserRegistrationForm(UserCreationForm):
    """Form for user registration with custom fields and styling"""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm",
                "placeholder": "Email address",
            }
        ),
    )

    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm",
                "placeholder": "First name",
            }
        ),
    )

    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm",
                "placeholder": "Last name",
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
            }
        )
        # Customize password fields
        self.fields["password1"].widget.attrs.update(
            {
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm",
                "placeholder": "Password",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm",
                "placeholder": "Confirm password",
            }
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email


class CustomLoginForm(AuthenticationForm):
    """Custom login form with styled fields"""

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm",
                "placeholder": "Username",
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm",
                "placeholder": "Password",
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
            }
        )
    )

    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm",
                "placeholder": "Confirm new password",
            }
        )
    )
