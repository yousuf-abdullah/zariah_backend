from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import GoldPriceService

class GoldPriceView(APIView):
    def get(self, request):
        service = GoldPriceService()

        try:
            snapshot = service.get_snapshot()

            data = {
                "timestamp": snapshot.timestamp,
                "usd_per_ounce": snapshot.usd_per_ounce,
                "usd_pkr_rate": snapshot.usd_pkr_rate,
                "sell_price": {
                    "ounce": snapshot.pkr_per_ounce_final,
                    "gram": snapshot.pkr_per_gram_final,
                    "tola": snapshot.pkr_per_tola_final,
                },
                "raw_price": {
                    "ounce": snapshot.pkr_per_ounce_raw,
                    "gram": snapshot.pkr_per_gram_raw,
                    "tola": snapshot.pkr_per_tola_raw,
                }
            }

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
