"""Supabase helpers for storing snapshots."""
from __future__ import annotations

from typing import Any, Dict

from supabase import create_client
from supabase.client import Client


def create_supabase(supabase_url: str, supabase_service_role_key: str) -> Client:
    return create_client(supabase_url, supabase_service_role_key)


def persist_market_snapshot(client: Client, snapshot: Dict[str, Any]) -> None:
    _insert(client, "market_snapshots", snapshot)


def persist_weather_snapshot(client: Client, snapshot: Dict[str, Any]) -> None:
    _insert(client, "weather_snapshots", snapshot)


def _insert(client: Client, table: str, payload: Dict[str, Any]) -> None:
    response = client.table(table).insert(payload).execute()
    error = getattr(response, "error", None)
    if error:
        raise RuntimeError(f"Supabase insert into {table} failed: {error}")
