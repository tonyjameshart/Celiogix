# path: utils/settings.py
from __future__ import annotations

import sqlite3
from typing import Any

_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS app_settings (
    key   TEXT PRIMARY KEY,
    value TEXT
)
"""

def ensure_settings_table(conn: sqlite3.Connection) -> None:
    """Create storage table once per DB."""
    try:
        conn.execute(_TABLE_SQL)
        conn.commit()
    except Exception:
        # keep UI responsive even if settings table can't be created
        pass

def get_setting(conn: sqlite3.Connection, key: str, default: str | None = None) -> str | None:
    """
    Read a setting as string. Returns default on any error or if missing.

    Used by providers, e.g.:
      spoonacular_api_key
      edamam_app_id
      edamam_app_key
    """
    ensure_settings_table(conn)
    try:
        row = conn.execute("SELECT value FROM app_settings WHERE key=?", (key,)).fetchone()
        if row is None:
            return default
        return row[0]
    except Exception:
        return default

def set_setting(conn: sqlite3.Connection, key: str, value: Any) -> None:
    """Upsert a setting. Values are stored as strings."""
    ensure_settings_table(conn)
    try:
        conn.execute(
            """
            INSERT INTO app_settings(key, value) VALUES(?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """,
            (key, "" if value is None else str(value)),
        )
        conn.commit()
    except Exception:
        pass

# Optional convenience readers
def get_bool(conn: sqlite3.Connection, key: str, default: bool = False) -> bool:
    val = (get_setting(conn, key, None) or "").strip().lower()
    if val in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if val in {"0", "false", "f", "no", "n", "off"}:
        return False
    return default

def get_int(conn: sqlite3.Connection, key: str, default: int = 0) -> int:
    try:
        return int(get_setting(conn, key, str(default)) or default)
    except Exception:
        return default
