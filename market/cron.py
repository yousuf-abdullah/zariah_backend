from django.utils import timezone
from .services import GoldPriceService
from .models import DailyClosingPrice, GoldPriceSnapshot


def fetch_gold_snapshot():
    """
    Runs every 60 seconds via APScheduler:
    - Fetch live gold price & USD/PKR rate
    - Compute PKR values (raw + final)
    - Store ONE snapshot
    """
    try:
        service = GoldPriceService()
        snapshot = service.fetch_and_store_snapshot()

        print(f"[APScheduler] Snapshot saved @ {snapshot.timestamp}")

    except Exception as e:
        print(f"[APScheduler] ERROR in fetch_gold_snapshot: {e}")


def generate_daily_closing_price():
    """
    Runs once per day at 23:59:
    - Picks the last snapshot of the day
    - Stores daily closing prices
    """
    today = timezone.localdate()
    last_snapshot = (
        GoldPriceSnapshot.objects
        .filter(timestamp__date=today)
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

    print(f"[APScheduler] Daily closing price saved for {today}.")
