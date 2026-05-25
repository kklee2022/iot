from django.urls import path

from . import views

app_name = "iot"

urlpatterns = [
    path("health/", views.HealthView.as_view(), name="health"),
    path("iot/auth/", views.MQTTAuthWebhookView.as_view(), name="mqtt-auth"),
    path("devices/", views.DeviceListView.as_view(), name="device-list"),
    path("devices/<str:device_id>/telemetry/", views.RecentTelemetryView.as_view(), name="device-telemetry"),
    path("devices/<str:device_id>/history/", views.DeviceHistoryView.as_view(), name="device-history"),
]
