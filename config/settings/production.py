"""Production settings — all secrets must be provided via environment."""
from .base import *  # noqa: F401, F403
from .base import env

DEBUG = False

# TLS / security hardening
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Postgres required in production.
# DATABASE_URL must be set in the environment.

# MQTT TLS on in production by default.
MQTT_USE_TLS = env.bool("MQTT_USE_TLS", default=True)

LOGGING_FORMAT = "json"
