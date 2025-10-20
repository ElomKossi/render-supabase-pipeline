"""Environment helpers for Open-Meteo ingestion."""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv

REQUIRED_ENVS = ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "OPENMETEO_LATITUDE", "OPENMETEO_LONGITUDE"]
DEFAULT_HOURLY_VARS = ["temperature_2m", "relativehumidity_2m", "precipitation", "windspeed_10m"]
DEFAULT_TIMEOUT = 30.0


@dataclass(frozen=True)
class WeatherConfig:
    supabase_url: str
    supabase_service_role_key: str
    latitude: float
    longitude: float
    location_label: str
    hourly_variables: List[str]
    timeout_seconds: float


def _parse_float(value: str, field: str) -> float:
    try:
        return float(value)
    except ValueError as error:
        raise SystemExit(f"Invalid {field} value: {value}") from error


def _parse_list(raw: str | None, default: List[str]) -> List[str]:
    if not raw:
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


def _parse_timeout(raw: str | None) -> float:
    if not raw:
        return DEFAULT_TIMEOUT
    try:
        value = float(raw)
    except ValueError as error:
        raise SystemExit(f"Invalid OPENMETEO_TIMEOUT value: {raw}") from error
    return value if value > 0 else DEFAULT_TIMEOUT


def load_config() -> WeatherConfig:
    load_dotenv()
    missing = [var for var in REQUIRED_ENVS if not os.getenv(var)]
    if missing:
        for var in missing:
            print(f"Missing required environment variable: {var}", file=sys.stderr)
        sys.exit(1)

    latitude = _parse_float(os.environ["OPENMETEO_LATITUDE"], "OPENMETEO_LATITUDE")
    longitude = _parse_float(os.environ["OPENMETEO_LONGITUDE"], "OPENMETEO_LONGITUDE")

    return WeatherConfig(
        supabase_url=os.environ["SUPABASE_URL"],
        supabase_service_role_key=os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        latitude=latitude,
        longitude=longitude,
        location_label=os.getenv("OPENMETEO_LOCATION", "unknown"),
        hourly_variables=_parse_list(os.getenv("OPENMETEO_HOURLY_VARS"), DEFAULT_HOURLY_VARS),
        timeout_seconds=_parse_timeout(os.getenv("OPENMETEO_TIMEOUT")),
    )
