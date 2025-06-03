from django.urls import path
from . import views

app_name = "orders"  # This sets the namespace for the orders app

urlpatterns = [
    path("checkout/", views.checkout_view, name="checkout"),
    path(
        "confirmation/<int:pk>/",
        views.order_confirmation_view,
        name="order_confirmation",
    ),
    path("history/", views.order_history_view, name="order_history"),
    path("detail/<int:pk>/", views.order_detail_view, name="order_detail"),
    path("cancel/<int:pk>/", views.cancel_order_view, name="cancel_order"),
]
