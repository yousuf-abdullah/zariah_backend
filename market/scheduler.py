from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler import util
from django.utils import timezone
import atexit

from .cron import fetch_gold_snapshot, generate_daily_closing_price


def start():
    scheduler = BackgroundScheduler(timezone="Asia/Karachi")
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Run every 60 seconds
    scheduler.add_job(
        fetch_gold_snapshot,
        trigger="interval",
        seconds=60,
        id="gold_snapshot_job",
        replace_existing=True,
    )

    # Daily closing price at 23:59
    scheduler.add_job(
        generate_daily_closing_price,
        trigger="cron",
        hour=23,
        minute=59,
        id="daily_closing_job",
        replace_existing=True,
    )

    scheduler.start()
    print("🎯 APScheduler started successfully")

    # Shutdown APScheduler when Django stops
    atexit.register(lambda: scheduler.shutdown(wait=False))
