from django.urls import path
from .views import WalletView, WalletLedgerView

urlpatterns = [
    path("", WalletView.as_view(), name="wallet-detail"),
    path("ledger/", WalletLedgerView.as_view(), name="wallet-ledger"),
]
