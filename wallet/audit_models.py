from django.db import models
from django.conf import settings


class OrderAuditLog(models.Model):
    # -----------------------------
    # Event Types
    # -----------------------------
    EVENT_LOCK_CREATED = "LOCK_CREATED"
    EVENT_LOCK_EXPIRED = "LOCK_EXPIRED"
    EVENT_EXECUTED = "EXECUTED"
    EVENT_CANCELLED_BY_USER = "CANCELLED_BY_USER"
    EVENT_PAYMENT_FAILED = "PAYMENT_FAILED"
    EVENT_REVERSAL_COMPLETED = "REVERSAL_COMPLETED"

    EVENT_TYPES = [
        (EVENT_LOCK_CREATED, "Lock Created"),
        (EVENT_LOCK_EXPIRED, "Lock Expired"),
        (EVENT_EXECUTED, "Executed"),
        (EVENT_CANCELLED_BY_USER, "Cancelled By User"),
        (EVENT_PAYMENT_FAILED, "Payment Failed"),
        (EVENT_REVERSAL_COMPLETED, "Reversal Completed"),
    ]

    # -----------------------------
    # Core Fields
    # -----------------------------
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="order_audit_logs"
    )

    # Generic reference to Buy or Sell order
    order_id = models.CharField(max_length=100)
    order_type = models.CharField(
        max_length=10,
        choices=[("BUY", "Buy"), ("SELL", "Sell")]
    )

    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    description = models.TextField(blank=True, null=True)

    # Snapshot of values at moment of event
    price_per_gram = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    gold_quantity_grams = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)

    # Extra structured details
    metadata = models.JSONField(default=dict, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"[{self.event_type}] {self.order_type} {self.order_id} — {self.user}"
