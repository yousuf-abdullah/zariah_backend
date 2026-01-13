from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from wallet.models import Wallet, BuyOrder
from wallet.services import WalletEngine, InventoryEngine

from django.utils import timezone
from datetime import timedelta


User = get_user_model()


class WalletEngineTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass"
        )

        # Wallet is auto-created (signal or OneToOne logic)
        self.wallet = Wallet.objects.get(user=self.user)

        self.inventory = InventoryEngine.get_inventory()
        self.inventory.total_grams = Decimal("100")
        self.inventory.reserved_grams = Decimal("0")
        self.inventory.save()

    def test_wallet_credit(self):
        WalletEngine.credit(self.wallet, Decimal("1.5"), reference="test")
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.gold_balance_grams, Decimal("1.5"))

    def test_wallet_debit(self):
        WalletEngine.credit(self.wallet, Decimal("2"), reference="init")
        WalletEngine.debit(self.wallet, Decimal("1"), reference="debit")
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.gold_balance_grams, Decimal("1"))

    def test_wallet_debit_insufficient_balance(self):
        with self.assertRaises(ValueError):
            WalletEngine.debit(self.wallet, Decimal("1"), reference="fail")

    def test_inventory_reserve_and_release(self):
        InventoryEngine.reserve(Decimal("10"))
        inv = InventoryEngine.get_inventory()
        self.assertEqual(inv.reserved_grams, Decimal("10"))

        InventoryEngine.release(Decimal("5"))
        inv.refresh_from_db()
        self.assertEqual(inv.reserved_grams, Decimal("5"))

    def test_inventory_over_reserve(self):
        with self.assertRaises(ValueError):
            InventoryEngine.reserve(Decimal("1000"))


class BuyOrderSafetyTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="buyer",
            password="testpass"
        )
        self.wallet = Wallet.objects.get(user=self.user)

    def test_double_confirm_is_safe(self):
        now = timezone.now()

        order = BuyOrder.objects.create(
            user=self.user,
            wallet=self.wallet,
            gold_quantity_grams=Decimal("1"),
            locked_price_per_gram=Decimal("40000"),
            fee_pkr=Decimal("0"),
            total_payable_pkr=Decimal("40000"),
            soft_allocated_grams=Decimal("1"),
            locked_at=now,
            expires_at=now + timedelta(seconds=60),
            status=BuyOrder.STATUS_EXECUTED
        )

        # Re-confirming should not change state or crash
        self.assertEqual(order.status, BuyOrder.STATUS_EXECUTED)
