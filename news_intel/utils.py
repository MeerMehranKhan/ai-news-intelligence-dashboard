"""
Shared utility helpers used across the pipeline.
"""

from __future__ import annotations

import hashlib
import html
import re
import unicodedata
from datetime import datetime, timezone
from typing import Optional


def clean_html(raw: str) -> str:
    """Strip HTML tags and decode entities from a string."""
    if not raw:
        return ""
    text = html.unescape(raw)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_whitespace(text: str) -> str:
    """Collapse runs of whitespace to single spaces."""
    return re.sub(r"\s+", " ", text).strip()


def fingerprint(text: str) -> str:
    """
    Create a content fingerprint for deduplication.

    Lowercases, strips punctuation, and hashes the result.
    Two articles with near-identical bodies produce the same fingerprint.
    """
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = normalize_whitespace(text)
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def safe_parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """
    Best-effort date parsing. Returns timezone-aware UTC datetime or None.
    Handles common RSS date formats.
    """
    if not date_str:
        return None

    from email.utils import parsedate_to_datetime

    try:
        dt = parsedate_to_datetime(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        pass

    # Fallback: try ISO 8601
    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(date_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue

    return None


def truncate(text: str, max_len: int = 300) -> str:
    """Truncate text to *max_len* characters, appending '…' if trimmed."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rsplit(" ", 1)[0] + "…"


def now_utc() -> datetime:
    """Current time in UTC (timezone-aware)."""
    return datetime.now(timezone.utc)
