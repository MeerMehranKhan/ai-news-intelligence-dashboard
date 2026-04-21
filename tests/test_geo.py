"""Tests for news_intel.geo — country/region extraction."""

import pytest
import pandas as pd

from news_intel.geo import extract_geo


def _make_df(titles_and_descs):
    return pd.DataFrame(
        [{"title": t, "description": d} for t, d in titles_and_descs]
    )


class TestGeoExtraction:
    def test_detects_us(self):
        df = _make_df([("White House announces new policy", "Washington reacts.")])
        result = extract_geo(df)
        assert "United States" in result.iloc[0]["countries"]

    def test_detects_china(self):
        df = _make_df([("Beijing issues trade warning", "Chinese exports fall.")])
        result = extract_geo(df)
        assert "China" in result.iloc[0]["countries"]

    def test_detects_multiple_countries(self):
        df = _make_df([("Russia and Ukraine hold peace talks", "Moscow and Kyiv negotiate.")])
        result = extract_geo(df)
        countries = result.iloc[0]["countries"]
        assert "Russia" in countries
        assert "Ukraine" in countries

    def test_no_country_detected(self):
        df = _make_df([("New recipe for chocolate cake", "A delicious dessert idea.")])
        result = extract_geo(df)
        assert result.iloc[0]["primary_country"] == ""

    def test_region_assigned(self):
        df = _make_df([("Tokyo hosts global summit", "Japanese leaders gather.")])
        result = extract_geo(df)
        assert result.iloc[0]["primary_region"] == "Asia-Pacific"

    def test_empty_df(self):
        df = pd.DataFrame(columns=["title", "description"])
        result = extract_geo(df)
        assert result.empty
