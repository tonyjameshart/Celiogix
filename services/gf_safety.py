# services/gf_safety.py - PATCHED VERSION with critical safety fixes
from __future__ import annotations

from collections.abc import Iterable, Mapping
from functools import lru_cache
import re
from typing import Any, Final, NamedTuple

# Import from centralized lexicon
try:
    from utils.gf_lexicon import (
        GLUTEN_TERMS as _GLUTEN_TERMS,
        AMBIGUOUS_TERMS as _AMBIGUOUS_TERMS,
        MAY_CONTAIN_TERMS as _MAY_CONTAIN_TERMS,
        CERT_MARKS as _CERT_MARKS,
        CLAIMS_SAFE as _CLAIMS_SAFE,
    )
except ImportError:
    # Fallback if lexicon not yet updated
    _GLUTEN_TERMS = (
        "wheat", "barley", "rye", "triticale", "spelt", "kamut", "farro",
        "einkorn", "emmer", "bulgur", "semolina", "durum", "graham",
        "malt", "malt extract", "malt syrup", "malt flavor", "malt vinegar",
        "brewer's yeast", "wheat flour", "barley flour", "rye flour", "farina",
    )
    _AMBIGUOUS_TERMS = (
        "starch", "modified starch", "food starch", "dextrin", "maltodextrin",
        "natural flavor", "flavoring", "seasoning", "yeast extract",
        "hydrolyzed vegetable protein", "miso", "soy sauce", "oats", "oat",
    )
    _MAY_CONTAIN_TERMS = (
        "may contain wheat", "contains wheat", "may contain traces of wheat",
        "made on shared equipment with wheat",
        "processed on shared equipment with wheat",
        "made in a facility that also processes wheat",
        "manufactured in a facility that also processes wheat",
    )
    _CERT_MARKS = (
        "certified gluten free", "certified gf", "gfco",
        "gluten-free certification", "gluten free certified",
    )
    _CLAIMS_SAFE = ("gluten free", "gluten-free", "gf")

GLUTEN_TERMS: Final[tuple[str, ...]] = _GLUTEN_TERMS
AMBIGUOUS_TERMS: Final[tuple[str, ...]] = _AMBIGUOUS_TERMS
MAY_CONTAIN_TERMS: Final[tuple[str, ...]] = _MAY_CONTAIN_TERMS
CERT_MARKS: Final[tuple[str, ...]] = _CERT_MARKS
CLAIMS_SAFE: Final[tuple[str, ...]] = _CLAIMS_SAFE

DEFAULT_LIMIT_PPM: Final[int] = 20


class Match(NamedTuple):
    term: str
    start: int
    end: int


class SafetyResult(NamedTuple):
    is_safe: bool
    risk_score: int
    reasons: tuple[str, ...]
    matches_positive: tuple[Match, ...]
    matches_negative: tuple[Match, ...]
    matches_ambiguous: tuple[Match, ...]
    limit_ppm: int


GFSafetyResult = SafetyResult  # alias for backward compatibility


