import tldextract
from urllib.parse import urlparse, urljoin

def normalize_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    if url.startswith("//"):
        url = "https:" + url
    return url

def absolute_url(base_url: str, maybe_relative: str) -> str:
    return normalize_url(urljoin(base_url, maybe_relative))

def is_probable_homepage(url: str) -> bool:
    try:
        p = urlparse(url)
        if p.scheme not in ("http", "https"):
            return False
        ext = tldextract.extract(url)
        return bool(ext.domain) and bool(ext.suffix)
    except Exception:
        return False
