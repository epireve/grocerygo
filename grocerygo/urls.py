"""
URL configuration for grocerygo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from products.views import categories_view, category_detail_view, product_detail_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls", namespace="core")),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    # Products app URLs
    path("products/", include("products.urls", namespace="products")),
    # Top-level URLs with the products namespace
    path("categories/", categories_view, name="category_list"),
    path("category/<slug:slug>/", category_detail_view, name="category_detail"),
    path("product/<slug:slug>/", product_detail_view, name="product_detail"),
    path("cart/", include("cart.urls", namespace="cart")),
    path("orders/", include("orders.urls", namespace="orders")),
    path("__reload__/", include("django_browser_reload.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