def _normalize(s: str | None) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _unique(seq: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    out: list[str] = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return tuple(out)


@lru_cache(maxsize=1)
def _compiled_patterns() -> dict[str, tuple[re.Pattern[str], ...]]:
    def pat(terms: Iterable[str]) -> tuple[re.Pattern[str], ...]:
        compiled: list[re.Pattern[str]] = []
        for t in terms:
            t_norm = _normalize(t)
            if " " in t_norm or "'" in t_norm:
                compiled.append(re.compile(re.escape(t_norm)))
            else:
                compiled.append(re.compile(rf"\b{re.escape(t_norm)}\b"))
        return tuple(compiled)

    return {
        "pos": pat(CERT_MARKS + CLAIMS_SAFE),
        "neg": pat(GLUTEN_TERMS + MAY_CONTAIN_TERMS),
        "amb": pat(AMBIGUOUS_TERMS),
    }


def _scan(text: str, patterns: tuple[re.Pattern[str], ...]) -> tuple[Match, ...]:
    hits: list[Match] = []
    for p in patterns:
        for m in p.finditer(text):
            hits.append(Match(term=p.pattern, start=m.start(), end=m.end()))
    return tuple(hits)


def evaluate_label(*parts: str | None, ppm_limit: int = DEFAULT_LIMIT_PPM) -> SafetyResult:
    """
    CRITICAL SAFETY FIX: Advisory warnings now override all certifications.
    
    Risk scoring (when no advisory):
      +5 explicit gluten ingredient
      +3 advisory/cross-contact phrase (DISQUALIFYING)
      +1 ambiguous term (cap at +3)
      -4 certified gluten-free
      -2 generic 'gluten free' claim
    
    Safe if risk_score <= 0 AND no advisory warnings.
    """
    text = _normalize(" ".join(p or "" for p in parts))
    pats = _compiled_patterns()

    pos = _scan(text, pats["pos"])
    neg = _scan(text, pats["neg"])
    amb = _scan(text, pats["amb"])

    # CRITICAL FIX: Check for advisory warnings first
    advisory_phrases = (
        "may contain", "contains wheat", "contains barley", "contains rye",
        "made on shared equipment", "processed on shared equipment",
        "made in a facility", "manufactured in a facility",
        "processed in a facility"
    )
    
    has_advisory = False
    advisory_terms: list[str] = []
    for m in neg:
        human = m.term.replace(r"\b", "").replace("\\", "")
        if any(phrase in human for phrase in advisory_phrases):
            has_advisory = True
            advisory_terms.append(human)
    
    # Advisory warnings are DISQUALIFYING regardless of certification
    if has_advisory:
        return SafetyResult(
            is_safe=False,
            risk_score=999,  # Maximum risk score
            reasons=(
                "CROSS-CONTACT WARNING: " + ", ".join(_unique(advisory_terms)),
                "This product is unsafe regardless of any GF certification claims",
            ),
            matches_positive=pos,
            matches_negative=neg,
            matches_ambiguous=amb,
            limit_ppm=ppm_limit,
        )

    # Original scoring logic for non-advisory cases
    score = 0
    reasons: list[str] = []

    neg_terms: list[str] = []
    for m in neg:
        human = m.term.replace(r"\b", "").replace("\\", "")
        neg_terms.append(human)
        score += 5  # All remaining negatives are explicit gluten
    if neg_terms:
        reasons.append("gluten ingredients: " + ", ".join(_unique(neg_terms)))

    amb_terms: list[str] = []
    for m in amb:
        human = m.term.replace(r"\b", "").replace("\\", "")
        amb_terms.append(human)
        score += 1
    if amb_terms:
        # Cap ambiguous contribution at +3
        excess = len(amb_terms) - 3
        if excess > 0:
            score -= excess
        reasons.append("ambiguous ingredients: " + ", ".join(_unique(amb_terms)))

    pos_terms: list[str] = []
    for m in pos:
        human = m.term.replace(r"\b", "").replace("\\", "")
        pos_terms.append(human)
        if "certified" in human or "gfco" in human:
            score -= 4
        else:
            score -= 2
    if pos_terms:
        reasons.append("safety claims: " + ", ".join(_unique(pos_terms)))

    return SafetyResult(
        is_safe=score <= 0,
        risk_score=score,
        reasons=tuple(reasons) if reasons else ("no signals detected",),
        matches_positive=pos,
        matches_negative=neg,
        matches_ambiguous=amb,
        limit_ppm=ppm_limit,
    )


def classify_text(text: str | None) -> SafetyResult:
    """Classify arbitrary text for gluten content."""
    return evaluate_label(text)


def classify_pantry_item(item: Mapping[str, Any] | dict[str, Any]) -> SafetyResult:
    """Classify a pantry item by combining all text fields."""
    name = str(item.get("name", "")) if isinstance(item, Mapping) else ""
    brand = str(item.get("brand", "")) if isinstance(item, Mapping) else ""
    category = str(item.get("category", "")) if isinstance(item, Mapping) else ""
    tags = str(item.get("tags", "")) if isinstance(item, Mapping) else ""
    notes = str(item.get("notes", "")) if isinstance(item, Mapping) else ""
    
    return evaluate_label(name, brand, category, tags, notes)


def classify_recipe_record(rec: Mapping[str, Any] | dict[str, Any]) -> SafetyResult:
    """Classify a recipe by title, ingredients, and notes."""
    title = str(rec.get("title", "")) if isinstance(rec, Mapping) else ""
    ingredients = str(rec.get("ingredients", "")) if isinstance(rec, Mapping) else ""
    instructions = str(rec.get("instructions", "")) if isinstance(rec, Mapping) else ""
    notes = str(rec.get("notes", "")) if isinstance(rec, Mapping) else ""
    tags = str(rec.get("tags", "")) if isinstance(rec, Mapping) else ""
    
    return evaluate_label(title, ingredients, instructions, tags, notes)


def apply_to_pantry_dict(d: dict[str, Any]) -> dict[str, Any]:
    """
    Apply GF classification to a pantry dict and add computed fields.
    Does NOT override existing explicit gf_flag values.
    """
    res = classify_pantry_item(d)
    
    # Only update if gf_flag is missing or UNKNOWN
    existing_flag = (d.get("gf_flag") or "").strip().upper()
    if existing_flag not in ("GF", "SAFE", "RISK", "NGF"):
        d["gf_flag"] = "GF" if res.is_safe else ("RISK" if res.risk_score > 0 else "UNKNOWN")
    
    # Always update computed fields for display
    d["gf_is_safe"] = res.is_safe
    d["gf_risk_score"] = res.risk_score
    d["gf_reasons"] = "; ".join(res.reasons)
    
    return d


def get_display_symbol(result: SafetyResult) -> str:
    """Return a single-character symbol for display in tables."""
    if result.risk_score >= 999:  # Advisory warning
        return "?"
    elif result.is_safe:
        return "?"
    elif result.risk_score > 0:
        return "?"
    else:
        return "?"