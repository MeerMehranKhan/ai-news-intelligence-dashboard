"""
Cleaner — normalise, deduplicate, and filter articles.

Takes RawArticle objects from the fetcher, returns a clean pandas DataFrame
that the rest of the pipeline consumes.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import pandas as pd

from news_intel.fetcher import RawArticle
from news_intel.config import Config
from news_intel.utils import fingerprint, normalize_whitespace, now_utc

logger = logging.getLogger(__name__)


def articles_to_dataframe(articles: List[RawArticle]) -> pd.DataFrame:
    """Convert a list of RawArticle objects to a DataFrame."""
    records = [a.to_dict() for a in articles]
    df = pd.DataFrame(records)
    if df.empty:
        return _empty_df()
    return df


def _empty_df() -> pd.DataFrame:
    """Return an empty DataFrame with the expected schema."""
    return pd.DataFrame(columns=[
        "title", "url", "source", "published", "description",
        "category_hint", "region_hint",
    ])


def clean_articles(
    df: pd.DataFrame,
    lookback_days: Optional[int] = None,
) -> pd.DataFrame:
    """
    Full cleaning pipeline:
      1. Drop rows with missing titles
      2. Normalise whitespace
      3. Parse dates
      4. Filter by lookback window
      5. Deduplicate by content fingerprint
      6. Sort by published date descending

    Args:
        df: Raw article DataFrame.
        lookback_days: Only keep articles within this many days. None = use config default.

    Returns:
        Cleaned DataFrame.
    """
    if df.empty:
        return _empty_df()

    # 1. Drop empty titles
    df = df.dropna(subset=["title"])
    df = df[df["title"].str.strip().astype(bool)].copy()

    if df.empty:
        return _empty_df()

    # 2. Normalise text fields
    df["title"] = df["title"].apply(normalize_whitespace)
    df["description"] = df["description"].fillna("").apply(normalize_whitespace)

    # 3. Parse dates
    df["published"] = pd.to_datetime(df["published"], errors="coerce", utc=True)

    # 4. Filter by lookback
    days = lookback_days or Config.DEFAULT_LOOKBACK_DAYS
    cutoff = now_utc() - timedelta(days=days)
    has_date = df["published"].notna()
    df = df[~has_date | (df["published"] >= cutoff)].copy()

    # 5. Deduplicate
    df["_fingerprint"] = (df["title"] + " " + df["description"]).apply(fingerprint)
    before = len(df)
    df = df.drop_duplicates(subset="_fingerprint", keep="first")
    dupes = before - len(df)
    if dupes:
        logger.info("Removed %d duplicate articles", dupes)
    df = df.drop(columns=["_fingerprint"])

    # 6. Sort
    df = df.sort_values("published", ascending=False, na_position="last")
    df = df.reset_index(drop=True)

    logger.info("Clean article count: %d", len(df))
    return df
