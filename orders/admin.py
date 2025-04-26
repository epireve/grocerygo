from django.contrib import admin
from .models import Order, OrderItem, Address, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["total_price"]


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ["created_at"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number",
        "user",
        "order_status",
        "payment_status",
        "order_items_count",
        "total",
        "created_at",
    ]
    list_filter = ["order_status", "payment_status", "payment_method", "created_at"]
    search_fields = ["order_number", "user__username", "user__email"]
    readonly_fields = ["order_items_count"]
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    date_hierarchy = "created_at"

    actions = [
        "mark_as_processing",
        "mark_as_shipped",
        "mark_as_delivered",
        "mark_as_cancelled",
    ]

    def mark_as_processing(self, request, queryset):
        for order in queryset:
            order.order_status = "processing"
            order.save()
            OrderStatusHistory.objects.create(
                order=order,
                status="processing",
                created_by=request.user,
                notes="Status changed from admin panel",
            )
        self.message_user(request, f"{queryset.count()} orders marked as processing.")

    mark_as_processing.short_description = "Mark selected orders as processing"

    def mark_as_shipped(self, request, queryset):
        for order in queryset:
            order.order_status = "shipped"
            order.save()
            OrderStatusHistory.objects.create(
                order=order,
                status="shipped",
                created_by=request.user,
                notes="Status changed from admin panel",
            )
        self.message_user(request, f"{queryset.count()} orders marked as shipped.")

    mark_as_shipped.short_description = "Mark selected orders as shipped"

    def mark_as_delivered(self, request, queryset):
        for order in queryset:
            order.order_status = "delivered"
            order.save()
            OrderStatusHistory.objects.create(
                order=order,
                status="delivered",
                created_by=request.user,
                notes="Status changed from admin panel",
            )
        self.message_user(request, f"{queryset.count()} orders marked as delivered.")

    mark_as_delivered.short_description = "Mark selected orders as delivered"

    def mark_as_cancelled(self, request, queryset):
        for order in queryset:
            order.order_status = "cancelled"
            order.save()
            OrderStatusHistory.objects.create(
                order=order,
                status="cancelled",
                created_by=request.user,
                notes="Status changed from admin panel",
            )
        self.message_user(request, f"{queryset.count()} orders marked as cancelled.")

    mark_as_cancelled.short_description = "Mark selected orders as cancelled"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "product", "quantity", "price", "total_price"]
    list_filter = ["order__order_status"]
    search_fields = ["order__order_number", "product__name"]
    readonly_fields = ["total_price"]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "full_name", "address_type", "city", "is_default"]
    list_filter = ["address_type", "is_default", "city", "state", "country"]
    search_fields = ["user__username", "full_name", "street_address", "city"]
    date_hierarchy = "created_at"


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "status", "created_by", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["order__order_number", "notes"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at"]
