"""
AI News Intelligence Dashboard — Core Package

A modular news intelligence engine that fetches, analyzes, clusters,
and summarizes news from multiple sources into actionable insights.

Modules:
    config      — Environment and application configuration
    constants   — Topic taxonomies, keyword maps, source definitions
    fetcher     — RSS/API news ingestion
    cleaner     — Deduplication, normalization, text cleaning
    classifier  — Topic classification via keyword matching + TF-IDF
    sentiment   — VADER-based sentiment scoring
    geo         — Country/region signal extraction
    trends      — Trend detection, keyword frequency, temporal patterns
    summarizer  — Extractive local summaries + optional LLM enhancement
    pipeline    — End-to-end orchestration of the analysis pipeline
    utils       — Shared helper functions
"""

__version__ = "1.0.0"
__author__ = "AI News Intelligence Dashboard"
