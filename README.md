# IoT Platform (Django)

A Django-based IoT ingestion and monitoring platform with:

- MQTT telemetry ingestion
- Device and sensor dictionary models
- REST APIs for telemetry and history
- Tailwind-based UI dashboard
- Approval-gated login (only approved users can sign in)

## Current Status

Implemented and verified:

- Core models: Device, SensorType, TelemetryData
- MQTT subscriber command with isolated topic support
- MQTT auth webhook endpoint for broker-side authentication
- Dashboard UI and device detail view with chart-ready history API
- Login/logout flow with approval gating via user active flag
- Seed command for local demo/test data
- End-to-end test with HiveMQ public broker and isolated topic prefix

## Tech Stack

- Python 3.13
- Django 4.2
- Django REST Framework
- Celery + Redis
- paho-mqtt
- Tailwind CSS (CDN)

## Main Data Model

- Device
  - device_id (unique)
  - access_token (unique)
  - is_active
  - last_seen
- SensorType
  - code (unique)
  - name, unit
- TelemetryData
  - device (FK)
  - sensor_type (FK)
  - value
  - timestamp

## Authentication and Approval

UI pages require login.

- Login URL: /accounts/login/
- Logout URL: /accounts/logout/
- Approval rule: only users with is_active=True can log in
- Inactive users see: pending administrator approval

To approve a user:

1. Open Django Admin: /admin/
2. Go to Users
3. Set is_active = True
4. Save

## Environment Configuration

All runtime configuration is read from .env.

Important MQTT variables:

- MQTT_BROKER_HOST
- MQTT_BROKER_PORT
- MQTT_USERNAME
- MQTT_PASSWORD
- MQTT_USE_TLS
- MQTT_KEEPALIVE
- MQTT_CLIENT_ID
- MQTT_INGEST_TOPIC

Current default isolated ingestion topic:

- MQTT_INGEST_TOPIC=kklee/iot/device/+/telemetry

Supported topic formats for ingestion:

- device/<device_id>/telemetry
- <prefix>/device/<device_id>/telemetry

This means you can switch MQTT server/provider by editing only .env and restarting services.

## Setup

1. Create and activate virtual environment
2. Install dependencies
3. Configure .env
4. Run migrations
5. Create admin user

Example:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/local.txt
python manage.py migrate
python manage.py createsuperuser
```

## Run (Local)

Web server:

```bash
python manage.py runserver 0.0.0.0:8000
```

MQTT subscriber:

```bash
python manage.py run_ingest_subscriber
```

## Seed Test Data

Seed sample devices/sensors/telemetry:

```bash
python manage.py seed_data --points 96
```

Flush and reseed:

```bash
python manage.py seed_data --flush --points 96
```

## MQTT Payload Contract

Publish to topic:

- device/<device_id>/telemetry
- or prefixed topic such as kklee/iot/device/<device_id>/telemetry

Payload:

```json
{
  "timestamp": 1782372000,
  "metrics": {
    "water_level_m": 2.45,
    "rain_mm": 0.5,
    "temperature": 26.7
  }
}
```

Behavior:

- device_id is extracted from topic
- device must exist and be active
- unknown sensor codes are auto-created in SensorType
- one TelemetryData row is created per metrics key

## Key Endpoints

UI:

- /
- /devices/<device_id>/

Auth:

- /accounts/login/
- /accounts/logout/

API:

- GET /api/health/
- POST /api/iot/auth/
- GET /api/devices/
- GET /api/devices/<device_id>/telemetry/?limit=100
- GET /api/devices/<device_id>/history/?sensor=<sensor_code>&days=7

## Broker Authentication Webhook

Endpoint:

- POST /api/iot/auth/

Expected body:

```json
{
  "clientid": "gateway_site_01",
  "password": "device_access_token"
}
```

Allow condition:

- Device.device_id matches clientid
- Device.access_token matches password
- Device.is_active is True

## Testing

Run all tests:

```bash
.venv/bin/python -m pytest -q
```

## Notes

- Health endpoint is public for liveness probes.
- Most API endpoints require authentication by default.
- The current architecture is ingest-first (MQTT subscriber writes telemetry to DB).
- Legacy polling pipeline is not part of active runtime flow.

## Production Minimum Checklist

Use this as the minimum baseline for a safe production rollout.

1. Infrastructure and services

- PostgreSQL is provisioned and reachable.
- Redis is provisioned and reachable.
- MQTT broker is provisioned and reachable.
- Reverse proxy (Nginx/Caddy/Ingress) is configured for HTTPS.

2. Required environment variables

- DJANGO_SETTINGS_MODULE=config.settings.production
- DJANGO_SECRET_KEY is set to a strong random value.
- DJANGO_ALLOWED_HOSTS includes your real domain(s).
- DATABASE_URL points to production PostgreSQL.
- REDIS_URL and CELERY_BROKER_URL point to production Redis.
- MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_USE_TLS, MQTT_USERNAME, MQTT_PASSWORD are set.
- MQTT_INGEST_TOPIC is set to your isolated topic prefix.

3. Django app deployment

- Install dependencies and run migrations:

```bash
pip install -r requirements/production.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

- Create at least one admin user:

```bash
python manage.py createsuperuser
```

- Start web app with Gunicorn (example):

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

4. Background workers

- Start Celery worker:

```bash
celery -A config worker -l info
```

- Start Celery beat:

```bash
celery -A config beat -l info
```

- Start MQTT subscriber process:

```bash
python manage.py run_ingest_subscriber
```

Use a process manager (systemd, supervisor, Docker/Kubernetes) so all three processes auto-restart.

5. Security hardening

- Enforce HTTPS at the reverse proxy.
- Keep MQTT credentials out of source control.
- Restrict Django admin access by network and/or SSO if possible.
- Only approved users (is_active=True) can access the UI.
- Rotate SECRET_KEY and broker credentials through secrets management policy.

6. Smoke test after deploy

- Open /api/health/ and confirm status ok.
- Log in via /accounts/login/ with an approved account.
- Publish one MQTT test message to your isolated topic.
- Confirm 1+ new TelemetryData rows are written.
- Open dashboard and device detail page to confirm data visibility.

7. Ongoing operations

- Monitor app logs, subscriber logs, and broker connection errors.
- Back up PostgreSQL on a schedule.
- Run `.venv/bin/python -m pytest -q` in CI before release.
