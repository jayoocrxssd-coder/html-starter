"""
Fetches OHLCV data via yfinance (free, ~15-min delayed for futures).
Returns a cleaned pandas DataFrame with columns: open, high, low, close, volume.
"""

import logging
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf

log = logging.getLogger(__name__)


def fetch_ohlcv(symbol: str, interval: str, period: str) -> pd.DataFrame:
    """Download bars and return a tidy DataFrame indexed by UTC datetime."""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(interval=interval, period=period, auto_adjust=True)
    except Exception as exc:
        log.error("yfinance error: %s", exc)
        return pd.DataFrame()

    if df.empty:
        log.warning("No data returned for %s %s/%s", symbol, interval, period)
        return df

    df.index = df.index.tz_convert("UTC")
    df.columns = [c.lower() for c in df.columns]
    df = df[["open", "high", "low", "close", "volume"]].dropna()
    return df


def session_levels(df_1h: pd.DataFrame) -> dict:
    """
    Derive Asia / London / NY high-low from the 1h dataframe for today.
    All times are UTC.
    """
    today = datetime.now(timezone.utc).date()
    day_df = df_1h[df_1h.index.date == today]

    def session_hl(start_h: int, end_h: int):
        s = day_df[(day_df.index.hour >= start_h) & (day_df.index.hour < end_h)]
        if s.empty:
            return None, None
        return round(s["high"].max(), 2), round(s["low"].min(), 2)

    asia_h,   asia_l   = session_hl(0,  8)    # 00-08 UTC
    london_h, london_l = session_hl(7,  12)   # 07-12 UTC
    ny_h,     ny_l     = session_hl(13, 21)   # 13-21 UTC  (09-17 ET)

    prev_day = day_df = df_1h[df_1h.index.date < today]
    pdh = round(prev_day["high"].max(), 2) if not prev_day.empty else None
    pdl = round(prev_day["low"].min(),  2) if not prev_day.empty else None

    return {
        "PDH": pdh, "PDL": pdl,
        "ASIA_H": asia_h, "ASIA_L": asia_l,
        "LDN_H": london_h, "LDN_L": london_l,
        "NY_H": ny_h, "NY_L": ny_l,
    }
