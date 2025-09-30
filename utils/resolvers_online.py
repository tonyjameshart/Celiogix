# File: utils/resolvers_online.py — Barcode (UPC/EAN/GTIN) → product via OpenFoodFacts + gluten safety inference

from __future__ import annotations

import re
from typing import Any

import requests

try:
    # Optional: use your lexicon to enrich reasons
    from .gf_lexicon import risk_badges
except Exception:  # graceful fallback

    def risk_badges(text: str) -> list[str]:
        return []


from .gtin import classify, normalize

OFF_URL = "https://world.openfoodfacts.org/api/v2/product/{code}.json"
UA = {"User-Agent": "CeliacCulinary/1.0 (+local app)"}

RISK_TERMS = (
    "gluten",
    "wheat",
    "barley",
    "rye",
    "malt",
    "triticale",
    "spelt",
    "麦",
    "大麦",
    "ライ麦",
    "glutenhaltig",
    "gluten-containing",
)


def _parse_quantity(q: str | None) -> tuple[float | None, str | None]:
    """
    OFF 'quantity' is free text like '400 g', '12 oz', '1 lb', '3x125 g'
    Best-effort parse of the *total pack* amount.
    """
    if not q:
        return None, None
    s = q.lower().replace(",", ".")
    # pick last number+unit (handles '3 x 125 g' → 125 g)
    m = re.findall(r"(\d+(?:\.\d+)?)\s*([a-zµ]+)", s)
    if not m:
        return None, None
    val, unit = m[-1]
    try:
        return float(val), unit.strip()
    except Exception:
        return None, unit.strip()


def _infer_gf(product: dict[str, Any]) -> tuple[int | None, list[str]]:
    """
    Return (flag, reasons)
      flag: 1=GF yes, 0=contains gluten, None=unknown
    """
    reasons: list[str] = []
    labs: list[str] = [str(x).lower() for x in (product.get("labels_tags") or [])]
    alls: list[str] = [str(x).lower() for x in (product.get("allergens_tags") or [])]
    ingr_text = (product.get("ingredients_text") or product.get("ingredients_text_en") or "") or ""
    ingr_text_low = ingr_text.lower()

    if any("gluten-free" in t or "en:gluten-free" in t for t in labs):
        reasons.append("Label: gluten-free")
        # But sanity-check allergens: if OFF marked gluten allergen, prefer NO
        if any("gluten" in a or "en:gluten" in a for a in alls):
            reasons.append("Allergens contradict label (gluten)")
            return 0, reasons
        return 1, reasons

    if any("gluten" in a or "en:gluten" in a for a in alls):
        reasons.append("Allergens include gluten")
        return 0, reasons

    if any(t in ingr_text_low for t in RISK_TERMS):
        reasons.append("Ingredients mention gluten-grains")
        # Let lexicon badges contribute nuance for UI
        reasons += [b for b in risk_badges(ingr_text) if b]
        return 0, reasons

    # Unsure
    if ingr_text.strip():
        reasons.append("No gluten flags found in ingredients")
    return None, reasons


def lookup_barcode(code: str) -> dict[str, Any]:
    """
    Accepts UPC/EAN/GTIN strings (8/12/13/14 digits). Returns a normalized dict:
      {
        name, brand, category, amount, unit,
        ingredients, gf_reasons[], gluten_free_flag (1/0/None)
      }
    """
    c = normalize(code)
    if not classify(c):
        return {}
    url = OFF_URL.format(code=c)
    r = requests.get(url, headers=UA, timeout=12)
    r.raise_for_status()
    data = r.json()
    if not data or data.get("status") != 1:
        return {}

    p = data.get("product", {}) or {}
    name = p.get("product_name") or p.get("generic_name") or ""
    brand = (p.get("brands") or "").split(",")[0].strip()
    # try first categories_tags or top-level category string
    cat = ""
    if p.get("categories_tags"):
        cat = str(p["categories_tags"][0]).split(":")[-1].replace("-", " ").title()
    elif p.get("categories"):
        cat = str(p["categories"]).split(",")[0].strip()

    qty, unit = _parse_quantity(p.get("quantity"))
    gf_flag, gf_reasons = _infer_gf(p)
    ingredients = p.get("ingredients_text_en") or p.get("ingredients_text") or ""

    return {
        "name": name,
        "brand": brand,
        "category": cat,
        "amount": qty,
        "unit": unit,
        "ingredients": ingredients,
        "gf_reasons": gf_reasons,
        "gluten_free_flag": gf_flag,
        "raw": p,  # handy for logs/debug
    }


# Backward-compat name used elsewhere
def lookup_upc(code: str) -> dict[str, Any]:
    return lookup_barcode(code)
