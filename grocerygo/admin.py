from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.db import connection
from django.core.cache import cache
from django.core.mail import get_connection
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.timezone import now
from decimal import Decimal
import os
import shutil
from datetime import datetime, timedelta

from orders.models import Checkout
from products.models import Product


class CustomAdminSite(admin.AdminSite):
    """Custom Admin Site with dashboard functionality"""

    site_header = "GroceryGo Administration"
    site_title = "GroceryGo Admin"
    index_title = "Dashboard"

    def get_dashboard_stats(self):
        """Get real-time dashboard statistics"""
        try:
            # Get current month start date
            current_month_start = now().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )

            # Total counts
            total_orders = Checkout.objects.count()
            total_products = Product.objects.filter(is_active=True).count()
            total_users = User.objects.filter(is_active=True).count()

            # Monthly revenue calculation
            monthly_revenue = Checkout.objects.filter(
                created_at__gte=current_month_start,
                status__in=[
                    "processing",
                    "shipped",
                    "delivered",
                ],  # Only count processed orders
            ).aggregate(total=Sum("total"))["total"] or Decimal("0.00")

            # Recent orders (last 10)
            recent_orders = Checkout.objects.select_related("user").order_by(
                "-created_at"
            )[:10]

            return {
                "total_orders": total_orders,
                "total_products": total_products,
                "total_users": total_users,
                "monthly_revenue": monthly_revenue,
                "recent_orders": recent_orders,
            }
        except Exception as e:
            # Return default values if there's an error
            return {
                "total_orders": 0,
                "total_products": 0,
                "total_users": 0,
                "monthly_revenue": Decimal("0.00"),
                "recent_orders": [],
                "error": str(e),
            }

    def get_system_status(self):
        """Get system status information"""
        status = {
            "Database Connection": {"status": "error", "message": "Unknown"},
            "Cache System": {"status": "error", "message": "Unknown"},
            "Email Service": {"status": "error", "message": "Unknown"},
            "Storage": {"status": "error", "message": "Unknown", "usage": 0},
        }

        # Database connection test
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                status["Database Connection"] = {
                    "status": "active",
                    "message": "Connected",
                }
        except Exception as e:
            status["Database Connection"] = {
                "status": "error",
                "message": f"Connection failed: {str(e)}",
            }

        # Cache system test
        try:
            cache.set("health_check", "test", 10)
            if cache.get("health_check") == "test":
                status["Cache System"] = {"status": "running", "message": "Working"}
            else:
                status["Cache System"] = {
                    "status": "error",
                    "message": "Cache not responding",
                }
        except Exception as e:
            status["Cache System"] = {
                "status": "error",
                "message": f"Cache error: {str(e)}",
            }

        # Email service test
        try:
            connection = get_connection()
            connection.open()
            connection.close()
            status["Email Service"] = {
                "status": "operational",
                "message": "SMTP accessible",
            }
        except Exception as e:
            status["Email Service"] = {
                "status": "error",
                "message": f"SMTP error: {str(e)}",
            }

        # Storage status
        try:
            from django.conf import settings

            total, used, free = shutil.disk_usage(settings.BASE_DIR)
            usage_percent = int((used / total) * 100)

            if usage_percent < 80:
                storage_status = "good"
                message = f"{usage_percent}% Used"
            elif usage_percent < 90:
                storage_status = "warning"
                message = f"{usage_percent}% Used"
            else:
                storage_status = "critical"
                message = f"{usage_percent}% Used"

            status["Storage"] = {
                "status": storage_status,
                "message": message,
                "usage": usage_percent,
            }
        except Exception as e:
            status["Storage"] = {
                "status": "error",
                "message": f"Storage check failed: {str(e)}",
                "usage": 0,
            }

        return status

    def index(self, request, extra_context=None):
        """Custom admin index view with dashboard data"""
        # Get dashboard statistics
        dashboard_stats = self.get_dashboard_stats()
        system_status = self.get_system_status()

        # Format monthly revenue for display
        formatted_revenue = f"RM {dashboard_stats['monthly_revenue']:,.2f}"

        # Prepare context
        extra_context = extra_context or {}
        extra_context.update(
            {
                "total_orders": dashboard_stats["total_orders"],
                "total_products": dashboard_stats["total_products"],
                "total_users": dashboard_stats["total_users"],
                "monthly_revenue": formatted_revenue,
                "recent_orders": dashboard_stats["recent_orders"],
                "system_status": system_status,
                "dashboard_error": dashboard_stats.get("error"),
            }
        )

        return super().index(request, extra_context)

    def get_urls(self):
        """Add custom URLs for dashboard API endpoints"""
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path(
                "api/sales-trend/<int:days>/",
                self.admin_view(self.sales_trend_api),
                name="sales_trend_api",
            ),
            path(
                "api/order-status/",
                self.admin_view(self.order_status_api),
                name="order_status_api",
            ),
            path(
                "api/top-products/",
                self.admin_view(self.top_products_api),
                name="top_products_api",
            ),
            path(
                "api/low-stock/",
                self.admin_view(self.low_stock_api),
                name="low_stock_api",
            ),
        ]
        return custom_urls + urls

    def sales_trend_api(self, request, days=7):
        """API endpoint for sales trend data"""
        from django.http import JsonResponse
        from datetime import datetime, timedelta
        from django.db.models import Sum, Count
        from django.utils import timezone

        # Calculate date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Get sales data for the period
        orders_by_day = []
        for i in range(days):
            day_start = start_date + timedelta(days=i)
            day_end = day_start + timedelta(days=1)

            daily_sales = Checkout.objects.filter(
                created_at__gte=day_start,
                created_at__lt=day_end,
                status__in=["processing", "shipped", "delivered"],
            ).aggregate(total_sales=Sum("total"), order_count=Count("id"))

            orders_by_day.append(
                {
                    "date": day_start.strftime("%Y-%m-%d"),
                    "day_name": day_start.strftime("%a"),
                    "sales": float(daily_sales["total_sales"] or 0),
                    "orders": daily_sales["order_count"] or 0,
                }
            )

        return JsonResponse(
            {
                "labels": [day["day_name"] for day in orders_by_day],
                "sales_data": [day["sales"] for day in orders_by_day],
                "order_data": [day["orders"] for day in orders_by_day],
            }
        )

    def order_status_api(self, request):
        """API endpoint for order status distribution"""
        from django.http import JsonResponse
        from django.db.models import Count

        status_counts = (
            Checkout.objects.values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )

        status_labels = []
        status_data = []
        status_colors = {
            "pending": "#f59e0b",
            "processing": "#3b82f6",
            "shipped": "#8b5cf6",
            "delivered": "#10b981",
            "cancelled": "#ef4444",
        }

        for item in status_counts:
            status_labels.append(item["status"].title())
            status_data.append(item["count"])

        return JsonResponse(
            {
                "labels": status_labels,
                "data": status_data,
                "colors": [
                    status_colors.get(status.lower(), "#6b7280")
                    for status in [item["status"] for item in status_counts]
                ],
            }
        )

    def top_products_api(self, request):
        """API endpoint for top selling products"""
        from django.http import JsonResponse
        from django.db.models import Sum, Count
        from orders.models import CheckoutItem

        # Get top selling products by quantity
        top_products = (
            CheckoutItem.objects.values("product__name")
            .annotate(
                total_sold=Sum("quantity"),
                order_count=Count("checkout_id", distinct=True),
            )
            .order_by("-total_sold")[:10]
        )

        product_names = []
        product_sales = []

        for item in top_products:
            product_names.append(item["product__name"])
            product_sales.append(item["total_sold"])

        return JsonResponse({"labels": product_names, "data": product_sales})

    def low_stock_api(self, request):
        """API endpoint for low stock products"""
        from django.http import JsonResponse

        # Get products with low stock (≤ 10 items)
        low_stock_products = (
            Product.objects.filter(stock__lte=10, is_active=True)
            .select_related("category")
            .order_by("stock")[:20]
        )

        products_data = []
        for product in low_stock_products:
            products_data.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "stock": product.stock,
                    "category": product.category.name,
                    "price": float(product.get_effective_price()),
                    "stock_level": self.get_stock_level_class(product.stock),
                }
            )

        return JsonResponse({"products": products_data, "count": len(products_data)})

    def get_stock_level_class(self, stock):
        """Get stock level classification"""
        if stock <= 0:
            return "out"
        elif stock <= 5:
            return "critical"
        elif stock <= 10:
            return "low"
        elif stock <= 50:
            return "medium"
        else:
            return "high"


# Create custom admin site instance
admin_site = CustomAdminSite(name="admin")

# Import and register all admin classes with the custom admin site
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from orders.admin import (
    AddressAdmin,
    OrderStatusHistoryAdmin,
    CheckoutAdmin,
    CheckoutItemAdmin,
)
from products.admin import CategoryAdmin, ProductAdmin
from orders.models import (
    Address,
    OrderStatusHistory,
    Checkout,
    CheckoutItem,
)
from products.models import Category, Product
from cart.models import Cart, CartItem, Coupon
from cart.admin import CartAdmin, CartItemAdmin, CouponAdmin

# Register models with custom admin site
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(Address, AddressAdmin)
admin_site.register(OrderStatusHistory, OrderStatusHistoryAdmin)
admin_site.register(Checkout, CheckoutAdmin)
admin_site.register(CheckoutItem, CheckoutItemAdmin)
admin_site.register(Category, CategoryAdmin)
admin_site.register(Product, ProductAdmin)
admin_site.register(Cart, CartAdmin)
admin_site.register(CartItem, CartItemAdmin)
admin_site.register(Coupon, CouponAdmin)
