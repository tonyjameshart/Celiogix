# path: utils/categorize.py
from __future__ import annotations

import json
import os
import re

# ====== Core text helpers ======
_BULLET = re.compile(r"^[\s\u00B7\u2022\u2023\u2043\u2212\-\*\u25A0-\u25FF]+\s*")
_PARENS = re.compile(r"\([^)]*\)")
_NUMERIC = re.compile(r"^\d+([\/.]\d+)?$")

_UNITS = {
    "tsp",
    "tsps",
    "teaspoon",
    "teaspoons",
    "tbsp",
    "tbsps",
    "tablespoon",
    "tablespoons",
    "cup",
    "cups",
    "pint",
    "pints",
    "quart",
    "quarts",
    "gallon",
    "gallons",
    "ml",
    "l",
    "liter",
    "liters",
    "dl",
    "g",
    "kg",
    "gram",
    "grams",
    "kilogram",
    "kilograms",
    "mg",
    "oz",
    "ounce",
    "ounces",
    "lb",
    "lbs",
    "pound",
    "pounds",
    "stick",
    "sticks",
    "clove",
    "cloves",
    "bunch",
    "pinch",
    "dash",
    "package",
    "packages",
    "can",
    "cans",
}

_STOPWORDS = {
    "of",
    "fresh",
    "minced",
    "chopped",
    "diced",
    "ground",
    "whole",
    "large",
    "small",
    "medium",
    "dry",
    "dried",
    "and",
    "or",
}


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def core_from_ingredient(line: str) -> str:
    """Strip bullets, numbers, units, and fluff; return a simplified phrase for matching."""
    s = _norm(line)
    s = _BULLET.sub("", s)
    s = _PARENS.sub("", s)
    tokens = [t for t in re.split(r"[^\w%]+", s) if t]
    out = []
    for t in tokens:
        if _NUMERIC.match(t):  # drop pure numbers/fractions
            continue
        if t in _UNITS or t in _STOPWORDS:
            continue
        out.append(t)
    return " ".join(out).strip()


# ====== Category canonicalization ======
# Canonical set we want to end up with (extend as you like)
KNOWN_CATEGORIES = [
    "Produce",
    "Meat & Seafood",
    "Dairy",
    "Pantry",
    "Canned & Jarred",
    "Condiments",
    "Bakery",
    "Frozen",
    "Beverages",
    "Misc",
    "(Uncategorized)",
]

# Lowercased synonym → canonical bucket
_CANON_MAP = {
    "produce": "Produce",
    "vegetable": "Produce",
    "vegetables": "Produce",
    "veg": "Produce",
    "meat": "Meat & Seafood",
    "seafood": "Meat & Seafood",
    "butcher": "Meat & Seafood",
    "dairy": "Dairy",
    "eggs": "Dairy",
    "egg": "Dairy",
    "pantry": "Pantry",
    "dry goods": "Pantry",
    "drygoods": "Pantry",
    "baking": "Pantry",
    "spices": "Pantry",
    "canned": "Canned & Jarred",
    "canned goods": "Canned & Jarred",
    "jarred": "Canned & Jarred",
    "cans": "Canned & Jarred",
    "condiments": "Condiments",
    "sauces": "Condiments",
    "oils": "Condiments",
    "oil": "Condiments",
    "bakery": "Bakery",
    "bread": "Bakery",
    "frozen": "Frozen",
    "freezer": "Frozen",
    "beverage": "Beverages",
    "beverages": "Beverages",
    "drinks": "Beverages",
    "misc": "Misc",
    "other": "Misc",
    "uncategorized": "(Uncategorized)",
    "(uncategorized)": "(Uncategorized)",
}


def canonical_category(cat: str) -> str:
    s = _norm(cat)
    if not s:
        return ""
    # collapse internal spaces
    s = re.sub(r"\s+", " ", s)
    return _CANON_MAP.get(s, s.title())


