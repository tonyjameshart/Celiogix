# file: tests/test_db_cli.py
"""Pytest coverage for tools.db_cli.
Validates CLI behavior, schema init, and idempotent seeding.
"""

from __future__ import annotations

import importlib
import sqlite3
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def db_cli_module():
    """Import the CLI module once per session.
    This import doesn't require `utils/`; specific tests that need utils are skipped when absent.
    """
    return importlib.import_module("tools.db_cli")


@pytest.fixture()
def temp_db(tmp_path: Path) -> Path:
    return tmp_path / "app.db"


def has_utils() -> bool:
    """True if project has a `utils/` package alongside tests/tools."""
    return (PROJECT_ROOT / "utils").is_dir()


def test_no_flags_returns_2(db_cli_module):
    # No utils required; main([]) exits before touching deps.
    assert db_cli_module.main([]) == 2


@pytest.mark.skipif(not has_utils(), reason="utils/ not present; skip runtime tests")
def test_init_creates_db_file(db_cli_module, temp_db: Path):
    rc = db_cli_module.main(["--init-db", "--db", str(temp_db)])
    assert rc == 0
    assert temp_db.exists(), "DB file should be created"


@pytest.mark.skipif(not has_utils(), reason="utils/ not present; skip runtime tests")
def test_seed_idempotent(db_cli_module, temp_db: Path):
    # Ensure schema first
    assert db_cli_module.main(["--init-db", "--db", str(temp_db)]) == 0
    # First seed
    assert db_cli_module.main(["--seed", "--db", str(temp_db)]) == 0

    def count(table: str) -> int:
        con = sqlite3.connect(str(temp_db))
        try:
            return con.execute(f"SELECT COUNT(1) FROM {table}").fetchone()[0]
        finally:
            con.close()

    first = {
        t: count(t)
        for t in [
            "recipes",
            "menu_plan",
            "pantry",
            "shopping_list",
            "health_log",
        ]
    }

    # Second seed should not duplicate any rows
    assert db_cli_module.main(["--seed", "--db", str(temp_db)]) == 0
    second = {
        t: count(t)
        for t in [
            "recipes",
            "menu_plan",
            "pantry",
            "shopping_list",
            "health_log",
        ]
    }

    assert second == first, "Seeding should be idempotent"


# Negative test: if utils/ is missing, CLI should return code 4.
@pytest.mark.skipif(has_utils(), reason="utils/ present; skip negative import test")
def test_returns_4_when_utils_missing():
    # Import CLI module and force a fresh dependency load path.
    mod = importlib.import_module("tools.db_cli")

    # Reset cached deps if present, to force a re-check.
    if hasattr(mod, "_DEPS"):
        mod._DEPS = None  # type: ignore[attr-defined]

    rc = mod.main(["--init-db"])  # requires utils.*; should fail with 4
    assert rc == 4
