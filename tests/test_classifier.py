"""Tests for news_intel.classifier — topic assignment and query filtering."""

import pytest
import pandas as pd

from news_intel.classifier import (
    classify_by_keywords,
    classify_articles,
    filter_by_query,
)


def _make_df(titles_and_descs):
    """Helper: create a DataFrame from list of (title, description) tuples."""
    return pd.DataFrame(
        [{"title": t, "description": d, "source": "Test", "url": "https://x.com"}
         for t, d in titles_and_descs]
    )


class TestKeywordClassification:
    def test_ai_topic_detected(self):
        df = _make_df([("OpenAI releases GPT-5 model", "The new large language model is faster.")])
        result = classify_by_keywords(df)
        assert result.iloc[0]["topic"] == "AI / ML"

    def test_crypto_topic_detected(self):
        df = _make_df([("Bitcoin surges past $100K", "Cryptocurrency markets rally.")])
        result = classify_by_keywords(df)
        assert result.iloc[0]["topic"] == "Crypto / Blockchain"

    def test_no_match_returns_none(self):
        df = _make_df([("Local bakery wins award", "A small bakery got recognition.")])
        result = classify_by_keywords(df)
        assert result.iloc[0]["topic"] is None

    def test_multiple_articles_classified(self):
        df = _make_df([
            ("Fed raises interest rates again", "The central bank tightens monetary policy."),
            ("New vaccine approved by FDA", "Healthcare regulators clear the drug."),
            ("NVIDIA announces new AI chip", "GPU maker targets deep learning market."),
        ])
        result = classify_by_keywords(df)
        topics = result["topic"].tolist()
        assert "Economy / Macro" in topics or "Markets / Stocks" in topics
        assert "Healthcare" in topics
        assert "AI / ML" in topics


class TestFullClassification:
    def test_no_none_topics_after_full_pipeline(self):
        df = _make_df([
            ("OpenAI launches ChatGPT update", "New AI features released."),
            ("Mystery event at local fair", "Something happened somewhere."),
            ("Bitcoin drops 10%", "Crypto markets tumble."),
        ])
        result = classify_articles(df)
        assert result["topic"].isna().sum() == 0

    def test_confidence_column_added(self):
        df = _make_df([("AI is the future", "Machine learning everywhere.")])
        result = classify_articles(df)
        assert "topic_confidence" in result.columns

    def test_empty_df_handled(self):
        df = pd.DataFrame(columns=["title", "description", "source", "url"])
        result = classify_articles(df)
        assert result.empty


class TestQueryFiltering:
    def test_relevant_articles_ranked_higher(self):
        df = _make_df([
            ("Artificial intelligence transforms healthcare", "AI diagnoses diseases."),
            ("Local sports team wins championship", "Exciting game last night."),
            ("Machine learning in autonomous driving", "Self-driving cars use neural networks."),
        ])
        result = filter_by_query(df, "artificial intelligence machine learning")
        assert len(result) > 0
        # AI articles should be ranked first
        assert "intelligence" in result.iloc[0]["title"].lower() or \
               "machine" in result.iloc[0]["title"].lower()

    def test_empty_query_returns_all(self):
        df = _make_df([("Test", "Body")])
        result = filter_by_query(df, "")
        assert len(result) == 1

    def test_empty_df_returns_empty(self):
        df = pd.DataFrame(columns=["title", "description"])
        result = filter_by_query(df, "anything")
        assert result.empty
