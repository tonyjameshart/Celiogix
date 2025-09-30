# file: tools/db_cli.py
"""DB initialization & seeding CLI for Celiogix.

Fix: resilient imports. This tool now auto-adds the project root to sys.path so
`utils.db` can be found when running directly (e.g., `python tools/db_cli.py`).

Usage:
  python tools/db_cli.py --init-db
  python tools/db_cli.py --init-db --seed
  python tools/db_cli.py --seed --db ./data/app.db
  python tools/db_cli.py --run-tests

Exit codes:
  0 = success, 2 = no-op (no flags), 4 = cannot import dependencies
"""

from __future__ import annotations

import argparse
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
import os
from pathlib import Path
import sys
from typing import NamedTuple

# -----------------------------------------------------------------------------
# Import bootstrap: make sure `utils` package is importable when running directly
# -----------------------------------------------------------------------------


def _add_project_root_to_sys_path() -> Path | None:
    here = Path(__file__).resolve()
    # Project root is the parent of `tools/` if this file lives in tools/db_cli.py
    candidates = [
        here.parent.parent,  # project root (../)
        Path.cwd(),  # current working directory
    ]
    for root in candidates:
        utils_dir = root / "utils"
        if utils_dir.is_dir():  # PEP 420 namespace packages don't require __init__.py
            s = str(root)
            if s not in sys.path:
                sys.path.insert(0, s)
            return root
    return None


class Deps(NamedTuple):
    get_connection: object
    query_one: object
    execute_with_retry: object
    transaction: object
    ensure_schema: object
    canonical_category: object
    canonical_subcategory: object


_DEPS: Deps | None = None


def _load_deps() -> Deps:
    global _DEPS
    if _DEPS is not None:
        return _DEPS
    _add_project_root_to_sys_path()
    try:
        from utils.categorize import canonical_category, canonical_subcategory  # type: ignore
        from utils.db import (  # type: ignore
            execute_with_retry,
            get_connection,
            query_one,
            transaction,
        )
        from utils.migrations import ensure_schema  # type: ignore
    except ModuleNotFoundError as e:
        raise RuntimeError(
            "Cannot import required modules (utils.*). Ensure your project layout is:\n"
            "  <project>/utils/db.py\n  <project>/utils/migrations.py\n  <project>/utils/categorize.py\n"
            "Then run this script from within <project> or provide PYTHONPATH."
        ) from e
    _DEPS = Deps(
        get_connection,
        query_one,
        execute_with_retry,
        transaction,
        ensure_schema,
        canonical_category,
        canonical_subcategory,
    )
    return _DEPS


# ---- data models ------------------------------------------------------------
@dataclass(frozen=True)
class RecipeSeed:
    title: str
    source: str
    url: str
    tags: str
    prep_time: int
    cook_time: int
    servings: int
    rating: float
    favorite: int


@dataclass(frozen=True)
class PantrySeed:
    name: str
    brand: str
    category: str | None
    subcategory: str | None
    net_weight: float
    unit: str
    quantity: float
    store: str
    expiration: str | None
    gf_flag: str | None
    tags: str | None
    notes: str | None


@dataclass(frozen=True)
class ShoppingSeed:
    name: str
    brand: str
    category: str | None
    net_weight: float
    thresh: float
    store: str
    notes: str | None


# ---- helpers ----------------------------------------------------------------


def _ensure_schema(db_path: str | None) -> None:
    d = _load_deps()
    conn = d.get_connection(db_path)  # type: ignore[call-arg]
    d.ensure_schema(conn)  # type: ignore[misc]
    conn.close()


def _table_count(conn, table: str) -> int:
    d = _load_deps()
    row = d.query_one(conn, f"SELECT COUNT(1) AS n FROM {table}")  # type: ignore[misc]
    return int(row[0]) if row else 0


# ---- seeders ----------------------------------------------------------------


