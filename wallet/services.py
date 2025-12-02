from decimal import Decimal
from django.db import transaction, IntegrityError
from django.utils import timezone
import uuid

from .models import Wallet, WalletTransaction, BuyOrder, SellOrder
from market.models import GoldPriceSnapshot


class WalletEngine:

    # --------------------------------------------------------
    # AUTO CREATE WALLET (called when user registers)
    # --------------------------------------------------------
    @staticmethod
    def create_wallet_for_user(user):
        wallet, created = Wallet.objects.get_or_create(user=user)
        return wallet

    # --------------------------------------------------------
    # ATOMIC CREDIT (add gold to wallet)
    # --------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def credit(wallet: Wallet, grams: Decimal, reference: str) -> WalletTransaction:
        wallet.gold_balance_grams += grams
        wallet.save()

        tx = WalletTransaction.objects.create(
            user=wallet.user,
            wallet=wallet,
            tx_type=WalletTransaction.CREDIT,
            gold_amount_grams=grams,
            balance_after_tx=wallet.gold_balance_grams,
            reference=reference,
            idempotency_key=str(uuid.uuid4())
        )

        return tx

    # --------------------------------------------------------
    # ATOMIC DEBIT (remove gold from wallet)
    # --------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def debit(wallet: Wallet, grams: Decimal, reference: str) -> WalletTransaction:
        if wallet.gold_balance_grams < grams:
            raise ValueError("Insufficient gold balance")

        wallet.gold_balance_grams -= grams
        wallet.save()

        tx = WalletTransaction.objects.create(
            user=wallet.user,
            wallet=wallet,
            tx_type=WalletTransaction.DDEBIT,
            gold_amount_grams=grams,
            balance_after_tx=wallet.gold_balance_grams,
            reference=reference,
            idempotency_key=str(uuid.uuid4())
        )

        return tx

    # --------------------------------------------------------
    # CREATE BUY ORDER (but not executed yet)
    # --------------------------------------------------------
    @staticmethod
    def create_buy_order(user, grams: Decimal, snapshot_id: int):
        snap = GoldPriceSnapshot.objects.get(id=snapshot_id)

        order = BuyOrder.objects.create(
            user=user,
            wallet=user.wallet,
            gold_quantity_grams=grams,
            price_per_gram=snap.price_per_gram,
            total_pkr=grams * snap.price_per_gram,
            snapshot_reference=snap
        )

        return order

    # --------------------------------------------------------
    # EXECUTE BUY ORDER (lock price & credit wallet)
    # --------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def execute_buy_order(order: BuyOrder):

        if order.is_executed:
            return order  # idempotent

        wallet = order.wallet

        # Credit gold to wallet
        WalletEngine.credit(
            wallet,
            grams=order.gold_quantity_grams,
            reference=f"BUY-{order.id}"
        )

        order.is_executed = True
        order.executed_at = timezone.now()
        order.save()

        return order

    # --------------------------------------------------------
    # CREATE SELL ORDER
    # --------------------------------------------------------
    @staticmethod
    def create_sell_order(user, grams: Decimal, snapshot_id: int):
        wallet = user.wallet

        if wallet.gold_balance_grams < grams:
            raise ValueError("Not enough gold to sell")

        snap = GoldPriceSnapshot.objects.get(id=snapshot_id)

        order = SellOrder.objects.create(
            user=user,
            wallet=wallet,
            gold_quantity_grams=grams,
            price_per_gram=snap.price_per_gram,
            total_pkr=grams * snap.price_per_gram,
            snapshot_reference=snap
        )

        return order

    # --------------------------------------------------------
    # EXECUTE SELL ORDER (debit wallet)
    # --------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def execute_sell_order(order: SellOrder):

        if order.is_executed:
            return order  # idempotent

        wallet = order.wallet

        # Debit gold
        WalletEngine.debit(
            wallet,
            grams=order.gold_quantity_grams,
            reference=f"SELL-{order.id}"
        )

        order.is_executed = True
        order.executed_at = timezone.now()
        order.save()

        return order
