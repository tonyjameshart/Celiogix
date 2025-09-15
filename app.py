# path: app.py (fixed)
from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Tuple, Optional

from utils.logger import init_logging
LOG_PATH = init_logging()

from utils.db import get_connection
from utils.migrations import ensure_schema
from utils.factory_reset import factory_reset
from panels.settings_panel import SettingsPanel  # ensure Settings is available for the modal

# Label, module path, class name
PANEL_BUILDERS: List[Tuple[str, str, str]] = [
    ("Pantry",       "panels.pantry_panel",        "PantryPanel"),
    ("Cookbook",     "panels.cookbook_panel",      "CookbookPanel"),
    ("Shopping",     "panels.shopping_list_panel", "ShoppingListPanel"),
    ("Health Log",   "panels.health_log_panel",    "HealthLogPanel"),
    ("Menu",         "panels.menu_panel",          "MenuPanel"),
    ("Calendar",     "panels.calendar_panel",      "CalendarPanel"),
]


class _SimpleTheme:
    spacing = {"sm": 4, "md": 8, "lg": 12}


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Celiogix")
        self.minsize(980, 620)

        # --- Logging
        self.logger = logging.getLogger("Celiogix.App")

        # --- SQLite: open + migrate
        self.db: sqlite3.Connection = get_connection()
        ensure_schema(self.db)

        # --- theme and ttk styles
        self.theme = _SimpleTheme()
        st = ttk.Style(self)
        try:
            st.theme_use(st.theme_use())
        except Exception:
            pass
        st.configure("Card.TFrame", relief="flat")
        st.configure("Muted.TLabel", foreground="#666666")

        # --- menubar (Tools → Settings…, Factory Reset…)
        self._settings_win: Optional[tk.Toplevel] = None  # single-instance tracker
        menubar = tk.Menu(self)
        tools = tk.Menu(menubar, tearoff=0)
        tools.add_command(label="Settings…", command=self._open_settings_dialog, accelerator="Ctrl+,")
        tools.add_separator()
        tools.add_command(label="Factory Reset…", command=self._factory_reset_dialog)
        menubar.add_cascade(label="Tools", menu=tools)
        self.config(menu=menubar)
        self._menubar = menubar
        self.bind_all("<Control-comma>", lambda e: self._open_settings_dialog())

        # --- layout
        root = ttk.Frame(self, padding=(8, 8))
        root.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.nav = ttk.Frame(root, padding=(8, 8), style="Card.TFrame")
        self.nav.grid(row=0, column=0, rowspan=3, sticky="nsw")

        self.actions = ttk.Frame(root, padding=(8, 6), style="Card.TFrame")
        self.actions.grid(row=0, column=1, sticky="new")

        self.content = ttk.Frame(root, padding=(8, 8))
        self.content.grid(row=1, column=1, sticky="nsew")

        status_bar = ttk.Frame(root, padding=(8, 6), style="Card.TFrame")
        status_bar.grid(row=2, column=1, sticky="sew")
        self._status = tk.StringVar(value="Ready")
        ttk.Label(status_bar, textvariable=self._status, style="Muted.TLabel").grid(row=0, column=0, sticky="w")

        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(1, weight=1)

        # --- keep *all* panel specs; import lazily on selection
        self._panel_specs: Dict[str, Tuple[str, str]] = {label: (mod, cls) for (label, mod, cls) in PANEL_BUILDERS}
        self._panel_types: Dict[str, type] = {}         # cached constructors after first successful import
        self._panels: Dict[str, tk.Widget] = {}         # instantiated panel widgets
        self._current_key: Optional[str] = None

        # --- nav buttons (always create)
        for i, (label, _spec) in enumerate(self._panel_specs.items()):  # noqa: B007
            ttk.Button(self.nav, text=label, width=20, command=lambda k=label: self.show_panel(k)).grid(
                row=i, column=0, sticky="ew", pady=(0, 6)
            )

        # close handling (dashboard_app.py closes DB; we destroy the window)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # open first panel
        if self._panel_specs:
            self.show_panel(next(iter(self._panel_specs.keys())))

    # --------- status API ----------
    def set_status(self, msg: str) -> None:
        self._status.set(msg or "")

    # --------- window close ----------
    def _on_close(self) -> None:
        try:
            # Graceful close if needed (e.g., flushing logs/DB)
            pass
        finally:
            self.destroy()

    # --------- dynamic loader ----------
    def _get_panel_ctor(self, key: str) -> type:
        # return cached if available
        ctor = self._panel_types.get(key)
        if ctor is not None:
            return ctor
        # import on demand
        try:
            mod_name, cls_name = self._panel_specs[key]
            mod = __import__(mod_name, fromlist=[cls_name])
            ctor = getattr(mod, cls_name)
            self._panel_types[key] = ctor
            return ctor
        except Exception as e:
            messagebox.showerror("Panel Load Error", f"Couldn’t load panel '{key}':\n{e}", parent=self)
            raise

    def _instantiate_panel(self, ctor: type) -> tk.Widget:
        return ctor(self.content, self)  # panels expect (master, app)

    # --------- panel mgmt ----------
    def show_panel(self, key: str) -> None:
        if key == self._current_key:
            return
        # hide current
        if self._current_key and self._current_key in self._panels:
            self._panels[self._current_key].grid_forget()

        # build or reuse
        p = self._panels.get(key)
        if p is None:
            try:
                ctor = self._get_panel_ctor(key)
                p = self._instantiate_panel(ctor)
                self._panels[key] = p
            except Exception:
                # failed to create; revert to previous if exists
                self.set_status(f"{key}: failed to load (see error)")
                return

        # show
        p.grid(row=0, column=0, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        self._current_key = key

        # actions bar
        self._rebuild_actions(p, key)
        self.set_status(f"{key} ready")

    # --------- actions toolbar ----------
    def _rebuild_actions(self, panel: tk.Widget, key: str) -> None:
        for child in list(self.actions.winfo_children()):
            child.destroy()

        def add(label: str, method_names: List[str]) -> None:
            for name in method_names:
                fn = getattr(panel, name, None)
                if callable(fn):
                    ttk.Button(self.actions, text=label, command=fn).pack(side="left", padx=(0, 6))
                    return

        # Keep toolbar lean; avoid duplicates with context menus.
        if key in ("Pantry", "Cookbook", "Shopping"):
            add("Add", ["add_item", "add"])  # right-click handles edit/delete/export
            return

        if key == "Health Log":
            add("Add", ["add_item", "add"])
            add("Edit", ["edit_selected", "edit"])
            add("Delete", ["delete_selected", "delete"])
            add("Export HTML", ["export_html"])
            add("Export CSV", ["export_csv"])
        elif key == "Menu":
            add("Add", ["add_item", "add"])
            add("Generate Shopping List", ["generate_shopping_list"])
        # Settings: live inside modal dialog

    # ---------- Tools: Factory Reset ----------
    def _factory_reset_dialog(self):
        msg = (
            "Factory Reset will:\n"
            "• Backup your database to the backups/ folder\n"
            "• Delete the database (app.db, -wal, -shm)\n"
            "• Keep logs and exports (you can wipe them too)\n\n"
            "Proceed?"
        )
        if not messagebox.askyesno("Factory Reset", msg, icon="warning", default="no"):
            return

        # Optional extra wipe prompt
        wipe_more = messagebox.askyesno(
            "Reset Options",
            "Also wipe logs and exports? (Backed up first)",
            icon="question",
            default="no",
        )

        try:
            backup_zip = factory_reset(
                self.db,
                project_root=Path(__file__).resolve().parents[0],  # adjust if your app root differs
                backup=True,
                wipe_logs=wipe_more,
                wipe_exports=wipe_more,
                logger=getattr(self, "logger", None),
                restart_after=True,
            )
            # If auto-restart works, we won't reach here.
            messagebox.showinfo(
                "Factory Reset complete",
                f"Backup saved to:\n{backup_zip}\n\nPlease restart the app.",
            )
        except Exception as e:
            # If something blocks deletion, show details and capture in log
            if getattr(self, "logger", None):
                self.logger.exception("Factory Reset failed: %s", e)
            messagebox.showerror("Factory Reset failed", str(e))

    # ---------- Tools: Settings (modal) ----------
    def _open_settings_dialog(self):
        # Reuse if already open
        if self._settings_win and self._settings_win.winfo_exists():
            self._settings_win.lift()
            self._settings_win.focus_force()
            return

        win = tk.Toplevel(self)
        win.title("Settings")
        win.transient(self)
        win.grab_set()               # modal
        win.resizable(False, False)
        win.protocol("WM_DELETE_WINDOW", win.destroy)

        # Container for the panel
        wrap = ttk.Frame(win, padding=8)
        wrap.pack(fill="both", expand=True)

        # Mount the existing SettingsPanel (unchanged)
        panel = SettingsPanel(wrap, self)  # BasePanel subclass; master=wrap, app=self
        try:
            panel.pack(fill="both", expand=True)  # works because BasePanel is a Frame
        except Exception:
            # If your BasePanel uses grid internally, this still works since we're packing the outer Frame.
            pass

        # Keep a handle to avoid multiple windows
        self._settings_win = win

        # Center roughly on parent
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (win.winfo_reqwidth() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (win.winfo_reqheight() // 2)
        win.geometry(f"+{max(0,x)}+{max(0,y)}")