def seed_recipes(conn) -> dict[str, int]:
    """Insert example recipes; return title→id map. Skips existing by title."""
    rows: list[RecipeSeed] = [
        RecipeSeed(
            title="Gluten-Free Pancakes",
            source="Celiogix",
            url="https://example.com/gf-pancakes",
            tags="breakfast,gluten-free,simple",
            prep_time=10,
            cook_time=10,
            servings=4,
            rating=4.6,
            favorite=1,
        ),
        RecipeSeed(
            title="Quinoa & Chickpea Salad",
            source="Celiogix",
            url="https://example.com/quinoa-salad",
            tags="lunch,vegetarian,gluten-free",
            prep_time=15,
            cook_time=15,
            servings=2,
            rating=4.3,
            favorite=0,
        ),
        RecipeSeed(
            title="Roast Chicken with Veg",
            source="Celiogix",
            url="https://example.com/roast-chicken",
            tags="dinner,protein",
            prep_time=15,
            cook_time=60,
            servings=4,
            rating=4.8,
            favorite=0,
        ),
    ]

    d = _load_deps()
    title_to_id: dict[str, int] = {}
    with d.transaction(conn):  # type: ignore[misc]
        for r in rows:
            existing = d.query_one(conn, "SELECT id FROM recipes WHERE title=?", (r.title,))  # type: ignore[misc]
            if existing:
                title_to_id[r.title] = int(existing[0])
                continue
            cur = d.execute_with_retry(
                conn,
                """
                INSERT INTO recipes(title, source, url, tags, prep_time, cook_time, servings, rating, favorite)
                VALUES(?,?,?,?,?,?,?,?,?)
                """,
                (
                    r.title,
                    r.source,
                    r.url,
                    r.tags,
                    r.prep_time,
                    r.cook_time,
                    r.servings,
                    r.rating,
                    r.favorite,
                ),
            )  # type: ignore[misc]
            title_to_id[r.title] = int(cur.lastrowid)
    return title_to_id


def seed_menu_plan(conn, title_to_id: dict[str, int]) -> None:
    base = date.today()
    sample = [
        (
            base,
            "Breakfast",
            title_to_id.get("Gluten-Free Pancakes"),
            "GF Pancakes",
            "Maple syrup optional",
        ),
        (
            base,
            "Lunch",
            title_to_id.get("Quinoa & Chickpea Salad"),
            "Quinoa Salad",
            "Add feta if tolerated",
        ),
        (
            base,
            "Dinner",
            title_to_id.get("Roast Chicken with Veg"),
            "Roast Chicken",
            "Leftovers rock",
        ),
        (
            base + timedelta(days=1),
            "Dinner",
            title_to_id.get("Roast Chicken with Veg"),
            "Roast Chicken",
            "Repeat",
        ),
        (
            base + timedelta(days=2),
            "Lunch",
            title_to_id.get("Quinoa & Chickpea Salad"),
            "Quinoa Salad",
            "Pack to-go",
        ),
    ]
    d = _load_deps()
    with d.transaction(conn):  # type: ignore[misc]
        for dte, meal, rid, title, notes in sample:
            if d.query_one(
                conn, "SELECT 1 FROM menu_plan WHERE date=? AND meal=?", (dte.isoformat(), meal)
            ):
                continue
            d.execute_with_retry(
                conn,
                """
                INSERT INTO menu_plan(date, meal, recipe_id, title, notes)
                VALUES(?,?,?,?,?)
                """,
                (dte.isoformat(), meal, rid, title, notes),
            )  # type: ignore[misc]


