import os
from dotenv import load_dotenv

load_dotenv()

# ── Instrument ──────────────────────────────────────────────────────────────
SYMBOL = os.getenv("SYMBOL", "NQ=F")          # NQ futures via yfinance
SYMBOL_DISPLAY = os.getenv("SYMBOL_DISPLAY", "NQ")

# ── Telegram ─────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")

# ── Twilio SMS ────────────────────────────────────────────────────────────────
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM        = os.getenv("TWILIO_FROM", "")   # e.g. +15005550006
TWILIO_TO          = os.getenv("TWILIO_TO", "")     # your phone number

# ── Strategy ──────────────────────────────────────────────────────────────────
MIN_RR            = float(os.getenv("MIN_RR", "2.0"))    # minimum risk:reward
SWING_LOOKBACK    = int(os.getenv("SWING_LOOKBACK", "5")) # bars each side for pivot
FVG_MIN_PTS       = float(os.getenv("FVG_MIN_PTS", "5")) # min FVG size in points
SCAN_INTERVAL_SEC = int(os.getenv("SCAN_INTERVAL_SEC", "60"))

# ── Timeframes to analyse (yfinance intervals) ────────────────────────────────
TIMEFRAMES = {
    "4h":  {"interval": "1h",  "period": "60d"},   # yfinance max granularity trick
    "1h":  {"interval": "1h",  "period": "30d"},
    "30m": {"interval": "30m", "period": "10d"},
    "15m": {"interval": "15m", "period": "7d"},
    "5m":  {"interval": "5m",  "period": "5d"},
    "1m":  {"interval": "1m",  "period": "1d"},
}

# Entry timeframe for signals
SIGNAL_TF = "5m"
