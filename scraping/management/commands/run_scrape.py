from django.core.management.base import BaseCommand

from scraping.services.run_service import ScrapeRunService
from scraping.services.seed_service import SeedService
from scraping.services.target_service import ScrapeTargetService
from scraping.models import ScrapeTarget

class Command(BaseCommand):
    help = "Run scraping job"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--limit", type=int)

    def handle(self, *args, **options):
        run_service = ScrapeRunService(dry_run=options["dry_run"])
        seed_service = SeedService()
        target_service = ScrapeTargetService()

        run = run_service.create_run()
        run.status = run.STATUS_RUNNING
        run.save()

        seeds = seed_service.get_active_seeds(limit=options.get("limit"))
        run.total_targets = len(seeds)
        run.save()

        for seed in seeds:
            target = ScrapeTarget.objects.create(
                scrape_run=run,
                url=seed.url,
            )

            try:
                target_service.start(target)

                from scraping.browser.browser_manager import BrowserManager
                from scraping.browser.page_fetcher import PageFetcher

                browser = BrowserManager(headless=True)
                browser.start()

                fetcher = PageFetcher(browser)

                # inside loop (replace placeholder)
                result = fetcher.fetch(target.url)
                target_service.succeed(
                    target,
                    http_status=result.get("http_status"),
                )

                run.succeeded_targets += 1
                browser.stop()

            except Exception as e:
                target_service.fail(target, "UNKNOWN_ERROR", str(e))
                run.failed_targets += 1

            run.save()

        run_service.finalize_run(run)
