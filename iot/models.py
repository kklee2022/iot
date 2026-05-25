import uuid

from django.db import models


def generate_access_token() -> str:
    return uuid.uuid4().hex


class Device(models.Model):
    """Represents a field gateway/edge node that publishes telemetry."""

    device_id = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128)
    access_token = models.CharField(max_length=64, unique=True, default=generate_access_token)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["device_id"]

    def __str__(self):
        return f"{self.name} ({self.device_id})"


class SensorType(models.Model):
    """Canonical sensor dictionary entry, keyed by code in MQTT metrics."""

    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128)
    unit = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.code


class TelemetryData(models.Model):
    """Single telemetry point from MQTT metrics payload."""

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="telemetry")
    sensor_type = models.ForeignKey(SensorType, on_delete=models.CASCADE, related_name="telemetry")
    value = models.FloatField()
    timestamp = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["device", "timestamp"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"{self.device.device_id}/{self.sensor_type.code} @ {self.timestamp}"
