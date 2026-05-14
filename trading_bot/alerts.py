"""
Alert delivery: Telegram Bot API + Twilio SMS.
Both channels are optional — if credentials are missing the channel is skipped.
"""

import logging
from typing import Optional

import requests

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_FROM,
    TWILIO_TO,
    SYMBOL_DISPLAY,
)
from strategy import Signal

log = logging.getLogger(__name__)


def _format_telegram(sig: Signal, levels: dict) -> str:
    arrow  = "🟢▲" if sig.direction == "LONG" else "🔴▼"
    bullet = "•"

    conf_text = "\n".join(f"  {bullet} {c}" for c in sig.confluences) or "  (none)"

    lvl_lines = []
    for k, v in levels.items():
        if v is not None:
            lvl_lines.append(f"  {k}: {v}")
    lvl_text = "\n".join(lvl_lines) or "  —"

    delta_sym = "+" if sig.vol_delta >= 0 else ""

    return (
        f"⚡ *{SYMBOL_DISPLAY} SIGNAL — {arrow} {sig.direction}*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 *Entry:*    `{sig.entry}`\n"
        f"🛑 *Stop Loss:* `{sig.stop_loss}`\n"
        f"🎯 *TP1 (2R):* `{sig.tp1}`\n"
        f"🎯 *TP2 (4R):* `{sig.tp2}`\n"
        f"📐 *Risk:*      `{sig.risk_pts} pts`\n"
        f"📊 *R:R:*       `1:{sig.rr}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🧠 *Bias:* 4H `{sig.bias_4h}` | 1H `{sig.bias_1h}`\n"
        f"📈 *Vol Delta (5 bars):* `{delta_sym}{sig.vol_delta:,.0f}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"*Confluences:*\n{conf_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"*Session Levels:*\n{lvl_text}\n"
    )


def _format_sms(sig: Signal) -> str:
    arrow = "▲" if sig.direction == "LONG" else "▼"
    return (
        f"{SYMBOL_DISPLAY} {arrow}{sig.direction} | "
        f"Entry:{sig.entry} SL:{sig.stop_loss} "
        f"TP1:{sig.tp1} TP2:{sig.tp2} | "
        f"RR 1:{sig.rr} Risk:{sig.risk_pts}pts"
    )


def send_telegram(sig: Signal, levels: dict) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log.info("Telegram not configured – skipping")
        return False

    url  = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    text = _format_telegram(sig, levels)
    try:
        resp = requests.post(url, json={
            "chat_id":    TELEGRAM_CHAT_ID,
            "text":       text,
            "parse_mode": "Markdown",
        }, timeout=10)
        if resp.ok:
            log.info("Telegram alert sent")
            return True
        log.error("Telegram error %s: %s", resp.status_code, resp.text)
    except Exception as exc:
        log.error("Telegram exception: %s", exc)
    return False


def send_sms(sig: Signal) -> bool:
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM, TWILIO_TO]):
        log.info("Twilio not configured – skipping")
        return False

    try:
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        msg = client.messages.create(
            body=_format_sms(sig),
            from_=TWILIO_FROM,
            to=TWILIO_TO,
        )
        log.info("SMS sent: %s", msg.sid)
        return True
    except ImportError:
        log.warning("twilio package not installed – SMS skipped")
    except Exception as exc:
        log.error("Twilio exception: %s", exc)
    return False


def fire_alert(sig: Signal, levels: dict) -> None:
    """Send signal to all configured channels."""
    tg_ok  = send_telegram(sig, levels)
    sms_ok = send_sms(sig)
    if not tg_ok and not sms_ok:
        # Fallback: log prominently so you always see it
        log.warning(
            "\n%s\n%s",
            "=" * 50,
            _format_sms(sig),
        )
