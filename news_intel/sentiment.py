"""
Sentiment analyser — VADER-based, no external API needed.

VADER (Valence Aware Dictionary and sEntiment Reasoner) works well on
news headlines and short text without any fine-tuning or GPU.

Each article gets:
  - sentiment_score  (float, -1 to +1)
  - sentiment_label  ("positive", "negative", "neutral")
"""

from __future__ import annotations

import logging
from typing import Tuple

import pandas as pd

# VADER is part of nltk — we lazy-import to handle the data download gracefully.
logger = logging.getLogger(__name__)

_analyzer = None  # singleton


def _get_analyzer():
    """Lazy-initialise VADER. Downloads lexicon on first use if missing."""
    global _analyzer
    if _analyzer is not None:
        return _analyzer

    import nltk
    try:
        nltk.data.find("sentiment/vader_lexicon.zip")
    except LookupError:
        logger.info("Downloading VADER lexicon…")
        nltk.download("vader_lexicon", quiet=True)

    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    _analyzer = SentimentIntensityAnalyzer()
    return _analyzer


def score_text(text: str) -> Tuple[float, str]:
    """
    Return (compound_score, label) for a single text string.

    compound_score: float in [-1, 1]
    label: 'positive' | 'negative' | 'neutral'
    """
    if not text.strip():
        return 0.0, "neutral"

    analyzer = _get_analyzer()
    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    return round(compound, 4), label


def score_articles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add sentiment columns to the article DataFrame.

    New columns:
        sentiment_score  — float [-1, 1]
        sentiment_label  — 'positive' / 'negative' / 'neutral'
    """
    if df.empty:
        df["sentiment_score"] = pd.Series(dtype=float)
        df["sentiment_label"] = pd.Series(dtype=str)
        return df

    combined = df["title"].fillna("") + ". " + df["description"].fillna("")
    results = combined.apply(lambda t: score_text(t))

    df = df.copy()
    df["sentiment_score"] = results.apply(lambda r: r[0])
    df["sentiment_label"] = results.apply(lambda r: r[1])

    dist = df["sentiment_label"].value_counts()
    logger.info("Sentiment distribution:\n%s", dist.to_string())
    return df
