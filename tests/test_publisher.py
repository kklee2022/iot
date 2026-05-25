"""
Phase E — Unit tests: MQTT publisher offline buffering and replay.
"""
from unittest.mock import MagicMock, patch

import pytest

from iot.polling.publisher import MQTTPublisher


@pytest.fixture
def publisher():
    """Return a publisher that has NOT connected to a real broker."""
    with patch("iot.polling.publisher.mqtt.Client"):
        pub = MQTTPublisher()
        pub._connected = False
        yield pub


class TestOfflineBuffering:
    def test_buffers_when_disconnected(self, publisher):
        publisher.publish("dtu-01", "temperature", '{"v":25}')
        assert publisher.queue_depth() == 1

    def test_multiple_messages_buffered(self, publisher):
        for i in range(5):
            publisher.publish("dtu-01", "temperature", f'{{"v":{i}}}')
        assert publisher.queue_depth() == 5

    def test_queue_bounded_by_max_size(self, publisher):
        for i in range(MQTTPublisher.MAX_QUEUE_SIZE + 100):
            publisher.publish("dtu-01", "temperature", f'{{"v":{i}}}')
        assert publisher.queue_depth() == MQTTPublisher.MAX_QUEUE_SIZE


class TestReplayOnReconnect:
    def test_replays_all_queued_messages(self, publisher):
        publisher._queue.append(("iot/telemetry/dtu-01/temperature", '{"v":1}', 1))
        publisher._queue.append(("iot/telemetry/dtu-01/pressure", '{"v":2}', 1))

        mock_client = MagicMock()
        publisher._client = mock_client
        publisher._connected = True
        publisher._replay_queue()

        assert mock_client.publish.call_count == 2
        assert publisher.queue_depth() == 0

    def test_queue_empty_after_replay(self, publisher):
        publisher._queue.append(("topic", "payload", 1))
        mock_client = MagicMock()
        publisher._client = mock_client
        publisher._replay_queue()
        assert publisher.queue_depth() == 0

    def test_no_replay_when_queue_empty(self, publisher):
        mock_client = MagicMock()
        publisher._client = mock_client
        publisher._replay_queue()
        mock_client.publish.assert_not_called()


class TestPublishWhenConnected:
    def test_publishes_directly_when_connected(self, publisher):
        mock_client = MagicMock()
        publisher._client = mock_client
        publisher._connected = True

        publisher.publish("dtu-01", "temperature", '{"v":99}')

        mock_client.publish.assert_called_once()
        assert publisher.queue_depth() == 0

    def test_topic_format(self, publisher):
        mock_client = MagicMock()
        publisher._client = mock_client
        publisher._connected = True

        publisher.publish("dtu-01", "flow_rate", '{}')

        call_args = mock_client.publish.call_args
        topic = call_args[0][0]
        assert "dtu-01" in topic
        assert "flow_rate" in topic
