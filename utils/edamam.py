# path: utils/edamam.py
from __future__ import annotations

import json
import sqlite3
from typing import Any

import requests

from .settings import get_setting

SEARCH_URL = "https://api.edamam.com/search"


def _normalize(hit: dict[str, Any]) -> dict[str, Any]:
    recipe = hit.get("recipe") or {}
    ings = recipe.get("ingredients") or []
    norm_ings = []
    for ing in ings:
        norm_ings.append(
            {
                "original": ing.get("text") or "",
                "name": ing.get("food") or "",
                "quantity": ing.get("quantity"),
                "unit": ing.get("measure") or "",
            }
        )
    return {
        "title": recipe.get("label") or "Untitled",
        "ingredients": norm_ings,
        "instructions": "",  # Edamam doesn't return steps
        "url": recipe.get("url") or "",
        "tags": ", ".join(recipe.get("dietLabels") or []),
        "json": json.dumps({"source": "edamam", "raw": recipe}, ensure_ascii=False),
    }


def search_recipes(conn: sqlite3.Connection, query: str, n: int = 10) -> list[dict[str, Any]]:
    app_id = get_setting(conn, "edamam_app_id")
    app_key = get_setting(conn, "edamam_app_key")
    if not app_id or not app_key:
        raise RuntimeError(
            "Missing Edamam credentials. Set EDAMAM_APP_ID / EDAMAM_APP_KEY or use Settings."
        )
    params = {
        "q": query,
        "app_id": app_id,
        "app_key": app_key,
        "health": "gluten-free",
        "to": max(1, min(50, int(n or 10))),
    }
    r = requests.get(SEARCH_URL, params=params, timeout=15)
    r.raise_for_status()
    data = r.json() or {}
    return [_normalize(hit) for hit in (data.get("hits") or [])][:n]
