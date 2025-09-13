# path: services/gf_safety.py
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
import json
import re

from utils.gf_lexicon import (
    RISK_TERMS, MAYBE_TERMS, SAFE_TERMS,
    PHRASES_RISK, PHRASES_SAFE,
    EXCEPTIONS_SAFE, TERM_WEIGHTS, ALIASES,
)

# --------------------------- datamodel ---------------------------

@dataclass
class GFSafetyResult:
    flag: str                   # "SAFE" | "RISK" | "UNKNOWN"
    confidence: float           # 0.0 - 1.0
    reasons: List[str]          # human-readable strings
    matches: Dict[str, List[str]]  # {"risk":[...], "maybe":[...], "safe":[...], "phrases":[...]}
    evidence: Dict[str, Any]    # any extra structured bits

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # stable ordering for display/testing
        for k in ("risk", "maybe", "safe", "phrases"):
            if k in d["matches"]:
                d["matches"][k] = sorted(set(d["matches"][k]))
        return d


# ------------------------ normalization -------------------------

def _norm(s: Any) -> str:
    return (str(s or "")).strip().lower()

def _apply_aliases(text: str) -> str:
    out = text
    for a, b in ALIASES.items():
        out = out.replace(a, b)
    return out

def _any(pats: Iterable[re.Pattern], text: str) -> Optional[re.Pattern]:
    for p in pats:
        if p.search(text):
            return p
    return None


# -------------------------- core logic --------------------------

def _scan_terms(text: str, terms: Iterable[str]) -> List[str]:
    t = _apply_aliases(_norm(text))
    hits: List[str] = []
    for term in terms:
        tt = term.lower()
        if tt and tt in t:
            hits.append(term)
    return hits

def _apply_exceptions(term: str, text: str) -> bool:
    """Return True if an exception pattern ‘saves’ this MAYBE term."""
    pats = EXCEPTIONS_SAFE.get(term.lower())
    if not pats:
        return False
    return _any(pats, text) is not None

def _score(
    risk_terms: Sequence[str],
    maybe_terms: Sequence[str],
    safe_terms: Sequence[str],
    phrase_risk: Sequence[Tuple[re.Pattern, float, str]],
    phrase_safe: Sequence[Tuple[re.Pattern, float, str]],
    text: str,
) -> Tuple[str, float, List[str], Dict[str, List[str]], Dict[str, Any]]:
    """Return (flag, confidence, reasons, matches, evidence)."""
    t = _apply_aliases(_norm(text))
    reasons: List[str] = []
    matches: Dict[str, List[str]] = {"risk": [], "maybe": [], "safe": [], "phrases": []}

    # strong phrases
    pr = _any([p for p, _, _ in phrase_risk], t)
    ps = _any([p for p, _, _ in phrase_safe], t)
    risk_score = 0.0
    safe_score = 0.0

    if pr:
        w = next(w for p, w, _ in phrase_risk if p.pattern == pr.pattern)
        label = next(label for p, _, label in phrase_risk if p.pattern == pr.pattern)
        risk_score += w
        matches["phrases"].append(pr.pattern)
        reasons.append(f"Risk phrase matched: {label}")
    if ps:
        w = next(w for p, w, _ in phrase_safe if p.pattern == ps.pattern)
        label = next(label for p, _, label in phrase_safe if p.pattern == ps.pattern)
        safe_score += w
        matches["phrases"].append(ps.pattern)
        reasons.append(f"Safe phrase matched: {label}")

    # term hits
    risk_hits = _scan_terms(t, risk_terms)
    maybe_hits = _scan_terms(t, maybe_terms)
    safe_hits = _scan_terms(t, safe_terms)

    # exception-aware filtering for MAYBE set
    kept_maybe: List[str] = []
    for m in maybe_hits:
        if _apply_exceptions(m, t):
            reasons.append(f"Qualifier detected for “{m}” → treated as SAFE context")
            safe_hits.append(m)   # treat as soft safe signal
        else:
            kept_maybe.append(m)
    maybe_hits = kept_maybe

    if risk_hits:
        risk_score += TERM_WEIGHTS.get("risk", 0.75) * min(1.0, 0.4 + 0.15 * len(risk_hits))
        reasons.append(f"Risk terms: {', '.join(sorted(set(risk_hits)))}")
        matches["risk"].extend(risk_hits)

    if maybe_hits:
        risk_score += TERM_WEIGHTS.get("maybe", 0.35) * min(1.0, 0.3 + 0.1 * len(maybe_hits))
        reasons.append(f"Needs review (ambiguous): {', '.join(sorted(set(maybe_hits)))}")
        matches["maybe"].extend(maybe_hits)

    if safe_hits:
        safe_score += TERM_WEIGHTS.get("safe", 0.45) * min(1.0, 0.3 + 0.1 * len(safe_hits))
        reasons.append(f"Safe signals: {', '.join(sorted(set(safe_hits)))}")
        matches["safe"].extend(safe_hits)

    # decision
    # bias to risk if both sides are similar, otherwise choose stronger side
    if risk_score >= max(safe_score * 1.05, 0.6):
        flag = "RISK"
        conf = max(0.55, min(1.0, risk_score))
    elif safe_score >= max(risk_score * 1.1, 0.6):
        flag = "SAFE"
        conf = max(0.55, min(1.0, safe_score))
    else:
        flag = "UNKNOWN"
        conf = max(0.35, min(0.65, max(risk_score, safe_score)))

    evidence = {
        "risk_score": round(risk_score, 3),
        "safe_score": round(safe_score, 3),
        "risk_hits": sorted(set(risk_hits)),
        "maybe_hits": sorted(set(maybe_hits)),
        "safe_hits": sorted(set(safe_hits)),
    }
    return flag, conf, reasons, matches, evidence

