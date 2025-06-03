from django.contrib import admin
from .models import Cart, CartItem, Coupon


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ["total_price"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "session_id",
        "total_items",
        "total_price",
        "created_at",
    ]
    list_filter = ["created_at"]
    search_fields = ["user__username", "session_id"]
    inlines = [CartItemInline]
    readonly_fields = ["total_price", "total_items"]
    date_hierarchy = "created_at"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["id", "cart", "product", "quantity", "total_price", "added_at"]
    list_filter = ["added_at"]
    search_fields = ["cart__user__username", "product__name"]
    readonly_fields = ["total_price"]
    date_hierarchy = "added_at"


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "discount_type",
        "value",
        "min_purchase",
        "valid_from",
        "valid_to",
        "is_active",
    ]
    list_filter = ["discount_type", "is_active", "valid_from", "valid_to"]
    search_fields = ["code"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "valid_to"
