# path: utils/recipes.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
import json
import sqlite3
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

from .settings import get_setting

# Optional imports (kept lazy so missing providers don't crash the app)
try:
    from . import edamam as _edamam
except Exception:
    _edamam = None  # type: ignore[assignment]
try:
    from . import spoonacular as _spoon
except Exception:
    _spoon = None  # type: ignore[assignment]


@dataclass
class Recipe:
    """Normalized recipe payload used by the UI and storage."""
    title: str
    ingredients: List[Dict[str, Any]]
    instructions: str
    url: str
    tags: str
    json: str    # original provider JSON, serialized
    source: str  # 'edamam' | 'spoonacular' | ...

    def as_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "ingredients": self.ingredients,
            "instructions": self.instructions,
            "url": self.url,
            "tags": self.tags,
            "json": self.json,
        }


# -------------------------
# Provider adapters
# -------------------------

class Provider:
    name: str = "provider"

    def available(self, conn: sqlite3.Connection) -> bool:  # override if needed
        return True

    def search(self, conn: sqlite3.Connection, query: str, n: int) -> List[Recipe]:  # override
        raise NotImplementedError


class SpoonacularProvider(Provider):
    name = "spoonacular"

    def available(self, conn: sqlite3.Connection) -> bool:
        return bool(get_setting(conn, "spoonacular_api_key", "")) and (_spoon is not None)

    def search(self, conn: sqlite3.Connection, query: str, n: int) -> List[Recipe]:
        if _spoon is None:
            return []
        hits = _spoon.search_recipes(conn, query, n)  # expected dicts
        out: List[Recipe] = []
        for h in hits or []:
            out.append(Recipe(
                title=h.get("title") or "Untitled",
                ingredients=h.get("ingredients") or [],
                instructions=h.get("instructions") or "",
                url=h.get("url") or "",
                tags=h.get("tags") or "",
                json=h.get("json") if isinstance(h.get("json"), str) else json.dumps(h.get("json") or {}),
                source=self.name,
            ))
        return out


class EdamamProvider(Provider):
    name = "edamam"

    def available(self, conn: sqlite3.Connection) -> bool:
        have_id = bool(get_setting(conn, "edamam_app_id", ""))
        have_key = bool(get_setting(conn, "edamam_app_key", ""))
        return have_id and have_key and (_edamam is not None)

    def search(self, conn: sqlite3.Connection, query: str, n: int) -> List[Recipe]:
        if _edamam is None:
            return []
        hits = _edamam.search_recipes(conn, query, n)  # expected dicts
        out: List[Recipe] = []
        for h in hits or []:
            out.append(Recipe(
                title=h.get("title") or "Untitled",
                ingredients=h.get("ingredients") or [],
                instructions=h.get("instructions") or "",
                url=h.get("url") or "",
                tags=h.get("tags") or "",
                json=h.get("json") if isinstance(h.get("json"), str) else json.dumps(h.get("json") or {}),
                source=self.name,
            ))
        return out


# -------------------------
# Aggregation & de-dup
# -------------------------

_TRACKING_KEYS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "utm_name", "utm_id", "utm_reader", "ck_subscriber_id", "mc_cid", "mc_eid",
}

def _normalize_url(u: str) -> str:
    """Normalize URL for dedupe: strip tracking, lowercase host, ignore fragments."""
    if not u:
        return ""
    try:
        p = urlparse(u)
        # remove tracking params
        q = [(k, v) for (k, v) in parse_qsl(p.query, keep_blank_values=False) if k not in _TRACKING_KEYS]
        # lowercase netloc, drop fragment
        canon = p._replace(
            scheme=p.scheme.lower() or "https",
            netloc=(p.netloc or "").lower(),
            query=urlencode(q, doseq=True),
            fragment="",
        )
        # normalize trailing slash
        s = urlunparse(canon)
        if s.endswith("/") and len(canon.path) > 1:
            s = s[:-1]
        # ignore scheme for equality; compare from netloc onward
        return (canon.netloc + canon.path + ("?" + canon.query if canon.query else "")).lower()
    except Exception:
        return u.strip().lower()

def _key_for(r: Recipe) -> Tuple[str, str]:
    ukey = _normalize_url(r.url)
    tkey = (r.title or "").strip().lower()
    return (ukey, tkey)

def dedupe(recipes: Iterable[Recipe]) -> List[Recipe]:
    """De-duplicate by normalized URL, then by case-insensitive title."""
    seen_url: set[str] = set()
    seen_title: set[str] = set()
    out: List[Recipe] = []
    for r in recipes:
        ukey, tkey = _key_for(r)
        if ukey and ukey in seen_url:
            continue
        if not ukey and tkey and tkey in seen_title:
            continue
        out.append(r)
        if ukey:
            seen_url.add(ukey)
        if tkey:
            seen_title.add(tkey)
    return out


def available_providers(conn: sqlite3.Connection) -> List[Provider]:
    """Return providers that are usable given current settings."""
    providers: List[Provider] = [SpoonacularProvider(), EdamamProvider()]
    return [p for p in providers if p.available(conn)]


def search_all(
    conn: sqlite3.Connection,
    query: str,
    *,
    total: int = 20,
    per_provider: Optional[int] = None,
    providers: Optional[Sequence[Provider]] = None,
    deduplicate: bool = True,
) -> List[Recipe]:
    """
    Query all available providers and return a unified, optionally de-duplicated list.

    Args:
      total: approximate total results desired (split across providers)
      per_provider: override for results per provider
      providers: explicit providers list; defaults to available_providers()
    """
    provs = list(providers or available_providers(conn))
    if not provs:
        return []

    n_each = per_provider or max(1, total // len(provs))
    all_hits: List[Recipe] = []
    for p in provs:
        try:
            all_hits.extend(p.search(conn, query, n_each))
        except Exception:
            # Defensive: provider failure shouldn't kill the search
            # (Log this in your app logger if desired)
            continue

    if deduplicate:
        all_hits = dedupe(all_hits)

    # If we undershot total due to dedupe, that's fine; order is provider order
    return all_hits[:total]
