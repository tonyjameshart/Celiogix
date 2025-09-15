# panels/menu_panel.py

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, List, Tuple
import datetime
import calendar
import sqlite3

from panels.base_panel import BasePanel
from utils.export import export_table_html, export_recipes_html
from utils.scroll import ScrollFrame  # horizontal/vertical panel scrolling

# ------------------------- Tiny modal date picker -------------------------
class _DatePickerDialog(tk.Toplevel):
    """Modal mini-calendar that returns ISO date (YYYY-MM-DD) via .result."""

    def __init__(self, parent: tk.Misc, initial: Optional[datetime.date] = None, title: str = "Choose Date"):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        self.result: Optional[str] = None

        today = datetime.date.today()
        if initial is None:
            initial = today

        self._y = initial.year
        self._m = initial.month

        outer = ttk.Frame(self, padding=8)
        outer.grid(row=0, column=0, sticky="nsew")
        outer.grid_columnconfigure(0, weight=1)

        # Header: month nav + Today
        hdr = ttk.Frame(outer)
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        hdr.grid_columnconfigure(1, weight=1)
        ttk.Button(hdr, text="◀", width=3, command=lambda: self._shift(-1)).pack(side="left")
        self._label = ttk.Label(hdr, width=18, anchor="center")
        self._label.pack(side="left", expand=True)
        ttk.Button(hdr, text="▶", width=3, command=lambda: self._shift(+1)).pack(side="left")
        ttk.Button(hdr, text="Today", command=lambda: self._choose(today)).pack(side="right")

        # Weekday header + days grid
        self._grid = ttk.Frame(outer)
        self._grid.grid(row=1, column=0)
        for i, wd in enumerate(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
            ttk.Label(self._grid, text=wd, width=4, anchor="center").grid(row=0, column=i, padx=1, pady=(0, 2))

        # Footer
        ftr = ttk.Frame(outer)
        ftr.grid(row=2, column=0, sticky="e", pady=(6, 0))
        ttk.Button(ftr, text="Cancel", command=self._cancel).pack(side="right")

        self._rebuild()
        self.wait_visibility()
        self.focus_set()
        self.bind("<Escape>", lambda _e: self._cancel())

    def _shift(self, delta_months: int) -> None:
        y, m = self._y, self._m
        m += delta_months
        while m < 1:
            m += 12
            y -= 1
        while m > 12:
            m -= 12
            y += 1
        self._y, self._m = y, m
        self._rebuild()

    def _choose(self, d: datetime.date) -> None:
        self.result = d.isoformat()
        self.destroy()

    def _cancel(self) -> None:
        self.result = None
        self.destroy()

    def _rebuild(self) -> None:
        # Clear rows > 0
        for w in self._grid.grid_slaves():
            info = w.grid_info()
            if int(info.get("row", 0)) > 0:
                w.destroy()

        self._label.config(text=f"{calendar.month_name[self._m]} {self._y}")

        first_wd, days_in_month = calendar.monthrange(self._y, self._m)  # Monday=0
        col = (first_wd + 6) % 7  # Monday-first
        row = 1
        for day in range(1, days_in_month + 1):
            d = datetime.date(self._y, self._m, day)
            b = ttk.Button(self._grid, text=str(day), width=4, command=lambda dd=d: self._choose(dd))
            b.grid(row=row, column=col, padx=1, pady=1)
            col += 1
            if col > 6:
                col = 0
                row += 1


# ------------------------------ Panel proper ------------------------------
# Menu items view
MENU_COLS: List[Tuple[str, str, int, str]] = [
    ("date", "Date", 100, "c"),
    ("meal", "Meal", 100, "w"),
    ("title", "Recipe", 300, "w"),
    ("prep_time", "Prep", 80, "c"),
    ("cook_time", "Cook", 80, "c"),
    ("servings", "Servings", 80, "c"),
    ("notes", "Notes", 240, "w"),
]

# Recipe library columns (now inside a Notebook tab)
REC_COLS: List[Tuple[str, str, int, str]] = [
    ("title", "Title", 280, "w"),
    ("source", "Source", 140, "w"),
    ("prep_time", "Prep", 80, "c"),
    ("cook_time", "Cook", 80, "c"),
    ("servings", "Servings", 80, "c"),
]

MEALS = ["Breakfast", "Lunch", "Dinner", "Snack", "Other"]


class MenuPanel(BasePanel):
    """Notebook with two tabs: Menu (default) and Recipes.
    Wrapped in ScrollFrame so the whole panel can pan horizontally when content is wider than the viewport.
    """

    def __init__(self, master, app, **kw):
        self._tree_menu: Optional[ttk.Treeview] = None
        self._tree_rec: Optional[ttk.Treeview] = None
        self._menu_hsb: Optional[ttk.Scrollbar] = None
        self._rec_hsb: Optional[ttk.Scrollbar] = None
        self._scroller: Optional[ScrollFrame] = None
        self._fit_job: Optional[str] = None
        self._right_nb: Optional[ttk.Notebook] = None
        super().__init__(master, app, **kw)

    # ---------- helpers ----------
    def _open_date_picker(self, parent: tk.Misc, initial_iso: Optional[str] = None) -> Optional[str]:
        init_date: Optional[datetime.date] = None
        if initial_iso:
            try:
                init_date = datetime.date.fromisoformat(initial_iso)
            except Exception:
                init_date = None
        dp = _DatePickerDialog(parent, initial=init_date, title="Choose Date")
        dp.wait_window()
        return dp.result  # ISO string or None

    def _setup_treeview(self, treeview: ttk.Treeview, columns: List[Tuple[str, str, int, str]]) -> None:
        for k, h, w, a in columns:
            treeview.heading(k, text=h)
            anc = {"w": "w", "c": "center", "e": "e"}.get(a, "w")
            treeview.column(k, width=w, anchor=anc, stretch=False)

    # ---------- UI ----------
    def build(self) -> None:
        # Outer: scrollable wrapper so the content can pan horizontally when wider than the viewport
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        scroller = ScrollFrame(self, autohide=True)
        self._scroller = scroller
        scroller.grid(row=0, column=0, sticky="nsew")
        # persist + update on size/content changes
        try:
            scroller.hbar.bind("<ButtonRelease-1>", lambda _e: (self._save_scroll(), self._update_scrollbars()))
            scroller.content.bind("<Configure>", lambda _e: self._update_scrollbars())
            scroller.canvas.bind("<Configure>", lambda _e: self._update_scrollbars())
            scroller.content.bind("<Shift-MouseWheel>", lambda _e: self._save_scroll())
        except Exception:
            pass

        outer = scroller.content
        # Keep natural width so the outer scroller can pan
        outer.grid_rowconfigure(0, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        # Single Notebook hosting both tabs: Menu (default) and Recipes
        nb = ttk.Notebook(outer)
        self._right_nb = nb
        nb.grid(row=0, column=0, sticky="nsew")

        # ----- TAB: Menu (default) -----
        tab_menu = ttk.Frame(nb, padding=6)
        nb.add(tab_menu, text="Menu")
        nb.select(tab_menu)  # make Menu the default-selected tab

        ttk.Label(tab_menu, text="Menu").pack(anchor="w")
        wrap_m = ttk.Frame(tab_menu)
        wrap_m.pack(fill="both", expand=True)
        wrap_m.grid_rowconfigure(0, weight=1)
        wrap_m.grid_columnconfigure(0, weight=1)

        tvm = ttk.Treeview(
            wrap_m, columns=[c[0] for c in MENU_COLS], show="headings", height=16, selectmode="extended"
        )
        self._setup_treeview(tvm, MENU_COLS)
        tvm.grid(row=0, column=0, sticky="nw")
        # per-tree horizontal scrollbar (fallback when outer H-bar hidden)
        hsbm = ttk.Scrollbar(wrap_m, orient="horizontal", command=tvm.xview)
        self._menu_hsb = hsbm
        tvm.configure(xscrollcommand=hsbm.set)
        hsbm.grid(row=1, column=0, sticky="ew")
        self._tree_menu = tvm

        # Buttons for Menu tab
        btns = ttk.Frame(tab_menu)
        btns.pack(fill="x", pady=(6, 0))
        ttk.Button(btns, text="Edit", command=self.edit_selected).pack(fill="x")
        ttk.Button(btns, text="Delete", command=self.delete_selected).pack(fill="x", pady=(4, 0))
        ttk.Button(btns, text="Export HTML", command=self.export_html_menu).pack(fill="x", pady=(6, 0))

        # ----- TAB: Recipes -----
        tab_recipes = ttk.Frame(nb, padding=(6, 6))
        nb.add(tab_recipes, text="Recipes")

        ttk.Label(tab_recipes, text="Recipes").grid(row=0, column=0, sticky="w")

        tuv = ttk.Treeview(
            tab_recipes,
            columns=[c[0] for c in REC_COLS],
            show="headings",
            selectmode="extended",
            height=16,
        )
        self._setup_treeview(tuv, REC_COLS)
        tuv.grid(row=1, column=0, sticky="nsew")
        self._tree_rec = tuv

        vsb = ttk.Scrollbar(tab_recipes, orient="vertical", command=tuv.yview)
        tuv.configure(yscrollcommand=vsb.set)
        vsb.grid(row=1, column=1, sticky="ns")

        # per-tree horizontal scrollbar (fallback)
        hsbr = ttk.Scrollbar(tab_recipes, orient="horizontal", command=tuv.xview)
        self._rec_hsb = hsbr
        tuv.configure(xscrollcommand=hsbr.set)
        hsbr.grid(row=2, column=0, sticky="ew")

        # "Add From Selection" lives in the Recipes tab
        tab_recipes_btns = ttk.Frame(tab_recipes)
        tab_recipes_btns.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ttk.Button(tab_recipes_btns, text="Add From Selection", command=self.add_from_selection).pack(fill="x")

        # Tab layout weights
        tab_menu.grid_columnconfigure(0, weight=1)
        tab_recipes.grid_rowconfigure(1, weight=1)
        tab_recipes.grid_columnconfigure(0, weight=1)

        # Interactions
        tuv.bind("<Double-1>", self._open_recipe_html)

        # Context menu for menu table
        m_menu = tk.Menu(self, tearoff=0)
        m_menu.add_command(label="Edit", command=self.edit_selected)
        m_menu.add_command(label="Delete", command=self.delete_selected)

        def popm(e):
            try:
                m_menu.tk_popup(e.x_root, e.y_root)
            finally:
                m_menu.grab_release()

        tvm.bind("<Button-3>", popm)
        tvm.bind("<Double-1>", lambda _e: self.edit_selected())

        # Ensure we recompute fit once data is loaded; done async so geometry settles
        self.refresh_recipes()
        self.refresh_menu()
        self.bind("<Visibility>", lambda _e: self._schedule_fit_check())
        self._schedule_fit_check()

    # ---------- Data ----------
    def refresh_recipes(self) -> None:
        tv = self._tree_rec
        if not isinstance(tv, ttk.Treeview):
            return
        for it in tv.get_children():
            tv.delete(it)
        rows = self.db.execute(
            """
            SELECT id, title, source,
                   COALESCE(prep_time,'') AS prep_time,
                   COALESCE(cook_time,'') AS cook_time,
                   COALESCE(servings,0)   AS servings
              FROM recipes
             ORDER BY LOWER(title)
            """
        ).fetchall()
        for r in rows:
            tv.insert(
                "",
                "end",
                iid=f"rec::{r['id']}",
                values=[
                    r["title"] or "",
                    r["source"] or "",
                    r["prep_time"] or "",
                    r["cook_time"] or "",
                    r["servings"] or 0,
                ],
            )
        self._schedule_fit_check()

    def refresh_menu(self) -> None:
        tv = self._tree_menu
        if not isinstance(tv, ttk.Treeview):
            return
        for it in tv.get_children():
            tv.delete(it)
        rows = self.db.execute(
            """
            SELECT mp.id, mp.date, mp.meal, mp.title,
                   COALESCE(r.prep_time,'') AS prep_time,
                   COALESCE(r.cook_time,'') AS cook_time,
                   COALESCE(r.servings,0)   AS servings,
                   mp.notes
              FROM menu_plan mp
              LEFT JOIN recipes r ON r.id = mp.recipe_id
             ORDER BY mp.date ASC, mp.meal ASC, LOWER(mp.title)
            """
        ).fetchall()
        for r in rows:
            tv.insert(
                "",
                "end",
                iid=str(r["id"]),
                values=[
                    r["date"] or "",
                    r["meal"] or "",
                    r["title"] or "",
                    r["prep_time"] or "",
                    r["cook_time"] or "",
                    r["servings"] or 0,
                    r["notes"] or "",
                ],
            )
        self._schedule_fit_check()
    # ---------- Helpers (DB) ----------
    def _row_to_dict(self, cursor, row):
        """Convert a sqlite row to dict using cursor.description; robust to default row_factory.
        Only comment on the why: avoid depending on connection row_factory.
        """
        if row is None:
            return {}
        try:
            keys = [d[0] for d in cursor.description]
            return {k: row[i] for i, k in enumerate(keys)}
        except Exception:
            try:
                return dict(row)
            except Exception:
                fields = [
                    "id",
                    "title",
                    "source",
                    "ingredients",
                    "instructions",
                    "prep_time",
                    "cook_time",
                    "servings",
                    "notes",
                ]
                return {f: getattr(row, f, "" if f != "servings" else 0) for f in fields}

    def _fetch_recipe_as_dict(self, rid: int):
        """Fetch recipe by id, tolerating schema drift (missing optional columns).
        Avoids OperationalError by introspecting columns and selecting only those available.
        """
        cur = self.db.cursor()
        try:
            info = cur.execute("PRAGMA table_info(recipes)").fetchall()
            names = set()
            for ci in info or []:
                try:
                    # sqlite3.Row or tuple
                    name = ci["name"] if isinstance(ci, dict) else ci[1]
                except Exception:
                    name = getattr(ci, "name", None) or (ci[1] if isinstance(ci, (list, tuple)) and len(ci) > 1 else None)
                if name:
                    names.add(name)
        except Exception:
            names = set()

        select = ["id", "title", "source", "ingredients", "instructions"]
        if "prep_time" in names:
            select.append("COALESCE(prep_time,'') AS prep_time")
        if "cook_time" in names:
            select.append("COALESCE(cook_time,'') AS cook_time")
        if "servings" in names:
            select.append("COALESCE(servings,0) AS servings")
        if "notes" in names:
            select.append("COALESCE(notes,'') AS notes")

        q = f"SELECT {', '.join(select)} FROM recipes WHERE id = ?"
        cur.execute(q, (rid,))
        row = cur.fetchone()
        if not row:
            return None
        rec = self._row_to_dict(cur, row)
        # fill defaults if some optional columns are absent
        rec.setdefault("prep_time", "")
        rec.setdefault("cook_time", "")
        rec.setdefault("servings", 0)
        rec.setdefault("notes", "")
        return rec

    # ---------- Actions ----------
    def add_from_selection(self) -> None:
        tvr = self._tree_rec
        if not isinstance(tvr, ttk.Treeview):
            return
        sel = [i for i in tvr.selection() if i.startswith("rec::")]
        if not sel:
            messagebox.showinfo("Menu", "Select recipe(s) in the Recipes tab.", parent=self.winfo_toplevel())
            return

        # Calendar picker → ISO date
        date = self._open_date_picker(self.winfo_toplevel())
        if not date:
            return

        meal = simpledialog.askstring(
            "Menu Planner", "Meal:", initialvalue="Dinner", parent=self.winfo_toplevel()
        ) or "Dinner"

        cur = self.db.cursor()
        for iid in sel:
            rid = int(iid.split("::", 1)[1])
            r = cur.execute("SELECT title FROM recipes WHERE id=?", (rid,)).fetchone()
            if r:
                cur.execute(
                    "INSERT INTO menu_plan(date, meal, recipe_id, title, notes) VALUES(?,?,?,?,?)",
                    (date.strip(), meal.strip(), rid, r["title"], ""),
                )
        self.db.commit()
        self.refresh_menu()
        self.set_status(f"Added {len(sel)} item(s) to Menu")

    def edit_selected(self) -> None:
        tv = self._tree_menu
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        if len(sel) != 1:
            messagebox.showinfo("Menu", "Select one row to edit.", parent=self.winfo_toplevel())
            return
        rid = int(sel[0])
        r = self.db.execute("SELECT date, meal, title, notes FROM menu_plan WHERE id=?", (rid,)).fetchone()
        if not r:
            return

        dlg = tk.Toplevel(self)
        dlg.title("Edit Menu Item")
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()

        frm = ttk.Frame(dlg, padding=8)
        frm.grid(row=0, column=0, sticky="nsew")
        frm.grid_columnconfigure(1, weight=1)

        v_date = tk.StringVar(value=(r["date"] or ""))
        v_meal = tk.StringVar(value=(r["meal"] or "Dinner"))
        v_title = tk.StringVar(value=(r["title"] or ""))
        v_notes = tk.StringVar(value=(r["notes"] or ""))

        def row(lbl: str, w: tk.Widget, i: int) -> None:
            ttk.Label(frm, text=lbl).grid(row=i, column=0, sticky="w", padx=(0, 8), pady=4)
            w.grid(row=i, column=1, sticky="ew", pady=4)

        # Date row: Entry + calendar button
        f_date = ttk.Frame(frm)
        e_date = ttk.Entry(f_date, textvariable=v_date, width=12)
        e_date.pack(side="left")
        ttk.Button(
            f_date,
            text="📅",
            width=3,
            command=lambda: (lambda picked=self._open_date_picker(dlg, v_date.get()): v_date.set(picked or v_date.get()))(),
            takefocus=False,
        ).pack(side="left", padx=(6, 0))
        row("Date", f_date, 0)

        row("Meal", ttk.Combobox(frm, textvariable=v_meal, values=MEALS, state="readonly", width=12), 1)
        row("Title", ttk.Entry(frm, textvariable=v_title, width=36), 2)
        row("Notes", ttk.Entry(frm, textvariable=v_notes, width=48), 3)
        frm.grid_columnconfigure(1, weight=1)

        out: dict = {}

        def save() -> None:
            out.update(
                {
                    "date": v_date.get().strip(),
                    "meal": v_meal.get().strip(),
                    "title": v_title.get().strip(),
                    "notes": v_notes.get().strip(),
                }
            )
            dlg.destroy()

        bt = ttk.Frame(dlg, padding=(8, 6))
        bt.grid(row=1, column=0, sticky="e")
        ttk.Button(bt, text="Cancel", command=dlg.destroy).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(bt, text="Save", command=save).grid(row=0, column=1)
        dlg.wait_window()
        if not out:
            return

        self.db.execute(
            "UPDATE menu_plan SET date=?, meal=?, title=?, notes=? WHERE id=?",
            (out["date"], out["meal"], out["title"], out["notes"], rid),
        )
        self.db.commit()
        self.refresh_menu()

    def delete_selected(self) -> None:
        tv = self._tree_menu
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        if not sel:
            messagebox.showinfo("Menu", "Select at least one row to delete.", parent=self.winfo_toplevel())
            return
        if not self.confirm_delete(len(sel)):
            return
        ids = [int(i) for i in sel]
        q = ",".join("?" for _ in ids)
        self.db.execute(f"DELETE FROM menu_plan WHERE id IN ({q})", ids)
        self.db.commit()
        self.refresh_menu()

    def export_html_menu(self) -> None:
        tv = self._tree_menu
        if not isinstance(tv, ttk.Treeview):
            return
        items = tv.get_children("")
        rows = [list(tv.item(i, "values")) for i in items]
        headings = [hdr for _k, hdr, _w, _a in MENU_COLS]
        export_table_html(
            path=None,
            title="Menu Plan",
            columns=headings,
            rows=rows,
            subtitle="Generated from Celiogix",
            meta={"Source": "Menu", "Rows": len(rows)},
            open_after=True,
        )

    def _find_cookbook_panel(self):
        # Directly access the cookbook_panel attribute from the app
        return getattr(self.app, "cookbook_panel", None)

    def _open_recipe_html(self, event: tk.Event) -> None:
        tv = self._tree_rec
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        if len(sel) != 1:
            messagebox.showinfo("Recipes", "Select one recipe to print.", parent=self.winfo_toplevel())
            return
        iid = sel[0]
        if not iid.startswith("rec::"):
            return
        rid = int(iid.split("::", 1)[1])

        # Prefer pulling the recipe from the cookbook panel if available
        cookbook_panel = self._find_cookbook_panel()
        recipe = None
        if cookbook_panel is not None:
            get_fn = getattr(cookbook_panel, "get_recipe_by_id", None)
            if callable(get_fn):
                try:
                    recipe = get_fn(rid)
                except Exception:
                    recipe = None

        # Fallback: query DB directly if we couldn't get it from the panel
        if recipe is None:
            try:
                recipe = self._fetch_recipe_as_dict(rid)
            except Exception:
                recipe = None
            if not recipe:
                messagebox.showerror("Error", "Recipe not found.", parent=self.winfo_toplevel())
                return

        # Normalize to dict for export
        if isinstance(recipe, dict):
            recipe_dict = recipe
        else:
            try:
                recipe_dict = dict(recipe)
            except Exception:
                # last-resort coercion from attributes
                recipe_dict = {
                    "id": getattr(recipe, "id", rid),
                    "title": getattr(recipe, "title", "Recipe"),
                    "source": getattr(recipe, "source", ""),
                    "ingredients": getattr(recipe, "ingredients", ""),
                    "instructions": getattr(recipe, "instructions", ""),
                    "prep_time": getattr(recipe, "prep_time", ""),
                    "cook_time": getattr(recipe, "cook_time", ""),
                    "servings": getattr(recipe, "servings", 0),
                    "notes": getattr(recipe, "notes", ""),
                }
        export_recipes_html(
            recipes=[recipe_dict],
            title=recipe_dict.get("title", "Recipe"),
            subtitle="Ready for printing",
            open_after=True,
        )

    # ---------- Scroll persistence ----------
    def _save_scroll(self) -> None:
        """Persist horizontal scroll position into app._ui_state."""
        try:
            sc = self._scroller
            if not sc:
                return
            first, _last = sc.canvas.xview()
            state = getattr(self.app, "_ui_state", None)
            if not isinstance(state, dict):
                state = {}
                setattr(self.app, "_ui_state", state)
            state["menu.scroll_x"] = float(first)
        except Exception:
            pass

    def _restore_scroll(self) -> None:
        try:
            sc = self._scroller
            if not sc:
                return
            state = getattr(self.app, "_ui_state", {})
            pos = float(state.get("menu.scroll_x", 0.0) or 0.0)
            sc.canvas.xview_moveto(pos)
        except Exception:
            pass

    def on_show(self) -> None:
        # when panel becomes visible, restore position and re-evaluate scrollbars
        self.after(0, self._restore_scroll)
        self.after(0, self._update_scrollbars)
        self._schedule_fit_check()

    def _update_scrollbars(self) -> None:
        """Auto-hide outer H-bar if content fits; show per-tree H-bars as fallback.
        Also wires hotkeys for horizontal navigation."""
        sc = self._scroller
        if not sc:
            return
        try:
            # compare content requested width vs visible canvas width
            sc.content.update_idletasks()
            content_w = sc.content.winfo_reqwidth()
            canvas_w = sc.canvas.winfo_width()
            outer_needed = content_w > (canvas_w + 1)

            # Toggle per-tree H-bars
            for tv, hsb in ((self._tree_menu, self._menu_hsb), (self._tree_rec, self._rec_hsb)):
                if not (isinstance(tv, ttk.Treeview) and isinstance(hsb, ttk.Scrollbar)):
                    continue
                if outer_needed:
                    # hide per-tree bars to avoid double H-bars
                    try:
                        hsb.grid_remove()
                        tv.configure(xscrollcommand="")  # detach; outer handles pan
                    except Exception:
                        pass
                else:
                    # show per-tree bars for each tree if outer isn't needed
                    try:
                        tv.configure(xscrollcommand=hsb.set)
                        hsb.grid()
                    except Exception:
                        pass

            # Show/hide outer H-bar
            sc.set_hbar_visible(outer_needed)

            # keybindings for horizontal nav
            self.bind_all("<Shift-MouseWheel>", lambda e: self._nudge_scroll(-0.08 if e.delta > 0 else +0.08))
            self.bind_all("<Control-MouseWheel>", lambda e: self._nudge_scroll(-0.08 if e.delta > 0 else +0.08))
            self.bind_all("<Shift-Left>", lambda _e: self._nudge_scroll(-0.08))
            self.bind_all("<Shift-Right>", lambda _e: self._nudge_scroll(+0.08))
            self.bind_all("<Home>", lambda _e: self._scroll_to(0.0))
            self.bind_all("<End>", lambda _e: self._scroll_to(1.0))
            self.bind_all("<Shift-Prior>", lambda _e: self._nudge_scroll(-0.25))  # PageUp
            self.bind_all("<Shift-Next>", lambda _e: self._nudge_scroll(+0.25))  # PageDown
        except Exception:
            pass

    def _nudge_scroll(self, frac_delta: float) -> None:
        sc = self._scroller
        if not sc:
            return
        first, _last = sc.canvas.xview()
        new_first = max(0.0, min(1.0, first + frac_delta))
        sc.canvas.xview_moveto(new_first)
        self._save_scroll()

    def _scroll_to(self, pos: float) -> None:
        sc = self._scroller
        if not sc:
            return
        sc.canvas.xview_moveto(max(0.0, min(1.0, pos)))
        self._save_scroll()

    # ---------- sizing helpers ----------
    def _schedule_fit_check(self, delay: int = 120, retries: int = 3) -> None:
        """Throttle geometry checks so panel opens wide enough for its content."""
        try:
            job = self._fit_job
            if job:
                self.after_cancel(job)
        except Exception:
            pass

        def _runner() -> None:
            self._fit_job = None
            self._ensure_window_width(retries=retries)

        self._fit_job = self.after(delay, _runner)

    def _ensure_window_width(self, retries: int = 3) -> None:
        sc = self._scroller
        if sc is None:
            return
        top = self.winfo_toplevel()
        if not isinstance(top, tk.Misc):
            return
        try:
            sc.update_idletasks()
            sc.content.update_idletasks()
            top.update_idletasks()

            window_width = top.winfo_width()
            scroller_width = max(sc.winfo_width(), sc.winfo_reqwidth())
            content_width = sc.content.winfo_reqwidth()

            if (window_width <= 1 or scroller_width <= 1 or content_width <= 1) and retries > 0:
                self._schedule_fit_check(delay=160, retries=retries - 1)
                return

            extra = max(0, window_width - scroller_width)
            target_width = int(content_width + extra)

            if target_width > window_width:
                current_height = top.winfo_height()
                if current_height <= 1:
                    current_height = max(top.winfo_reqheight(), 1)
                top.geometry(f"{target_width}x{current_height}")
                top.update_idletasks()
                self.after(0, self._update_scrollbars)
        except Exception:
            if retries > 0:
                self._schedule_fit_check(delay=200, retries=retries - 1)
