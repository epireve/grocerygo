from django.urls import path
from . import views

app_name = "cart"  # This sets up the 'cart' namespace

urlpatterns = [
    path("add/<slug:slug>/", views.add_to_cart, name="add_to_cart"),
    path("view/", views.view_cart, name="view_cart"),
    path("remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
]
