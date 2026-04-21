"""
Topic classifier — assigns each article a topic label.

Strategy (layered):
  1. **Keyword matching** (fast, deterministic, explainable)
     Scans title + description against the TOPIC_KEYWORDS map.
  2. **TF-IDF + nearest-centroid fallback**
     For articles that don't match any keyword, we compute TF-IDF vectors
     against labelled articles and assign the nearest topic centroid.

This avoids expensive embeddings while still giving reasonable results.
"""

from __future__ import annotations

import logging
from collections import Counter
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from news_intel.constants import TOPIC_KEYWORDS, TOPICS

logger = logging.getLogger(__name__)


def _keyword_match(text: str) -> Optional[str]:
    """
    Return the first matching topic for *text* using keyword lookup.
    Returns None if no match is found.
    """
    text_lower = text.lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return topic
    return None


def classify_by_keywords(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a 'topic' column using keyword matching.
    Unmatched articles get topic = None (handled later by fallback).
    """
    df = df.copy()
    combined = df["title"].fillna("") + " " + df["description"].fillna("")
    df["topic"] = combined.apply(_keyword_match)
    matched = df["topic"].notna().sum()
    logger.info("Keyword match: %d / %d articles classified", matched, len(df))
    return df


def _fallback_tfidf(df: pd.DataFrame) -> pd.DataFrame:
    """
    For unclassified articles, use TF-IDF similarity to labelled articles.

    1. Build TF-IDF matrix from labelled + unlabelled articles.
    2. Compute centroid vector for each topic from labelled articles.
    3. Assign each unlabelled article to the nearest centroid.
    """
    labelled = df[df["topic"].notna()].copy()
    unlabelled = df[df["topic"].isna()].copy()

    if unlabelled.empty or labelled.empty:
        # If no labelled articles exist, everything becomes "Other"
        if unlabelled.empty:
            return df
        df.loc[df["topic"].isna(), "topic"] = "Other"
        return df

    # Combine text
    all_text = pd.concat([labelled, unlabelled], ignore_index=True)
    combined = all_text["title"].fillna("") + " " + all_text["description"].fillna("")

    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words="english",
        ngram_range=(1, 2),
    )
    tfidf_matrix = vectorizer.fit_transform(combined)

    n_labelled = len(labelled)
    labelled_vectors = tfidf_matrix[:n_labelled]
    unlabelled_vectors = tfidf_matrix[n_labelled:]

    # Build centroids per topic
    centroids: Dict[str, np.ndarray] = {}
    for topic in labelled["topic"].unique():
        mask = labelled["topic"].values == topic
        centroids[topic] = np.asarray(labelled_vectors[mask].mean(axis=0))

    # Stack centroids into a matrix
    topic_names = list(centroids.keys())
    centroid_matrix = np.vstack([np.asarray(centroids[t]) for t in topic_names])

    # Compute similarity
    sims = cosine_similarity(unlabelled_vectors, centroid_matrix)
    best_idx = sims.argmax(axis=1)
    assigned = [topic_names[i] for i in best_idx]

    df.loc[df["topic"].isna(), "topic"] = assigned
    logger.info("TF-IDF fallback classified %d articles", len(assigned))
    return df


def classify_articles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full classification pipeline: keyword match → TF-IDF fallback.

    Adds columns:
        topic — primary topic label
        topic_confidence — 'keyword' or 'tfidf' indicating the method used
    """
    if df.empty:
        df["topic"] = pd.Series(dtype=str)
        df["topic_confidence"] = pd.Series(dtype=str)
        return df

    df = classify_by_keywords(df)
    # Mark confidence level before fallback
    df["topic_confidence"] = df["topic"].apply(
        lambda t: "keyword" if t is not None else None
    )

    df = _fallback_tfidf(df)

    # Fill any remaining None
    df["topic"] = df["topic"].fillna("Other")
    df["topic_confidence"] = df["topic_confidence"].fillna("tfidf")

    # Stats
    dist = df["topic"].value_counts()
    logger.info("Topic distribution:\n%s", dist.to_string())
    return df


def filter_by_query(df: pd.DataFrame, query: str) -> pd.DataFrame:
    """
    Filter articles relevant to a free-text user query.

    Uses TF-IDF cosine similarity against the query string.
    Returns articles sorted by relevance, keeping those above a threshold.
    """
    if df.empty or not query.strip():
        return df

    combined = (df["title"].fillna("") + " " + df["description"].fillna("")).tolist()
    combined.append(query)

    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words="english",
        ngram_range=(1, 2),
    )
    tfidf = vectorizer.fit_transform(combined)

    query_vec = tfidf[-1]
    article_vecs = tfidf[:-1]

    sims = cosine_similarity(article_vecs, query_vec).flatten()
    df = df.copy()
    df["relevance_score"] = sims

    # Keep articles with any relevance, or at least top 50
    threshold = 0.05
    relevant = df[df["relevance_score"] >= threshold]
    if len(relevant) < 10:
        relevant = df.nlargest(min(50, len(df)), "relevance_score")

    return relevant.sort_values("relevance_score", ascending=False).reset_index(drop=True)
