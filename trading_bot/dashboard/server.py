"""
NQ SENTINEL — Dashboard Server
FastAPI + WebSocket backend.

Run:
    uvicorn dashboard.server:app --host 0.0.0.0 --port 8000 --reload

Then open http://localhost:8000
"""

import asyncio
import json
import logging
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Allow imports from the trading_bot root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import SIGNAL_TF, SYMBOL, TIMEFRAMES
from data_feed import fetch_ohlcv, session_levels
from indicators import htf_bias, volume_delta
from strategy import evaluate

from dashboard.news_feed import fetch_news

log = logging.getLogger("nq_sentinel.dashboard")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)

STATIC_DIR = Path(__file__).parent / "static"

# ── Shared state ──────────────────────────────────────────────────────────────

state: dict[str, Any] = {
    "price":       0.0,
    "prev_price":  0.0,
    "open_price":  0.0,
    "change":      0.0,
    "change_pct":  0.0,
    "last_update": 0.0,
    "candles":     [],        # last 120 × 5m OHLCV for the chart
    "levels":      {},
    "bias": {
        "overall": "NEUTRAL",
        "score":   50,
        "tfs": {"4h": "NEUTRAL", "1h": "NEUTRAL", "30m": "NEUTRAL",
                "15m": "NEUTRAL", "5m": "NEUTRAL", "1m": "NEUTRAL"},
    },
    "signal":      None,
    "signal_history": [],     # last 10 signals
    "news":        [],
    "delta_bars":  [],
}


# ── WebSocket manager ─────────────────────────────────────────────────────────

class _WsManager:
    def __init__(self):
        self._clients: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self._clients.append(ws)

    def disconnect(self, ws: WebSocket):
        self._clients = [c for c in self._clients if c is not ws]

    async def broadcast(self, msg: dict):
        dead = []
        payload = json.dumps(msg)
        for ws in self._clients:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


ws_manager = _WsManager()


# ── Data helpers ──────────────────────────────────────────────────────────────

def _bias_score(tfs: dict[str, str]) -> int:
    bull = sum(1 for v in tfs.values() if v == "BULL")
    total = len(tfs)
    return int(bull / total * 100)


def _overall_bias(tfs: dict[str, str]) -> str:
    score = _bias_score(tfs)
    if score >= 65:
        return "BULL"
    if score <= 35:
        return "BEAR"
    return "NEUTRAL"


def _candles_to_list(df: pd.DataFrame, limit: int = 120) -> list[dict]:
    df = df.tail(limit)
    result = []
    for ts, row in df.iterrows():
        result.append({
            "t": ts.isoformat(),
            "o": round(row["open"],  2),
            "h": round(row["high"],  2),
            "l": round(row["low"],   2),
            "c": round(row["close"], 2),
            "v": int(row["volume"]),
        })
    return result


# ── Background scanner ────────────────────────────────────────────────────────

async def _scan_loop():
    last_signal_ts = 0.0

    while True:
        try:
            await _do_scan(last_signal_ts)
        except Exception as exc:
            log.error("Scan error: %s", exc, exc_info=True)
        await asyncio.sleep(60)


