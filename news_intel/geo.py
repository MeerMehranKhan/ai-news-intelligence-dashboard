"""
Geography / region signal extractor.

Scans title + description for country and region mentions using
the keyword lists defined in constants.py.

This is intentionally simple — a production system would use NER,
but keyword matching is fast, explainable, and good enough for
a dashboard that surfaces "which regions are in the news today".
"""

from __future__ import annotations

import logging
from typing import List, Optional, Tuple

import pandas as pd

from news_intel.constants import COUNTRY_KEYWORDS, REGION_MAP

logger = logging.getLogger(__name__)


def _extract_countries(text: str) -> List[str]:
    """Return list of countries mentioned in *text*."""
    text_lower = text.lower()
    found = []
    for country, keywords in COUNTRY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                found.append(country)
                break  # one hit per country is enough
    return found


def extract_geo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add geography columns to the article DataFrame.

    New columns:
        countries  — list of mentioned country names
        regions    — list of corresponding regions
        primary_country — first detected country (or '')
        primary_region  — first detected region (or '')
    """
    if df.empty:
        for col in ("countries", "regions", "primary_country", "primary_region"):
            df[col] = pd.Series(dtype=object)
        return df

    df = df.copy()
    combined = df["title"].fillna("") + " " + df["description"].fillna("")

    countries_series = combined.apply(_extract_countries)

    df["countries"] = countries_series
    df["regions"] = countries_series.apply(
        lambda cs: list({REGION_MAP.get(c, "Other") for c in cs})
    )
    df["primary_country"] = countries_series.apply(
        lambda cs: cs[0] if cs else ""
    )
    df["primary_region"] = df["primary_country"].apply(
        lambda c: REGION_MAP.get(c, "") if c else ""
    )

    geo_count = (df["primary_country"] != "").sum()
    logger.info("Geo signals found for %d / %d articles", geo_count, len(df))
    return df
