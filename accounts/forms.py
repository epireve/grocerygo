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
from orders.models import Address
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


class AddressForm(forms.ModelForm):
    """Form for adding and editing shipping addresses"""

    class Meta:
        model = Address
        fields = [
            "full_name",
            "street_address",
            "apartment_address",
            "city",
            "state",
            "postal_code",
            "country",
            "phone",
            "is_default",
        ]
        widgets = {
            "full_name": forms.TextInput(
                attrs={
                    "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm",
                    "placeholder": "Full Name",
                    "autocomplete": "name",
                }
            ),
            "street_address": forms.TextInput(
                attrs={
                    "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm",
                    "placeholder": "Street Address",
                    "autocomplete": "street-address",
                }
            ),
            "apartment_address": forms.TextInput(
                attrs={
                    "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm",
                    "placeholder": "Apartment, suite, etc. (optional)",
                    "autocomplete": "address-line2",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm",
                    "placeholder": "City",
                    "autocomplete": "address-level2",
                }
            ),
            "state": forms.TextInput(
                attrs={
                    "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm",
                    "placeholder": "State",
                    "autocomplete": "address-level1",
                }
            ),
            "postal_code": forms.TextInput(
                attrs={
                    "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm",
                    "placeholder": "Postal Code",
                    "autocomplete": "postal-code",
                }
            ),
            "country": forms.TextInput(
                attrs={
                    "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm",
                    "placeholder": "Country",
                    "autocomplete": "country",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm",
                    "placeholder": "Phone Number (optional)",
                    "autocomplete": "tel",
                }
            ),
            "is_default": forms.CheckboxInput(
                attrs={
                    "class": "h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        address = super().save(commit=False)
        if self.user:
            address.user = self.user
            address.address_type = "shipping"  # Always shipping for profile management
        if commit:
            address.save()
        return address

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get("postal_code")
        if postal_code:
            # Remove any spaces and ensure it's 5 digits for Malaysian postal codes
            postal_code = postal_code.replace(" ", "")
            if not postal_code.isdigit() or len(postal_code) != 5:
                raise forms.ValidationError("Please enter a valid 5-digit postal code.")
        return postal_code

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            # Remove spaces and dashes for validation
            phone_clean = phone.replace(" ", "").replace("-", "")
            # Check if it starts with Malaysia country code or is a local number
            if not (
                phone_clean.startswith("+60")
                or phone_clean.startswith("60")
                or phone_clean.startswith("0")
            ):
                raise forms.ValidationError(
                    "Please enter a valid Malaysian phone number."
                )
        return phone
