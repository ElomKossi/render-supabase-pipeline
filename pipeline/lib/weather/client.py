"""Open-Meteo client helpers."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests

from .config import WeatherConfig

BASE_URL = "https://api.open-meteo.com/v1/forecast"
DEFAULT_CURRENT_VARS = [
    "temperature_2m",
    "relativehumidity_2m",
    "is_day",
    "precipitation",
    "weathercode",
    "windspeed_10m",
    "winddirection_10m",
]


def fetch_payload(config: WeatherConfig) -> Dict[str, Any]:
    params = {
        "latitude": config.latitude,
        "longitude": config.longitude,
        "current": ",".join(DEFAULT_CURRENT_VARS),
        "hourly": ",".join(sorted(set(config.hourly_variables + ["temperature_2m"]))),
        "past_days": 1,
        "timezone": "UTC",
    }
    response = requests.get(BASE_URL, params=params, timeout=config.timeout_seconds)
    response.raise_for_status()
    return response.json()


def _to_utc(timestamp: str) -> str:
    if timestamp.endswith("Z"):
        return timestamp
    dt = datetime.fromisoformat(timestamp)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def extract_previous_hour(payload: Dict[str, Any], current_time: str) -> Optional[float]:
    hourly = payload.get("hourly")
    if not hourly:
        return None
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    if not times or not temps:
        return None
    target_index = None
    for index, timestamp in enumerate(times):
        if timestamp == current_time:
            target_index = index
            break
        if timestamp > current_time:
            target_index = max(0, index - 1)
            break
    if target_index is None:
        target_index = len(times) - 1
    previous_index = max(0, target_index - 1)
    if previous_index >= len(temps):
        return None
    try:
        return float(temps[previous_index])
    except (ValueError, TypeError):
        return None


def build_snapshot(payload: Dict[str, Any], config: WeatherConfig) -> Dict[str, Any]:
    current = payload.get("current")
    if not current:
        raise RuntimeError("Open-Meteo current weather missing in payload")
    current_time = current.get("time")
    if not current_time:
        raise RuntimeError("Open-Meteo payload missing current time field")

    captured_at = _to_utc(current_time)
    temperature = _as_float(current.get("temperature_2m"))
    previous_temperature = extract_previous_hour(payload, current_time)

    change = (
        temperature - previous_temperature
        if temperature is not None and previous_temperature is not None
        else None
    )
    change_percent = (
        round((change / previous_temperature) * 100, 4)
        if change not in (None, 0) and previous_temperature not in (None, 0)
        else None
    )

    return {
        "location": config.location_label,
        "captured_at": captured_at,
        "temperature_c": temperature,
        "relative_humidity": _as_float(current.get("relativehumidity_2m")),
        "windspeed_kmh": _as_float(current.get("windspeed_10m")),
        "winddirection_deg": _as_float(current.get("winddirection_10m")),
        "precipitation_mm": _as_float(current.get("precipitation")),
        "previous_temperature_c": previous_temperature,
        "temperature_change": change,
        "temperature_change_percent": change_percent,
        "source": "open-meteo",
        "metadata": {
            "weather_code": current.get("weathercode"),
            "is_day": current.get("is_day"),
            "latitude": payload.get("latitude"),
            "longitude": payload.get("longitude"),
        },
    }


def _as_float(value: Any) -> Optional[float]:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
