from django.contrib import admin
from .models import BuyOrder, SellOrder, Wallet, GoldInventory
from .audit_models import OrderAuditLog


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "gold_balance_grams", "tola", "milligrams", "updated_at")
    search_fields = ("user__email", "user__phone")


@admin.register(BuyOrder)
class BuyOrderAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "locked_price_per_gram",
        "gold_quantity_grams",
        "status",
        "locked_at",
        "expires_at",
        "executed_at",
    )
    list_filter = ("status",)
    search_fields = ("user__email", "user__phone", "order_token")


@admin.register(SellOrder)
class SellOrderAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "locked_price_per_gram",
        "gold_quantity_grams",
        "status",
        "locked_at",
        "expires_at",
        "executed_at",
    )
    list_filter = ("status",)
    search_fields = ("user__email", "user__phone", "order_token")

admin.site.register(GoldInventory)