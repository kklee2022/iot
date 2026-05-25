#!/bin/sh
# Celery worker entrypoint.
set -e

echo "==> Waiting for database..."
python manage.py wait_for_db

echo "==> Starting Celery worker..."
exec celery -A config worker \
    --loglevel="${CELERY_LOG_LEVEL:-info}" \
    --concurrency="${CELERY_WORKER_CONCURRENCY:-2}" \
    --without-gossip \
    --without-mingle
