from django.utils import timezone
from django.contrib.auth import logout
from django.conf import settings
import datetime
import logging
import secrets

logger = logging.getLogger("security")


class UserActivityMiddleware:
    """
    Middleware to track user activity and automatically log out inactive users.

    This helps improve security by ensuring users are not left logged in
    indefinitely if they are inactive for a certain period of time.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Get the last activity time from the session
            last_activity = request.session.get("last_activity")

            # Get the inactivity timeout from settings with a default of 30 minutes
            timeout_minutes = getattr(settings, "USER_INACTIVITY_TIMEOUT", 30)

            if last_activity:
                # Convert the string timestamp to datetime
                last_activity_time = datetime.datetime.fromisoformat(last_activity)

                # Calculate time difference
                time_elapsed = timezone.now() - last_activity_time

                # If the user has been inactive for too long, log them out
                if time_elapsed.total_seconds() > (timeout_minutes * 60):
                    logout(request)
                    logger.info(
                        f"User {request.user.username} logged out due to inactivity after {timeout_minutes} minutes"
                    )
                    # Don't update the activity as they're being logged out
                    return self.get_response(request)

            # Update the last activity time
            request.session["last_activity"] = timezone.now().isoformat()

        # Process the request
        response = self.get_response(request)
        return response


class SecurityHeadersMiddleware:
    """
    Middleware to add security headers to all responses.

    This enhances security by setting headers that help protect against
    common web vulnerabilities like XSS, clickjacking, etc.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Content Security Policy (CSP)
        # This is a basic policy - in production, you should customize it
        # based on your specific needs and third-party integrations
        if not response.has_header("Content-Security-Policy"):
            response["Content-Security-Policy"] = self._get_csp_policy()

        # Referrer Policy
        # Limit information passed to other sites when navigating away
        if not response.has_header("Referrer-Policy"):
            response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy (formerly Feature Policy)
        # Restrict browser features to mitigate risks
        if not response.has_header("Permissions-Policy"):
            response["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

        # Add strict transport security header if not already set
        # This is now handled by SECURE_HSTS_SECONDS in settings.py

        return response

    def _get_csp_policy(self):
        """
        Generate a Content Security Policy based on the environment.

        In production, this should be carefully tailored to your application's needs.
        """
        is_production = getattr(settings, "IS_PRODUCTION", False)

        if is_production:
            # Stricter policy for production
            return (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-src 'none'; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self';"
            )
        else:
            # More permissive for development
            return (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-src 'self'; "
                "object-src 'none';"
            )


class CSPNonceMiddleware:
    """
    Middleware that adds a random nonce to each request for Content Security Policy.

    This allows using the nonce in CSP headers to authorize inline scripts
    without using 'unsafe-inline', which is more secure.

    To use the nonce in templates, use the {% csp_nonce request %} template tag:
    <script nonce="{% csp_nonce request %}">...</script>
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Generate a random nonce
        nonce = secrets.token_urlsafe(32)

        # Attach the nonce to the request object
        request.csp_nonce = nonce

        # Get the response
        response = self.get_response(request)

        # Update the CSP header with the nonce if it exists
        if response.has_header("Content-Security-Policy"):
            csp = response["Content-Security-Policy"]

            # Add the nonce to script-src and style-src
            if "script-src" in csp:
                csp = csp.replace("script-src", f"script-src 'nonce-{nonce}'")

            # Update the header
            response["Content-Security-Policy"] = csp

        return response
