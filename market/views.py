from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from .services import GoldPriceService
from .models import GoldPriceConfig


class GoldPriceView(APIView):
    """
    Returns the latest saved gold price snapshot (not live).
    """

    def get(self, request):
        service = GoldPriceService()
        snapshot = service.get_latest_snapshot()

        if not snapshot:
            return Response(
                {"detail": "No price data available yet. Please try again shortly."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # Get config margins
        config = GoldPriceConfig.get_solo()

        # Compute staleness
        age_seconds = (timezone.now() - snapshot.timestamp).total_seconds()
        stale = age_seconds > 180  # more than 3 minutes old

        data = {
            "timestamp": snapshot.timestamp,
            "is_stale": stale,

            "usd_per_ounce": snapshot.usd_per_ounce,
            "usd_pkr_rate": snapshot.usd_pkr_rate,

            "pkr_per_ounce_raw": snapshot.pkr_per_ounce_raw,
            "pkr_per_gram_raw": snapshot.pkr_per_gram_raw,
            "pkr_per_tola_raw": snapshot.pkr_per_tola_raw,

            "pkr_per_ounce_final": snapshot.pkr_per_ounce_final,
            "pkr_per_gram_final": snapshot.pkr_per_gram_final,
            "pkr_per_tola_final": snapshot.pkr_per_tola_final,

            "margins": {
                "safeguard_margin": config.safeguard_margin,
                "spread_margin": config.spread_margin,
            }
        }

        return Response(data, status=status.HTTP_200_OK)
