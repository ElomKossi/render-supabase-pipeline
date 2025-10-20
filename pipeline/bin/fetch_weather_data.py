#!/usr/bin/env python3
"""Ingest weather data from Open-Meteo and persist to Supabase."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path when executed as a script
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from pipeline.lib.utils import persist  # noqa: E402
from pipeline.lib.weather import client, config  # noqa: E402


def main() -> None:
    cfg = config.load_config()
    payload = client.fetch_payload(cfg)
    snapshot = client.build_snapshot(payload, cfg)
    supabase_client = persist.create_supabase(cfg.supabase_url, cfg.supabase_service_role_key)
    persist.persist_weather_snapshot(supabase_client, snapshot)
    print(
        "Stored weather snapshot for"
        f" {cfg.location_label} at {snapshot['captured_at']}"
    )


if __name__ == "__main__":
    main()
