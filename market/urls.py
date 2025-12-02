from django.urls import path
from .views import GoldPriceView

urlpatterns = [
    path("gold-price/", GoldPriceView.as_view(), name="gold-price"),
    
    # Future endpoints (placeholders for now)
    # path("history/1h/", HourHistoryView.as_view()),
    # path("history/1d/", DayHistoryView.as_view()),
    # path("config/", GoldPriceConfigView.as_view()),
]