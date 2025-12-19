from bs4 import BeautifulSoup
from scraping.extraction.base import Extractor, ExtractedCompany
from scraping.normalization.cleaners import clean_text

ACQ_KEYWORDS = ("acquired", "acquisition", "announced", "has acquired", "completed the acquisition")

class PressReleaseExtractor(Extractor):
    source_type = "PRESS_RELEASE"

    def can_handle(self, url: str, html: str) -> bool:
        text = BeautifulSoup(html, "lxml").get_text(" ").lower()
        return any(k in text for k in ACQ_KEYWORDS)

    def extract(self, url: str, html: str) -> list[ExtractedCompany]:
        soup = BeautifulSoup(html, "lxml")
        text = clean_text(soup.get_text(" "))

        # For now we don’t hallucinate company names.
        # We persist the evidence in notes; entity extraction becomes a later phase.
        return [
            ExtractedCompany(
                name="",
                website=None,
                country=None,
                state=None,
                city=None,
                source_url=url,
                source_type=self.source_type,
                notes=f"Acquisition-related page detected. Evidence stored for later NLP/entity extraction.",
            )
        ]
