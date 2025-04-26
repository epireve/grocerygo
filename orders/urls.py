from django.urls import path
from . import views

app_name = "orders"  # This sets the namespace for the orders app

urlpatterns = [
    path("checkout/", views.checkout_view, name="checkout"),
]
