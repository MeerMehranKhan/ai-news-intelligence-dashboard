"""Tests for news_intel.cleaner — deduplication, normalisation, date filtering."""

import pytest
import pandas as pd
from datetime import datetime, timedelta, timezone

from news_intel.cleaner import clean_articles, articles_to_dataframe, _empty_df
from news_intel.fetcher import RawArticle


def _make_articles(n=5, base_title="Test headline"):
    """Helper to create a list of RawArticle objects."""
    now = datetime.now(timezone.utc)
    return [
        RawArticle(
            title=f"{base_title} {i}",
            url=f"https://example.com/article-{i}",
            source=f"Source {i % 3}",
            published=now - timedelta(hours=i),
            description=f"Description for article {i} with unique content.",
        )
        for i in range(n)
    ]


class TestArticlesToDataframe:
    def test_converts_list_to_df(self):
        articles = _make_articles(3)
        df = articles_to_dataframe(articles)
        assert len(df) == 3
        assert "title" in df.columns
        assert "url" in df.columns

    def test_empty_list_returns_empty_df(self):
        df = articles_to_dataframe([])
        assert df.empty


class TestCleanArticles:
    def test_removes_empty_titles(self):
        articles = _make_articles(3)
        articles.append(RawArticle(title="", url="https://x.com", source="X"))
        articles.append(RawArticle(title="   ", url="https://y.com", source="Y"))
        df = articles_to_dataframe(articles)
        cleaned = clean_articles(df, lookback_days=30)
        assert len(cleaned) == 3

    def test_deduplicates_identical_articles(self):
        articles = [
            RawArticle(title="Same headline", url="https://a.com", source="A",
                       published=datetime.now(timezone.utc), description="Same body"),
            RawArticle(title="Same headline", url="https://b.com", source="B",
                       published=datetime.now(timezone.utc), description="Same body"),
        ]
        df = articles_to_dataframe(articles)
        cleaned = clean_articles(df, lookback_days=30)
        assert len(cleaned) == 1

    def test_keeps_different_articles(self):
        articles = [
            RawArticle(title="Apple launches new iPhone", url="https://a.com",
                       source="A", published=datetime.now(timezone.utc),
                       description="Apple announced a new product."),
            RawArticle(title="Google releases Pixel update", url="https://b.com",
                       source="B", published=datetime.now(timezone.utc),
                       description="Google pushed a software update."),
        ]
        df = articles_to_dataframe(articles)
        cleaned = clean_articles(df, lookback_days=30)
        assert len(cleaned) == 2

    def test_filters_old_articles(self):
        old = datetime.now(timezone.utc) - timedelta(days=30)
        recent = datetime.now(timezone.utc) - timedelta(hours=1)
        articles = [
            RawArticle(title="Old news", url="https://a.com", source="A",
                       published=old, description="Old."),
            RawArticle(title="Fresh news", url="https://b.com", source="B",
                       published=recent, description="Fresh."),
        ]
        df = articles_to_dataframe(articles)
        cleaned = clean_articles(df, lookback_days=7)
        assert len(cleaned) == 1
        assert cleaned.iloc[0]["title"] == "Fresh news"

    def test_sorts_by_date_descending(self):
        articles = _make_articles(5)
        df = articles_to_dataframe(articles)
        cleaned = clean_articles(df, lookback_days=30)
        dates = cleaned["published"].dropna().tolist()
        assert dates == sorted(dates, reverse=True)

    def test_empty_df_returns_empty(self):
        df = _empty_df()
        cleaned = clean_articles(df)
        assert cleaned.empty
