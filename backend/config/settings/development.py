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