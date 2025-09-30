# path: tests/test_pantry_workflow.py
import os
import sqlite3
import tempfile
import tkinter as tk

import pytest

# UI target: current panel you shared (already color-tags 'low' rows)
from panels.pantry_panel import PantryPanel  # :contentReference[oaicite:2]{index=2}
from services import pantry as pantry_svc
from services import shopping as shopping_svc

# Use your project modules
from utils import db as dbmod
from utils.migrations import migrate


@pytest.fixture(scope="function")
def temp_db_path(monkeypatch):
    """Point the app DB to a temp file and run migrations."""
    tmpdir = tempfile.TemporaryDirectory()
    db_path = os.path.join(tmpdir.name, "test.db")
    # Point utils.db at our temp file
    monkeypatch.setattr(dbmod, "_DB_PATH", db_path, raising=True)
    # Bootstrap schema
    conn = dbmod.get_conn()
    migrate(conn)
    conn.close()
    yield db_path
    tmpdir.cleanup()


def _count_open_shopping(conn: sqlite3.Connection) -> int:
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM shopping_list WHERE COALESCE(status,'open')='open'")
        return int(cur.fetchone()[0])
    except Exception:
        return 0


def _get_tree_first_tags(panel: PantryPanel):
    tv = panel.tree
    kids = tv.get_children()
    if not kids:
        return tuple()
    return tuple(tv.item(kids[0], "tags"))


def test_add_edit_delete_recompute_and_row_color(temp_db_path):
    # 1) Insert a low-stock pantry item (quantity <= threshold) → recompute → shopping item appears
    item = {
        "name": "Rice",
        "brand": "Lundberg",
        "category": "Pantry",
        "subcategory": "Grains",
        "quantity": 0.0,
        "unit": "lb",
        "net_weight_value": 2.0,
        "net_weight_unit": "lb",
        "measure_phase": None,  # inferred elsewhere; not needed for threshold rule
        "threshold": 1.0,
        "notes": "fixture",
    }
    pid = pantry_svc.insert(item)

    # Recompute shopping from thresholds
    shopping_svc.recompute_from_thresholds()

    # Assert an 'open' shopping row exists
    conn = dbmod.get_conn()
    assert _count_open_shopping(conn) == 1
    conn.close()

    # 2) UI: row should be 'low' (red-tinted) initially; after lowering threshold, should flip to 'ok'
    # Try to build the panel in a headless-safe way
    try:
        root = tk.Tk()
        root.withdraw()
    except Exception:
        pytest.skip("Tk not available in this environment")

    panel = PantryPanel(
        root
    )  # current panel uses ttk.Frame signature (no app required) :contentReference[oaicite:3]{index=3}
    panel.refresh()
    initial_tags = _get_tree_first_tags(panel)
    assert "low" in initial_tags  # was low-stock

    # Lower threshold to 0 (i.e., not low anymore) and refresh UI
    pantry_svc.update(pid, {**item, "threshold": 0.0})
    panel.refresh()
    after_tags = _get_tree_first_tags(panel)
    assert "low" not in after_tags  # should now be normal colored (e.g., 'ok' / zebra)

    # 3) Delete the pantry item → recompute again → should not crash, shopping remains at least as-is
    pantry_svc.delete_many([pid])
    shopping_svc.recompute_from_thresholds()
    conn = dbmod.get_conn()
    assert _count_open_shopping(conn) >= 1  # previously added row remains; recompute won't remove
    conn.close()

    # Cleanup Tk
    try:
        root.destroy()
    except Exception:
        pass
