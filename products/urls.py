from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    # Regular products URL patterns
    path("", views.product_list_view, name="product_list"),
    # Remove duplicate paths that now exist at the top level
    # path("categories/", views.categories_view, name="category_list"),
    # path("category/<slug:slug>/", views.category_detail_view, name="category_detail"),
    # path("product/<slug:slug>/", views.product_detail_view, name="product_detail"),
]


# This is what Django uses to get the URL patterns from this module
def get_patterns(**kwargs):
    """Get URL patterns based on kwargs."""
    categories_only = kwargs.get("categories_only", False)
    category_detail_only = kwargs.get("category_detail_only", False)
    product_detail_only = kwargs.get("product_detail_only", False)

    if categories_only:
        # Handle /categories/ URL
        return [
            path("", views.categories_view, name="category_list"),
        ]
    elif category_detail_only:
        # Handle /category/<slug>/ URL
        return [
            path("", views.category_detail_view, name="category_detail"),
        ]
    elif product_detail_only:
        # Handle /product/<slug>/ URL
        return [
            path("", views.product_detail_view, name="product_detail"),
        ]
    return urlpatterns


# Override the default urlpatterns with the get_patterns function
# Django's URL resolver will call this function when loading the URL patterns
globals()["get_urlpatterns"] = get_patterns
