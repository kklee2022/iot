"""
Phase E — Unit tests: telemetry ingest boundary (validation + persistence).
"""
import pytest

from iot.ingest import ingest_payload
from iot.models import SensorType, TelemetryData
from tests.factories import DeviceFactory


def _good_payload() -> dict:
    return {
        "timestamp": 1_782_372_000,
        "metrics": {
            "temperature": 25.0,
            "humidity": 60.5,
        },
    }


@pytest.mark.django_db
class TestIngestPayload:
    def test_valid_payload_creates_rows(self):
        device = DeviceFactory()
        created = ingest_payload(device.device_id, _good_payload())
        assert created == 2
        assert TelemetryData.objects.filter(device=device).count() == 2

    def test_rows_linked_to_device(self):
        device = DeviceFactory()
        ingest_payload(device.device_id, _good_payload())
        assert TelemetryData.objects.filter(device=device).exists()

    def test_unknown_device_returns_zero(self):
        created = ingest_payload("nonexistent-device-xyz", _good_payload())
        assert created == 0

    def test_inactive_device_returns_zero(self):
        device = DeviceFactory(is_active=False)
        created = ingest_payload(device.device_id, _good_payload())
        assert created == 0

    def test_empty_metrics_returns_zero(self):
        device = DeviceFactory()
        created = ingest_payload(device.device_id, {"metrics": {}})
        assert created == 0

    def test_sensor_types_auto_created(self):
        device = DeviceFactory()
        ingest_payload(device.device_id, _good_payload())
        assert SensorType.objects.filter(code="temperature").exists()
        assert SensorType.objects.filter(code="humidity").exists()

    def test_record_count_increments(self):
        device = DeviceFactory()
        before = TelemetryData.objects.count()
        ingest_payload(device.device_id, _good_payload())
        assert TelemetryData.objects.count() == before + 2
