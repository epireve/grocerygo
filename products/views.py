from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product
from django.contrib import messages
from django.urls import reverse
from django.urls import reverse_lazy
from django.urls import reverse
from django.urls import reverse_lazy


# Create your views here.
def product_list_view(request):
    """View for displaying all products, optionally filtered"""
    categories = Category.objects.filter(active=True, parent=None)
    products = Product.objects.filter(is_active=True, parent=None)
    return render(
        request,
        "products/product_list.html",
        {
            "categories": categories,
            "products": products,
        },
    )


def product_detail_view(request, slug):
    """View for displaying a single product's details"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]

    return render(
        request,
        "products/product_detail.html",
        {
            "product": product,
            "related_products": related_products,
        },
    )


def categories_view(request):
    """View for displaying all parent categories"""
    categories = Category.objects.filter(active=True, parent=None)
    for category in categories:
        category.subcategory_count = category.children.filter(active=True).count()
        # Add product count for the main category (including all subcategories)
        # Get all subcategory IDs for this category
        subcategory_ids = list(
            category.children.filter(active=True).values_list("id", flat=True)
        )
        # Include the main category ID as well
        all_category_ids = [category.id] + subcategory_ids
        # Count products from main category and all its subcategories
        category.product_count = Product.objects.filter(
            category__id__in=all_category_ids, is_active=True, parent=None
        ).count()
        # Add the subcategories to each category with product counts
        subcategories = category.children.filter(active=True)
        for subcategory in subcategories:
            subcategory.product_count = Product.objects.filter(
                category=subcategory, is_active=True, parent=None
            ).count()
        category.subcategories = subcategories
    return render(request, "products/categories.html", {"categories": categories})


def category_detail_view(request, slug):
    """
    View function for displaying a category and its products.

    Args:
        request: The HTTP request
        slug: The slug of the category

    Returns:
        Rendered category detail page
    """
    try:
        category = get_object_or_404(Category, slug=slug, active=True)

        # Get active subcategories
        subcategories = category.children.filter(active=True)

        # Add the subcategories property to the category object for consistency
        category.subcategories = subcategories

        # Get sibling categories if this is a subcategory
        siblings = []
        if category.parent:
            siblings = category.parent.children.filter(active=True).exclude(
                id=category.id
            )

        # Get all parent categories (for breadcrumb navigation)
        parent_categories = Category.objects.filter(parent=None, active=True)

        # Get all products from this category
        products = Product.objects.filter(
            category=category,
            is_active=True,
            parent=None,  # Only show parent products, not variants
        )

        context = {
            "category": category,
            "subcategories": subcategories,
            "siblings": siblings,
            "parent_categories": parent_categories,
            "products": products,
        }
        return render(request, "products/category_detail.html", context)
    except Category.DoesNotExist:
        messages.error(request, "Category not found.")
        return redirect("products:product_list")
