from decimal import Decimal
import uuid

from django.db import transaction

from .models import Wallet, WalletTransaction, GoldInventory


# ----------------------------------------------
# WALLET ENGINE
# ----------------------------------------------
class WalletEngine:

    @staticmethod
    @transaction.atomic
    def credit(wallet: Wallet, grams: Decimal, reference: str):
        if grams <= 0:
            raise ValueError("Credit grams must be positive")

        wallet.gold_balance_grams += grams
        wallet.save(update_fields=["gold_balance_grams"])

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
        if grams <= 0:
            raise ValueError("Debit grams must be positive")

        if wallet.gold_balance_grams < grams:
            raise ValueError("Insufficient gold balance")

        wallet.gold_balance_grams -= grams
        wallet.save(update_fields=["gold_balance_grams"])

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
        inventory, _ = GoldInventory.objects.get_or_create(id=1)
        return inventory

    @staticmethod
    @transaction.atomic
    def reserve(grams: Decimal):
        if grams <= 0:
            raise ValueError("Reserve grams must be positive")

        inv = InventoryEngine.get_inventory()

        if grams > inv.available_grams:
            raise ValueError("Insufficient inventory to reserve gold")

        inv.reserved_grams += grams
        inv.save(update_fields=["reserved_grams"])
        return inv

    @staticmethod
    @transaction.atomic
    def release(grams: Decimal):
        if grams <= 0:
            return InventoryEngine.get_inventory()

        inv = InventoryEngine.get_inventory()
        inv.reserved_grams = max(inv.reserved_grams - grams, Decimal("0"))
        inv.save(update_fields=["reserved_grams"])
        return inv

    @staticmethod
    @transaction.atomic
    def reduce_total(grams: Decimal):
        if grams <= 0:
            raise ValueError("Reduce grams must be positive")

        inv = InventoryEngine.get_inventory()

        if grams > inv.total_grams:
            raise ValueError("Insufficient total inventory")

        inv.total_grams -= grams
        inv.save(update_fields=["total_grams"])
        return inv

    @staticmethod
    @transaction.atomic
    def increase_total(grams: Decimal):
        if grams <= 0:
            raise ValueError("Increase grams must be positive")

        inv = InventoryEngine.get_inventory()
        inv.total_grams += grams
        inv.save(update_fields=["total_grams"])
        return inv