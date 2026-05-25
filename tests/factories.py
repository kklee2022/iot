"""factory_boy factories for IoT models."""
import factory
from django.utils import timezone

from iot.models import Device, SensorType, TelemetryData


class DeviceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Device

    device_id = factory.Sequence(lambda n: f"device-{n:03d}")
    name = factory.LazyAttribute(lambda o: f"Device {o.device_id}")
    is_active = True
    description = ""


class SensorTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SensorType

    code = factory.Sequence(lambda n: f"sensor_{n:03d}")
    name = factory.LazyAttribute(lambda o: o.code.replace("_", " ").title())
    unit = ""


class TelemetryDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TelemetryData

    device = factory.SubFactory(DeviceFactory)
    sensor_type = factory.SubFactory(SensorTypeFactory, code="temperature", name="Temperature", unit="C")
    timestamp = factory.LazyFunction(timezone.now)
    value = 25.0
