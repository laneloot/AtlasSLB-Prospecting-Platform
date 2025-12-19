from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

import structlog

from scraping.browser.browser_manager import BrowserManager
from scraping.browser.page_fetcher import PageFetcher
from scraping.policies.robots import RobotsPolicy
from scraping.policies.rate_limit import RateLimiter

from scraping.models import Seed, ScrapeRun, ScrapeTarget
from scraping.extraction.aggregator import ExtractionAggregator
from exports.models import PlatformCompany

logger = structlog.get_logger()


class Command(BaseCommand):
    help = "Run scraping pipeline and extract platform companies"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--limit", type=int, help="Limit number of seeds")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        limit = options.get("limit")

        # ---- Initialize run ----
        scrape_run = ScrapeRun.objects.create(
            status=ScrapeRun.STATUS_RUNNING,
            dry_run=dry_run,
            started_at=timezone.now(),
        )

        logger.info(
            "scrape_run_started",
            run_id=scrape_run.id,
            dry_run=dry_run,
        )

        # ---- Load dependencies ----
        browser_manager = BrowserManager(headless=True)
        page_fetcher = PageFetcher(browser_manager)
        robots_policy = RobotsPolicy(user_agent="AtlasSLB")
        rate_limiter = RateLimiter()
        extractor = ExtractionAggregator()

        browser_manager.start()

        try:
            seeds_qs = Seed.objects.filter(
                active=True,
                permanently_disabled=False,
            ).select_related("firm")

            if limit:
                seeds_qs = seeds_qs[:limit]

            for seed in seeds_qs:
                self._process_seed(
                    seed=seed,
                    scrape_run=scrape_run,
                    page_fetcher=page_fetcher,
                    robots_policy=robots_policy,
                    rate_limiter=rate_limiter,
                    extractor=extractor,
                    dry_run=dry_run,
                )

            # ---- Final status ----
            scrape_run.status = (
                ScrapeRun.STATUS_PARTIAL
                if scrape_run.failed_targets > 0
                else ScrapeRun.STATUS_SUCCESS
            )
            scrape_run.finished_at = timezone.now()
            scrape_run.save()

            logger.info(
                "scrape_run_completed",
                run_id=scrape_run.id,
                status=scrape_run.status,
                total=scrape_run.total_targets,
                succeeded=scrape_run.succeeded_targets,
                failed=scrape_run.failed_targets,
            )

        except Exception as exc:
            scrape_run.status = ScrapeRun.STATUS_FAILED
            scrape_run.failure_reason = str(exc)
            scrape_run.finished_at = timezone.now()
            scrape_run.save()

            logger.exception(
                "scrape_run_failed",
                run_id=scrape_run.id,
                error=str(exc),
            )
            raise

        finally:
            browser_manager.stop()

    # ------------------------------------------------------------------

    def _process_seed(
        self,
        *,
        seed,
        scrape_run,
        page_fetcher,
        robots_policy,
        rate_limiter,
        extractor,
        dry_run,
    ):
        url = seed.url

        # ---- robots.txt ----
        if not robots_policy.is_allowed(url):
            logger.info("robots_disallowed", url=url)
            return

        rate_limiter.wait(url)

        scrape_run.total_targets += 1
        scrape_run.save(update_fields=["total_targets"])

        try:
            result = page_fetcher.fetch(url)
            html = result["html"]

            ScrapeTarget.objects.create(
                scrape_run=scrape_run,
                url=url,
                success=True,
            )

            extracted = extractor.extract(url, html)

            if not dry_run:
                self._persist_companies(
                    extracted=extracted,
                    seed=seed,
                )

            scrape_run.succeeded_targets += 1
            scrape_run.save(update_fields=["succeeded_targets"])

            seed.last_scraped_at = timezone.now()
            seed.consecutive_failures = 0
            seed.save(update_fields=["last_scraped_at", "consecutive_failures"])

            logger.info(
                "seed_processed",
                seed_id=seed.id,
                url=url,
                extracted_count=len(extracted),
            )

        except Exception as exc:
            ScrapeTarget.objects.create(
                scrape_run=scrape_run,
                url=url,
                success=False,
                error=str(exc),
            )

            scrape_run.failed_targets += 1
            scrape_run.save(update_fields=["failed_targets"])

            seed.consecutive_failures += 1
            if seed.consecutive_failures >= 3:
                seed.permanently_disabled = True

            seed.save(update_fields=["consecutive_failures", "permanently_disabled"])

            logger.error(
                "seed_failed",
                seed_id=seed.id,
                url=url,
                error=str(exc),
            )

    # ------------------------------------------------------------------

    def _persist_companies(self, *, extracted, seed):
        """
        DB-first persistence.
        Idempotent via get_or_create.
        """
        with transaction.atomic():
            for item in extracted:
                PlatformCompany.objects.get_or_create(
                    name=item.name,
                    defaults={
                        "website": item.website,
                        "country": item.country,
                        "state": item.state,
                        "city": item.city,
                        "source_url": item.source_url,
                        "source_type": item.source_type,
                        "notes": item.notes,
                        "locations_count": item.locations_count,
                        "real_estate_intensive": item.real_estate_intensive,
                        "firm": seed.firm,
                    },
                )
