from django.contrib import admin

from .models import Device, SensorType, TelemetryData


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ["device_id", "name", "is_active", "last_seen", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["device_id", "name"]
    readonly_fields = ["created_at", "updated_at", "last_seen"]


@admin.register(SensorType)
class SensorTypeAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "unit", "created_at"]
    search_fields = ["code", "name", "unit"]
    readonly_fields = ["created_at"]


@admin.register(TelemetryData)
class TelemetryDataAdmin(admin.ModelAdmin):
    list_display = ["device", "sensor_type", "value", "timestamp", "created_at"]
    list_filter = ["sensor_type__code"]
    search_fields = ["device__device_id", "sensor_type__code", "sensor_type__name"]
    readonly_fields = ["created_at"]
