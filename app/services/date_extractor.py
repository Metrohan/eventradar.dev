import re
from dateparser import parse
from typing import Optional


def extract_date_from_text(text: str) -> Optional[str]:
    """
    Metin içinden ilk geçerli tarihi döndürür (ISO formatında).
    """
    if not text:
        return None
    # Basit tarih regex: 12 Aralık 2025, 13 Mart, 07 Aralık, vs.
    patterns = [
        r"\b\d{1,2} [A-Za-zÇĞİÖŞÜçğıöşü]+ \d{4}\b",  # 12 Aralık 2025
        r"\b\d{1,2} [A-Za-zÇĞİÖŞÜçğıöşü]+\b",  # 13 Mart
        r"\b\d{1,2}\.\d{1,2}\.\d{4}\b",  # 12.12.2025
        r"\b\d{1,2}/\d{1,2}/\d{4}\b",  # 12/12/2025
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            dt = parse(match.group(), languages=["tr"])
            if dt:
                return dt.isoformat()
    return None
