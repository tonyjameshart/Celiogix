# path: panels/cookbook_panel.py
from __future__ import annotations

import csv
import os
import re
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from typing import Optional, List, Tuple, Any

from panels.base_panel import BasePanel
from utils.export import export_table_html, export_recipes_html
from utils import recipes as recipes_api  # online providers + URL scraper

# Visible columns in Library/Favorites
LIB_COLS: List[Tuple[str, str, int, str]] = [
    ("favorite",   "♥",        34,  "c"),
    ("title",      "Title",    300, "w"),
    ("source",     "Source",   130, "w"),
    ("tags",       "Tags",     160, "w"),
    ("url",        "URL",      220, "w"),
    ("prep_time",  "Prep",      80, "c"),
    ("cook_time",  "Cook",      80, "c"),
    ("servings",   "Servings",  80, "c"),
    ("rating",     "★",         60, "c"),
]

CSV_FIELDS_ORDER = [
    "title","source","url","tags","ingredients","instructions",
    "rating","prep_time","cook_time","servings","favorite","notes",
]

SEARCH_COLUMNS = [
    "(any)",
    "title","source","tags","url",
    "ingredients","instructions","notes",
    "prep_time","cook_time","servings","rating",
]

_ESCAPE_CHAR = "^"  # single-char escape for LIKE


