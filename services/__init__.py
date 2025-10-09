# path: services/__init__.py
"""
Service layer exports (functional style).
- Inventory & Shopping helpers
- Optional Pantry CRUD (only if services/pantry.py exists)
- Optional GF Safety helpers (only if services/gf_safety.py exists)
"""

# --- Inventory / Shopping (optional - may not exist) ---
try:
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
except ImportError:
    # Inventory/Shopping modules not present; skip re-exports
    pass

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

# --- Recipe services ---
try:
    from .recipe_scraper import (
        RecipeScraper, scrape_recipe_from_url, scrape_recipes_from_url,
        check_scraper_dependencies, is_scraper_available
    )
    from .recipe_enhancement import (
        RecipeRanker, RecipeScaler, IngredientSubstitution, RecipeConverter, RecipeExporter,
        recipe_ranker, recipe_scaler, ingredient_substitution, recipe_converter, recipe_exporter
    )
except Exception:
    # Recipe services not present; skip re-exports
    pass

# --- Gluten Guardian services ---
try:
    from .symptom_correlation_engine import (
        analyze_symptom_patterns,
        generate_correlation_insights,
        recommend_meals_based_on_symptoms,
        SymptomPattern,
        CorrelationInsight,
    )
    from .pdf_export_service import PDFExportService, check_reportlab_available
    from .barcode_scanner_service import BarcodeScannerService, BarcodeResult, check_scanner_available
except Exception:
    # Gluten Guardian modules not present; skip re-exports
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
    # recipe services
    "RecipeScraper",
    "scrape_recipe_from_url",
    "scrape_recipes_from_url",
    "check_scraper_dependencies",
    "is_scraper_available",
    "RecipeRanker",
    "RecipeScaler", 
    "IngredientSubstitution",
    "RecipeConverter",
    "RecipeExporter",
    "recipe_ranker",
    "recipe_scaler",
    "ingredient_substitution",
    "recipe_converter",
    "recipe_exporter",
    # gluten guardian services
    "analyze_symptom_patterns",
    "generate_correlation_insights", 
    "recommend_meals_based_on_symptoms",
    "SymptomPattern",
    "CorrelationInsight",
    "PDFExportService",
    "check_reportlab_available",
    "BarcodeScannerService",
    "BarcodeResult",
    "check_scanner_available",
]
# Keep only names actually defined (pantry/gf_safety are optional)
__all__ = [name for name in __all__ if name in globals()]
