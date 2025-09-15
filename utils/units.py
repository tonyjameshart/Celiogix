# File: utils/units.py
# Description: Unit normalization + conversion with simple mass/volume "phases".
# Supports two calling styles for backward-compat:
#   - to_canonical(value, unit) -> (canon_value, canon_unit)
#   - to_canonical(value, unit, phase) -> canon_value where phase is one of PHASE_DRY/PHASE_WET
#   - from_canonical(canon_value, canon_unit, desired_unit) -> value
#   - from_canonical(canon_value, to_unit, phase) -> value
#
from __future__ import annotations
from typing import Optional, Tuple, Union

PHASE_DRY = "dry"
PHASE_WET = "wet"

# Normalization map
_ALIASES = {
    # mass
    "g": "g", "gram": "g", "grams": "g",
    "kg": "kg", "kilogram": "kg", "kilograms": "kg",
    "oz": "oz", "ounce": "oz", "ounces": "oz",
    "lb": "lb", "lbs": "lb", "pound": "lb", "pounds": "lb",
    # volume (US)
    "ml": "ml", "milliliter": "ml", "milliliters": "ml",
    "l": "l", "liter": "l", "liters": "l",
    "fl oz": "floz", "floz": "floz", "fluid ounce": "floz", "fluid ounces": "floz",
    "tsp": "tsp", "teaspoon": "tsp", "teaspoons": "tsp",
    "tbsp": "tbsp", "tablespoon": "tbsp", "tablespoons": "tbsp",
    "cup": "cup", "cups": "cup",
    # neutral / count
    "count": "count", "ct": "count", "ea": "count", "each": "count"
}

_MASS = {"g", "kg", "oz", "lb"}
_VOLUME = {"ml", "l", "floz", "tsp", "tbsp", "cup"}
_NEUTRAL = {"count"}

# Base factors
_MASS_TO_G = {"g": 1.0, "kg": 1000.0, "oz": 28.349523125, "lb": 453.59237}
_VOL_TO_ML = {
    "ml": 1.0,
    "l": 1000.0,
    "floz": 29.5735295625,
    "tsp": 4.92892159375,
    "tbsp": 14.78676478125,
    "cup": 236.5882365,  # 16 tbsp in 1 cup for internal consistency
}

def normalize_unit(u: Optional[str]) -> Optional[str]:
    if not u:
        return None
    return _ALIASES.get(u.strip().lower(), u.strip().lower())

def unit_class(u: Optional[str]) -> Optional[str]:
    u = normalize_unit(u)
    if not u:
        return None
    if u in _MASS:
        return "mass"
    if u in _VOLUME:
        return "volume"
    if u in _NEUTRAL:
        return "neutral"
    return None

def unit_phase(u: Optional[str]) -> Optional[str]:
    """Map a unit to its 'phase': dry (mass), wet (volume), or None for neutral/unknown."""
    cls = unit_class(u)
    if cls == "mass":
        return PHASE_DRY
    if cls == "volume":
        return PHASE_WET
    return None

def _to_canon_factor(u: str) -> Tuple[float, str]:
    """Return (factor, base_unit) to convert *from* unit u to canonical base."""
    u = normalize_unit(u) or ""
    if u in _MASS:
        return (_MASS_TO_G[u], "g")
    if u in _VOLUME:
        return (_VOL_TO_ML[u], "ml")
    if u in _NEUTRAL or u == "":
        return (1.0, "count" if u in _NEUTRAL else "")
    # unknown unit → identity in that unit
    return (1.0, u)

def _from_canon_factor(u: str) -> Tuple[float, str]:
    """Return (inv_factor, base_unit) to convert *to* unit u from canonical base."""
    u = normalize_unit(u) or ""
    if u in _MASS:
        return (1.0/_MASS_TO_G[u], "g")
    if u in _VOLUME:
        return (1.0/_VOL_TO_ML[u], "ml")
    if u in _NEUTRAL or u == "":
        return (1.0, "count" if u in _NEUTRAL else "")
    return (1.0, u)

def to_canonical(value: float, unit: Optional[str], *maybe_phase: str) -> Union[Tuple[float, str], float]:
    """Convert (value, unit) to a canonical base.
    - If called with 2 args → returns (canon_value, canon_unit).
    - If called with a third arg (phase) → returns canon_value (float) assuming phase:
        dry → base 'g'; wet → base 'ml'. If phase doesn't match unit class, returns value unchanged.
    """
    u = normalize_unit(unit)
    # Two-arg form: return tuple
    if len(maybe_phase) == 0:
        if u is None:
            return (value, "")
        f, base = _to_canon_factor(u)
        return (value * f, base)
    # Three-arg form: return float
    phase = maybe_phase[0]
    if phase == PHASE_DRY:
        # expect base g; if unit not mass, refuse conversion
        if unit_class(u) == "mass":
            return value * _MASS_TO_G[u]
        return float(value)
    if phase == PHASE_WET:
        if unit_class(u) == "volume":
            return value * _VOL_TO_ML[u]
        return float(value)
    # Unknown phase → identity
    return float(value)

def from_canonical(canon_value: float, u_or_base: Optional[str], target: Optional[str]) -> float:
    """Inverse of to_canonical with support for two signatures:
    A) from_canonical(canon_value, canon_unit, desired_unit)
    B) from_canonical(canon_value, to_unit, phase) where phase in {PHASE_DRY, PHASE_WET}
    If units are incompatible for (A), returns canon_value (as tests expect).
    """
    canon_unit = normalize_unit(u_or_base)
    target = normalize_unit(target)
    # Signature B: second arg is the *to_unit* and third is phase
    if target in {PHASE_DRY, PHASE_WET}:
        to_unit = canon_unit
        phase = target
        if to_unit is None:
            return float(canon_value)
        if phase == PHASE_DRY:
            # canon_value is in grams
            if unit_class(to_unit) == "mass":
                inv, base = _from_canon_factor(to_unit)  # base 'g'
                return float(canon_value) * inv
            return float(canon_value)
        if phase == PHASE_WET:
            if unit_class(to_unit) == "volume":
                inv, base = _from_canon_factor(to_unit)  # base 'ml'
                return float(canon_value) * inv
            return float(canon_value)
        return float(canon_value)
    # Signature A: have canon_unit and desired unit
    desired = target
    if desired is None:
        return float(canon_value)
    # If canon_unit equals desired
    if canon_unit == desired:
        return float(canon_value)
    # If canon is one of base units
    if canon_unit in ("g", "ml", "count", None, ""):
        # Use inv factor for desired
        inv, base = _from_canon_factor(desired)
        # only convert if bases match
        if (canon_unit in ("g",) and base == "g") or (canon_unit in ("ml",) and base == "ml") or (canon_unit in ("count","",None) and base == "count"):
            return float(canon_value) * inv
        # mismatched base → return canon_value unchanged
        return float(canon_value)
    # Unknown bases → identity
    return float(canon_value)
