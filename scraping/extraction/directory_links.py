from bs4 import BeautifulSoup
from scraping.extraction.base import Extractor, ExtractedCompany
from scraping.normalization.cleaners import clean_text, looks_like_company_name
from scraping.normalization.location import parse_city_state
from scraping.normalization.url_tools import absolute_url, is_probable_homepage

class DirectoryLinksExtractor(Extractor):
    source_type = "DIRECTORY_PAGE"

    def can_handle(self, url: str, html: str) -> bool:
        h = html.lower()
        return ("locations" in h or "find a location" in h or "directory" in h) and h.count("<a") > 30

    def extract(self, url: str, html: str) -> list[ExtractedCompany]:
        soup = BeautifulSoup(html, "lxml")
        results: list[ExtractedCompany] = []
        seen = set()

        # Heuristic: location-like link text
        for a in soup.select("a[href]"):
            text = clean_text(a.get_text(" "))
            if len(text) < 4:
                continue

            city, state = parse_city_state(text)
            if not city or not state:
                continue

            href = absolute_url(url, a.get("href", ""))
            # For directories, href is internal detail page. Website often the operator site (same domain).
            operator_site = url

            key = (city.lower(), state, href.lower())
            if key in seen:
                continue
            seen.add(key)

            # We don't know platform name from this page alone; we store directory evidence as Notes later.
            results.append(
                ExtractedCompany(
                    name="",
                    website=operator_site if is_probable_homepage(operator_site) else None,
                    country="United States",
                    state=state,
                    city=city,
                    source_url=url,
                    source_type=self.source_type,
                    notes=f"Location reference found: {text} -> {href}",
                )
            )

        return results
