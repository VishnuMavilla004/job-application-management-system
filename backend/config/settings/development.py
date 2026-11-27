
import os

from .base import *


DEBUG = True

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "development-only-insecure-key",
)

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "testserver",
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

EMAIL_BACKEND = (
    "django.core.mail.backends.console.EmailBackend"
)

DEFAULT_FROM_EMAIL = "noreply@jobmanagement.local"

FRONTEND_PASSWORD_RESET_URL = (
    "http://localhost:5173/reset-password"
)

# Preserve the existing JWT lifetimes and rotation settings.
SIMPLE_JWT = {
    **SIMPLE_JWT,
    "SIGNING_KEY": os.getenv(
        "JWT_SIGNING_KEY",
        SECRET_KEY,
    ),
}

# Development database values come from .env.
DATABASES["default"].update({
    "NAME": os.getenv("DB_NAME", "job_management_db"),
    "USER": os.getenv("DB_USER", "postgres"),
    "PASSWORD": os.getenv("DB_PASSWORD", ""),
    "HOST": os.getenv("DB_HOST", "localhost"),
    "PORT": os.getenv("DB_PORT", "5432"),
})

# Local file logging, in addition to console logging.
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING["handlers"]["file"] = {
    "class": "logging.FileHandler",
    "filename": LOG_DIR / "application.log",
    "formatter": "standard",
    "encoding": "utf-8",
}

LOGGING["root"]["handlers"] = ["console", "file"]