async def _do_scan(last_signal_ts: float) -> float:
    log.info("Scanning %s …", SYMBOL)
    frames: dict[str, pd.DataFrame] = {}

    for tf, cfg in TIMEFRAMES.items():
        df = await asyncio.to_thread(fetch_ohlcv, SYMBOL, cfg["interval"], cfg["period"])
        if df.empty:
            continue
        if tf == "4h":
            df = (
                df.resample("4h")
                .agg({"open": "first", "high": "max", "low": "min",
                      "close": "last", "volume": "sum"})
                .dropna()
            )
        frames[tf] = df

    if not frames:
        log.warning("No data — skipping scan")
        return last_signal_ts

    # ── price ──────────────────────────────────────────────────────────────
    df_5 = frames.get("5m", pd.DataFrame())
    if not df_5.empty:
        price     = round(float(df_5["close"].iloc[-1]), 2)
        open_p    = round(float(df_5["open"].iloc[0]),   2)
        chg       = round(price - open_p, 2)
        chg_pct   = round(chg / open_p * 100, 2)
        state["prev_price"]  = state["price"]
        state["price"]       = price
        state["open_price"]  = open_p
        state["change"]      = chg
        state["change_pct"]  = chg_pct
        state["last_update"] = time.time()
        state["candles"]     = _candles_to_list(df_5)

        # volume delta last 5 bars
        vd = volume_delta(df_5).tail(5).values.tolist()
        state["delta_bars"] = [
            {"label": str(df_5.index[-(5 - i)].strftime("%H:%M")),
             "delta": round(float(vd[i]))}
            for i in range(len(vd))
        ]

    # ── levels ─────────────────────────────────────────────────────────────
    df_1h = frames.get("1h", pd.DataFrame())
    if not df_1h.empty:
        lvls = await asyncio.to_thread(session_levels, df_1h)
        state["levels"] = lvls

    # ── bias per TF ────────────────────────────────────────────────────────
    tf_bias: dict[str, str] = {}
    for tf in ["4h", "1h", "30m", "15m", "5m", "1m"]:
        df = frames.get(tf)
        if df is not None and len(df) > 15:
            tf_bias[tf] = htf_bias(df)
        else:
            tf_bias[tf] = "NEUTRAL"

    overall = _overall_bias(tf_bias)
    score   = _bias_score(tf_bias)
    state["bias"] = {"overall": overall, "score": score, "tfs": tf_bias}

    # ── signal ─────────────────────────────────────────────────────────────
    sig = await asyncio.to_thread(evaluate, frames, state["levels"])
    if sig and (time.time() - last_signal_ts > 300):
        sig_dict = {
            "direction":   sig.direction,
            "entry":       sig.entry,
            "stop_loss":   sig.stop_loss,
            "tp1":         sig.tp1,
            "tp2":         sig.tp2,
            "risk_pts":    sig.risk_pts,
            "rr":          sig.rr,
            "confluences": sig.confluences,
            "bias_4h":     sig.bias_4h,
            "bias_1h":     sig.bias_1h,
            "vol_delta":   sig.vol_delta,
            "ts":          time.time(),
        }
        state["signal"] = sig_dict
        state["signal_history"].insert(0, sig_dict)
        state["signal_history"] = state["signal_history"][:10]
        last_signal_ts = time.time()

        # fire external alerts in background
        try:
            from alerts import fire_alert
            await asyncio.to_thread(fire_alert, sig, state["levels"])
        except Exception as e:
            log.warning("Alert delivery error: %s", e)

    # ── news ───────────────────────────────────────────────────────────────
    state["news"] = await asyncio.to_thread(fetch_news)

    # ── broadcast to all WS clients ────────────────────────────────────────
    await ws_manager.broadcast({"type": "full_state", "data": _public_state()})
    log.info("Broadcast sent — price=%s bias=%s signal=%s",
             state["price"], state["bias"]["overall"],
             state["signal"]["direction"] if state["signal"] else "—")

    return last_signal_ts


def _public_state() -> dict:
    return {
        "price":          state["price"],
        "change":         state["change"],
        "change_pct":     state["change_pct"],
        "candles":        state["candles"],
        "levels":         state["levels"],
        "bias":           state["bias"],
        "signal":         state["signal"],
        "signal_history": state["signal_history"],
        "news":           state["news"],
        "delta_bars":     state["delta_bars"],
        "last_update":    state["last_update"],
    }


# ── App lifespan ──────────────────────────────────────────────────────────────

@asynccontextmanager
async def _lifespan(app: FastAPI):
    task = asyncio.create_task(_scan_loop())
    yield
    task.cancel()


app = FastAPI(title="NQ SENTINEL", lifespan=_lifespan)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/state")
async def api_state():
    return JSONResponse(_public_state())


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws_manager.connect(ws)
    # send current state immediately on connect
    await ws.send_text(json.dumps({"type": "full_state", "data": _public_state()}))
    try:
        while True:
            await ws.receive_text()   # keep-alive / client pings
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)
