from scraping.extraction.base import ExtractedCompany
from scraping.extraction.portfolio_grid import PortfolioGridExtractor
from scraping.extraction.directory_links import DirectoryLinksExtractor
from scraping.extraction.press_release import PressReleaseExtractor

class ExtractionAggregator:
    def __init__(self):
        self.extractors = [
            PortfolioGridExtractor(),
            DirectoryLinksExtractor(),
            PressReleaseExtractor(),
        ]

    def extract_all(self, url: str, html: str) -> list[ExtractedCompany]:
        items: list[ExtractedCompany] = []
        for ex in self.extractors:
            if ex.can_handle(url, html):
                items.extend(ex.extract(url, html))

        # Deduplicate (name + website + source_type)
        seen = set()
        out: list[ExtractedCompany] = []
        for it in items:
            key = ((it.name or "").lower(), (it.website or "").lower(), it.source_type)
            if key in seen:
                continue
            seen.add(key)
            out.append(it)
        return out
