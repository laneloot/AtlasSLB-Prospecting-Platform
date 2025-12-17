import structlog

logger = structlog.get_logger()

class ScrapeRunTracker:
    def __init__(self, scrape_run):
        self.scrape_run = scrape_run

    def start(self):
        self.scrape_run.status = "RUNNING"
        self.scrape_run.save()
        logger.info("scrape_run_started", run_id=self.scrape_run.id)

    def fail(self, reason):
        self.scrape_run.status = "FAILED"
        self.scrape_run.save()
        logger.error(
            "scrape_run_failed",
            run_id=self.scrape_run.id,
            reason=reason,
        )

    def finish(self, success=True):
        self.scrape_run.status = "SUCCESS" if success else "PARTIAL_SUCCESS"
        self.scrape_run.save()
        logger.info(
            "scrape_run_finished",
            run_id=self.scrape_run.id,
            status=self.scrape_run.status,
        )
