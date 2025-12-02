from django.db import models
from django.conf import settings
from decimal import Decimal
from django.utils import timezone


GRAM_PER_TOLA = Decimal("11.6638038")
MILLIGRAM = Decimal("0.001")  # For micro-purchases


# ----------------------------------------------------
# WALLET (Stores gold balance)
# ----------------------------------------------------
class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gold_balance_grams = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal("0.0"))

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet for {self.user}"

    # Display Helpers
    def grams(self):
        return self.gold_balance_grams

    def tola(self):
        return self.gold_balance_grams / GRAM_PER_TOLA

    def milligrams(self):
        return self.gold_balance_grams * Decimal("1000")


# ----------------------------------------------------
# WALLET TRANSACTIONS (Immutable ledger)
# ----------------------------------------------------
class WalletTransaction(models.Model):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"

    TRANSACTION_TYPES = [
        (CREDIT, "Credit"),
        (DEBIT, "Debit"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    tx_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)

    gold_amount_grams = models.DecimalField(max_digits=20, decimal_places=6)
    balance_after_tx = models.DecimalField(max_digits=20, decimal_places=6)

    reference = models.CharField(max_length=100, blank=True, null=True)  # order ID
    timestamp = models.DateTimeField(default=timezone.now)

    idempotency_key = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.tx_type} {self.gold_amount_grams}g → bal {self.balance_after_tx}g"


# ----------------------------------------------------
# BUY ORDER
# ----------------------------------------------------
class BuyOrder(models.Model):
    STATUS_PENDING_LOCKED = "PENDING_LOCKED"
    STATUS_EXECUTED = "EXECUTED"
    STATUS_EXPIRED = "EXPIRED"

    STATUS_CHOICES = [
        (STATUS_PENDING_LOCKED, "Pending Locked"),
        (STATUS_EXECUTED, "Executed"),
        (STATUS_EXPIRED, "Expired"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)

    # Amount of gold user wants (in grams)
    gold_quantity_grams = models.DecimalField(max_digits=20, decimal_places=6)

    # Snapshot reference for audit only
    snapshot_reference = models.ForeignKey(
        "market.GoldPriceSnapshot",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Locked values
    locked_price_per_gram = models.DecimalField(max_digits=20, decimal_places=4)
    total_pkr = models.DecimalField(max_digits=20, decimal_places=2)

    expires_at = models.DateTimeField(null=True, blank=True)
    locked_at = models.DateTimeField(null=True, blank=True)
    order_token = models.CharField(max_length=50, unique=True, null=True)


    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING_LOCKED)
    executed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Buy {self.gold_quantity_grams}g @ {self.locked_price_per_gram}"

# ----------------------------------------------------
# SELL ORDER
# ----------------------------------------------------
class SellOrder(models.Model):
    STATUS_PENDING_LOCKED = "PENDING_LOCKED"
    STATUS_EXECUTED = "EXECUTED"
    STATUS_EXPIRED = "EXPIRED"

    STATUS_CHOICES = [
        (STATUS_PENDING_LOCKED, "Pending Locked"),
        (STATUS_EXECUTED, "Executed"),
        (STATUS_EXPIRED, "Expired"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)

    gold_quantity_grams = models.DecimalField(max_digits=20, decimal_places=6)
    snapshot_reference = models.ForeignKey(
        "market.GoldPriceSnapshot",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    locked_price_per_gram = models.DecimalField(max_digits=20, decimal_places=4)
    total_pkr = models.DecimalField(max_digits=20, decimal_places=2)

    expires_at = models.DateTimeField(null=True, blank=True)
    locked_at = models.DateTimeField(null=True, blank=True)
    order_token = models.CharField(max_length=50, unique=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING_LOCKED)
    executed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Sell {self.gold_quantity_grams}g @ {self.locked_price_per_gram}"

