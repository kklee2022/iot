from rest_framework import serializers

from .models import Device, SensorType, TelemetryData


class SensorTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorType
        fields = "__all__"


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = [
            "id",
            "device_id",
            "name",
            "is_active",
            "description",
            "last_seen",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["last_seen", "created_at", "updated_at"]


class TelemetryDataSerializer(serializers.ModelSerializer):
    device_id = serializers.CharField(source="device.device_id", read_only=True)
    sensor_code = serializers.CharField(source="sensor_type.code", read_only=True)
    sensor_name = serializers.CharField(source="sensor_type.name", read_only=True)
    unit = serializers.CharField(source="sensor_type.unit", read_only=True)

    class Meta:
        model = TelemetryData
        fields = [
            "id",
            "device_id",
            "sensor_code",
            "sensor_name",
            "unit",
            "value",
            "timestamp",
            "created_at",
        ]
        read_only_fields = fields


class TelemetryIngestSerializer(serializers.Serializer):
    """Validates a topic-derived ingest payload with metrics dictionary."""

    timestamp = serializers.DateTimeField(required=False)
    metrics = serializers.DictField(child=serializers.FloatField(), allow_empty=False)

    def validate(self, attrs):
        if not attrs.get("metrics"):
            raise serializers.ValidationError({"metrics": "Metrics must not be empty."})
        return attrs
