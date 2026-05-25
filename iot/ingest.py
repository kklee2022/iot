"""Ingest MQTT telemetry payloads into the canonical models."""
import logging
from datetime import datetime, timezone as dt_timezone

from django.utils import timezone

from .models import Device, SensorType, TelemetryData
from .serializers import TelemetryIngestSerializer

logger = logging.getLogger(__name__)


def _parse_timestamp(value):
    if value is None:
        return timezone.now()
    if isinstance(value, (int, float)):
        if value > 5_000_000_000:
            value = value / 1000
        return timezone.make_aware(datetime.fromtimestamp(value), dt_timezone.utc)
    if isinstance(value, str):
        if value.isdigit():
            return _parse_timestamp(int(value))
    return value


def ingest_payload(device_id: str, payload: dict) -> int:
    """
    Validate *payload* and persist all metrics for one device.

    Returns the number of created rows, or 0 on any validation/device error.
    """
    payload = dict(payload or {})
    payload["timestamp"] = _parse_timestamp(payload.get("timestamp"))
    serializer = TelemetryIngestSerializer(data=payload)
    if not serializer.is_valid():
        logger.warning("Ingest validation failed for %s: %s", device_id, serializer.errors)
        return 0

    data = serializer.validated_data

    try:
        device = Device.objects.get(device_id=device_id, is_active=True)
    except Device.DoesNotExist:
        logger.warning("Ingest: unknown or inactive device %r", device_id)
        return 0

    timestamp = data.get("timestamp") or timezone.now()
    metrics = data["metrics"]
    telemetry_rows = []

    for sensor_code, value in metrics.items():
        sensor, _ = SensorType.objects.get_or_create(
            code=sensor_code,
            defaults={"name": sensor_code.replace("_", " ").title(), "unit": ""},
        )
        telemetry_rows.append(
            TelemetryData(
                device=device,
                sensor_type=sensor,
                value=float(value),
                timestamp=timestamp,
            )
        )

    created = 0
    if telemetry_rows:
        TelemetryData.objects.bulk_create(telemetry_rows)
        created = len(telemetry_rows)

    if created:
        Device.objects.filter(pk=device.pk).update(last_seen=timezone.now())
        logger.info("Ingested %s metrics from %s", created, device_id)
    return created
