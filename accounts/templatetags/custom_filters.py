from django import template
from django.template.defaultfilters import stringfilter
from django.middleware.csrf import get_token

register = template.Library()


@register.filter
@stringfilter
def split(value, arg):
    """Split a string by the given separator and return a list."""
    return value.split(arg)


@register.simple_tag
def csrf_token_value(request):
    """
    Returns the actual CSRF token value to use in JavaScript.
    """
    return get_token(request)
