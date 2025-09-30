# File: utils/inventory_engine.py
# Description: Applies menu-based recipe consumption to pantry stock and auto-adds items to the shopping
#              list when remaining Net. weight crosses a threshold. Safe to run repeatedly (idempotent via usage_applied).

from __future__ import annotations

import datetime as _dt
from typing import Any

from .units import convert_amount

# ---------- Shopping table helpers ----------


def _get_table_cols(db, table: str) -> set[str]:
    cur = db.cursor()
    return {c["name"] for c in cur.execute(f"PRAGMA table_info({table})").fetchall()}


def _shopping_table(db) -> str:
    cur = db.cursor()
    for name in ("shopping_list", "shopping_items"):
        if cur.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
        ).fetchone():
            return name
    # Create default
    name = "shopping_list"
    cur.execute(
        f"""
      CREATE TABLE IF NOT EXISTS {name} (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        brand TEXT,
        quantity REAL DEFAULT 1.0,
        unit TEXT,
        category TEXT,
        notes TEXT,
        store TEXT,
        status TEXT DEFAULT 'pending',
        linked_pantry_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    """
    )
    db.commit()
    return name


def _map_cols(cols: set[str]) -> dict[str, str | None]:
    def first(*xs):
        return next((x for x in xs if x in cols), None)

    return {
        "id": first("id", "rowid"),
        "name": first("name", "item", "title"),
        "brand": first("brand"),
        "quantity": first("quantity", "qty", "amount", "count"),
        "unit": first("unit", "units"),
        "category": first("category", "cat"),
        "notes": first("notes", "note", "description", "desc"),
        "store": first("store", "shop", "market"),
        "status": first("status", "state"),
        "linked_pantry_id": first("linked_pantry_id", "pantry_id", "source_id"),
    }


