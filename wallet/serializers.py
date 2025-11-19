from rest_framework import serializers
from .models import Wallet, LedgerEntry


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["gold_balance"]


class LedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerEntry
        fields = [
            "transaction_type",
            "gold_delta",
            "gold_balance_after",
            "fiat_amount",
            "fiat_currency",
            "description",
            "created_at",
        ]
