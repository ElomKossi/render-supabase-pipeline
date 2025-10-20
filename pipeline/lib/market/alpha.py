"""Alpha Vantage client helpers."""
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict

import requests

from .config import Config

ALPHAVANTAGE_BASE = "https://www.alphavantage.co/query"
MAX_RETRIES = 5
RETRY_BACKOFF_SECONDS = 10


def _request(params: Dict[str, str], config: Config) -> Dict[str, Any]:
    attempt = 0
    while True:
        attempt += 1
        try:
            response = requests.get(
                ALPHAVANTAGE_BASE,
                params=params,
                timeout=config.timeout_seconds,
            )
            response.raise_for_status()
            payload: Dict[str, Any] = response.json()
            note = payload.get("Note")
            message = payload.get("Error Message")
            if note or message:
                raise RuntimeError(note or message)
            return payload
        except requests.exceptions.Timeout as exc:
            if attempt >= MAX_RETRIES:
                raise RuntimeError("Alpha Vantage request timed out") from exc
            time.sleep(RETRY_BACKOFF_SECONDS * attempt)
        except requests.exceptions.HTTPError as exc:
            status = exc.response.status_code if exc.response else None
            if status and (status == 429 or status >= 500):
                if attempt >= MAX_RETRIES:
                    raise RuntimeError(
                        f"Alpha Vantage request failed after retries (status {status})"
                    ) from exc
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            raise RuntimeError(f"Alpha Vantage HTTP error: {status}") from exc
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(f"Alpha Vantage request failed: {exc}") from exc
        except RuntimeError as exc:
            message = str(exc)
            if "frequency" in message.lower() or "limit" in message.lower():
                if attempt >= MAX_RETRIES:
                    raise RuntimeError("Alpha Vantage rate limit hit repeatedly") from exc
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            raise


def fetch_intraday(symbol: str, config: Config) -> Dict[str, Any]:
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": config.interval,
        "outputsize": "compact",
        "apikey": config.alphavantage_api_key,
    }
    data = _request(params, config)
    series_key = f"Time Series ({config.interval})"
    series = data.get(series_key)
    if not series:
        raise RuntimeError(f"Intraday data missing for {symbol}")
    latest_timestamp, latest_candle = next(iter(series.items()))
    timestamp = datetime.fromisoformat(latest_timestamp).replace(tzinfo=timezone.utc)
    return {
        "symbol": symbol,
        "captured_at": timestamp.isoformat(),
        "open": float(latest_candle["1. open"]),
        "high": float(latest_candle["2. high"]),
        "low": float(latest_candle["3. low"]),
        "close": float(latest_candle["4. close"]),
        "volume": float(latest_candle["5. volume"]),
    }


def fetch_daily(symbol: str, config: Config) -> Dict[str, Any]:
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol,
        "outputsize": "compact",
        "apikey": config.alphavantage_api_key,
    }
    data = _request(params, config)
    series = data.get("Time Series (Daily)")
    if not series:
        raise RuntimeError(f"Daily data missing for {symbol}")
    iterator = iter(series.items())
    latest_date, latest_candle = next(iterator)
    previous_entry = next(iterator, None)
    previous_close = float(previous_entry[1]["4. close"]) if previous_entry else None
    return {
        "latest_date": latest_date,
        "latest_close": float(latest_candle["4. close"]),
        "previous_close": previous_close,
    }
