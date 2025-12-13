from decimal import Decimal
from django.db import models
from django.utils import timezone


# --------------------------------------------
# GOLD PRICE CONFIG (Singleton)
# --------------------------------------------
class GoldPriceConfig(models.Model):
    """
    Stores admin-adjustable margins and fees for gold pricing.
    There must always be exactly ONE active row.
    """

    min_buy_amount_pkr = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=Decimal("500.00")
    )

    lock_duration_seconds = models.PositiveIntegerField(default=60)

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

    # FEES
    buy_fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("3.00")
    )

    sell_fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00")
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Gold Config (min {self.min_buy_amount_pkr} PKR)"

    @classmethod
    def load(cls):
        config = cls.objects.filter(is_active=True).order_by("-updated_at").first()
        if not config:
            raise RuntimeError("GoldPriceConfig is not configured.")
        return config

    def save(self, *args, **kwargs):
        if self.is_active:
            GoldPriceConfig.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


# --------------------------------------------
# GOLD PRICE SNAPSHOT (Every minute)
# --------------------------------------------
class GoldPriceSnapshot(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)

    usd_per_ounce = models.DecimalField(max_digits=14, decimal_places=4)
    usd_pkr_rate = models.DecimalField(max_digits=14, decimal_places=4)

    pkr_per_ounce_raw = models.DecimalField(max_digits=18, decimal_places=4)
    pkr_per_gram_raw = models.DecimalField(max_digits=18, decimal_places=4)
    pkr_per_tola_raw = models.DecimalField(max_digits=18, decimal_places=4)

    pkr_per_ounce_final = models.DecimalField(max_digits=18, decimal_places=4)
    pkr_per_gram_final = models.DecimalField(max_digits=18, decimal_places=4)
    pkr_per_tola_final = models.DecimalField(max_digits=18, decimal_places=4)

    def __str__(self):
        return f"Snapshot @ {self.timestamp}"


# --------------------------------------------
# DAILY CLOSING PRICE (Once per day)
# --------------------------------------------
class DailyClosingPrice(models.Model):
    date = models.DateField(unique=True)

    closing_ounce = models.DecimalField(max_digits=14, decimal_places=4)
    closing_gram = models.DecimalField(max_digits=14, decimal_places=4)
    closing_tola = models.DecimalField(max_digits=14, decimal_places=4)

    source_snapshot = models.ForeignKey(
        GoldPriceSnapshot,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Closing Price for {self.date}"
