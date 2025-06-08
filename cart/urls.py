from django.urls import path
from . import views

app_name = "cart"  # This sets up the 'cart' namespace

urlpatterns = [
    # Main cart URLs
    path(
        "add/", views.add_to_cart, name="add_to_cart_no_slug"
    ),  # Handle direct access to /cart/add/
    path("add/<slug:slug>/", views.add_to_cart, name="add_to_cart"),
    path("view/", views.view_cart, name="view_cart"),
    path("remove/<slug:slug>/", views.remove_from_cart, name="remove_from_cart"),
    path("update/<slug:slug>/", views.update_quantity, name="update_quantity"),
    path("clear/", views.clear_cart, name="clear_cart"),
    # Coupon management
    path("apply-coupon/", views.apply_coupon, name="apply_coupon"),
    path("remove-coupon/", views.remove_coupon, name="remove_coupon"),
    # API endpoints for localStorage sync
    path("sync/", views.sync_cart, name="sync_cart"),
    path("get-session-cart/", views.api_get_session_cart, name="get_session_cart"),
]
