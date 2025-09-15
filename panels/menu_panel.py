# path: panels/menu_panel.py
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, List, Tuple
import datetime, calendar

from panels.base_panel import BasePanel
from utils.export import export_table_html, export_recipes_html

# ------------------------- Tiny modal date picker -------------------------
class _DatePickerDialog(tk.Toplevel):
    """Modal mini-calendar that returns ISO date (YYYY-MM-DD) via .result."""
    def __init__(self, parent: tk.Misc, initial: Optional[datetime.date] = None, title="Choose Date"):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        self.result: Optional[str] = None

        today = datetime.date.today()
        d0 = initial or today
        self._y, self._m = d0.year, d0.month

        outer = ttk.Frame(self, padding=8)
        outer.grid(row=0, column=0, sticky="nsew")

        # Header: prev / month label / next / Today
        hdr = ttk.Frame(outer)
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 6))
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
        self.bind("<Escape>", lambda e: self._cancel())

    def _shift(self, delta_months: int):
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

    def _rebuild(self):
        self._label.config(text=f"{datetime.date(self._y, self._m, 1):%B %Y}")
        # Clear old day buttons (rows > 0)
        for w in list(self._grid.grid_slaves()):
            if w.grid_info().get("row", 0) != 0:
                w.destroy()
        cal = calendar.Calendar()
        weeks = cal.monthdatescalendar(self._y, self._m)
        for r, week in enumerate(weeks, start=1):
            for c, d in enumerate(week):
                is_this_month = (d.month == self._m)
                btn = ttk.Button(self._grid, text=str(d.day), width=4, command=(lambda dd=d: self._choose(dd)))
                btn.state(["!disabled"] if is_this_month else ["disabled"])
                btn.grid(row=r, column=c, padx=1, pady=1)

    def _choose(self, d: datetime.date):
        self.result = d.isoformat()
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


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

# Recipe library (picker) inside Menu tab
REC_COLS: List[Tuple[str, str, int, str]] = [
    ("title", "Title", 280, "w"),
    ("source", "Source", 140, "w"),
    ("prep_time", "Prep", 80, "c"),
    ("cook_time", "Cook", 80, "c"),
    ("servings", "Servings", 80, "c"),
]

MEALS = ["Breakfast", "Lunch", "Dinner", "Snack", "Other"]


