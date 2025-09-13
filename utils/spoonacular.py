# path: utils/spoonacular.py
from __future__ import annotations
from typing import Any, Dict, List
import json
import requests
import sqlite3

from .settings import get_setting

BASE_URL = "https://api.spoonacular.com/recipes/complexSearch"

def _normalize(hit: Dict[str, Any]) -> Dict[str, Any]:
    ings = []
    for ing in (hit.get("extendedIngredients") or []):
        ings.append({
            "original": ing.get("original") or "",
            "name": ing.get("name") or "",
            "quantity": ing.get("amount"),
            "unit": ing.get("unit") or "",
        })
    return {
        "title": hit.get("title") or "Untitled",
        "ingredients": ings,
        "instructions": hit.get("instructions") or "",
        "url": hit.get("sourceUrl") or hit.get("spoonacularSourceUrl") or "",
        "tags": ", ".join(hit.get("diets") or []),
        "json": json.dumps({"source": "spoonacular", "raw": hit}, ensure_ascii=False),
    }

def search_recipes(conn: sqlite3.Connection, query: str, n: int = 10) -> List[Dict[str, Any]]:
    key = get_setting(conn, "spoonacular_api_key")
    if not key:
        raise RuntimeError("Missing Spoonacular API key. Set it in Settings or ENV SPOONACULAR_API_KEY.")
    params = {
        "apiKey": key,
        "query": query,
        "diet": "gluten free",
        "number": max(1, min(50, int(n or 10))),
        "addRecipeInformation": True,
    }
    r = requests.get(BASE_URL, params=params, timeout=15)
    r.raise_for_status()
    data = r.json() or {}
    return [_normalize(hit) for hit in (data.get("results") or [])][:n]
