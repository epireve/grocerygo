from django import template
from django.template.defaultfilters import stringfilter
from django.middleware.csrf import get_token

register = template.Library()


@register.filter
@stringfilter
def split(value, arg):
    """Split a string by the given separator and return a list."""
    return value.split(arg)


@register.filter
def make_list(value):
    """Convert a string to a list of characters"""
    return list(str(value))


@register.filter
def percentage_off(discount_price, original_price):
    """Calculate percentage off between two prices"""
    try:
        discount = float(discount_price)
        original = float(original_price)
        if original > 0:
            percentage = ((original - discount) / original) * 100
            return int(round(percentage))
        return 0
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.simple_tag
def csrf_token_value(request):
    """
    Returns the actual CSRF token value to use in JavaScript.
    """
    return get_token(request)
