from __future__ import annotations

from collections.abc import Iterable  # ruff: UP035
import sqlite3


def _has_table(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? COLLATE NOCASE", (name,)
    ).fetchone()
    return row is not None


def _cols(conn: sqlite3.Connection, table: str) -> set[str]:
    try:
        return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
    except sqlite3.Error:
        return set()


def _add_col(conn: sqlite3.Connection, table: str, coldef: str) -> None:
    name = coldef.split()[0]
    if name not in _cols(conn, table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {coldef}")


def _create_indexes(conn: sqlite3.Connection, table: str, defs: Iterable[tuple[str, str]]) -> None:
    for idx, expr in defs:
        conn.execute(f"CREATE INDEX IF NOT EXISTS {idx} ON {table}({expr})")


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON")

    conn.execute(
        """CREATE TABLE IF NOT EXISTS app_settings(
            key TEXT PRIMARY KEY,
            value TEXT
        )"""
    )

    conn.execute(
        """CREATE TABLE IF NOT EXISTS pantry(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            brand TEXT,
            category TEXT,
            subcategory TEXT,
            net_weight REAL DEFAULT 0,
            unit TEXT,
            quantity REAL DEFAULT 0,
            store TEXT,
            expiration TEXT,
            gf_flag TEXT DEFAULT 'UNKNOWN',
            tags TEXT,
            notes TEXT
        )"""
    )
    _create_indexes(
        conn,
        "pantry",
        [
            ("idx_pantry_name", "name"),
            ("idx_pantry_cat", "category"),
            ("idx_pantry_brand", "brand"),
        ],
    )

    conn.execute(
        """CREATE TABLE IF NOT EXISTS shopping_list(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            brand TEXT,
            category TEXT,
            net_weight REAL DEFAULT 0,
            thresh REAL DEFAULT 0,
            store TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    _create_indexes(conn, "shopping_list", [("idx_shop_created", "created_at")])

    conn.execute(
        """CREATE TABLE IF NOT EXISTS recipes(
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            source TEXT,
            url TEXT UNIQUE,
            tags TEXT,
            ingredients TEXT,
            instructions TEXT,
            rating REAL DEFAULT 0.0,
            prep_time TEXT DEFAULT '',
            cook_time TEXT DEFAULT '',
            servings INTEGER DEFAULT 0
        )"""
    )
    _create_indexes(
        conn,
        "recipes",
        [
            ("idx_rec_title", "title"),
            ("idx_rec_url", "url"),
        ],
    )
    _add_col(conn, "recipes", "source TEXT")
    _add_col(conn, "recipes", "rating REAL DEFAULT 0.0")
    _add_col(conn, "recipes", "prep_time TEXT DEFAULT ''")
    _add_col(conn, "recipes", "cook_time TEXT DEFAULT ''")
    _add_col(conn, "recipes", "servings INTEGER DEFAULT 0")

    conn.execute(
        """CREATE TABLE IF NOT EXISTS menu_plan(
            id INTEGER PRIMARY KEY,
            date TEXT,
            meal TEXT,
            recipe_id INTEGER,
            title TEXT,
            notes TEXT
        )"""
    )
    _create_indexes(conn, "menu_plan", [("idx_menu_date", "date")])

    conn.execute(
        """CREATE TABLE IF NOT EXISTS health_log(
            id INTEGER PRIMARY KEY,
            date TEXT,
            time TEXT,
            meal TEXT,
            items TEXT,
            risk TEXT,
            onset_min INTEGER DEFAULT 0,
            severity INTEGER DEFAULT 0,
            stool INTEGER DEFAULT 0,
            recipe TEXT,
            symptoms TEXT,
            notes TEXT
        )"""
    )
    _create_indexes(conn, "health_log", [("idx_health_dt", "date, time")])

    _migrate_legacy_health(conn)
    conn.commit()


def _get_flag(conn: sqlite3.Connection, key: str) -> str:
    row = conn.execute("SELECT value FROM app_settings WHERE key=?", (key,)).fetchone()
    return "" if row is None or row[0] is None else str(row[0])


def _set_flag(conn: sqlite3.Connection, key: str, val: str) -> None:
    conn.execute(
        "INSERT INTO app_settings(key,value) VALUES(?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, val),
    )


def _migrate_legacy_health(conn: sqlite3.Connection) -> None:
    if _get_flag(conn, "migrated_health_logs") == "1":
        return
    if not _has_table(conn, "health_logs"):
        _set_flag(conn, "migrated_health_logs", "1")
        return

    legacy = _cols(conn, "health_logs")

    def c(name: str) -> str:
        return name if name in legacy else "NULL"

    sql = f"""
        INSERT INTO health_log(date,time,meal,items,risk,onset_min,severity,stool,recipe,symptoms,notes)
        SELECT
            {c('date')}                                   AS date,
            ''                                            AS time,
            COALESCE({c('meal')},{c('meal_type')})       AS meal,
            {c('meal')}                                   AS items,
            COALESCE({c('risk_level')}, 'UNKNOWN')        AS risk,
            COALESCE({c('onset')}, 0)                     AS onset_min,
            COALESCE({c('severity')}, 0)                  AS severity,
            COALESCE({c('stool_scale')}, 0)               AS stool,
            ''                                            AS recipe,
            COALESCE({c('symptoms')}, '')                 AS symptoms,
            COALESCE({c('notes')}, '')                    AS notes
        FROM health_logs
    """
    try:
        conn.execute(sql)
    finally:
        _set_flag(conn, "migrated_health_logs", "1")
