from django.db import models
from django.conf import settings
from decimal import Decimal


class Wallet(models.Model):
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gold_balance = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=Decimal("0"),
        help_text="Total gold held by the user (in grams, 8 decimal precision).",
    )

    def __str__(self):
        return f"{self.user.email} - {self.gold_balance} g"


class LedgerEntry(models.Model):
    """
    Immutable audit record of changes in gold holdings.
    E.g. BUY adds gold, SELL removes gold, ADJUST/REFERRAL modify balance.
    """
    TRANSACTION_TYPES = [
        ("BUY", "Buy Gold"),
        ("SELL", "Sell Gold"),
        ("ADJUST", "Admin Adjustment"),
        ("REFERRAL", "Referral Gold Credit"),
    ]

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="ledger",
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)

    # Gold change: positive for added, negative for removed
    gold_delta = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        help_text="Change in gold quantity. Positive for buy/credit, negative for sell/debit.",
    )

    # Gold balance after this entry
    gold_balance_after = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        help_text="Gold balance after applying this ledger entry.",
    )

    # Optional fiat information for audit/statement purposes only
    fiat_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Fiat value (e.g. PKR) of this operation, for audit only.",
    )
    fiat_currency = models.CharField(
        max_length=3,
        default="PKR",
        help_text="ISO currency code, e.g. PKR.",
    )

    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.transaction_type} {self.gold_delta} g"
