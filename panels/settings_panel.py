# path: panels/settings_panel.py
from __future__ import annotations

import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, colorchooser
import csv
import json
from typing import List, Dict, Any, Optional, Tuple

from panels.base_panel import BasePanel
from services.themes import (
    list_theme_names,
    get_theme as load_theme_spec,
    save_theme as persist_theme,
    delete_theme as remove_theme,
    set_active_theme,
    get_active_theme_name,
    make_theme_instance,
)

# --- scroll container (vertical + optional horizontal, with forced overflow) --
class _ScrollFrame(ttk.Frame):
    """
    Canvas + inner body frame + scrollbars.
    - xscroll=True enables horizontal scrolling.
    - force_hscroll=True keeps the inner window a bit wider than the canvas so
      the horizontal scrollbar is guaranteed to appear (useful for Notebook tabs).
    """
    def __init__(self, parent, *, xscroll: bool = False, force_hscroll: bool = False, hoffset: int = 200, **kwargs):
        super().__init__(parent, **kwargs)
        self.xscroll_enabled = bool(xscroll)
        self.force_hscroll = bool(force_hscroll)
        self.hoffset = int(hoffset)

        self.canvas = tk.Canvas(self, highlightthickness=0, borderwidth=0)
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.hsb = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview) if self.xscroll_enabled else None

        if self.xscroll_enabled:
            self.canvas.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        else:
            self.canvas.configure(yscrollcommand=self.vsb.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vsb.grid(row=0, column=1, sticky="ns")
        if self.hsb:
            self.hsb.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # inner body where real content lives
        self.body = ttk.Frame(self)
        self._win = self.canvas.create_window((0, 0), window=self.body, anchor="nw")

        # update scrollregion and sizing
        self.body.bind("<Configure>", self._on_body_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # mouse-wheel scrolling (Win/macOS) + Linux buttons
        for w in (self.canvas, self.body):
            w.bind("<Enter>", lambda _e: self.canvas.focus_set())
            w.bind("<MouseWheel>", self._on_mousewheel)            # Win/macOS
            w.bind("<Button-4>", self._on_linux_scroll_up)         # Linux
            w.bind("<Button-5>", self._on_linux_scroll_down)
            w.bind("<Shift-MouseWheel>", self._on_mousewheel_x)
            w.bind("<Shift-Button-4>", self._on_linux_scroll_left)
            w.bind("<Shift-Button-5>", self._on_linux_scroll_right)

        # match theme background
        try:
            bg = ttk.Style().lookup("TFrame", "background") or self.cget("background")
            self.canvas.configure(background=bg)
        except Exception:
            pass

    def _on_body_configure(self, _e=None):
        # keep scrollregion correct
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, e=None):
        cw = self.canvas.winfo_width()

        if not self.xscroll_enabled:
            # Tie width to canvas when horizontal scrolling is off
            self.canvas.itemconfigure(self._win, width=cw)
        else:
            # If forcing horizontal visibility, keep inner width > canvas width
            if self.force_hscroll:
                req = self.body.winfo_reqwidth()
                target = max(req, cw + max(1, self.hoffset))
                self.canvas.itemconfigure(self._win, width=target)
            else:
                # Natural width (requested) to allow overflow only when content requires it
                self.canvas.itemconfigure(self._win, width=self.body.winfo_reqwidth())

        # Height is always natural; vertical scrollbar appears when content taller than canvas.

    # wheel handlers
    def _on_mousewheel(self, e):
        self.canvas.yview_scroll(-1 if e.delta > 0 else 1, "units")

    def _on_mousewheel_x(self, e):
        if not self.xscroll_enabled:
            return
        self.canvas.xview_scroll(-1 if e.delta > 0 else 1, "units")

    def _on_linux_scroll_up(self, _e):   self.canvas.yview_scroll(-1, "units")
    def _on_linux_scroll_down(self, _e): self.canvas.yview_scroll(+1, "units")
    def _on_linux_scroll_left(self, _e):
        if self.xscroll_enabled: self.canvas.xview_scroll(-1, "units")
    def _on_linux_scroll_right(self, _e):
        if self.xscroll_enabled: self.canvas.xview_scroll(+1, "units")


# ---- small helpers ----
def _ci_map(header_row: List[str]) -> Dict[str, int]:
    """case-insensitive header -> index"""
    return {(h or "").strip().lower(): i for i, h in enumerate(header_row)}

def _read_csv_rows(path: str) -> List[List[str]]:
    rows: List[List[str]] = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        sniffer = csv.Sniffer()
        content = f.read()
        f.seek(0)
        dialect = sniffer.sniff(content[:4096]) if content else csv.excel
        reader = csv.reader(f, dialect)
        for r in reader:
            if not any((cell or "").strip() for cell in r):
                continue
            rows.append(r)
    return rows


class SettingsPanel(BasePanel):
    """Settings with Notebook tabs: General, Import/Export, Search URLs, Categories, Theme."""

    # --- convenience wrappers so self.info(...) never collides with tk.Pack ---
    def info(self, msg: str) -> None:
        try:
            self.set_status(msg)
        except Exception:
            pass
        try:
            messagebox.showinfo("Settings", msg, parent=self.winfo_toplevel())
        except Exception:
            pass

    def warn(self, msg: str) -> None:
        try:
            self.set_status(msg)
        except Exception:
            pass
        try:
            messagebox.showwarning("Settings", msg, parent=self.winfo_toplevel())
        except Exception:
            pass

    def error(self, msg: str) -> None:
        try:
            self.set_status(msg)
        except Exception:
            pass
        try:
            messagebox.showerror("Settings", msg, parent=self.winfo_toplevel())
        except Exception:
            pass

    # ------------- UI build -------------
    def build(self) -> None:
        self._ensure_search_urls_table()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        nb = ttk.Notebook(self)
        nb.grid(row=0, column=0, sticky="nsew")

        # Tabs
        t_general = ttk.Frame(nb)
        t_io = ttk.Frame(nb)
        t_urls = ttk.Frame(nb)
        t_cats = ttk.Frame(nb)
        t_theme = ttk.Frame(nb)

        nb.add(t_general, text="General")
        nb.add(t_io, text="Import / Export")
        nb.add(t_urls, text="Search URLs")
        nb.add(t_cats, text="Categories")
        nb.add(t_theme, text="Theme")

        # ---- General tab ----
        self._build_general(t_general)
        # ---- Import/Export (Pantry/Cookbook/Shopping + Bulk UPC) ----
        self._build_io(t_io)
        # ---- Search URLs ----
        self._build_urls(t_urls)
        # ---- Categories (Category + Subcategory) ----
        self._build_categories(t_cats)
        # ---- Theme (granular customizations + JSON import/export + scrolling) ----
        self._build_theme(t_theme)

    # ------------- General -------------
    def _build_general(self, parent: tk.Widget) -> None:
        box = ttk.Frame(parent, padding=10)
        box.pack(fill="both", expand=True)

        ttk.Label(box, text="Celiac Culinary – Settings", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 6))
        # show DB path if available
        db_path = ""
        try:
            row = self.db.execute("PRAGMA database_list").fetchone()
            if row and len(row) >= 3:
                db_path = row[2] or ""
        except Exception:
            pass
        ttk.Label(box, text=f"Database: {db_path or '(in-memory or unknown)'}").pack(anchor="w")

        ttk.Separator(box).pack(fill="x", pady=10)
        ttk.Label(box, text="Theme applied.", style="Muted.TLabel").pack(anchor="w")

    # ------------- Import / Export -------------
    def _build_io(self, parent: tk.Widget) -> None:
        pad = dict(padx=10, pady=6)
        parent.grid_columnconfigure(1, weight=1)

        # Pantry
        ttk.Label(parent, text="Pantry", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", **pad)
        pbtns = ttk.Frame(parent); pbtns.grid(row=0, column=1, sticky="w", **pad)
        ttk.Button(pbtns, text="Import CSV", command=self._import_pantry_csv).pack(side="left")
        ttk.Button(pbtns, text="Export CSV", command=self._export_pantry_csv).pack(side="left", padx=(8,0))

        # Cookbook
        ttk.Label(parent, text="Cookbook", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", **pad)
        cbtns = ttk.Frame(parent); cbtns.grid(row=1, column=1, sticky="w", **pad)
        ttk.Button(cbtns, text="Import CSV", command=self._import_recipes_csv).pack(side="left")
        ttk.Button(cbtns, text="Export CSV", command=self._export_recipes_csv).pack(side="left", padx=(8,0))

        # Shopping
        ttk.Label(parent, text="Shopping List", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", **pad)
        sbtns = ttk.Frame(parent); sbtns.grid(row=2, column=1, sticky="w", **pad)
        ttk.Button(sbtns, text="Import CSV", command=self._import_shopping_csv).pack(side="left")
        ttk.Button(sbtns, text="Export CSV", command=self._export_shopping_csv).pack(side="left", padx=(8,0))

        # UPC Bulk
        ttk.Label(parent, text="Pantry – Bulk Add by UPC", font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky="w", **pad)
        ubtns = ttk.Frame(parent); ubtns.grid(row=3, column=1, sticky="w", **pad)
        ttk.Button(ubtns, text="Import UPCs (CSV/TXT)", command=self._import_upcs_file).pack(side="left")
        ttk.Label(parent, text="CSV: header 'upc' or first column used; TXT: one UPC per line.", style="Muted.TLabel").grid(row=4, column=1, sticky="w", padx=10)

    # ---- IO: generic helpers ----
    def _table_exists(self, name: str) -> bool:
        try:
            r = self.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone()
            return bool(r)
        except Exception:
            return False

    def _table_columns(self, table: str) -> List[str]:
        try:
            rows = self.db.execute(f"PRAGMA table_info({table})").fetchall()
            return [r[1] for r in rows]
        except Exception:
            return []

    def _export_table_to_csv(self, table: str, *, default_name: Optional[str] = None) -> None:
        if not self._table_exists(table):
            self.error(f"Table '{table}' not found.")
            return
        cols = self._table_columns(table)
        if not cols:
            self.error(f"No columns found for table '{table}'.")
            return
        path = filedialog.asksaveasfilename(
            title=f"Export '{table}' to CSV",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile=(default_name or f"{table}.csv"),
        )
        if not path:
            return
        try:
            rows = self.db.execute(f"SELECT {', '.join(cols)} FROM {table}").fetchall()
            with open(path, "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(cols)
                for r in rows:
                    if isinstance(r, sqlite3.Row):
                        w.writerow([r[c] for c in cols])
                    else:
                        w.writerow(list(r))
            self.info(f"Exported {len(rows)} row(s) from '{table}'.")
        except Exception as e:
            self.error(f"Failed to export '{table}':\n{e!s}")

    def _import_csv_into_table(self, table: str) -> None:
        if not self._table_exists(table):
            self.error(f"Table '{table}' not found.")
            return
        path = filedialog.askopenfilename(
            title=f"Import CSV into '{table}'",
            filetypes=[("CSV", "*.csv"), ("All Files", "*.*")],
        )
        if not path:
            return
        try:
            rows = _read_csv_rows(path)
            if not rows:
                self.warn("File appears to be empty.")
                return
            header = rows[0]
            csv_cols_ci = _ci_map(header)
            table_cols = self._table_columns(table)
            if not table_cols:
                self.error(f"Could not read columns for table '{table}'.")
                return

            # choose intersection, keep DB order
            use_cols = [c for c in table_cols if c.lower() in csv_cols_ci]
            if not use_cols:
                self.error("No matching columns between CSV header and table schema.")
                return

            data = []
            for r in rows[1:]:
                vals = []
                for c in use_cols:
                    idx = csv_cols_ci[c.lower()]
                    vals.append(r[idx] if idx < len(r) else None)
                data.append(tuple(vals))

            with self.db:
                placeholders = ",".join(["?"] * len(use_cols))
                sql = f"INSERT INTO {table} ({', '.join(use_cols)}) VALUES ({placeholders})"
                self.db.executemany(sql, data)

            self.info(f"Imported {len(data)} row(s) into '{table}'.")
            if table == "search_urls":
                self._urls_refresh()
        except Exception as e:
            self.error(f"Failed to import into '{table}':\n{e!s}")

    # ---- IO: specific button handlers ----
    def _export_pantry_csv(self) -> None:
        self._export_table_to_csv("pantry", default_name="pantry.csv")

    def _import_pantry_csv(self) -> None:
        self._import_csv_into_table("pantry")

    def _export_recipes_csv(self) -> None:
        t = self._pick_recipes_table()
        if not t:
            return
        self._export_table_to_csv(t, default_name=f"{t}.csv")

    def _import_recipes_csv(self) -> None:
        t = self._pick_recipes_table()
        if not t:
            return
        self._import_csv_into_table(t)

    def _export_shopping_csv(self) -> None:
        t = self._pick_shopping_table()
        if not t:
            return
        self._export_table_to_csv(t, default_name=f"{t}.csv")

    def _import_shopping_csv(self) -> None:
        t = self._pick_shopping_table()
        if not t:
            return
        self._import_csv_into_table(t)

    def _pick_recipes_table(self) -> Optional[str]:
        for cand in ("recipes", "cookbook", "recipe"):
            if self._table_exists(cand):
                return cand
        self.error("No recipes/cookbook table found (tried: recipes, cookbook, recipe).")
        return None

    def _pick_shopping_table(self) -> Optional[str]:
        for cand in ("shopping_list", "shopping", "groceries"):
            if self._table_exists(cand):
                return cand
        self.error("No shopping list table found (tried: shopping_list, shopping, groceries).")
        return None

    def _import_upcs_file(self) -> None:
        if not self._table_exists("pantry"):
            self.error("Table 'pantry' not found.")
            return
        cols = self._table_columns("pantry")
        if "upc" not in [c.lower() for c in cols]:
            self.error("The 'pantry' table has no 'upc' column.")
            return

        path = filedialog.askopenfilename(
            title="Import UPCs (CSV/TXT)",
            filetypes=[("CSV/TXT", "*.csv;*.txt"), ("CSV", "*.csv"), ("Text", "*.txt"), ("All Files", "*.*")],
        )
        if not path:
            return

        # read UPCs
        upcs: List[str] = []
        try:
            if path.lower().endswith(".txt"):
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        s = (line or "").strip()
                        if s:
                            upcs.append(s)
            else:
                rows = _read_csv_rows(path)
                if not rows:
                    self.warn("File appears to be empty.")
                    return
                hdr = _ci_map(rows[0])
                if "upc" in hdr:
                    for r in rows[1:]:
                        if hdr["upc"] < len(r):
                            s = (r[hdr["upc"]] or "").strip()
                            if s:
                                upcs.append(s)
                else:
                    # first column fallback
                    for r in rows[1:]:
                        if r and (r[0] or "").strip():
                            upcs.append(r[0].strip())
        except Exception as e:
            self.error(f"Failed to read UPC file:\n{e!s}")
            return

        # insert UPCs if not present
        inserted = 0
        skipped = 0
        try:
            with self.db:
                for u in upcs:
                    row = self.db.execute("SELECT id FROM pantry WHERE upc = ?", (u,)).fetchone()
                    if row:
                        skipped += 1
                        continue
                    try:
                        self.db.execute("INSERT INTO pantry(upc) VALUES (?)", (u,))
                        inserted += 1
                    except Exception:
                        skipped += 1
        except Exception as e:
            self.error(f"Failed to import UPCs:\n{e!s}")
            return

        self.info(f"UPCs processed → inserted: {inserted}, skipped: {skipped}")

    # ------------- Search URLs -------------
    def _ensure_search_urls_table(self) -> None:
        try:
            self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS search_urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE,
                    label TEXT,
                    enabled INTEGER
                )
                """
            )
            self.db.commit()
        except Exception:
            pass

    def _build_urls(self, parent: tk.Widget) -> None:
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        # toolbar
        bar = ttk.Frame(parent, padding=(8, 6))
        bar.grid(row=0, column=0, sticky="ew")
        ttk.Button(bar, text="Add", command=self._urls_add).pack(side="left")
        ttk.Button(bar, text="Edit", command=self._urls_edit).pack(side="left", padx=(6, 0))
        ttk.Button(bar, text="Delete", command=self._urls_delete).pack(side="left", padx=(6, 0))
        ttk.Button(bar, text="Import…", command=self._urls_import).pack(side="left", padx=(12, 0))
        ttk.Button(bar, text="Export…", command=self._urls_export).pack(side="left", padx=(6, 0))

        # table
        tv = ttk.Treeview(parent, columns=("url", "label", "enabled"), show="headings", selectmode="extended")
        tv.heading("url", text="URL")
        tv.heading("label", text="Label")
        tv.heading("enabled", text="Enabled")
        tv.column("url", width=360, anchor="w")
        tv.column("label", width=160, anchor="w")
        tv.column("enabled", width=90, anchor="center")
        tv.grid(row=1, column=0, sticky="nsew")
        self._urls_tree = tv

        vsb = ttk.Scrollbar(parent, orient="vertical", command=tv.yview)
        tv.configure(yscroll=vsb.set)
        vsb.grid(row=1, column=1, sticky="ns")

        self._urls_refresh()

    def _urls_refresh(self) -> None:
        tv = getattr(self, "_urls_tree", None)
        if not isinstance(tv, ttk.Treeview):
            return
        for it in tv.get_children():
            tv.delete(it)
        rows = self.db.execute(
            """
            SELECT id, url, COALESCE(label,'') AS label, IFNULL(enabled,1) AS enabled
              FROM search_urls
             ORDER BY LOWER(url)
            """
        ).fetchall()
        for r in rows:
            tv.insert("", "end", iid=str(r["id"]), values=[r["url"], r["label"], "yes" if r["enabled"] else "no"])
        self.set_status(f"{len(rows)} URL(s) configured")

    def _urls_add(self) -> None:
        url = simpledialog.askstring("Add URL", "Enter URL:", parent=self.winfo_toplevel())
        if not url:
            return
        label = simpledialog.askstring("Add URL", "Label (optional):", parent=self.winfo_toplevel()) or ""
        self.db.execute("INSERT OR IGNORE INTO search_urls(url, label, enabled) VALUES(?,?,1)", (url.strip(), label.strip()))
        self.db.commit()
        self._urls_refresh()

    def _urls_edit(self) -> None:
        tv = getattr(self, "_urls_tree", None)
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        if len(sel) != 1:
            messagebox.showinfo("Search URLs", "Select one item to edit.", parent=self.winfo_toplevel())
            return
        rid = int(sel[0])
        row = self.db.execute("SELECT url,label,enabled FROM search_urls WHERE id=?", (rid,)).fetchone()
        if not row:
            return
        url = simpledialog.askstring("Edit URL", "URL:", initialvalue=row["url"], parent=self.winfo_toplevel()) or row["url"]
        label = simpledialog.askstring("Edit URL", "Label:", initialvalue=row["label"], parent=self.winfo_toplevel()) or row["label"]
        enabled = messagebox.askyesno("Search URLs", "Enabled for search?", parent=self.winfo_toplevel())
        self.db.execute("UPDATE search_urls SET url=?, label=?, enabled=? WHERE id=?", (url.strip(), label.strip(), 1 if enabled else 0, rid))
        self.db.commit()
        self._urls_refresh()

    def _urls_delete(self) -> None:
        tv = getattr(self, "_urls_tree", None)
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        if not sel:
            return
        if not self.confirm_delete(len(sel)):
            return
        ids = [int(i) for i in sel]
        q = ",".join("?" for _ in ids)
        self.db.execute(f"DELETE FROM search_urls WHERE id IN ({q})", ids)
        self.db.commit()
        self._urls_refresh()

    def _urls_import(self) -> None:
        path = filedialog.askopenfilename(
            title="Import Search URLs (CSV/TXT)",
            filetypes=[("CSV/TXT", "*.csv;*.txt"), ("CSV", "*.csv"), ("Text", "*.txt"), ("All Files", "*.*")],
        )
        if not path:
            return
        added = 0
        try:
            if path.lower().endswith(".txt"):
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        s = (line or "").strip()
                        if s:
                            self.db.execute("INSERT OR IGNORE INTO search_urls(url, enabled) VALUES(?,1)", (s,))
                            added += 1
            else:
                rows = _read_csv_rows(path)
                if not rows:
                    self.warn("File appears to be empty.")
                    return
                hdr = _ci_map(rows[0])
                data = rows[1:]
                for r in data:
                    url = r[hdr["url"]].strip() if "url" in hdr and hdr["url"] < len(r) else (r[0].strip() if r else "")
                    if not url:
                        continue
                    label = r[hdr["label"]].strip() if "label" in hdr and hdr["label"] < len(r) else ""
                    enabled = r[hdr["enabled"]].strip().lower() if "enabled" in hdr and hdr["enabled"] < len(r) else "1"
                    en = 0 if enabled in ("0", "no", "false", "off") else 1
                    self.db.execute(
                        """
                        INSERT INTO search_urls(url, label, enabled) VALUES(?,?,?)
                        ON CONFLICT(url) DO UPDATE SET label=excluded.label, enabled=excluded.enabled
                        """,
                        (url, label, en),
                    )
                    added += 1
            self.db.commit()
            self._urls_refresh()
            self.info(f"Imported {added} URL(s).")
        except Exception as e:
            self.error(f"Failed to import URLs:\n{e!s}")

    def _urls_export(self) -> None:
        path = filedialog.asksaveasfilename(title="Export Search URLs", defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        try:
            rows = self.db.execute("SELECT url,label,enabled FROM search_urls ORDER BY LOWER(url)").fetchall()
            with open(path, "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["url", "label", "enabled"])
                for r in rows:
                    w.writerow([r["url"], r["label"] or "", r["enabled"] or 1])
            self.info(f"Exported {len(rows)} URL(s).")
        except Exception as e:
            self.error(f"Failed to export URLs:\n{e!s}")

    # ------------- Categories (Pantry + Shopping) -------------
    def _build_categories(self, parent: tk.Widget) -> None:
        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True)

        cat_tab = ttk.Frame(nb)
        sub_tab = ttk.Frame(nb)
        nb.add(cat_tab, text="Categories")
        nb.add(sub_tab, text="Subcategories (Pantry)")

        self._build_categories_tab(cat_tab)
        self._build_subcategories_tab(sub_tab)

    def _build_categories_tab(self, parent: tk.Widget) -> None:
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        bar = ttk.Frame(parent, padding=(8, 6))
        bar.grid(row=0, column=0, sticky="ew")

        ttk.Button(bar, text="Rename / Merge…", command=self._cats_rename).pack(side="left")
        ttk.Button(bar, text="Bulk Reassign…", command=self._cats_reassign).pack(side="left", padx=(6, 0))
        ttk.Button(bar, text="Delete → (Uncategorized)", command=self._cats_delete).pack(side="left", padx=(6, 0))
        ttk.Button(bar, text="Clean (fix duplicates)", command=self._cats_clean_all).pack(side="left", padx=(12, 0))
        ttk.Button(bar, text="Refresh", command=self._cats_refresh).pack(side="left", padx=(12, 0))

        cols = ("category", "pantry", "shopping", "total")
        tv = ttk.Treeview(parent, columns=cols, show="headings", selectmode="browse")
        tv.heading("category", text="Category")
        tv.heading("pantry", text="Pantry")
        tv.heading("shopping", text="Shopping")
        tv.heading("total", text="Total")
        tv.column("category", width=240, anchor="w")
        tv.column("pantry", width=80, anchor="e")
        tv.column("shopping", width=90, anchor="e")
        tv.column("total", width=80, anchor="e")
        tv.grid(row=1, column=0, sticky="nsew")
        self._cats_tree = tv

        vsb = ttk.Scrollbar(parent, orient="vertical", command=tv.yview)
        tv.configure(yscroll=vsb.set)
        vsb.grid(row=1, column=1, sticky="ns")

        self._cats_refresh()

    def _cats_selected(self) -> Optional[str]:
        tv = getattr(self, "_cats_tree", None)
        if not isinstance(tv, ttk.Treeview):
            return None
        sel = tv.selection()
        if len(sel) != 1:
            return None
        vals = tv.item(sel[0], "values")
        return str(vals[0]) if vals else None

    def _cats_collect_counts(self) -> Dict[str, Tuple[int, int]]:
        from utils.categorize import canonical_category  # lazy import
        counts: Dict[str, Tuple[int, int]] = {}

        for r in self.db.execute("SELECT category FROM pantry").fetchall():
            raw = (r["category"] or "").strip()
            label = canonical_category(raw) or "(Uncategorized)"
            p, s = counts.get(label, (0, 0))
            counts[label] = (p + 1, s)

        try:
            for r in self.db.execute("SELECT category FROM shopping_list").fetchall():
                raw = (r["category"] or "").strip()
                label = canonical_category(raw) or "(Uncategorized)"
                p, s = counts.get(label, (0, 0))
                counts[label] = (p, s + 1)
        except Exception:
            pass

        return counts

    def _cats_refresh(self) -> None:
        tv = getattr(self, "_cats_tree", None)
        if not isinstance(tv, ttk.Treeview):
            return
        for it in tv.get_children():
            tv.delete(it)
        counts = self._cats_collect_counts()
        total_rows = 0
        for cat in sorted(counts.keys(), key=lambda s: s.lower()):
            p, s = counts[cat]
            t = p + s
            total_rows += t
            tv.insert("", "end", values=(cat, p, s, t))
        self.set_status(f"{len(counts)} categories • {total_rows} rows across Pantry + Shopping")

    def _cats_reassign(self) -> None:
        from utils.categorize import canonical_category
        old_label = self._cats_selected()
        if not old_label:
            messagebox.showinfo("Categories", "Select a category to reassign.", parent=self.winfo_toplevel())
            return

        target = simpledialog.askstring("Bulk Reassign", f"Move all items from '{old_label}' to:", parent=self.winfo_toplevel())
        if target is None:
            return
        target = target.strip()
        if not target:
            return
        if target == "(Uncategorized)":
            return self._cats_delete()

        def match_row(cat_val: Optional[str]) -> bool:
            s = (cat_val or "").strip()
            if old_label == "(Uncategorized)":
                return s == ""
            return canonical_category(s) == old_label

        cur = self.db.cursor()
        p_ids = [int(r["id"]) for r in cur.execute("SELECT id, category FROM pantry").fetchall() if match_row(r["category"])]
        try:
            s_ids = [int(r["id"]) for r in cur.execute("SELECT id, category FROM shopping_list").fetchall() if match_row(r["category"])]
        except Exception:
            s_ids = []

        changed = 0
        if p_ids:
            qp = ",".join("?" for _ in p_ids)
            cur.execute(f"UPDATE pantry SET category=? WHERE id IN ({qp})", [target, *p_ids])
            changed += cur.rowcount if cur.rowcount is not None else 0
        if s_ids:
            qs = ",".join("?" for _ in s_ids)
            cur.execute(f"UPDATE shopping_list SET category=? WHERE id IN ({qs})", [target, *s_ids])
            changed += cur.rowcount if cur.rowcount is not None else 0
        self.db.commit()
        self._cats_refresh()
        self.info(f"Reassigned → {changed} row(s) updated.")

    def _cats_rename(self) -> None:
        from utils.categorize import canonical_category
        old_label = self._cats_selected()
        if not old_label:
            messagebox.showinfo("Categories", "Select a category to rename/merge.", parent=self.winfo_toplevel())
            return
        new_label = simpledialog.askstring("Rename / Merge", f"Rename '{old_label}' to:", parent=self.winfo_toplevel())
        if new_label is None:
            return
        new_label = new_label.strip()
        if not new_label:
            messagebox.showerror("Categories", "Category cannot be empty.", parent=self.winfo_toplevel())
            return
        if new_label == "(Uncategorized)":
            messagebox.showerror("Categories", "'(Uncategorized)' is a display label, not a storable name.", parent=self.winfo_toplevel())
            return

        def match_row(cat_val: Optional[str]) -> bool:
            s = (cat_val or "").strip()
            if old_label == "(Uncategorized)":
                return s == ""
            return canonical_category(s) == old_label

        cur = self.db.cursor()
        p_ids = [int(r["id"]) for r in cur.execute("SELECT id, category FROM pantry").fetchall() if match_row(r["category"])]
        try:
            s_ids = [int(r["id"]) for r in cur.execute("SELECT id, category FROM shopping_list").fetchall() if match_row(r["category"])]
        except Exception:
            s_ids = []

        changed = 0
        if p_ids:
            qp = ",".join("?" for _ in p_ids)
            cur.execute(f"UPDATE pantry SET category=? WHERE id IN ({qp})", [new_label, *p_ids])
            changed += cur.rowcount if cur.rowcount is not None else 0
        if s_ids:
            qs = ",".join("?" for _ in s_ids)
            cur.execute(f"UPDATE shopping_list SET category=? WHERE id IN ({qs})", [new_label, *s_ids])
            changed += cur.rowcount if cur.rowcount is not None else 0
        self.db.commit()
        self._cats_refresh()
        self.info(f"Renamed/Merged → {changed} row(s) updated.")

    def _cats_delete(self) -> None:
        from utils.categorize import canonical_category
        old_label = self._cats_selected()
        if not old_label:
            return
        if not self.confirm_delete(1):
            return

        def match_row(cat_val: Optional[str]) -> bool:
            s = (cat_val or "").strip()
            if old_label == "(Uncategorized)":
                return s == ""
            return canonical_category(s) == old_label

        cur = self.db.cursor()
        p_ids = [int(r["id"]) for r in cur.execute("SELECT id, category FROM pantry").fetchall() if match_row(r["category"])]
        try:
            s_ids = [int(r["id"]) for r in cur.execute("SELECT id, category FROM shopping_list").fetchall() if match_row(r["category"])]
        except Exception:
            s_ids = []

        changed = 0
        if p_ids:
            qp = ",".join("?" for _ in p_ids)
            cur.execute(f"UPDATE pantry SET category=NULL WHERE id IN ({qp})", p_ids)
            changed += cur.rowcount if cur.rowcount is not None else 0
        if s_ids:
            qs = ",".join("?" for _ in s_ids)
            cur.execute(f"UPDATE shopping_list SET category=NULL WHERE id IN ({qs})", s_ids)
            changed += cur.rowcount if cur.rowcount is not None else 0
        self.db.commit()
        self._cats_refresh()
        self.info(f"Deleted category label → {changed} row(s) set to (Uncategorized).")

    def _cats_clean_all(self) -> None:
        from utils.categorize import canonical_category, canonical_subcategory
        cur = self.db.cursor()
        changed = 0
        try:
            prows = cur.execute("SELECT id, category, subcategory FROM pantry").fetchall()
            for r in prows:
                cid = int(r["id"])
                old_cat = r["category"] or ""
                old_sub = r["subcategory"] or ""
                new_cat = canonical_category(old_cat)
                new_sub = canonical_subcategory(old_sub)
                if new_cat != old_cat or new_sub != old_sub:
                    cur.execute("UPDATE pantry SET category=?, subcategory=? WHERE id=?", (new_cat, new_sub, cid))
                    changed += 1
        except Exception:
            pass
        try:
            srows = cur.execute("SELECT id, category FROM shopping_list").fetchall()
            for r in srows:
                cid = int(r["id"])
                old_cat = r["category"] or ""
                new_cat = canonical_category(old_cat)
                if new_cat != old_cat:
                    cur.execute("UPDATE shopping_list SET category=? WHERE id=?", (new_cat, cid))
                    changed += 1
        except Exception:
            pass
        self.db.commit()
        self._cats_refresh()
        self.info(f"Cleaned categories on {changed} row(s).")

    # ----- Subcategory tab -----
    def _build_subcategories_tab(self, parent: tk.Widget) -> None:
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        bar = ttk.Frame(parent, padding=(8, 6))
        bar.grid(row=0, column=0, sticky="ew")

        ttk.Button(bar, text="Rename / Merge…", command=self._subcats_rename).pack(side="left")
        ttk.Button(bar, text="Bulk Reassign…", command=self._subcats_reassign).pack(side="left", padx=(6, 0))
        ttk.Button(bar, text="Delete → (Uncategorized)", command=self._subcats_delete).pack(side="left", padx=(6, 0))
        ttk.Button(bar, text="Clean (canonicalize)", command=self._subcats_clean).pack(side="left", padx=(12, 0))
        ttk.Button(bar, text="Refresh", command=self._subcats_refresh).pack(side="left", padx=(12, 0))

        cols = ("subcategory", "pantry")
        tv = ttk.Treeview(parent, columns=cols, show="headings", selectmode="browse")
        tv.heading("subcategory", text="Subcategory")
        tv.heading("pantry", text="Pantry")
        tv.column("subcategory", width=260, anchor="w")
        tv.column("pantry", width=90, anchor="e")
        tv.grid(row=1, column=0, sticky="nsew")
        self._subcats_tree = tv

        vsb = ttk.Scrollbar(parent, orient="vertical", command=tv.yview)
        tv.configure(yscroll=vsb.set)
        vsb.grid(row=1, column=1, sticky="ns")

        self._subcats_refresh()

    def _subcats_selected(self) -> Optional[str]:
        tv = getattr(self, "_subcats_tree", None)
        if not isinstance(tv, ttk.Treeview):
            return None
        sel = tv.selection()
        if len(sel) != 1:
            return None
        vals = tv.item(sel[0], "values")
        return str(vals[0]) if vals else None

    def _subcats_collect_counts(self) -> Dict[str, int]:
        from utils.categorize import canonical_subcategory
        counts: Dict[str, int] = {}
        try:
            for r in self.db.execute("SELECT subcategory FROM pantry").fetchall():
                raw = (r["subcategory"] or "").strip()
                label = canonical_subcategory(raw) or "(Uncategorized)"
                counts[label] = counts.get(label, 0) + 1
        except Exception:
            pass
        return counts

    def _subcats_refresh(self) -> None:
        tv = getattr(self, "_subcats_tree", None)
        if not isinstance(tv, ttk.Treeview):
            return
        for it in tv.get_children():
            tv.delete(it)
        counts = self._subcats_collect_counts()
        total = 0
        for sub in sorted(counts.keys(), key=lambda s: s.lower()):
            n = counts[sub]
            total += n
            tv.insert("", "end", values=(sub, n))
        self.set_status(f"{len(counts)} subcategories • {total} pantry rows")

    def _subcats_reassign(self) -> None:
        from utils.categorize import canonical_subcategory
        old_label = self._subcats_selected()
        if not old_label:
            messagebox.showinfo("Subcategories", "Select a subcategory to reassign.", parent=self.winfo_toplevel())
            return

        target = simpledialog.askstring("Bulk Reassign Subcategory", f"Move all items from '{old_label}' to:", parent=self.winfo_toplevel())
        if target is None:
            return
        target = target.strip()
        if not target:
            return
        if target == "(Uncategorized)":
            return self._subcats_delete()

        def match_row(sub_val: Optional[str]) -> bool:
            s = (sub_val or "").strip()
            if old_label == "(Uncategorized)":
                return s == ""
            from utils.categorize import canonical_subcategory as canon
            return canon(s) == old_label

        cur = self.db.cursor()
        ids = [int(r["id"]) for r in cur.execute("SELECT id, subcategory FROM pantry").fetchall() if match_row(r["subcategory"])]
        changed = 0
        if ids:
            q = ",".join("?" for _ in ids)
            cur.execute(f"UPDATE pantry SET subcategory=? WHERE id IN ({q})", [target, *ids])
            changed = cur.rowcount if cur.rowcount is not None else len(ids)
        self.db.commit()
        self._subcats_refresh()
        self.info(f"Reassigned subcategory → {changed} row(s) updated.")

    def _subcats_rename(self) -> None:
        from utils.categorize import canonical_subcategory
        old_label = self._subcats_selected()
        if not old_label:
            messagebox.showinfo("Subcategories", "Select a subcategory to rename/merge.", parent=self.winfo_toplevel())
            return
        new_label = simpledialog.askstring("Rename / Merge Subcategory", f"Rename '{old_label}' to:", parent=self.winfo_toplevel())
        if new_label is None:
            return
        new_label = new_label.strip()
        if not new_label:
            messagebox.showerror("Subcategories", "Subcategory cannot be empty.", parent=self.winfo_toplevel())
            return
        if new_label == "(Uncategorized)":
            messagebox.showerror("Subcategories", "'(Uncategorized)' is a display label, not a storable name.", parent=self.winfo_toplevel())
            return

        def match_row(sub_val: Optional[str]) -> bool:
            s = (sub_val or "").strip()
            if old_label == "(Uncategorized)":
                return s == ""
            return canonical_subcategory(s) == old_label

        cur = self.db.cursor()
        ids = [int(r["id"]) for r in cur.execute("SELECT id, subcategory FROM pantry").fetchall() if match_row(r["subcategory"])]
        changed = 0
        if ids:
            q = ",".join("?" for _ in ids)
            cur.execute(f"UPDATE pantry SET subcategory=? WHERE id IN ({q})", [new_label, *ids])
            changed = cur.rowcount if cur.rowcount is not None else len(ids)
        self.db.commit()
        self._subcats_refresh()
        self.info(f"Renamed/Merged subcategory → {changed} row(s) updated.")

    # In panels/settings_panel.py, inside class SettingsPanel

    def _subcats_clean(self) -> None:
        """
        Canonicalize all pantry subcategory labels, fixing case/spacing/synonyms.
        Only touches the `pantry` table (Subcategories tab is pantry-focused).
        """
        try:
            from utils.categorize import canonical_subcategory
        except Exception:
            # If categorize utils aren't available, bail gracefully.
            self.warn("Canonicalizer not available.")
            return

        cur = self.db.cursor()
        changed = 0
        try:
            rows = cur.execute("SELECT id, subcategory FROM pantry").fetchall()
            for r in rows:
                rid = int(r["id"])
                old = r["subcategory"] or ""
                new = canonical_subcategory(old)
                if new != old:
                    cur.execute("UPDATE pantry SET subcategory=? WHERE id=?", (new, rid))
                    changed += 1
            self.db.commit()
        except Exception as e:
            self.error(f"Failed to clean subcategories:\n{e!s}")
            return

        # Refresh the tab’s table
        self._subcats_refresh()
        self.info(f"Cleaned subcategories on {changed} row(s).")


    def _subcats_delete(self) -> None:
        from utils.categorize import canonical_subcategory
        old_label = self._subcats_selected()
        if not old_label:
            return
        if not self.confirm_delete(1):
            return

        def match_row(sub_val: Optional[str]) -> bool:
            s = (sub_val or "").strip()
            if old_label == "(Uncategorized)":
                return s == ""
            return canonical_subcategory(s) == old_label

        cur = self.db.cursor()
        ids = [int(r["id"]) for r in cur.execute("SELECT id, subcategory FROM pantry").fetchall() if match_row(r["subcategory"])]
        changed = 0
        if ids:
            q = ",".join("?" for _ in ids)
            cur.execute(f"UPDATE pantry SET subcategory=NULL WHERE id IN ({q})", ids)
            changed = cur.rowcount if cur.rowcount is not None else len(ids)
        self.db.commit()
        self._subcats_refresh()
        self.info(f"Deleted subcategory label → {changed} row(s) set to (Uncategorized).")

    # ------------- Theme (granular customizations, scrolling) -------------
    def _build_theme(self, parent: tk.Widget) -> None:
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        # enable BOTH vertical and horizontal scrolling; force horizontal to be visible
        sf = _ScrollFrame(parent, xscroll=True, force_hscroll=False)
        sf.grid(row=0, column=0, sticky="nsew")
        body = sf.body

        # --- Toolbar: theme picker & actions ---
        bar = ttk.Frame(body, padding=(8, 6))
        bar.grid(row=0, column=0, sticky="ew")

        ttk.Label(bar, text="Theme:").pack(side="left")
        self._theme_var = tk.StringVar(value=get_active_theme_name())
        self._theme_combo = ttk.Combobox(
            bar,
            textvariable=self._theme_var,
            values=sorted(list_theme_names(), key=str.lower),
            state="readonly",
            width=28,
        )
        self._theme_combo.pack(side="left", padx=(6, 6))
        self._theme_combo.bind("<<ComboboxSelected>>", lambda _e: self._load_theme_into_editor(self._theme_var.get()))

        def on_activate():
            name = (self._theme_var.get() or "").strip()
            if not name:
                return
            set_active_theme(name)
            try:
                self.app.theme = make_theme_instance(name)
                self.app.theme.apply(self.app)
            except Exception:
                pass
            self.set_status(f"Activated theme: {name}")
            self._load_theme_into_editor(name)

        ttk.Button(bar, text="Activate", command=on_activate).pack(side="left")

        def on_duplicate():
            name = self._theme_var.get() or get_active_theme_name()
            spec = load_theme_spec(name)
            base = dict(spec)
            base["name"] = f"{spec.get('name', name)} (Copy)"
            persist_theme(base)
            self._refresh_theme_names(select=base["name"])
            self._load_theme_into_editor(base["name"])
            self.set_status(f"Duplicated theme → {base['name']}")

        ttk.Button(bar, text="Duplicate…", command=on_duplicate).pack(side="left", padx=(8, 0))

        def on_save():
            spec = self._collect_editor_spec()
            persist_theme(spec)
            self._refresh_theme_names(select=spec["name"])
            if spec["name"] == get_active_theme_name():
                self.app.theme = make_theme_instance(spec["name"])
                self.app.theme.apply(self.app)
            self.set_status(f"Saved theme: {spec['name']}")

        ttk.Button(bar, text="Save", command=on_save).pack(side="left", padx=(6, 0))

        def on_delete():
            name = (self._theme_var.get() or "").strip()
            if not name:
                return
            if not self.confirm_delete(1):
                return
            remove_theme(name)
            self._refresh_theme_names()
            self._theme_var.set(get_active_theme_name())
            self._load_theme_into_editor(self._theme_var.get())
            self.set_status(f"Deleted theme: {name}")

        ttk.Button(bar, text="Delete", command=on_delete).pack(side="left", padx=(6, 0))

        ttk.Button(bar, text="Import Theme…", command=self._theme_import).pack(side="left", padx=(12, 0))
        ttk.Button(bar, text="Export Theme…", command=self._theme_export).pack(side="left", padx=(6, 0))

        # --- Editor form (two columns) ---
        wrap = ttk.Frame(body, padding=(10, 8))
        wrap.grid(row=1, column=0, sticky="w")  # 'w' so it keeps natural width (helps horizontal overflow)

        ttk.Label(wrap, text="Theme Name").grid(row=0, column=0, sticky="w")
        self._name_var = tk.StringVar()
        ttk.Entry(wrap, textvariable=self._name_var, width=32).grid(row=0, column=1, sticky="w", padx=(6, 18))

        # colors
        ttk.Label(wrap, text="Colors", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=(8, 4))
        colors_frame = ttk.Frame(wrap)
        colors_frame.grid(row=2, column=0, columnspan=2, sticky="w")
        self._color_vars: Dict[str, tk.StringVar] = {}
        color_keys = [
            "bg", "surface", "text", "muted_text", "border",
            "accent", "accent_fg", "warning", "danger",
            "zebra_even", "zebra_odd", "low_bg", "low_fg",
        ]

        def make_color_row(r: int, key: str, label: str):
            ttk.Label(colors_frame, text=label).grid(row=r, column=0, sticky="w")
            v = tk.StringVar()
            self._color_vars[key] = v
            e = ttk.Entry(colors_frame, textvariable=v, width=16)
            e.grid(row=r, column=1, sticky="w", padx=(6, 6))
            def pick():
                initial = v.get() or "#FFFFFF"
                color = colorchooser.askcolor(initialcolor=initial, parent=self.winfo_toplevel())[1]
                if color:
                    v.set(color); self._apply_preview()
            ttk.Button(colors_frame, text="Pick…", command=pick).grid(row=r, column=2, sticky="w")

        for i, k in enumerate(color_keys):
            make_color_row(i, k, k.replace("_", " ").title())

        # fonts
        ttk.Label(wrap, text="Fonts", font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky="w", pady=(10, 4))
        self._font_base_family = tk.StringVar()
        self._font_base_size = tk.IntVar()
        self._font_mono_family = tk.StringVar()

        ttk.Label(wrap, text="Base Family").grid(row=4, column=0, sticky="w")
        ttk.Entry(wrap, textvariable=self._font_base_family, width=22).grid(row=4, column=1, sticky="w", padx=(6, 18))

        ttk.Label(wrap, text="Base Size").grid(row=5, column=0, sticky="w")
        ttk.Spinbox(wrap, from_=8, to=20, textvariable=self._font_base_size, width=6,
                    command=lambda: self._apply_preview()).grid(row=5, column=1, sticky="w", padx=(6, 18))

        ttk.Label(wrap, text="Mono Family").grid(row=6, column=0, sticky="w")
        ttk.Entry(wrap, textvariable=self._font_mono_family, width=22).grid(row=6, column=1, sticky="w", padx=(6, 18))

        # spacing
        ttk.Label(wrap, text="Spacing", font=("Segoe UI", 10, "bold")).grid(row=7, column=0, sticky="w", pady=(10, 4))
        self._sp_xs = tk.IntVar(); self._sp_sm = tk.IntVar(); self._sp_md = tk.IntVar(); self._sp_lg = tk.IntVar()

        def slider(row: int, label: str, var: tk.IntVar):
            ttk.Label(wrap, text=label).grid(row=row, column=0, sticky="w")
            s = ttk.Scale(wrap, from_=0, to=24, orient="horizontal",
                          command=lambda _v=None: self._apply_preview(), variable=var)
            s.grid(row=row, column=1, sticky="w", padx=(6, 18))
        slider(8,  "xs", self._sp_xs)
        slider(9,  "sm", self._sp_sm)
        slider(10, "md", self._sp_md)
        slider(11, "lg", self._sp_lg)

        # tree settings
        ttk.Label(wrap, text="Tree", font=("Segoe UI", 10, "bold")).grid(row=12, column=0, sticky="w", pady=(10, 4))
        self._tree_row_h = tk.IntVar()
        ttk.Label(wrap, text="Row Height").grid(row=13, column=0, sticky="w")
        ttk.Spinbox(wrap, from_=16, to=40, textvariable=self._tree_row_h, width=6,
                    command=lambda: self._apply_preview()).grid(row=13, column=1, sticky="w", padx=(6, 18))

        # live preview on edits
        for v in list(self._color_vars.values()) + [self._font_base_family, self._font_mono_family]:
            v.trace_add("write", lambda *_: self._apply_preview())

        # --- Preview area (compact) ---
        preview = ttk.Frame(body, padding=(8, 6), style="Card.TFrame")
        preview.grid(row=2, column=0, sticky="ew")
        ttk.Label(preview, text="Preview area").grid(row=0, column=0, sticky="w")
        tv = ttk.Treeview(preview, columns=("a", "b"), show="headings", height=4)
        tv.heading("a", text="Column A"); tv.heading("b", text="Column B")
        tv.insert("", "end", values=("Foo", "Bar"))
        tv.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        preview.grid_columnconfigure(0, weight=1)
        self._theme_preview_tree = tv

        # give wrap a healthy natural width so horizontal always has something to scroll
        #self.after(0, lambda: wrap.configure(width=max(wrap.winfo_reqwidth(), 1100)))

        # boot with active
        self._load_theme_into_editor(get_active_theme_name())

    def _refresh_theme_names(self, *, select: str | None = None) -> None:
        names = sorted(list_theme_names(), key=str.lower)
        self._theme_combo.configure(values=names)
        if select and select in names:
            self._theme_var.set(select)

    def _load_theme_into_editor(self, name: str) -> None:
        spec = load_theme_spec(name)
        self._name_var.set(spec.get("name", name))

        colors = spec.get("colors", {}) or {}
        for k, var in self._color_vars.items():
            var.set(colors.get(k, ""))

        fonts = spec.get("fonts", {}) or {}
        self._font_base_family.set(fonts.get("base_family", "Segoe UI"))
        self._font_base_size.set(int(fonts.get("base_size", 10)))
        self._font_mono_family.set(fonts.get("mono_family", "Consolas"))

        sp = spec.get("spacing", {}) or {}
        self._sp_xs.set(int(sp.get("xs", 2)))
        self._sp_sm.set(int(sp.get("sm", 4)))
        self._sp_md.set(int(sp.get("md", 8)))
        self._sp_lg.set(int(sp.get("lg", 12)))

        tree = spec.get("tree", {}) or {}
        self._tree_row_h.set(int(tree.get("row_height", 22)))

        self._apply_preview()

    def _collect_editor_spec(self) -> Dict[str, Any]:
        name = (self._name_var.get() or "").strip() or "Custom Theme"
        colors = {k: v.get().strip() for k, v in self._color_vars.items() if v.get().strip()}
        spec = {
            "name": name,
            "colors": colors,
            "fonts": {
                "base_family": self._font_base_family.get().strip() or "Segoe UI",
                "base_size": int(self._font_base_size.get() or 10),
                "mono_family": self._font_mono_family.get().strip() or "Consolas",
            },
            "spacing": {
                "xs": int(self._sp_xs.get() or 2),
                "sm": int(self._sp_sm.get() or 4),
                "md": int(self._sp_md.get() or 8),
                "lg": int(self._sp_lg.get() or 12),
            },
            "tree": {"row_height": int(self._tree_row_h.get() or 22)},
        }
        return spec

    def _apply_preview(self) -> None:
        try:
            active_name = get_active_theme_name()
            base = load_theme_spec(active_name)
            merged = dict(base)
            for k in ("colors", "fonts", "spacing", "tree"):
                merged.setdefault(k, {})
                merged[k].update(self._collect_editor_spec().get(k, {}) or {})

            th = getattr(self.app, "theme", None) or make_theme_instance(active_name)
            th.spec = merged
            self.app.theme = th
            th.apply(self.app)
            self.set_status("Preview applied (not saved)")
        except Exception:
            pass

    # Theme import/export
    def _theme_import(self) -> None:
        path = filedialog.askopenfilename(
            title="Import Theme(s) from JSON",
            filetypes=[("JSON", "*.json"), ("All Files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            imported_names: List[str] = []

            def _normalize_and_save(name: str, spec: Dict[str, Any]) -> None:
                payload = {
                    "name": name.strip() or "Imported Theme",
                    "colors": dict(spec.get("colors", {})),
                    "fonts": dict(spec.get("fonts", {})),
                    "spacing": dict(spec.get("spacing", {})),
                    "tree": dict(spec.get("tree", {})),
                }
                persist_theme(payload)
                imported_names.append(payload["name"])

            if isinstance(data, dict) and ("colors" in data or "fonts" in data or "spacing" in data or "tree" in data):
                _normalize_and_save(data.get("name") or "Imported Theme", data)
            elif isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, dict):
                        _normalize_and_save(str(k), v)
            elif isinstance(data, list):
                for idx, v in enumerate(data, 1):
                    if isinstance(v, dict):
                        _normalize_and_save(v.get("name") or f"Imported {idx}", v)
            else:
                raise ValueError("Unsupported JSON structure for themes.")

            self._refresh_theme_names(select=imported_names[-1] if imported_names else None)
            if imported_names:
                self._load_theme_into_editor(imported_names[-1])
            self.info(f"Imported {len(imported_names)} theme(s).")
        except Exception as e:
            self.error(f"Failed to import theme(s):\n{e!s}")

    def _theme_export(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Export Theme to JSON",
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            initialfile=f"{(self._name_var.get() or self._theme_var.get() or 'theme').strip()}.json",
        )
        if not path:
            return
        try:
            spec = self._collect_editor_spec()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(spec, f, ensure_ascii=False, indent=2)
            self.info(f"Exported theme → {path}")
        except Exception as e:
            self.error(f"Failed to export theme:\n{e!s}")
