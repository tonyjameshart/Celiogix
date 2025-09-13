# path: services/inventory.py
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Set

import sqlite3

from utils.db import get_conn, transaction, query_all, query_one, execute_with_retry, safe_commit
from utils.units import PHASE_DRY, PHASE_WET, to_canonical, from_canonical, unit_phase
from services import shopping as shopping_svc


def is_low_stock(quantity: Optional[float], threshold: Optional[float]) -> bool:
    try:
        if quantity is None or threshold is None:
            return False
        return float(quantity) <= float(threshold)
    except Exception:
        return False


def iter_low_stock_items(conn: Optional[sqlite3.Connection] = None):
    own = False
    if conn is None:
        conn, own = get_conn(), True
    try:
        rows = query_all(
            conn,
            """
            SELECT id, name, brand, quantity, unit, threshold, category, subcategory, store
            FROM pantry
            WHERE threshold IS NOT NULL
            """,
        )
        for r in rows:
            if is_low_stock(r["quantity"], r["threshold"]):
                yield r
    finally:
        if own:
            conn.close()


def _find_best_pantry_match(conn: sqlite3.Connection, ingredient_name: str) -> Optional[sqlite3.Row]:
    return query_one(
        conn,
        """
        SELECT id, name, brand, quantity, unit, net_weight_unit, measure_phase, expiration
        FROM pantry
        WHERE name = ?
        ORDER BY (expiration IS NULL), expiration ASC
        LIMIT 1
        """,
        (ingredient_name,),
    )


def _deduct_pantry_quantity(
    conn: sqlite3.Connection,
    pantry_id: int,
    deduct_value: float,
    deduct_unit: str,
    phase: str,
    reason: str,
    ref_type: str,
    ref_id: int,
) -> Dict[str, Any]:
    cur_row = query_one(
        conn,
        "SELECT quantity, unit, measure_phase FROM pantry WHERE id = ?",
        (pantry_id,),
    )
    if not cur_row:
        return {"pantry_id": pantry_id, "status": "missing"}

    cur_qty = float(cur_row["quantity"] or 0)
    cur_unit = cur_row["unit"] or deduct_unit
    cur_phase = cur_row["measure_phase"] or phase

    if cur_phase != phase:
        return {"pantry_id": pantry_id, "status": "phase-mismatch", "expected": cur_phase, "given": phase}

    need_canon = to_canonical(float(deduct_value), deduct_unit, phase)
    cur_canon = to_canonical(cur_qty, cur_unit, phase)
    new_canon = max(0.0, cur_canon - need_canon)
    new_qty = round(from_canonical(new_canon, cur_unit, phase), 3)

    execute_with_retry(conn, "UPDATE pantry SET quantity = ? WHERE id = ?", (new_qty, pantry_id))
    execute_with_retry(
        conn,
        """
        INSERT INTO pantry_txns (pantry_id, delta, unit, reason, ref_type, ref_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (pantry_id, -float(deduct_value), deduct_unit, reason, ref_type, ref_id),
    )

    return {"pantry_id": pantry_id, "status": "deducted", "old_qty": cur_qty, "new_qty": new_qty, "unit": cur_unit}


def expand_menu_ingredients(conn: sqlite3.Connection, menu_id: int) -> List[sqlite3.Row]:
    return query_all(
        conn,
        """
        SELECT r.id AS recipe_id, ri.ingredient, ri.qty_value, ri.qty_unit, ri.measure_phase
        FROM menu_plan m
        JOIN recipes r ON r.id = m.recipe_id
        JOIN recipe_ingredients ri ON ri.recipe_id = r.id
        WHERE m.id = ?
        """,
        (menu_id,),
    )


def apply_menu_consumption(menu_id: int, conn: Optional[sqlite3.Connection] = None) -> Dict[str, Any]:
    own = False
    if conn is None:
        conn, own = get_conn(), True

    touched: Set[int] = set()
    report: Dict[str, Any] = {"menu_id": menu_id, "deducted": [], "unmatched": []}
    with transaction(conn) as tconn:
        items = expand_menu_ingredients(tconn, menu_id)

        for row in items:
            ing_name = row["ingredient"]
            qv = row["qty_value"]
            qu = (row["qty_unit"] or "").lower()
            phase = (row["measure_phase"] or unit_phase(qu))

            if qv is None or not qu or phase not in (PHASE_DRY, PHASE_WET):
                report["unmatched"].append(
                    {"ingredient": ing_name, "reason": "missing-or-unknown-unit/phase", "qty_value": qv, "qty_unit": qu}
                )
                continue

            pantry = _find_best_pantry_match(tconn, ing_name)
            if not pantry:
                report["unmatched"].append({"ingredient": ing_name, "reason": "no-pantry-match"})
                continue

            pid = int(pantry["id"])
            p_phase = pantry["measure_phase"]
            if p_phase and p_phase != phase:
                report["unmatched"].append(
                    {"ingredient": ing_name, "reason": "phase-mismatch", "pantry_phase": p_phase, "recipe_phase": phase}
                )
                continue

            result = _deduct_pantry_quantity(
                tconn,
                pantry_id=pid,
                deduct_value=float(qv),
                deduct_unit=qu,
                phase=phase,
                reason="menu_done",
                ref_type="menu",
                ref_id=menu_id,
            )

            if result.get("status") == "deducted":
                report["deducted"].append({"ingredient": ing_name, **result})
                touched.add(pid)
            else:
                report["unmatched"].append({"ingredient": ing_name, "reason": result.get("status", "unknown")})

        execute_with_retry(tconn, "UPDATE menu_plan SET usage_applied = 1 WHERE id = ?", (menu_id,))
        safe_commit(tconn)

    try:
        shopping_svc.recompute_for_ids(touched, conn=conn)
    except Exception:
        pass

    if own:
        conn.close()

    return report


def apply_pending(conn: Optional[sqlite3.Connection] = None) -> Dict[str, int]:
    own = False
    if conn is None:
        conn, own = get_conn(), True

    rows = query_all(conn, "SELECT id FROM menu_plan WHERE COALESCE(usage_applied,0) = 0 ORDER BY date, id")
    processed = 0
    total_deducted = 0
    total_unmatched = 0

    for r in rows:
        rep = apply_menu_consumption(int(r["id"]), conn=conn)
        processed += 1
        total_deducted += len(rep.get("deducted", []))
        total_unmatched += len(rep.get("unmatched", []))

    if own:
        conn.close()

    return {"processed_entries": processed, "deducted": total_deducted, "unmatched": total_unmatched}
