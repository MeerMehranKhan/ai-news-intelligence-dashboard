"""
Summariser — generates narrative summaries of article clusters.

Two modes:
  1. **Local extractive** (default, no API key needed)
     Picks the most representative sentences using TF-IDF centrality.
     Constructs a structured narrative from top keywords and article data.

  2. **LLM-enhanced** (optional, requires OPENAI_API_KEY or ANTHROPIC_API_KEY)
     Sends cluster data to an LLM for editorial-style narrative summaries.
     Falls back to local mode on any error.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from news_intel.config import Config

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Local extractive summariser
# ---------------------------------------------------------------------------

def _extractive_summary(texts: List[str], n_sentences: int = 3) -> str:
    """
    Pick the most representative sentences from *texts* using TF-IDF centrality.

    Strategy: vectorise all texts, pick those closest to the centroid.
    """
    if not texts:
        return "No articles available for summarisation."
    if len(texts) <= n_sentences:
        return " ".join(texts)

    vectorizer = TfidfVectorizer(stop_words="english", max_features=2000)
    try:
        tfidf = vectorizer.fit_transform(texts)
    except ValueError:
        return texts[0] if texts else ""

    centroid = np.asarray(tfidf.mean(axis=0))
    sims = cosine_similarity(tfidf, centroid).flatten()
    top_idx = sims.argsort()[::-1][:n_sentences]
    top_idx = sorted(top_idx)  # maintain original order
    return " ".join(texts[i] for i in top_idx)


def summarise_cluster_local(
    df: pd.DataFrame,
    topic: str,
) -> str:
    """
    Generate a structured local summary for a topic cluster.

    Returns a human-readable narrative paragraph.
    """
    if df.empty:
        return f"No articles found for {topic}."

    n = len(df)
    titles = df["title"].tolist()

    # Sentiment summary
    avg_sent = df["sentiment_score"].mean() if "sentiment_score" in df.columns else 0
    if avg_sent > 0.1:
        tone = "generally positive"
    elif avg_sent < -0.1:
        tone = "generally negative"
    else:
        tone = "mixed or neutral"

    # Top sources
    top_sources = df["source"].value_counts().head(3).index.tolist()

    # Representative headline (closest to centroid)
    lead = _extractive_summary(titles, n_sentences=2)

    # Build narrative
    parts = [
        f"**{topic}** — {n} article{'s' if n != 1 else ''} with {tone} sentiment.",
        f"Key headlines: {lead}",
        f"Covered by: {', '.join(top_sources)}.",
    ]

    # Region info if available
    if "primary_country" in df.columns:
        countries = df["primary_country"][df["primary_country"] != ""].value_counts().head(3)
        if not countries.empty:
            parts.append(f"Regional focus: {', '.join(countries.index.tolist())}.")

    return " ".join(parts)


def summarise_dashboard_local(
    df: pd.DataFrame,
    topic_counts: Dict[str, int],
) -> str:
    """
    Generate an overall dashboard summary using local heuristics.
    """
    if df.empty:
        return "No articles available. Try refreshing or broadening your search."

    n = len(df)
    top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_topic_str = ", ".join(f"{t} ({c})" for t, c in top_topics)

    avg_sent = df["sentiment_score"].mean() if "sentiment_score" in df.columns else 0
    if avg_sent > 0.1:
        mood = "The overall tone of coverage is **positive**."
    elif avg_sent < -0.1:
        mood = "The overall tone of coverage is **cautious or negative**."
    else:
        mood = "The overall tone of coverage is **balanced**."

    sources = df["source"].nunique()

    return (
        f"📊 **Dashboard Summary** — Analysed **{n} articles** from **{sources} sources**. "
        f"The most active topics are: {top_topic_str}. {mood} "
        f"Scroll down for detailed breakdowns by topic, sentiment, region, and trend."
    )


# ---------------------------------------------------------------------------
# LLM-enhanced summariser (optional)
# ---------------------------------------------------------------------------

def _call_openai(prompt: str) -> str:
    """Call OpenAI API. Returns empty string on failure."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": (
                    "You are a concise news analyst. Summarise the given news data "
                    "into a clear, professional intelligence briefing. Focus on: "
                    "what is happening, why it matters, and what is gaining momentum. "
                    "Use bullet points sparingly. Keep it under 200 words."
                )},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        logger.warning("OpenAI call failed: %s — falling back to local.", exc)
        return ""


def _call_anthropic(prompt: str) -> str:
    """Call Anthropic API. Returns empty string on failure."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=Config.ANTHROPIC_MODEL,
            max_tokens=500,
            messages=[{"role": "user", "content": (
                "You are a concise news analyst. Summarise the following news data "
                "into a clear, professional intelligence briefing. Focus on: "
                "what is happening, why it matters, and what is gaining momentum. "
                "Keep it under 200 words.\n\n" + prompt
            )}],
        )
        return response.content[0].text.strip()
    except Exception as exc:
        logger.warning("Anthropic call failed: %s — falling back to local.", exc)
        return ""


def _build_llm_prompt(df: pd.DataFrame, topic: Optional[str] = None) -> str:
    """Build a compact prompt from article data for LLM consumption."""
    subset = df.head(30)  # limit tokens
    lines = []
    if topic:
        lines.append(f"Topic: {topic}")
    lines.append(f"Total articles: {len(df)}")

    if "sentiment_score" in df.columns:
        lines.append(f"Average sentiment: {df['sentiment_score'].mean():.2f}")

    lines.append("\nHeadlines:")
    for _, row in subset.iterrows():
        src = row.get("source", "")
        title = row.get("title", "")
        sent = row.get("sentiment_label", "")
        lines.append(f"- [{src}] {title} ({sent})")

    return "\n".join(lines)


def summarise_with_llm(
    df: pd.DataFrame,
    topic: Optional[str] = None,
) -> str:
    """
    Attempt LLM summary. Returns empty string if LLM is not available / fails.
    """
    if not Config.should_use_llm():
        return ""

    prompt = _build_llm_prompt(df, topic)

    if Config.OPENAI_API_KEY:
        result = _call_openai(prompt)
        if result:
            return result

    if Config.ANTHROPIC_API_KEY:
        result = _call_anthropic(prompt)
        if result:
            return result

    return ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def summarise_cluster(df: pd.DataFrame, topic: str) -> str:
    """
    Summarise a topic cluster. Uses LLM if available, else local.
    """
    llm_result = summarise_with_llm(df, topic)
    if llm_result:
        return llm_result
    return summarise_cluster_local(df, topic)


def summarise_dashboard(
    df: pd.DataFrame,
    topic_counts: Dict[str, int],
) -> str:
    """
    Generate the overall dashboard narrative summary.
    """
    llm_result = summarise_with_llm(df)
    if llm_result:
        return llm_result
    return summarise_dashboard_local(df, topic_counts)
