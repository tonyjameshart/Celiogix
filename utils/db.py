# path: utils/db.py
from __future__ import annotations
import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager
import time
from typing import Iterable, Tuple, Any, Optional

ENV_VAR = "CELIAC_DB"  # optional override

def _project_root() -> Path:
    # utils/ is one level under the project root
    return Path(__file__).resolve().parent.parent

def _default_db_path() -> Path:
    """
    Preferred: <project_root>/data/app.db
    If an existing DB is found elsewhere, prefer it to avoid “losing” data.
    """
    root = _project_root()
    candidates = [
        root / "data" / "app.db",
        Path.cwd() / "data" / "app.db",
        Path.cwd() / "app.db",
        root / "app.db",
    ]
    for p in candidates:
        if p.exists():
            return p
    return root / "data" / "app.db"

def resolve_path(db_path: str | os.PathLike | None = None) -> str:
    env = os.environ.get(ENV_VAR)
    p = Path(db_path or env or _default_db_path()).resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    return str(p)

def get_connection(db_path: str | os.PathLike | None = None) -> sqlite3.Connection:
    """
    Open SQLite with sensible defaults for a desktop app.
    """
    path = resolve_path(db_path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    with conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
    return conn

# ---------------------------------------------------------------------------
# Compatibility shims expected by services.inventory
# ---------------------------------------------------------------------------

def get_conn() -> sqlite3.Connection:
    """Alias to get_connection() for callers expecting get_conn()."""
    return get_connection()

@contextmanager
def transaction(conn: sqlite3.Connection):
    """
    Context manager that BEGINs a transaction and COMMITs or ROLLBACKs.
    Usage:
        with transaction(conn) as tconn:
            tconn.execute(...)
    """
    try:
        conn.execute("BEGIN")
        yield conn
        conn.commit()
    except Exception:
        try:
            conn.rollback()
        finally:
            raise

def query_all(conn: sqlite3.Connection, sql: str, params: Iterable[Any] | Tuple[Any, ...] = ()) -> list[sqlite3.Row]:
    cur = conn.execute(sql, tuple(params))
    return cur.fetchall()

def query_one(conn: sqlite3.Connection, sql: str, params: Iterable[Any] | Tuple[Any, ...] = ()) -> Optional[sqlite3.Row]:
    cur = conn.execute(sql, tuple(params))
    return cur.fetchone()

def execute_with_retry(conn: sqlite3.Connection, sql: str, params: Iterable[Any] | Tuple[Any, ...] = (),
                       retries: int = 3, delay: float = 0.05) -> None:
    """
    Simple retry wrapper for transient 'database is locked' cases.
    """
    for attempt in range(retries):
        try:
            conn.execute(sql, tuple(params))
            return
        except sqlite3.OperationalError as e:
            msg = str(e).lower()
            if "locked" in msg and attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
                continue
            raise

def safe_commit(conn: sqlite3.Connection) -> None:
    try:
        conn.commit()
    except Exception:
        # Attempt rollback; re-raise original exception after rollback
        try:
            conn.rollback()
        finally:
            raise
