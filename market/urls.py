from django.urls import path
from .views import GoldPriceView

urlpatterns = [
    path("gold-price/", GoldPriceView.as_view()),
]
