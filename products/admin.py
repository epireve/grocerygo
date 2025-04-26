from django.contrib import admin
from .models import Category


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
