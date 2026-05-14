"""
ICT / SMC indicator functions.
All functions accept a pandas DataFrame with columns: open, high, low, close, volume.
"""

import numpy as np
import pandas as pd


# ── Swing points ──────────────────────────────────────────────────────────────

def swing_highs(df: pd.DataFrame, n: int = 5) -> pd.Series:
    """Returns a boolean Series; True where close is a local swing high."""
    highs = df["high"]
    pivot = highs == highs.rolling(2 * n + 1, center=True).max()
    return pivot.fillna(False)


def swing_lows(df: pd.DataFrame, n: int = 5) -> pd.Series:
    lows = df["low"]
    pivot = lows == lows.rolling(2 * n + 1, center=True).min()
    return pivot.fillna(False)


# ── Structure ─────────────────────────────────────────────────────────────────

def detect_bos(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """
    Break of Structure detection.
    Returns df with added columns: bos_bull (True when a swing high is broken),
    bos_bear (True when a swing low is broken).
    """
    sh = swing_highs(df, n)
    sl = swing_lows(df, n)

    last_sh = pd.Series(np.nan, index=df.index)
    last_sl = pd.Series(np.nan, index=df.index)
    lsh = np.nan
    lsl = np.nan
    for i in range(len(df)):
        if sh.iloc[i]:
            lsh = df["high"].iloc[i]
        if sl.iloc[i]:
            lsl = df["low"].iloc[i]
        last_sh.iloc[i] = lsh
        last_sl.iloc[i] = lsl

    df = df.copy()
    df["bos_bull"] = (df["close"] > last_sh) & (last_sh.notna())
    df["bos_bear"] = (df["close"] < last_sl) & (last_sl.notna())
    df["last_sh"]  = last_sh
    df["last_sl"]  = last_sl
    return df


def detect_choch(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """
    Change of Character — first BOS opposing the prevailing swing direction.
    Appends choch_bull and choch_bear columns.
    """
    df = detect_bos(df, n)
    # prevailing trend: more recent BOS direction
    df["choch_bull"] = False
    df["choch_bear"] = False

    trend = 0  # 0=unknown, 1=bull, -1=bear
    for i in range(1, len(df)):
        if df["bos_bull"].iloc[i] and trend == -1:
            df.loc[df.index[i], "choch_bull"] = True
            trend = 1
        elif df["bos_bull"].iloc[i]:
            trend = 1
        if df["bos_bear"].iloc[i] and trend == 1:
            df.loc[df.index[i], "choch_bear"] = True
            trend = -1
        elif df["bos_bear"].iloc[i]:
            trend = -1
    return df


# ── Fair Value Gaps ───────────────────────────────────────────────────────────

def detect_fvg(df: pd.DataFrame, min_pts: float = 5.0) -> pd.DataFrame:
    """
    Bullish FVG: low[i] > high[i-2]  (gap up, 3-candle pattern)
    Bearish FVG: high[i] < low[i-2]
    Returns df with fvg_bull_top, fvg_bull_bot, fvg_bear_top, fvg_bear_bot.
    """
    df = df.copy()
    df["fvg_bull_top"] = np.nan
    df["fvg_bull_bot"] = np.nan
    df["fvg_bear_top"] = np.nan
    df["fvg_bear_bot"] = np.nan

    for i in range(2, len(df)):
        gap_up   = df["low"].iloc[i]  - df["high"].iloc[i - 2]
        gap_down = df["low"].iloc[i - 2] - df["high"].iloc[i]
        if gap_up > min_pts:
            df.loc[df.index[i], "fvg_bull_top"] = df["low"].iloc[i]
            df.loc[df.index[i], "fvg_bull_bot"] = df["high"].iloc[i - 2]
        if gap_down > min_pts:
            df.loc[df.index[i], "fvg_bear_top"] = df["low"].iloc[i - 2]
            df.loc[df.index[i], "fvg_bear_bot"] = df["high"].iloc[i]
    return df


# ── Order Blocks ──────────────────────────────────────────────────────────────

def detect_order_blocks(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """
    Bullish OB: last bearish candle before a bullish BOS.
    Bearish OB: last bullish candle before a bearish BOS.
    """
    df = detect_bos(df, n).copy()
    df["ob_bull_top"] = np.nan
    df["ob_bull_bot"] = np.nan
    df["ob_bear_top"] = np.nan
    df["ob_bear_bot"] = np.nan

    for i in range(1, len(df)):
        if df["bos_bull"].iloc[i]:
            # walk back to last bearish candle
            for j in range(i - 1, max(i - 20, 0), -1):
                if df["close"].iloc[j] < df["open"].iloc[j]:
                    df.loc[df.index[i], "ob_bull_top"] = df["open"].iloc[j]
                    df.loc[df.index[i], "ob_bull_bot"] = df["low"].iloc[j]
                    break
        if df["bos_bear"].iloc[i]:
            for j in range(i - 1, max(i - 20, 0), -1):
                if df["close"].iloc[j] > df["open"].iloc[j]:
                    df.loc[df.index[i], "ob_bear_top"] = df["high"].iloc[j]
                    df.loc[df.index[i], "ob_bear_bot"] = df["open"].iloc[j]
                    break
    return df


# ── Multi-TF Bias ─────────────────────────────────────────────────────────────

def htf_bias(df: pd.DataFrame, n: int = 5) -> str:
    """Returns 'BULL', 'BEAR', or 'NEUTRAL' for the last N-bar trend."""
    if len(df) < 2 * n + 1:
        return "NEUTRAL"
    recent = df.tail(3 * n)
    sh = swing_highs(recent, n)
    sl = swing_lows(recent, n)

    highs = recent.loc[sh, "high"].values
    lows  = recent.loc[sl, "low"].values

    if len(highs) >= 2 and len(lows) >= 2:
        hh = highs[-1] > highs[-2]
        hl = lows[-1]  > lows[-2]
        lh = highs[-1] < highs[-2]
        ll = lows[-1]  < lows[-2]
        if hh and hl:
            return "BULL"
        if lh and ll:
            return "BEAR"
    return "NEUTRAL"


# ── Volume Delta (approximation) ──────────────────────────────────────────────

def volume_delta(df: pd.DataFrame) -> pd.Series:
    """
    Approximate buy/sell delta: bullish candle → +volume, bearish → -volume.
    """
    sign = np.where(df["close"] >= df["open"], 1, -1)
    return pd.Series(sign * df["volume"].values, index=df.index)
