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
    user = request.user

    # Create a simple context with user data
    context = {
        "user": user,
        "profile_data": {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        },
    }

    if request.method == "POST":
        # Handle profile updates
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = request.POST.get("email", user.email)
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("accounts:profile")

    return render(request, "accounts/profile.html", context)


@login_required
def order_history_view(request):
    """View for displaying user's order history"""
    # This will be enhanced later when we have actual orders
    return render(request, "accounts/order_history.html", {"orders": []})


@login_required
def order_detail_view(request, order_id):
    """View for displaying details of a specific order"""
    # This will be enhanced later when we have actual orders
    return render(request, "accounts/order_detail.html", {"order": None})


@login_required
def cancel_order_view(request, order_id):
    """View for canceling an order"""
    if request.method == "POST":
        # This will be enhanced later when we have actual orders
        messages.success(request, "Order cancellation request submitted.")
    return redirect("accounts:order_detail", order_id=order_id)
