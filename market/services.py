from decimal import Decimal
import yfinance as yf
from django.utils import timezone
from .models import GoldPriceSnapshot, GoldPriceConfig


class GoldPriceService:
    """
    Clean, production-style gold pricing service.
    Responsibilities:
    - Fetch raw USD gold & USD→PKR
    - Compute PKR values
    - Apply safeguard + spread margins
    - Store snapshots (cron)
    - Provide latest snapshot (API)
    """

    OUNCE_TO_GRAM = Decimal("31.1035")
    GRAM_PER_TOLA = Decimal("11.6638038")

    # --------------------------------------------
    # 1. Fetch live market prices
    # --------------------------------------------
    def fetch_live_prices(self):
        """
        Most reliable fetch strategy for yfinance:
        1. Try fast_info (fast, but unreliable)
        2. Fallback to history() (slower, but very reliable)
        """

        try:
            gold = yf.Ticker("GC=F")
            fx = yf.Ticker("PKR=X")

            # --------------------------------------------
            # 1) TRY FAST_INFO
            # --------------------------------------------
            gold_fast = gold.fast_info.get("last_price")
            fx_fast = fx.fast_info.get("last_price")

            if gold_fast is not None and fx_fast is not None:
                return Decimal(str(gold_fast)), Decimal(str(fx_fast))

            # --------------------------------------------
            # 2) FALLBACK TO HISTORY
            # --------------------------------------------
            gold_hist = gold.history(period="1d", interval="1m")
            fx_hist = fx.history(period="1d", interval="1m")

            if gold_hist.empty or fx_hist.empty:
                raise ValueError("history() returned empty data for gold or PKR.")

            gold_price = gold_hist["Close"].iloc[-1]
            fx_price = fx_hist["Close"].iloc[-1]

            if gold_price is None or fx_price is None:
                raise ValueError("history() returned None values for close prices.")

            return Decimal(str(gold_price)), Decimal(str(fx_price))

        except Exception as e:
            raise RuntimeError(f"Failed to fetch live prices via yfinance: {e}")


    # --------------------------------------------
    # 2. Compute PKR prices with margins
    # --------------------------------------------
    def compute_prices(self, usd_per_ounce, usd_pkr_rate):
        """
        Converts raw USD prices into PKR (raw + final).
        Applies safeguard + spread margins.
        """

        # Raw PKR conversions
        pkr_per_ounce = usd_per_ounce * usd_pkr_rate
        pkr_per_gram = pkr_per_ounce / self.OUNCE_TO_GRAM
        pkr_per_tola = pkr_per_gram * self.GRAM_PER_TOLA

        # Apply margins
        config = GoldPriceConfig.load()
        safeguard = (Decimal("1.00") + config.safeguard_margin / Decimal("100"))
        spread = (Decimal("1.00") + config.spread_margin / Decimal("100"))

        pkr_per_ounce_final = pkr_per_ounce * safeguard * spread
        pkr_per_gram_final = pkr_per_gram * safeguard * spread
        pkr_per_tola_final = pkr_per_tola * safeguard * spread

        return {
            "usd_per_ounce": usd_per_ounce,
            "usd_pkr_rate": usd_pkr_rate,

            "pkr_per_ounce_raw": pkr_per_ounce,
            "pkr_per_gram_raw": pkr_per_gram,
            "pkr_per_tola_raw": pkr_per_tola,

            "pkr_per_ounce_final": pkr_per_ounce_final,
            "pkr_per_gram_final": pkr_per_gram_final,
            "pkr_per_tola_final": pkr_per_tola_final,
        }

    # --------------------------------------------
    # 3. Fetch + Compute + Store Snapshot (cron)
    # --------------------------------------------
    def fetch_and_store_snapshot(self):
        """
        Used exclusively by APScheduler every minute.
        Saves ONE snapshot in the DB.
        """

        usd_per_ounce, usd_pkr_rate = self.fetch_live_prices()
        computed = self.compute_prices(usd_per_ounce, usd_pkr_rate)

        snapshot = GoldPriceSnapshot.objects.create(
            timestamp=timezone.now(),
            usd_per_ounce=computed["usd_per_ounce"],
            usd_pkr_rate=computed["usd_pkr_rate"],
            pkr_per_ounce_raw=computed["pkr_per_ounce_raw"],
            pkr_per_gram_raw=computed["pkr_per_gram_raw"],
            pkr_per_tola_raw=computed["pkr_per_tola_raw"],
            pkr_per_ounce_final=computed["pkr_per_ounce_final"],
            pkr_per_gram_final=computed["pkr_per_gram_final"],
            pkr_per_tola_final=computed["pkr_per_tola_final"],
        )

        return snapshot

    # --------------------------------------------
    # 4. Retrieve Latest Snapshot (API only)
    # --------------------------------------------
    def get_latest_snapshot(self):
        return (
            GoldPriceSnapshot.objects
            .order_by("-timestamp")
            .first()
        )