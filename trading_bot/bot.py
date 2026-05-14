"""
NQ SENTINEL — Trading Bot
Usage:
    python bot.py              # run continuously
    python bot.py --test       # fire one simulated alert (no data needed)
"""

import argparse
import logging
import sys
import time
from datetime import datetime, timezone

from config import (
    SCAN_INTERVAL_SEC,
    SIGNAL_TF,
    SYMBOL,
    TIMEFRAMES,
)
from alerts import fire_alert
from data_feed import fetch_ohlcv, session_levels
from strategy import Signal, evaluate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("nq_sentinel")


def load_all_frames() -> dict:
    """Fetch all configured timeframes. Returns dict of DataFrames."""
    frames = {}
    for tf, cfg in TIMEFRAMES.items():
        log.debug("Fetching %s %s/%s …", SYMBOL, cfg["interval"], cfg["period"])
        df = fetch_ohlcv(SYMBOL, cfg["interval"], cfg["period"])
        if not df.empty:
            # For 4H we resample from 1H data
            if tf == "4h":
                df = (
                    df.resample("4h")
                    .agg({"open": "first", "high": "max", "low": "min",
                          "close": "last", "volume": "sum"})
                    .dropna()
                )
            frames[tf] = df
    return frames


def scan_once(last_signal_ts: float) -> float:
    """Run one scan cycle. Returns updated last_signal_ts."""
    log.info("Scanning %s …", SYMBOL)

    frames = load_all_frames()
    if not frames:
        log.warning("No data loaded — check network / symbol")
        return last_signal_ts

    df_1h = frames.get("1h")
    levels = session_levels(df_1h) if df_1h is not None else {}
    log.info(
        "Session levels — PDH:%s PDL:%s NY_H:%s NY_L:%s",
        levels.get("PDH"), levels.get("PDL"),
        levels.get("NY_H"), levels.get("NY_L"),
    )

    sig: Signal | None = evaluate(frames, levels)

    if sig is None:
        log.info("No signal this cycle")
        return last_signal_ts

    now = time.time()
    if now - last_signal_ts < 5 * 60:
        log.info("Signal suppressed — cooldown (< 5 min since last)")
        return last_signal_ts

    log.info(
        "SIGNAL: %s | Entry %s | SL %s | TP1 %s | TP2 %s | RR 1:%s",
        sig.direction, sig.entry, sig.stop_loss, sig.tp1, sig.tp2, sig.rr,
    )
    fire_alert(sig, levels)
    return now


def test_alert() -> None:
    """Fire a synthetic signal for wiring-test purposes."""
    from strategy import Signal
    sig = Signal(
        direction   = "LONG",
        entry       = 20_012.75,
        stop_loss   = 19_989.50,
        tp1         = 20_059.25,
        tp2         = 20_106.00,
        risk_pts    = 23.25,
        rr          = 2.5,
        timeframe   = "5m",
        confluences = [
            "4H bullish bias (HTF)",
            "15m CHoCH confirmed",
            "5m bullish FVG (20,005.00–20,015.50)",
            "NY session low swept (19,998.75)",
        ],
        bias_4h     = "BULL",
        bias_1h     = "BULL",
        vol_delta   = 3_340.0,
    )
    levels = {
        "PDH": 20_184.25, "PDL": 19_876.50,
        "ASIA_H": 20_042.75, "ASIA_L": 19_961.00,
        "LDN_H": 20_108.50, "LDN_L": 19_924.25,
        "NY_H": 20_156.00,  "NY_L": 19_998.75,
    }
    log.info("Firing test alert …")
    fire_alert(sig, levels)
    log.info("Done.")


def main() -> None:
    parser = argparse.ArgumentParser(description="NQ SENTINEL trading bot")
    parser.add_argument("--test", action="store_true", help="Fire one test alert and exit")
    parser.add_argument("--once", action="store_true", help="Run one scan cycle and exit")
    args = parser.parse_args()

    if args.test:
        test_alert()
        return

    log.info("NQ SENTINEL started — scanning every %ds", SCAN_INTERVAL_SEC)
    last_signal_ts = 0.0

    if args.once:
        scan_once(last_signal_ts)
        return

    while True:
        try:
            last_signal_ts = scan_once(last_signal_ts)
        except KeyboardInterrupt:
            log.info("Stopped by user")
            sys.exit(0)
        except Exception as exc:
            log.error("Unhandled error: %s", exc, exc_info=True)

        log.info("Next scan in %ds …", SCAN_INTERVAL_SEC)
        time.sleep(SCAN_INTERVAL_SEC)


if __name__ == "__main__":
    main()
