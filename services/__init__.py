# path: services/__init__.py
"""
Service layer exports (functional style).
- Inventory & Shopping helpers
- Optional Pantry CRUD (only if services/pantry.py exists)
- Optional GF Safety helpers (only if services/gf_safety.py exists)
"""

# --- Inventory / Shopping (required) ---
from .inventory import (
    apply_menu_consumption,
    apply_pending,
    expand_menu_ingredients,
    is_low_stock,
    iter_low_stock_items,
)
from .shopping import (
    mark_purchased,
    merge_or_increment,
    recompute_for_ids,
    recompute_from_thresholds,
)

# --- Optional: Pantry CRUD passthroughs ---
try:
    from .pantry import delete_many as pantry_delete_many
    from .pantry import get_by_id as pantry_get_by_id
    from .pantry import insert as pantry_insert
    from .pantry import list_all as pantry_list_all
    from .pantry import update as pantry_update
except Exception:
    # Pantry module not present; skip re-exports
    pass

# --- Optional: GF Safety helpers (explainable classifier) ---
try:
    from .gf_safety import (
        GFSafetyResult,
        apply_to_pantry_dict,
        classify_pantry_item,
        classify_recipe_record,
        classify_text,
    )
except Exception:
    # GF safety module not present; skip re-exports
    pass

# --- Public surface: build dynamically to avoid phantom names ---
__all__ = [
    # inventory
    "is_low_stock",
    "iter_low_stock_items",
    "expand_menu_ingredients",
    "apply_menu_consumption",
    "apply_pending",
    # shopping
    "merge_or_increment",
    "recompute_from_thresholds",
    "recompute_for_ids",
    "mark_purchased",
    # pantry (optional)
    "pantry_list_all",
    "pantry_get_by_id",
    "pantry_insert",
    "pantry_update",
    "pantry_delete_many",
    # gf safety (optional)
    "classify_text",
    "classify_pantry_item",
    "classify_recipe_record",
    "apply_to_pantry_dict",
    "GFSafetyResult",
]
# Keep only names actually defined (pantry/gf_safety are optional)
__all__ = [name for name in __all__ if name in globals()]
