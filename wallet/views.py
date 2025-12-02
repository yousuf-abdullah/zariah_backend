from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal

from .models import Wallet, WalletTransaction
from .services import WalletEngine
from market.models import GoldPriceSnapshot


class WalletBalanceView(APIView):
    def get(self, request):
        wallet = request.user.wallet

        return Response({
            "grams": wallet.grams(),
            "tola": wallet.tola(),
            "milligrams": wallet.milligrams(),
        })


class WalletLedgerView(APIView):
    def get(self, request):
        wallet = request.user.wallet
        tx = WalletTransaction.objects.filter(wallet=wallet).order_by("-timestamp")

        data = [{
            "type": t.tx_type,
            "grams": str(t.gold_amount_grams),
            "balance_after": str(t.balance_after_tx),
            "reference": t.reference,
            "timestamp": t.timestamp,
        } for t in tx]

        return Response(data)


class BuyGoldView(APIView):
    def post(self, request):
        try:
            grams = Decimal(request.data.get("grams"))
            snapshot_id = int(request.data.get("snapshot_id"))
        except:
            return Response({"error": "Invalid input"}, status=400)

        # Create buy order
        order = WalletEngine.create_buy_order(request.user, grams, snapshot_id)

        # Execute buy
        order = WalletEngine.execute_buy_order(order)

        return Response({
            "message": "Buy order executed",
            "grams": str(order.gold_quantity_grams),
            "price_per_gram": str(order.price_per_gram),
            "total_pkr": str(order.total_pkr),
        }, status=200)


class SellGoldView(APIView):
    def post(self, request):
        try:
            grams = Decimal(request.data.get("grams"))
            snapshot_id = int(request.data.get("snapshot_id"))
        except:
            return Response({"error": "Invalid input"}, status=400)

        try:
            order = WalletEngine.create_sell_order(request.user, grams, snapshot_id)
            order = WalletEngine.execute_sell_order(order)

            return Response({
                "message": "Sell order executed",
                "grams": str(order.gold_quantity_grams),
                "price_per_gram": str(order.price_per_gram),
                "total_pkr": str(order.total_pkr),
            })

        except ValueError as e:
            return Response({"error": str(e)}, status=400)
