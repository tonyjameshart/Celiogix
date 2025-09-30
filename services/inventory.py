from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
import sqlite3
from typing import Any

from services.pantry import add_item as pantry_add
from services.pantry import adjust_quantity as pantry_adjust_qty
from services.pantry import get_by_id as pantry_get
from services.pantry import list_items as pantry_list
from services.pantry import update_item as pantry_update
from services.shopping import delete_item as shop_delete
from services.shopping import get_by_id as shop_get
from utils.db import query_all, tx


def find_pantry_by_name_brand(
    conn: sqlite3.Connection, name: str, brand: str | None
) -> dict[str, Any] | None:
    rows = query_all(
        conn,
        """
        SELECT id, name, brand, quantity, unit, net_weight
        FROM pantry
        WHERE LOWER(name)=? AND LOWER(COALESCE(brand,''))=?
        LIMIT 1
        """,
        (name.strip().lower(), (brand or "").strip().lower()),
    )
    return dict(rows[0]) if rows else None


def ensure_pantry_entry(
    conn: sqlite3.Connection,
    *,
    name: str,
    brand: str | None = None,
    unit: str | None = None,
    net_weight: float | None = None,
) -> int:
    existing = find_pantry_by_name_brand(conn, name, brand)
    if existing:
        return int(existing["id"])
    return pantry_add(conn, name=name, brand=brand, unit=unit, net_weight=net_weight)


def apply_purchase_to_pantry(
    conn: sqlite3.Connection,
    shopping_id: int,
    *,
    quantity: float = 1.0,
    unit: str | None = None,
    attach_brand: bool = True,
) -> int:
    s = shop_get(conn, shopping_id)
    if not s:
        raise KeyError(f"shopping item {shopping_id} not found")
    name = str(s.get("name", "") or "")
    brand = str(s.get("brand") or "") if attach_brand else None
    pantry_id = ensure_pantry_entry(
        conn,
        name=name,
        brand=brand,
        unit=unit or (s.get("unit") if isinstance(s.get("unit"), str) else None),
        net_weight=float(s["net_weight"]) if s.get("net_weight") not in (None, "") else None,
    )
    pantry_adjust_qty(conn, pantry_id, quantity)
    shop_delete(conn, shopping_id)
    return pantry_id


def consume_from_pantry(conn: sqlite3.Connection, pantry_id: int, quantity: float) -> None:
    pantry_adjust_qty(conn, pantry_id, -abs(quantity))


def rename_merge_pantry(
    conn: sqlite3.Connection,
    *,
    source_id: int,
    target_name: str,
    target_brand: str | None = None,
) -> int:
    src = pantry_get(conn, source_id)
    if not src:
        raise KeyError(f"pantry item {source_id} not found")

    target = find_pantry_by_name_brand(conn, target_name, target_brand)
    if target:
        qty = float(src.get("quantity") or 0)
        pantry_adjust_qty(conn, int(target["id"]), qty)
        with tx(conn) as c:
            c.execute("DELETE FROM pantry WHERE id=?", (source_id,))
        return int(target["id"])

    pantry_update(conn, source_id, {"name": target_name, "brand": target_brand})
    return source_id


def build_pantry_index(conn: sqlite3.Connection) -> dict[tuple[str, str], int]:
    idx: dict[tuple[str, str], int] = {}
    for row in pantry_list(conn):
        key = (
            str(row.get("name", "")).strip().lower(),
            str(row.get("brand", "") or "").strip().lower(),
        )
        idx[key] = int(row["id"])
    return idx


# ----- Legacy API stubs expected by services/__init__.py -----


def apply_menu_consumption(
    conn: sqlite3.Connection, items: Iterable[Mapping[str, Any]] | None = None
) -> int:
    return 0


def apply_pending(conn: sqlite3.Connection) -> None:
    return None


def expand_menu_ingredients(
    conn: sqlite3.Connection,
    menu_items: Iterable[Mapping[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    return []


def is_low_stock(row: Mapping[str, Any] | dict[str, Any]) -> bool:
    try:
        q = float(row.get("quantity", 0) or 0)
    except Exception:
        q = 0.0
    return q <= 0.0


def iter_low_stock_items(conn: sqlite3.Connection) -> Iterator[dict[str, Any]]:
    for r in pantry_list(conn):
        if is_low_stock(r):
            yield r
