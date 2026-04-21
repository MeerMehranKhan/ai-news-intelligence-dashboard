"""
Pipeline orchestrator — runs the full analysis pipeline end-to-end.

This is the single entry point that the Streamlit UI calls.
It coordinates: fetch → clean → classify → sentiment → geo → trends → summarise.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

import pandas as pd

from news_intel.fetcher import fetch_all, RawArticle
from news_intel.cleaner import articles_to_dataframe, clean_articles
from news_intel.classifier import classify_articles, filter_by_query
from news_intel.sentiment import score_articles
from news_intel.geo import extract_geo
from news_intel.trends import generate_trend_report, TrendReport
from news_intel.summarizer import summarise_cluster, summarise_dashboard

logger = logging.getLogger(__name__)


@dataclass
class DashboardResult:
    """
    Complete output of the analysis pipeline.

    This object is passed directly to the Streamlit UI for rendering.
    """
    articles: pd.DataFrame                          # enriched article table
    trend_report: TrendReport                       # trend analysis
    dashboard_summary: str                          # overall narrative
    cluster_summaries: Dict[str, str]               # topic → narrative
    query: str = ""                                 # user query (if any)
    elapsed_seconds: float = 0.0                    # pipeline wall time
    article_count: int = 0
    source_count: int = 0
    topic_count: int = 0
    llm_used: bool = False
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def run_pipeline(
    query: str = "",
    lookback_days: Optional[int] = None,
) -> DashboardResult:
    """
    Execute the full intelligence pipeline.

    Args:
        query: Optional search query to filter/rank articles.
        lookback_days: Override for how far back to look.

    Returns:
        DashboardResult with all data needed to render the UI.
    """
    t0 = time.time()

    # 1. Fetch
    logger.info("Step 1/7 — Fetching articles…")
    raw_articles: List[RawArticle] = fetch_all(query)
    logger.info("Fetched %d raw articles", len(raw_articles))

    # 2. Clean
    logger.info("Step 2/7 — Cleaning & deduplicating…")
    df = articles_to_dataframe(raw_articles)
    df = clean_articles(df, lookback_days=lookback_days)

    # 3. Classify
    logger.info("Step 3/7 — Classifying topics…")
    df = classify_articles(df)

    # 4. Sentiment
    logger.info("Step 4/7 — Scoring sentiment…")
    df = score_articles(df)

    # 5. Geography
    logger.info("Step 5/7 — Extracting geo signals…")
    df = extract_geo(df)

    # 6. Filter by query (if provided)
    if query.strip():
        logger.info("Filtering by query: '%s'", query)
        df = filter_by_query(df, query)

    # 7. Trends
    logger.info("Step 6/7 — Detecting trends…")
    trend_report = generate_trend_report(df)

    # 8. Summarise
    logger.info("Step 7/7 — Generating summaries…")
    cluster_summaries: Dict[str, str] = {}
    if "topic" in df.columns:
        for topic in df["topic"].unique():
            cluster_df = df[df["topic"] == topic]
            cluster_summaries[topic] = summarise_cluster(cluster_df, topic)

    dashboard_summary = summarise_dashboard(df, trend_report.topic_counts)

    elapsed = round(time.time() - t0, 2)
    logger.info("Pipeline complete in %.2fs — %d articles", elapsed, len(df))

    from news_intel.config import Config

    return DashboardResult(
        articles=df,
        trend_report=trend_report,
        dashboard_summary=dashboard_summary,
        cluster_summaries=cluster_summaries,
        query=query,
        elapsed_seconds=elapsed,
        article_count=len(df),
        source_count=df["source"].nunique() if not df.empty else 0,
        topic_count=df["topic"].nunique() if "topic" in df.columns and not df.empty else 0,
        llm_used=Config.should_use_llm(),
        fetched_at=datetime.now(timezone.utc),
    )