class MenuPanel(BasePanel):
    """Simple planner: left = planned menu; right = recipe library with new time/servings columns."""
    def __init__(self, master, app, **kw):
        self._tree_menu: Optional[ttk.Treeview] = None
        self._tree_rec: Optional[ttk.Treeview] = None
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

    # ---------- UI ----------
    def build(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Left: planned menu
        left = ttk.Frame(self, padding=6)
        left.grid(row=0, column=0, sticky="ns")
        ttk.Label(left, text="Menu").pack(anchor="w")
        wrap_m = ttk.Frame(left)
        wrap_m.pack(fill="both", expand=True)
        tvm = ttk.Treeview(
            wrap_m, columns=[c[0] for c in MENU_COLS], show="headings", height=16, selectmode="extended"
        )
        for k, h, w, a in MENU_COLS:
            tvm.heading(k, text=h)
            anc = {"w": "w", "c": "center", "e": "e"}.get(a, "w")
            tvm.column(k, width=w, anchor=anc, stretch=True)
        tvm.pack(fill="both", expand=True)
        self._tree_menu = tvm

        btns = ttk.Frame(left)
        btns.pack(fill="x", pady=(6, 0))
        ttk.Button(btns, text="Add From Selection", command=self.add_from_selection).pack(fill="x")
        ttk.Button(btns, text="Edit", command=self.edit_selected).pack(fill="x", pady=(4, 0))
        ttk.Button(btns, text="Delete", command=self.delete_selected).pack(fill="x")
        ttk.Button(btns, text="Export HTML", command=self.export_html_menu).pack(fill="x", pady=(6, 0))

        # Right: recipe library (for picking)
        right = ttk.Frame(self, padding=6)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)
        ttk.Label(right, text="Recipes").grid(row=0, column=0, sticky="w")
        tuv = ttk.Treeview(right, columns=[c[0] for c in REC_COLS], show="headings", selectmode="extended")
        for k, h, w, a in REC_COLS:
            tuv.heading(k, text=h)
            anc = {"w": "w", "c": "center", "e": "e"}.get(a, "w")
            tuv.column(k, width=w, anchor=anc, stretch=True)
        tuv.grid(row=1, column=0, sticky="nsew")
        self._tree_rec = tuv

        vsb = ttk.Scrollbar(right, orient="vertical", command=tuv.yview)
        tuv.configure(yscroll=vsb.set)
        vsb.grid(row=1, column=1, sticky="ns")

        # Add double-click event to recipe treeview
        tuv.bind("<Double-1>", self._open_recipe_html)

        # Menus
        m_menu = tk.Menu(self, tearoff=0)
        m_menu.add_command(label="Edit", command=self.edit_selected)
        m_menu.add_command(label="Delete", command=self.delete_selected)

        def popm(e):
            try:
                m_menu.tk_popup(e.x_root, e.y_root)
            finally:
                m_menu.grab_release()

        tvm.bind("<Button-3>", popm)
        tvm.bind("<Double-1>", lambda e: self.edit_selected())

        self.refresh_recipes()
        self.refresh_menu()

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
                values=[r["title"] or "", r["source"] or "", r["prep_time"] or "", r["cook_time"] or "", r["servings"] or 0],
            )

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

    # ---------- Actions ----------
    def add_from_selection(self) -> None:
        tvr = self._tree_rec
        if not isinstance(tvr, ttk.Treeview):
            return
        sel = [i for i in tvr.selection() if i.startswith("rec::")]
        if not sel:
            messagebox.showinfo("Menu", "Select recipe(s) on the right.", parent=self.winfo_toplevel())
            return

        # Replaces the free-text prompt with a calendar picker (returns ISO date)
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

        v_date = tk.StringVar(value=r["date"] or "")
        v_meal = tk.StringVar(value=r["meal"] or "Dinner")
        v_title = tk.StringVar(value=r["title"] or "")
        v_notes = tk.StringVar(value=r["notes"] or "")

        def row(label, w, rowi):
            ttk.Label(frm, text=label).grid(row=rowi, column=0, sticky="e", padx=(0, 8), pady=(0, 4))
            w.grid(row=rowi, column=1, sticky="ew", pady=(0, 4))

        # Date row: Entry + 📅 button
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

        out = {}

        def save():
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
            subtitle="Generated from Celiac Culinary",
            meta={"Source": "Menu", "Rows": len(rows)},
            open_after=True,
        )

    def _find_cookbook_panel(self):
        # Directly access the cookbook_panel attribute from the app
        return getattr(self.app, "cookbook_panel", None)

    def _open_recipe_html(self, event: tk.Event) -> None:
        tvr = self._tree_rec
        if not isinstance(tvr, ttk.Treeview):
            return
        sel = tvr.selection()
        if len(sel) != 1:
            self.show_info("Menu", "Select one recipe to print.")
            return

        iid = sel[0]
        if not iid.startswith("rec::"):
            return

        rid = int(iid.split("::", 1)[1])
        # Fetch full recipe data from the database
        recipe = self.db.execute(
            """
            SELECT title, source, prep_time, cook_time, servings, ingredients, instructions, url, tags, rating
            FROM recipes
            WHERE id=?
            """,
            (rid,)
        ).fetchone()
        if not recipe:
            self.show_error("Error", "Recipe not found.")
            return

        # Convert sqlite3.Row to dict for export
        recipe_dict = dict(recipe)
        export_recipes_html(
            recipes=[recipe_dict],
            title=recipe_dict.get("title", "Recipe"),
            subtitle="Ready for printing",
            open_after=True
        )
