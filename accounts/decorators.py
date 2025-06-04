from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from functools import wraps
import logging

logger = logging.getLogger("security")


def staff_member_required(view_func):
    """
    Decorator for views that checks that the user is a staff member.
    Similar to login_required but checks is_staff instead.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return HttpResponseRedirect(
                reverse("accounts:login") + f"?next={request.path}"
            )

        if not request.user.is_staff:
            logger.warning(
                f"Unauthorized staff access attempt: {request.user.username} "
                f"attempted to access {request.path}"
            )
            messages.error(request, "You do not have permission to access this page.")
            return HttpResponseRedirect(reverse("core:home"))

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def owner_required(model_class, lookup_field="pk"):
    """
    Decorator for views that checks if the user is the owner of the object.
    Useful for views where users should only see their own data.

    Example usage:
    @owner_required(UserProfile, lookup_field='user__username')
    def profile_view(request, username):
        # This view will only execute if the logged-in user owns the profile
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "You must be logged in to access this page.")
                return HttpResponseRedirect(
                    reverse("accounts:login") + f"?next={request.path}"
                )

            lookup_value = kwargs.get(lookup_field)
            if not lookup_value:
                # If the lookup field isn't in kwargs, we can't check ownership
                raise ValueError(
                    f"Lookup field '{lookup_field}' not found in view kwargs"
                )

            # Build lookup dict dynamically
            lookup = {lookup_field: lookup_value}

            try:
                # Get the object and check ownership
                obj = model_class.objects.get(**lookup)

                # Check if the user is the owner (using a generic 'user' field)
                # For more complex ownership models, extend this function
                if hasattr(obj, "user") and obj.user == request.user:
                    return view_func(request, *args, **kwargs)

                # If it's an order, check if it belongs to the user
                if hasattr(obj, "user_id") and obj.user_id == request.user.id:
                    return view_func(request, *args, **kwargs)

                # Special case for User itself
                if hasattr(obj, "id") and obj.id == request.user.id:
                    return view_func(request, *args, **kwargs)

                # User is not the owner
                logger.warning(
                    f"Unauthorized access attempt: {request.user.username} "
                    f"attempted to access {model_class.__name__} {lookup_value} "
                    f"which they do not own."
                )
                messages.error(
                    request, "You do not have permission to access this page."
                )
                return HttpResponseRedirect(reverse("core:home"))

            except model_class.DoesNotExist:
                # Object doesn't exist
                messages.error(request, "The requested resource does not exist.")
                return HttpResponseRedirect(reverse("core:home"))

        return _wrapped_view

    return decorator


def ajax_login_required(view_func):
    """
    Decorator for AJAX views that require login.
    Returns a 403 status code instead of redirecting to the login page.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            logger.warning(f"Unauthenticated AJAX request attempted: {request.path}")
            raise PermissionDenied("Authentication required")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
