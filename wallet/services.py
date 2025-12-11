from decimal import Decimal
from django.db import transaction
from django.utils import timezone
import uuid

from .models import Wallet, WalletTransaction, GoldInventory


# ----------------------------------------------
# WALLET ENGINE
# ----------------------------------------------
class WalletEngine:

    @staticmethod
    @transaction.atomic
    def credit(wallet: Wallet, grams: Decimal, reference: str):
        wallet.gold_balance_grams += grams
        wallet.save()

        return WalletTransaction.objects.create(
            user=wallet.user,
            wallet=wallet,
            tx_type=WalletTransaction.CREDIT,
            gold_amount_grams=grams,
            balance_after_tx=wallet.gold_balance_grams,
            reference=reference,
            idempotency_key=str(uuid.uuid4())
        )

    @staticmethod
    @transaction.atomic
    def debit(wallet: Wallet, grams: Decimal, reference: str):
        if wallet.gold_balance_grams < grams:
            raise ValueError("Insufficient gold balance")

        wallet.gold_balance_grams -= grams
        wallet.save()

        return WalletTransaction.objects.create(
            user=wallet.user,
            wallet=wallet,
            tx_type=WalletTransaction.DEBIT,
            gold_amount_grams=grams,
            balance_after_tx=wallet.gold_balance_grams,
            reference=reference,
            idempotency_key=str(uuid.uuid4())
        )


# ----------------------------------------------
# INVENTORY ENGINE
# ----------------------------------------------
class InventoryEngine:

    @staticmethod
    def get_inventory():
        inv, _ = GoldInventory.objects.get_or_create(id=1)
        return inv

    @staticmethod
    def reserve(grams: Decimal):
        inv = InventoryEngine.get_inventory()
        if grams > inv.available_grams:
            raise ValueError("Insufficient inventory to reserve gold")
        inv.reserved_grams += grams
        inv.save()
        return inv

    @staticmethod
    def release(grams: Decimal):
        inv = InventoryEngine.get_inventory()
        inv.reserved_grams = max(inv.reserved_grams - grams, 0)
        inv.save()
        return inv

    @staticmethod
    def reduce_total(grams: Decimal):
        inv = InventoryEngine.get_inventory()
        inv.total_grams -= grams
        inv.save()
        return inv

    @staticmethod
    def increase_total(grams: Decimal):
        inv = InventoryEngine.get_inventory()
        inv.total_grams += grams
        inv.save()
        return inv