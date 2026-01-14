# config/settings.py

from pathlib import Path
from datetime import timedelta
import os
import environ

# ----------------------------
# Base / Environment
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    # Defaults (safe)
    DJANGO_ENV=(str, "local"),     # local | staging | production
    DEBUG=(bool, False),
)

# Read .env if present
# (Keep .env OUT of git; server should set real env vars too)
env_file = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_file):
    environ.Env.read_env(env_file)

DJANGO_ENV = env("DJANGO_ENV").lower()

# Debug defaults: True locally, False otherwise (unless explicitly set)
if DJANGO_ENV == "local":
    DEBUG = env.bool("DEBUG", default=True)
else:
    DEBUG = env.bool("DEBUG", default=False)

# Security key
SECRET_KEY = env("SECRET_KEY")

# ----------------------------
# Hosts / Origins
# ----------------------------
if DJANGO_ENV == "local":
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
    CSRF_TRUSTED_ORIGINS = []
else:
    # Set these on server as env vars, e.g.:
    # ALLOWED_HOSTS=api.zariah.pk,tea-5cd2471yxr
    # CSRF_TRUSTED_ORIGINS=https://api.zariah.pk,https://admin.zariah.pk
    ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost"])
    CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# ----------------------------
# Apps
# ----------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "django_apscheduler",

    # Third-party
    "rest_framework",

    # Project config (scheduler boot)
    "config.apps.ConfigConfig",

    # Local apps
    "accounts",
    "wallet.apps.WalletConfig",
    "market",

    # JWT blacklist
    "rest_framework_simplejwt.token_blacklist",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ----------------------------
# Database (SQLite local, Postgres server)
# ----------------------------
if DJANGO_ENV == "local":
    # Force SQLite locally (no Postgres required)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    # Server MUST provide DATABASE_URL, e.g.:
    # DATABASE_URL=postgres://USER:PASSWORD@HOST:5432/DBNAME
    DATABASES = {
        "default": env.db("DATABASE_URL")
    }
    # Optional: keep connections open
    DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=600)

# ----------------------------
# Password validation
# ----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ----------------------------
# Internationalization
# ----------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Karachi"
USE_I18N = True
USE_TZ = True

# ----------------------------
# Static / Media
# ----------------------------
STATIC_URL = "static/"

# On server, you generally want a STATIC_ROOT for collectstatic
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ----------------------------
# Auth / DRF / JWT
# ----------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",

    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# ----------------------------
# APScheduler
# ----------------------------
APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"
APSCHEDULER_RUN_NOW_TIMEOUT = 25  # seconds

# ----------------------------
# Production security toggles
# ----------------------------
if DJANGO_ENV != "local":
    # Turn these on when you're behind HTTPS (recommended)
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=True)
    CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=True)

    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)  # set True when HTTPS is confirmed

    # HSTS (enable only after HTTPS works correctly)
    SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=0)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
    SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=False)
