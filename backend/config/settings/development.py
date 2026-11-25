from .base import *

DEBUG = True

CORS_ALLOW_CREDENTIALS = True

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "testserver",
]

EMAIL_BACKEND = (
    "django.core.mail.backends.console.EmailBackend"
)

DEFAULT_FROM_EMAIL = (
    "noreply@jobmanagement.local"
)

FRONTEND_PASSWORD_RESET_URL = (
    "http://localhost:5173/reset-password"
)

SIMPLE_JWT = {
    # Preserve your other existing JWT settings here.
    "SIGNING_KEY": "dev-only-jwt-signing-key-2026-11-22-secure",
}


DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "job_management_db",
        "USER": "postgres",
        "PASSWORD": "PostgreSQL@266",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]