# path: utils/migrations.py
from __future__ import annotations
import sqlite3

# ---- tiny helpers -----------------------------------------------------------
def _cols(conn: sqlite3.Connection, table: str) -> set[str]:
    try:
        return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
    except Exception:
        return set()

def _has_table(conn: sqlite3.Connection, name: str) -> bool:
    cur = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=? COLLATE NOCASE", (name,))
    return cur.fetchone() is not None

def _add_col(conn: sqlite3.Connection, table: str, coldef: str) -> None:
    name = coldef.split()[0]
    if name not in _cols(conn, table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {coldef}")

# ---- public ----------------------------------------------------------------
def ensure_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    conn.execute("PRAGMA foreign_keys = ON;")

    # app settings (future flags)
    cur.execute("""CREATE TABLE IF NOT EXISTS app_settings(
        key TEXT PRIMARY KEY, value TEXT
    )""")

    # pantry
    cur.execute("""CREATE TABLE IF NOT EXISTS pantry(
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
    )""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pantry_name ON pantry(name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pantry_cat  ON pantry(category)")

    # shopping list
    cur.execute("""CREATE TABLE IF NOT EXISTS shopping_list(
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        brand TEXT,
        category TEXT,
        net_weight REAL DEFAULT 0,
        thresh REAL DEFAULT 0,
        store TEXT,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_shop_created ON shopping_list(created_at)")

    # recipes (compact but complete for panels)
    cur.execute("""CREATE TABLE IF NOT EXISTS recipes(
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
        servings INTEGER DEFAULT 0
    )""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_rec_title ON recipes(title)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_rec_url   ON recipes(url)")
    # in case upgrading from older schemas:
    _add_col(conn, "recipes", "source TEXT")
    _add_col(conn, "recipes", "rating REAL DEFAULT 0.0")
    _add_col(conn, "recipes", "prep_time TEXT DEFAULT ''")
    _add_col(conn, "recipes", "cook_time TEXT DEFAULT ''")
    _add_col(conn, "recipes", "servings INTEGER DEFAULT 0")

    # menu plan
    cur.execute("""CREATE TABLE IF NOT EXISTS menu_plan(
        id INTEGER PRIMARY KEY,
        date TEXT,            -- YYYY-MM-DD
        meal TEXT,            -- Breakfast/Lunch/Dinner/Snack/Other
        recipe_id INTEGER,    -- FK -> recipes.id (nullable)
        title TEXT,           -- snapshot of recipe title
        notes TEXT
    )""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_menu_date ON menu_plan(date)")

    # health log (used by Health panel; stool = Bristol code int)
    cur.execute("""CREATE TABLE IF NOT EXISTS health_log(
        id INTEGER PRIMARY KEY,
        date TEXT,
        time TEXT,
        meal TEXT,
        items TEXT,
        risk TEXT,
        onset_min INTEGER DEFAULT 0,
        severity INTEGER DEFAULT 0,
        stool INTEGER DEFAULT 0,   -- 0..7
        recipe TEXT,
        symptoms TEXT,
        notes TEXT
    )""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_health_dt ON health_log(date, time)")
    # if migrating from a legacy 'health_logs' table, do a one-shot copy:
    _maybe_migrate_legacy_health(conn)

    # search URLs (Settings → Search URLs tab)
    cur.execute("""CREATE TABLE IF NOT EXISTS search_urls(
        id INTEGER PRIMARY KEY,
        url TEXT UNIQUE,
        label TEXT,
        enabled INTEGER DEFAULT 1
    )""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_urls_enabled ON search_urls(enabled)")

    conn.commit()

# ---- small one-shot migration ----------------------------------------------
def _get_flag(conn: sqlite3.Connection, key: str) -> str:
    row = conn.execute("SELECT value FROM app_settings WHERE key=?", (key,)).fetchone()
    return row[0] if row and row[0] is not None else ""

def _set_flag(conn: sqlite3.Connection, key: str, val: str) -> None:
    conn.execute("INSERT INTO app_settings(key,value) VALUES(?,?) "
                 "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, val))

def _maybe_migrate_legacy_health(conn: sqlite3.Connection) -> None:
    if _get_flag(conn, "migrated_health_logs") == "1":  # already done
        return
    if not _has_table(conn, "health_logs"):
        _set_flag(conn, "migrated_health_logs", "1"); return

    legacy = _cols(conn, "health_logs")
    def c(name: str) -> str: return name if name in legacy else "NULL"

    # best-effort field mapping
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
        conn.commit()
