from django.contrib import admin
from .models import User, KYCProfile


class KYCInline(admin.StackedInline):
    model = KYCProfile
    can_delete = False
    extra = 0
    readonly_fields = ("created_at", "updated_at")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "phone", "first_name", "last_name", "is_active")
    search_fields = ("email", "phone", "first_name", "last_name")
    list_filter = ("is_active",)
    inlines = [KYCInline]
    ordering = ("id",)


@admin.register(KYCProfile)
class KYCProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "cnic", "is_verified")
    search_fields = ("cnic",)
    list_filter = ("is_verified",)
    readonly_fields = ("created_at", "updated_at")