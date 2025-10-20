"""Snapshot transformation helpers for market data."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from .config import Config


def build_snapshot(intraday: Dict[str, Any], daily: Dict[str, Any], config: Config) -> Dict[str, Any]:
    previous_close = daily.get("previous_close")
    change = intraday["close"] - previous_close if previous_close is not None else None
    change_percent = (
        round((change / previous_close) * 100, 4) if change is not None and previous_close else None
    )
    return {
        "symbol": intraday["symbol"],
        "captured_at": intraday["captured_at"],
        "interval": config.interval,
        "price": intraday["close"],
        "open": intraday["open"],
        "high": intraday["high"],
        "low": intraday["low"],
        "volume": intraday["volume"],
        "previous_close": previous_close,
        "change": change,
        "change_percent": change_percent,
        "source": "alphavantage",
        "metadata": {"daily_close_date": daily["latest_date"]},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
