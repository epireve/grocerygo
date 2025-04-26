from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_list_view, name="product_list"),
    path("<int:product_id>/", views.product_detail_view, name="product_detail"),
    path(
        "category/<slug:category_slug>/",
        views.category_detail_view,
        name="category_detail",
    ),
]
