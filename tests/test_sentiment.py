"""Tests for news_intel.sentiment — VADER scoring."""

import pytest
from news_intel.sentiment import score_text, score_articles
import pandas as pd


class TestScoreText:
    def test_positive_text(self):
        score, label = score_text("This is amazing, wonderful, and fantastic news!")
        assert score > 0
        assert label == "positive"

    def test_negative_text(self):
        score, label = score_text("This is terrible, horrible, and devastating.")
        assert score < 0
        assert label == "negative"

    def test_neutral_text(self):
        score, label = score_text("The meeting is scheduled for Tuesday.")
        assert label == "neutral"

    def test_empty_text(self):
        score, label = score_text("")
        assert score == 0.0
        assert label == "neutral"

    def test_score_in_range(self):
        score, _ = score_text("Moderately good news about the economy.")
        assert -1 <= score <= 1


class TestScoreArticles:
    def test_adds_sentiment_columns(self):
        df = pd.DataFrame({
            "title": ["Great news for markets", "Terrible crash ahead"],
            "description": ["Stocks surge today", "Economy in freefall"],
        })
        result = score_articles(df)
        assert "sentiment_score" in result.columns
        assert "sentiment_label" in result.columns
        assert len(result) == 2

    def test_empty_df(self):
        df = pd.DataFrame(columns=["title", "description"])
        result = score_articles(df)
        assert result.empty
        assert "sentiment_score" in result.columns