def canonical_subcategory(sub: str) -> str:
    s = _norm(sub)
    if not s:
        return ""
    s = re.sub(r"\s+", " ", s)
    return s.title()


# ====== Optional external map (./data/categories.json) ======
def _load_map_from_file() -> dict:
    p = os.path.join(".", "data", "categories.json")
    if not os.path.exists(p):
        return {}
    try:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        # Accept either {"map": {"keyword":"Category"}} or {"Produce":["apple","onion"], ...}
        if isinstance(data, dict):
            if "map" in data and isinstance(data["map"], dict):
                return {_norm(k): v for k, v in data["map"].items() if isinstance(v, str)}
            out = {}
            for cat, keys in data.items():
                if isinstance(keys, list):
                    for k in keys:
                        out[_norm(k)] = cat
            return out
    except Exception:
        pass
    return {}


_FILE_KEYWORD_MAP = _load_map_from_file()

# ====== Ingredient → Category guesser (used by Cookbook→Shopping) ======
_KEYWORD_TO_CATEGORY = {
    # Produce
    "apple": "Produce",
    "banana": "Produce",
    "orange": "Produce",
    "lemon": "Produce",
    "lime": "Produce",
    "onion": "Produce",
    "shallot": "Produce",
    "garlic": "Produce",
    "ginger": "Produce",
    "scallion": "Produce",
    "celery": "Produce",
    "carrot": "Produce",
    "potato": "Produce",
    "sweet potato": "Produce",
    "yam": "Produce",
    "tomato": "Produce",
    "bell pepper": "Produce",
    "pepper": "Produce",
    "jalapeno": "Produce",
    "chili": "Produce",
    "spinach": "Produce",
    "kale": "Produce",
    "lettuce": "Produce",
    "arugula": "Produce",
    "cabbage": "Produce",
    "mushroom": "Produce",
    "zucchini": "Produce",
    "cucumber": "Produce",
    "broccoli": "Produce",
    "cauliflower": "Produce",
    "parsley": "Produce",
    "cilantro": "Produce",
    "basil": "Produce",
    "thyme": "Produce",
    "rosemary": "Produce",
    "sage": "Produce",
    "bay leaf": "Produce",
    "bay leaves": "Produce",
    "avocado": "Produce",
    # Meat & Seafood
    "chicken": "Meat & Seafood",
    "chicken breast": "Meat & Seafood",
    "chicken thighs": "Meat & Seafood",
    "beef": "Meat & Seafood",
    "steak": "Meat & Seafood",
    "ground beef": "Meat & Seafood",
    "pork": "Meat & Seafood",
    "sausage": "Meat & Seafood",
    "bacon": "Meat & Seafood",
    "shrimp": "Meat & Seafood",
    "salmon": "Meat & Seafood",
    "tuna": "Meat & Seafood",
    "ham": "Meat & Seafood",
    "turkey": "Meat & Seafood",
    # Dairy & Eggs
    "milk": "Dairy",
    "butter": "Dairy",
    "unsalted butter": "Dairy",
    "cream": "Dairy",
    "heavy cream": "Dairy",
    "half and half": "Dairy",
    "cheese": "Dairy",
    "parmesan": "Dairy",
    "mozzarella": "Dairy",
    "cheddar": "Dairy",
    "yogurt": "Dairy",
    "sour cream": "Dairy",
    "egg": "Dairy",
    "eggs": "Dairy",
    # Pantry / Dry
    "rice": "Pantry",
    "quinoa": "Pantry",
    "pasta": "Pantry",
    "spaghetti": "Pantry",
    "macaroni": "Pantry",
    "flour": "Pantry",
    "cornstarch": "Pantry",
    "baking powder": "Pantry",
    "baking soda": "Pantry",
    "sugar": "Pantry",
    "brown sugar": "Pantry",
    "powdered sugar": "Pantry",
    "salt": "Pantry",
    "pepper": "Pantry",
    "white pepper": "Pantry",
    "thyme": "Pantry",
    "oregano": "Pantry",
    "cumin": "Pantry",
    "paprika": "Pantry",
    "turmeric": "Pantry",
    "curry": "Pantry",
    "cinnamon": "Pantry",
    "nutmeg": "Pantry",
    "clove": "Pantry",
    "cloves": "Pantry",
    "sage": "Pantry",
    "red pepper flakes": "Pantry",
    "pepper flakes": "Pantry",
    "bay leaves": "Pantry",
    "bay leaf": "Pantry",
    "vanilla": "Pantry",
    "yeast": "Pantry",
    "chocolate chips": "Pantry",
    "cocoa": "Pantry",
    # Canned / Jarred
    "tomato sauce": "Canned & Jarred",
    "diced tomatoes": "Canned & Jarred",
    "crushed tomatoes": "Canned & Jarred",
    "tomato paste": "Canned & Jarred",
    "broth": "Canned & Jarred",
    "stock": "Canned & Jarred",
    "coconut milk": "Canned & Jarred",
    "beans": "Canned & Jarred",
    "black beans": "Canned & Jarred",
    "chickpeas": "Canned & Jarred",
    "garbanzo": "Canned & Jarred",
    "olives": "Canned & Jarred",
    "pickles": "Canned & Jarred",
    # Condiments & Oils
    "ketchup": "Condiments",
    "mustard": "Condiments",
    "mayonnaise": "Condiments",
    "mayo": "Condiments",
    "soy sauce": "Condiments",
    "tamari": "Condiments",
    "fish sauce": "Condiments",
    "hot sauce": "Condiments",
    "vinegar": "Condiments",
    "apple cider vinegar": "Condiments",
    "balsamic": "Condiments",
    "olive oil": "Condiments",
    "vegetable oil": "Condiments",
    "canola oil": "Condiments",
    "sesame oil": "Condiments",
    # Bakery & Bread
    "bread": "Bakery",
    "english muffins": "Bakery",
    "tortilla": "Bakery",
    "buns": "Bakery",
    # Frozen
    "frozen": "Frozen",
    "ice cream": "Frozen",
    # Beverages
    "coffee": "Beverages",
    "tea": "Beverages",
    "juice": "Beverages",
    "soda": "Beverages",
    "sparkling water": "Beverages",
}

