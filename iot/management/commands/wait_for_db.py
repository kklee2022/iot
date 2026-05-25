"""Management command: block until the default database accepts connections."""
import logging
import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Pause until the default database accepts connections."

    def add_arguments(self, parser):
        parser.add_argument(
            "--retries",
            type=int,
            default=30,
            help="Maximum number of connection attempts (default: 30).",
        )
        parser.add_argument(
            "--interval",
            type=float,
            default=1.0,
            help="Seconds to wait between attempts (default: 1).",
        )

    def handle(self, *args, **options):
        retries = options["retries"]
        interval = options["interval"]

        self.stdout.write("Waiting for database...")
        for attempt in range(1, retries + 1):
            try:
                conn = connections["default"]
                conn.ensure_connection()
                self.stdout.write(self.style.SUCCESS("Database is available."))
                return
            except OperationalError:
                self.stdout.write(f"  attempt {attempt}/{retries} — not ready, retrying in {interval}s...")
                time.sleep(interval)

        raise SystemExit("Database did not become available in time.")
