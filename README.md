# 🌐 AI News Intelligence Dashboard

> Real-time multi-source news analysis with topic clustering, sentiment scoring, geographic mapping, and trend detection — powered by Python, scikit-learn, and Streamlit.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-F7931E?logo=scikit-learn&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📸 Screenshots

<!-- Replace these with actual screenshots after running the app -->
> *Run the app and take screenshots to replace these placeholders.*

| Dashboard Overview | Topic Analysis | Trend Detection |
|---|---|---|
| *Screenshot 1* | *Screenshot 2* | *Screenshot 3* |

---

## 🎯 What This Is

An **end-to-end news intelligence platform** that:

1. **Pulls** articles from 25+ RSS feeds (Reuters, BBC, NYT, TechCrunch, Al Jazeera, etc.)
2. **Cleans** and deduplicates them using content fingerprinting
3. **Classifies** topics using keyword matching + TF-IDF cosine similarity
4. **Scores** sentiment with VADER (no API needed)
5. **Extracts** geographic signals from a curated 28-country dictionary
6. **Detects** trends via TF-IDF keyword extraction + temporal frequency analysis
7. **Summarises** narratives using extractive summarisation (with optional LLM enhancement)
8. **Renders** everything in a polished Streamlit dashboard with light/dark theme toggle

It works **100% locally** with zero paid APIs. Optional OpenAI/Anthropic integration enhances narrative summaries when configured.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Topic Search** | Search by sector (AI, crypto, geopolitics, etc.) with TF-IDF relevance ranking |
| 📊 **Topic Clustering** | 13 topic categories with keyword-first + ML fallback classification |
| 💹 **Sentiment Analysis** | Per-article and per-topic VADER sentiment scoring with visual breakdown |
| 🌍 **Geographic Mapping** | Country and region detection across 28 nations |
| 📈 **Trend Detection** | Rising topics, keyword spikes, temporal volume patterns |
| 📋 **Narrative Summaries** | Extractive summaries per topic cluster + overall dashboard briefing |
| 📌 **Watchlist** | Save and track topics of interest |
| 🔍 **Explainability** | Full methodology disclosure — no black-box "AI magic" |
| 🤖 **Optional LLM Layer** | OpenAI / Anthropic integration for editorial-quality summaries |
| 🌗 **Light / Dark Mode** | Theme toggle with full UI, chart, and sidebar adaptation |
| 📰 **25+ Sources** | Reuters, BBC, NYT, CNBC, TechCrunch, Guardian, Al Jazeera, and more |

---

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  RSS Feeds   │────▶│   Fetcher    │────▶│   Cleaner    │
│  (25+ feeds) │     │ (concurrent) │     │ (dedup/norm) │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                 │
                     ┌──────────────┐     ┌──────▼───────┐
                     │   Optional   │     │  Classifier  │
                     │   NewsAPI    │────▶│ (keyword+ML) │
                     └──────────────┘     └──────┬───────┘
                                                 │
              ┌──────────────┐            ┌──────▼───────┐
              │  Sentiment   │◀───────────│   Enriched   │
              │   (VADER)    │            │  DataFrame   │
              └──────┬───────┘            └──────┬───────┘
                     │                           │
              ┌──────▼───────┐            ┌──────▼───────┐
              │     Geo      │            │    Trends    │
              │ (28 nations) │            │  (TF-IDF)    │
              └──────┬───────┘            └──────┬───────┘
                     │                           │
                     └─────────┬─────────────────┘
                               │
                        ┌──────▼───────┐
                        │  Summariser  │
                        │ (local/LLM)  │
                        └──────┬───────┘
                               │
                        ┌──────▼───────┐
                        │  Streamlit   │
                        │  Dashboard   │
                        └──────────────┘
```

---

## 📁 Project Structure

```
ai-news-intelligence-dashboard/
├── streamlit_app.py          # Main UI — Streamlit dashboard
├── requirements.txt          # Python dependencies
├── pyproject.toml            # Pytest configuration
├── .env.example              # Environment variable template
├── .gitignore                # Git ignore rules
├── README.md                 # This file
│
├── news_intel/               # Core Python package
│   ├── __init__.py           # Package metadata
│   ├── config.py             # Environment + app configuration
│   ├── constants.py          # Topic taxonomy, keyword maps, RSS sources, geo data
│   ├── fetcher.py            # Multi-source news ingestion (RSS + optional API)
│   ├── cleaner.py            # Deduplication, normalisation, date filtering
│   ├── classifier.py         # Topic classification (keyword + TF-IDF fallback)
│   ├── sentiment.py          # VADER sentiment analysis
│   ├── geo.py                # Country/region extraction
│   ├── trends.py             # Trend detection, keyword extraction, temporal analysis
│   ├── summarizer.py         # Narrative summaries (local + optional LLM)
│   ├── pipeline.py           # End-to-end orchestration
│   └── utils.py              # Shared helpers
│
├── tests/                    # Test suite
│   ├── test_cleaner.py       # Cleaning + dedup tests
│   ├── test_classifier.py    # Topic classification tests
│   ├── test_sentiment.py     # Sentiment scoring tests
│   ├── test_summarizer.py    # Summarisation + fallback tests
│   └── test_geo.py           # Geo extraction tests
│
└── data/
    └── sample_articles.json  # Sample data for offline demo
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or newer
- pip

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/ai-news-intelligence-dashboard.git
cd ai-news-intelligence-dashboard

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Configure environment variables
copy .env.example .env
# Edit .env if you want LLM summaries or NewsAPI — but it works without any keys

