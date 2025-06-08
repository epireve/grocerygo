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

    # Get category filter from URL parameters
    category_filter = request.GET.get("category")
    selected_category = None

    if category_filter:
        try:
            selected_category = Category.objects.get(slug=category_filter, active=True)
            # Filter products by the selected category and its subcategories
            subcategory_ids = list(
                selected_category.children.filter(active=True).values_list(
                    "id", flat=True
                )
            )
            all_category_ids = [selected_category.id] + subcategory_ids
            products = products.filter(category__id__in=all_category_ids)
        except Category.DoesNotExist:
            # If category doesn't exist, show all products
            pass

    return render(
        request,
        "products/product_list.html",
        {
            "categories": categories,
            "products": products,
            "selected_category": selected_category,
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
    View function for displaying a category and its products with subcategory filtering.

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

        # Add product count to each subcategory
        for subcategory in subcategories:
            subcategory.product_count = Product.objects.filter(
                category=subcategory, is_active=True, parent=None
            ).count()

        # Add the subcategories property to the category object for consistency
        category.subcategories = subcategories

        # Get subcategory filter from URL parameters
        subcategory_filter = request.GET.get("subcategory")
        selected_subcategory = None

        # Determine which products to show based on filtering
        if subcategory_filter and subcategories.exists():
            try:
                selected_subcategory = subcategories.get(slug=subcategory_filter)
                # Show products from the selected subcategory only
                products = Product.objects.filter(
                    category=selected_subcategory,
                    is_active=True,
                    parent=None,  # Only show parent products, not variants
                )
            except Category.DoesNotExist:
                # If subcategory doesn't exist, show all products in the main category
                # Get all products from this category and its subcategories
                subcategory_ids = list(subcategories.values_list("id", flat=True))
                all_category_ids = [category.id] + subcategory_ids
                products = Product.objects.filter(
                    category__id__in=all_category_ids,
                    is_active=True,
                    parent=None,
                )
        else:
            # Show all products from this category and its subcategories
            if subcategories.exists():
                subcategory_ids = list(subcategories.values_list("id", flat=True))
                all_category_ids = [category.id] + subcategory_ids
                products = Product.objects.filter(
                    category__id__in=all_category_ids,
                    is_active=True,
                    parent=None,
                )
            else:
                # No subcategories, just show products from this category
                products = Product.objects.filter(
                    category=category,
                    is_active=True,
                    parent=None,
                )

        # Get related categories
        related_categories = []
        if category.parent:
            # If this is a subcategory, get sibling categories
            related_categories = category.parent.children.filter(active=True).exclude(
                id=category.id
            )[
                :6
            ]  # Limit to 6 related categories
        else:
            # If this is a parent category, get other parent categories
            related_categories = Category.objects.filter(
                parent=None, active=True
            ).exclude(id=category.id)[
                :6
            ]  # Limit to 6 related categories

        # Add product counts to related categories
        for related_category in related_categories:
            if related_category.children.exists():
                # Include products from subcategories
                subcategory_ids = list(
                    related_category.children.filter(active=True).values_list(
                        "id", flat=True
                    )
                )
                all_category_ids = [related_category.id] + subcategory_ids
                related_category.product_count = Product.objects.filter(
                    category__id__in=all_category_ids, is_active=True, parent=None
                ).count()
            else:
                related_category.product_count = Product.objects.filter(
                    category=related_category, is_active=True, parent=None
                ).count()

        # Get all parent categories (for breadcrumb navigation)
        parent_categories = Category.objects.filter(parent=None, active=True)

        # Calculate total product count for this category (including subcategories)
        if subcategories.exists():
            subcategory_ids = list(subcategories.values_list("id", flat=True))
            all_category_ids = [category.id] + subcategory_ids
            total_product_count = Product.objects.filter(
                category__id__in=all_category_ids, is_active=True, parent=None
            ).count()
        else:
            total_product_count = Product.objects.filter(
                category=category, is_active=True, parent=None
            ).count()

        context = {
            "category": category,
            "subcategories": subcategories,
            "selected_subcategory": selected_subcategory,
            "related_categories": related_categories,
            "parent_categories": parent_categories,
            "products": products,
            "total_product_count": total_product_count,
            "has_subcategories": subcategories.exists(),
        }
        return render(request, "products/category_detail.html", context)
    except Category.DoesNotExist:
        messages.error(request, "Category not found.")
        return redirect("products:product_list")
