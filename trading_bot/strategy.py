"""
ICT / SMC signal engine.

A signal is generated when ALL of the following align:
  HTF bias (4H + 1H) agrees on direction
  Session level swept (liquidity taken below/above key level)
  15m CHoCH or BOS confirms reversal
  5m price is inside a FVG or OB in the HTF direction
  Minimum R:R met (configurable)

Returns a Signal dataclass or None.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import pandas as pd

from config import MIN_RR, SWING_LOOKBACK, FVG_MIN_PTS
from indicators import (
    detect_choch,
    detect_fvg,
    detect_order_blocks,
    htf_bias,
    volume_delta,
)

log = logging.getLogger(__name__)


@dataclass
class Signal:
    direction: str        # "LONG" or "SHORT"
    entry:     float
    stop_loss: float
    tp1:       float      # 2R target
    tp2:       float      # 4R target
    risk_pts:  float
    rr:        float
    timeframe: str
    confluences: list[str]
    bias_4h:   str
    bias_1h:   str
    vol_delta: float      # cumulative last 5 bars


def _risk_pts(direction: str, entry: float, stop: float) -> float:
    if direction == "LONG":
        return round(entry - stop, 2)
    return round(stop - entry, 2)


def _tp(direction: str, entry: float, risk: float, multiple: float) -> float:
    if direction == "LONG":
        return round(entry + risk * multiple, 2)
    return round(entry - risk * multiple, 2)


def _sl_from_swing(direction: str, df_5m: pd.DataFrame, n: int) -> float:
    """SL = beyond the last swing extreme on 5m."""
    if direction == "LONG":
        recent_lows = df_5m["low"].tail(3 * n)
        return round(recent_lows.min() - 2, 2)   # 2-pt buffer
    recent_highs = df_5m["high"].tail(3 * n)
    return round(recent_highs.max() + 2, 2)


def evaluate(
    dfs: dict[str, pd.DataFrame],
    levels: dict,
) -> Optional[Signal]:
    """
    dfs  – keyed by timeframe string, e.g. {"4h": df, "1h": df, "5m": df, ...}
    levels – session levels dict from data_feed.session_levels()
    """
    required = {"4h", "1h", "15m", "5m"}
    if not required.issubset(dfs):
        log.warning("Missing required timeframes: %s", required - dfs.keys())
        return None

    # ── HTF bias ──────────────────────────────────────────────────────────────
    bias_4h = htf_bias(dfs["4h"], SWING_LOOKBACK)
    bias_1h = htf_bias(dfs["1h"], SWING_LOOKBACK)

    if bias_4h == "NEUTRAL" and bias_1h == "NEUTRAL":
        log.debug("Both HTF neutral – no trade")
        return None

    # Use the majority bias; if they conflict use 4H
    if bias_4h != "NEUTRAL":
        direction = bias_4h
    else:
        direction = bias_1h

    # ── 15m CHoCH / BOS confirmation ─────────────────────────────────────────
    df_15 = detect_choch(dfs["15m"], SWING_LOOKBACK)
    last = df_15.iloc[-1]
    if direction == "BULL":
        structure_ok = last["choch_bull"] or last["bos_bull"]
    else:
        structure_ok = last["choch_bear"] or last["bos_bear"]

    if not structure_ok:
        log.debug("No 15m structure confirmation")
        return None

    # ── 5m FVG / OB entry zone ────────────────────────────────────────────────
    df_5 = dfs["5m"].copy()
    df_5 = detect_fvg(df_5, FVG_MIN_PTS)
    df_5 = detect_order_blocks(df_5, SWING_LOOKBACK)

    recent_5 = df_5.tail(10)
    price_now = df_5["close"].iloc[-1]

    confluences: list[str] = []
    entry_zone_hit = False

    if direction == "BULL":
        # Price inside bullish FVG
        fvg_rows = recent_5.dropna(subset=["fvg_bull_bot"])
        for _, row in fvg_rows.iterrows():
            if row["fvg_bull_bot"] <= price_now <= row["fvg_bull_top"]:
                entry_zone_hit = True
                confluences.append(f"5m bullish FVG ({row['fvg_bull_bot']:.2f}–{row['fvg_bull_top']:.2f})")
        # Price inside bullish OB
        ob_rows = recent_5.dropna(subset=["ob_bull_bot"])
        for _, row in ob_rows.iterrows():
            if row["ob_bull_bot"] <= price_now <= row["ob_bull_top"]:
                entry_zone_hit = True
                confluences.append(f"5m bullish OB ({row['ob_bull_bot']:.2f}–{row['ob_bull_top']:.2f})")
    else:
        fvg_rows = recent_5.dropna(subset=["fvg_bear_top"])
        for _, row in fvg_rows.iterrows():
            if row["fvg_bear_bot"] <= price_now <= row["fvg_bear_top"]:
                entry_zone_hit = True
                confluences.append(f"5m bearish FVG ({row['fvg_bear_bot']:.2f}–{row['fvg_bear_top']:.2f})")
        ob_rows = recent_5.dropna(subset=["ob_bear_top"])
        for _, row in ob_rows.iterrows():
            if row["ob_bear_bot"] <= price_now <= row["ob_bear_top"]:
                entry_zone_hit = True
                confluences.append(f"5m bearish OB ({row['ob_bear_bot']:.2f}–{row['ob_bear_top']:.2f})")

    if not entry_zone_hit:
        log.debug("Price not in FVG/OB zone")
        return None

    # ── Liquidity sweep check (optional but adds score) ──────────────────────
    if levels.get("NY_L") and direction == "BULL":
        if df_5["low"].tail(6).min() <= levels["NY_L"]:
            confluences.append(f"NY session low swept ({levels['NY_L']})")

    if levels.get("NY_H") and direction == "BEAR":
        if df_5["high"].tail(6).max() >= levels["NY_H"]:
            confluences.append(f"NY session high swept ({levels['NY_H']})")

    # ── Build levels ──────────────────────────────────────────────────────────
    entry    = round(price_now, 2)
    sl       = _sl_from_swing(direction, df_5, SWING_LOOKBACK)
    risk     = _risk_pts(direction, entry, sl)

    if risk <= 0:
        log.debug("Invalid risk (%s pts)", risk)
        return None

    rr_tp1   = 2.0
    rr_tp2   = 4.0
    tp1      = _tp(direction, entry, risk, rr_tp1)
    tp2      = _tp(direction, entry, risk, rr_tp2)
    rr       = round((tp1 - entry) / risk if direction == "LONG" else (entry - tp1) / risk, 2)

    if rr < MIN_RR:
        log.debug("R:R %.2f below minimum %.2f", rr, MIN_RR)
        return None

    # ── Volume delta ──────────────────────────────────────────────────────────
    vd = volume_delta(df_5).tail(5).sum()

    # Add structure confluence labels
    if bias_4h == "BULL":
        confluences.append("4H bullish bias (HTF)")
    elif bias_4h == "BEAR":
        confluences.append("4H bearish bias (HTF)")

    if last.get("choch_bull") or last.get("choch_bear"):
        confluences.append("15m CHoCH confirmed")
    elif last.get("bos_bull") or last.get("bos_bear"):
        confluences.append("15m BOS confirmed")

    dir_label = "LONG" if direction == "BULL" else "SHORT"

    return Signal(
        direction  = dir_label,
        entry      = entry,
        stop_loss  = sl,
        tp1        = tp1,
        tp2        = tp2,
        risk_pts   = risk,
        rr         = rr,
        timeframe  = "5m",
        confluences= confluences,
        bias_4h    = bias_4h,
        bias_1h    = bias_1h,
        vol_delta  = float(vd),
    )
