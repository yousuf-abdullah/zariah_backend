from decimal import Decimal
from django.db import models
from django.utils import timezone


class GoldPriceConfig(models.Model):
    """
    Stores platform-wide parameters for gold pricing.

    - safety_margin_pct: extra % added on top of spot PKR price as a safeguard
    - buy_spread_pct: extra % the user pays when BUYING gold on top of the internal for-sale price
    - gram_per_tola: conversion factor between grams and tola
    - ounce_to_gram: conversion factor between troy ounce and gram
    """

    name = models.CharField(max_length=50, default="default", unique=True)

    safety_margin_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("2.00"),
        help_text="Safeguard % added to spot PKR price before setting internal for-sale price."
    )
    buy_spread_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("3.00"),
        help_text="Additional % charged when a user BUYS gold (on top of internal for-sale price)."
    )

    # If later you want a separate sell spread, you can add it here.
    # For now SELL price = internal for-sale price (no extra spread).

    gram_per_tola = models.DecimalField(
        max_digits=8, decimal_places=4, default=Decimal("11.6638"),
        help_text="Number of grams in one tola."
    )
    ounce_to_gram = models.DecimalField(
        max_digits=10, decimal_places=7, default=Decimal("31.1034768"),
        help_text="Number of grams in one troy ounce."
    )

    # Optional: last cached values (for debugging / future caching)
    last_spot_ounce_usd = models.DecimalField(
        max_digits=12, decimal_places=4, null=True, blank=True
    )
    last_usd_pkr = models.DecimalField(
        max_digits=12, decimal_places=4, null=True, blank=True
    )
    last_computed_at = models.DateTimeField(null=True, blank=True)

    cache_ttl_seconds = models.PositiveIntegerField(
        default=300,
        help_text="How long (in seconds) to reuse cached FX & spot prices before refetching."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Gold Price Config"
        verbose_name_plural = "Gold Price Config"

    def __str__(self) -> str:
        return f"GoldPriceConfig({self.name})"

    @classmethod
    def get_active(cls) -> "GoldPriceConfig":
        """
        Always return a single active config.
        Creates a default one if it doesn't exist.
        """
        obj, _ = cls.objects.get_or_create(name="default")
        return obj

    def should_refresh_cache(self) -> bool:
        if not self.last_computed_at:
            return True
        delta = timezone.now() - self.last_computed_at
        return delta.total_seconds() > self.cache_ttl_seconds
