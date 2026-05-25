from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Device",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("device_id", models.CharField(max_length=64, unique=True)),
                ("name", models.CharField(max_length=128)),
                (
                    "protocol",
                    models.CharField(
                        choices=[("modbus_tcp", "Modbus TCP"), ("modbus_rtu", "Modbus RTU")],
                        default="modbus_tcp",
                        max_length=20,
                    ),
                ),
                ("host", models.CharField(help_text="IP address or hostname for TCP; serial port for RTU", max_length=255)),
                ("port", models.PositiveIntegerField(default=502)),
                ("slave_id", models.PositiveSmallIntegerField(default=1)),
                ("poll_interval", models.PositiveIntegerField(default=10, help_text="Polling interval in seconds")),
                ("enabled", models.BooleanField(default=True)),
                ("last_seen", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["device_id"]},
        ),
        migrations.CreateModel(
            name="RegisterMap",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "device",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="register_maps",
                        to="iot.device",
                    ),
                ),
                ("sensor_type", models.CharField(help_text="e.g. temperature, pressure, flow_rate", max_length=64)),
                ("register_address", models.PositiveIntegerField()),
                (
                    "register_type",
                    models.CharField(
                        choices=[
                            ("holding", "Holding Register (FC3)"),
                            ("input", "Input Register (FC4)"),
                            ("coil", "Coil (FC1)"),
                            ("discrete", "Discrete Input (FC2)"),
                        ],
                        default="holding",
                        max_length=20,
                    ),
                ),
                (
                    "data_type",
                    models.CharField(
                        choices=[
                            ("int16", "INT16"),
                            ("uint16", "UINT16"),
                            ("int32", "INT32"),
                            ("uint32", "UINT32"),
                            ("float32", "FLOAT32"),
                            ("bool", "Boolean"),
                        ],
                        default="uint16",
                        max_length=10,
                    ),
                ),
                ("scale", models.FloatField(default=1.0, help_text="Multiply raw value by this factor")),
                ("offset", models.FloatField(default=0.0, help_text="Add this after scaling")),
                ("unit", models.CharField(blank=True, max_length=32)),
                ("enabled", models.BooleanField(default=True)),
            ],
            options={"ordering": ["device", "register_address"]},
        ),
        migrations.CreateModel(
            name="TelemetryRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "device",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="telemetry",
                        to="iot.device",
                    ),
                ),
                ("sensor_type", models.CharField(max_length=64)),
                ("timestamp", models.DateTimeField(db_index=True)),
                ("raw_value", models.FloatField()),
                ("normalized_value", models.FloatField()),
                ("unit", models.CharField(blank=True, max_length=32)),
                (
                    "quality",
                    models.CharField(
                        choices=[("good", "Good"), ("uncertain", "Uncertain"), ("bad", "Bad")],
                        default="good",
                        max_length=12,
                    ),
                ),
                ("payload", models.JSONField(help_text="Full original MQTT JSON payload")),
                ("received_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-timestamp"]},
        ),
        migrations.AddIndex(
            model_name="telemetryrecord",
            index=models.Index(fields=["device", "sensor_type", "-timestamp"], name="iot_telemet_device_i_sensor_t_idx"),
        ),
        migrations.AlterUniqueTogether(
            name="registermap",
            unique_together={("device", "register_address", "register_type")},
        ),
    ]
