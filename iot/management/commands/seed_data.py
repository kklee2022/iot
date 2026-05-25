"""Seed representative Device/SensorType/TelemetryData records for local demos."""

import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from iot.models import Device, SensorType, TelemetryData

DEVICE_SPECS = [
    {"device_id": "gateway_site_01", "name": "River Site 01", "description": "North embankment"},
    {"device_id": "gateway_site_02", "name": "River Site 02", "description": "South spillway"},
    {"device_id": "edge_camera_01", "name": "Camera Edge 01", "description": "Bridge camera node"},
]

SENSOR_SPECS = [
    {"code": "water_level_m", "name": "Water Level", "unit": "m"},
    {"code": "rain_mm", "name": "Rain Gauge", "unit": "mm"},
    {"code": "soil_moisture", "name": "Soil Moisture", "unit": "%"},
    {"code": "temperature", "name": "Temperature", "unit": "C"},
]


class Command(BaseCommand):
    help = "Seed Device/SensorType/TelemetryData sample records"

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true", help="Delete existing iot data before seeding")
        parser.add_argument("--points", type=int, default=96, help="Telemetry points per sensor/device")

    def handle(self, *args, **options):
        if options["flush"]:
            TelemetryData.objects.all().delete()
            SensorType.objects.all().delete()
            Device.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing data flushed."))

        sensors = {}
        for spec in SENSOR_SPECS:
            sensor, _ = SensorType.objects.get_or_create(code=spec["code"], defaults=spec)
            sensors[sensor.code] = sensor

        now = timezone.now()
        created_devices = 0
        created_points = 0

        for spec in DEVICE_SPECS:
            device, created = Device.objects.get_or_create(
                device_id=spec["device_id"],
                defaults={
                    "name": spec["name"],
                    "description": spec["description"],
                    "is_active": True,
                },
            )
            if created:
                created_devices += 1

            rows = []
            for i in range(options["points"]):
                ts = now - timedelta(minutes=5 * (options["points"] - i))
                rows.extend(
                    [
                        TelemetryData(device=device, sensor_type=sensors["water_level_m"], value=round(1.8 + random.random() * 0.6, 3), timestamp=ts),
                        TelemetryData(device=device, sensor_type=sensors["rain_mm"], value=round(random.random() * 2.0, 3), timestamp=ts),
                        TelemetryData(device=device, sensor_type=sensors["soil_moisture"], value=round(20 + random.random() * 25, 2), timestamp=ts),
                        TelemetryData(device=device, sensor_type=sensors["temperature"], value=round(18 + random.random() * 10, 2), timestamp=ts),
                    ]
                )

            TelemetryData.objects.bulk_create(rows)
            created_points += len(rows)
            Device.objects.filter(pk=device.pk).update(last_seen=now)

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created {created_devices} devices, {len(sensors)} sensor types, {created_points} telemetry points."
            )
        )
