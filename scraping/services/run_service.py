import structlog
from django.utils import timezone
from scraping.models import ScrapeRun, ScrapeTarget, Seed

logger = structlog.get_logger()

class ScrapeRunService:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run

    def create_run(self):
        run = ScrapeRun.objects.create(dry_run=self.dry_run)
        logger.info("scrape_run_created", run_id=run.id, dry_run=self.dry_run)
        return run

    def finalize_run(self, run):
        run.finished_at = timezone.now()
        if run.failed_targets > 0 and run.succeeded_targets > 0:
            run.status = ScrapeRun.STATUS_PARTIAL
        elif run.failed_targets > 0:
            run.status = ScrapeRun.STATUS_FAILED
        else:
            run.status = ScrapeRun.STATUS_SUCCESS

        run.save()
        logger.info(
            "scrape_run_finalized",
            run_id=run.id,
            status=run.status,
            succeeded=run.succeeded_targets,
            failed=run.failed_targets,
        )