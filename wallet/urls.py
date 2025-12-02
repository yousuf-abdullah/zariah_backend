from django.urls import path
from .views import WalletBalanceView, WalletLedgerView, BuyGoldView, SellGoldView

urlpatterns = [
    path("balance/", WalletBalanceView.as_view(), name="wallet-balance"),
    path("ledger/", WalletLedgerView.as_view(), name="wallet-ledger"),
    path("buy/", BuyGoldView.as_view(), name="wallet-buy"),
    path("sell/", SellGoldView.as_view(), name="wallet-sell"),
]
