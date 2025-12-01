from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import GoldPriceService


class GoldPriceView(APIView):
    """
    GET /api/market/gold-price/
    Returns computed PKR gold prices
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        service = GoldPriceService()
        snapshot = service.get_snapshot()
        return Response(snapshot.as_dict)
