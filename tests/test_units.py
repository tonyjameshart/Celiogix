# file: tests/test_units.py
"""Minimal tests for utils.units to guard conversions and phases."""

from __future__ import annotations

import math

from utils.units import PHASE_DRY, PHASE_WET, from_canonical, to_canonical, unit_phase


def _approx(a: float, b: float, tol: float = 1e-6) -> bool:
    return math.isclose(a, b, rel_tol=0, abs_tol=tol)


def test_phase_mass_and_volume():
    assert unit_phase("g") == PHASE_DRY
    assert unit_phase("kg") == PHASE_DRY
    assert unit_phase("oz") == PHASE_DRY
    assert unit_phase("ml") == PHASE_WET
    assert unit_phase("cup") == PHASE_WET
    assert unit_phase("tbsp") == PHASE_WET


def test_to_canonical_mass_and_volume():
    v, u = to_canonical(1, "kg")
    assert u == "g" and _approx(v, 1000.0)

    v, u = to_canonical(2, "cup")
    assert u == "ml" and _approx(v, 473.176473, tol=1e-3)

    v, u = to_canonical(3, "count")
    assert u == "count" and _approx(v, 3.0)


def test_from_canonical_round_trip():
    v, u = to_canonical(2.2, "lb")
    back = from_canonical(v, u, "lb")
    assert _approx(back, 2.2, tol=1e-6)

    v, u = to_canonical(8, "tbsp")
    cups = from_canonical(v, u, "cup")
    # 16 tbsp ≈ 1 cup → 8 tbsp ≈ 0.5 cup
    assert _approx(cups, 0.5, tol=1e-3)


def test_incompatible_returns_base_value():
    # Asking to turn grams into cups should just return the base value
    v, u = to_canonical(100, "g")
    out = from_canonical(v, u, "cup")
    assert _approx(out, v)
