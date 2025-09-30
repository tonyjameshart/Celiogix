# File: utils/labels.py — centralized UI labels
from __future__ import annotations

LABELS = {
    "amount": "Net. weight",
    "net_weight": "Net. weight",
    "quantity": "Quantity",  # NEW
    "unit": "Unit",
    "threshold": "Threshold",
    "brand": "Brand",
    "subcategory": "Subcategory",
    "category": "Category",
    "notes": "Notes",
    "name": "Name",
    "store": "Store",
}


def L(key: str) -> str:
    return LABELS.get(key, key.replace("_", " ").title())
