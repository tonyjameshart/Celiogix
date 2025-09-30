# path: utils/gtin.py
from __future__ import annotations

import csv
import os
import re
from typing import Any

try:
    import requests
except Exception:
    requests = None  # type: ignore


# ---------- UPC / EAN helpers ----------


def _digits(s: str) -> str:
    return "".join(ch for ch in (s or "") if ch.isdigit())


def _ean13_check_digit(d12: str) -> int:
    """Compute EAN-13 check digit from the first 12 digits."""
    if len(d12) != 12 or not d12.isdigit():
        raise ValueError("EAN-13 needs 12 digits for checksum")
    s = 0
    for i, ch in enumerate(d12):
        n = ord(ch) - 48
        s += n * (3 if (i % 2) else 1)
    return (10 - (s % 10)) % 10


def to_ean13(code: str) -> str:
    """
    Convert a UPC-A / EAN to 13 digits.
    - If 12 digits (UPC-A), prefix '0' and recompute checksum.
    - If 13 digits, return as-is.
    - Strips non-digits.
    """
    c = _digits(code)
    if len(c) == 13:
        return c
    if len(c) == 12:
        base12 = "0" + c[:-1]  # UPC-A (first 11) -> EAN base (12 with leading 0)
        chk = _ean13_check_digit(base12)
        return base12 + str(chk)
    if len(c) in (8, 11, 14):  # handle odd inputs by best-effort
        if len(c) == 14 and c.startswith("0"):
            return c[1:]
        if len(c) == 11:  # missing UPC check digit
            base12 = "0" + c  # make 12 (assume UPC missing the 12th)
            chk = _ean13_check_digit(base12)
            return base12 + str(chk)
    # last resort: pad with leading zeros to 13 and recompute
    c = c.zfill(13)
    base12, _ = c[:-1], c[-1]
    chk = _ean13_check_digit(base12)
    return base12 + str(chk)


def to_upc12(code: str) -> str:
    """Convert an EAN-13 that starts with 0 into UPC-A (12 digits)."""
    c = _digits(code)
    if len(c) == 13 and c.startswith("0"):
        return c[1:]
    if len(c) == 12:
        return c
    return _digits(code)[-12:]


# ---------- Local override (no internet required) ----------


def _read_local_override(upc: str) -> dict[str, Any] | None:
    """
    If data/upc_overrides.csv exists, allow forced mapping.
    Columns (case-insensitive, optional): upc,name,brand,category,subcategory,net_weight,unit,quantity,tags,gf_flag,notes
    """
    paths = ("./data/upc_overrides.csv", "./upc_overrides.csv")
    for p in paths:
        if not os.path.exists(p):
            continue
        try:
            with open(p, encoding="utf-8-sig", newline="") as f:
                rd = csv.DictReader(f)
                for row in rd:
                    if not row:
                        continue
                    r_upc = _digits(row.get("upc", ""))
                    if not r_upc:
                        continue
                    if r_upc == _digits(upc):
                        # normalize numeric fields
                        def pf(x):
                            s = str(x or "").strip()
                            if not s:
                                return 0.0
                            try:
                                if "/" in s and re.match(r"^\s*\d+\s*/\s*\d+\s*$", s):
                                    a, b = s.split("/", 1)
                                    return float(a) / float(b)
                                return float(s)
                            except Exception:
                                return 0.0

                        return {
                            "name": row.get("name", ""),
                            "brand": row.get("brand", ""),
                            "category": row.get("category", ""),
                            "subcategory": row.get("subcategory", ""),
                            "net_weight": pf(row.get("net_weight", "")),
                            "unit": row.get("unit", ""),
                            "quantity": pf(row.get("quantity", "") or 1),
                            "tags": row.get("tags", ""),
                            "gf_flag": row.get("gf_flag", ""),
                            "notes": row.get("notes", ""),
                        }
        except Exception:
            pass
    return None


# ---------- OpenFoodFacts provider (no key required) ----------


