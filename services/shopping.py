# path: services/shopping.py
from __future__ import annotations

from typing import Any, Dict, Iterable, Optional
import sqlite3

from utils.db import (
    get_conn,
    transaction,
    query_all,
    query_one,
    execute_with_retry,
    safe_commit,
)

# ------------------------------ helpers ------------------------------

def _iter_low_stock_rows(conn: sqlite3.Connection):
    """
    Yields pantry rows at/below threshold.
    Kept private so we don't create cross-module imports.
    """
    rows = query_all(
        conn,
        """
        SELECT id, name, brand, category, store, quantity, unit, threshold
        FROM pantry
        WHERE threshold IS NOT NULL
        """,
    )
    for r in rows:
        qty = r["quantity"]
        thr = r["threshold"]
        try:
            if qty is not None and thr is not None and float(qty) <= float(thr):
                yield r
        except Exception:
            # ignore malformed values
            continue

def _shopping_table(conn: sqlite3.Connection) -> str:
    row = query_one(conn, "SELECT name FROM sqlite_master WHERE type='table' AND name='shopping_list'")
    return "shopping_list" if row else "shopping"

# ------------------------------ public API ------------------------------

def merge_or_increment(
    conn: sqlite3.Connection,
    *,
    name: str,
    brand: str | None = None,
    category: str | None = None,
    store: str | None = None,
    notes: str | None = None,
    qty_needed: float = 1.0,
    unit: str | None = None,
    pantry_id: int | None = None,
) -> int:
    """
    Upsert an 'open' shopping row, deduping by pantry_id if provided,
    else by (name, brand, unit).
    Returns the row id.
    """
    tbl = _shopping_table(conn)

    if pantry_id is not None:
        existing = query_one(
            conn,
            f"SELECT id, qty_needed FROM {tbl} WHERE pantry_id=? AND COALESCE(status,'open')='open'",
            (pantry_id,),
        )
        if existing:
            new_qty = float(existing["qty_needed"] or 0) + float(qty_needed)
            execute_with_retry(conn, f"UPDATE {tbl} SET qty_needed=? WHERE id=?", (new_qty, existing["id"]))
            return int(existing["id"])

    existing = query_one(
        conn,
        f"""
        SELECT id, qty_needed FROM {tbl}
        WHERE pantry_id IS NULL
          AND COALESCE(status,'open')='open'
          AND COALESCE(LOWER(name),'')  = COALESCE(LOWER(?),'')
          AND COALESCE(LOWER(brand),'') = COALESCE(LOWER(?),'')
          AND COALESCE(LOWER(unit),'')  = COALESCE(LOWER(?),'')
        """,
        (name, brand, unit),
    )
    if existing:
        new_qty = float(existing["qty_needed"] or 0) + float(qty_needed)
        execute_with_retry(conn, f"UPDATE {tbl} SET qty_needed=? WHERE id=?", (new_qty, existing["id"]))
        return int(existing["id"])

    cur = execute_with_retry(
        conn,
        f"""
        INSERT INTO {tbl} (name, brand, category, store, notes, qty_needed, unit, pantry_id, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'open')
        """,
        (name, brand, category, store, notes, float(qty_needed), unit, pantry_id),
    )
    return int(cur.lastrowid)


def recompute_from_thresholds(conn: Optional[sqlite3.Connection] = None) -> int:
    """
    Ensure each low-stock pantry item has an open shopping row.
    Returns number of inserts (new rows).
    """
    own = False
    if conn is None:
        conn, own = get_conn(), True

    tbl = _shopping_table(conn)
    inserted = 0
    with transaction(conn) as tconn:
        existing_open = {
            r["pantry_id"]
            for r in query_all(
                tconn,
                f"SELECT pantry_id FROM {tbl} WHERE pantry_id IS NOT NULL AND COALESCE(status,'open')='open'",
            )
            if r["pantry_id"] is not None
        }

        for r in _iter_low_stock_rows(tconn):
            pid = int(r["id"])
            if pid in existing_open:
                continue
            merge_or_increment(
                tconn,
                name=r["name"],
                brand=r["brand"],
                category=r["category"],
                store=r["store"],
                qty_needed=1.0,
                unit=r["unit"],
                pantry_id=pid,
                notes="auto: threshold",
            )
            inserted += 1

        safe_commit(tconn)

    if own:
        conn.close()
    return inserted


def recompute_for_ids(pantry_ids: Iterable[int], conn: Optional[sqlite3.Connection] = None) -> int:
    """
    Targeted recompute for specific pantry ids (insert or increment).
    Returns count of upserts performed.
    """
    own = False
    if conn is None:
        conn, own = get_conn(), True
    ids = {int(i) for i in pantry_ids if i is not None}
    if not ids:
        if own:
            conn.close()
        return 0

    tbl = _shopping_table(conn)
    upserts = 0
    with transaction(conn) as tconn:
        rows = query_all(
            tconn,
            f"""
            SELECT id, name, brand, category, quantity, unit, threshold
            FROM pantry
            WHERE id IN ({",".join("?" for _ in ids)})
            """,
            tuple(ids),
        )
        for r in rows:
            qty, thr = r["quantity"], r["threshold"]
            if thr is None or qty is None or float(qty) > float(thr):
                continue

            existing = query_one(
                tconn,
                f"SELECT id, qty_needed FROM {tbl} WHERE COALESCE(status,'open')='open' AND pantry_id=?",
                (r["id"],),
            )
            if existing:
                new_qty = float(existing["qty_needed"] or 0.0) + 1.0
                execute_with_retry(tconn, f"UPDATE {tbl} SET qty_needed=? WHERE id=?", (new_qty, existing["id"]))
            else:
                merge_or_increment(
                    tconn,
                    name=r["name"],
                    brand=r["brand"],
                    category=r["category"],
                    store=None,
                    qty_needed=1.0,
                    unit=r["unit"],
                    pantry_id=int(r["id"]),
                    notes="auto: threshold",
                )
            upserts += 1

        safe_commit(tconn)

    if own:
        conn.close()
    return upserts


def mark_purchased(conn: Optional[sqlite3.Connection], shopping_id: int) -> None:
    own = False
    if conn is None:
        conn, own = get_conn(), True
    tbl = _shopping_table(conn)
    with transaction(conn) as tconn:
        execute_with_retry(tconn, f"UPDATE {tbl} SET status='purchased' WHERE id=?", (int(shopping_id),))
        safe_commit(tconn)
    if own:
        conn.close()
