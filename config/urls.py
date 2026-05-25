"""Root URL configuration."""
from django.contrib import admin
from django.urls import include, path

from iot import views as iot_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # Authentication (approval-gated)
    path("accounts/", include("accounts.urls", namespace="accounts")),

    # REST API
    path("api/", include("iot.urls", namespace="iot")),

    # Template (UI) — requires authenticated, approved user
    path("", iot_views.IndexView.as_view(), name="ui-index"),
    path("devices/<str:device_id>/", iot_views.DeviceDetailTemplateView.as_view(), name="ui-device-detail"),
]
