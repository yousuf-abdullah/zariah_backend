from django.apps import AppConfig
import sys


class ConfigConfig(AppConfig):
    name = "config"

    def ready(self):
        # Avoid starting scheduler for migrations, shell, commands
        if "runserver" in sys.argv:
            try:
                from market.scheduler import start as start_scheduler
                start_scheduler()
                print("APScheduler started successfully.")
            except Exception as e:
                print("APScheduler failed to start:", e)
