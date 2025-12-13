from django.db import models
from django.conf import settings
from decimal import Decimal
from django.utils import timezone

# -----------------------------
# CONSTANTS
# -----------------------------
GRAM_PER_TOLA = Decimal("11.6638038")


# -----------------------------
# WALLET MODEL
# -----------------------------
class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gold_balance_grams = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal("0.0"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet for {self.user.email}"

    def grams(self):
        return self.gold_balance_grams

    def tola(self):
        return self.gold_balance_grams / GRAM_PER_TOLA

    def milligrams(self):
        return self.gold_balance_grams * Decimal("1000")


# -----------------------------
# WALLET TRANSACTION LEDGER
# -----------------------------
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

    reference = models.CharField(max_length=200, null=True, blank=True)
    idempotency_key = models.CharField(max_length=200, unique=True)

    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.tx_type} {self.gold_amount_grams}g ({self.reference})"


# -----------------------------
# BUY ORDER
# -----------------------------
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

    gold_quantity_grams = models.DecimalField(max_digits=20, decimal_places=6)
    locked_price_per_gram = models.DecimalField(max_digits=20, decimal_places=6, default=0)

    fee_pkr = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_payable_pkr = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    soft_allocated_grams = models.DecimalField(max_digits=20, decimal_places=8, default=0)

    snapshot_reference = models.ForeignKey(
        "market.GoldPriceSnapshot",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    locked_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    executed_at = models.DateTimeField(null=True, blank=True)

    order_token = models.CharField(max_length=100, unique=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING_LOCKED)

    def __str__(self):
        return f"BuyOrder({self.order_token})"


# -----------------------------
# SELL ORDER
# -----------------------------
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
    locked_price_per_gram = models.DecimalField(max_digits=20, decimal_places=6, default=0)

    fee_pkr = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_payable_pkr = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    soft_allocated_grams = models.DecimalField(max_digits=20, decimal_places=8, default=0)

    snapshot_reference = models.ForeignKey(
        "market.GoldPriceSnapshot",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    locked_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    executed_at = models.DateTimeField(null=True, blank=True)

    order_token = models.CharField(max_length=100, unique=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING_LOCKED)

    def __str__(self):
        return f"SellOrder({self.order_token})"


# -----------------------------
# GOLD INVENTORY
# -----------------------------
class GoldInventory(models.Model):
    total_grams = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    reserved_grams = models.DecimalField(max_digits=20, decimal_places=8, default=0)

    @property
    def available_grams(self):
        return self.total_grams - self.reserved_grams

    def __str__(self):
        return f"Inventory: {self.total_grams}g total / {self.reserved_grams}g reserved"