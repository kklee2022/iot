"""Local development settings."""
from .base import *  # noqa: F401, F403
from .base import INSTALLED_APPS, MIDDLEWARE, env

DEBUG = True
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "0.0.0.0"])

# SQLite for zero-config local dev; override DATABASE_URL to use Postgres.
# DATABASES already defaults to SQLite in base.py.

# Celery — run tasks eagerly in local so no worker needed by default.
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)

INSTALLED_APPS += ["django_extensions"]

MIDDLEWARE += ["django.middleware.common.BrokenLinkEmailsMiddleware"]

# Allow all hosts for local convenience.
INTERNAL_IPS = ["127.0.0.1"]