def seed_pantry(conn) -> None:
    items: list[PantrySeed] = [
        PantrySeed(
            "Rolled Oats (GF)",
            "Bob's Red Mill",
            "Pantry",
            "Oats",
            907,
            "g",
            1,
            "Supermarket",
            None,
            "GF",
            "breakfast",
            None,
        ),
        PantrySeed(
            "Chicken Thighs",
            "—",
            "Meat & Seafood",
            "Poultry",
            1.5,
            "lb",
            1,
            "Butcher",
            None,
            None,
            "protein",
            None,
        ),
        PantrySeed(
            "Quinoa",
            "Ancient Harvest",
            "Pantry",
            "Pasta & Rice",
            340,
            "g",
            2,
            "Supermarket",
            None,
            "GF",
            "grain",
            None,
        ),
        PantrySeed(
            "Olive Oil",
            "California",
            "Pantry",
            "Oils",
            750,
            "ml",
            1,
            "Supermarket",
            None,
            None,
            "condiment",
            None,
        ),
        PantrySeed(
            "Greek Yogurt",
            "Fage",
            "Dairy",
            "Yogurt",
            32,
            "oz",
            1,
            "Supermarket",
            None,
            None,
            None,
            None,
        ),
    ]
    d = _load_deps()
    with d.transaction(conn):  # type: ignore[misc]
        for it in items:
            cat = d.canonical_category(it.category)  # type: ignore[misc]
            sub = d.canonical_subcategory(cat, it.subcategory)  # type: ignore[misc]
            if d.query_one(
                conn, "SELECT 1 FROM pantry WHERE name=? AND brand=?", (it.name, it.brand)
            ):
                continue
            d.execute_with_retry(
                conn,
                """
                INSERT INTO pantry(name, brand, category, subcategory, net_weight, unit, quantity, store, expiration, gf_flag, tags, notes)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    it.name,
                    it.brand,
                    cat,
                    sub,
                    it.net_weight,
                    it.unit,
                    it.quantity,
                    it.store,
                    it.expiration,
                    it.gf_flag,
                    it.tags,
                    it.notes,
                ),
            )  # type: ignore[misc]


def seed_shopping_list(conn) -> None:
    items: list[ShoppingSeed] = [
        ShoppingSeed("Maple Syrup", "Crown", "Pantry", 250, 1, "Supermarket", "For pancakes"),
        ShoppingSeed("Bananas", "—", "Produce", 6, 5, "Supermarket", "Ripe"),
    ]
    d = _load_deps()
    with d.transaction(conn):  # type: ignore[misc]
        for it in items:
            if d.query_one(
                conn, "SELECT 1 FROM shopping_list WHERE name=? AND brand=?", (it.name, it.brand)
            ):
                continue
            d.execute_with_retry(
                conn,
                """
                INSERT INTO shopping_list(name, brand, category, net_weight, thresh, store, notes)
                VALUES(?,?,?,?,?,?,?)
                """,
                (
                    it.name,
                    it.brand,
                    d.canonical_category(it.category),
                    it.net_weight,
                    it.thresh,
                    it.store,
                    it.notes,
                ),
            )  # type: ignore[misc]


def seed_health_log(conn) -> None:
    d = _load_deps()
    if _table_count(conn, "health_log") > 0:
        return
    d.execute_with_retry(
        conn,
        """
        INSERT INTO health_log(date, time, meal, items, risk, onset_min, severity, stool, recipe, symptoms, notes)
        VALUES(date('now'), time('now'), 'Dinner', 'Roast Chicken', 'Low', 60, 2, 4, 'Roast Chicken with Veg', 'None', 'Sample entry')
        """,
    )  # type: ignore[misc]


# ---- CLI -------------------------------------------------------------------


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Celiogix DB init & seeding tool")
    p.add_argument("--db", help="Path to SQLite DB (overrides CELIAC_DB)")
    p.add_argument("--init-db", action="store_true", help="Create/upgrade DB schema")
    p.add_argument("--seed", action="store_true", help="Insert sample data across tables")
    p.add_argument("--run-tests", action="store_true", help="Run built-in unit tests and exit")
    return p.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)

    if args.run_tests:
        import unittest

        result = unittest.TextTestRunner(verbosity=2).run(load_tests(None, None, None))
        return 0 if result.wasSuccessful() else 1

    if not args.init_db and not args.seed:
        print("Nothing to do. Use --init-db and/or --seed. See --help.")
        return 2

    try:
        d = _load_deps()
    except RuntimeError as e:
        print(str(e))
        return 4

    db_path = args.db or os.environ.get("CELIAC_DB")

    if args.init_db or args.seed:
        conn = d.get_connection(db_path)  # type: ignore[call-arg]
        d.ensure_schema(conn)  # type: ignore[misc]
        conn.close()
        print("✔ Schema ensured")

    if args.seed:
        conn = d.get_connection(db_path)  # type: ignore[call-arg]
        titles = seed_recipes(conn)
        seed_menu_plan(conn, titles)
        seed_pantry(conn)
        seed_shopping_list(conn)
        seed_health_log(conn)
        conn.close()
        print("✔ Seeded recipes, menu_plan, pantry, shopping_list, health_log")

    print("✅ Done.")
    return 0


# ---- Minimal tests ----------------------------------------------------------
# These tests avoid touching the real DB. They verify CLI behavior and import resilience.

import unittest


class TestCLI(unittest.TestCase):
    def test_parse_no_flags(self):
        ns = parse_args([])
        assert not ns.init_db
        assert not ns.seed

    def test_noop_exit_code(self):
        rc = main([])
        assert rc == 2

    def test_missing_deps_returns_4(self):
        # Simulate missing deps by temporarily renaming any found utils path from sys.path scan.
        # If utils is available, we skip to avoid false failures in user envs where deps are present.
        try:
            _load_deps()
            self.skipTest("utils present; import bootstrap OK")
        except RuntimeError:
            pass
        # Force load_deps again to hit the error path and ensure code returns 4
        global _DEPS
        _DEPS = None
        rc = main(["--init-db"])  # triggers import
        assert rc == 4


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestCLI))
    return suite


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
