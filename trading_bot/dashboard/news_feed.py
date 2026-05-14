"""
News feed aggregator.
Priority:
  1. Alpha Vantage NEWS_SENTIMENT (set ALPHA_VANTAGE_KEY in .env)
  2. Yahoo Finance RSS (no key needed, always available)
"""

import logging
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Optional

import requests

log = logging.getLogger(__name__)

ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")
_NEWS_CACHE: list[dict] = []
_CACHE_TS: float = 0.0
CACHE_TTL = 300  # 5 minutes


def _parse_av(data: dict) -> list[dict]:
    items = []
    for article in (data.get("feed") or [])[:15]:
        ts_raw = article.get("time_published", "")
        try:
            ts = datetime.strptime(ts_raw, "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
            time_str = ts.strftime("%I:%M %p")
        except Exception:
            time_str = "—"

        score = float(article.get("overall_sentiment_score", 0))
        if score > 0.15:
            impact = "high"
        elif score > 0.05:
            impact = "med"
        else:
            impact = "low"

        items.append({
            "time":    time_str,
            "title":   article.get("title", "")[:90],
            "source":  article.get("source", ""),
            "impact":  impact,
            "url":     article.get("url", ""),
            "score":   round(score, 3),
        })
    return items


def _parse_rss(xml_text: str) -> list[dict]:
    items = []
    try:
        root = ET.fromstring(xml_text)
        channel = root.find("channel")
        if channel is None:
            return items
        for item in (channel.findall("item") or [])[:12]:
            title   = (item.findtext("title") or "").strip()[:90]
            pub_raw = item.findtext("pubDate") or ""
            try:
                from email.utils import parsedate_to_datetime
                ts = parsedate_to_datetime(pub_raw)
                time_str = ts.astimezone(timezone.utc).strftime("%I:%M %p")
            except Exception:
                time_str = "—"

            keywords_high = ["fed", "fomc", "cpi", "gdp", "nfp", "rate", "inflation", "powell"]
            keywords_med  = ["earnings", "nasdaq", "futures", "treasury", "jobs", "retail"]
            tl = title.lower()
            if any(k in tl for k in keywords_high):
                impact = "high"
            elif any(k in tl for k in keywords_med):
                impact = "med"
            else:
                impact = "low"

            items.append({
                "time":   time_str,
                "title":  title,
                "source": "Yahoo Finance",
                "impact": impact,
                "url":    item.findtext("link") or "",
                "score":  None,
            })
    except Exception as exc:
        log.warning("RSS parse error: %s", exc)
    return items


def fetch_news(force: bool = False) -> list[dict]:
    """Return cached news, refreshing if stale."""
    import time
    global _NEWS_CACHE, _CACHE_TS

    if not force and (time.time() - _CACHE_TS < CACHE_TTL) and _NEWS_CACHE:
        return _NEWS_CACHE

    news: list[dict] = []

    # --- Alpha Vantage ---
    if ALPHA_VANTAGE_KEY:
        try:
            url = (
                "https://www.alphavantage.co/query"
                f"?function=NEWS_SENTIMENT&tickers=QQQ,NQ&sort=LATEST"
                f"&limit=20&apikey={ALPHA_VANTAGE_KEY}"
            )
            resp = requests.get(url, timeout=10)
            if resp.ok:
                news = _parse_av(resp.json())
                log.info("Alpha Vantage: %d news items", len(news))
        except Exception as exc:
            log.warning("Alpha Vantage news error: %s", exc)

    # --- Yahoo Finance RSS fallback ---
    if not news:
        try:
            rss_url = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=NQ=F,QQQ&region=US&lang=en-US"
            resp = requests.get(rss_url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
            if resp.ok:
                news = _parse_rss(resp.text)
                log.info("Yahoo RSS: %d news items", len(news))
        except Exception as exc:
            log.warning("Yahoo RSS error: %s", exc)

    if news:
        _NEWS_CACHE = news
        _CACHE_TS = time.time()
    elif not _NEWS_CACHE:
        _NEWS_CACHE = [{
            "time": "—", "title": "News feed unavailable — check API keys",
            "source": "", "impact": "low", "url": "", "score": None,
        }]

    return _NEWS_CACHE
