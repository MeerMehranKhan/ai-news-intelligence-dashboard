<![CDATA[# 🌐 AI News Intelligence Dashboard

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

### What each file does

| File | Purpose |
|---|---|
| `config.py` | Loads `.env`, defines typed settings, manages API key detection |
| `constants.py` | Topic taxonomy (13 topics), 200+ keywords, 25+ RSS sources, 28 countries |
| `fetcher.py` | Concurrently fetches RSS feeds via ThreadPoolExecutor + optional NewsAPI |
| `cleaner.py` | MD5-based content fingerprinting for dedup, date windowing, normalisation |
| `classifier.py` | Keyword-match → TF-IDF centroid fallback classifier + query relevance scoring |
| `sentiment.py` | VADER SentimentIntensityAnalyzer with lazy lexicon download |
| `geo.py` | Keyword-based country detection with region mapping (28 nations, 10 regions) |
| `trends.py` | TF-IDF keyword extraction, growth-ratio detection, hourly volume analysis |
| `summarizer.py` | TF-IDF centrality extractive summarisation + optional OpenAI/Anthropic calls |
| `pipeline.py` | Orchestrates the 7-step pipeline, returns `DashboardResult` to UI |

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

### Behaviour with and without API keys

| Configuration | Behaviour |
|---|---|
| **No keys** | Fully functional. Summaries use TF-IDF extractive method. All charts, sentiment, trends, and geo work normally. |
| **OpenAI key only** | Summaries are generated by GPT. Everything else stays the same. |
| **Anthropic key only** | Summaries are generated by Claude. Everything else stays the same. |
| **NewsAPI key** | Additional articles from NewsAPI supplement RSS feeds. |
| **All keys** | Maximum coverage and AI-enhanced summaries. OpenAI is tried first. |

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

## 📊 Analysis Dimensions

### 1. Topic Classification (13 categories)
- AI / ML, Crypto / Blockchain, Markets / Stocks, Geopolitics, Economy / Macro
- Energy, Politics / Elections, Defense / Military, Healthcare, Technology
- Company News, Climate / Environment, Other

**Method:** Keyword matching (200+ curated terms) with TF-IDF cosine-similarity fallback for unmatched articles.

### 2. Sentiment Analysis
- Per-article compound score (−1 to +1)
- Aggregate sentiment per topic cluster
- Three-label classification: positive / neutral / negative

**Method:** VADER — specifically designed for news/social text, no training needed.

### 3. Trend Detection
- Rising topics (growth-ratio vs. recent 12h window)
- Top TF-IDF keywords across the corpus
- Hourly publication volume timeline
- Source concentration analysis

### 4. Geographic Signals
- 28 countries, 10 regions
- Keyword-based extraction (fast, explainable)
- Country distribution charts and region pie

### 5. Narrative Summaries
- Per-topic cluster summaries
- Overall dashboard executive briefing
- Local: TF-IDF centrality-based extractive method
- Optional: LLM-generated editorial-style narratives

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

## 💡 Design Choices

| Decision | Rationale |
|---|---|
| **Keyword-first classification** | Fast, explainable, no GPU needed. TF-IDF fallback handles edge cases. |
| **VADER over transformer models** | Works on headlines without fine-tuning. No GPU. No 500MB model download. |
| **Concurrent RSS fetching** | ThreadPoolExecutor makes 25+ feed fetches take ~3s instead of ~30s. |
| **Content fingerprinting for dedup** | MD5 of normalised text catches near-identical articles from different sources. |
| **Optional LLM layer** | Core app must work without paid services. LLM is an enhancement, not a dependency. |
| **Streamlit** | Fastest path to a polished dashboard for a solo Python project. No frontend build step. |
| **No database** | Keeps setup friction minimal. DataFrame-in-memory is fine for real-time analysis. |

---

## 📝 Resume Bullet

> **AI News Intelligence Dashboard** — Built a real-time news intelligence platform that ingests 25+ RSS feeds, classifies articles into 13 topic categories using keyword matching and TF-IDF cosine similarity, performs VADER sentiment analysis, detects geographic signals across 28 countries, identifies rising trends via temporal frequency analysis, and generates narrative summaries — all rendered in a polished Streamlit dashboard with optional LLM enhancement. Python · scikit-learn · NLTK · Plotly · Streamlit.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
]]>
