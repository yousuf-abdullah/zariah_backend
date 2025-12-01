from django.urls import path

from .views import GoldPriceView

app_name = "market"

urlpatterns = [
    path("gold-price/", GoldPriceView.as_view(), name="gold-price"),
]
