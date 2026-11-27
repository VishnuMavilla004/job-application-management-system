
import os

from .base import *


DEBUG = False

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")

if not SECRET_KEY or SECRET_KEY == "development-only-insecure-key":
    raise RuntimeError(
        "A strong DJANGO_SECRET_KEY must be configured."
    )

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "DJANGO_ALLOWED_HOSTS", ""
    ).split(",")
    if host.strip()
]

if not ALLOWED_HOSTS:
    raise RuntimeError(
        "DJANGO_ALLOWED_HOSTS must be configured."
    )

# Production database configuration.
required_database_variables = [
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "DB_HOST",
]

missing_database_variables = [
    variable
    for variable in required_database_variables
    if not os.environ.get(variable)
]

if missing_database_variables:
    raise RuntimeError(
        "Missing database environment variables: "
        + ", ".join(missing_database_variables)
    )

DATABASES["default"].update({
    "NAME": os.environ["DB_NAME"],
    "USER": os.environ["DB_USER"],
    "PASSWORD": os.environ["DB_PASSWORD"],
    "HOST": os.environ["DB_HOST"],
    "PORT": os.getenv("DB_PORT", "5432"),
    "CONN_MAX_AGE": int(
        os.getenv("DB_CONN_MAX_AGE", "60")
    ),
    "OPTIONS": {
        "sslmode": os.getenv("DB_SSLMODE", "require"),
    },
})

# Frontend origins must be explicit.
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS", ""
    ).split(",")
    if origin.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CSRF_TRUSTED_ORIGINS", ""
    ).split(",")
    if origin.strip()
]

CORS_ALLOW_CREDENTIALS = True

if not CORS_ALLOWED_ORIGINS:
    raise RuntimeError(
        "CORS_ALLOWED_ORIGINS must be configured."
    )

if not CSRF_TRUSTED_ORIGINS:
    raise RuntimeError(
        "CSRF_TRUSTED_ORIGINS must be configured."
    )

# HTTPS and reverse-proxy configuration.
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

SECURE_SSL_REDIRECT = (
    os.getenv("SECURE_SSL_REDIRECT", "true").lower()
    == "true"
)

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"

# Enable HSTS after confirming HTTPS works on the deployed domain.
SECURE_HSTS_SECONDS = int(
    os.getenv("SECURE_HSTS_SECONDS", "0")
)

SECURE_HSTS_INCLUDE_SUBDOMAINS = (
    SECURE_HSTS_SECONDS > 0
)

SECURE_HSTS_PRELOAD = (
    SECURE_HSTS_SECONDS > 0
)

# Email configuration.
EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
)

EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")

EMAIL_USE_TLS = (
    os.getenv("EMAIL_USE_TLS", "true").lower() == "true"
)

EMAIL_USE_SSL = (
    os.getenv("EMAIL_USE_SSL", "false").lower() == "true"
)

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    "noreply@example.com",
)

FRONTEND_PASSWORD_RESET_URL = os.getenv(
    "FRONTEND_PASSWORD_RESET_URL",
    "",
)

if not FRONTEND_PASSWORD_RESET_URL:
    raise RuntimeError(
        "FRONTEND_PASSWORD_RESET_URL must be configured."
    )


# --------------------------------------------------
# Persistent resume storage — Supabase S3
# --------------------------------------------------

required_storage_variables = [
    "SUPABASE_STORAGE_BUCKET",
    "SUPABASE_S3_ENDPOINT_URL",
    "SUPABASE_S3_REGION",
    "SUPABASE_S3_ACCESS_KEY_ID",
    "SUPABASE_S3_SECRET_ACCESS_KEY",
]

missing_storage_variables = [
    variable
    for variable in required_storage_variables
    if not os.environ.get(variable)
]

if missing_storage_variables:
    raise RuntimeError(
        "Missing Supabase storage environment variables: "
        + ", ".join(missing_storage_variables)
    )

STORAGES = {
    **STORAGES,
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": os.environ["SUPABASE_STORAGE_BUCKET"],
            "endpoint_url": os.environ["SUPABASE_S3_ENDPOINT_URL"],
            "region_name": os.environ["SUPABASE_S3_REGION"],
            "access_key": os.environ["SUPABASE_S3_ACCESS_KEY_ID"],
            "secret_key": os.environ["SUPABASE_S3_SECRET_ACCESS_KEY"],
            "addressing_style": "path",
            "signature_version": "s3v4",
            "default_acl": None,
            "querystring_auth": True,
            "querystring_expire": 300,
            "file_overwrite": False,
            "use_ssl": True,
        },
    },
}


# Production logging goes to the console.
LOGGING["root"]["handlers"] = ["console"]

# Production should not expose Django debug information.
DEBUG = False

