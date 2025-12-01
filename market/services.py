from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict

from django.utils import timezone

import yfinance as yf  # type: ignore

from .models import GoldPriceConfig


# ---------- Helpers ----------


def _to_decimal(value) -> Decimal:
    """
    Convert floats / np types to Decimal safely via string.
    """
    return Decimal(str(value))


def _round4(value: Decimal) -> Decimal:
    """
    Round to 4 decimal places for storage / API.
    """
    return value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


@dataclass
class GoldPriceSnapshot:
    """
    Computed prices in PKR for different units.
    All values already include safeguard and spreads.
    """
    spot_ounce_usd: Decimal
    usd_pkr: Decimal

    mid_price_per_gram_pkr: Decimal  # internal for-sale price (after safeguard)
    buy_price_per_gram_pkr: Decimal  # user pays this when buying
    sell_price_per_gram_pkr: Decimal  # user receives this when selling

    gram_per_tola: Decimal
    ounce_to_gram: Decimal

    @property
    def as_dict(self) -> Dict:
        """
        Shape we will return from the API.
        """
        gram = {
            "mid": _round4(self.mid_price_per_gram_pkr),
            "buy": _round4(self.buy_price_per_gram_pkr),
            "sell": _round4(self.sell_price_per_gram_pkr),
        }

        tola_grams = self.gram_per_tola
        ounce_grams = self.ounce_to_gram

        def scale(unit_grams: Decimal) -> Dict[str, Decimal]:
            return {
                "mid": _round4(self.mid_price_per_gram_pkr * unit_grams),
                "buy": _round4(self.buy_price_per_gram_pkr * unit_grams),
                "sell": _round4(self.sell_price_per_gram_pkr * unit_grams),
            }

        return {
            "meta": {
                "spot_ounce_usd": _round4(self.spot_ounce_usd),
                "usd_pkr": _round4(self.usd_pkr),
                "gram_per_tola": _round4(self.gram_per_tola),
                "ounce_to_gram": _round4(self.ounce_to_gram),
            },
            "per_gram": gram,
            "per_tola": scale(tola_grams),
            "per_ounce": scale(ounce_grams),
        }


class GoldPriceService:
    """
    Encapsulates the business logic for converting international spot price
    into PKR prices (gram / tola / ounce) with safeguard & spreads applied.

    High level steps:

    1) Fetch USD/PKR FX rate (yfinance, USDPKR=X)
    2) Fetch XAUUSD spot price per troy ounce (yfinance, XAUUSD=X)
    3) Convert ounce price (USD) -> PKR/gram
    4) Add safeguard margin (config.safety_margin_pct) => mid price
    5) Add buy spread (config.buy_spread_pct) => buy price
       Sell price = mid price (for now, no extra sell spread)
    """

    FX_SYMBOL = "USDPKR=X"     # USD/PKR from yfinance
    GOLD_SYMBOL = "XAUUSD=X"   # Gold spot XAUUSD from yfinance

    def __init__(self, config: GoldPriceConfig | None = None) -> None:
        self.config = config or GoldPriceConfig.get_active()

    # ---- External data fetchers ----

    def _fetch_usd_pkr_rate(self) -> Decimal:
        """
        Fetch USD/PKR rate from yfinance.
        """
        ticker = yf.Ticker(self.FX_SYMBOL)
        hist = ticker.history(period="1d")
        if hist.empty:
            raise RuntimeError("Could not fetch USD/PKR rate from yfinance.")
        last_close = hist["Close"].iloc[-1]
        return _to_decimal(last_close)

    def _fetch_spot_ounce_usd(self) -> Decimal:
        """
        Fetch XAUUSD spot (USD per troy ounce) from yfinance.
        """
        ticker = yf.Ticker(self.GOLD_SYMBOL)
        hist = ticker.history(period="1d")
        if hist.empty:
            raise RuntimeError("Could not fetch XAUUSD spot price from yfinance.")
        last_close = hist["Close"].iloc[-1]
        return _to_decimal(last_close)

    # ---- Public API ----

    def get_snapshot(self) -> GoldPriceSnapshot:
        """
        Get a GoldPriceSnapshot, optionally reusing cached data based on config.
        """

        if not self.config.should_refresh_cache():
            # Use cached values
            if (
                self.config.last_spot_ounce_usd is not None
                and self.config.last_usd_pkr is not None
            ):
                spot_ounce_usd = self.config.last_spot_ounce_usd
                usd_pkr = self.config.last_usd_pkr
            else:
                # Fallback: force refresh
                spot_ounce_usd = self._fetch_spot_ounce_usd()
                usd_pkr = self._fetch_usd_pkr_rate()
        else:
            spot_ounce_usd = self._fetch_spot_ounce_usd()
            usd_pkr = self._fetch_usd_pkr_rate()

            # update cache in DB
            self.config.last_spot_ounce_usd = spot_ounce_usd
            self.config.last_usd_pkr = usd_pkr
            self.config.last_computed_at = timezone.now()
            self.config.save(update_fields=[
                "last_spot_ounce_usd",
                "last_usd_pkr",
                "last_computed_at",
            ])

        ounce_to_gram = self.config.ounce_to_gram
        gram_per_tola = self.config.gram_per_tola

        # Step 3: USD/ounce -> PKR/gram
        # (spot_ounce_usd * usd_pkr) gives PKR per ounce.
        pkr_per_ounce = spot_ounce_usd * usd_pkr
        base_pkr_per_gram = pkr_per_ounce / ounce_to_gram

        # Step 4: add safeguard margin
        safety_factor = Decimal("1") + (self.config.safety_margin_pct / Decimal("100"))
        mid_price_per_gram = base_pkr_per_gram * safety_factor

        # Step 5: buy spread
        buy_factor = Decimal("1") + (self.config.buy_spread_pct / Decimal("100"))
        buy_price_per_gram = mid_price_per_gram * buy_factor

        # For now: sell price = mid price (no additional sell spread)
        sell_price_per_gram = mid_price_per_gram

        return GoldPriceSnapshot(
            spot_ounce_usd=spot_ounce_usd,
            usd_pkr=usd_pkr,
            mid_price_per_gram_pkr=mid_price_per_gram,
            buy_price_per_gram_pkr=buy_price_per_gram,
            sell_price_per_gram_pkr=sell_price_per_gram,
            gram_per_tola=gram_per_tola,
            ounce_to_gram=ounce_to_gram,
        )
