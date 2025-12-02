from django.contrib import admin
from .models import GoldPriceConfig, GoldPriceSnapshot, DailyClosingPrice


# --------------------------------------------
# GOLD PRICE CONFIG ADMIN (Singleton)
# --------------------------------------------
@admin.register(GoldPriceConfig)
class GoldPriceConfigAdmin(admin.ModelAdmin):
    list_display = ("id", "safeguard_margin", "spread_margin")
    readonly_fields = ("id",)
    fieldsets = (
        ("Margins", {
            "fields": ("safeguard_margin", "spread_margin"),
            "description": "Adjust these cautiously."
        }),
    )

    def has_add_permission(self, request):
        # Only allow one row
        return not GoldPriceConfig.objects.exists()


# --------------------------------------------
# SNAPSHOT ADMIN (Every 60 seconds)
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
    search_fields = ("timestamp",)
    readonly_fields = [f.name for f in GoldPriceSnapshot._meta.fields]
    ordering = ("-timestamp",)


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
    readonly_fields = [f.name for f in DailyClosingPrice._meta.fields if f != "source_snapshot"]
    search_fields = ("date",)
