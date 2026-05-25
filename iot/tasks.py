"""Celery tasks kept for compatibility while ingest-first architecture is active."""
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def poll_device(device_id: str) -> None:
    """Deprecated task placeholder kept to avoid scheduler import failures."""
    logger.info("poll_device is deprecated in ingest-first mode; device_id=%s", device_id)


@shared_task(ignore_result=True)
def poll_all_devices() -> None:
    """Deprecated scheduler placeholder kept for compatibility with existing beat config."""
    logger.info("poll_all_devices is deprecated in ingest-first mode")
