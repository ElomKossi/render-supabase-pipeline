"""Environment loading and runtime configuration helpers for market ingestion."""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv

REQUIRED_ENVS = ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "ALPHAVANTAGE_API_KEY"]
DEFAULT_INTERVAL = "5min"
DEFAULT_SYMBOLS = ["AAPL"]
DEFAULT_TIMEOUT = 45.0


@dataclass(frozen=True)
class Config:
    supabase_url: str
    supabase_service_role_key: str
    alphavantage_api_key: str
    interval: str
    symbols: List[str]
    timeout_seconds: float


def _parse_symbols(raw: str | None) -> List[str]:
    if not raw:
        return DEFAULT_SYMBOLS
    return [symbol.strip().upper() for symbol in raw.split(",") if symbol.strip()]


def _parse_timeout(raw: str | None) -> float:
    if not raw:
        return DEFAULT_TIMEOUT
    try:
        value = float(raw)
    except ValueError as error:
        raise SystemExit(f"Invalid ALPHAVANTAGE_TIMEOUT value: {raw}") from error
    return value if value > 0 else DEFAULT_TIMEOUT


def load_config() -> Config:
    """Load .env, validate prerequisites, and return runtime configuration."""
    load_dotenv()
    missing = [var for var in REQUIRED_ENVS if not os.getenv(var)]
    if missing:
        for var in missing:
            print(f"Missing required environment variable: {var}", file=sys.stderr)
        sys.exit(1)

    return Config(
        supabase_url=os.environ["SUPABASE_URL"],
        supabase_service_role_key=os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        alphavantage_api_key=os.environ["ALPHAVANTAGE_API_KEY"],
        interval=os.getenv("INTRADAY_INTERVAL", DEFAULT_INTERVAL),
        symbols=_parse_symbols(os.getenv("MARKET_SYMBOLS")),
        timeout_seconds=_parse_timeout(os.getenv("ALPHAVANTAGE_TIMEOUT")),
    )
