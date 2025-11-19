from django.contrib import admin
from django.urls import path, include
from .views import health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),

    # Auth API
    path("api/auth/", include("accounts.urls")),

    # DRF browsable login/logout
    path("api-auth/", include("rest_framework.urls")),
]
