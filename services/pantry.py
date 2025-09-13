# path: services/pantry.py
from __future__ import annotations

from typing import Any, Dict, List, Optional

from utils.db import get_conn, query_all, query_one, execute_with_retry, transaction, safe_commit


def list_all(search: str = "") -> List[Dict[str, Any]]:
    """
    Return pantry rows (as sqlite3.Row). If search is provided, filter
    by name/brand/category/subcategory/notes (case-insensitive).
    """
    conn = get_conn()
    try:
        if search:
            s = f"%{search.lower()}%"
            return query_all(
                conn,
                """
                SELECT id, name, brand, category, subcategory,
                       quantity, unit,
                       net_weight_value, net_weight_unit, measure_phase,
                       threshold, notes
                FROM pantry
                WHERE LOWER(COALESCE(name,''))        LIKE ?
                   OR LOWER(COALESCE(brand,''))       LIKE ?
                   OR LOWER(COALESCE(category,''))    LIKE ?
                   OR LOWER(COALESCE(subcategory,'')) LIKE ?
                   OR LOWER(COALESCE(notes,''))       LIKE ?
                ORDER BY LOWER(name), LOWER(brand)
                """,
                (s, s, s, s, s),
            )
        return query_all(
            conn,
            """
            SELECT id, name, brand, category, subcategory,
                   quantity, unit,
                   net_weight_value, net_weight_unit, measure_phase,
                   threshold, notes
            FROM pantry
            ORDER BY LOWER(name), LOWER(brand)
            """,
        )
    finally:
        conn.close()


def get_by_id(row_id: int):
    conn = get_conn()
    try:
        return query_one(
            conn,
            """
            SELECT id, name, brand, category, subcategory,
                   quantity, unit, net_weight_value, net_weight_unit,
                   measure_phase, threshold, notes
            FROM pantry
            WHERE id = ?
            """,
            (int(row_id),),
        )
    finally:
        conn.close()


def insert(item: Dict[str, Any]) -> int:
    with transaction() as conn:
        cur = execute_with_retry(
            conn,
            """
            INSERT INTO pantry
              (name, brand, category, subcategory,
               quantity, unit,
               net_weight_value, net_weight_unit, measure_phase,
               threshold, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.get("name"),
                item.get("brand"),
                item.get("category"),
                item.get("subcategory"),
                item.get("quantity"),
                item.get("unit"),
                item.get("net_weight_value"),
                item.get("net_weight_unit"),
                item.get("measure_phase"),
                item.get("threshold"),
                item.get("notes"),
            ),
        )
        safe_commit(conn)
        return int(cur.lastrowid)


def update(row_id: int, item: Dict[str, Any]) -> None:
    with transaction() as conn:
        execute_with_retry(
            conn,
            """
            UPDATE pantry
            SET name=?, brand=?, category=?, subcategory=?,
                quantity=?, unit=?,
                net_weight_value=?, net_weight_unit=?, measure_phase=?,
                threshold=?, notes=?
            WHERE id=?
            """,
            (
                item.get("name"),
                item.get("brand"),
                item.get("category"),
                item.get("subcategory"),
                item.get("quantity"),
                item.get("unit"),
                item.get("net_weight_value"),
                item.get("net_weight_unit"),
                item.get("measure_phase"),
                item.get("threshold"),
                item.get("notes"),
                int(row_id),
            ),
        )
        safe_commit(conn)


def delete_many(ids: List[int]) -> None:
    if not ids:
        return
    with transaction() as conn:
        for pid in ids:
            execute_with_retry(conn, "DELETE FROM pantry WHERE id=?", (int(pid),))
        safe_commit(conn)
