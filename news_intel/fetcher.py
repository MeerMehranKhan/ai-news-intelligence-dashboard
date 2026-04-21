"""
News fetcher — pulls articles from RSS feeds (and optionally NewsAPI).

Returns a list of raw article dicts that the cleaner will normalise.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional

import feedparser
import requests

from news_intel.config import Config
from news_intel.constants import RSS_FEEDS, RSSSource
from news_intel.utils import clean_html, safe_parse_date, now_utc

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Article data container
# ---------------------------------------------------------------------------
@dataclass
class RawArticle:
    """Flat representation of one news article before enrichment."""
    title: str
    url: str
    source: str
    published: Optional[datetime] = None
    description: str = ""
    category_hint: str = ""
    region_hint: str = ""

    def to_dict(self) -> Dict:
        d = asdict(self)
        if d["published"]:
            d["published"] = d["published"].isoformat()
        return d


# ---------------------------------------------------------------------------
# RSS fetching
# ---------------------------------------------------------------------------
def _fetch_rss(source: RSSSource, timeout: int) -> List[RawArticle]:
    """Parse a single RSS feed and return RawArticle objects."""
    articles: List[RawArticle] = []
    try:
        resp = requests.get(source.url, timeout=timeout, headers={
            "User-Agent": "NewsIntelDashboard/1.0"
        })
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)

        for entry in feed.entries:
            title = clean_html(getattr(entry, "title", ""))
            if not title:
                continue

            link = getattr(entry, "link", "")
            desc = clean_html(
                getattr(entry, "summary", "")
                or getattr(entry, "description", "")
            )
            pub_date = safe_parse_date(
                getattr(entry, "published", None)
                or getattr(entry, "updated", None)
            )

            articles.append(RawArticle(
                title=title,
                url=link,
                source=source.name,
                published=pub_date,
                description=desc[:1000] if desc else "",
                category_hint=source.category,
                region_hint=source.region,
            ))
    except Exception as exc:
        logger.warning("Failed to fetch %s: %s", source.name, exc)

    return articles


def fetch_rss_feeds(
    feeds: Optional[List[RSSSource]] = None,
    max_workers: int = 8,
) -> List[RawArticle]:
    """
    Concurrently fetch all configured RSS feeds.

    Args:
        feeds: Override list of feeds. Defaults to all RSS_FEEDS.
        max_workers: Thread pool size for concurrent fetching.

    Returns:
        Flat list of RawArticle objects (unsorted, undeduped).
    """
    feeds = feeds or RSS_FEEDS
    timeout = Config.FETCH_TIMEOUT
    all_articles: List[RawArticle] = []

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_fetch_rss, src, timeout): src for src in feeds}
        for future in as_completed(futures):
            src = futures[future]
            try:
                result = future.result()
                logger.info("Fetched %d articles from %s", len(result), src.name)
                all_articles.extend(result)
            except Exception as exc:
                logger.warning("Error processing %s: %s", src.name, exc)

    logger.info("Total raw articles fetched: %d", len(all_articles))
    return all_articles


# ---------------------------------------------------------------------------
# Optional: NewsAPI.org
# ---------------------------------------------------------------------------
def fetch_newsapi(query: str = "", page_size: int = 50) -> List[RawArticle]:
    """
    Fetch headlines from NewsAPI.org.  Requires NEWSAPI_KEY in .env.

    Returns empty list if no key is configured.
    """
    key = Config.NEWSAPI_KEY
    if not key:
        return []

    articles: List[RawArticle] = []
    params = {
        "apiKey": key,
        "pageSize": min(page_size, 100),
        "language": "en",
    }
    if query:
        url = "https://newsapi.org/v2/everything"
        params["q"] = query
        params["sortBy"] = "publishedAt"
    else:
        url = "https://newsapi.org/v2/top-headlines"
        params["country"] = "us"

    try:
        resp = requests.get(url, params=params, timeout=Config.FETCH_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("articles", []):
            title = item.get("title", "")
            if not title or title == "[Removed]":
                continue
            pub = safe_parse_date(item.get("publishedAt"))
            articles.append(RawArticle(
                title=clean_html(title),
                url=item.get("url", ""),
                source=item.get("source", {}).get("name", "NewsAPI"),
                published=pub,
                description=clean_html(item.get("description", "") or ""),
                category_hint="newsapi",
                region_hint="",
            ))
    except Exception as exc:
        logger.warning("NewsAPI fetch failed: %s", exc)

    return articles


# ---------------------------------------------------------------------------
# Unified fetch
# ---------------------------------------------------------------------------
def fetch_all(query: str = "") -> List[RawArticle]:
    """
    Fetch from all configured sources.

    Combines RSS feeds + optional NewsAPI.
    """
    articles = fetch_rss_feeds()
    articles.extend(fetch_newsapi(query))
    return articles[:Config.MAX_ARTICLES]
