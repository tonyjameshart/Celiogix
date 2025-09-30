from __future__ import annotations

from collections.abc import Iterable
import sqlite3
from typing import Any

from utils.db import execute_with_retry, query_all, tx


def _rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(r) for r in rows]


def list_items(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = query_all(
        conn,
        """
        SELECT id, name, brand, category, subcategory, net_weight, unit,
               quantity, store, expiration, gf_flag, tags, notes
        FROM pantry
        ORDER BY LOWER(name) ASC, COALESCE(brand,'') ASC
        """,
    )
    return _rows_to_dicts(rows)


def search_items(conn: sqlite3.Connection, q: str) -> list[dict[str, Any]]:
    like = f"%{q.lower().strip()}%"
    rows = query_all(
        conn,
        """
        SELECT id, name, brand, category, subcategory, net_weight, unit,
               quantity, store, expiration, gf_flag, tags, notes
        FROM pantry
        WHERE LOWER(name) LIKE ?
           OR LOWER(brand) LIKE ?
           OR LOWER(category) LIKE ?
           OR LOWER(tags) LIKE ?
        ORDER BY LOWER(name) ASC
        """,
        (like, like, like, like),
    )
    return _rows_to_dicts(rows)


def get_by_id(conn: sqlite3.Connection, item_id: int) -> dict[str, Any] | None:
    rows = query_all(
        conn,
        """
        SELECT id, name, brand, category, subcategory, net_weight, unit,
               quantity, store, expiration, gf_flag, tags, notes
        FROM pantry
        WHERE id=?
        """,
        (item_id,),
    )
    return dict(rows[0]) if rows else None


def add_item(  # noqa: PLR0913
    conn: sqlite3.Connection,
    *,
    name: str,
    brand: str | None = None,
    category: str | None = None,
    subcategory: str | None = None,
    net_weight: float | None = None,
    unit: str | None = None,
    quantity: float | None = None,
    store: str | None = None,
    expiration: str | None = None,
    gf_flag: str | None = None,
    tags: str | None = None,
    notes: str | None = None,
) -> int:
    with tx(conn) as c:
        cur = c.execute(
            """
            INSERT INTO pantry(name, brand, category, subcategory, net_weight, unit,
                               quantity, store, expiration, gf_flag, tags, notes)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                name,
                brand,
                category,
                subcategory,
                net_weight,
                unit,
                quantity,
                store,
                expiration,
                gf_flag,
                tags,
                notes,
            ),
        )
        last_id = cur.lastrowid
        if last_id is None:
            raise RuntimeError("Failed to retrieve inserted pantry id")
        return int(last_id)


def insert(conn: sqlite3.Connection, **kwargs: Any) -> int:  # legacy alias
    return add_item(conn, **kwargs)


def update_item(conn: sqlite3.Connection, item_id: int, updates: dict[str, Any]) -> None:
    if not updates:
        return
    cols = ", ".join(f"{k}=?" for k in updates)
    params: list[Any] = [*updates.values(), item_id]
    with tx(conn) as c:
        execute_with_retry(c, f"UPDATE pantry SET {cols} WHERE id=?", tuple(params))


def update(conn: sqlite3.Connection, item_id: int, updates: dict[str, Any]) -> None:  # legacy
    update_item(conn, item_id, updates)


def delete_item(conn: sqlite3.Connection, item_id: int) -> None:
    with tx(conn) as c:
        execute_with_retry(c, "DELETE FROM pantry WHERE id=?", (item_id,))


def delete_many(conn: sqlite3.Connection, ids: Iterable[int]) -> None:
    ids_list = list(ids)
    if not ids_list:
        return
    with tx(conn) as c:
        for i in ids_list:
            execute_with_retry(c, "DELETE FROM pantry WHERE id=?", (i,))


def adjust_quantity(conn: sqlite3.Connection, item_id: int, delta: float) -> None:
    with tx(conn) as c:
        execute_with_retry(
            c,
            "UPDATE pantry SET quantity = COALESCE(quantity,0) + ? WHERE id=?",
            (delta, item_id),
        )


def list_all(conn: sqlite3.Connection) -> list[dict[str, Any]]:  # legacy alias
    return list_items(conn)