class CookbookPanel(BasePanel):
    """Recipes Library with Favorites, CSV/.TXT import, URL scrape, and local/online search."""

    def __init__(self, master, app, **kw):
        self._nb: Optional[ttk.Notebook] = None
        self._tab_lib: Optional[ttk.Frame] = None
        self._tab_fav: Optional[ttk.Frame] = None
        self._tree_lib: Optional[ttk.Treeview] = None
        self._tree_fav: Optional[ttk.Treeview] = None
        self._fav_only: Optional[tk.BooleanVar] = None
        self._fav_first: Optional[tk.BooleanVar] = None

        self._tab_search: Optional[ttk.Frame] = None
        self._search_q: Optional[tk.StringVar] = None
        self._search_col: Optional[tk.StringVar] = None
        self._search_tags: Optional[tk.StringVar] = None
        self._search_local: Optional[tk.BooleanVar] = None
        self._search_online: Optional[tk.BooleanVar] = None
        self._search_limit: Optional[tk.IntVar] = None
        self._tree_search: Optional[ttk.Treeview] = None

        # New: edit-after-URL toggle
        self._edit_after_url: Optional[tk.BooleanVar] = None

        super().__init__(master, app, **kw)

    # ---------- UI ----------
    def build(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._ensure_schema()

        nb = ttk.Notebook(self)
        nb.grid(row=0, column=0, sticky="nsew")
        self._nb = nb

        self._build_search_tab(nb)

        self._fav_first = tk.BooleanVar(value=False)
        self._fav_only = tk.BooleanVar(value=False)

        # Library tab
        self._tab_lib = ttk.Frame(nb)
        nb.add(self._tab_lib, text="Library")
        self._tab_lib.grid_rowconfigure(0, weight=1)
        self._tab_lib.grid_columnconfigure(0, weight=1)

        wrap = ttk.Frame(self._tab_lib); wrap.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        wrap.grid_rowconfigure(0, weight=1); wrap.grid_columnconfigure(0, weight=1)

        tv = ttk.Treeview(wrap, columns=[c[0] for c in LIB_COLS], show="headings", selectmode="extended")
        for key, hdr, width, align in LIB_COLS:
            tv.heading(key, text=hdr)
            anc = {"w":"w","e":"e","c":"center"}.get(align, "w")
            tv.column(key, width=width, anchor=anc, stretch=True)
        tv.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(wrap, orient="vertical", command=tv.yview)
        hsb = ttk.Scrollbar(wrap, orient="horizontal", command=tv.xview)
        tv.configure(yscroll=vsb.set, xscroll=hsb.set)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        m1 = self._make_context_menu(for_favorites=False)
        tv.bind("<Button-3>", lambda e, m=m1: self._popup_menu(e, m))
        tv.bind("<Double-1>", lambda _e: self.edit_selected())
        tv.bind("<Key-f>", lambda _e: self.toggle_favorite_selected())
        self._tree_lib = tv

        # Favorites tab
        self._tab_fav = ttk.Frame(nb)
        nb.add(self._tab_fav, text="Favorites")
        self._tab_fav.grid_rowconfigure(0, weight=1)
        self._tab_fav.grid_columnconfigure(0, weight=1)

        wrap2 = ttk.Frame(self._tab_fav); wrap2.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        wrap2.grid_rowconfigure(0, weight=1); wrap2.grid_columnconfigure(0, weight=1)

        tv2 = ttk.Treeview(wrap2, columns=[c[0] for c in LIB_COLS], show="headings", selectmode="extended")
        for key, hdr, width, align in LIB_COLS:
            tv2.heading(key, text=hdr)
            anc = {"w":"w","e":"e","c":"center"}.get(align, "w")
            tv2.column(key, width=width, anchor=anc, stretch=True)
        tv2.grid(row=0, column=0, sticky="nsew")

        vsb2 = ttk.Scrollbar(wrap2, orient="vertical", command=tv2.yview)
        hsb2 = ttk.Scrollbar(wrap2, orient="horizontal", command=tv2.xview)
        tv2.configure(yscroll=vsb2.set, xscroll=hsb2.set)
        vsb2.grid(row=0, column=1, sticky="ns")
        hsb2.grid(row=1, column=0, sticky="ew")

        m2 = self._make_context_menu(for_favorites=True)
        tv2.bind("<Button-3>", lambda e, m=m2: self._popup_menu(e, m))
        tv2.bind("<Double-1>", lambda _e: self.edit_selected())
        tv2.bind("<Key-f>", lambda _e: self.toggle_favorite_selected())
        self._tree_fav = tv2

        nb.select(self._tab_search)
        self._refresh_both()

    def _build_search_tab(self, nb: ttk.Notebook) -> None:
        t = ttk.Frame(nb)
        nb.add(t, text="Search")
        self._tab_search = t

        bar = ttk.Frame(t); bar.pack(fill="x", padx=8, pady=8)

        self._search_q = tk.StringVar(value="")
        self._search_col = tk.StringVar(value="(any)")
        self._search_tags = tk.StringVar(value="")
        self._search_local = tk.BooleanVar(value=True)
        self._search_online = tk.BooleanVar(value=False)
        self._search_limit = tk.IntVar(value=20)
        self._edit_after_url = tk.BooleanVar(value=True)  # new

        ttk.Label(bar, text="Query").pack(side="left")
        e_q = ttk.Entry(bar, textvariable=self._search_q, width=34)
        e_q.pack(side="left", padx=(6, 12))
        e_q.bind("<Return>", lambda _e: self.search_now())

        ttk.Label(bar, text="In").pack(side="left")
        ttk.Combobox(bar, values=SEARCH_COLUMNS, textvariable=self._search_col, width=12, state="readonly").pack(side="left", padx=(6, 12))

        ttk.Label(bar, text="Tags contains").pack(side="left")
        ttk.Entry(bar, textvariable=self._search_tags, width=22).pack(side="left", padx=(6, 12))

        ttk.Checkbutton(bar, text="Local", variable=self._search_local).pack(side="left")
        ttk.Checkbutton(bar, text="Online", variable=self._search_online).pack(side="left", padx=(6, 0))

        ttk.Label(bar, text="Limit").pack(side="left", padx=(12, 0))
        ttk.Spinbox(bar, from_=1, to=100, textvariable=self._search_limit, width=4).pack(side="left", padx=(6, 12))

        ttk.Checkbutton(bar, text="Edit after URL", variable=self._edit_after_url).pack(side="right", padx=(6, 0))  # new
        ttk.Button(bar, text="Add from URL…", command=self.add_from_url).pack(side="right")

        ttk.Button(bar, text="Search", command=self.search_now).pack(side="left")
        ttk.Button(bar, text="Clear", command=self._clear_search_inputs).pack(side="left", padx=(6, 0))

        wrap = ttk.Frame(t); wrap.pack(fill="both", expand=True, padx=8, pady=(0,8))
        wrap.grid_rowconfigure(0, weight=1); wrap.grid_columnconfigure(0, weight=1)

        cols = ["source", "title", "tags", "url"]
        tv = ttk.Treeview(wrap, columns=cols, show="headings", selectmode="extended")
        tv.heading("source", text="Source"); tv.column("source", width=110, anchor="w", stretch=True)
        tv.heading("title", text="Title"); tv.column("title", width=420, anchor="w", stretch=True)
        tv.heading("tags", text="Tags"); tv.column("tags", width=220, anchor="w", stretch=True)
        tv.heading("url", text="URL"); tv.column("url", width=380, anchor="w", stretch=True)
        tv.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(wrap, orient="vertical", command=tv.yview)
        hsb = ttk.Scrollbar(wrap, orient="horizontal", command=tv.xview)
        tv.configure(yscroll=vsb.set, xscroll=hsb.set)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tv.bind("<Double-1>", lambda _e: self._open_selected_urls(tv))

        m = tk.Menu(self, tearoff=0)
        m.add_command(label="Open URL", command=lambda: self._open_selected_urls(tv))
        m.add_separator()
        m.add_command(label="Import Selected → Library", command=lambda: self._import_search_rows(tv, only_selected=True))
        m.add_command(label="Import All → Library", command=lambda: self._import_search_rows(tv, only_selected=False))
        m.add_separator()
        m.add_command(label="Add from URL…", command=self.add_from_url)
        m.add_command(label="Fit Columns", command=lambda: self.fit_columns_now(tv, exact=True, max_px_map={"url": 1600, "tags": 1000}))
        m.add_command(label="Clear Results", command=lambda: self._clear_tree(tv))
        tv.bind("<Button-3>", lambda e, menu=m: self._popup_menu(e, menu))

        self._tree_search = tv

    # ---------- Menus ----------
    def _popup_menu(self, ev: tk.Event, menu: tk.Menu) -> None:
        try:
            menu.tk_popup(ev.x_root, ev.y_root)
        finally:
            menu.grab_release()

    def _make_context_menu(self, *, for_favorites: bool) -> tk.Menu:
        m = tk.Menu(self, tearoff=0)
        m.add_command(label="Add", command=getattr(self, "add_recipe", lambda: None))
        m.add_command(label="Add from URL…", command=getattr(self, "add_from_url", lambda: None))
        m.add_command(label="Edit", command=getattr(self, "edit_selected", lambda: None))
        m.add_command(label="Delete", command=getattr(self, "delete_selected", lambda: None))
        m.add_separator()
        m.add_command(label="Toggle Favorite", command=getattr(self, "toggle_favorite_selected", lambda: None))
        m.add_command(label="Add to Menu…", command=getattr(self, "add_selected_to_menu", lambda: None))
        m.add_separator()
        m.add_command(
            label="Import CSV…",
            command=getattr(self, "import_csv", lambda: messagebox.showinfo("Cookbook", "CSV import not available")),
            state=("normal" if hasattr(self, "import_csv") else "disabled"),
        )
        m.add_command(
            label="Import .TXT…",
            command=getattr(self, "import_txt", lambda: messagebox.showinfo("Cookbook", "TXT import not available")),
            state=("normal" if hasattr(self, "import_txt") else "disabled"),
        )
        m.add_separator()
        m.add_command(label="Export HTML (visible)", command=getattr(self, "export_html_visible", lambda: None))
        m.add_command(label="Print Recipe (HTML)", command=getattr(self, "export_html_recipe_selected", lambda: None))
        m.add_separator()
        m.add_command(label="Fit Columns", command=getattr(self, "_fit_current", lambda: None))
        m.add_command(label="Refresh", command=getattr(self, "_refresh_both", lambda: None))

        view = tk.Menu(m, tearoff=0)
        view.add_checkbutton(label="Favorites only", variable=self._fav_only, command=self._refresh_both)
        view.add_checkbutton(label="♥ first", variable=self._fav_first, command=self._refresh_both)
        m.add_cascade(label="View", menu=view)

        if for_favorites:
            self._fav_only.set(True)
        return m

    def _fit_current(self) -> None:
        tv = self._current_tree()
        if isinstance(tv, ttk.Treeview):
            self.fit_columns_now(tv, exact=True, max_px_map={"url": 1400, "tags": 900})

    # ---------- Helpers ----------
    def _current_tree(self) -> Optional[ttk.Treeview]:
        nb = self._nb
        if not isinstance(nb, ttk.Notebook):
            return self._tree_lib
        cur = nb.select()
        if self._tab_fav and str(self._tab_fav) == cur:
            return self._tree_fav
        if self._tab_search and str(self._tab_search) == cur:
            return self._tree_search
        return self._tree_lib

    def _order_sql(self) -> str:
        fav_first = bool(self._fav_first.get()) if isinstance(self._fav_first, tk.BooleanVar) else False
        return "ORDER BY IFNULL(favorite,0) DESC, LOWER(title)" if fav_first else "ORDER BY LOWER(title)"

    def _refresh_both(self) -> None:
        self.refresh_library()
        self.refresh_favorites()

    # ---------- Schema ----------
    def _columns(self) -> set[str]:
        try:
            return {r[1] for r in self.db.execute("PRAGMA table_info(recipes)").fetchall()}
        except Exception:
            return set()

    def _table_exists(self, name: str) -> bool:
        try:
            r = self.db.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                (name,),
            ).fetchone()
            return bool(r)
        except Exception:
            return False

    def _ensure_schema(self) -> None:
        cur = self.db.cursor()
        # Create table if missing
        if not self._table_exists("recipes"):
            cur.execute("""
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
            """)
            # Unique URL if provided
            cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_recipes_url_unique ON recipes(url)")
            self.db.commit()

        # Add missing columns on existing DBs
        def ensure(col: str, ddl: str) -> None:
            try:
                cols = {r[1] for r in self.db.execute("PRAGMA table_info(recipes)")}
                if col not in cols:
                    cur.execute(f"ALTER TABLE recipes ADD COLUMN {ddl}")
            except sqlite3.OperationalError:
                pass

        ensure("favorite", "favorite INTEGER NOT NULL DEFAULT 0")
        ensure("ingredients", "ingredients TEXT DEFAULT ''")
        ensure("instructions", "instructions TEXT DEFAULT ''")
        ensure("notes", "notes TEXT DEFAULT ''")
        self.db.commit()

        # Ensure unique index on url (nullable allowed)
        try:
            cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_recipes_url_unique ON recipes(url)")
            self.db.commit()
        except Exception:
            pass


    def _has_unique_url(self) -> bool:
        try:
            rows = self.db.execute("PRAGMA index_list(recipes)").fetchall()
            names = [r["name"] for r in rows]
            for name in names:
                cols = [c["name"] for c in self.db.execute(f"PRAGMA index_info({name})").fetchall()]
                if cols == ["url"]:
                    return True
        except Exception:
            return False
        return False

    # ---------- Data (Library) ----------
    def refresh_library(self) -> None:
        tv = self._tree_lib
        if not isinstance(tv, ttk.Treeview):
            return
        for it in tv.get_children():
            tv.delete(it)

        where = []
        if isinstance(self._fav_only, tk.BooleanVar) and self._fav_only.get():
            where.append("IFNULL(favorite,0)=1")
        where_sql = (" WHERE " + " AND ".join(where)) if where else ""

        rows = self.db.execute(f"""
            SELECT id,
                   IFNULL(favorite,0) AS favorite,
                   title, source, tags, url,
                   COALESCE(prep_time,'') AS prep_time,
                   COALESCE(cook_time,'') AS cook_time,
                   COALESCE(servings,0)   AS servings,
                   IFNULL(rating,0.0)     AS rating
              FROM recipes
              {where_sql}
              {self._order_sql()}
        """).fetchall()

        for r in rows:
            tv.insert("", "end", iid=str(r["id"]), values=[
                ("♥" if (r["favorite"] or 0) else ""),
                r["title"] or "", r["source"] or "", r["tags"] or "", r["url"] or "",
                r["prep_time"] or "", r["cook_time"] or "", r["servings"] or 0, r["rating"] or 0
            ])
        self.set_status(f"{len(rows)} recipe(s)")

    # ---------- Data (Favorites) ----------
    def refresh_favorites(self) -> None:
        tv = self._tree_fav
        if not isinstance(tv, ttk.Treeview):
            return
        for it in tv.get_children():
            tv.delete(it)

        rows = self.db.execute(f"""
            SELECT id,
                   IFNULL(favorite,0) AS favorite,
                   title, source, tags, url,
                   COALESCE(prep_time,'') AS prep_time,
                   COALESCE(cook_time,'') AS cook_time,
                   COALESCE(servings,0)   AS servings,
                   IFNULL(rating,0.0)     AS rating
              FROM recipes
             WHERE IFNULL(favorite,0)=1
              {self._order_sql()}
        """).fetchall()

        for r in rows:
            tv.insert("", "end", iid=str(r["id"]), values=[
                ("♥" if (r["favorite"] or 0) else ""),
                r["title"] or "", r["source"] or "", r["tags"] or "", r["url"] or "",
                r["prep_time"] or "", r["cook_time"] or "", r["servings"] or 0, r["rating"] or 0
            ])

    # ---------- Search ----------
    def _like_escape(self, s: str) -> str:
        esc = _ESCAPE_CHAR
        return s.replace(esc, esc + esc).replace("%",  esc + "%").replace("_",  esc + "_")

    def _clear_search_inputs(self) -> None:
        if self._search_q: self._search_q.set("")
        if self._search_tags: self._search_tags.set("")
        if self._tree_search: self._clear_tree(self._tree_search)

    def _clear_tree(self, tv: ttk.Treeview) -> None:
        for iid in tv.get_children():
            tv.delete(iid)

    def search_now(self) -> None:
        tv = self._tree_search
        if not isinstance(tv, ttk.Treeview):
            return
        self._clear_tree(tv)

        query = (self._search_q.get() if self._search_q else "") or ""
        col = (self._search_col.get() if self._search_col else "(any)") or "(any)"
        tags = (self._search_tags.get() if self._search_tags else "") or ""
        want_local = bool(self._search_local.get()) if self._search_local else True
        want_online = bool(self._search_online.get()) if self._search_online else False
        limit = int(self._search_limit.get()) if self._search_limit else 20

        total_rows = 0

        # Local search
        if want_local:
            params: List[Any] = []
            wh: List[str] = []
            if query.strip():
                pattern = f"%{self._like_escape(query.strip())}%"
                if col == "(any)":
                    cols = ["title","source","tags","url","ingredients","instructions","notes"]
                    wh.append("(" + " OR ".join([f"{c} LIKE ? ESCAPE '{_ESCAPE_CHAR}'" for c in cols]) + ")")
                    params.extend([pattern] * len(cols))
                else:
                    wh.append(f"{col} LIKE ? ESCAPE '{_ESCAPE_CHAR}'")
                    params.append(pattern)
            if tags.strip():
                like_tags = f"%{self._like_escape(tags.strip())}%"
                wh.append(f"IFNULL(tags,'') LIKE ? ESCAPE '{_ESCAPE_CHAR}'")
                params.append(like_tags)

            where_sql = ("WHERE " + " AND ".join(wh)) if wh else ""
            sql = f"""
                SELECT 'local' AS source,
                       title, IFNULL(tags,'') AS tags, IFNULL(url,'') AS url
                  FROM recipes
                  {where_sql}
                 ORDER BY LOWER(title)
                 LIMIT ?
            """
            params.append(max(1, limit))
            try:
                rows = self.db.execute(sql, params).fetchall()
            except sqlite3.OperationalError as e:
                messagebox.showerror("Search", f"Invalid column selection:\n{e}", parent=self.winfo_toplevel())
                rows = []
            for r in rows:
                tv.insert("", "end", values=[r["source"], r["title"], r["tags"], r["url"]])
            total_rows += len(rows)

        # Online search
        if want_online and query.strip():
            try:
                hits = recipes_api.search_all(self.db, query.strip(), total=max(1, limit))
            except Exception as e:
                messagebox.showerror("Online Search", f"{e}", parent=self.winfo_toplevel())
                hits = []
            for h in hits:
                tv.insert("", "end", values=[getattr(h, "source", "online"), h.title, h.tags, h.url])
            total_rows += len(hits)

        self.set_status(f"Search results: {total_rows}")
        self.fit_columns_now(tv, exact=True, max_px_map={"url": 1600, "tags": 1000})

    def _open_selected_urls(self, tv: ttk.Treeview) -> None:
        import webbrowser
        sel = tv.selection() or []
        for iid in sel:
            url = (tv.item(iid, "values") or ["","","",""])[3]
            u = str(url).strip()
            if not u:
                continue
            if not (u.startswith("http://") or u.startswith("https://")):
                u = "http://" + u
            try:
                webbrowser.open(u, new=2)
            except Exception:
                pass

    def _import_search_rows(self, tv: ttk.Treeview, *, only_selected: bool) -> None:
        items = tv.selection() if only_selected else tv.get_children()
        if not items:
            return
        count = 0
        for iid in items:
            src, title, tags, url = (tv.item(iid, "values") or ["","","",""])[:4]
            data = {
                "title": title or "Untitled",
                "source": src or "",
                "url": url or "",
                "tags": tags or "",
                "ingredients": "",
                "instructions": "",
                "rating": 0.0,
                "prep_time": "",
                "cook_time": "",
                "servings": 0,
                "favorite": 0,
                "notes": "",
            }
            try:
                self._insert_or_update_by_url(data)
                count += 1
            except Exception:
                pass
        if count:
            self.db.commit()
            self._refresh_both()
        self.set_status(f"Imported {count} item(s) to Library")

    # ---------- CRUD ----------
    def add_recipe(self) -> None:
        data = self._edit_dialog(None)
        if not data:
            return
        self._insert_or_update_by_url(data)
        self._refresh_both()
        self.set_status("Recipe saved")

    def add_from_url(self) -> None:
        url = simpledialog.askstring("Add Recipe from URL", "Paste recipe URL:", parent=self.winfo_toplevel())
        if not url:
            return
        try:
            r = recipes_api.scrape_url(self.db, url.strip())
        except Exception as e:
            messagebox.showerror("Add from URL", f"Failed to fetch/parse:\n{e}", parent=self.winfo_toplevel())
            return
        ingredients_text = "\n".join([i.get("original", "") for i in (r.ingredients or [])]).strip()
        data = {
            "title": r.title or "Untitled",
            "source": r.source or "web",
            "url": r.url or url.strip(),
            "tags": r.tags or "",
            "ingredients": ingredients_text,
            "instructions": r.instructions or "",
            "rating": 0.0,
            "prep_time": "",
            "cook_time": "",
            "servings": 0,
            "favorite": 0,
            "notes": "",
        }

        # New: optional edit after scrape
        if isinstance(self._edit_after_url, tk.BooleanVar) and self._edit_after_url.get():
            edited = self._edit_dialog(data)
            if not edited:
                self.set_status("Canceled")
                return
            data = edited

        self._insert_or_update_by_url(data)
        self._refresh_both()
        self.set_status(f"Added from URL: {data['title']}")

    def edit_selected(self) -> None:
        tv = self._current_tree()
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        if len(sel) != 1:
            messagebox.showinfo("Cookbook", "Select one recipe to edit.", parent=self.winfo_toplevel()); return
        rid = int(sel[0])
        r = self.db.execute("""
            SELECT id, title, source, url, tags, ingredients, instructions,
                   IFNULL(rating,0.0) AS rating,
                   COALESCE(prep_time,'') AS prep_time,
                   COALESCE(cook_time,'') AS cook_time,
                   COALESCE(servings,0)   AS servings,
                   IFNULL(favorite,0)     AS favorite,
                   COALESCE(notes,'')     AS notes
              FROM recipes WHERE id=?
        """, (rid,)).fetchone()
        if not r:
            return
        data = self._edit_dialog(r)
        if not data:
            return
        self.db.execute("""
            UPDATE recipes SET
                title=?, source=?, url=?, tags=?, ingredients=?, instructions=?,
                rating=?, prep_time=?, cook_time=?, servings=?, favorite=?, notes=?
             WHERE id=?
        """, (
            data["title"], data["source"], data["url"], data["tags"],
            data["ingredients"], data["instructions"],
            data["rating"], data["prep_time"], data["cook_time"],
            data["servings"], data.get("favorite", 0), data.get("notes",""), rid
        ))
        self.db.commit()
        self._refresh_both()
        self.set_status("Recipe updated")

    def delete_selected(self) -> None:
        tv = self._current_tree()
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        if not sel:
            return
        if not self.confirm_delete(len(sel)):
            return
        ids = [int(i) for i in sel]
        qs = ",".join("?" for _ in ids)
        self.db.execute(f"DELETE FROM recipes WHERE id IN ({qs})", ids)
        self.db.commit()
        self._refresh_both()
        self.set_status(f"Deleted {len(ids)} recipe(s)")

    # ---------- Favorite toggle ----------
    def toggle_favorite_selected(self) -> None:
        tv = self._current_tree()
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        if not sel:
            return
        ids = [int(i) for i in sel]
        cur = self.db.execute(
            f"SELECT COUNT(*) AS c, SUM(CASE WHEN IFNULL(favorite,0)=1 THEN 1 ELSE 0 END) AS f FROM recipes WHERE id IN ({','.join('?' for _ in ids)})",
            ids
        ).fetchone()
        make_fav = 0 if cur and cur["c"] == cur["f"] else 1
        self.db.execute(
            f"UPDATE recipes SET favorite=? WHERE id IN ({','.join('?' for _ in ids)})",
            [make_fav, *ids]
        )
        self.db.commit()
        self._refresh_both()
        self.set_status(("Unfavorited " if not make_fav else "Favorited ") + f"{len(ids)} recipe(s)")

    # ---------- Add to Menu ----------
    def add_selected_to_menu(self) -> None:
        tv = self._current_tree()
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        if len(sel) != 1:
            messagebox.showinfo("Menu", "Select one recipe to add.", parent=self.winfo_toplevel()); return
        rid = int(sel[0])
        date = simpledialog.askstring("Menu Planner", "Date (YYYY-MM-DD):", parent=self.winfo_toplevel())
        if not date:
            return
        meal = simpledialog.askstring("Menu Planner", "Meal (Breakfast/Lunch/Dinner/Snack/Other):",
                                      initialvalue="Dinner", parent=self.winfo_toplevel()) or "Dinner"
        r = self.db.execute("SELECT title FROM recipes WHERE id=?", (rid,)).fetchone()
        if not r:
            return
        self.db.execute(
            "INSERT INTO menu_plan(date, meal, recipe_id, title, notes) VALUES(?,?,?,?,?)",
            (date.strip(), meal.strip(), rid, r["title"], "")
        )
        self.db.commit()
        self.set_status("Added to Menu")

    # ---------- Export ----------
    def export_html_visible(self) -> None:
        tv = self._current_tree()
        if not isinstance(tv, ttk.Treeview):
            return
        items = tv.get_children()
        rows = [list(tv.item(i, "values")) for i in items]
        headings = [hdr for _k, hdr, _w, _a in LIB_COLS]
        export_table_html(
            path=None,
            title="Recipes",
            columns=headings,
            rows=rows,
            subtitle="Generated from Celiac Culinary",
            meta={"Source": "Cookbook", "Rows": len(rows)},
            open_after=True,
        )

    def export_html_recipe_selected(self) -> None:
        tv = self._current_tree()
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        if not sel:
            messagebox.showinfo("Print Recipe", "Select at least one recipe in the list.")
            return
        ids = [int(s) for s in sel if str(s).isdigit()]
        if not ids:
            messagebox.showinfo("Print Recipe", "No valid recipe selected.")
            return
        qs = ",".join("?" for _ in ids)
        rows = self.db.execute(f"""
            SELECT title, source, url, tags, ingredients, instructions,
                   IFNULL(rating,0.0) AS rating,
                   COALESCE(prep_time,'') AS prep_time,
                   COALESCE(cook_time,'') AS cook_time,
                   COALESCE(servings,0)   AS servings
              FROM recipes WHERE id IN ({qs})
             ORDER BY LOWER(title)
        """, ids).fetchall()
        export_recipes_html(
            [dict(r) for r in rows],
            title = "Recipe" if len(rows)==1 else "Recipes",
            subtitle = "Printable view",
            meta = {"Count": len(rows)},
            open_after = True,
        )

    # ---------- Add/Edit dialog ----------
    def _edit_dialog(self, row: Optional[sqlite3.Row | dict]) -> Optional[dict]:
        dlg = tk.Toplevel(self); dlg.title("Recipe"); dlg.transient(self.winfo_toplevel()); dlg.grab_set()
        frm = ttk.Frame(dlg, padding=8); frm.grid(row=0, column=0, sticky="nsew")
        dlg.grid_rowconfigure(0, weight=1); dlg.grid_columnconfigure(0, weight=1)

        def g(k, d=""):
            if isinstance(row, dict):
                return row.get(k, d)
            if row and k in row.keys():
                return row[k]
            return d

        sv = {
            "title": tk.StringVar(value=str(g("title",""))),
            "source": tk.StringVar(value=str(g("source",""))),
            "url": tk.StringVar(value=str(g("url",""))),
            "tags": tk.StringVar(value=str(g("tags",""))),
            "prep_time": tk.StringVar(value=str(g("prep_time",""))),
            "cook_time": tk.StringVar(value=str(g("cook_time",""))),
            "servings": tk.StringVar(value=str(g("servings","") or "")),
            "rating": tk.StringVar(value=str(g("rating","0") or "0")),
            "favorite": tk.BooleanVar(value=bool(g("favorite", 0))),
            "notes": tk.StringVar(value=str(g("notes",""))),
        }

        r = 0
        def roww(label: str, widget: tk.Widget, col=1):
            nonlocal r
            ttk.Label(frm, text=label).grid(row=r, column=0, sticky="e", padx=(0,8), pady=(0,4))
            widget.grid(row=r, column=col, sticky="ew", pady=(0,4))
            frm.grid_columnconfigure(col, weight=1)
            r += 1

        roww("Title *", ttk.Entry(frm, textvariable=sv["title"], width=40))
        roww("Source", ttk.Entry(frm, textvariable=sv["source"], width=30))
        roww("URL", ttk.Entry(frm, textvariable=sv["url"], width=40))
        roww("Tags", ttk.Entry(frm, textvariable=sv["tags"], width=40))

        pack2 = ttk.Frame(frm); roww("Times / Servings / ★", pack2, col=1)
        ttk.Entry(pack2, textvariable=sv["prep_time"], width=12).pack(side="left")
        ttk.Label(pack2, text="Prep").pack(side="left", padx=(4,10))
        ttk.Entry(pack2, textvariable=sv["cook_time"], width=12).pack(side="left")
        ttk.Label(pack2, text="Cook").pack(side="left", padx=(4,10))
        ttk.Entry(pack2, textvariable=sv["servings"], width=6).pack(side="left")
        ttk.Label(pack2, text="Servings").pack(side="left", padx=(4,10))
        ttk.Entry(pack2, textvariable=sv["rating"], width=6).pack(side="left")
        ttk.Label(pack2, text="★").pack(side="left", padx=(4,10))
        ttk.Checkbutton(pack2, text="Favorite", variable=sv["favorite"]).pack(side="left")

        ttk.Label(frm, text="Ingredients").grid(row=r, column=0, sticky="ne", padx=(0,8))
        txt_ing = tk.Text(frm, height=10, width=60, wrap="word")
        txt_ing.insert("1.0", str(g("ingredients","") or ""))
        txt_ing.grid(row=r, column=1, sticky="nsew"); r += 1

        ttk.Label(frm, text="Instructions").grid(row=r, column=0, sticky="ne", padx=(0,8))
        txt_ins = tk.Text(frm, height=12, width=60, wrap="word")
        txt_ins.insert("1.0", str(g("instructions","") or ""))
        txt_ins.grid(row=r, column=1, sticky="nsew"); r += 1

        roww("Notes", ttk.Entry(frm, textvariable=sv["notes"], width=40))

        out: dict = {}
        def on_save():
            title = (sv["title"].get() or "").strip()
            if not title:
                messagebox.showerror("Cookbook", "Title is required.", parent=dlg); return
            ingredients = txt_ing.get("1.0","end").strip()
            instructions = txt_ins.get("1.0","end").strip()
            try:
                rating = float((sv["rating"].get() or "0").strip() or 0)
            except Exception:
                rating = 0.0
            try:
                servings = int((sv["servings"].get() or "0").strip() or 0)
            except Exception:
                servings = 0
            out.update({
                "title": title,
                "source": (sv["source"].get() or "").strip(),
                "url": (sv["url"].get() or "").strip(),
                "tags": (sv["tags"].get() or "").strip(),
                "ingredients": ingredients,
                "instructions": instructions,
                "rating": rating,
                "prep_time": (sv["prep_time"].get() or "").strip(),
                "cook_time": (sv["cook_time"].get() or "").strip(),
                "servings": servings,
                "favorite": 1 if sv["favorite"].get() else 0,
                "notes": (sv["notes"].get() or "").strip(),
            })
            dlg.destroy()

        btns = ttk.Frame(dlg, padding=(8,6)); btns.grid(row=1, column=0, sticky="e")
        ttk.Button(btns, text="Cancel", command=dlg.destroy).grid(row=0, column=0, padx=(0,6))
        ttk.Button(btns, text="Save", command=on_save).grid(row=0, column=1)
        dlg.wait_window()
        return out or None

    # ---------- Insert/Update logic ----------
    def _insert_or_update_by_url(self, data: dict) -> None:
        url = (data.get("url") or "").strip()
        have_unique = self._has_unique_url() and bool(url)
        if have_unique:
            self.db.execute("""
                INSERT INTO recipes(title, source, url, tags, ingredients, instructions, rating, prep_time, cook_time, servings, favorite, notes)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(url) DO UPDATE SET
                    title=excluded.title, source=excluded.source, tags=excluded.tags,
                    ingredients=excluded.ingredients, instructions=excluded.instructions,
                    rating=excluded.rating, prep_time=excluded.prep_time, cook_time=excluded.cook_time,
                    servings=excluded.servings, favorite=excluded.favorite, notes=excluded.notes
            """, (
                data["title"], data["source"], url, data["tags"], data["ingredients"], data["instructions"],
                data["rating"], data["prep_time"], data["cook_time"], data["servings"], data.get("favorite",0), data.get("notes","")
            ))
            self.db.commit()
            return
        if url:
            r = self.db.execute("SELECT id FROM recipes WHERE url=?", (url,)).fetchone()
            if r:
                self.db.execute("""
                    UPDATE recipes SET
                        title=?, source=?, tags=?, ingredients=?, instructions=?, rating=?,
                        prep_time=?, cook_time=?, servings=?, favorite=?, notes=?
                     WHERE id=?
                """, (
                    data["title"], data["source"], data["tags"], data["ingredients"], data["instructions"],
                    data["rating"], data["prep_time"], data["cook_time"], data["servings"], data.get("favorite",0),
                    data.get("notes",""), r["id"]
                ))
                self.db.commit()
                return
        self.db.execute("""
            INSERT INTO recipes(title, source, url, tags, ingredients, instructions, rating, prep_time, cook_time, servings, favorite, notes)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            data["title"], data["source"], url, data["tags"], data["ingredients"], data["instructions"],
            data["rating"], data["prep_time"], data["cook_time"], data["servings"], data.get("favorite",0), data.get("notes","")
        ))
        self.db.commit()

    # ---------- CSV import ----------
    def import_csv(self) -> None:
        path = filedialog.askopenfilename(
            parent=self.winfo_toplevel(),
            title="Import Recipes CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8-sig", newline="") as f:
                rows = list(csv.reader(f))
        except Exception as e:
            messagebox.showerror("Import CSV", f"Failed to read CSV:\n{e}", parent=self.winfo_toplevel()); return
        if not rows:
            messagebox.showinfo("Import CSV", "CSV is empty.", parent=self.winfo_toplevel()); return

        headers = [h.strip() for h in rows[0]]
        sample = rows[1 : min(len(rows), 6)]
        mapping = self._mapping_dialog(headers, sample)
        if mapping is None:
            return

        ok, fail = self._import_rows(headers, rows[1:], mapping)
        base = os.path.basename(path)
        messagebox.showinfo("Import CSV", f"{base}\nImported: {ok}\nSkipped: {fail}", parent=self.winfo_toplevel())
        self._refresh_both()

    def _mapping_dialog(self, headers: list[str], sample_rows: list[list[str]]) -> dict[str, str] | None:
        dlg = tk.Toplevel(self); dlg.title("Map CSV Columns → Recipe Fields"); dlg.transient(self.winfo_toplevel()); dlg.grab_set()
        frm = ttk.Frame(dlg, padding=10); frm.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frm, text="Map CSV columns. Title required. Ingredients and Instructions supported.").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 8)
        )
        choices = ["(skip)"] + headers
        vars_map: dict[str, tk.StringVar] = {}
        r = 1
        for field in CSV_FIELDS_ORDER:
            ttk.Label(frm, text=field).grid(row=r, column=0, sticky="e", padx=(0,6), pady=2)
            v = tk.StringVar(value="(skip)")
            ttk.Combobox(frm, values=choices, textvariable=v, width=32, state="readonly").grid(row=r, column=1, sticky="w", pady=2)
            vars_map[field] = v
            r += 1

        prev = ttk.Frame(frm); prev.grid(row=1, column=2, rowspan=r, sticky="n")
        ttk.Label(prev, text="Sample rows:").grid(row=0, column=0, sticky="w")
        for i, row in enumerate(sample_rows):
            ttk.Label(prev, text=" | ".join(row[:6]) + (" ..." if len(row) > 6 else "")).grid(row=i+1, column=0, sticky="w")

        err = ttk.Label(frm, text="", foreground="red"); err.grid(row=r, column=1, sticky="w", pady=(6, 0))
        btns = ttk.Frame(dlg, padding=(10, 8)); btns.grid(row=1, column=0, sticky="e")
        ttk.Button(btns, text="Cancel", command=dlg.destroy).grid(row=0, column=0, padx=(0,6))

        result: dict[str, str] = {}
        def ok():
            nonlocal result
            mapping = {fld: v.get() for fld, v in vars_map.items()}
            if mapping.get("title") in (None, "", "(skip)"):
                err.config(text="Title must be mapped."); return
            result = {fld: col for fld, col in mapping.items() if col and col != "(skip)"}
            dlg.destroy()
        ttk.Button(btns, text="Import", command=ok).grid(row=0, column=1)
        dlg.wait_window()
        return result or None

    def _import_rows(self, headers: list[str], rows: list[list[str]], mapping: dict[str, str]) -> tuple[int,int]:
        index = {h: i for i, h in enumerate(headers)}
        ok = 0
        fail = 0
        for row in rows:
            try:
                data: dict[str, object] = {}
                for fld, col in mapping.items():
                    i = index.get(col, -1)
                    data[fld] = (row[i] if 0 <= i < len(row) else "").strip()
                title = str(data.get("title","")).strip()
                if not title:
                    fail += 1; continue
                try:
                    data["rating"] = float(str(data.get("rating","") or "0"))
                except Exception:
                    data["rating"] = 0.0
                try:
                    data["servings"] = int(str(data.get("servings","") or "0"))
                except Exception:
                    data["servings"] = 0
                fv = str(data.get("favorite","")).strip().lower()
                data["favorite"] = 1 if fv in ("1","y","yes","true","t") else 0
                for k in ("source","url","tags","prep_time","cook_time","notes","ingredients","instructions"):
                    data[k] = str(data.get(k,"") or "")
                self._insert_or_update_by_url(data)
                ok += 1
            except Exception:
                fail += 1
        return ok, fail

    # ---------- TXT import ----------
    def import_txt(self) -> None:
        path = filedialog.askopenfilename(
            parent=self.winfo_toplevel(),
            title="Import Recipe .TXT",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                text = f.read()
        except Exception as e:
            messagebox.showerror("Import .TXT", f"Failed to read file:\n{e}", parent=self.winfo_toplevel()); return

        data = self._parse_recipe_txt(text, fallback_title=os.path.splitext(os.path.basename(path))[0])
        if not data or not data.get("title"):
            messagebox.showerror("Import .TXT", "Could not parse a title. Ensure the file has a title and sections.", parent=self.winfo_toplevel()); return

        self._insert_or_update_by_url(data)
        self._refresh_both()
        self.set_status(f"Imported: {data['title']}")

    def _parse_recipe_txt(self, text: str, *, fallback_title: str = "Untitled") -> dict:
        s = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = [ln.rstrip() for ln in s.split("\n")]

        def find_header(patterns: list[str]) -> int | None:
            rx = re.compile(r"^\s*(?:" + "|".join(patterns) + r")\s*:?\s*$", re.IGNORECASE)
            for i, ln in enumerate(lines):
                if rx.match(ln):
                    return i
            return None

        idx_ing = find_header(["ingredients?"])
        idx_ins = find_header(["instructions?", "directions?", "method", "preparation"])
        idx_notes = find_header(["notes?"])

        title = None
        scan_upto = idx_ing if idx_ing is not None else 10
        scan_upto = min(scan_upto if scan_upto is not None else len(lines), len(lines))
        for i in range(0, scan_upto):
            t = lines[i].strip()
            if t:
                title = t
                break
        if not title:
            title = fallback_title.strip() or "Untitled"

        def section(start: int | None, end: int | None) -> str:
            if start is None:
                return ""
            a = start + 1
            b = end if end is not None else len(lines)
            return "\n".join(lines[a:b]).strip()

        ing_end = idx_ins if idx_ins is not None else idx_notes
        ins_end = idx_notes

        ingredients = section(idx_ing, ing_end)
        instructions = section(idx_ins, ins_end)
        notes = section(idx_notes, None)

        def clean_bullets(txt: str) -> str:
            out = []
            for ln in txt.splitlines():
                out.append(re.sub(r"^\s*[-*•]\s*", "", ln).rstrip())
            return "\n".join(out).strip()
        ingredients = clean_bullets(ingredients)
        instructions = instructions.strip()

        header_block = "\n".join(lines[: (idx_ing or 0)]).strip()
        url = ""
        m = re.search(r"https?://\S+", header_block, re.IGNORECASE)
        if m:
            url = m.group(0)

        source = ""
        m2 = re.search(r"\bby\s+(.+)$", header_block, re.IGNORECASE)
        if m2:
            source = m2.group(1).strip()
        elif (m3 := re.search(r"\bfrom\s+(.+)$", header_block, re.IGNORECASE)):
            source = m3.group(1).strip()

        return {
            "title": title,
            "source": source,
            "url": url,
            "tags": "",
            "ingredients": ingredients,
            "instructions": instructions,
            "rating": 0.0,
            "prep_time": "",
            "cook_time": "",
            "servings": 0,
            "favorite": 0,
            "notes": notes,
        }
