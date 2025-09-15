# utils/db_utils.py
from __future__ import annotations
import re, sqlite3
from typing import Sequence, List, Tuple

def _referencing_children(conn: sqlite3.Connection, parent_table: str) -> List[Tuple[str, str]]:
    """
    Find tables/columns that reference `parent_table` via FOREIGN KEY ... REFERENCES parent_table(...).
    Returns [(child_table, child_fk_col), ...]
    """
    rows = conn.execute(
        "SELECT name, sql FROM sqlite_master WHERE type='table' AND sql LIKE ?",
        (f'%REFERENCES {parent_table}%',)
    ).fetchall()
    pat = re.compile(r'(\w+)[^,]*\sREFERENCES\s+' + re.escape(parent_table) + r'\s*\(\s*(\w+)\s*\)', re.I)
    refs: List[Tuple[str, str]] = []
    for name, sql in rows:
        # A table can have multiple FKs to the same parent; capture them all
        for col, _parent_col in pat.findall(sql or ""):
            refs.append((name, col))
    return refs

def delete_with_dependents(conn: sqlite3.Connection, parent_table: str, parent_id_col: str, ids: Sequence[int]) -> int:
    """
    Manually cascade delete: delete from all child tables that FK-reference the parent, then delete the parent.
    Returns number of parent rows deleted.
    """
    if not ids:
        return 0
    qs = ",".join("?" * len(ids))
    with conn:  # atomic transaction
        conn.execute("PRAGMA foreign_keys=ON")
        for child_table, child_fk_col in _referencing_children(conn, parent_table):
            conn.execute(f"DELETE FROM {child_table} WHERE {child_fk_col} IN ({qs})", ids)
        cur = conn.execute(f"DELETE FROM {parent_table} WHERE {parent_id_col} IN ({qs})", ids)
        return cur.rowcount if cur.rowcount is not None else conn.execute("SELECT changes()").fetchone()[0]