# 5. Run the dashboard
streamlit run streamlit_app.py
```

The dashboard will open at `http://localhost:8501`.

---

## ⚙️ Environment Variables

All variables are **optional**. The app runs fully without any API keys.

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | *(empty)* | OpenAI key for AI-enhanced narrative summaries |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `ANTHROPIC_API_KEY` | *(empty)* | Anthropic key (alternative to OpenAI) |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-20250514` | Anthropic model to use |
| `NEWSAPI_KEY` | *(empty)* | NewsAPI.org key for additional article coverage |
| `MAX_ARTICLES` | `200` | Maximum articles to process per pipeline run |
| `FETCH_TIMEOUT` | `15` | HTTP timeout in seconds for RSS fetching |
| `CACHE_TTL_MINUTES` | `30` | How long to cache results in the UI |
| `DEFAULT_LOOKBACK_DAYS` | `7` | Default lookback window |
| `USE_LLM` | `auto` | `auto` / `true` / `false` — controls LLM usage |

---

## 📰 Data Sources

The app pulls from **25+ RSS feeds** across these categories:

| Category | Sources |
|---|---|
| **Wire Services** | Reuters (World, Business, Tech), Associated Press |
| **Broadsheets** | NYT (World, Business, Tech), The Guardian (World, Business) |
| **Broadcast** | BBC (World, Business, Tech), NPR, DW |
| **Finance** | CNBC, Yahoo Finance, MarketWatch |
| **Tech** | TechCrunch, Ars Technica, The Verge, Wired, Hacker News |
| **International** | Al Jazeera, The Guardian, Deutsche Welle |
| **Science/Health** | Nature, WHO |

All RSS feeds are **free and publicly available**. No API key is required for core functionality.

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=news_intel --cov-report=term-missing

# Run a specific test file
pytest tests/test_classifier.py -v
```

**Test coverage includes:**
- Article cleaning and deduplication
- Topic classification (keyword + fallback)
- Sentiment scoring (positive, negative, neutral, edge cases)
- Summarisation (local + LLM fallback behaviour)
- Geographic extraction (single, multi, none)

---

## 🔧 Extending the Project

### Add a new RSS source
Edit `constants.py` → `RSS_FEEDS` list:
```python
RSSSource("My Source", "https://example.com/rss.xml", "tech", "us"),
```

### Add a new topic
1. Add to `TOPICS` list in `constants.py`
2. Add keyword entry to `TOPIC_KEYWORDS` dict
3. Done — classifier picks it up automatically

### Add a new country for geo detection
Add to `COUNTRY_KEYWORDS` and `REGION_MAP` in `constants.py`.

### Swap the LLM provider
Implement a new `_call_*` function in `summarizer.py` and add it to the fallback chain in `summarise_with_llm`.

### Add persistent storage
Replace the in-memory DataFrame with SQLite or PostgreSQL. The `DashboardResult` dataclass makes this straightforward — serialize `articles` to a table.

---

## 🚧 Limitations

- **Headline-level analysis only** — full article text requires scraping, which is not included
- **Geo extraction is keyword-based** — NER would be more accurate but adds a spaCy model dependency
- **No historical persistence** — each run starts fresh (could add SQLite caching)
- **RSS availability** — some feeds may change URLs or become unavailable
- **Rate limits** — NewsAPI free tier is 100 requests/day

---

## 🔮 Future Improvements

- [ ] **Persistent storage** — SQLite/PostgreSQL for historical trend tracking
- [ ] **Full-text analysis** — Scrape and analyse complete articles
- [ ] **Named Entity Recognition** — spaCy NER for more accurate geo/entity extraction
- [ ] **Email digest** — Scheduled daily briefing email
- [ ] **Custom RSS feeds** — Let users add their own feeds via the UI
- [ ] **Embeddings-based clustering** — Replace TF-IDF with sentence-transformers for better topic grouping
- [ ] **MCP server integration** — Expose the analysis pipeline as an MCP tool server for AI assistants
- [ ] **Deployment** — Dockerfile + Streamlit Cloud deployment guide

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
