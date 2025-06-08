from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
        is_featured=True, is_active=True, parent=None
    )[:8]

    # If we have less than 8 featured products, add some regular products
    if featured_products.count() < 8:
        regular_products = Product.objects.filter(is_active=True, parent=None).exclude(
            id__in=[p.id for p in featured_products]
        )
        needed = 8 - featured_products.count()
        featured_products = list(featured_products) + list(regular_products[:needed])

    context = {
        "categories": categories,
        "featured_products": featured_products,
    }
    return render(request, "core/home.html", context)


def deals(request):
    """
    View for the deals page - displays all featured products with pagination
    """
    # Get all featured products, ordered by name
    featured_products = Product.objects.filter(
        is_featured=True, is_active=True, parent=None
    ).order_by("name")

    # Pagination - 12 products per page
    paginator = Paginator(featured_products, 12)
    page = request.GET.get("page", 1)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        products = paginator.page(paginator.num_pages)

    context = {
        "products": products,
        "featured_products": products,  # For template compatibility
        "total_count": featured_products.count(),
    }
    return render(request, "core/deals.html", context)


def about(request):
    """
    View for the about page - displays company information, values, and philosophy
    """
    context = {
        "page_title": "About Us",
    }
    return render(request, "core/about.html", context)
