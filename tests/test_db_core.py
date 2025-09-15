# file: tests/test_db_core.py
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pytest

from utils.db import (
    ENV_VAR,
    execute_with_retry,
    get_connection,
    query_all,
    query_one,
    resolve_path,
    safe_commit,
    transaction,
)


def test_resolve_path_env_override(tmp_path, monkeypatch):
    target = tmp_path / "mydb.sqlite"
    monkeypatch.setenv(ENV_VAR, str(target))
    p = resolve_path(None)
    assert Path(p) == target


def test_get_connection_creates_db(tmp_path):
    db = tmp_path / "app.db"
    conn = get_connection(db)
    try:
        assert db.exists()
        # PRAGMAs should be applied
        fk = conn.execute("PRAGMA foreign_keys").fetchone()[0]
        assert int(fk) == 1
    finally:
        conn.close()


def test_transaction_commit_and_rollback(tmp_path):
    db = tmp_path / "t.db"
    conn = get_connection(db)
    try:
        conn.execute("CREATE TABLE t(id INTEGER PRIMARY KEY, v TEXT)")
        with transaction(conn):
            conn.execute("INSERT INTO t(v) VALUES ('ok')")
        assert query_one(conn, "SELECT COUNT(1) FROM t")[0] == 1
        # rollback on exception
        with pytest.raises(RuntimeError):
            with transaction(conn):
                conn.execute("INSERT INTO t(v) VALUES ('nope')")
                raise RuntimeError("boom")
        assert query_one(conn, "SELECT COUNT(1) FROM t")[0] == 1
    finally:
        conn.close()


def test_query_helpers(tmp_path):
    db = tmp_path / "q.db"
    conn = get_connection(db)
    try:
        conn.execute("CREATE TABLE a(id INTEGER PRIMARY KEY, v TEXT)")
        conn.executemany("INSERT INTO a(v) VALUES (?)", [("x",), ("y",)])
        assert query_one(conn, "SELECT v FROM a WHERE id=1")[0] == "x"
        rows = query_all(conn, "SELECT v FROM a ORDER BY id")
        assert [r[0] for r in rows] == ["x", "y"]
    finally:
        conn.close()


def test_execute_with_retry_handles_locked(monkeypatch):
    calls = {"n": 0}

    class FakeConn:
        def __init__(self):
            self._commits = 0
            self._rolls = 0

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            # emulate sqlite connection context manager
            if exc_type is None:
                self._commits += 1
            else:
                self._rolls += 1
            return False

        def execute(self, sql, params=()):
            calls["n"] += 1
            if calls["n"] < 3:
                raise sqlite3.OperationalError("database is locked")

            # return a dummy cursor-like object
            class Cur:
                lastrowid = 1

            return Cur()

    cur = execute_with_retry(FakeConn(), "INSERT INTO t VALUES (1)")
    assert getattr(cur, "lastrowid", 0) == 1
    assert calls["n"] == 3
