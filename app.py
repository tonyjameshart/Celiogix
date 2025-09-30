# path: app.py - PATCHED VERSION with GF safety disclaimer
from __future__ import annotations

import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from panels.pantry_panel import PantryPanel
from panels.cookbook_panel import CookbookPanel
from panels.shopping_list_panel import ShoppingListPanel
from panels.health_log_panel import HealthLogPanel
from panels.menu_panel import MenuPanel
from panels.calendar_panel import CalendarPanel
from panels.settings_panel import SettingsPanel


def set_default_geometry_once(root: tk.Tk, geometry: str = "1385x680") -> None:
    try:
        root.update_idletasks()
        root.geometry(geometry)
    except Exception:
        pass


def _default_db_path() -> str:
    base = os.path.join(os.path.expanduser("~"), ".celiogix")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "celiogix.db")


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Celiogix")
        set_default_geometry_once(self, "1385x680")
        self.minsize(900, 520)

        # DB
        self.db_path = _default_db_path()
        self.db = sqlite3.connect(self.db_path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self._ensure_core_tables()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Menu bar
        menubar = tk.Menu(self)
        tools = tk.Menu(menubar, tearoff=0)
        tools.add_command(label="Refresh Current Tab", command=self.refresh_current_tab)
        tools.add_separator()
        tools.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="Tools", menu=tools)
        self.config(menu=menubar)

        # Tabs
        self.nb = ttk.Notebook(self)
        self.nb.grid(row=0, column=0, sticky="nsew")

        # Status
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status_var, anchor="w").grid(row=1, column=0, sticky="ew")

        # Panels
        self.pantry_panel: Optional[PantryPanel] = PantryPanel(master=self.nb, app=self)
        self.nb.add(self.pantry_panel, text="Pantry")

        self.cookbook_panel: Optional[CookbookPanel] = CookbookPanel(master=self.nb, app=self)
        self.nb.add(self.cookbook_panel, text="Cookbook")

        self.shopping_list_panel: Optional[ShoppingListPanel] = ShoppingListPanel(master=self.nb, app=self)
        self.nb.add(self.shopping_list_panel, text="Shopping")

        self.health_log_panel: Optional[HealthLogPanel] = HealthLogPanel(master=self.nb, app=self)
        self.nb.add(self.health_log_panel, text="Health Log")

        self.menu_panel: Optional[MenuPanel] = MenuPanel(master=self.nb, app=self)
        self.nb.add(self.menu_panel, text="Menu")

        self.calendar_panel: Optional[CalendarPanel] = CalendarPanel(master=self.nb, app=self)
        self.nb.add(self.calendar_panel, text="Calendar")

        self.settings_panel: Optional[SettingsPanel] = SettingsPanel(master=self.nb, app=self)
        self.nb.add(self.settings_panel, text="Settings")

        self.nb.enable_traversal()
        self.nb.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        
        # Show GF disclaimer on first run
        self.after(500, self._show_gf_disclaimer_once)

    # ---------- DB ----------
    def _ensure_core_tables(self) -> None:
        c = self.db.cursor()

        # Helpers
        def cols(table: str) -> set[str]:
            try:
                return {r[1] for r in self.db.execute(f"PRAGMA table_info({table})").fetchall()}
            except Exception:
                return set()

        def ensure_col(table: str, name: str, ddl: str) -> None:
            if name not in cols(table):
                try:
                    c.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")
                except Exception:
                    pass

        # Recipes
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                source TEXT,
                url TEXT,
                tags TEXT,
                ingredients TEXT,
                instructions TEXT,
                rating REAL DEFAULT 0.0,
                prep_time TEXT,
                cook_time TEXT,
                servings INTEGER DEFAULT 0,
                favorite INTEGER NOT NULL DEFAULT 0,
                notes TEXT
            )
            """
        )
        c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_recipes_url_unique ON recipes(url)")

        # Pantry
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS pantry (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                brand TEXT,
                category TEXT,
                subcategory TEXT,
                store TEXT,
                quantity REAL DEFAULT 0,
                net_weight TEXT,
                gf_flag TEXT,
                tags TEXT,
                notes TEXT
            )
            """
        )

        # Shopping list
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS shopping_list (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                brand TEXT,
                category TEXT,
                net_weight REAL,
                thresh REAL,
                store TEXT,
                notes TEXT
            )
            """
        )

        # Menu planner
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS menu_plan (
                id INTEGER PRIMARY KEY,
                date TEXT NOT NULL,
                meal TEXT,
                recipe_id INTEGER,
                title TEXT,
                notes TEXT
            )
            """
        )

        # Health log
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS health_log (
                id INTEGER PRIMARY KEY,
                date TEXT,
                time TEXT,
                meal TEXT,
                items TEXT,
                risk TEXT,
                severity INTEGER DEFAULT 0,
                stool INTEGER DEFAULT 0,
                recipe TEXT,
                symptoms TEXT,
                notes TEXT,
                onset_min INTEGER DEFAULT 0
            )
            """
        )
        # Migrate old schema variants
        ensure_col("health_log", "date", "date TEXT")
        ensure_col("health_log", "time", "time TEXT")
        ensure_col("health_log", "meal", "meal TEXT")
        ensure_col("health_log", "items", "items TEXT")
        ensure_col("health_log", "risk", "risk TEXT")
        ensure_col("health_log", "severity", "severity INTEGER DEFAULT 0")
        ensure_col("health_log", "stool", "stool INTEGER DEFAULT 0")
        ensure_col("health_log", "recipe", "recipe TEXT")
        ensure_col("health_log", "symptoms", "symptoms TEXT")
        ensure_col("health_log", "notes", "notes TEXT")
        ensure_col("health_log", "onset_min", "onset_min INTEGER DEFAULT 0")

        self.db.commit()

    # ---------- GF Safety Disclaimer ----------
    def _show_gf_disclaimer_once(self) -> None:
        """Show gluten-free safety disclaimer on first launch."""
        try:
            flag = self.db.execute(
                "SELECT value FROM app_settings WHERE key='gf_disclaimer_shown'"
            ).fetchone()
            
            if flag and flag[0] == '1':
                return  # Already shown
            
            # Show disclaimer
            response = messagebox.showwarning(
                "Gluten-Free Safety Feature",
                "Celiogix includes automated gluten content analysis to assist with dietary management.\n\n"
                "⚠️  IMPORTANT MEDICAL DISCLAIMER:\n\n"
                "This is a SCREENING TOOL ONLY, not a medical device.\n\n"
                "• The algorithm analyzes ingredient text for gluten-related terms\n"
                "• It cannot replace careful reading of actual product labels\n"
                "• False negatives are possible (unsafe items marked safe)\n"
                "• Always verify ingredients yourself before consumption\n"
                "• Consult healthcare providers for medical advice\n\n"
                "Cross-contact warnings override all other signals.\n"
                "Green ✓ = likely safe | Yellow ⚠ = ambiguous | Red ✗ = risk detected\n\n"
                "By using this feature, you acknowledge these limitations.",
                parent=self,
                type=messagebox.OK,
                icon=messagebox.WARNING
            )
            
            # Record that disclaimer was shown
            self.db.execute(
                """
                INSERT INTO app_settings(key, value) VALUES('gf_disclaimer_shown', '1')
                ON CONFLICT(key) DO UPDATE SET value='1'
                """
            )
            self.db.commit()
            
        except Exception:
            # Don't crash if disclaimer fails to show
            pass

    # ---------- App helpers ----------
    def _on_close(self) -> None:
        try:
            self.db.commit()
            self.db.close()
        except Exception:
            pass
        self.destroy()

    def set_status(self, msg: str) -> None:
        self.status_var.set(msg)

    def _on_tab_changed(self, _e=None) -> None:
        cur = self.nb.select()
        w = self.nametowidget(cur)
        if hasattr(w, "on_tab_activated"):
            try:
                w.on_tab_activated()
            except Exception:
                pass
        self.set_status("Ready")

    def refresh_current_tab(self) -> None:
        cur = self.nb.select()
        w = self.nametowidget(cur)
        for meth in ("refresh", "refresh_list", "refresh_library", "reload"):
            if hasattr(w, meth):
                try:
                    getattr(w, meth)()
                    self.set_status("Refreshed")
                    return
                except Exception:
                    break
        self.set_status("No refresh hook on this tab")