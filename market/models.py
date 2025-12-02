from decimal import Decimal
from django.db import models


class GoldPriceConfig(models.Model):
    safeguard_margin = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("2.00")
    )
    spread_margin = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("3.00")
    )

    def __str__(self):
        return "Gold Price Configuration"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj


from decimal import Decimal
from django.db import models


class GoldPriceConfig(models.Model):
    safeguard_margin = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("2.00")
    )
    spread_margin = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("3.00")
    )

    def __str__(self):
        return "Gold Price Configuration"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj

class GoldPriceSnapshot(models.Model):
    timestamp = models.DateTimeField(null=True, blank=True)

    usd_per_ounce = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    usd_pkr_rate = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)

    pkr_per_ounce_raw = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    pkr_per_gram_raw = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    pkr_per_tola_raw = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)

    pkr_per_ounce_final = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    pkr_per_gram_final = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    pkr_per_tola_final = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)

    def __str__(self):
        return f"Gold Snapshot @ {self.timestamp}"

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