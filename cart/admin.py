from django.contrib import admin
from .models import Cart, CartItem


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
