"""Build the unified MQTT/JSON telemetry payload from a raw Modbus reading."""
from datetime import datetime, timezone
from typing import Optional

from ..models import Device, RegisterMap


def build_payload(
    device: Device,
    register_map: RegisterMap,
    raw_value: float,
    quality: str,
    timestamp: Optional[datetime] = None,
) -> dict:
    """
    Return the canonical MQTT/JSON payload dict for one sensor reading.

    Schema
    ------
    device_id        str   — unique device identifier
    sensor_type      str   — e.g. "temperature", "pressure"
    timestamp        str   — ISO-8601 UTC
    raw_value        float — value read directly from the register
    normalized_value float — raw_value * scale + offset
    unit             str   — engineering unit, e.g. "°C"
    quality          str   — "good" | "uncertain" | "bad"
    payload          dict  — register metadata for traceability
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    ts = timestamp.isoformat() if hasattr(timestamp, "isoformat") else str(timestamp)
    normalized = raw_value * register_map.scale + register_map.offset

    return {
        "device_id": device.device_id,
        "sensor_type": register_map.sensor_type,
        "timestamp": ts,
        "raw_value": raw_value,
        "normalized_value": normalized,
        "unit": register_map.unit,
        "quality": quality,
        "payload": {
            "register_address": register_map.register_address,
            "register_type": register_map.register_type,
            "data_type": register_map.data_type,
            "scale": register_map.scale,
            "offset": register_map.offset,
        },
    }
