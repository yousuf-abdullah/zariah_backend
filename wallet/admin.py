from django.contrib import admin
from .models import Wallet, LedgerEntry


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "gold_balance")


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = (
        "wallet",
        "transaction_type",
        "gold_delta",
        "gold_balance_after",
        "fiat_amount",
        "fiat_currency",
        "created_at",
    )
    list_filter = ("transaction_type", "fiat_currency")
    search_fields = ("wallet__user__email", "description")
