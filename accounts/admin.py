from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile
from django.core.exceptions import PermissionDenied
import csv
from django.http import HttpResponse


# Define inline admin for UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "get_phone_number",
    )
    list_filter = BaseUserAdmin.list_filter + ("profile__terms_accepted",)
    search_fields = BaseUserAdmin.search_fields + (
        "profile__full_name",
        "profile__phone_number",
    )
    actions = ["export_users_as_csv"]

    def get_phone_number(self, obj):
        return obj.profile.phone_number if hasattr(obj, "profile") else ""

    get_phone_number.short_description = "Phone Number"
    get_phone_number.admin_order_field = "profile__phone_number"

    def export_users_as_csv(self, request, queryset):
        """Export selected users with their profile data as CSV"""
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to perform this action")

        # Define the fields to export
        user_fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
            "is_active",
            "date_joined",
            "last_login",
        ]
        profile_fields = ["full_name", "phone_number", "address", "terms_accepted"]

        # Combine fields for the header
        header_fields = user_fields + ["profile_" + field for field in profile_fields]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename=users_export.csv"
        writer = csv.writer(response)

        # Write header row
        writer.writerow(header_fields)

        # Write data rows
        for user in queryset:
            # Get user data
            user_data = [getattr(user, field) for field in user_fields]

            # Get profile data if exists
            profile_data = []
            if hasattr(user, "profile"):
                profile_data = [
                    getattr(user.profile, field) for field in profile_fields
                ]
            else:
                profile_data = [""] * len(profile_fields)

            # Combine data and write row
            writer.writerow(user_data + profile_data)

        return response

    export_users_as_csv.short_description = "Export selected users as CSV"


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# Register UserProfile as a standalone model as well
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "phone_number", "terms_accepted")
    list_filter = ("terms_accepted",)
    search_fields = ("user__username", "user__email", "full_name", "phone_number")
    raw_id_fields = ("user",)
    actions = ["export_profiles_as_csv"]

    def export_profiles_as_csv(self, request, queryset):
        """Export selected user profiles as CSV file"""
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to perform this action")

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        # Add username and email fields
        export_fields = ["user__username", "user__email"] + field_names

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename=profiles_export.csv"
        writer = csv.writer(response)

        # Write header row with custom field names
        header = ["username", "email"] + field_names
        writer.writerow(header)

        # Write data rows
        for profile in queryset:
            row_data = [profile.user.username, profile.user.email]
            for field in field_names:
                row_data.append(getattr(profile, field))
            writer.writerow(row_data)

        return response

    export_profiles_as_csv.short_description = "Export selected profiles as CSV"
