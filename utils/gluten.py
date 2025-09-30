# path: utils/gluten.py
from __future__ import annotations

from collections.abc import Iterable
import json
import re
from typing import Any

# Try to import your lexicon; fall back to reasonable defaults.
try:
    from .gf_lexicon import SAFE_TERMS as _SAFE_TERMS  # type: ignore[attr-defined]
except Exception:
    _SAFE_TERMS = set()
try:
    from .gf_lexicon import RISK_TERMS as _RISK_TERMS  # type: ignore[attr-defined]
except Exception:
    _RISK_TERMS = set()
try:
    from .gf_lexicon import MAYBE_TERMS as _MAYBE_TERMS  # type: ignore[attr-defined]
except Exception:
    _MAYBE_TERMS = set()

# Sensible defaults if lexicon doesn't define them
if not _RISK_TERMS:
    _RISK_TERMS = {
        "wheat",
        "barley",
        "rye",
        "malt",
        "spelt",
        "farro",
        "durum",
        "semolina",
        "graham",
        "triticale",
        "seitan",
        "kamut",
        "bulgur",
        "couscous",
        "einkorn",
        "wheat starch",
        "barley malt",
        "brewer's yeast",
        "brewers yeast",
    }
if not _MAYBE_TERMS:
    _MAYBE_TERMS = {
        "oats",
        "oat",
        "oat flour",
        "miso",
        "soy sauce",
        "maltodextrin",
        "natural flavors",
        "beer",
        "ale",
        "stout",
        "vinegar malt",
    }
if not _SAFE_TERMS:
    _SAFE_TERMS = {
        "gluten-free",
        "gluten free",
        "certified gluten-free",
        "certified gluten free",
        "gf",
        "no gluten",
        "wheat-free",
        "wheat free",
        "tamari (gluten-free)",
        "rice",
        "corn",
    }

# Phrase patterns with strong semantics
_PATTERNS_RISK = [
    re.compile(r"\bcontains\b.*\b(wheat|barley|rye|malt|gluten)\b", re.I),
    re.compile(r"\bmade with\b.*\b(wheat|barley|rye|malt)\b", re.I),
]
_PATTERNS_SAFE = [
    re.compile(r"\b(certified\s+)?gluten[-\s]?free\b", re.I),
]


def _norm(s: Any) -> str:
    return (str(s or "")).strip().lower()


def _match_terms(text: str, terms: Iterable[str]) -> list[str]:
    t = _norm(text)
    hits: list[str] = []
    for term in terms:
        tt = term.lower()
        if tt and tt in t:
            hits.append(term)
    return hits


def classify_text(text: str) -> dict[str, Any]:
    """
    Classify arbitrary text (labels, notes, descriptions).
    Returns: {'flag': 'SAFE'|'RISK'|'UNKNOWN', 'tags': [...], 'evidence': {...}}
    """
    t = _norm(text)
    if not t:
        return {"flag": "UNKNOWN", "tags": [], "evidence": {}}

    # Strong phrases first
    for p in _PATTERNS_RISK:
        if p.search(t):
            return {"flag": "RISK", "tags": ["contains"], "evidence": {"pattern": p.pattern}}

    safe_phrase = any(p.search(t) for p in _PATTERNS_SAFE)

    risk_hits = _match_terms(t, _RISK_TERMS)
    maybe_hits = _match_terms(t, _MAYBE_TERMS)
    safe_hits = _match_terms(t, _SAFE_TERMS)

    if risk_hits:
        return {
            "flag": "RISK",
            "tags": sorted({h.upper() for h in risk_hits}),
            "evidence": {"risk_terms": risk_hits},
        }
    if safe_phrase or safe_hits:
        tags = sorted(
            {"CERTIFIED GF" if safe_phrase else None} | {h.upper() for h in safe_hits} - {None}
        )
        return {
            "flag": "SAFE",
            "tags": tags,
            "evidence": {"safe_terms": safe_hits, "safe_phrase": safe_phrase},
        }
    if maybe_hits:
        return {
            "flag": "UNKNOWN",
            "tags": [f"CHECK:{h.upper()}" for h in sorted(set(maybe_hits))],
            "evidence": {"maybe_terms": maybe_hits},
        }
    return {"flag": "UNKNOWN", "tags": [], "evidence": {}}


