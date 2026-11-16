from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ApiToken, User


@admin.register(User)
class SiteUserAdmin(UserAdmin):
    ordering = ("-date_joined",)
    list_display = ("phone", "first_name", "last_name", "email", "is_staff")
    search_fields = ("phone", "first_name", "last_name", "email")
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("პირადი ინფორმაცია", {"fields": ("first_name", "last_name", "email")}),
        ("უფლებები", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("phone", "first_name", "last_name", "email", "password1", "password2")}),
    )


admin.site.register(ApiToken)
