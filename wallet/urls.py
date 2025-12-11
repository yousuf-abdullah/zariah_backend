from django.urls import path

from .views import (
    WalletBalanceView,
    WalletLedgerView,
    BuyLockView,
    BuyConfirmView,
    SellLockView,
    SellConfirmView,
)

urlpatterns = [
    path("balance/", WalletBalanceView.as_view()),
    path("ledger/", WalletLedgerView.as_view()),

    # NEW BUY/SELL SYSTEM
    path("buy/lock/", BuyLockView.as_view()),
    path("buy/confirm/", BuyConfirmView.as_view()),
    path("sell/lock/", SellLockView.as_view()),
    path("sell/confirm/", SellConfirmView.as_view()),
]
