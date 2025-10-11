from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence  # ruff: UP035
from contextlib import contextmanager
import os
from pathlib import Path
import sqlite3
import time
from typing import cast

ENV_VAR = "CELIAC_DB"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _db_path() -> Path:
    return Path(os.getenv(ENV_VAR) or _project_root() / "data" / "celiacshield.db")


def _configure_connection(conn: sqlite3.Connection) -> None:
    conn.row_factory = sqlite3.Row
    # Ensure proper text encoding for Unicode characters
    conn.text_factory = str
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA encoding='UTF-8'")


def get_connection() -> sqlite3.Connection:
    dbp = _db_path()
    dbp.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(dbp)
    _configure_connection(conn)
    return conn


def get_conn() -> sqlite3.Connection:  # legacy alias
    return get_connection()


@contextmanager
def tx(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    try:
        conn.execute("BEGIN")
        yield conn
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise


transaction = tx  # optional alias


def execute(conn: sqlite3.Connection, sql: str, params: Sequence[object] = ()) -> None:
    conn.execute(sql, tuple(params))


def executemany(
    conn: sqlite3.Connection, sql: str, seq_of_params: Iterable[Sequence[object]]
) -> None:
    conn.executemany(sql, [tuple(p) for p in seq_of_params])


def query_all(
    conn: sqlite3.Connection, sql: str, params: Sequence[object] = ()
) -> list[sqlite3.Row]:
    cur = conn.execute(sql, tuple(params))
    rows = cur.fetchall()
    return cast(list[sqlite3.Row], rows)


def query_one(
    conn: sqlite3.Connection, sql: str, params: Sequence[object] = ()
) -> sqlite3.Row | None:
    cur = conn.execute(sql, tuple(params))
    row = cur.fetchone()
    return cast(sqlite3.Row | None, row)


def execute_with_retry(
    conn: sqlite3.Connection,
    sql: str,
    params: Sequence[object] = (),
    retries: int = 3,
    delay: float = 0.05,
) -> None:
    for attempt in range(retries):
        try:
            conn.execute(sql, tuple(params))
            return
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower() and attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
                continue
            raise


def safe_commit(conn: sqlite3.Connection) -> None:
    try:
        conn.commit()
    except Exception:
        try:
            conn.rollback()
        finally:
            raise
