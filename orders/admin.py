from django.contrib import admin
from .models import (
    Order,
    OrderItem,
    Address,
    OrderStatusHistory,
    ShippingAddress,
    Checkout,
    CheckoutItem,
)
from django.core.exceptions import PermissionDenied
import csv
from django.http import HttpResponse


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
        "id",
        "user",
        "order_status",
        "payment_status",
        "payment_method",
        "get_items_count",
        "total",
        "created_at",
    ]
    list_filter = ["order_status", "payment_status", "payment_method", "created_at"]
    search_fields = ["id", "user__username", "user__email"]
    readonly_fields = ["get_items_count"]
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    date_hierarchy = "created_at"

    actions = [
        "mark_as_processing",
        "mark_as_shipped",
        "mark_as_delivered",
        "mark_as_cancelled",
        "export_orders_as_csv",
    ]

    def get_items_count(self, obj):
        return obj.items.count()

    get_items_count.short_description = "Items Count"

    def mark_as_processing(self, request, queryset):
        """Mark selected orders as processing"""
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to perform this action")

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
        """Mark selected orders as shipped"""
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to perform this action")

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
        """Mark selected orders as delivered"""
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to perform this action")

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
        """Mark selected orders as cancelled"""
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to perform this action")

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

    def export_orders_as_csv(self, request, queryset):
        """Export selected orders as CSV file with related items"""
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to perform this action")

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        # Add custom fields for order items
        field_names.append("items")

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename=orders_export.csv"
        writer = csv.writer(response)

        # Add headers with column names
        writer.writerow(field_names)

        # Add data rows
        for obj in queryset:
            # Get basic order fields
            row_data = [
                getattr(obj, field) for field in field_names if field != "items"
            ]

            # Add order items as a comma-separated string
            items_str = "; ".join(
                [f"{item.quantity}x {item.product.name}" for item in obj.items.all()]
            )
            row_data.append(items_str)

            writer.writerow(row_data)

        return response

    export_orders_as_csv.short_description = "Export selected orders as CSV"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "product", "quantity", "price", "total_price"]
    list_filter = ["order__order_status"]
    search_fields = ["order__id", "product__name"]
    readonly_fields = ["total_price"]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "full_name", "address_type", "city", "is_default"]
    list_filter = ["address_type", "is_default", "city", "state", "country"]
    search_fields = ["user__username", "full_name", "street_address", "city"]
    date_hierarchy = "created_at"
    actions = ["export_addresses_as_csv"]

    def export_addresses_as_csv(self, request, queryset):
        """Export selected addresses as CSV file"""
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to perform this action")

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename=addresses_export.csv"
        writer = csv.writer(response)

        # Add headers with column names
        writer.writerow(field_names)

        # Add data rows
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_addresses_as_csv.short_description = "Export selected addresses as CSV"


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "status", "created_by", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["order__id", "notes"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at"]


# Register new checkout models
class CheckoutItemInline(admin.TabularInline):
    model = CheckoutItem
    extra = 0
    readonly_fields = ["total"]


@admin.register(Checkout)
class CheckoutAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "status",
        "payment_method",
        "get_items_count",
        "total",
        "created_at",
    ]
    list_filter = ["status", "payment_method", "created_at"]
    search_fields = ["id", "user__username", "user__email"]
    readonly_fields = ["get_items_count"]
    inlines = [CheckoutItemInline]
    date_hierarchy = "created_at"

    def get_items_count(self, obj):
        return obj.items.count()

    get_items_count.short_description = "Items Count"

    actions = [
        "mark_as_processing",
        "mark_as_shipped",
        "mark_as_delivered",
        "mark_as_cancelled",
        "export_as_csv",
    ]

    def mark_as_processing(self, request, queryset):
        """Mark selected checkouts as processing"""
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to perform this action")
        updated = queryset.update(status="processing")
        self.message_user(request, f"{updated} orders marked as processing.")

    mark_as_processing.short_description = "Mark selected orders as processing"

    def mark_as_shipped(self, request, queryset):
        """Mark selected checkouts as shipped"""
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to perform this action")
        updated = queryset.update(status="shipped")
        self.message_user(request, f"{updated} orders marked as shipped.")

    mark_as_shipped.short_description = "Mark selected orders as shipped"

    def mark_as_delivered(self, request, queryset):
        """Mark selected checkouts as delivered"""
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to perform this action")
        updated = queryset.update(status="delivered")
        self.message_user(request, f"{updated} orders marked as delivered.")

    mark_as_delivered.short_description = "Mark selected orders as delivered"

    def mark_as_cancelled(self, request, queryset):
        """Mark selected checkouts as cancelled"""
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to perform this action")
        updated = queryset.update(status="cancelled")
        self.message_user(request, f"{updated} orders marked as cancelled.")

    mark_as_cancelled.short_description = "Mark selected orders as cancelled"

    def export_as_csv(self, request, queryset):
        """Export selected checkouts as CSV file"""
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to perform this action")

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        # Add custom fields for items
        field_names.append("items")

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename=checkouts_export.csv"
        writer = csv.writer(response)

        # Add headers with column names
        writer.writerow(field_names)

        # Add data rows
        for obj in queryset:
            # Get basic checkout fields
            row_data = [
                getattr(obj, field) for field in field_names if field != "items"
            ]

            # Add checkout items as a comma-separated string
            items_str = "; ".join(
                [f"{item.quantity}x {item.product.name}" for item in obj.items.all()]
            )
            row_data.append(items_str)

            writer.writerow(row_data)

        return response

    export_as_csv.short_description = "Export selected checkouts as CSV"


@admin.register(CheckoutItem)
class CheckoutItemAdmin(admin.ModelAdmin):
    list_display = ["id", "checkout", "product", "quantity", "price", "total"]
    list_filter = ["checkout__status"]
    search_fields = ["checkout__id", "product__name"]
    readonly_fields = ["total"]


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "full_name", "city", "is_default"]
    list_filter = ["is_default", "city", "state", "country"]
    search_fields = ["user__username", "full_name", "street_address", "city", "phone"]
    date_hierarchy = "created_at"
