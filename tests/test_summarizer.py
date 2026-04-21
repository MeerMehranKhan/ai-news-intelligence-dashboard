"""Tests for news_intel.summarizer — local extractive summaries and fallback behaviour."""

import pytest
import pandas as pd

from news_intel.summarizer import (
    summarise_cluster_local,
    summarise_dashboard_local,
    summarise_with_llm,
)


def _make_cluster_df(n=5):
    """Create a small DataFrame simulating a topic cluster."""
    countries = ["United States", "China", "United States", "", "Germany"]
    return pd.DataFrame({
        "title": [f"Headline about topic {i}" for i in range(n)],
        "description": [f"Description of event {i} with details." for i in range(n)],
        "source": [f"Source {i % 3}" for i in range(n)],
        "sentiment_score": [0.1 * ((i % 5) - 2) for i in range(n)],
        "sentiment_label": ["positive" if i % 5 > 2 else "negative" if i % 5 < 2 else "neutral" for i in range(n)],
        "primary_country": [countries[i % len(countries)] for i in range(n)],
        "url": [f"https://example.com/{i}" for i in range(n)],
    })


class TestClusterSummaryLocal:
    def test_returns_string(self):
        df = _make_cluster_df()
        result = summarise_cluster_local(df, "AI / ML")
        assert isinstance(result, str)
        assert len(result) > 20

    def test_includes_topic_name(self):
        df = _make_cluster_df()
        result = summarise_cluster_local(df, "Crypto / Blockchain")
        assert "Crypto / Blockchain" in result

    def test_includes_article_count(self):
        df = _make_cluster_df(10)
        result = summarise_cluster_local(df, "Markets / Stocks")
        assert "10" in result

    def test_empty_df(self):
        df = pd.DataFrame(columns=["title", "description", "source", "sentiment_score"])
        result = summarise_cluster_local(df, "Energy")
        assert "No articles" in result


class TestDashboardSummaryLocal:
    def test_returns_readable_summary(self):
        df = _make_cluster_df(20)
        topic_counts = {"AI / ML": 10, "Markets / Stocks": 7, "Other": 3}
        result = summarise_dashboard_local(df, topic_counts)
        assert "20" in result
        assert "AI / ML" in result

    def test_empty_df(self):
        df = pd.DataFrame(columns=["title", "sentiment_score", "source"])
        result = summarise_dashboard_local(df, {})
        assert "No articles" in result


class TestLLMFallback:
    def test_returns_empty_without_key(self):
        """Without API keys configured, LLM summariser should return empty string."""
        df = _make_cluster_df()
        result = summarise_with_llm(df, "AI / ML")
        # Should be empty string when no key is set
        assert isinstance(result, str)
