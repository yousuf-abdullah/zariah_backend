from django.db import transaction
from decimal import Decimal
from .models import Wallet, LedgerEntry


def add_gold(
    wallet: Wallet,
    gold_amount: Decimal,
    fiat_amount: Decimal | None = None,
    description: str = "",
    transaction_type: str = "BUY",
) -> Wallet:
    """
    Increase the user's gold holdings.

    Typically called when:
    - A card/Easypaisa payment for BUY has been successfully confirmed.
    - Referral/reward gold is granted to the user.
    """
    if gold_amount <= 0:
        raise ValueError("Gold amount must be positive when adding gold.")

    with transaction.atomic():
        w = Wallet.objects.select_for_update().get(id=wallet.id)

        new_balance = w.gold_balance + gold_amount
        w.gold_balance = new_balance
        w.save()

        LedgerEntry.objects.create(
            wallet=w,
            transaction_type=transaction_type,
            gold_delta=gold_amount,
            gold_balance_after=new_balance,
            fiat_amount=fiat_amount,
            description=description,
        )

        return w


def remove_gold(
    wallet: Wallet,
    gold_amount: Decimal,
    fiat_amount: Decimal | None = None,
    description: str = "",
    transaction_type: str = "SELL",
) -> Wallet:
    """
    Decrease the user's gold holdings.

    Typically called when:
    - User sells gold and payout is sent to bank/Easypaisa.
    """
    if gold_amount <= 0:
        raise ValueError("Gold amount must be positive when removing gold.")

    with transaction.atomic():
        w = Wallet.objects.select_for_update().get(id=wallet.id)

        if w.gold_balance < gold_amount:
            raise ValueError("Insufficient gold balance.")

        new_balance = w.gold_balance - gold_amount
        w.gold_balance = new_balance
        w.save()

        # Note: gold_delta is negative for removal
        LedgerEntry.objects.create(
            wallet=w,
            transaction_type=transaction_type,
            gold_delta=-gold_amount,
            gold_balance_after=new_balance,
            fiat_amount=fiat_amount,
            description=description,
        )

        return w
