#!/usr/bin/env python3
"""Main entry point for the Render cron job."""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Dict, List

# Ensure project root is on sys.path when executed as a script
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from pipeline.lib.market import alpha, config, snapshot  # noqa: E402
from pipeline.lib.utils import persist  # noqa: E402

CALL_DELAY_SECONDS = 15  # Alpha Vantage free tier: 5 requests/minute.


def poll_symbol(symbol: str, cfg: config.Config, client) -> None:
    print(f"Fetching data for {symbol}...")
    intraday = alpha.fetch_intraday(symbol, cfg)
    daily = alpha.fetch_daily(symbol, cfg)
    snap = snapshot.build_snapshot(intraday, daily, cfg)
    persist.persist_market_snapshot(client, snap)
    print(f"Stored snapshot for {symbol} at {snap['captured_at']}")


def run(symbols: List[str], cfg: config.Config) -> int:
    client = persist.create_supabase(cfg.supabase_url, cfg.supabase_service_role_key)
    errors: List[Dict[str, str]] = []
    for index, symbol in enumerate(symbols):
        try:
            poll_symbol(symbol, cfg, client)
        except Exception as exc:  # noqa: BLE001
            msg = str(exc)
            errors.append({"symbol": symbol, "error": msg})
            print(f"Error processing {symbol}: {msg}", file=sys.stderr)
        if index != len(symbols) - 1:
            time.sleep(CALL_DELAY_SECONDS)
    if errors:
        print("Completed with errors:", errors, file=sys.stderr)
        return 1
    print("All snapshots stored successfully")
    return 0


def main() -> None:
    cfg = config.load_config()
    exit_code = run(cfg.symbols, cfg)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
