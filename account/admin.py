from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserCreationForm, UserChangeForm
from .models import User, OTP

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ("phone_number", "full_name", "email", "is_active", "is_admin")
    list_filter = ("is_admin", "is_active")
    search_fields = ("phone_number", "full_name", "email")
    ordering = ("phone_number",)
    filter_horizontal = ()

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("Personal info", {"fields": ("full_name", "email", "image")}),
        ("Permissions", {"fields": ("is_active", "is_admin")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone_number", "full_name", "password1", "password2"),
        }),
    )


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "code", "created_at", "expires_at")
    search_fields = ("phone_number",)

