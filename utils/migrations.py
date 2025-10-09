from __future__ import annotations

from collections.abc import Iterable  # ruff: UP035
import sqlite3


def _has_table(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? COLLATE NOCASE", (name,)
    ).fetchone()
    return row is not None


def _cols(conn: sqlite3.Connection, table: str) -> set[str]:
    try:
        return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
    except sqlite3.Error:
        return set()


def _add_col(conn: sqlite3.Connection, table: str, coldef: str) -> None:
    name = coldef.split()[0]
    if name not in _cols(conn, table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {coldef}")


def _insert_default_categories(conn: sqlite3.Connection) -> None:
    """Insert default categories if they don't exist"""
    # Check if categories already exist
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM categories")
    count = cursor.fetchone()[0]
    
    if count > 0:
        return  # Categories already exist
    
    # Primary categories
    primary_categories = [
        ("Breakfast & Brunch", None, "Morning meals and brunch dishes", "#f39c12", "🌅", 1),
        ("Lunch & Light Meals", None, "Midday meals and light dishes", "#27ae60", "🥗", 2),
        ("Dinner & Main Courses", None, "Evening meals and main dishes", "#e74c3c", "🍽️", 3),
        ("Sides & Vegetables", None, "Side dishes and vegetable recipes", "#2ecc71", "🥕", 4),
        ("Desserts & Sweets", None, "Sweet treats and desserts", "#9b59b6", "🍰", 5),
        ("Beverages & Drinks", None, "Drinks, cocktails, and beverages", "#3498db", "🥤", 6),
        ("Snacks & Appetizers", None, "Appetizers and snack foods", "#f1c40f", "🍿", 7),
        ("Baking & Breads", None, "Baked goods and bread recipes", "#d35400", "🍞", 8),
    ]
    
    # Insert primary categories
    for name, parent_id, description, color, icon, sort_order in primary_categories:
        cursor.execute("""
            INSERT OR IGNORE INTO categories (name, parent_id, description, color, icon, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, parent_id, description, color, icon, sort_order))
    
    # Get primary category IDs for subcategories
    cursor.execute("SELECT id, name FROM categories WHERE parent_id IS NULL")
    primary_cats = {name: id for id, name in cursor.fetchall()}
    
    # Subcategories
    subcategories = [
        # Breakfast subcategories
        ("Pancakes & Waffles", primary_cats["Breakfast & Brunch"], "Fluffy pancakes and crispy waffles", "#f39c12", "🥞", 1),
        ("Eggs & Omelets", primary_cats["Breakfast & Brunch"], "Egg-based breakfast dishes", "#f39c12", "🍳", 2),
        ("Cereals & Oatmeal", primary_cats["Breakfast & Brunch"], "Hot and cold cereals", "#f39c12", "🥣", 3),
        ("Smoothies & Juices", primary_cats["Breakfast & Brunch"], "Healthy morning drinks", "#f39c12", "🥤", 4),
        
        # Lunch subcategories
        ("Salads", primary_cats["Lunch & Light Meals"], "Fresh and hearty salads", "#27ae60", "🥗", 1),
        ("Sandwiches", primary_cats["Lunch & Light Meals"], "Sandwiches and wraps", "#27ae60", "🥪", 2),
        ("Soups", primary_cats["Lunch & Light Meals"], "Hot and cold soups", "#27ae60", "🍲", 3),
        ("Quick & Easy", primary_cats["Lunch & Light Meals"], "Fast lunch options", "#27ae60", "⚡", 4),
        
        # Dinner subcategories
        ("Beef & Veal", primary_cats["Dinner & Main Courses"], "Beef and veal dishes", "#e74c3c", "🥩", 1),
        ("Pork", primary_cats["Dinner & Main Courses"], "Pork recipes", "#e74c3c", "🐷", 2),
        ("Poultry", primary_cats["Dinner & Main Courses"], "Chicken, turkey, and duck", "#e74c3c", "🐔", 3),
        ("Seafood", primary_cats["Dinner & Main Courses"], "Fish and seafood dishes", "#e74c3c", "🐟", 4),
        ("Vegetarian", primary_cats["Dinner & Main Courses"], "Plant-based main dishes", "#e74c3c", "🌱", 5),
        ("Vegan", primary_cats["Dinner & Main Courses"], "No animal products", "#e74c3c", "🌿", 6),
        
        # Cuisine types
        ("Italian", primary_cats["Dinner & Main Courses"], "Italian cuisine", "#e74c3c", "🇮🇹", 7),
        ("Asian", primary_cats["Dinner & Main Courses"], "Asian cuisine", "#e74c3c", "🍜", 8),
        ("Mexican", primary_cats["Dinner & Main Courses"], "Mexican cuisine", "#e74c3c", "🌮", 9),
        ("Mediterranean", primary_cats["Dinner & Main Courses"], "Mediterranean cuisine", "#e74c3c", "🫒", 10),
        ("American", primary_cats["Dinner & Main Courses"], "American cuisine", "#e74c3c", "🇺🇸", 11),
        
        # Sides subcategories
        ("Vegetables", primary_cats["Sides & Vegetables"], "Vegetable side dishes", "#2ecc71", "🥕", 1),
        ("Grains & Rice", primary_cats["Sides & Vegetables"], "Grain and rice sides", "#2ecc71", "🍚", 2),
        ("Potatoes", primary_cats["Sides & Vegetables"], "Potato dishes", "#2ecc71", "🥔", 3),
        ("Bread & Rolls", primary_cats["Sides & Vegetables"], "Bread and roll sides", "#2ecc71", "🍞", 4),
        
        # Desserts subcategories
        ("Cakes", primary_cats["Desserts & Sweets"], "Layer cakes and cupcakes", "#9b59b6", "🎂", 1),
        ("Cookies", primary_cats["Desserts & Sweets"], "Cookies and bars", "#9b59b6", "🍪", 2),
        ("Pies & Tarts", primary_cats["Desserts & Sweets"], "Pies and tarts", "#9b59b6", "🥧", 3),
        ("Ice Cream", primary_cats["Desserts & Sweets"], "Ice cream and frozen treats", "#9b59b6", "🍦", 4),
        ("Candies", primary_cats["Desserts & Sweets"], "Homemade candies", "#9b59b6", "🍬", 5),
        
        # Beverages subcategories
        ("Coffee & Tea", primary_cats["Beverages & Drinks"], "Hot beverages", "#3498db", "☕", 1),
        ("Smoothies", primary_cats["Beverages & Drinks"], "Fruit and vegetable smoothies", "#3498db", "🥤", 2),
        ("Cocktails", primary_cats["Beverages & Drinks"], "Alcoholic beverages", "#3498db", "🍹", 3),
        ("Non-Alcoholic", primary_cats["Beverages & Drinks"], "Non-alcoholic drinks", "#3498db", "🧃", 4),
        
        # Snacks subcategories
        ("Dips & Spreads", primary_cats["Snacks & Appetizers"], "Dips and spreads", "#f1c40f", "🥄", 1),
        ("Finger Foods", primary_cats["Snacks & Appetizers"], "Finger foods and appetizers", "#f1c40f", "👆", 2),
        ("Chips & Crackers", primary_cats["Snacks & Appetizers"], "Chips and crackers", "#f1c40f", "🍟", 3),
        ("Party Foods", primary_cats["Snacks & Appetizers"], "Party and entertaining foods", "#f1c40f", "🎉", 4),
        
        # Baking subcategories
        ("Bread", primary_cats["Baking & Breads"], "Yeast and quick breads", "#d35400", "🍞", 1),
        ("Pastries", primary_cats["Baking & Breads"], "Pastries and danish", "#d35400", "🥐", 2),
        ("Muffins", primary_cats["Baking & Breads"], "Muffins and quick breads", "#d35400", "🧁", 3),
        ("Specialty Baking", primary_cats["Baking & Breads"], "Special baking projects", "#d35400", "🎨", 4),
    ]
    
    # Insert subcategories
    for name, parent_id, description, color, icon, sort_order in subcategories:
        cursor.execute("""
            INSERT OR IGNORE INTO categories (name, parent_id, description, color, icon, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, parent_id, description, color, icon, sort_order))
    
    conn.commit()


def _create_indexes(conn: sqlite3.Connection, table: str, defs: Iterable[tuple[str, str]]) -> None:
    for idx, expr in defs:
        conn.execute(f"CREATE INDEX IF NOT EXISTS {idx} ON {table}({expr})")


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON")

    conn.execute(
        """CREATE TABLE IF NOT EXISTS app_settings(
            key TEXT PRIMARY KEY,
            value TEXT
        )"""
    )

    conn.execute(
        """CREATE TABLE IF NOT EXISTS pantry(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            brand TEXT,
            category TEXT,
            subcategory TEXT,
            net_weight REAL DEFAULT 0,
            unit TEXT,
            quantity REAL DEFAULT 0,
            store TEXT,
            expiration TEXT,
            gf_flag TEXT DEFAULT 'UNKNOWN',
            tags TEXT,
            notes TEXT
        )"""
    )
    _create_indexes(
        conn,
        "pantry",
        [
            ("idx_pantry_name", "name"),
            ("idx_pantry_cat", "category"),
            ("idx_pantry_brand", "brand"),
        ],
    )

    conn.execute(
        """CREATE TABLE IF NOT EXISTS shopping_list(
            id INTEGER PRIMARY KEY,
            item TEXT NOT NULL,
            item_name TEXT NOT NULL,
            quantity TEXT,
            category TEXT,
            store TEXT,
            priority TEXT,
            notes TEXT,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    _create_indexes(conn, "shopping_list", [("idx_shop_created", "created_date")])

    conn.execute(
        """CREATE TABLE IF NOT EXISTS recipes(
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            source TEXT,
            url TEXT UNIQUE,
            tags TEXT,
            ingredients TEXT,
            instructions TEXT,
            rating REAL DEFAULT 0.0,
            prep_time TEXT DEFAULT '',
            cook_time TEXT DEFAULT '',
            servings INTEGER DEFAULT 0,
            category TEXT DEFAULT 'Main Course',
            description TEXT DEFAULT ''
        )"""
    )
    _create_indexes(
        conn,
        "recipes",
        [
            ("idx_rec_title", "title"),
            ("idx_rec_url", "url"),
        ],
    )
    _add_col(conn, "recipes", "source TEXT")
    _add_col(conn, "recipes", "rating REAL DEFAULT 0.0")
    _add_col(conn, "recipes", "prep_time TEXT DEFAULT ''")
    _add_col(conn, "recipes", "cook_time TEXT DEFAULT ''")
    _add_col(conn, "recipes", "servings INTEGER DEFAULT 0")
    _add_col(conn, "recipes", "difficulty TEXT DEFAULT 'Medium'")
    _add_col(conn, "recipes", "is_favorite INTEGER DEFAULT 0")
    _add_col(conn, "recipes", "image_path TEXT DEFAULT ''")
    
    # Add UPC column to pantry table
    _add_col(conn, "pantry", "upc TEXT")
    
    # Create recipe_ingredients table
    conn.execute(
        """CREATE TABLE IF NOT EXISTS recipe_ingredients(
            id INTEGER PRIMARY KEY,
            recipe_id INTEGER NOT NULL,
            ingredient_name TEXT NOT NULL,
            quantity TEXT,
            unit TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        )"""
    )
    
    # Create categories table
    conn.execute(
        """CREATE TABLE IF NOT EXISTS categories(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            parent_id INTEGER,
            description TEXT,
            color TEXT DEFAULT '#3498db',
            icon TEXT DEFAULT '📁',
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES categories(id)
        )"""
    )
    
    # Create recipe_categories junction table
    conn.execute(
        """CREATE TABLE IF NOT EXISTS recipe_categories(
            recipe_id INTEGER,
            category_id INTEGER,
            PRIMARY KEY (recipe_id, category_id),
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
        )"""
    )
    
    # Insert default categories
    _insert_default_categories(conn)
    
    # Add missing columns to existing tables
    _add_col(conn, "recipes", "category TEXT DEFAULT 'Main Course'")
    _add_col(conn, "recipes", "description TEXT DEFAULT ''")
    _add_col(conn, "shopping_list", "item_name TEXT")
    _add_col(conn, "health_log", "meal_type TEXT DEFAULT 'Breakfast'")
    
    # Create pantry_items view as alias for pantry table
    conn.execute("DROP VIEW IF EXISTS pantry_items")
    conn.execute("CREATE VIEW pantry_items AS SELECT * FROM pantry")

    conn.execute(
        """CREATE TABLE IF NOT EXISTS menu_plan(
            id INTEGER PRIMARY KEY,
            date TEXT,
            meal TEXT,
            recipe_id INTEGER,
            title TEXT,
            notes TEXT
        )"""
    )
    _create_indexes(conn, "menu_plan", [("idx_menu_date", "date")])

    conn.execute(
        """CREATE TABLE IF NOT EXISTS calendar_events(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT,
            event_type TEXT,
            priority TEXT,
            description TEXT,
            reminder TEXT,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    _create_indexes(conn, "calendar_events", [("idx_cal_date", "date")])

    conn.execute(
        """CREATE TABLE IF NOT EXISTS health_log(
            id INTEGER PRIMARY KEY,
            date TEXT,
            time TEXT,
            meal TEXT,
            meal_type TEXT DEFAULT 'Breakfast',
            items TEXT,
            risk TEXT,
            onset_min INTEGER DEFAULT 0,
            severity INTEGER DEFAULT 0,
            stool INTEGER DEFAULT 0,
            recipe TEXT,
            symptoms TEXT,
            notes TEXT
        )"""
    )
    _create_indexes(conn, "health_log", [("idx_health_dt", "date, time")])

    # Gluten Guardian enhancements
    conn.execute(
        """CREATE TABLE IF NOT EXISTS hydration_log(
            id INTEGER PRIMARY KEY,
            date TEXT,
            liters REAL DEFAULT 0.0,
            notes TEXT
        )"""
    )
    _create_indexes(conn, "hydration_log", [("idx_hydration_date", "date")])

    conn.execute(
        """CREATE TABLE IF NOT EXISTS fiber_log(
            id INTEGER PRIMARY KEY,
            date TEXT,
            grams REAL DEFAULT 0.0,
            source TEXT,
            notes TEXT
        )"""
    )
    _create_indexes(conn, "fiber_log", [("idx_fiber_date", "date")])

    conn.execute(
        """CREATE TABLE IF NOT EXISTS bristol_log(
            id INTEGER PRIMARY KEY,
            date TEXT,
            time TEXT,
            type INTEGER CHECK (type >= 1 AND type <= 7),
            notes TEXT
        )"""
    )
    _create_indexes(conn, "bristol_log", [("idx_bristol_dt", "date, time")])

    conn.execute(
        """CREATE TABLE IF NOT EXISTS symptom_patterns(
            id INTEGER PRIMARY KEY,
            pattern_type TEXT,
            detected_date TEXT,
            confidence REAL,
            description TEXT,
            recommendation TEXT
        )"""
    )
    _create_indexes(conn, "symptom_patterns", [("idx_patterns_date", "detected_date")])

    # Add new columns to existing health_log table
    _add_col(conn, "health_log", "hydration_liters REAL DEFAULT 0.0")
    _add_col(conn, "health_log", "fiber_grams REAL DEFAULT 0.0")
    _add_col(conn, "health_log", "mood TEXT DEFAULT ''")
    _add_col(conn, "health_log", "energy_level INTEGER DEFAULT 5")

    _migrate_legacy_health(conn)
    conn.commit()


def _get_flag(conn: sqlite3.Connection, key: str) -> str:
    row = conn.execute("SELECT value FROM app_settings WHERE key=?", (key,)).fetchone()
    return "" if row is None or row[0] is None else str(row[0])


def _set_flag(conn: sqlite3.Connection, key: str, val: str) -> None:
    conn.execute(
        "INSERT INTO app_settings(key,value) VALUES(?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, val),
    )


def _migrate_legacy_health(conn: sqlite3.Connection) -> None:
    if _get_flag(conn, "migrated_health_logs") == "1":
        return
    if not _has_table(conn, "health_logs"):
        _set_flag(conn, "migrated_health_logs", "1")
        return

    legacy = _cols(conn, "health_logs")

    def c(name: str) -> str:
        return name if name in legacy else "NULL"

    sql = f"""
        INSERT INTO health_log(date,time,meal,items,risk,onset_min,severity,stool,recipe,symptoms,notes)
        SELECT
            {c('date')}                                   AS date,
            ''                                            AS time,
            COALESCE({c('meal')},{c('meal_type')})       AS meal,
            {c('meal')}                                   AS items,
            COALESCE({c('risk_level')}, 'UNKNOWN')        AS risk,
            COALESCE({c('onset')}, 0)                     AS onset_min,
            COALESCE({c('severity')}, 0)                  AS severity,
            COALESCE({c('stool_scale')}, 0)               AS stool,
            ''                                            AS recipe,
            COALESCE({c('symptoms')}, '')                 AS symptoms,
            COALESCE({c('notes')}, '')                    AS notes
        FROM health_logs
    """
    try:
        conn.execute(sql)
    finally:
        _set_flag(conn, "migrated_health_logs", "1")
