# File: utils/categories.py — Robust loader/saver for category taxonomy with smart path discovery & adoption

from __future__ import annotations

import json
import os
import shutil

# Search order (first hit wins):
# 1) CC_CATEGORIES_PATH (env)
# 2) <cwd>/data/categories.json
# 3) <cwd>/categories.json
# 4) <project_root>/data/categories.json
# 5) <project_root>/categories.json
# On save, we always persist to <project_root>/data/categories.json

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
PERSIST_DIR = os.path.join(PROJECT_ROOT, "data")
PERSIST_PATH = os.path.join(PERSIST_DIR, "categories.json")


def _candidates() -> list[str]:
    env = os.environ.get("CC_CATEGORIES_PATH")
    cwd = os.getcwd()
    return [
        p
        for p in [
            env if env else None,
            os.path.join(cwd, "data", "categories.json"),
            os.path.join(cwd, "categories.json"),
            PERSIST_PATH,
            os.path.join(PROJECT_ROOT, "categories.json"),
        ]
        if p
    ]


def _read_raw(path: str) -> tuple[list[dict], dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    cats = data.get("categories", data if isinstance(data, list) else [])
    out: list[dict] = []
    for c in cats or []:
        if isinstance(c, dict):
            out.append({"name": c.get("name", ""), "subs": list(c.get("subs") or [])})
        else:
            out.append({"name": str(c), "subs": []})
    return out, data


def get_categories_path() -> str:
    for p in _candidates():
        if p and os.path.exists(p):
            return p
    return PERSIST_PATH


def load_categories() -> list[dict]:
    # Try candidates; adopt first hit into PERSIST_PATH if needed
    for p in _candidates():
        if p and os.path.exists(p):
            try:
                cats, _ = _read_raw(p)
                # adopt into data/ for stability
                if os.path.abspath(p) != os.path.abspath(PERSIST_PATH):
                    os.makedirs(PERSIST_DIR, exist_ok=True)
                    shutil.copyfile(p, PERSIST_PATH)
                return cats
            except Exception:
                continue
    # fallback: empty list (user can Manage… to add)
    return []


def save_categories(categories: list[dict]) -> str:
    os.makedirs(PERSIST_DIR, exist_ok=True)
    payload = {
        "version": 1,
        "categories": [
            {"name": c.get("name", ""), "subs": list(c.get("subs") or [])} for c in categories
        ],
    }
    with open(PERSIST_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return PERSIST_PATH
