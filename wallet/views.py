from decimal import Decimal
from uuid import uuid4
from datetime import timedelta

from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from market.models import GoldPriceSnapshot, GoldPriceConfig

from .models import Wallet, BuyOrder, SellOrder, WalletTransaction
from .services import WalletEngine, InventoryEngine

# -----------------------------
# BUY — LOCK
# -----------------------------
class BuyLockView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        
        user = request.user
        wallet = user.wallet

        amount_pkr = Decimal(request.data.get("amount_pkr"))

        config = GoldPriceConfig.load()
        min_buy = config.min_buy_amount_pkr
        fee_pct = config.buy_fee_percentage

        if amount_pkr < min_buy:
            return Response(
                {"error": f"Minimum buy amount is {min_buy} PKR"},
                status=400
            )

        snapshot = GoldPriceSnapshot.objects.latest("timestamp")
        price = snapshot.pkr_per_gram_final

        grams = amount_pkr / price
        fee_pkr = amount_pkr * fee_pct / 100
        total_payable = amount_pkr + fee_pkr

        # Reserve inventory BEFORE creating order
        InventoryEngine.reserve(grams)

        order = BuyOrder.objects.create(
            user=user,
            wallet=wallet,
            gold_quantity_grams=grams,
            locked_price_per_gram=price,
            fee_pkr=fee_pkr,
            total_payable_pkr=total_payable,
            soft_allocated_grams=grams,
            snapshot_reference=snapshot,
            locked_at=timezone.now(),
            expires_at=timezone.now() + timedelta(seconds=config.lock_duration_seconds),
            order_token=str(uuid4()),
        )

        return Response({
            "order_token": order.order_token,
            "locked_price_per_gram": str(price),
            "amount_pkr": str(amount_pkr),
            "fee_pkr": str(fee_pkr),
            "total_payable_pkr": str(total_payable),
            "gold_quantity_grams": str(grams),
            "expires_at": order.expires_at,
        })


# -----------------------------
# BUY — CONFIRM
# -----------------------------
class BuyConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("order_token")
        order = get_object_or_404(BuyOrder, order_token=token)

        if order.status != BuyOrder.STATUS_PENDING_LOCKED:
            return Response({"error": "Order cannot be confirmed"}, status=400)

        if timezone.now() > order.expires_at:
            InventoryEngine.release(order.soft_allocated_grams)
            order.status = BuyOrder.STATUS_EXPIRED
            order.save()
            return Response({"error": "Order expired"}, status=400)

        InventoryEngine.reduce_total(order.gold_quantity_grams)
        InventoryEngine.release(order.soft_allocated_grams)

        WalletEngine.credit(order.wallet, order.gold_quantity_grams, reference=order.order_token)

        order.status = BuyOrder.STATUS_EXECUTED
        order.executed_at = timezone.now()
        order.save()

        return Response({
            "status": "success",
            "gold_added_grams": str(order.gold_quantity_grams),
            "wallet_balance_grams": str(order.wallet.gold_balance_grams),
        })


# -----------------------------
# SELL — LOCK
# -----------------------------
class SellLockView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        user = request.user
        wallet = user.wallet

        # Extract grams to sell
        grams = Decimal(request.data.get("sell_grams"))

        # Validate available gold
        if wallet.gold_balance_grams < grams:
            return Response({"error": "Not enough gold to sell"}, status=400)

        # Load current config and pricing
        config = GoldPriceConfig.load()
        fee_pct = config.sell_fee_percentage

        snapshot = GoldPriceSnapshot.objects.latest("timestamp")
        price = snapshot.pkr_per_gram_final

        # Calculate PKR values
        gross_pkr = grams * price
        fee_pkr = gross_pkr * fee_pct / 100
        net_pkr = gross_pkr - fee_pkr

        # Soft debit (hold) the gold before creating order
        WalletEngine.debit(wallet, grams, reference="soft_sell_hold")

        # Create sell order
        order = SellOrder.objects.create(
            user=user,
            wallet=wallet,
            gold_quantity_grams=grams,
            soft_allocated_grams=grams,
            locked_price_per_gram=price,
            fee_pkr=fee_pkr,
            total_payable_pkr=net_pkr,
            snapshot_reference=snapshot,
            locked_at=timezone.now(),
            expires_at=timezone.now() + timedelta(seconds=config.lock_duration_seconds),
            order_token=str(uuid4()),
        )

        # Return response
        return Response({
            "order_token": order.order_token,
            "sell_grams": str(grams),
            "gross_pkr": str(gross_pkr),
            "fee_pkr": str(fee_pkr),
            "net_pkr": str(net_pkr),
            "locked_price_per_gram": str(price),
            "expires_at": order.expires_at
        })


# -----------------------------
# SELL — CONFIRM
# -----------------------------
class SellConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("order_token")
        order = get_object_or_404(SellOrder, order_token=token)

        if order.status != SellOrder.STATUS_PENDING_LOCKED:
            return Response({"error": "Order cannot be confirmed"}, status=400)

        if timezone.now() > order.expires_at:
            WalletEngine.credit(order.wallet, order.soft_allocated_grams, reference="sell_expire")
            order.status = SellOrder.STATUS_EXPIRED
            order.save()
            return Response({"error": "Order expired"}, status=400)

        InventoryEngine.increase_total(order.gold_quantity_grams)

        order.status = SellOrder.STATUS_EXECUTED
        order.executed_at = timezone.now()
        order.save()

        return Response({
            "status": "success",
            "net_pkr": str(order.total_payable_pkr),
        })

class WalletBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet = request.user.wallet
        return Response({
            "balance_grams": str(wallet.gold_balance_grams),
            "locked_grams": "0",
        })

class WalletLedgerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tx = WalletTransaction.objects.filter(
            wallet=request.user.wallet
        ).order_by("-timestamp")

        return Response(list(tx.values()))
