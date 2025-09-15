from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, List, Tuple

from panels.base_panel import BasePanel
from utils.export import export_table_html, export_recipes_html

# Visible columns in lists (prepended with Favorite)
LIB_COLS: List[Tuple[str, str, int, str]] = [
    ("favorite",   "♥",        34,  "c"),  # heart ♥
    ("title",      "Title",       300, "w"),
    ("source",     "Source",      130, "w"),
    ("tags",       "Tags",        160, "w"),
    ("url",        "URL",         220, "w"),
    ("prep_time",  "Prep",         80, "c"),
    ("cook_time",  "Cook",         80, "c"),
    ("servings",   "Servings",     80, "c"),
    ("rating",     "★",        60, "c"),   # star ★
]

MEALS = ["Breakfast","Lunch","Dinner","Snack","Other"]

class CookbookPanel(BasePanel):
    """Recipes Library with Favorites: ♥ sort toggle and a dedicated Favorites tab."""

    def __init__(self, master, app, **kw):
        # UI state
        self._nb: Optional[ttk.Notebook] = None
        self._tab_lib: Optional[ttk.Frame] = None
        self._tab_fav: Optional[ttk.Frame] = None
        self._tree_lib: Optional[ttk.Treeview] = None
        self._tree_fav: Optional[ttk.Treeview] = None
        self._search_q: Optional[tk.StringVar] = None
        self._fav_only: Optional[tk.BooleanVar] = None
        self._fav_first: Optional[tk.BooleanVar] = None
        super().__init__(master, app, **kw)

    # ---------- search ----------
    def _do_search(self, q: str | None = None) -> None:
        if q is None:
            # fall back to the search var if available
            v = self._widgets.get("search_var")
            try:
                q = (v.get() if v else "").strip()
            except Exception:
                q = ""
        q = q.strip() if q else ""
        # stub: replace with real search logic later
        self.info(f"Search is stubbed for now. Query: {q}")

    # ---------- UI ----------
    def build(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Ensure DB column for favorites exists before any queries
        self._ensure_schema()

        nb = ttk.Notebook(self)
        nb.grid(row=0, column=0, sticky="nsew")
        self._nb = nb

        # Search tab (basic)
        t_search = ttk.Frame(nb); nb.add(t_search, text="Search")
        sbar, svar, _ = self.build_search_bar(
            t_search,
            on_return=self._do_search,   # will be called with the query string
            refresh_text="Search")
        sbar.pack(fill="x", padx=6, pady=6)
        ttk.Label(t_search, text="(Search providers coming soon)").pack(anchor="w", padx=12, pady=12)
        self._search_q = svar

        # Shared sort state
        self._fav_first = tk.BooleanVar(value=False)

        # Library tab
        self._tab_lib = ttk.Frame(nb)
        nb.add(self._tab_lib, text="Library")
        self._tab_lib.grid_rowconfigure(1, weight=1)
        self._tab_lib.grid_columnconfigure(0, weight=1)

        top = ttk.Frame(self._tab_lib); top.grid(row=0, column=0, sticky="ew", padx=6, pady=(6,4))
        ttk.Button(top, text="Add", command=self.add_recipe).pack(side="left")
        ttk.Button(top, text="Edit", command=self.edit_selected).pack(side="left", padx=(6,0))
        ttk.Button(top, text="Delete", command=self.delete_selected).pack(side="left", padx=(6,0))
        ttk.Button(top, text="Export HTML", command=self.export_html_visible).pack(side="left", padx=(12,0))
        ttk.Button(top, text="Print Recipe", command=self.export_html_recipe_selected).pack(side="left", padx=(8,0))
        ttk.Button(top, text="Add to Menu", command=self.add_selected_to_menu).pack(side="left", padx=(12,0))
        ttk.Button(top, text="♥ Favorite", command=self.toggle_favorite_selected).pack(side="left", padx=(12,0))
        self._fav_only = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text="Favorites only", variable=self._fav_only, command=self._refresh_both).pack(side="left", padx=(12,0))
        ttk.Checkbutton(top, text="♥ first", variable=self._fav_first, command=self._refresh_both).pack(side="left", padx=(6,0))

        wrap = ttk.Frame(self._tab_lib); wrap.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0,6))
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

        menu = self._make_context_menu()
        def popup(ev, m=menu):
            try: m.tk_popup(ev.x_root, ev.y_root)
            finally: m.grab_release()
        tv.bind("<Button-3>", popup)
        tv.bind("<Double-1>", lambda e: self.edit_selected())
        tv.bind("<Key-f>", lambda e: self.toggle_favorite_selected())  # quick toggle
        self._tree_lib = tv

        # Favorites tab (always favorites-only)
        self._tab_fav = ttk.Frame(nb)
        nb.add(self._tab_fav, text="Favorites")
        self._tab_fav.grid_rowconfigure(1, weight=1)
        self._tab_fav.grid_columnconfigure(0, weight=1)

        top2 = ttk.Frame(self._tab_fav); top2.grid(row=0, column=0, sticky="ew", padx=6, pady=(6,4))
        ttk.Button(top2, text="Edit", command=self.edit_selected).pack(side="left")
        ttk.Button(top2, text="Delete", command=self.delete_selected).pack(side="left", padx=(6,0))
        ttk.Button(top2, text="Export HTML", command=self.export_html_visible).pack(side="left", padx=(12,0))
        ttk.Button(top2, text="Print Recipe", command=self.export_html_recipe_selected).pack(side="left", padx=(8,0))
        ttk.Button(top2, text="Remove ♥", command=self.toggle_favorite_selected).pack(side="left", padx=(12,0))
        ttk.Checkbutton(top2, text="♥ first", variable=self._fav_first, command=self._refresh_both).pack(side="left", padx=(6,0))

        wrap2 = ttk.Frame(self._tab_fav); wrap2.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0,6))
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

        menu2 = self._make_context_menu()
        def popup2(ev, m=menu2):
            try: m.tk_popup(ev.x_root, ev.y_root)
            finally: m.grab_release()
        tv2.bind("<Button-3>", popup2)
        tv2.bind("<Double-1>", lambda e: self.edit_selected())
        tv2.bind("<Key-f>", lambda e: self.toggle_favorite_selected())
        self._tree_fav = tv2

        # Default to Library tab
        nb.select(self._tab_lib)

        self._refresh_both()

    def _make_context_menu(self) -> tk.Menu:
        m = tk.Menu(self, tearoff=0)
        m.add_command(label="Edit", command=self.edit_selected)
        m.add_command(label="Delete", command=self.delete_selected)
        m.add_separator()
        m.add_command(label="Add to Menu", command=self.add_selected_to_menu)
        m.add_separator()
        m.add_command(label="Toggle Favorite", command=self.toggle_favorite_selected)
        m.add_command(label="Export HTML (visible)", command=self.export_html_visible)
        m.add_command(label="Print Recipe (HTML)", command=self.export_html_recipe_selected)
        return m

    # ---------- Helpers ----------
    def _current_tree(self) -> Optional[ttk.Treeview]:
        nb = self._nb
        if not isinstance(nb, ttk.Notebook):
            return self._tree_lib
        cur = nb.select()
        if self._tab_fav and str(self._tab_fav) == cur:
            return self._tree_fav
        return self._tree_lib

    def _order_sql(self) -> str:
        fav_first = bool(self._fav_first.get()) if isinstance(self._fav_first, tk.BooleanVar) else False
        return "ORDER BY IFNULL(favorite,0) DESC, LOWER(title)" if fav_first else "ORDER BY LOWER(title)"

    def _refresh_both(self) -> None:
        self.refresh_library()
        self.refresh_favorites()

    # ---------- Schema ----------
    def _ensure_schema(self) -> None:
        try:
            cols = {r[1] for r in self.db.execute("PRAGMA table_info(recipes)").fetchall()}
            if "favorite" not in cols:
                self.db.execute("ALTER TABLE recipes ADD COLUMN favorite INTEGER NOT NULL DEFAULT 0")
                self.db.commit()
        except Exception as e:
            self.set_status(f"Schema check failed: {e}")

    # ---------- Data (Library tab) ----------
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

    # ---------- Data (Favorites tab) ----------
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

    # ---------- Search placeholder ----------
    def _do_search(self) -> None:
        q = (self._search_q.get() or "").strip()
        if not q:
            self.info("Type something to search.")
            return
        self.info(f"Search is stubbed for now. Query: {q}")

    # ---------- CRUD ----------
    def add_recipe(self) -> None:
        data = self._edit_dialog(None)
        if not data:
            return
        self.db.execute("""
            INSERT INTO recipes(title, source, url, tags, ingredients, instructions, rating, prep_time, cook_time, servings, favorite)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(url) DO UPDATE SET
                title=excluded.title, source=excluded.source, tags=excluded.tags,
                ingredients=excluded.ingredients, instructions=excluded.instructions,
                rating=excluded.rating, prep_time=excluded.prep_time, cook_time=excluded.cook_time, servings=excluded.servings,
                favorite=excluded.favorite
        """, (
            data["title"], data["source"], data["url"], data["tags"], data["ingredients"], data["instructions"],
            data["rating"], data["prep_time"], data["cook_time"], data["servings"], data.get("favorite", 0)
        ))
        self.db.commit()
        self._refresh_both()
        self.set_status("Recipe saved")

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
                   IFNULL(favorite,0)     AS favorite
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
                rating=?, prep_time=?, cook_time=?, servings=?, favorite=?
             WHERE id=?
        """, (
            data["title"], data["source"], data["url"], data["tags"], data["ingredients"], data["instructions"],
            data["rating"], data["prep_time"], data["cook_time"], data["servings"], data.get("favorite", 0), rid
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

    # ---------- Favorites ----------
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

    # ---------- edit dialog ----------
    def _edit_dialog(self, row: Optional[dict]) -> Optional[dict]:
        dlg = tk.Toplevel(self); dlg.title("Recipe"); dlg.transient(self.winfo_toplevel()); dlg.grab_set()
        frm = ttk.Frame(dlg, padding=8); frm.grid(row=0, column=0, sticky="nsew")
        dlg.grid_rowconfigure(0, weight=1); dlg.grid_columnconfigure(0, weight=1)

        def g(k, d=""):
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
        }

        r = 0
        def roww(label: str, widget: tk.Widget, col=1):
            nonlocal r
            ttk.Label(frm, text=label).grid(row=r, column=0, sticky="e", padx=(0,8), pady=(0,4))
            widget.grid(row=r, column=col, sticky="ew", pady=(0,4))
            frm.grid_columnconfigure(col, weight=1)
            r += 1

        roww("Title", ttk.Entry(frm, textvariable=sv["title"], width=40))
        roww("Source", ttk.Entry(frm, textvariable=sv["source"], width=30))
        roww("URL", ttk.Entry(frm, textvariable=sv["url"], width=40))
        roww("Tags", ttk.Entry(frm, textvariable=sv["tags"], width=40))

        pack2 = ttk.Frame(frm); roww("Times / Servings", pack2, col=1)
        ttk.Entry(pack2, textvariable=sv["prep_time"], width=12).pack(side="left")
        ttk.Label(pack2, text="Prep").pack(side="left", padx=(4,10))
        ttk.Entry(pack2, textvariable=sv["cook_time"], width=12).pack(side="left")
        ttk.Label(pack2, text="Cook").pack(side="left", padx=(4,10))
        ttk.Entry(pack2, textvariable=sv["servings"], width=6).pack(side="left")
        ttk.Label(pack2, text="Servings").pack(side="left", padx=(4,10))
        ttk.Entry(pack2, textvariable=sv["rating"], width=6).pack(side="left")
        ttk.Label(pack2, text="★").pack(side="left", padx=(4,10))
        ttk.Checkbutton(pack2, text="Favorite", variable=sv["favorite"]).pack(side="left")  # why: quick toggle during edit

        ttk.Label(frm, text="Ingredients (JSON or lines)").grid(row=r, column=0, sticky="ne", padx=(0,8))
        txt_ing = tk.Text(frm, height=8, width=60, wrap="word")
        txt_ing.insert("1.0", str(g("ingredients","") or ""))
        txt_ing.grid(row=r, column=1, sticky="nsew"); r += 1

        ttk.Label(frm, text="Instructions").grid(row=r, column=0, sticky="ne", padx=(0,8))
        txt_ins = tk.Text(frm, height=8, width=60, wrap="word")
        txt_ins.insert("1.0", str(g("instructions","") or ""))
        txt_ins.grid(row=r, column=1, sticky="nsew"); r += 1

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
            })
            dlg.destroy()

        btns = ttk.Frame(dlg, padding=(8,6)); btns.grid(row=1, column=0, sticky="e")
        ttk.Button(btns, text="Cancel", command=dlg.destroy).grid(row=0, column=0, padx=(0,6))
        ttk.Button(btns, text="Save", command=on_save).grid(row=0, column=1)
        dlg.wait_window()
        return out or None

    def export_html_recipe_selected(self) -> None:
        """Export the selected recipe(s) as printable HTML and open in browser."""
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
        # Fetch full recipe details
        qs = ",".join("?" for _ in ids)
        rows = self.db.execute(f"""            SELECT title, source, url, tags, ingredients, instructions,
                   IFNULL(rating,0.0) AS rating,
                   COALESCE(prep_time,'') AS prep_time,
                   COALESCE(cook_time,'') AS cook_time,
                   COALESCE(servings,0)   AS servings
              FROM recipes WHERE id IN ({qs})
             ORDER BY LOWER(title)
        """, ids).fetchall()
        # Convert sqlite Row objects to dicts
        recipes = [dict(r) for r in rows]
        export_recipes_html(
            recipes,
            title = "Recipe" if len(recipes)==1 else "Recipes",
            subtitle = "Printable view",
            meta = {"Count": len(recipes)},
            open_after = True,
        )

    def print_recipe(self, recipe_id: int):
        """Prints or exports the recipe with the given ID."""
        # ... implementation ...
