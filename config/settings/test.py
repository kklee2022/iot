"""Test settings — fast, deterministic, no external services."""
from .base import *  # noqa: F401, F403
from .base import env

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Use in-memory cache during tests.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Run Celery tasks synchronously so no broker is required.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Silence password hashing cost for speed.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Dummy secret key for tests.
SECRET_KEY = env("DJANGO_SECRET_KEY", default="test-secret-key-not-for-production")
