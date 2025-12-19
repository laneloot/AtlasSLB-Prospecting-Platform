import re

def clean_text(value: str) -> str:
    value = (value or "").strip()
    value = re.sub(r"\s+", " ", value)
    return value

def looks_like_company_name(name: str) -> bool:
    name = clean_text(name)
    return len(name) >= 2 and len(name) <= 255
