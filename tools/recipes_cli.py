# file: tools/recipes_cli.py
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

from utils.db import get_connection
from utils.migrations import ensure_schema
from utils.recipe_import import import_recipes_from_json


def _import_file(path: Path, update: bool, db: str | None) -> list[int]:
    try:
        return import_recipes_from_json(path, update=update, db_path=db)
    except Exception as exc:  # why: keep batch import going
        print(f"[ERROR] {path}: {exc}", file=sys.stderr)
        return []


def main(argv: Iterable[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Bulk import recipes from JSON")
    p.add_argument("--json", nargs="*", help="JSON file(s) to import")
    p.add_argument("--dir", help="Directory to scan for .json files", default=None)
    p.add_argument("--db", help="Database file path (optional)")
    p.add_argument("--skip-update", action="store_true", help="Do not update existing entries")
    args = p.parse_args(list(argv) if argv is not None else None)

    files: list[Path] = []
    files += [Path(f) for f in (args.json or [])]
    if args.dir:
        root = Path(args.dir)
        files += list(root.rglob("*.json"))

    if not files:
        p.error("Provide --json file(s) or --dir directory with .json files")

    update = not args.skip_update
    total = 0
    ids: list[int] = []
    for f in files:
        batch = _import_file(f, update, args.db)
        total += len(batch)
        ids.extend(batch)
        print(f"Imported {len(batch)} from {f}")

    print(f"Done. Imported/updated: {total} recipe(s).")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
