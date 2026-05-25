"""Shared fixtures for the test suite."""
import pytest

from tests.factories import DeviceFactory, SensorTypeFactory, TelemetryDataFactory


@pytest.fixture
def device(db):
    return DeviceFactory()


@pytest.fixture
def sensor_type(db):
    return SensorTypeFactory()


@pytest.fixture
def telemetry_record(db, device, sensor_type):
    return TelemetryDataFactory(device=device, sensor_type=sensor_type)