def classify_ingredients(ingredients: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """
    Classify based on a list of provider-style ingredient dicts:
      [{'name': 'soy sauce', 'quantity': 1, 'unit': 'tbsp', 'original': '1 tbsp soy sauce'}, ...]
    """
    blob = " | ".join(
        [
            " ".join(
                [
                    _norm(ing.get("original")),
                    _norm(ing.get("name")),
                    _norm(ing.get("unit")),
                ]
            )
            for ing in (ingredients or [])
        ]
    )
    return classify_text(blob)


def classify_pantry_data(data: dict[str, Any]) -> dict[str, Any]:
    """
    Classify a pantry item dict: combines name/brand/category/subcategory/tags/notes into one signal.
    Returns {'flag': ..., 'tags': [...]}.
    """
    parts = [
        data.get("name"),
        data.get("brand"),
        data.get("category"),
        data.get("subcategory"),
        data.get("tags"),
        data.get("notes"),
    ]
    return classify_text(" | ".join(_norm(p) for p in parts if p))


def classify_recipe_record(row: dict[str, Any]) -> dict[str, Any]:
    """
    Classify a recipe DB row — prefers parsed 'ingredients' list, falls back to provider 'json'.
    """
    ings = None
    try:
        if isinstance(row.get("ingredients"), str) and row["ingredients"].strip():
            ings = json.loads(row["ingredients"])
        elif isinstance(row.get("ingredients"), list):
            ings = row["ingredients"]
    except Exception:
        ings = None
    if ings:
        return classify_ingredients(ings)

    # Fallback: inspect provider JSON if present
    try:
        raw = (
            json.loads(row.get("json"))
            if isinstance(row.get("json"), str)
            else (row.get("json") or {})
        )
    except Exception:
        raw = {}
    # Spoonacular extendedIngredients
    ext = (raw.get("raw") or {}).get("extendedIngredients") or raw.get("extendedIngredients")
    if isinstance(ext, list):
        return classify_ingredients(ext)
    # Edamam recipe.ingredients
    rec = (raw.get("raw") or {}).get("recipe") or raw.get("recipe") or {}
    eda = rec.get("ingredients")
    if isinstance(eda, list):
        return classify_ingredients(eda)
    return {"flag": "UNKNOWN", "tags": [], "evidence": {}}


# ---------------------------
# DB helpers (optional use)
# ---------------------------
def apply_flag_to_pantry_row(existing_flag: str, suggested_flag: str) -> str:
    """
    Don't override explicit user decisions. Only fill when empty/UNKNOWN.
    """
    ex = (existing_flag or "").strip().upper()
    sug = (suggested_flag or "").strip().upper()
    if ex in {"SAFE", "RISK"}:
        return ex
    return sug or (ex or "UNKNOWN")


def autotag_pantry_item(data: dict[str, Any]) -> dict[str, Any]:
    """
    Return a copy of data with gf_flag/tags enriched, but never clobbering existing explicit flags.
    """
    res = classify_pantry_data(data)
    out = dict(data)
    out["gf_flag"] = apply_flag_to_pantry_row(out.get("gf_flag", ""), res["flag"])
    # merge tags (preserve original order roughly)
    orig_tags = [t.strip() for t in (out.get("tags") or "").split(",") if t.strip()]
    new_tags = [t for t in (res.get("tags") or []) if t and t not in orig_tags]
    if new_tags:
        out["tags"] = ", ".join(orig_tags + new_tags)
    return out
