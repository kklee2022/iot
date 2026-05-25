from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views import View
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Device, TelemetryData
from .serializers import DeviceSerializer, TelemetryDataSerializer


# ── API views (JSON) ──────────────────────────────────────────────────────────

class HealthView(APIView):
    """Liveness probe — always returns 200 if the app is up."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response({"status": "ok", "time": timezone.now().isoformat()})


class DeviceListView(APIView):
    """List all registered devices."""

    def get(self, request):
        devices = Device.objects.filter(is_active=True)
        serializer = DeviceSerializer(devices, many=True)
        return Response(serializer.data)


class RecentTelemetryView(APIView):
    """Return the N most recent telemetry records for a device."""

    def get(self, request, device_id):
        try:
            device = Device.objects.get(device_id=device_id, is_active=True)
        except Device.DoesNotExist:
            return Response({"detail": "Device not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            limit = int(request.query_params.get("limit", 100))
        except (TypeError, ValueError):
            return Response({"detail": "Invalid limit parameter."}, status=status.HTTP_400_BAD_REQUEST)
        limit = max(1, min(limit, 1000))
        records = TelemetryData.objects.filter(device=device).select_related("sensor_type").order_by("-timestamp")[:limit]
        serializer = TelemetryDataSerializer(records, many=True)
        return Response(serializer.data)


class MQTTAuthWebhookView(APIView):
    """HTTP authentication endpoint for MQTT broker callbacks."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        client_id = request.data.get("clientid")
        password = request.data.get("password")
        if not client_id or not password:
            return Response({"result": "deny"}, status=status.HTTP_400_BAD_REQUEST)

        device = Device.objects.filter(
            device_id=client_id,
            access_token=password,
            is_active=True,
        ).first()
        if not device:
            return Response({"result": "deny"}, status=status.HTTP_403_FORBIDDEN)

        device.last_seen = timezone.now()
        device.save(update_fields=["last_seen"])
        return Response({"result": "allow", "is_superuser": False})


class DeviceHistoryView(APIView):
    """Return chart-ready telemetry history for one device and one sensor."""

    permission_classes = [IsAuthenticated]

    def get(self, request, device_id):
        sensor = request.query_params.get("sensor")
        if not sensor:
            return Response({"detail": "Missing required query param: sensor"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            days = max(1, min(int(request.query_params.get("days", 7)), 365))
        except ValueError:
            return Response({"detail": "Invalid days parameter."}, status=status.HTTP_400_BAD_REQUEST)

        end_time = timezone.now()
        start_time = end_time - timedelta(days=days)

        points = (
            TelemetryData.objects.filter(
                device__device_id=device_id,
                sensor_type__code=sensor,
                timestamp__gte=start_time,
                timestamp__lte=end_time,
            )
            .order_by("timestamp")
            .values_list("timestamp", "value")
        )

        timestamps = []
        values = []
        for ts, value in points:
            timestamps.append(timezone.localtime(ts).strftime("%m-%d %H:%M"))
            values.append(value)

        return Response(
            {
                "device_id": device_id,
                "sensor": sensor,
                "days": days,
                "timestamps": timestamps,
                "values": values,
            }
        )


# ── Template (UI) views ───────────────────────────────────────────────────────

class IndexView(LoginRequiredMixin, View):
    """Device list dashboard."""

    def get(self, request):
        devices = Device.objects.all().order_by("device_id")
        ctx = {
            "devices": devices,
            "device_count": devices.filter(is_active=True).count(),
            "total_telemetry": TelemetryData.objects.count(),
        }
        return render(request, "iot/index.html", ctx)


class DeviceDetailTemplateView(LoginRequiredMixin, View):
    """Per-device detail page with register map and recent telemetry."""

    def get(self, request, device_id):
        device = get_object_or_404(Device, device_id=device_id)
        records = (
            TelemetryData.objects.filter(device=device)
            .select_related("sensor_type")
            .order_by("-timestamp")[:100]
        )
        sensor_types = (
            device.telemetry.values_list("sensor_type__code", flat=True)
            .distinct()
            .order_by("sensor_type__code")
        )
        ctx = {
            "device": device,
            "records": records,
            "sensor_codes": list(sensor_types),
        }
        return render(request, "iot/device_detail.html", ctx)

