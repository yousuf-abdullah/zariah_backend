from django.contrib import admin
from .models import GoldPriceConfig, GoldPriceSnapshot, DailyClosingPrice


# --------------------------------------------
# GOLD PRICE CONFIG ADMIN (Singleton)
# --------------------------------------------
@admin.register(GoldPriceConfig)
class GoldPriceConfigAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "min_buy_amount_pkr",
        "buy_fee_percentage",
        "sell_fee_percentage",
        "safeguard_margin",
        "spread_margin",
        "is_active",
        "updated_at",
    )

    readonly_fields = ("id", "created_at", "updated_at")

    fieldsets = (
        ("Core Settings", {
            "fields": (
                "min_buy_amount_pkr",
                "lock_duration_seconds",
                "is_active",
            )
        }),
        ("Margins", {
            "fields": (
                "safeguard_margin",
                "spread_margin",
            )
        }),
        ("Fees", {
            "fields": (
                "buy_fee_percentage",
                "sell_fee_percentage",
            )
        }),
        ("Timestamps", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )

    def has_add_permission(self, request):
        # Enforce singleton
        return not GoldPriceConfig.objects.exists()


# --------------------------------------------
# GOLD PRICE SNAPSHOT ADMIN
# --------------------------------------------
@admin.register(GoldPriceSnapshot)
class GoldPriceSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "usd_per_ounce",
        "usd_pkr_rate",
        "pkr_per_gram_final",
        "pkr_per_tola_final",
    )

    list_filter = ("timestamp",)
    ordering = ("-timestamp",)
    readonly_fields = [f.name for f in GoldPriceSnapshot._meta.fields]


# --------------------------------------------
# DAILY CLOSING PRICE ADMIN
# --------------------------------------------
@admin.register(DailyClosingPrice)
class DailyClosingPriceAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "closing_gram",
        "closing_tola",
        "closing_ounce",
        "source_snapshot",
    )

    ordering = ("-date",)
    readonly_fields = [
        f.name for f in DailyClosingPrice._meta.fields
        if f.name != "source_snapshot"
    ]