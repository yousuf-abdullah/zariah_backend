from decimal import Decimal
import yfinance as yf
from django.utils import timezone
from .models import GoldPriceSnapshot


class GoldPriceService:
    """
    Service for fetching gold prices, converting units, applying safeguard and spread margins.
    Uses free & legal Yahoo Finance endpoints:
    - GC=F  : COMEX Gold Futures (USD/oz)
    - PKR=X : USD→PKR FX rate
    """

    OUNCE_TO_TOLA = Decimal("2.430555")  # 1 tola = 11.664g → 1oz = 31.1035g → oz/tola ratio
    OUNCE_TO_GRAM = Decimal("31.1035")

    def __init__(self):
        pass

    # ------------------------------------------------------------
    # FETCH USD → PKR FX RATE
    # ------------------------------------------------------------
    def _fetch_usd_pkr(self) -> Decimal:
        """
        Fetch USD to PKR conversion using Yahoo Finance (PKR=X)
        """
        ticker = yf.Ticker("PKR=X")
        hist = ticker.history(period="1d")

        if hist.empty:
            raise RuntimeError("Could not fetch USD/PKR rate (PKR=X).")

        fx = hist["Close"].iloc[-1]
        return Decimal(str(fx)).quantize(Decimal("0.0001"))

    # ------------------------------------------------------------
    # FETCH GOLD PRICE (USD PER OUNCE)
    # ------------------------------------------------------------
    def _fetch_future_gold_ounce_usd(self) -> Decimal:
        """
        Fetch COMEX Gold Futures (GC=F) as a proxy for spot gold.
        This is free, legal, stable, and serves well for dev environments.
        """
        ticker = yf.Ticker("GC=F")
        hist = ticker.history(period="1d")

        if hist.empty:
            raise RuntimeError("Could not fetch GC=F gold futures price.")

        price = hist["Close"].iloc[-1]
        return Decimal(str(price)).quantize(Decimal("0.01"))

    # ------------------------------------------------------------
    # MAIN SNAPSHOT BUILDER
    # ------------------------------------------------------------
    def get_snapshot(self) -> GoldPriceSnapshot:
        """
        Fetches:
        - Gold price (USD/oz)
        - USD→PKR FX rate
        Converts to:
        - PKR/oz
        - PKR/tola
        - PKR/gm

        Applies:
        - safeguard % (configurable in DB)
        - spread % (configurable)

        Saves snapshot to DB and returns it.
        """

        # Fetch base prices
        usd_per_ounce = self._fetch_future_gold_ounce_usd()
        usd_pkr_rate = self._fetch_usd_pkr()

        # Conversions
        pkr_per_ounce = (usd_per_ounce * usd_pkr_rate).quantize(Decimal("1.0000"))
        pkr_per_gram = (pkr_per_ounce / self.OUNCE_TO_GRAM).quantize(Decimal("1.0000"))
        pkr_per_tola = (pkr_per_ounce / self.OUNCE_TO_TOLA).quantize(Decimal("1.0000"))

        # Load margins from DB — create if none exists
        from .models import GoldPriceConfig
        config = GoldPriceConfig.get_solo()

        # Safeguard margin
        safeguard_multiplier = (Decimal("1") + config.safeguard_margin / Decimal("100"))
        pkr_per_ounce_safeguarded = (pkr_per_ounce * safeguard_multiplier).quantize(Decimal("1.0000"))

        # Spread margin
        spread_multiplier = (Decimal("1") + config.spread_margin / Decimal("100"))
        pkr_per_ounce_with_spread = (pkr_per_ounce_safeguarded * spread_multiplier).quantize(Decimal("1.0000"))

        # Final selling prices for UI
        final_price_ounce = pkr_per_ounce_with_spread
        final_price_gram = (final_price_ounce / self.OUNCE_TO_GRAM).quantize(Decimal("1.0000"))
        final_price_tola = (final_price_ounce / self.OUNCE_TO_TOLA).quantize(Decimal("1.0000"))

        # Save snapshot
        snapshot = GoldPriceSnapshot.objects.create(
            timestamp=timezone.now(),
            usd_per_ounce=usd_per_ounce,
            usd_pkr_rate=usd_pkr_rate,
            pkr_per_ounce_raw=pkr_per_ounce,
            pkr_per_gram_raw=pkr_per_gram,
            pkr_per_tola_raw=pkr_per_tola,
            pkr_per_ounce_final=final_price_ounce,
            pkr_per_gram_final=final_price_gram,
            pkr_per_tola_final=final_price_tola,
        )

        return snapshot
