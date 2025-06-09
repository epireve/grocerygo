from django.contrib import admin
from .models import Cart, CartItem, Coupon


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ["total_price"]


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


class CartItemAdmin(admin.ModelAdmin):
    list_display = ["id", "cart", "product", "quantity", "total_price", "added_at"]
    list_filter = ["added_at"]
    search_fields = ["cart__user__username", "product__name"]
    readonly_fields = ["total_price"]
    date_hierarchy = "added_at"


class CouponAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "discount_display",
        "min_purchase",
        "validity_status",
        "usage_period",
        "is_active",
        "created_at",
    ]
    list_filter = [
        "discount_type",
        "is_active",
        ("valid_from", admin.DateFieldListFilter),
        ("valid_to", admin.DateFieldListFilter),
        ("created_at", admin.DateFieldListFilter),
    ]
    search_fields = ["code", "discount_type"]
    readonly_fields = ["created_at", "updated_at", "validity_status"]
    date_hierarchy = "valid_to"
    ordering = ["-created_at"]
    list_per_page = 25

    # Enhanced fieldsets for better organization
    fieldsets = (
        (
            "Coupon Information",
            {
                "fields": ("code", "discount_type", "value", "min_purchase"),
                "description": "Basic coupon configuration and discount settings.",
            },
        ),
        (
            "Validity Period",
            {
                "fields": ("valid_from", "valid_to", "is_active"),
                "description": "Set when this coupon can be used.",
            },
        ),
        (
            "System Information",
            {
                "fields": ("created_at", "updated_at", "validity_status"),
                "classes": ("collapse",),
                "description": "System-generated timestamps and status information.",
            },
        ),
    )

    # Custom actions
    actions = ["activate_coupons", "deactivate_coupons", "extend_validity"]

    def discount_display(self, obj):
        """Display discount in a formatted way"""
        if obj.discount_type == "percentage":
            return f"{obj.value}% off"
        return f"RM{obj.value} off"

    discount_display.short_description = "Discount"
    discount_display.admin_order_field = "value"

    def validity_status(self, obj):
        """Show current validity status with color coding"""
        from django.utils.html import format_html
        from django.utils import timezone

        now = timezone.now()

        if not obj.is_active:
            return format_html(
                '<span style="color: #dc2626; font-weight: bold;">❌ Inactive</span>'
            )
        elif obj.valid_from > now:
            return format_html(
                '<span style="color: #f59e0b; font-weight: bold;">⏳ Not Started</span>'
            )
        elif obj.valid_to < now:
            return format_html(
                '<span style="color: #dc2626; font-weight: bold;">⏰ Expired</span>'
            )
        else:
            return format_html(
                '<span style="color: #10b981; font-weight: bold;">✅ Active</span>'
            )

    validity_status.short_description = "Status"

    def usage_period(self, obj):
        """Display the usage period in a readable format"""
        from django.utils.html import format_html

        start = obj.valid_from.strftime("%b %d, %Y")
        end = obj.valid_to.strftime("%b %d, %Y")

        return format_html(
            '<span style="font-size: 0.875rem;">{} - {}</span>', start, end
        )

    usage_period.short_description = "Valid Period"
    usage_period.admin_order_field = "valid_from"

    # Custom actions
    def activate_coupons(self, request, queryset):
        """Activate selected coupons"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Successfully activated {updated} coupon(s).")

    activate_coupons.short_description = "Activate selected coupons"

    def deactivate_coupons(self, request, queryset):
        """Deactivate selected coupons"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Successfully deactivated {updated} coupon(s).")

    deactivate_coupons.short_description = "Deactivate selected coupons"

    def extend_validity(self, request, queryset):
        """Extend validity period by 30 days"""
        from django.utils import timezone
        from datetime import timedelta

        updated = 0
        for coupon in queryset:
            coupon.valid_to = coupon.valid_to + timedelta(days=30)
            coupon.save()
            updated += 1

        self.message_user(
            request,
            f"Successfully extended validity period for {updated} coupon(s) by 30 days.",
        )

    extend_validity.short_description = "Extend validity by 30 days"

    def get_form(self, request, obj=None, **kwargs):
        """Customize the form"""
        form = super().get_form(request, obj, **kwargs)

        # Add help text for fields
        if "code" in form.base_fields:
            form.base_fields["code"].help_text = (
                "Enter a unique coupon code (e.g., SAVE20, WELCOME10)"
            )
        if "value" in form.base_fields:
            form.base_fields["value"].help_text = (
                "For percentage: enter value without % (e.g., 20 for 20% off). For fixed: enter amount in RM."
            )
        if "min_purchase" in form.base_fields:
            form.base_fields["min_purchase"].help_text = (
                "Minimum purchase amount required to use this coupon (in RM)"
            )

        return form

    def save_model(self, request, obj, form, change):
        """Custom save logic with validation"""
        if not change:  # New object
            # Ensure code is uppercase
            obj.code = obj.code.upper()

        # Validate discount value
        if obj.discount_type == "percentage" and obj.value > 100:
            from django.contrib import messages

            messages.warning(request, "Percentage discount cannot exceed 100%")
            obj.value = 100

        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        """Add extra context to changelist view"""
        from django.utils import timezone

        extra_context = extra_context or {}

        # Add statistics
        total_coupons = Coupon.objects.count()
        active_coupons = Coupon.objects.filter(
            is_active=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now()
        ).count()
        expired_coupons = Coupon.objects.filter(valid_to__lt=timezone.now()).count()

        extra_context.update(
            {
                "coupon_stats": {
                    "total": total_coupons,
                    "active": active_coupons,
                    "expired": expired_coupons,
                }
            }
        )

        return super().changelist_view(request, extra_context=extra_context)

    def delete_view(self, request, object_id, extra_context=None):
        """Enhanced delete view with usage statistics"""
        obj = self.get_object(request, object_id)
        if obj:
            # Calculate usage statistics
            # Count how many carts currently have this coupon applied
            active_carts = Cart.objects.filter(coupon=obj).count()

            # For demonstration, we'll set usage_count and total_savings to 0
            # In a real system, you might track coupon usage in order history
            usage_count = 0
            total_savings = 0

            extra_context = extra_context or {}
            extra_context.update(
                {
                    "usage_count": usage_count,
                    "total_savings": total_savings,
                    "active_carts": active_carts,
                }
            )

        return super().delete_view(request, object_id, extra_context=extra_context)


# Register models with admin site
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Coupon, CouponAdmin)
