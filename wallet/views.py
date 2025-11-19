from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Wallet
from .serializers import WalletSerializer, LedgerSerializer


class WalletView(generics.GenericAPIView):
    """
    Returns the user's current gold balance.
    """
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wallet = Wallet.objects.get(user=request.user)
        serializer = self.get_serializer(wallet)
        return Response(serializer.data)


class WalletLedgerView(generics.GenericAPIView):
    """
    Returns the user's gold ledger entries (most recent first).
    """
    serializer_class = LedgerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wallet = Wallet.objects.get(user=request.user)
        ledger_qs = wallet.ledger.all()
        serializer = self.get_serializer(ledger_qs, many=True)
        return Response(serializer.data)
