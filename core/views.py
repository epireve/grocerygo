from django.shortcuts import render
from products.models import Category, Product

# Create your views here.


def home(request):
    """
    View for the home page
    """
    # Get top-level categories (no parent)
    categories = Category.objects.filter(parent=None, active=True)[:6]

    # Get featured products, limit to 8
    featured_products = Product.objects.filter(
        is_featured=True, active=True, parent=None
    )[:8]

    # If we have less than 8 featured products, add some regular products
    if featured_products.count() < 8:
        regular_products = Product.objects.filter(active=True, parent=None).exclude(
            id__in=[p.id for p in featured_products]
        )
        needed = 8 - featured_products.count()
        featured_products = list(featured_products) + list(regular_products[:needed])

    context = {
        "categories": categories,
        "featured_products": featured_products,
    }
    return render(request, "core/home.html", context)
