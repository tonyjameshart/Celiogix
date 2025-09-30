# path: utils/importers.py
from __future__ import annotations

import json
import re
import urllib.request
from typing import Any, Iterable


def _fetch(url: str, *, timeout: int = 20) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; Celiogix/1.0)"
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def _iter_jsonld(html: str) -> Iterable[dict[str, Any]]:
    pattern = r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
    for m in re.finditer(pattern, html, flags=re.IGNORECASE | re.DOTALL):
        raw = m.group(1).strip()
        try:
            data = json.loads(raw)
            objs = data if isinstance(data, list) else [data]
        except Exception:
            try:
                raw2 = re.sub(r",(\s*[}\]])", r"\1", raw)
                data = json.loads(raw2)
                objs = data if isinstance(data, list) else [data]
            except Exception:
                continue
        for obj in objs:
            if isinstance(obj, dict):
                yield obj


def _is_recipe(obj: dict[str, Any]) -> bool:
    t = obj.get("@type")
    if isinstance(t, str): return t.lower() == "recipe"
    if isinstance(t, list): return any(isinstance(x, str) and x.lower() == "recipe" for x in t)
    return False


def _txt(x: Any) -> str:
    return "" if x is None else (x if isinstance(x, str) else str(x))


def _parse_instructions(instr: Any) -> str:
    if isinstance(instr, str):
        return instr.strip()
    out: list[str] = []
    if isinstance(instr, list):
        for i, step in enumerate(instr, start=1):
            if isinstance(step, str):
                text = step
            elif isinstance(step, dict):
                if step.get("@type") == "HowToSection":
                    name = _txt(step.get("name")).strip()
                    nested = _parse_instructions(step.get("itemListElement", []))
                    text = (name + ":\n" + nested) if name else nested
                else:
                    text = _txt(step.get("text") or step.get("name"))
            else:
                text = _txt(step)
            text = (text or "").strip()
            if text:
                out.append(f"{i}. {text}")
    return "\n".join(out).strip()


def _parse_ingredients(val: Any) -> list[dict[str, Any]]:
    items: list[str] = []
    if isinstance(val, list):
        for x in val:
            s = _txt(x).strip()
            if s:
                items.append(s)
    elif isinstance(val, str):
        items = [ln.strip() for ln in val.splitlines() if ln.strip()]
    return [{"original": s, "name": "", "quantity": None, "unit": ""} for s in items]


def scrape_recipe(url: str, *, timeout: int = 20) -> dict[str, Any]:
    html = _fetch(url, timeout=timeout)

    recipe_obj: dict[str, Any] | None = None
    for obj in _iter_jsonld(html):
        if _is_recipe(obj):
            recipe_obj = obj
            break
        graph = obj.get("@graph")
        if isinstance(graph, list):
            for node in graph:
                if isinstance(node, dict) and _is_recipe(node):
                    recipe_obj = node
                    break
        if recipe_obj:
            break

    if not recipe_obj:
        title = ""
        m = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
        if m:
            title = re.sub(r"\s+", " ", m.group(1)).strip()
        return {"title": title or "Untitled", "ingredients": [], "instructions": "", "url": url, "tags": "", "json": json.dumps({"parsed": False}), "source": "web"}

    name = _txt(recipe_obj.get("name")).strip() or "Untitled"
    ingredients = _parse_ingredients(recipe_obj.get("recipeIngredient") or recipe_obj.get("ingredients") or [])
    instructions = _parse_instructions(recipe_obj.get("recipeInstructions") or recipe_obj.get("instructions") or "")

    tags = ""
    kw = recipe_obj.get("keywords") or ""
    if isinstance(kw, str):
        parts = [t.strip() for t in re.split(r"[;,]", kw) if t.strip()]
        tags = ", ".join(parts)
    elif isinstance(kw, list):
        tags = ", ".join([_txt(t).strip() for t in kw if _txt(t).strip()])

    src = "web"
    pub = recipe_obj.get("publisher")
    if isinstance(pub, dict):
        src = _txt(pub.get("name") or "web") or "web"
    elif recipe_obj.get("author"):
        a = recipe_obj["author"]
        if isinstance(a, dict):
            src = _txt(a.get("name") or "web") or "web"
        elif isinstance(a, list) and a:
            src = _txt(a[0].get("name") if isinstance(a[0], dict) else a[0]) or "web"

    return {
        "title": name,
        "ingredients": ingredients,
        "instructions": instructions,
        "url": url,
        "tags": tags,
        "json": json.dumps({"ld": recipe_obj}, ensure_ascii=False),
        "source": src,
    }
