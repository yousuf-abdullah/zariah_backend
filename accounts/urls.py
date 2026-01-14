from django.urls import path
from .views import CsrfView, LoginView, LogoutView, JWTLoginView, JWTLogoutView, RegisterView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("csrf/", CsrfView.as_view(), name="csrf"),
    path("register/", RegisterView.as_view(), name="register"),

    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    path("jwt/login/", JWTLoginView.as_view(), name="jwt_login"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt_refresh"),
    path("jwt/logout/", JWTLogoutView.as_view(), name="jwt_logout"),
]