# Merge external keyword map if present
_KEYWORD_TO_CATEGORY = {**_KEYWORD_TO_CATEGORY, **_FILE_KEYWORD_MAP}


def guess_category_from_keywords(phrase: str) -> str | None:
    if not phrase:
        return None
    s = _norm(phrase)
    # try longest keys first to prefer "red pepper flakes" over "pepper"
    for key in sorted(_KEYWORD_TO_CATEGORY.keys(), key=lambda k: len(k), reverse=True):
        if key and key in s:
            return _KEYWORD_TO_CATEGORY[key]
    return None


def guess_category(db, ingredient_line: str) -> str:
    """
    Heuristic: pantry match -> keyword map -> 'Misc'.
    - Pantry match tries exact name, then LIKE %core% against pantry.name
    """
    core = core_from_ingredient(ingredient_line)
    if db and core:
        try:
            row = db.execute(
                "SELECT category FROM pantry WHERE LOWER(name)=LOWER(?) AND COALESCE(TRIM(category),'')<>'' LIMIT 1",
                (core,),
            ).fetchone()
            if row and row["category"]:
                return canonical_category(row["category"])
            row = db.execute(
                "SELECT category FROM pantry WHERE LOWER(name) LIKE ? AND COALESCE(TRIM(category),'')<>'' ORDER BY LENGTH(name) DESC LIMIT 1",
                (f"%{core}%",),
            ).fetchone()
            if row and row["category"]:
                return canonical_category(row["category"])
        except Exception:
            pass
    cat = guess_category_from_keywords(core)
    return canonical_category(cat or "Misc")
