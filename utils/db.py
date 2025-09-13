# path: utils/db.py
from __future__ import annotations
import os
import sqlite3
from pathlib import Path

ENV_VAR = "CELIAC_DB"  # optional override

def _project_root() -> Path:
    # utils/ is one level under the project root
    return Path(__file__).resolve().parent.parent

def _default_db_path() -> Path:
    """
    Preferred: <project_root>/data/app.db  (matches Tree.txt)
    If an existing DB is found elsewhere, prefer it to avoid “losing” data.
    Search order for existing files:
      1) <project_root>/data/app.db
      2) CWD/data/app.db
      3) CWD/app.db
      4) <project_root>/app.db  (legacy/accidental)
    Otherwise create: <project_root>/data/app.db
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
    # Allow explicit override via argument or env var
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
