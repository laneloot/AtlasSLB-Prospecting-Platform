import structlog
from core.exceptions import ScraperError

logger = structlog.get_logger()

class PageFetcher:
    def __init__(self, browser_manager, timeout_ms=30000):
        self.browser_manager = browser_manager
        self.timeout_ms = timeout_ms

    def fetch(self, url, user_agent=None):
        context = self.browser_manager.new_context(user_agent=user_agent)
        page = context.new_page()
        page.set_default_timeout(self.timeout_ms)

        try:
            logger.info("page_fetch_started", url=url)
            response = page.goto(url, wait_until="networkidle")
            status = response.status if response else None
            content = page.content()

            logger.info(
                "page_fetch_completed",
                url=url,
                http_status=status,
            )

            return {
                "url": url,
                "http_status": status,
                "html": content,
            }

        except Exception as e:
            logger.error("page_fetch_failed", url=url, error=str(e))
            raise ScraperError(str(e))

        finally:
            context.close()
