"""
Static constants — topic taxonomy, keyword maps, and RSS source registry.

These are the canonical definitions used throughout the pipeline.
Changing them here automatically propagates everywhere.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


# ---------------------------------------------------------------------------
# Topic taxonomy
# ---------------------------------------------------------------------------
TOPICS: List[str] = [
    "AI / ML",
    "Crypto / Blockchain",
    "Markets / Stocks",
    "Geopolitics",
    "Economy / Macro",
    "Energy",
    "Politics / Elections",
    "Defense / Military",
    "Healthcare",
    "Technology",
    "Company News",
    "Climate / Environment",
    "Other",
]

# Keyword → topic mapping.  Lowercase. Order matters: first match wins.
TOPIC_KEYWORDS: Dict[str, List[str]] = {
    "AI / ML": [
        "artificial intelligence", "machine learning", "deep learning", "neural network",
        "chatgpt", "openai", "anthropic", "gemini", "llm", "large language model",
        "generative ai", "gpt", "transformer", "computer vision", "nlp",
        "natural language", "ai model", "ai chip", "nvidia ai", "ai regulation",
        "ai safety", "ai agent", "copilot", "midjourney", "stable diffusion",
        "reinforcement learning", "autonomous", "robotics",
    ],
    "Crypto / Blockchain": [
        "bitcoin", "ethereum", "crypto", "blockchain", "defi", "nft",
        "stablecoin", "binance", "coinbase", "solana", "token", "web3",
        "mining", "halving", "decentralized", "cryptocurrency",
    ],
    "Markets / Stocks": [
        "stock market", "s&p 500", "nasdaq", "dow jones", "wall street",
        "earnings", "ipo", "share price", "market rally", "bear market",
        "bull market", "fed rate", "interest rate", "treasury", "bond yield",
        "stock", "equities", "trading", "hedge fund", "mutual fund", "etf",
        "nasdaq", "nyse", "market cap",
    ],
    "Geopolitics": [
        "geopolitics", "sanctions", "trade war", "diplomacy", "nato",
        "united nations", "g7", "g20", "territorial", "sovereignty",
        "coup", "embargo", "peace talks", "ceasefire", "conflict",
        "bilateral", "alliance", "geopolitical", "foreign policy",
    ],
    "Economy / Macro": [
        "economy", "gdp", "inflation", "recession", "unemployment",
        "economic growth", "central bank", "monetary policy", "fiscal",
        "trade deficit", "supply chain", "consumer spending", "cpi",
        "ppi", "jobs report", "labor market", "wage", "tariff",
    ],
    "Energy": [
        "oil price", "opec", "natural gas", "renewable energy", "solar",
        "wind energy", "nuclear energy", "petroleum", "crude oil",
        "energy transition", "ev battery", "lithium", "hydrogen",
        "fossil fuel", "carbon capture", "lng", "pipeline", "refinery",
    ],
    "Politics / Elections": [
        "election", "presidential", "congress", "senate", "parliament",
        "voting", "ballot", "campaign", "democrat", "republican",
        "political party", "governor", "legislation", "bill passed",
        "executive order", "midterm", "primary", "caucus", "poll",
    ],
    "Defense / Military": [
        "military", "defense", "pentagon", "missile", "drone strike",
        "warfare", "troops", "navy", "army", "air force", "weapons",
        "nuclear weapon", "arms deal", "defense budget", "veteran",
        "intelligence agency", "cyber attack", "espionage",
    ],
    "Healthcare": [
        "healthcare", "vaccine", "fda", "drug approval", "clinical trial",
        "pandemic", "disease", "hospital", "medical", "pharma",
        "biotech", "gene therapy", "mental health", "insurance",
        "public health", "who", "health policy", "medicare", "medicaid",
    ],
    "Technology": [
        "tech", "software", "hardware", "cloud computing", "cybersecurity",
        "data breach", "semiconductor", "chip", "5g", "quantum computing",
        "apple", "google", "microsoft", "amazon", "meta", "startup",
        "saas", "open source", "api", "platform",
    ],
    "Company News": [
        "ceo", "acquisition", "merger", "layoff", "restructuring",
        "quarterly results", "revenue", "profit", "loss", "funding round",
        "series a", "series b", "valuation", "board of directors",
        "corporate", "executive", "partnership", "bankruptcy",
    ],
    "Climate / Environment": [
        "climate change", "global warming", "carbon emission", "greenhouse",
        "deforestation", "wildfire", "flood", "drought", "sea level",
        "biodiversity", "conservation", "epa", "paris agreement",
        "sustainability", "net zero", "pollution", "ecological",
    ],
}


# ---------------------------------------------------------------------------
# RSS feed registry
# ---------------------------------------------------------------------------
@dataclass
class RSSSource:
    """One RSS feed endpoint."""
    name: str
    url: str
    category: str = "general"
    region: str = "global"


RSS_FEEDS: List[RSSSource] = [
    # --- Major wire services / broadsheets ---
    RSSSource("Reuters — World",         "https://feeds.reuters.com/reuters/worldNews",        "general",   "global"),
    RSSSource("Reuters — Business",      "https://feeds.reuters.com/reuters/businessNews",     "business",  "global"),
    RSSSource("Reuters — Technology",    "https://feeds.reuters.com/reuters/technologyNews",   "tech",      "global"),
    RSSSource("AP News — Top",           "https://rsshub.app/apnews/topics/apf-topnews",      "general",   "global"),
    RSSSource("BBC — World",             "http://feeds.bbci.co.uk/news/world/rss.xml",         "general",   "global"),
    RSSSource("BBC — Business",          "http://feeds.bbci.co.uk/news/business/rss.xml",      "business",  "global"),
    RSSSource("BBC — Technology",        "http://feeds.bbci.co.uk/news/technology/rss.xml",    "tech",      "global"),

    # --- US-centric ---
    RSSSource("NPR — News",             "https://feeds.npr.org/1001/rss.xml",                 "general",   "us"),
    RSSSource("CNBC — Top",             "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114", "business", "us"),
    RSSSource("NYT — World",            "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "general", "global"),
    RSSSource("NYT — Business",         "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml", "business", "us"),
    RSSSource("NYT — Technology",       "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml", "tech", "us"),

    # --- Tech-focused ---
    RSSSource("TechCrunch",             "https://techcrunch.com/feed/",                       "tech",      "global"),
    RSSSource("Ars Technica",           "https://feeds.arstechnica.com/arstechnica/index",    "tech",      "global"),
    RSSSource("The Verge",              "https://www.theverge.com/rss/index.xml",             "tech",      "global"),
    RSSSource("Wired",                  "https://www.wired.com/feed/rss",                     "tech",      "global"),
    RSSSource("Hacker News — Best",     "https://hnrss.org/best",                             "tech",      "global"),

    # --- International ---
    RSSSource("Al Jazeera — News",      "https://www.aljazeera.com/xml/rss/all.xml",          "general",   "middle_east"),
    RSSSource("The Guardian — World",   "https://www.theguardian.com/world/rss",              "general",   "europe"),
    RSSSource("The Guardian — Business","https://www.theguardian.com/uk/business/rss",        "business",  "europe"),
    RSSSource("DW — Top",              "https://rss.dw.com/rdf/rss-en-top",                  "general",   "europe"),

    # --- Finance ---
    RSSSource("Yahoo Finance",          "https://finance.yahoo.com/news/rssindex",            "business",  "us"),
    RSSSource("MarketWatch",            "https://feeds.marketwatch.com/marketwatch/topstories","business",  "us"),

    # --- Science / Health ---
    RSSSource("Nature — News",          "https://www.nature.com/nature.rss",                  "science",   "global"),
    RSSSource("WHO — News",             "https://www.who.int/rss-feeds/news-english.xml",     "healthcare","global"),
]


# ---------------------------------------------------------------------------
# Country / region keyword lists (for geo extraction)
# ---------------------------------------------------------------------------
COUNTRY_KEYWORDS: Dict[str, List[str]] = {
    "United States": ["united states", "u.s.", "usa", "washington", "pentagon", "white house", "congress", "new york", "california", "texas", "florida"],
    "China": ["china", "beijing", "shanghai", "chinese", "xi jinping", "ccp"],
    "Russia": ["russia", "moscow", "kremlin", "putin", "russian"],
    "United Kingdom": ["united kingdom", "u.k.", "uk", "london", "britain", "british", "england"],
    "European Union": ["european union", "eu", "brussels", "eurozone"],
    "India": ["india", "new delhi", "modi", "mumbai", "indian"],
    "Japan": ["japan", "tokyo", "japanese"],
    "Germany": ["germany", "berlin", "german", "bundestag"],
    "France": ["france", "paris", "french", "macron", "élysée"],
    "Ukraine": ["ukraine", "kyiv", "ukrainian", "zelensky"],
    "Israel": ["israel", "tel aviv", "israeli", "netanyahu", "jerusalem"],
    "Palestine": ["palestine", "palestinian", "gaza", "west bank", "hamas"],
    "Iran": ["iran", "tehran", "iranian"],
    "Saudi Arabia": ["saudi arabia", "riyadh", "saudi"],
    "South Korea": ["south korea", "seoul", "korean"],
    "North Korea": ["north korea", "pyongyang", "kim jong"],
    "Taiwan": ["taiwan", "taipei", "taiwanese"],
    "Brazil": ["brazil", "brasilia", "brazilian"],
    "Turkey": ["turkey", "ankara", "erdogan", "turkish", "istanbul"],
    "Australia": ["australia", "canberra", "australian", "sydney", "melbourne"],
    "Canada": ["canada", "ottawa", "canadian", "trudeau", "toronto"],
    "Mexico": ["mexico", "mexican", "mexico city"],
    "Nigeria": ["nigeria", "nigerian", "lagos", "abuja"],
    "South Africa": ["south africa", "johannesburg", "pretoria", "cape town"],
    "Egypt": ["egypt", "cairo", "egyptian"],
    "Pakistan": ["pakistan", "islamabad", "pakistani"],
    "Indonesia": ["indonesia", "jakarta", "indonesian"],
}

REGION_MAP: Dict[str, str] = {
    "United States": "North America",
    "Canada": "North America",
    "Mexico": "Latin America",
    "Brazil": "Latin America",
    "China": "Asia-Pacific",
    "Japan": "Asia-Pacific",
    "South Korea": "Asia-Pacific",
    "North Korea": "Asia-Pacific",
    "Taiwan": "Asia-Pacific",
    "India": "South Asia",
    "Pakistan": "South Asia",
    "Indonesia": "Asia-Pacific",
    "Australia": "Asia-Pacific",
    "Russia": "Europe / Central Asia",
    "United Kingdom": "Europe",
    "European Union": "Europe",
    "Germany": "Europe",
    "France": "Europe",
    "Turkey": "Middle East / Europe",
    "Ukraine": "Europe",
    "Israel": "Middle East",
    "Palestine": "Middle East",
    "Iran": "Middle East",
    "Saudi Arabia": "Middle East",
    "Egypt": "Africa / Middle East",
    "Nigeria": "Africa",
    "South Africa": "Africa",
}