# -------------------------- public API --------------------------

def classify_text(text: str) -> GFSafetyResult:
    flag, conf, reasons, matches, evidence = _score(
        RISK_TERMS, MAYBE_TERMS, SAFE_TERMS, PHRASES_RISK, PHRASES_SAFE, text or ""
    )
    # bonus guidance
    recs: List[str] = []
    if "oats" in (t.lower() for t in matches.get("maybe", [])):
        recs.append("If oats are present, verify 'gluten-free oats' on label or certification.")
    if any("soy sauce" in t.lower() for t in matches.get("maybe", [])):
        recs.append("If soy sauce is listed, prefer GF tamari or a soy sauce labeled gluten-free.")
    if recs:
        reasons.extend(recs)
    return GFSafetyResult(flag=flag, confidence=round(conf, 3), reasons=reasons, matches=matches, evidence=evidence)

def classify_ingredients(ingredients: Iterable[Dict[str, Any]]) -> GFSafetyResult:
    blob = " | ".join(
        " ".join(
            str(ing.get("original") or "") + " " + str(ing.get("name") or "") + " " + str(ing.get("unit") or "")
        )
        for ing in (ingredients or [])
    )
    return classify_text(blob)

def classify_pantry_item(data: Dict[str, Any]) -> GFSafetyResult:
    parts = [
        data.get("name"), data.get("brand"),
        data.get("category"), data.get("subcategory"),
        data.get("tags"), data.get("notes"),
    ]
    return classify_text(" | ".join(p for p in map(_norm, parts) if p))

def classify_recipe_record(row: Dict[str, Any]) -> GFSafetyResult:
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

    # optional fallbacks for provider JSON shapes
    try:
        raw = json.loads(row.get("json")) if isinstance(row.get("json"), str) else (row.get("json") or {})
    except Exception:
        raw = {}
    ext = (raw.get("raw") or {}).get("extendedIngredients") or raw.get("extendedIngredients")
    if isinstance(ext, list):
        return classify_ingredients(ext)
    rec = (raw.get("raw") or {}).get("recipe") or raw.get("recipe") or {}
    if isinstance(rec.get("ingredients"), list):
        return classify_ingredients(rec["ingredients"])

    return GFSafetyResult(flag="UNKNOWN", confidence=0.4, reasons=[], matches={"risk": [], "maybe": [], "safe": [], "phrases": []}, evidence={})

def apply_to_pantry_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns a copy enriched with gf_flag and gf_reason (non-destructive).
    Never overwrites explicit SAFE/RISK if already set.
    """
    result = classify_pantry_item(data)
    out = dict(data)
    current = (out.get("gf_flag") or "").strip().upper()
    if current not in {"SAFE", "RISK"}:
        out["gf_flag"] = result.flag
    out["gf_reason"] = "; ".join(result.reasons)
    return out
