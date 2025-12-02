import os
from django.apps import AppConfig

class ConfigConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "config"

    def ready(self):
        # Prevent scheduler from running twice due to autoreloader
        if os.environ.get("RUN_MAIN") == "true":
            from market.scheduler import start
            start()
