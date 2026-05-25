"""
Phase E — Integration-style view tests (health, API, template UI).
"""
import json

import pytest
from django.urls import reverse

from tests.factories import DeviceFactory, SensorTypeFactory, TelemetryDataFactory


# ── Health endpoint ───────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestHealthView:
    def test_returns_200(self, client):
        url = reverse("iot:health")
        response = client.get(url)
        assert response.status_code == 200

    def test_response_body(self, client):
        url = reverse("iot:health")
        data = client.get(url).json()
        assert data["status"] == "ok"
        assert "time" in data

    def test_no_auth_required(self, client):
        """Health endpoint must be accessible without credentials."""
        url = reverse("iot:health")
        assert client.get(url).status_code == 200


# ── Device list API ───────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestDeviceListAPI:
    def test_requires_authentication(self, client):
        url = reverse("iot:device-list")
        response = client.get(url)
        assert response.status_code in (401, 403)

    def test_returns_device_for_authenticated_user(self, client, django_user_model):
        user = django_user_model.objects.create_user(username="tester", password="pass")
        client.force_login(user)
        DeviceFactory()
        url = reverse("iot:device-list")
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_disabled_device_excluded(self, client, django_user_model):
        user = django_user_model.objects.create_user(username="tester2", password="pass")
        client.force_login(user)
        DeviceFactory(is_active=False)
        url = reverse("iot:device-list")
        data = client.get(url).json()
        assert all(d["is_active"] for d in data)


# ── Recent telemetry API ──────────────────────────────────────────────────────

@pytest.mark.django_db
class TestRecentTelemetryAPI:
    def test_404_for_unknown_device(self, client, django_user_model):
        user = django_user_model.objects.create_user(username="t3", password="pass")
        client.force_login(user)
        url = reverse("iot:device-telemetry", kwargs={"device_id": "no-such-device"})
        assert client.get(url).status_code == 404

    def test_returns_records_for_known_device(self, client, django_user_model):
        user = django_user_model.objects.create_user(username="t4", password="pass")
        client.force_login(user)
        device = DeviceFactory()
        sensor = SensorTypeFactory(code="temperature", name="Temperature", unit="C")
        TelemetryDataFactory(device=device, sensor_type=sensor, value=25.0)
        url = reverse("iot:device-telemetry", kwargs={"device_id": device.device_id})
        data = client.get(url).json()
        assert len(data) == 1
        assert data[0]["sensor_code"] == "temperature"


@pytest.mark.django_db
class TestMQTTAuthWebhook:
    def test_allow_for_valid_credentials(self, client):
        device = DeviceFactory(access_token="token-abc")
        url = reverse("iot:mqtt-auth")
        response = client.post(
            url,
            data=json.dumps({"clientid": device.device_id, "password": "token-abc"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["result"] == "allow"

    def test_deny_for_invalid_credentials(self, client):
        DeviceFactory(access_token="token-abc")
        url = reverse("iot:mqtt-auth")
        response = client.post(
            url,
            data=json.dumps({"clientid": "device-000", "password": "bad-token"}),
            content_type="application/json",
        )
        assert response.status_code in (400, 403)


@pytest.mark.django_db
class TestHistoryAPI:
    def test_history_requires_sensor_param(self, client, django_user_model):
        user = django_user_model.objects.create_user(username="hist1", password="pass")
        client.force_login(user)
        device = DeviceFactory()
        url = reverse("iot:device-history", kwargs={"device_id": device.device_id})
        response = client.get(url)
        assert response.status_code == 400

    def test_history_returns_points(self, client, django_user_model):
        user = django_user_model.objects.create_user(username="hist2", password="pass")
        client.force_login(user)
        device = DeviceFactory()
        sensor = SensorTypeFactory(code="temperature", name="Temperature", unit="C")
        TelemetryDataFactory(device=device, sensor_type=sensor, value=22.3)

        url = reverse("iot:device-history", kwargs={"device_id": device.device_id})
        response = client.get(url, {"sensor": "temperature", "days": 7})
        assert response.status_code == 200
        data = response.json()
        assert data["sensor"] == "temperature"
        assert len(data["values"]) == 1


# ── Template UI views ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestIndexUI:
    def test_anonymous_redirects_to_login(self, client):
        response = client.get(reverse("ui-index"))
        assert response.status_code == 302
        assert "/accounts/login/" in response["Location"]

    def test_index_returns_200_for_authenticated_user(self, client, django_user_model):
        user = django_user_model.objects.create_user(username="ui1", password="pass")
        client.force_login(user)
        response = client.get(reverse("ui-index"))
        assert response.status_code == 200

    def test_index_shows_device(self, client, django_user_model):
        user = django_user_model.objects.create_user(username="ui2", password="pass")
        client.force_login(user)
        DeviceFactory(name="My Sensor")
        response = client.get(reverse("ui-index"))
        assert b"My Sensor" in response.content


@pytest.mark.django_db
class TestDeviceDetailUI:
    def test_returns_200_for_existing_device(self, client, django_user_model):
        user = django_user_model.objects.create_user(username="ui3", password="pass")
        client.force_login(user)
        device = DeviceFactory()
        url = reverse("ui-device-detail", kwargs={"device_id": device.device_id})
        assert client.get(url).status_code == 200

    def test_returns_404_for_missing_device(self, client, django_user_model):
        user = django_user_model.objects.create_user(username="ui4", password="pass")
        client.force_login(user)
        url = reverse("ui-device-detail", kwargs={"device_id": "ghost-device"})
        assert client.get(url).status_code == 404

    def test_shows_telemetry_record(self, client, django_user_model):
        user = django_user_model.objects.create_user(username="ui5", password="pass")
        client.force_login(user)
        device = DeviceFactory()
        sensor = SensorTypeFactory(code="pressure", name="Pressure")
        TelemetryDataFactory(device=device, sensor_type=sensor, value=123.4)
        url = reverse("ui-device-detail", kwargs={"device_id": device.device_id})
        assert b"pressure" in client.get(url).content
