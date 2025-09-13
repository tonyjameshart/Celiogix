# path: utils/settings.py
from __future__ import annotations
import os
import sqlite3
from typing import Optional

_ENV_MAP = {
    "edamam_app_id": "EDAMAM_APP_ID",
    "edamam_app_key": "EDAMAM_APP_KEY",
    "spoonacular_api_key": "SPOONACULAR_API_KEY",
}

def get_setting(conn: sqlite3.Connection, key: str, default: str = "") -> str:
    """Return setting with ENV taking precedence over DB."""
    env_key = _ENV_MAP.get(key)
    if env_key and os.getenv(env_key):
        return os.getenv(env_key, "").strip()
    try:
        row = conn.execute("SELECT value FROM app_settings WHERE key=?", (key,)).fetchone()
        return (row[0] if row and row[0] is not None else default).strip()
    except Exception:
        return default

def set_setting(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO app_settings(key,value) VALUES(?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value.strip()),
    )
    conn.commit()
