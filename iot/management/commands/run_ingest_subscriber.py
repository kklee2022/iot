"""Management command: subscribe to MQTT broker and persist telemetry records."""
import json
import logging
import signal
import sys

import paho.mqtt.client as mqtt
from django.conf import settings
from django.core.management.base import BaseCommand

from iot.ingest import ingest_payload

logger = logging.getLogger(__name__)


def extract_device_id_from_topic(topic: str) -> str | None:
    """
    Extract device_id from either:
    - device/<device_id>/telemetry
    - <prefix>/device/<device_id>/telemetry
    """
    parts = topic.split("/")
    for idx, part in enumerate(parts):
        if part == "device" and idx + 2 < len(parts) and parts[idx + 2] == "telemetry":
            return parts[idx + 1]
    return None


class Command(BaseCommand):
    help = "Subscribe to the MQTT broker and ingest telemetry into the database."

    def handle(self, *args, **options):
        topic = settings.MQTT_INGEST_TOPIC
        client_id = f"{settings.MQTT_CLIENT_ID}-ingest"

        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION1,
            client_id=client_id,
        )
        if settings.MQTT_USERNAME:
            client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
        if settings.MQTT_USE_TLS:
            client.tls_set()

        def on_connect(c, userdata, flags, rc):
            if rc == 0:
                c.subscribe(topic, qos=1)
                self.stdout.write(self.style.SUCCESS(f"Subscribed to {topic}"))
            else:
                self.stderr.write(f"MQTT connection refused: rc={rc}")

        def on_disconnect(c, userdata, rc):
            if rc != 0:
                self.stderr.write(f"Unexpected MQTT disconnect: rc={rc}")

        def on_message(c, userdata, msg):
            try:
                payload = json.loads(msg.payload.decode())
                device_id = extract_device_id_from_topic(msg.topic)
                if not device_id:
                    logger.warning("Ingest: unsupported topic format %s", msg.topic)
                    return
                ingest_payload(device_id, payload)
            except json.JSONDecodeError as exc:
                logger.error("Ingest: bad JSON on %s: %s", msg.topic, exc)
            except Exception as exc:
                logger.error("Ingest: unhandled error on %s: %s", msg.topic, exc)

        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_message = on_message

        def _shutdown(signum, frame):
            self.stdout.write("Shutting down ingest subscriber...")
            client.disconnect()
            sys.exit(0)

        signal.signal(signal.SIGTERM, _shutdown)
        signal.signal(signal.SIGINT, _shutdown)

        self.stdout.write(
            f"Connecting to {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT} ..."
        )
        try:
            client.connect(
                settings.MQTT_BROKER_HOST,
                settings.MQTT_BROKER_PORT,
                keepalive=settings.MQTT_KEEPALIVE,
            )
        except (OSError, ConnectionRefusedError) as exc:
            self.stderr.write(f"Could not connect to broker: {exc}")
            sys.exit(1)

        client.loop_forever()
