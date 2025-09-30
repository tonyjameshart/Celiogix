from __future__ import annotations

from typing import Final, Literal

# ---- Core unit maps (canonical keys are lowercase) ----
_MASS_G_PER_UNIT: Final[dict[str, float]] = {
    "g": 1.0,
    "gram": 1.0,
    "grams": 1.0,
    "kg": 1000.0,
    "kilogram": 1000.0,
    "kilograms": 1000.0,
    "oz": 28.349523125,
    "ounce": 28.349523125,
    "ounces": 28.349523125,
    "lb": 453.59237,
    "lbs": 453.59237,
    "pound": 453.59237,
    "pounds": 453.59237,
}

_VOLUME_ML_PER_UNIT: Final[dict[str, float]] = {
    "ml": 1.0,
    "milliliter": 1.0,
    "milliliters": 1.0,
    "l": 1000.0,
    "liter": 1000.0,
    "liters": 1000.0,
    "tsp": 4.92892159375,
    "teaspoon": 4.92892159375,
    "teaspoons": 4.92892159375,
    "tbsp": 14.78676478125,
    "tablespoon": 14.78676478125,
    "tablespoons": 14.78676478125,
    "cup": 236.5882365,
    "cups": 236.5882365,
    "pt": 473.176473,
    "pint": 473.176473,
    "pints": 473.176473,
    "qt": 946.352946,
    "quart": 946.352946,
    "quarts": 946.352946,
    "gal": 3785.411784,
    "gallon": 3785.411784,
    "gallons": 3785.411784,
}

UnitKind = Literal["mass", "volume", "unknown"]

# ---- Phases (typed literals) ----
PHASE_DRY: Final[Literal["dry"]] = "dry"
PHASE_WET: Final[Literal["wet"]] = "wet"
PHASE_UNKNOWN: Final[Literal["unknown"]] = "unknown"
Phase = Literal["dry", "wet", "unknown"]


def _norm(u: str | None) -> str:
    return (u or "").strip().lower()


def unit_kind(u: str | None) -> UnitKind:
    k = _norm(u)
    if k in _MASS_G_PER_UNIT:
        return "mass"
    if k in _VOLUME_ML_PER_UNIT:
        return "volume"
    return "unknown"


def unit_phase(u: str | None) -> Phase:
    kind = unit_kind(u)
    if kind == "mass":
        return PHASE_DRY
    if kind == "volume":
        return PHASE_WET
    return PHASE_UNKNOWN


def grams_from(value: float, unit: str | None) -> float:
    key = _norm(unit)
    factor = _MASS_G_PER_UNIT.get(key)
    return value * factor if factor is not None else value


def ml_from(value: float, unit: str | None) -> float:
    key = _norm(unit)
    factor = _VOLUME_ML_PER_UNIT.get(key)
    return value * factor if factor is not None else value


def to_canonical(value: float, unit: str | None) -> float:
    k = unit_kind(unit)
    if k == "mass":
        return grams_from(value, unit)
    if k == "volume":
        return ml_from(value, unit)
    return value


def from_canonical(value: float, unit: str | None) -> float:
    key = _norm(unit)
    if key in _MASS_G_PER_UNIT:
        factor = _MASS_G_PER_UNIT[key] or 1.0
        return value / factor
    if key in _VOLUME_ML_PER_UNIT:
        factor = _VOLUME_ML_PER_UNIT[key] or 1.0
        return value / factor
    return value


def convert(value: float, from_unit: str | None, to_unit: str | None) -> float:
    fk = unit_kind(from_unit)
    tk = unit_kind(to_unit)
    if fk == "mass" and tk == "mass":
        g = grams_from(value, from_unit)
        return from_canonical(g, to_unit)
    if fk == "volume" and tk == "volume":
        ml = ml_from(value, from_unit)
        return from_canonical(ml, to_unit)
    return value


def try_parse_qty_unit(s: str) -> tuple[float, str] | None:
    text = (s or "").strip().lower()
    if not text:
        return None
    parts = text.split()
    try:
        if len(parts) == 1:
            return float(parts[0]), ""
        val = float(parts[0])
        unit = " ".join(parts[1:]).strip()
        return val, unit
    except Exception:
        return None
