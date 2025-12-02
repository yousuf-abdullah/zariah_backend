from django.http import HttpResponse
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # API modules
    path("api/accounts/", include("accounts.urls")),
    path("api/wallet/", include("wallet.urls")),
    path("api/market/", include("market.urls")),

    # Health check endpoint
    path("api/ping/", lambda r: HttpResponse("pong")),
]