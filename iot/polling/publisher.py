"""Thread-safe MQTT publisher with reconnect backoff and offline buffering."""
import collections
import logging
import threading
import time
from typing import Optional

import paho.mqtt.client as mqtt
from django.conf import settings

logger = logging.getLogger(__name__)

_PUBLISHER_LOCK = threading.Lock()
_publisher: Optional["MQTTPublisher"] = None


class MQTTPublisher:
    """
    Publish telemetry to an MQTT broker.

    Offline behaviour
    -----------------
    When the broker is unreachable, outgoing messages are queued in an
    in-memory deque (bounded by MAX_QUEUE_SIZE).  On reconnection, all
    queued messages are replayed in order before new ones are sent.
    """

    MAX_QUEUE_SIZE = 1000
    _BASE_BACKOFF = 1      # seconds
    _MAX_BACKOFF = 60      # seconds

    def __init__(self) -> None:
        self._queue: collections.deque = collections.deque(maxlen=self.MAX_QUEUE_SIZE)
        self._connected = False
        self._lock = threading.Lock()
        self._client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION1,
            client_id=settings.MQTT_CLIENT_ID,
            clean_session=True,
        )
        if settings.MQTT_USERNAME:
            self._client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
        if settings.MQTT_USE_TLS:
            self._client.tls_set()
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect

    # ── MQTT callbacks ────────────────────────────────────────────────────────

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("MQTT connected to %s:%s", settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT)
            with self._lock:
                self._connected = True
            self._replay_queue()
        else:
            logger.error("MQTT connect failed: rc=%s", rc)

    def _on_disconnect(self, client, userdata, rc):
        with self._lock:
            self._connected = False
        if rc != 0:
            logger.warning("MQTT unexpected disconnection: rc=%s", rc)

    # ── Public API ────────────────────────────────────────────────────────────

    def connect(self, retries: int = 5) -> None:
        """Attempt to connect with exponential backoff."""
        backoff = self._BASE_BACKOFF
        for attempt in range(1, retries + 1):
            try:
                self._client.connect(
                    settings.MQTT_BROKER_HOST,
                    settings.MQTT_BROKER_PORT,
                    keepalive=settings.MQTT_KEEPALIVE,
                )
                self._client.loop_start()
                return
            except (OSError, ConnectionRefusedError) as exc:
                logger.warning(
                    "MQTT connect attempt %s/%s failed: %s — retrying in %ss",
                    attempt, retries, exc, backoff,
                )
                time.sleep(backoff)
                backoff = min(backoff * 2, self._MAX_BACKOFF)

        logger.error(
            "MQTT could not connect after %s attempts; messages will be buffered.", retries
        )

    def publish(self, device_id: str, sensor_type: str, payload_json: str) -> None:
        """Publish or buffer a telemetry message."""
        topic = f"{settings.MQTT_TOPIC_PREFIX}/{device_id}/{sensor_type}"
        with self._lock:
            connected = self._connected

        if connected:
            self._client.publish(topic, payload_json, qos=1)
            logger.debug("MQTT published: %s", topic)
        else:
            self._queue.append((topic, payload_json, 1))
            logger.debug(
                "MQTT offline — buffered %s (queue depth: %s)", topic, len(self._queue)
            )

    def queue_depth(self) -> int:
        return len(self._queue)

    def disconnect(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _replay_queue(self) -> None:
        """Drain the offline queue after reconnection."""
        replayed = 0
        while self._queue:
            topic, payload, qos = self._queue.popleft()
            self._client.publish(topic, payload, qos=qos)
            replayed += 1
        if replayed:
            logger.info("MQTT replayed %s buffered messages.", replayed)


def get_publisher() -> MQTTPublisher:
    """Return (or lazily create) the module-level publisher singleton."""
    global _publisher
    if _publisher is None:
        with _PUBLISHER_LOCK:
            if _publisher is None:
                _publisher = MQTTPublisher()
                _publisher.connect()
    return _publisher
