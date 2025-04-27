from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def csp_nonce(request):
    """
    Return the Content Security Policy nonce from the request.
    This allows for inline scripts with a CSP policy.

    Usage: <script nonce="{% csp_nonce request %}">...</script>
    """
    return getattr(request, "csp_nonce", "")


@register.simple_tag
def meta_security_tags():
    """
    Return a set of security-related meta tags for the HTML head.

    Usage: {% meta_security_tags %}
    """
    tags = [
        '<meta http-equiv="X-Content-Type-Options" content="nosniff">',
        '<meta http-equiv="X-XSS-Protection" content="1; mode=block">',
        '<meta http-equiv="Referrer-Policy" content="strict-origin-when-cross-origin">',
    ]

    # Only add Strict-Transport-Security in production
    is_production = getattr(settings, "IS_PRODUCTION", False)
    if is_production:
        tags.append(
            '<meta http-equiv="Strict-Transport-Security" content="max-age=31536000; includeSubDomains; preload">'
        )

    return mark_safe("\n    ".join(tags))


@register.simple_tag
def no_cache_headers():
    """
    Return no-cache meta tags for pages that should not be cached
    (like account pages, checkout, etc.)

    Usage: {% no_cache_headers %}
    """
    tags = [
        '<meta http-equiv="Cache-Control" content="no-store, no-cache, must-revalidate, max-age=0">',
        '<meta http-equiv="Pragma" content="no-cache">',
        '<meta http-equiv="Expires" content="0">',
    ]

    return mark_safe("\n    ".join(tags))
