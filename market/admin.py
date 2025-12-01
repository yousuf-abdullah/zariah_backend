from django.contrib import admin
from .models import GoldPriceConfig


@admin.register(GoldPriceConfig)
class GoldPriceConfigAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "safety_margin_pct",
        "buy_spread_pct",
        "gram_per_tola",
        "ounce_to_gram",
        "last_spot_ounce_usd",
        "last_usd_pkr",
        "last_computed_at",
    )
    readonly_fields = ("last_spot_ounce_usd", "last_usd_pkr", "last_computed_at")
