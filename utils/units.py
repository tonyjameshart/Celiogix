# File: utils/units.py
# Description: Lightweight unit normalization and conversion helpers for mass/volume units.

from __future__ import annotations
from typing import Optional, Tuple

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
}

_MASS = {"g", "kg", "oz", "lb"}
_VOLUME = {"ml", "l", "floz", "tsp", "tbsp", "cup"}

# Base factors
_MASS_TO_G = {"g": 1.0, "kg": 1000.0, "oz": 28.349523125, "lb": 453.59237}
_VOL_TO_ML = {
    "ml": 1.0,
    "l": 1000.0,
    "floz": 29.5735295625,
    "tsp": 4.92892159375,
    "tbsp": 14.78676478125,
    "cup": 240.0,  # “cooking cup”
}

def normalize_unit(u: Optional[str]) -> Optional[str]:
    if not u:
        return None
    return _ALIASES.get(u.strip().lower(), u.strip().lower())

def unit_class(u: Optional[str]) -> Optional[str]:
    u = normalize_unit(u)
    if not u: return None
    if u in _MASS: return "mass"
    if u in _VOLUME: return "volume"
    return None

def convert_amount(value: float, from_unit: Optional[str], to_unit: Optional[str]) -> Tuple[Optional[float], bool]:
    """
    Convert value from from_unit → to_unit.
    Returns (converted_value or None, ok_flag).
    - If units identical or both missing: passthrough.
    - If classes differ (mass vs volume) or one side missing: fail.
    """
    fu = normalize_unit(from_unit)
    tu = normalize_unit(to_unit)
    if fu == tu:  # includes both None
        return (value, True)
    if fu is None or tu is None:
        return (None, False)

    fcls, tcls = unit_class(fu), unit_class(tu)
    if fcls != tcls or fcls is None:
        return (None, False)

    if fcls == "mass":
        g = value * _MASS_TO_G[fu]
        return (g / _MASS_TO_G[tu], True)
    ml = value * _VOL_TO_ML[fu]
    return (ml / _VOL_TO_ML[tu], True)
