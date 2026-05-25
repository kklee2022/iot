#!/bin/sh
# Celery beat entrypoint — only one beat instance should ever run.
set -e

echo "==> Waiting for database..."
python manage.py wait_for_db

echo "==> Starting Celery beat..."
exec celery -A config beat \
    --loglevel="${CELERY_LOG_LEVEL:-info}" \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler
