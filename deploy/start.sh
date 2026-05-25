#!/bin/sh
# Application entrypoint — migrate, check, then start gunicorn.
set -e

echo "==> Waiting for database..."
python manage.py wait_for_db

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Running Django system check..."
python manage.py check

echo "==> Starting gunicorn on port ${PORT:-8000}..."
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${GUNICORN_WORKERS:-2}" \
    --timeout "${GUNICORN_TIMEOUT:-60}" \
    --preload \
    --access-logfile - \
    --error-logfile -
