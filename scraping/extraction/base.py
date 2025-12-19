from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class ExtractedCompany:
    name: str
    website: Optional[str]
    country: Optional[str]
    state: Optional[str]
    city: Optional[str]
    source_url: str
    source_type: str
    notes: str = ""
    locations_count: Optional[int] = None
    real_estate_intensive: Optional[bool] = None


class Extractor:
    source_type: str

    def can_handle(self, url: str, html: str) -> bool:
        raise NotImplementedError

    def extract(self, url: str, html: str) -> list[ExtractedCompany]:
        raise NotImplementedError
