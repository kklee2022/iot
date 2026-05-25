"""Tests for MQTT topic parsing in ingest subscriber."""

from iot.management.commands.run_ingest_subscriber import extract_device_id_from_topic


def test_extract_device_id_plain_topic():
    assert extract_device_id_from_topic("device/gateway_01/telemetry") == "gateway_01"


def test_extract_device_id_prefixed_topic():
    assert extract_device_id_from_topic("kklee/iot/device/gateway_01/telemetry") == "gateway_01"


def test_extract_device_id_invalid_topic_returns_none():
    assert extract_device_id_from_topic("kklee/iot/device/gateway_01/data") is None
