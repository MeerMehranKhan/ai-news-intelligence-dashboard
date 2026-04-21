"""
Trend detection — identifies rising topics, keyword spikes, and patterns.

Works on the enriched article DataFrame (after classification + sentiment).
All logic is purely local: TF-IDF keyword extraction + temporal counting.
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from news_intel.utils import now_utc

logger = logging.getLogger(__name__)


@dataclass
class TrendReport:
    """Container for trend analysis results."""
    top_keywords: List[Tuple[str, float]]         # (keyword, tfidf_weight)
    topic_counts: Dict[str, int]                    # topic → article count
    rising_topics: List[Tuple[str, float]]          # (topic, growth_ratio)
    sentiment_by_topic: Dict[str, float]            # topic → avg sentiment
    source_concentration: Dict[str, int]            # source → count
    hourly_volume: List[Tuple[str, int]]            # (hour_label, count)
    total_articles: int = 0


def extract_top_keywords(
    df: pd.DataFrame,
    n: int = 20,
) -> List[Tuple[str, float]]:
    """
    Extract the most important keywords from the corpus using TF-IDF.

    Returns list of (keyword, weight) tuples sorted by weight descending.
    """
    if df.empty:
        return []

    combined = (df["title"].fillna("") + " " + df["description"].fillna("")).tolist()

    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    
    custom_stopwords = {
        "said", "new", "president", "told", "added", "reported", "according",
        "year", "years", "time", "day", "days", "week", "weeks", "month", "months",
        "people", "just", "like", "say", "says", "news", "report", "state", 
        "states", "world", "make", "made", "right", "way", "going", "know", 
        "think", "good", "well", "now", "today", "yesterday", "tomorrow", "use",
        "used", "using", "work", "working", "want", "wanted", "help", "helped",
        "need", "needed", "come", "came", "look", "looked", "take", "took",
        "mr", "ms", "mrs", "dr", "prof", "percent", "per", "cent", "cents",
        "don", "didn", "has", "have", "had", "isn", "aren", "wasn", "weren",
        "reuters", "bbc", "nyt", "bloomberg", "ap", "cnn", "fox", "daily",
        "times", "post", "journal", "wall", "street", "guardian", "telegraph",
        "update", "updates", "breaking", "exclusive", "interview", "video", "photo",
        "images", "live", "coverage", "latest", "watch", "read", "share", "click",
        "subscribe", "newsletter", "podcast", "listen", "audio", "app", "download"
    }
    stop_words = list(ENGLISH_STOP_WORDS.union(custom_stopwords))

    vectorizer = TfidfVectorizer(
        max_features=3000,
        stop_words=stop_words,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.8,
    )

    try:
        tfidf = vectorizer.fit_transform(combined)
    except ValueError:
        # Not enough documents for min_df=2
        vectorizer.min_df = 1
        tfidf = vectorizer.fit_transform(combined)

    feature_names = vectorizer.get_feature_names_out()
    mean_weights = np.asarray(tfidf.mean(axis=0)).flatten()

    top_indices = mean_weights.argsort()[::-1][:n]
    keywords = [(feature_names[i], round(float(mean_weights[i]), 4)) for i in top_indices]
    return keywords


def compute_topic_counts(df: pd.DataFrame) -> Dict[str, int]:
    """Count articles per topic."""
    if "topic" not in df.columns or df.empty:
        return {}
    return df["topic"].value_counts().to_dict()


def compute_rising_topics(
    df: pd.DataFrame,
    recent_hours: int = 12,
) -> List[Tuple[str, float]]:
    """
    Detect topics with disproportionately more coverage in the last
    *recent_hours* compared to the overall dataset.

    Returns (topic, growth_ratio) sorted descending.
    A ratio > 1.0 means the topic is over-represented recently.
    """
    if df.empty or "topic" not in df.columns or "published" not in df.columns:
        return []

    df_dated = df.dropna(subset=["published"]).copy()
    if df_dated.empty:
        return []

    cutoff = now_utc() - timedelta(hours=recent_hours)
    recent = df_dated[df_dated["published"] >= cutoff]

    if recent.empty or len(recent) < 3:
        return []

    overall_dist = df_dated["topic"].value_counts(normalize=True)
    recent_dist = recent["topic"].value_counts(normalize=True)

    rising = []
    for topic in recent_dist.index:
        overall_share = overall_dist.get(topic, 0.001)
        recent_share = recent_dist[topic]
        ratio = recent_share / overall_share
        if ratio > 1.0 and recent_dist[topic] * len(recent) >= 2:
            rising.append((topic, round(ratio, 2)))

    rising.sort(key=lambda x: x[1], reverse=True)
    return rising


def compute_sentiment_by_topic(df: pd.DataFrame) -> Dict[str, float]:
    """Average sentiment score per topic."""
    if df.empty or "sentiment_score" not in df.columns:
        return {}
    return df.groupby("topic")["sentiment_score"].mean().round(3).to_dict()


def compute_source_concentration(df: pd.DataFrame) -> Dict[str, int]:
    """Article count per source."""
    if df.empty:
        return {}
    return df["source"].value_counts().head(15).to_dict()


def compute_hourly_volume(df: pd.DataFrame) -> List[Tuple[str, int]]:
    """Article count grouped by hour (last 48h)."""
    if df.empty or "published" not in df.columns:
        return []

    df_dated = df.dropna(subset=["published"]).copy()
    if df_dated.empty:
        return []

    cutoff = now_utc() - timedelta(hours=48)
    df_dated = df_dated[df_dated["published"] >= cutoff]

    if df_dated.empty:
        return []

    df_dated["hour"] = df_dated["published"].dt.strftime("%Y-%m-%d %H:00")
    counts = df_dated.groupby("hour").size().reset_index(name="count")
    return list(zip(counts["hour"], counts["count"]))


def generate_trend_report(df: pd.DataFrame) -> TrendReport:
    """
    Run all trend analyses and return a TrendReport.
    """
    return TrendReport(
        top_keywords=extract_top_keywords(df),
        topic_counts=compute_topic_counts(df),
        rising_topics=compute_rising_topics(df),
        sentiment_by_topic=compute_sentiment_by_topic(df),
        source_concentration=compute_source_concentration(df),
        hourly_volume=compute_hourly_volume(df),
        total_articles=len(df),
    )
