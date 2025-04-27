from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
from datetime import datetime, timedelta
import logging
from django.contrib import messages

User = get_user_model()
logger = logging.getLogger("security")


class RateLimitedAuthenticationBackend(ModelBackend):
    """
    Authentication backend that implements rate limiting for login attempts.

    This helps prevent brute force attacks by limiting the number of login
    attempts for a given username or IP address within a specified time period.
    """

    # Maximum number of login attempts
    MAX_ATTEMPTS = getattr(settings, "MAX_LOGIN_ATTEMPTS", 5)

    # Lockout period in minutes
    LOCKOUT_TIME = getattr(settings, "LOGIN_LOCKOUT_TIME", 30)  # 30 minutes

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate the user and implement rate limiting.
        """
        if not username or not password:
            return None

        # Check if the user is locked out
        is_locked, remaining_time = self.is_locked_out(request, username)
        if is_locked:
            # Log the failed attempt due to lockout
            ip_address = self.get_client_ip(request)
            logger.warning(
                f"Login attempt from locked account: username={username}, ip={ip_address}, "
                f"remaining_lockout_time={remaining_time} minutes"
            )

            # Add message to request if available
            if request and hasattr(request, "_messages"):
                messages.error(
                    request,
                    f"Your account is temporarily locked due to multiple failed login attempts. "
                    f"Please try again after {remaining_time} minutes.",
                )
            return None

        # Attempt to authenticate
        user = super().authenticate(
            request, username=username, password=password, **kwargs
        )

        if user is None:
            # Authentication failed, increment failed attempt counter
            self.increment_failed_attempts(request, username)

            # Log the failed attempt
            ip_address = self.get_client_ip(request)
            username_key = f"login_attempts_username_{username}"
            username_attempts = cache.get(username_key, 0) + 1

            logger.warning(
                f"Failed login attempt: username={username}, ip={ip_address}, "
                f"attempt_number={username_attempts}/{self.MAX_ATTEMPTS}"
            )

            # Check if this attempt caused a lockout
            if username_attempts >= self.MAX_ATTEMPTS:
                logger.warning(
                    f"Account locked: username={username}, ip={ip_address}, "
                    f"lockout_duration={self.LOCKOUT_TIME} minutes"
                )

                # Add message to request if available
                if request and hasattr(request, "_messages"):
                    messages.error(
                        request,
                        f"Your account has been locked due to multiple failed login attempts. "
                        f"Please try again after {self.LOCKOUT_TIME} minutes.",
                    )
        else:
            # Authentication succeeded, reset failed attempt counter
            self.reset_failed_attempts(request, username)

            # Log the successful login
            ip_address = self.get_client_ip(request)
            logger.info(f"Successful login: username={username}, ip={ip_address}")

        return user

    def is_locked_out(self, request, username):
        """
        Check if the user is locked out due to too many failed attempts.
        Returns a tuple of (is_locked_out, remaining_minutes)
        """
        # Get IP address
        ip_address = self.get_client_ip(request)

        # Check username-based lockout
        username_key = f"login_attempts_username_{username}"
        username_attempts = cache.get(username_key, 0)

        # Check IP-based lockout
        ip_key = f"login_attempts_ip_{ip_address}"
        ip_attempts = cache.get(ip_key, 0)

        # Calculate remaining lockout time in minutes (if locked)
        remaining_time = 0
        if username_attempts >= self.MAX_ATTEMPTS or ip_attempts >= self.MAX_ATTEMPTS:
            # Get TTL of the cache key to determine remaining lockout time
            username_ttl = cache.ttl(username_key)
            ip_ttl = cache.ttl(ip_key)
            # Convert seconds to minutes, rounded up
            remaining_time = (
                max(username_ttl, ip_ttl) // 60 + 1
                if max(username_ttl, ip_ttl) > 0
                else 0
            )

        return (
            (
                username_attempts >= self.MAX_ATTEMPTS
                or ip_attempts >= self.MAX_ATTEMPTS
            ),
            remaining_time,
        )

    def increment_failed_attempts(self, request, username):
        """
        Increment the failed login attempt counters for both username and IP.
        """
        # Get IP address
        ip_address = self.get_client_ip(request)

        # Increment username-based counter
        username_key = f"login_attempts_username_{username}"
        username_attempts = cache.get(username_key, 0)
        cache.set(
            username_key,
            username_attempts + 1,
            self.LOCKOUT_TIME * 60,  # Convert minutes to seconds
        )

        # Increment IP-based counter
        ip_key = f"login_attempts_ip_{ip_address}"
        ip_attempts = cache.get(ip_key, 0)
        cache.set(
            ip_key,
            ip_attempts + 1,
            self.LOCKOUT_TIME * 60,  # Convert minutes to seconds
        )

    def reset_failed_attempts(self, request, username):
        """
        Reset the failed login attempt counters for both username and IP.
        """
        # Get IP address
        ip_address = self.get_client_ip(request)

        # Reset username-based counter
        username_key = f"login_attempts_username_{username}"
        cache.delete(username_key)

        # Reset IP-based counter
        ip_key = f"login_attempts_ip_{ip_address}"
        cache.delete(ip_key)

    def get_client_ip(self, request):
        """
        Get the client IP address from the request.
        """
        if not request:
            return "unknown"

        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            # If behind a proxy, get the real IP
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "unknown")
        return ip