def _adapt_payload(m: dict[str, str | None], payload: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in payload.items():
        col = m.get(k)
        if col:
            out[col] = v
    return out


def _merge_or_insert_shopping(db, payload: dict[str, Any]) -> None:
    """Merge on linked_pantry_id if present, else on name(+unit). Increment quantity if present."""
    table = _shopping_table(db)
    cols = _get_table_cols(db, table)
    m = _map_cols(cols)
    cur = db.cursor()

    wheres, params = [], []
    if m["linked_pantry_id"] and payload.get("linked_pantry_id") is not None:
        wheres.append(f"{m['linked_pantry_id']}=?")
        params.append(int(payload["linked_pantry_id"]))
    elif m["name"]:
        wheres.append(f"{m['name']}=?")
        params.append(payload.get("name", ""))
        if m["unit"]:
            wheres.append(f"IFNULL({m['unit']},'')=?")
            params.append(payload.get("unit", "") or "")
    if m["status"]:
        wheres.append(f"IFNULL({m['status']},'pending') IN ('pending','')")
    where_sql = (" WHERE " + " AND ".join(wheres)) if wheres else ""

    # Fetch existing
    sel_cols = [m["id"] or "id"]
    alias_q = None
    if m["quantity"]:
        alias_q = "sl_qty"
        sel_cols.append(f"{m['quantity']} AS {alias_q}")
    row = cur.execute(
        f"SELECT {', '.join(sel_cols)} FROM {table}{where_sql}", tuple(params)
    ).fetchone()

    if row and m["quantity"]:
        try:
            inc = float(payload.get("quantity") or 1)
        except:
            inc = 1.0
        new_q = (row[alias_q] or 0) + inc
        cur.execute(
            f"UPDATE {table} SET {m['quantity']}=? WHERE {m['id']}=?", (new_q, row[m["id"] or "id"])
        )
        db.commit()
        return
    if row:
        return

    data = _adapt_payload(m, payload)
    if m["status"] and m["status"] not in data:
        data[m["status"]] = "pending"
    keys = ", ".join(data.keys())
    q = ", ".join(["?"] * len(data))
    cur.execute(f"INSERT INTO {table} ({keys}) VALUES ({q})", tuple(data.values()))
    db.commit()


# ---------- Pantry baseline / threshold ----------


def _ensure_baseline_for_item(db, pid: int) -> None:
    """If base_amount is NULL or less than current amount (restock), update it to current amount."""
    cur = db.cursor()
    row = cur.execute("SELECT amount, base_amount FROM pantry_items WHERE id=?", (pid,)).fetchone()
    if not row:
        return
    amt = float(row["amount"] or 0.0)
    base = row["base_amount"]
    if base is None or (amt > (base or 0)):
        cur.execute("UPDATE pantry_items SET base_amount=? WHERE id=?", (amt, pid))
        db.commit()


def _threshold_value(threshold: float | None, base_amount: float | None) -> float:
    """
    threshold in (0,1] => ratio of base_amount; >1 => absolute remaining.
    None/0 => no auto-add purely by threshold.
    """
    thr = float(threshold or 0.0)
    if 0 < thr <= 1.0:
        base = float(base_amount or 0.0)
        return base * thr
    return thr


def _clamp_nonneg(x: float) -> float:
    return x if x > 0 else 0.0


# ---------- Public API ----------


def sync_menu_consumption(db, up_to_date: str | None = None) -> dict[str, Any]:
    """
    Decrement pantry_items.amount by ingredient usage from scheduled menu_entries (pending only),
    then auto-add to shopping when remaining amount <= threshold (ratio or absolute).
    - up_to_date: YYYY-MM-DD; defaults to today.
    Returns summary dict.
    """
    today = up_to_date or _dt.date.today().isoformat()
    cur = db.cursor()

    # Pending menu entries up to date
    cur.execute(
        """
      SELECT id, date, recipe_id, COALESCE(servings,1) AS servings
      FROM menu_entries
      WHERE date <= ? AND COALESCE(usage_applied,0) = 0
      ORDER BY date, id
    """,
        (today,),
    )
    menu_rows = cur.fetchall()
    if not menu_rows:
        return {
            "processed_entries": 0,
            "updated_items": 0,
            "skipped_ingredients": 0,
            "auto_added": 0,
        }

    def get_pantry(pid: int):
        return cur.execute("SELECT * FROM pantry_items WHERE id=?", (pid,)).fetchone()

    updated_items = 0
    skipped_ingredients = 0
    auto_added = 0

    for me in menu_rows:
        rid = me["recipe_id"]
        servings = float(me["servings"] or 1)

        # Ingredients (need qty + unit + linked_pantry_id)
        ing = cur.execute(
            """
          SELECT id, recipe_id, name, COALESCE(qty,0) AS qty, unit, linked_pantry_id
          FROM recipe_ingredients
          WHERE recipe_id=?
        """,
            (rid,),
        ).fetchall()

        for ing_row in ing:
            pid = ing_row["linked_pantry_id"]
            if pid is None:
                skipped_ingredients += 1
                continue
            pantry = get_pantry(pid)
            if not pantry:
                skipped_ingredients += 1
                continue

            # Ensure baseline for ratio thresholds
            _ensure_baseline_for_item(db, pid)

            # Convert ingredient qty to pantry unit
            req_qty = float(ing_row["qty"] or 0.0) * servings
            req_unit = ing_row["unit"]
            pan_unit = pantry["unit"]
            conv, ok = convert_amount(req_qty, req_unit, pan_unit)
            if not ok or conv is None:
                # If both units empty/equal, treat as passthrough
                if (req_unit or "") == (pan_unit or ""):
                    conv = req_qty
                else:
                    skipped_ingredients += 1
                    continue

            remaining = float(pantry["amount"] or 0.0) - float(conv)
            remaining = _clamp_nonneg(remaining)
            cur.execute("UPDATE pantry_items SET amount=? WHERE id=?", (remaining, pid))
            updated_items += 1

            # Threshold evaluation
            thr_val = _threshold_value(pantry["threshold"], pantry["base_amount"])
            if thr_val > 0 and remaining <= thr_val:
                payload = {
                    "name": pantry["name"] or "Item",
                    "brand": pantry["brand"] or "",
                    "quantity": 1,  # buy one by default; adjust later if needed
                    "unit": pantry["unit"] or "",
                    "category": pantry["category"] or "",
                    "notes": f"Auto-added: remaining {remaining:g} {pantry['unit'] or ''} ≤ threshold {thr_val:g}",
                    "store": pantry["store"] if "store" in pantry.keys() else "",
                    "status": "pending",
                    "linked_pantry_id": int(pantry["id"]),
                }
                _merge_or_insert_shopping(db, payload)
                auto_added += 1

        # Mark usage as applied
        cur.execute("UPDATE menu_entries SET usage_applied=1 WHERE id=?", (me["id"],))
        db.commit()

    return {
        "processed_entries": len(menu_rows),
        "updated_items": updated_items,
        "skipped_ingredients": skipped_ingredients,
        "auto_added": auto_added,
    }
