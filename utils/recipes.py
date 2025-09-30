# path: utils/recipes.py
from __future__ import annotations

from dataclasses import dataclass
import json
import sqlite3
from typing import Any, Iterable, Sequence
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from .settings import get_setting
from . import importers

try:
    from . import edamam as _edamam
except Exception:
    _edamam = None
try:
    from . import spoonacular as _spoon
except Exception:
    _spoon = None


@dataclass
class Recipe:
    title: str
    ingredients: list[dict[str, Any]]
    instructions: str
    url: str
    tags: str
    json: str
    source: str


class Provider:
    name: str = "provider"
    def available(self, conn: sqlite3.Connection) -> bool: return True
    def search(self, conn: sqlite3.Connection, query: str, n: int) -> list[Recipe]: raise NotImplementedError


class SpoonacularProvider(Provider):
    name = "spoonacular"
    def available(self, conn: sqlite3.Connection) -> bool:
        return bool(get_setting(conn, "spoonacular_api_key", "")) and (_spoon is not None)
    def search(self, conn: sqlite3.Connection, query: str, n: int) -> list[Recipe]:
        if _spoon is None:
            return []
        hits = _spoon.search_recipes(conn, query, n) or []
        out: list[Recipe] = []
        for h in hits:
            out.append(Recipe(
                title=h.get("title") or "Untitled",
                ingredients=h.get("ingredients") or [],
                instructions=h.get("instructions") or "",
                url=h.get("url") or "",
                tags=h.get("tags") or "",
                json=(h.get("json") if isinstance(h.get("json"), str) else json.dumps(h.get("json") or {})),
                source=self.name,
            ))
        return out


class EdamamProvider(Provider):
    name = "edamam"
    def available(self, conn: sqlite3.Connection) -> bool:
        return bool(get_setting(conn, "edamam_app_id", "")) and bool(get_setting(conn, "edamam_app_key","")) and (_edamam is not None)
    def search(self, conn: sqlite3.Connection, query: str, n: int) -> list[Recipe]:
        if _edamam is None:
            return []
        hits = _edamam.search_recipes(conn, query, n) or []
        out: list[Recipe] = []
        for h in hits:
            out.append(Recipe(
                title=h.get("title") or "Untitled",
                ingredients=h.get("ingredients") or [],
                instructions=h.get("instructions") or "",
                url=h.get("url") or "",
                tags=h.get("tags") or "",
                json=(h.get("json") if isinstance(h.get("json"), str) else json.dumps(h.get("json") or {})),
                source=self.name,
            ))
        return out


_TRACKING_KEYS = {"utm_source","utm_medium","utm_campaign","utm_term","utm_content","utm_name","utm_id","utm_reader","ck_subscriber_id","mc_cid","mc_eid"}

def _normalize_url(u: str) -> str:
    if not u: return ""
    try:
        p = urlparse(u)
        q = [(k,v) for (k,v) in parse_qsl(p.query, keep_blank_values=False) if k not in _TRACKING_KEYS]
        canon = p._replace(scheme=p.scheme.lower() or "https", netloc=(p.netloc or "").lower(), query=urlencode(q, doseq=True), fragment="")
        s = urlunparse(canon)
        if s.endswith("/") and len(canon.path) > 1: s = s[:-1]
        return (canon.netloc + canon.path + ("?" + canon.query if canon.query else "")).lower()
    except Exception:
        return u.strip().lower()

def _key_for(r: Recipe) -> tuple[str, str]:
    return (_normalize_url(r.url), (r.title or "").strip().lower())

def dedupe(recipes: Iterable[Recipe]) -> list[Recipe]:
    seen_url: set[str] = set(); seen_title: set[str] = set(); out: list[Recipe] = []
    for r in recipes:
        ukey, tkey = _key_for(r)
        if ukey and ukey in seen_url: continue
        if not ukey and tkey and tkey in seen_title: continue
        out.append(r)
        if ukey: seen_url.add(ukey)
        if tkey: seen_title.add(tkey)
    return out

def available_providers(conn: sqlite3.Connection) -> list[Provider]:
    return [p for p in [SpoonacularProvider(), EdamamProvider()] if p.available(conn)]

def search_all(conn: sqlite3.Connection, query: str, *, total: int = 20) -> list[Recipe]:
    provs = available_providers(conn)
    if not provs: return []
    n_each = max(1, total // len(provs))
    all_hits: list[Recipe] = []
    for p in provs:
        try:
            all_hits.extend(p.search(conn, query, n_each))
        except Exception:
            continue
    return dedupe(all_hits)[:total]

def scrape_url(conn: sqlite3.Connection, url: str) -> Recipe:
    data = importers.scrape_recipe(url)
    return Recipe(
        title=data.get("title") or "Untitled",
        ingredients=data.get("ingredients") or [],
        instructions=data.get("instructions") or "",
        url=data.get("url") or url,
        tags=data.get("tags") or "",
        json=(data.get("json") if isinstance(data.get("json"), str) else json.dumps(data.get("json") or {})),
        source=data.get("source") or "web",
    )
