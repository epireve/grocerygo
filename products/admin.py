from django.contrib import admin
from .models import Category, Product
import csv
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.utils.html import format_html


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "active", "created_at")
    list_filter = ("active", "parent")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("active",)
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 10  # Set pagination to 5 items per page for testing
    fieldsets = (
        (None, {"fields": ("name", "slug", "description", "parent")}),
        ("Status", {"fields": ("active",)}),
        ("Image", {"fields": ("image",), "classes": ("collapse",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
    actions = ["toggle_active_status"]

    def toggle_active_status(self, request, queryset):
        """Toggle active status for selected categories"""
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to perform this action")

        # Count categories that will be activated/deactivated
        activate_count = queryset.filter(active=False).count()
        deactivate_count = queryset.filter(active=True).count()

        # Update the status
        for category in queryset:
            category.active = not category.active
            category.save()

        # Provide detailed feedback
        if activate_count and deactivate_count:
            msg = f"Activated {activate_count} categories and deactivated {deactivate_count} categories."
        elif activate_count:
            msg = f"Activated {activate_count} categories."
        else:
            msg = f"Deactivated {deactivate_count} categories."

        self.message_user(request, msg)

    toggle_active_status.short_description = (
        "Toggle active status for selected categories"
    )


class ProductVariantInline(admin.TabularInline):
    model = Product
    fk_name = "parent"
    extra = 1
    fields = ("name", "price", "is_active", "stock")
    show_change_link = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    change_list_template = "admin/products/product/change_list.html"

    def changelist_view(self, request, extra_context=None):
        # Handle custom list_per_page parameter
        if "list_per_page" in request.GET:
            try:
                per_page = int(request.GET["list_per_page"])
                if per_page in [10, 25, 50, 100]:
                    self.list_per_page = per_page
                    # Store the choice in session for persistence
                    request.session["products_list_per_page"] = per_page
            except (ValueError, TypeError):
                pass
        elif "products_list_per_page" in request.session:
            # Use stored preference if no explicit parameter
            self.list_per_page = request.session["products_list_per_page"]

        # Add pagination context
        extra_context = extra_context or {}
        extra_context.update(
            {
                "current_per_page": self.list_per_page,
                "per_page_options": [10, 25, 50, 100],
            }
        )

        return super().changelist_view(request, extra_context)

    def stock_level_display(self, obj):
        """Display stock level with visual indicators"""
        stock = obj.stock

        if stock <= 0:
            badge_class = "stock-out"
            icon = "fas fa-times-circle"
            text = "0"
        elif stock <= 10:
            badge_class = "stock-low"
            icon = "fas fa-exclamation-triangle"
            text = f"{stock}"
        elif stock <= 50:
            badge_class = "stock-medium"
            icon = "fas fa-exclamation-circle"
            text = f"{stock}"
        else:
            badge_class = "stock-high"
            icon = "fas fa-check-circle"
            text = f"{stock}"

        return format_html(
            '<span class="product-stock {}"><i class="{}"></i> {}</span>',
            badge_class,
            icon,
            text,
        )

    stock_level_display.short_description = "Stock Level"

    def category_display(self, obj):
        """Display category name"""
        return obj.category.name

    category_display.short_description = "Category"

    def price_display(self, obj):
        """Display price with discount information"""
        if obj.discount_price:
            return format_html(
                '<span class="product-price">RM {}</span> <span style="text-decoration: line-through; color: #9ca3af;">RM {}</span>',
                obj.discount_price,
                obj.price,
            )
        return format_html('<span class="product-price">RM {}</span>', obj.price)

    price_display.short_description = "Price"

    list_display = (
        "name",
        "price_display",
        "category_display",
        "stock_level_display",
        "is_active",
        "is_featured",
        "created_at",
    )
    list_filter = ("is_active", "is_featured", "category")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    # list_editable = ("is_active", "is_featured")  # Temporarily disabled to test pagination
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 10  # Set pagination to 5 items per page for testing
    inlines = [ProductVariantInline]
    actions = [
        "mark_as_featured",
        "mark_as_not_featured",
        "update_stock_zero",
        "export_as_csv",
        "apply_discount_percentage",
        "clear_discount_price",
    ]

    def get_inlines(self, request, obj=None):
        if obj and obj.parent is None:  # Only show variants inline for parent products
            return [ProductVariantInline]
        return []

    fieldsets = (
        (None, {"fields": ("name", "slug", "description", "category", "parent")}),
        ("Pricing", {"fields": ("price", "discount_price")}),
        ("Status", {"fields": ("is_active", "is_featured", "stock")}),
        ("Image", {"fields": ("image",), "classes": ("collapse",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def mark_as_featured(self, request, queryset):
        """Mark selected products as featured"""
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to perform this action")

        queryset.update(is_featured=True)
        self.message_user(request, f"{queryset.count()} products marked as featured.")

    mark_as_featured.short_description = "Mark selected products as featured"

    def mark_as_not_featured(self, request, queryset):
        """Remove featured status from selected products"""
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to perform this action")

        queryset.update(is_featured=False)
        self.message_user(
            request, f"{queryset.count()} products marked as not featured."
        )

    mark_as_not_featured.short_description = "Mark selected products as not featured"

    def update_stock_zero(self, request, queryset):
        """Set stock to zero for out-of-stock products"""
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to perform this action")

        queryset.update(stock=0)
        self.message_user(
            request, f"Stock set to zero for {queryset.count()} products."
        )

    update_stock_zero.short_description = "Set stock to zero"

    def export_as_csv(self, request, queryset):
        """Export selected products as CSV file"""
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to perform this action")

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename={meta}.csv"
        writer = csv.writer(response)

        # Add headers with column names
        writer.writerow(field_names)

        # Add data rows
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export selected products as CSV"

    def apply_discount_percentage(self, request, queryset):
        """Apply percentage discount to selected products"""
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to perform this action")

        from django.contrib.admin.helpers import ActionForm
        from django import forms
        from django.template.response import TemplateResponse
        from decimal import Decimal

        class DiscountForm(ActionForm):
            discount_percentage = forms.IntegerField(
                required=True,
                min_value=1,
                max_value=99,
                label="Discount percentage (1-99)",
                widget=forms.NumberInput(attrs={"style": "width: 6em"}),
            )

        # Check if the form has been submitted
        if "apply" in request.POST:
            form = DiscountForm(request.POST)
            if form.is_valid():
                percentage = form.cleaned_data["discount_percentage"]
                count = 0

                for product in queryset:
                    # Calculate discounted price
                    discount_factor = Decimal(percentage) / Decimal(100)
                    discount_amount = product.price * discount_factor
                    product.discount_price = product.price - discount_amount
                    product.save()
                    count += 1

                self.message_user(
                    request, f"Applied {percentage}% discount to {count} products."
                )
                return None
        else:
            form = DiscountForm()

        # If not submitted or invalid, show the form
        context = {
            "title": "Apply discount percentage",
            "queryset": queryset,
            "action_checkbox_name": admin.helpers.ACTION_CHECKBOX_NAME,
            "form": form,
            "opts": self.model._meta,
        }
        return TemplateResponse(
            request, "admin/products/product/apply_discount.html", context
        )

    apply_discount_percentage.short_description = "Apply percentage discount"

    def clear_discount_price(self, request, queryset):
        """Remove discount prices from selected products"""
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to perform this action")

        queryset.update(discount_price=None)
        self.message_user(
            request, f"Removed discount prices from {queryset.count()} products."
        )

    clear_discount_price.short_description = "Clear discount prices"
