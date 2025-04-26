from django.shortcuts import render, get_object_or_404
from .models import Category


# Create your views here.
def product_list_view(request):
    """View for displaying all products, optionally filtered"""
    categories = Category.objects.filter(active=True, parent=None)
    return render(
        request,
        "products/product_list.html",
        {
            "categories": categories,
            "products": [],  # Will be updated later when we have Product model
        },
    )


def product_detail_view(request, product_id):
    """View for displaying a single product's details"""
    # Will be updated later when we have Product model
    return render(request, "products/product_detail.html", {"product": None})


def category_detail_view(request, category_slug):
    """View for displaying products in a specific category"""
    category = get_object_or_404(Category, slug=category_slug, active=True)
    return render(
        request,
        "products/category_detail.html",
        {
            "category": category,
            "products": [],  # Will be updated later when we have Product model
        },
    )
