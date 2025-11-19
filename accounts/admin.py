from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, KYCProfile


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # Show these extra fields in admin
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Zariah Fields", {"fields": ("phone_number", "is_kyc_bypassed")}),
    )
    list_display = ("username", "email", "phone_number", "is_active", "is_kyc_bypassed", "is_staff")
    list_filter = ("is_active", "is_staff", "is_superuser", "is_kyc_bypassed")


@admin.register(KYCProfile)
class KYCProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email", "cnic")
