from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated


# -------------------------------------------------
# CSRF SEED ENDPOINT
# -------------------------------------------------
@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(APIView):
    """
    Sets the CSRF cookie.
    Required for session-based auth when using API clients (Postman, mobile, SPA).
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"detail": "CSRF cookie set"})


# -------------------------------------------------
# LOGIN (SESSION-BASED, CSRF-PROTECTED)
# -------------------------------------------------
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required"},
                status=400
            )

        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response(
                {"error": "Invalid credentials"},
                status=401
            )

        login(request, user)

        return Response({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
        })


# -------------------------------------------------
# LOGOUT
# -------------------------------------------------
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful"})
