from django.contrib import admin
from .models import Category, Product


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "active", "created_at")
    list_filter = ("active", "parent")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("active",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("name", "slug", "description", "parent")}),
        ("Status", {"fields": ("active",)}),
        ("Image", {"fields": ("image",), "classes": ("collapse",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


class ProductVariantInline(admin.TabularInline):
    model = Product
    fk_name = "parent"
    extra = 1
    fields = ("name", "price", "is_active", "stock")
    show_change_link = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "category",
        "is_active",
        "is_featured",
        "created_at",
    )
    list_filter = ("is_active", "is_featured", "category")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active", "is_featured")
    readonly_fields = ("created_at", "updated_at")
    inlines = [ProductVariantInline]

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