def _fetch_off(code: str) -> dict[str, Any] | None:
    """
    Query OpenFoodFacts by barcode. Returns raw OFF product JSON (or None).
    """
    if requests is None:
        return None
    ean = to_ean13(code)
    url = f"https://world.openfoodfacts.org/api/v0/product/{ean}.json"
    try:
        r = requests.get(url, timeout=7)
        if r.status_code != 200:
            return None
        data = r.json()
        if not isinstance(data, dict) or data.get("status") != 1:
            return None
        return data.get("product") or None
    except Exception:
        return None


def _parse_quantity(q: str) -> tuple[float, str]:
    """
    Parse strings like '296 ml', '14.5 oz', '907 g', '2 x 6 oz', '680g'
    -> (296.0,'ml'), (14.5,'oz'), (907,'g'), (12.0,'oz') etc.
    """
    if not q:
        return 0.0, ""
    s = q.strip().lower().replace(",", ".")
    # Handle multipacks "2 x 6 oz"
    m = re.search(r"(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)\s*([a-zA-Z]+)", s)
    if m:
        a, b, unit = m.groups()
        try:
            return float(a) * float(b), unit
        except Exception:
            pass
    # Handle simple "680 g" / "680g" / "14.5 oz"
    m = re.search(r"(\d+(?:\.\d+)?)\s*([a-zA-Z]+)", s)
    if m:
        val, unit = m.groups()
        try:
            return float(val), unit
        except Exception:
            return 0.0, unit
    return 0.0, ""


def _off_to_record(prod: dict[str, Any], upc: str) -> dict[str, Any]:
    name = (prod.get("product_name") or prod.get("generic_name") or "").strip()
    brand = (prod.get("brands") or "").split(",")[0].strip()
    categories = prod.get("categories") or ""
    # choose first two category tokens as Category/Subcategory
    cat_tokens = [c.strip() for c in categories.split(",") if c.strip()]
    category = cat_tokens[-2] if len(cat_tokens) >= 2 else (cat_tokens[-1] if cat_tokens else "")
    subcategory = cat_tokens[-1] if len(cat_tokens) >= 2 else ""
    # quantity parsing
    q = prod.get("quantity") or ""
    net_wt, unit = _parse_quantity(q)
    # rough GF detection
    labels_tags = prod.get("labels_tags") or []
    allergens = (prod.get("allergens") or "").lower()
    tags = []
    gf_flag = "UNKNOWN"
    if any(t in labels_tags for t in ("en:gluten-free", "en:no-gluten")):
        gf_flag = "GF"
        tags.append("GF")
    elif "gluten" in allergens:
        gf_flag = "NGF"
    # Build notes with barcode + OFF brand if missing
    notes = f"UPC:{_digits(upc)}"
    return {
        "name": name or f"Item {_digits(upc)}",
        "brand": brand,
        "category": category,
        "subcategory": subcategory,
        "net_weight": float(net_wt or 0.0),
        "unit": unit,
        "quantity": 1.0,
        "tags": ";".join(tags),
        "gf_flag": gf_flag,
        "notes": notes,
    }


# ---------- Public API ----------


def lookup(code: str) -> dict[str, Any] | None:
    """
    Return a *generic* product dict from any provider or local override.
    Keys you may get: name, brand, category, subcategory, net_weight, unit, quantity, tags, gf_flag, notes.
    """
    c = _digits(code)
    if not c:
        return None

    # 1) Local override beats everything
    ov = _read_local_override(c)
    if ov:
        return ov

    # 2) OpenFoodFacts (no key)
    prod = _fetch_off(c)
    if isinstance(prod, dict):
        return _off_to_record(prod, c)

    # 3) Nothing else for now
    return None


# Convenience aliases many callers will try
def lookup_upc(code: str) -> dict[str, Any] | None:
    return lookup(code)


def resolve_upc(code: str) -> dict[str, Any] | None:
    return lookup(code)


def fetch(code: str) -> dict[str, Any] | None:
    return lookup(code)


def fetch_upc(code: str) -> dict[str, Any] | None:
    return lookup(code)


def search(code: str) -> dict[str, Any] | None:
    return lookup(code)
