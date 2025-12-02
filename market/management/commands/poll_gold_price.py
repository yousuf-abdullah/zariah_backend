import time
from django.core.management.base import BaseCommand
from market.services import GoldPriceService

class Command(BaseCommand):
    help = "Polls gold price via Selenium scraping periodically and stores snapshots."

    def add_arguments(self, parser):
        parser.add_argument(
            "--interval",
            type=int,
            default=60,  # Changed default to 60 seconds
            help="Seconds between polls (default 60).",
        )

    def handle(self, *args, **options):
        interval = options["interval"]
        service = GoldPriceService()
        
        self.stdout.write(self.style.SUCCESS(f"Starting Gold Scraper Poller. Interval: {interval}s"))
        
        try:
            while True:
                start_time = time.time()
                
                try:
                    self.stdout.write("Fetching new snapshot...")
                    snapshot = service.get_snapshot()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"[{snapshot.created_at.strftime('%H:%M:%S')}] "
                            f"USD/OZ: ${snapshot.spot_ounce_usd} | "
                            f"PKR/Gram: {snapshot.spot_gram_pkr}"
                        )
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error during polling cycle: {e}"))
                
                # Calculate sleep time to maintain accurate 60s intervals
                # (Scraping takes time, so we subtract that execution time)
                elapsed = time.time() - start_time
                sleep_time = max(0, interval - elapsed)
                
                if sleep_time == 0:
                    self.stdout.write(self.style.WARNING("Scraping took longer than interval!"))

                time.sleep(sleep_time)

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Polling stopped by user."))