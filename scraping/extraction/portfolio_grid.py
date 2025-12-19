from bs4 import BeautifulSoup
from scraping.extraction.base import Extractor, ExtractedCompany
from scraping.normalization.cleaners import clean_text, looks_like_company_name
from scraping.normalization.url_tools import absolute_url, is_probable_homepage

class PortfolioGridExtractor(Extractor):
    source_type = "PORTFOLIO_PAGE"

    def can_handle(self, url: str, html: str) -> bool:
        # Heuristic: common keywords + lots of links/cards
        h = html.lower()
        return ("portfolio" in h or "our companies" in h or "our brands" in h) and h.count("<a") > 20

    def extract(self, url: str, html: str) -> list[ExtractedCompany]:
        soup = BeautifulSoup(html, "lxml")
        results: list[ExtractedCompany] = []

        # Common card-like patterns
        cards = soup.select("[class*='portfolio'], [class*='company'], [class*='brand'], li, article, section")
        seen = set()

        for card in cards:
            a_tags = card.select("a[href]")
            if not a_tags:
                continue

            name = ""
            website = ""

            # Prefer the most text-rich anchor in the card
            best_a = max(a_tags, key=lambda a: len(clean_text(a.get_text(" "))), default=None)
            if best_a:
                name = clean_text(best_a.get_text(" "))
                href = best_a.get("href", "")
                href = absolute_url(url, href)

                # Sometimes href is the company site; sometimes it’s an internal detail page.
                if is_probable_homepage(href):
                    website = href

            if not looks_like_company_name(name):
                continue

            key = (name.lower(), website.lower() if website else "")
            if key in seen:
                continue
            seen.add(key)

            results.append(
                ExtractedCompany(
                    name=name,
                    website=website or None,
                    country=None,
                    state=None,
                    city=None,
                    source_url=url,
                    source_type=self.source_type,
                    notes="",
                )
            )

        return results
