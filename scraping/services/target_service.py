import time
import structlog
from django.utils import timezone
from scraping.models import ScrapeTarget

logger = structlog.get_logger()

class ScrapeTargetService:
    def start(self, target):
        target.started_at = timezone.now()
        target.save()
        logger.info("scrape_target_started", target_id=target.id, url=target.url)

    def succeed(self, target, http_status=None):
        target.finished_at = timezone.now()
        target.duration_ms = int(
            (target.finished_at - target.started_at).total_seconds() * 1000
        )
        target.success = True
        target.http_status = http_status
        target.save()

        logger.info(
            "scrape_target_succeeded",
            target_id=target.id,
            duration_ms=target.duration_ms,
        )

    def fail(self, target, error_type, message=""):
        # if target.retries < 2 and error_type in ["TIMEOUT", "BROWSER_ERROR"]:
        #     target.retries += 1
        #     target.save()
        #     # re-attempt fetch
        # else:
        #     run.failed_targets += 1

        target.finished_at = timezone.now()
        target.duration_ms = int(
            (target.finished_at - target.started_at).total_seconds() * 1000
        )
        target.success = False
        target.error_type = error_type
        target.error_message = message
        target.save()

        logger.error(
            "scrape_target_failed",
            target_id=target.id,
            error_type=error_type,
            message=message,
        )
