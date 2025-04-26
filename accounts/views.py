from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.contrib.messages.views import SuccessMessageMixin
from .forms import (
    UserRegistrationForm,
    CustomLoginForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
)
from .models import UserProfile

# Create your views here.


class RegisterView(SuccessMessageMixin, CreateView):
    template_name = "accounts/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("accounts:login")
    success_message = "Your account has been created! You can now log in."

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("core:home")
        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(SuccessMessageMixin, LoginView):
    template_name = "accounts/login.html"
    form_class = CustomLoginForm
    success_message = "You have successfully logged in!"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("core:home")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        next_url = self.request.GET.get("next", None)
        if next_url:
            return next_url
        return reverse_lazy("core:home")


class CustomLogoutView(LogoutView):
    next_page = "core:home"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, "You have been logged out successfully!")
        return super().dispatch(request, *args, **kwargs)


class CustomPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy("accounts:password_reset_done")
    email_template_name = "accounts/password_reset_email.html"
    subject_template_name = "accounts/password_reset_subject.txt"


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy("accounts:password_reset_complete")


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"


@login_required
def profile_view(request):
    """View for displaying user profile"""
    return render(request, "accounts/profile.html")
