from django.contrib import admin
from .models import GoldPriceConfig, GoldPriceSnapshot


@admin.register(GoldPriceConfig)
class GoldPriceConfigAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "safeguard_margin",
        "spread_margin",
    )

    readonly_fields = ()

    fieldsets = (
        ("Gold Pricing Margins", {
            "fields": ("safeguard_margin", "spread_margin"),
        }),
    )


@admin.register(GoldPriceSnapshot)
class GoldPriceSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "usd_per_ounce",
        "usd_pkr_rate",
        "pkr_per_gram_final",
        "pkr_per_tola_final",
        "pkr_per_ounce_final",
    )

    readonly_fields = (
        "timestamp",
        "usd_per_ounce",
        "usd_pkr_rate",
        "pkr_per_ounce_raw",
        "pkr_per_gram_raw",
        "pkr_per_tola_raw",
        "pkr_per_ounce_final",
        "pkr_per_gram_final",
        "pkr_per_tola_final",
    )

    fieldsets = (
        ("Timestamp", {"fields": ("timestamp",)}),

        ("Raw FX & Spot Data", {
            "fields": ("usd_per_ounce", "usd_pkr_rate")
        }),

        ("Raw PKR Values", {
            "fields": (
                "pkr_per_ounce_raw",
                "pkr_per_gram_raw",
                "pkr_per_tola_raw",
            )
        }),

        ("Final PKR Values (After Margins)", {
            "fields": (
                "pkr_per_ounce_final",
                "pkr_per_gram_final",
                "pkr_per_tola_final",
            )
        }),
    )
