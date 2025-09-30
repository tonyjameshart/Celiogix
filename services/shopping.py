# path: D:\GitHub\Celiogix\Celiogix\services\shopping.py
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
        SELECT id, name, brand, category, net_weight, thresh, store, notes, created_at
        FROM shopping_list
        ORDER BY created_at DESC, LOWER(name) ASC
        """,
    )
    return _rows_to_dicts(rows)


def search_items(conn: sqlite3.Connection, q: str) -> list[dict[str, Any]]:
    like = f"%{q.lower().strip()}%"
    rows = query_all(
        conn,
        """
        SELECT id, name, brand, category, net_weight, thresh, store, notes, created_at
        FROM shopping_list
        WHERE LOWER(name) LIKE ?
           OR LOWER(brand) LIKE ?
           OR LOWER(category) LIKE ?
           OR LOWER(store) LIKE ?
           OR LOWER(notes) LIKE ?
        ORDER BY created_at DESC
        """,
        (like, like, like, like, like),
    )
    return _rows_to_dicts(rows)


def get_by_id(conn: sqlite3.Connection, item_id: int) -> dict[str, Any] | None:
    rows = query_all(
        conn,
        """
        SELECT id, name, brand, category, net_weight, thresh, store, notes, created_at
        FROM shopping_list
        WHERE id=?
        """,
        (item_id,),
    )
    return dict(rows[0]) if rows else None


def _find_by_name_brand(
    conn: sqlite3.Connection, name: str, brand: str | None
) -> dict[str, Any] | None:
    rows = query_all(
        conn,
        """
        SELECT id, name, brand, category, net_weight, thresh, store, notes, created_at
        FROM shopping_list
        WHERE LOWER(name)=? AND LOWER(COALESCE(brand,''))=?
        LIMIT 1
        """,
        (name.strip().lower(), (brand or "").strip().lower()),
    )
    return dict(rows[0]) if rows else None


def add_item(  # noqa: PLR0913
    conn: sqlite3.Connection,
    *,
    name: str,
    brand: str | None = None,
    category: str | None = None,
    net_weight: float | None = None,
    thresh: float | None = None,
    store: str | None = None,
    notes: str | None = None,
) -> int:
    with tx(conn) as c:
        cur = c.execute(
            """
            INSERT INTO shopping_list(name, brand, category, net_weight, thresh, store, notes)
            VALUES(?,?,?,?,?,?,?)
            """,
            (name, brand, category, net_weight, thresh, store, notes),
        )
        last_id = cur.lastrowid
        if last_id is None:
            raise RuntimeError("Failed to retrieve inserted shopping_list id")
        return int(last_id)


def merge_or_increment(  # noqa: PLR0913
    conn: sqlite3.Connection,
    *,
    name: str,
    brand: str | None = None,
    category: str | None = None,
    net_weight: float | None = None,
    thresh: float | None = None,
    store: str | None = None,
    notes: str | None = None,
) -> int:
    existing = _find_by_name_brand(conn, name, brand)
    if existing:
        return int(existing["id"])
    return add_item(
        conn,
        name=name,
        brand=brand,
        category=category,
        net_weight=net_weight,
        thresh=thresh,
        store=store,
        notes=notes,
    )


def update_item(conn: sqlite3.Connection, item_id: int, updates: dict[str, Any]) -> None:
    if not updates:
        return
    cols = ", ".join(f"{k}=?" for k in updates)  # SIM118
    params: list[Any] = [*updates.values(), item_id]
    with tx(conn) as c:
        execute_with_retry(c, f"UPDATE shopping_list SET {cols} WHERE id=?", tuple(params))


def delete_item(conn: sqlite3.Connection, item_id: int) -> None:
    with tx(conn) as c:
        execute_with_retry(c, "DELETE FROM shopping_list WHERE id=?", (item_id,))


def delete_many(conn: sqlite3.Connection, ids: Iterable[int]) -> None:
    id_list = list(ids)
    if not id_list:
        return
    with tx(conn) as c:
        for i in id_list:
            execute_with_retry(c, "DELETE FROM shopping_list WHERE id=?", (i,))


def recompute_for_ids(conn: sqlite3.Connection, ids: Iterable[int]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i in ids:
        row = get_by_id(conn, i)
        if row:
            out.append(row)
    return out


def recompute_from_thresholds(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return []


def set_thresh(conn: sqlite3.Connection, item_id: int, thresh: float | None) -> None:
    update_item(conn, item_id, {"thresh": thresh})


def list_all(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return list_items(conn)


def insert(conn: sqlite3.Connection, **kwargs: Any) -> int:
    return add_item(conn, **kwargs)


def update(conn: sqlite3.Connection, item_id: int, updates: dict[str, Any]) -> None:
    update_item(conn, item_id, updates)


def mark_purchased(
    conn: sqlite3.Connection,
    item_id: int,
    *,
    quantity: float = 1.0,
    unit: str | None = None,
    attach_brand: bool = True,
) -> int:
    # Lazy import to avoid circular import during module import.
    from services.inventory import apply_purchase_to_pantry

    return apply_purchase_to_pantry(
        conn, shopping_id=item_id, quantity=quantity, unit=unit, attach_brand=attach_brand
    )


def mark_purchased_many(
    conn: sqlite3.Connection,
    ids: Iterable[int],
    *,
    quantity_per_item: float = 1.0,
    unit: str | None = None,
    attach_brand: bool = True,
) -> list[int]:
    from services.inventory import apply_purchase_to_pantry  # lazy import

    out: list[int] = []
    for i in ids:
        try:
            out.append(
                apply_purchase_to_pantry(
                    conn,
                    shopping_id=i,
                    quantity=quantity_per_item,
                    unit=unit,
                    attach_brand=attach_brand,
                )
            )
        except KeyError:
            continue
    return out
