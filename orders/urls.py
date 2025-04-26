from django.urls import path
from . import views

app_name = "orders"  # This sets the namespace for the orders app

urlpatterns = [
    path("checkout/", views.checkout_view, name="checkout"),
    path(
        "confirmation/<int:checkout_id>/",
        views.order_confirmation_view,
        name="order_confirmation",
    ),
]
