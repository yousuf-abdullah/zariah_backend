from decimal import Decimal
from django.db import models
from django.utils import timezone


# --------------------------------------------
# GOLD PRICE CONFIG (Singleton)
# --------------------------------------------
class GoldPriceConfig(models.Model):
    """
    Stores admin-adjustable margins for gold pricing.

    safeguard_margin (%): Added on top of raw PKR price before spread
    spread_margin (%): Added after safeguard to get BUY price

    There will always be exactly one row of this model.
    """
    
    lock_duration_seconds = models.IntegerField(default=60)

    safeguard_margin = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("2.00"),
        help_text="Percentage added before spread margin."
    )

    spread_margin = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("3.00"),
        help_text="Percentage added after safeguard margin."
    )

    def __str__(self):
        return "Gold Price Configuration"

    @classmethod
    def get_solo(cls):
        """
        Ensures there is always exactly one GoldPriceConfig row.
        """
        obj, _ = cls.objects.get_or_create(id=1)
        return obj


# --------------------------------------------
# GOLD PRICE SNAPSHOTS (Every 60 seconds)
# --------------------------------------------
class GoldPriceSnapshot(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)

    # Raw data
    usd_per_ounce = models.DecimalField(max_digits=14, decimal_places=4)
    usd_pkr_rate = models.DecimalField(max_digits=14, decimal_places=4)

    # Raw PKR conversions
    pkr_per_ounce_raw = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    pkr_per_gram_raw = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    pkr_per_tola_raw = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)

    # Final PKR values (after margins)
    pkr_per_ounce_final = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    pkr_per_gram_final = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    pkr_per_tola_final = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)

    def __str__(self):
        return f"Gold Snapshot @ {self.timestamp}"


# --------------------------------------------
# DAILY CLOSING PRICE (Stored once per day)
# --------------------------------------------
class DailyClosingPrice(models.Model):
    date = models.DateField(unique=True)
    closing_ounce = models.DecimalField(max_digits=14, decimal_places=4)
    closing_gram = models.DecimalField(max_digits=14, decimal_places=4)
    closing_tola = models.DecimalField(max_digits=14, decimal_places=4)

    source_snapshot = models.ForeignKey(
        GoldPriceSnapshot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Closing Price for {self.date}"
