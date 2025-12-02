from django.utils import timezone
from .services import GoldPriceService
from .models import GoldPriceSnapshot, DailyClosingPrice


def fetch_gold_snapshot():
    """
    Fetches gold spot + USD/PKR & stores a snapshot.
    Runs every 60 seconds (via APScheduler).
    """
    service = GoldPriceService()
    data = service.get_snapshot()

    GoldPriceSnapshot.objects.create(
        timestamp=timezone.now(),

        usd_per_ounce=data["usd_per_ounce"],
        usd_pkr_rate=data["usd_pkr_rate"],

        pkr_per_ounce_raw=data["pkr_per_ounce_raw"],
        pkr_per_gram_raw=data["pkr_per_gram_raw"],
        pkr_per_tola_raw=data["pkr_per_tola_raw"],

        pkr_per_ounce_final=data["pkr_per_ounce_final"],
        pkr_per_gram_final=data["pkr_per_gram_final"],
        pkr_per_tola_final=data["pkr_per_tola_final"],
    )

    print("[APScheduler] Snapshot saved.")


def generate_daily_closing_price():
    """
    Saves the last snapshot for the day.
    Runs at 23:59 (via APScheduler).
    """
    today = timezone.localdate()
    last_snapshot = (
        GoldPriceSnapshot.objects.filter(timestamp__date=today)
        .order_by("-timestamp")
        .first()
    )

    if not last_snapshot:
        print("[APScheduler] No snapshots for today.")
        return

    DailyClosingPrice.objects.update_or_create(
        date=today,
        defaults={
            "closing_ounce": last_snapshot.pkr_per_ounce_final,
            "closing_gram": last_snapshot.pkr_per_gram_final,
            "closing_tola": last_snapshot.pkr_per_tola_final,
            "source_snapshot": last_snapshot,
        },
    )

    print("[APScheduler] Daily closing price saved.")
