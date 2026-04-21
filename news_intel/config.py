"""
Application configuration — loads from .env and provides typed defaults.

All external API keys are optional. The dashboard runs fully without them.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load .env from project root
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_PATH = _PROJECT_ROOT / ".env"
load_dotenv(_ENV_PATH)


class Config:
    """Centralised, immutable-ish configuration object."""

    # --- Paths ---------------------------------------------------------------
    PROJECT_ROOT: Path = _PROJECT_ROOT
    DATA_DIR: Path = _PROJECT_ROOT / "data"
    CACHE_DIR: Path = _PROJECT_ROOT / ".cache"

    # --- OpenAI (optional) ---------------------------------------------------
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # --- Anthropic (optional) ------------------------------------------------
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    # --- NewsAPI.org (optional, free tier = 100 req/day) ----------------------
    NEWSAPI_KEY: str = os.getenv("NEWSAPI_KEY", "")

    # --- Application settings ------------------------------------------------
    MAX_ARTICLES: int = int(os.getenv("MAX_ARTICLES", "200"))
    FETCH_TIMEOUT: int = int(os.getenv("FETCH_TIMEOUT", "15"))
    CACHE_TTL_MINUTES: int = int(os.getenv("CACHE_TTL_MINUTES", "30"))
    DEFAULT_LOOKBACK_DAYS: int = int(os.getenv("DEFAULT_LOOKBACK_DAYS", "7"))

    # --- LLM behaviour -------------------------------------------------------
    USE_LLM: bool = os.getenv("USE_LLM", "auto").lower()  # "auto" | "true" | "false"

    @classmethod
    def llm_available(cls) -> bool:
        """Return True when at least one LLM key is configured."""
        return bool(cls.OPENAI_API_KEY or cls.ANTHROPIC_API_KEY)

    @classmethod
    def should_use_llm(cls) -> bool:
        """Decide whether to use LLM based on config and key availability."""
        if cls.USE_LLM == "false":
            return False
        if cls.USE_LLM == "true":
            return cls.llm_available()
        # "auto" — use LLM only when a key is present
        return cls.llm_available()

    @classmethod
    def ensure_dirs(cls) -> None:
        """Create data / cache directories if they don't exist."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)


# Run once on import
Config.ensure_dirs()
