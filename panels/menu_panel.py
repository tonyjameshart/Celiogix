# path: panels/menu_panel.py
from __future__ import annotations

import calendar as _cal
import datetime as _dt
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

from panels.base_panel import BasePanel

MENU_COLS = [
    ("date", "Date", 110, "c"),
    ("meal", "Meal", 110, "w"),
    ("title", "Recipe", 320, "w"),
    ("prep_time", "Prep", 80, "c"),
    ("cook_time", "Cook", 80, "c"),
    ("servings", "Servings", 80, "c"),
    ("notes", "Notes", 260, "w"),
]


class MenuPanel(BasePanel):
    def __init__(self, master, app, **kw):
        self._tree_menu: ttk.Treeview | None = None
        self._tree_rec: ttk.Treeview | None = None
        super().__init__(master, app, **kw)

    # ---------- UI ----------
    def build(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        nb = ttk.Notebook(self)
        nb.grid(row=0, column=0, sticky="nsew")

        # ========== Menu tab ==========
        t1 = ttk.Frame(nb, padding=6)
        nb.add(t1, text="Menu")
        t1.grid_rowconfigure(1, weight=1)
        t1.grid_columnconfigure(0, weight=1)

        bar = ttk.Frame(t1)
        bar.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        ttk.Button(bar, text="Add", command=self.add_menu_item).pack(side="left")
        ttk.Button(bar, text="Edit", command=self.edit_selected).pack(side="left", padx=(6, 0))
        ttk.Button(bar, text="Delete", command=self.delete_selected).pack(side="left", padx=(6, 0))
        ttk.Button(
            bar,
            text="Fit Columns",
            command=lambda: self.fit_columns_now(self._tree_menu, exact=True, max_px_map={"notes": 1200}),
        ).pack(side="left", padx=(12, 0))
        ttk.Button(bar, text="Export visible", command=self.export_html_menu).pack(side="left", padx=(6, 0))

        wrap_m, tvm, vsbm, hsbm = self.make_scrolling_tree(t1, [c[0] for c in MENU_COLS])
        for key, hdr, width, align in MENU_COLS:
            tvm.heading(key, text=hdr)
            tvm.column(key, width=width, anchor={"w": "w", "e": "e", "c": "center"}.get(align, "w"), stretch=False)
        wrap_m.grid(row=1, column=0, sticky="nsew")
        self._tree_menu = tvm

        tvm.bind("<Double-1>", lambda _e: self.edit_selected())
        m_menu = tk.Menu(self, tearoff=0)
        m_menu.add_command(label="Add", command=self.add_menu_item)
        m_menu.add_command(label="Edit", command=self.edit_selected)
        m_menu.add_command(label="Duplicate", command=self.duplicate_selected)
        m_menu.add_separator()
        m_menu.add_command(label="Delete", command=self.delete_selected)
        m_menu.add_separator()
        m_menu.add_command(
            label="Fit Columns", command=lambda: self.fit_columns_now(self._tree_menu, exact=True, max_px_map={"notes": 1200})
        )
        m_menu.add_command(label="Export visible", command=self.export_html_menu)
        tvm.bind("<Button-3>", lambda e, mm=m_menu: self._popup_menu(e, mm))

        # ========== Recipes tab ==========
        REC_COLS = [
            ("title", "Title", 300, "w"),
            ("source", "Source", 140, "w"),
            ("prep_time", "Prep", 80, "c"),
            ("cook_time", "Cook", 80, "c"),
            ("servings", "Servings", 80, "c"),
        ]
        t2 = ttk.Frame(nb, padding=6)
        nb.add(t2, text="Recipes")
        t2.grid_rowconfigure(1, weight=1)
        t2.grid_columnconfigure(0, weight=1)

        bar2 = ttk.Frame(t2)
        bar2.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        ttk.Button(bar2, text="Add to Menu", command=self.add_recipe_row_to_menu).pack(side="left")
        ttk.Button(bar2, text="Fit Columns", command=lambda: self.fit_columns_now(self._tree_rec, exact=True)).pack(
            side="left", padx=(12, 0)
        )

        wrap_r, tvr, vsbr, hsbr = self.make_scrolling_tree(t2, [c[0] for c in REC_COLS])
        for key, hdr, width, align in REC_COLS:
            tvr.heading(key, text=hdr)
            tvr.column(key, width=width, anchor={"w": "w", "e": "e", "c": "center"}.get(align, "w"), stretch=False)
        wrap_r.grid(row=1, column=0, sticky="nsew")
        self._tree_rec = tvr

        tvr.bind("<Double-1>", lambda _e: self.add_recipe_row_to_menu())
        m_rec = tk.Menu(self, tearoff=0)
        m_rec.add_command(label="Add to Menu", command=self.add_recipe_row_to_menu)
        m_rec.add_separator()
        m_rec.add_command(label="Fit Columns", command=lambda: self.fit_columns_now(self._tree_rec, exact=True))
        tvr.bind("<Button-3>", lambda e, mm=m_rec: self._popup_menu(e, mm))

        # initial data
        self.refresh_recipes()
        self.refresh_menu()
        self.after(0, lambda: self.fit_columns_now(tvm, exact=True, max_px_map={"notes": 1200}))
        self.after(0, lambda: self.fit_columns_now(tvr, exact=True))

    # ---------- Tab lifecycle ----------
    def on_tab_activated(self) -> None:
        self.refresh_recipes()
        self.refresh_menu()

    # ---------- Helpers ----------
    def _popup_menu(self, ev: tk.Event, menu: tk.Menu) -> None:
        try:
            menu.tk_popup(ev.x_root, ev.y_root)
        finally:
            menu.grab_release()

    def _all_recipes(self) -> list[sqlite3.Row]:
        return self.db.execute(
            """
            SELECT id, title, source,
                   COALESCE(prep_time,'') AS prep_time,
                   COALESCE(cook_time,'') AS cook_time,
                   COALESCE(servings,0)   AS servings
              FROM recipes
             ORDER BY LOWER(title)
            """
        ).fetchall()

    def _notify_menu_changed(self) -> None:
        # Refresh Calendar tab if present
        cal = getattr(self.app, "calendar_panel", None)
        for meth in ("refresh", "reload", "refresh_view", "refresh_month"):
            if cal is not None and hasattr(cal, meth):
                try:
                    getattr(cal, meth)()
                except Exception:
                    pass
                break

    # ---------- Date picker ----------
    def _pick_date(self, initial: str | None = None) -> str | None:
        """Small month calendar. Returns YYYY-MM-DD or None."""
        today = _dt.date.today()
        if initial:
            try:
                d0 = _dt.date.fromisoformat(initial)
            except Exception:
                d0 = today
        else:
            d0 = today

        year = d0.year
        month = d0.month
        selected: dict[str, str | None] = {"val": None}

        dlg = tk.Toplevel(self)
        dlg.title("Pick date")
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()
        dlg.resizable(False, False)

        frm = ttk.Frame(dlg, padding=8)
        frm.grid(row=0, column=0)

        hdr = ttk.Frame(frm)
        hdr.grid(row=0, column=0, columnspan=7, pady=(0, 6), sticky="ew")

        lbl_mon = ttk.Label(hdr, text="")
        def set_header():
            lbl_mon.config(text=f"{_cal.month_name[month]} {year}")
        ttk.Button(hdr, text="?", width=3, command=lambda: nav(-1)).pack(side="left")
        lbl_mon.pack(side="left", expand=True)
        ttk.Button(hdr, text="?", width=3, command=lambda: nav(1)).pack(side="right")

        grid = ttk.Frame(frm)
        grid.grid(row=1, column=0)

        for i, wd in enumerate(["Mo","Tu","We","Th","Fr","Sa","Su"]):
            ttk.Label(grid, text=wd, width=3, anchor="center").grid(row=0, column=i, padx=1, pady=1)

        def build():
            # clear old
            for w in list(grid.grid_slaves()):
                info = w.grid_info()
                if int(info.get("row", 0)) >= 1:
                    w.destroy()
            cal = _cal.Calendar(firstweekday=0)  # Monday first to match headers
            r = 1
            for week in cal.monthdayscalendar(year, month):
                for c, day in enumerate(week):
                    if day == 0:
                        ttk.Label(grid, text=" ", width=3).grid(row=r, column=c, padx=1, pady=1)
                    else:
                        dstr = f"{year:04d}-{month:02d}-{day:02d}"
                        btn = ttk.Button(
                            grid,
                            text=str(day),
                            width=3,
                            command=lambda ds=dstr: (selected.__setitem__("val", ds), dlg.destroy()),
                        )
                        if dstr == today.isoformat():
                            btn.state(["!disabled", "focus"])
                        btn.grid(row=r, column=c, padx=1, pady=1)
                r += 1

        def nav(delta_months: int) -> None:
            nonlocal year, month
            m = month + delta_months
            y = year
            while m < 1:
                m += 12
                y -= 1
            while m > 12:
                m -= 12
                y += 1
            year, month = y, m
            set_header()
            build()

        set_header()
        build()

        btns = ttk.Frame(frm)
        btns.grid(row=2, column=0, pady=(6, 0), sticky="e")
        ttk.Button(btns, text="Today", command=lambda: (selected.__setitem__("val", today.isoformat()), dlg.destroy())).grid(row=0, column=0, padx=(0,6))
        ttk.Button(btns, text="Cancel", command=dlg.destroy).grid(row=0, column=1)

        dlg.wait_window()
        return selected["val"]

    # ---------- Data loading ----------
    def refresh_recipes(self) -> None:
        tv = self._tree_rec
        if not isinstance(tv, ttk.Treeview):
            return
        for it in tv.get_children():
            tv.delete(it)
        for r in self._all_recipes():
            tv.insert(
                "",
                "end",
                iid=f"rec::{r['id']}",
                values=[r["title"] or "", r["source"] or "", r["prep_time"] or "", r["cook_time"] or "", r["servings"] or 0],
            )
        self.fit_columns_now(tv, exact=True)

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
                   COALESCE(mp.notes,'')    AS notes
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
        self.fit_columns_now(tv, exact=True, max_px_map={"notes": 1200})

    # ---------- Actions ----------
    def add_recipe_row_to_menu(self) -> None:
        tv = self._tree_rec
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        if len(sel) != 1:
            messagebox.showinfo("Menu", "Select one recipe to add.", parent=self.winfo_toplevel())
            return
        iid = sel[0]
        if not str(iid).startswith("rec::"):
            return
        rid = int(str(iid).split("::", 1)[1])
        r = self.db.execute("SELECT id, title FROM recipes WHERE id=?", (rid,)).fetchone()
        if not r:
            return
        d = self._pick_date()
        if not d:
            return
        meal = "Dinner"
        self.db.execute(
            "INSERT INTO menu_plan(date, meal, recipe_id, title, notes) VALUES(?,?,?,?,?)",
            (d, meal, rid, r["title"], ""),
        )
        self.db.commit()
        self.refresh_menu()
        self._notify_menu_changed()

    def add_menu_item(self) -> None:
        self._menu_dialog(row=None)

    def edit_selected(self) -> None:
        tv = self._tree_menu
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        if len(sel) != 1:
            messagebox.showinfo("Menu", "Select one row to edit.", parent=self.winfo_toplevel())
            return
        mid = int(sel[0])
        row = self.db.execute(
            "SELECT id, date, meal, recipe_id, title, COALESCE(notes,'') AS notes FROM menu_plan WHERE id=?", (mid,)
        ).fetchone()
        if not row:
            return
        self._menu_dialog(row=row)

    def duplicate_selected(self) -> None:
        tv = self._tree_menu
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        if len(sel) != 1:
            return
        mid = int(sel[0])
        r = self.db.execute(
            "SELECT date, meal, recipe_id, title, COALESCE(notes,'') AS notes FROM menu_plan WHERE id=?", (mid,)
        ).fetchone()
        if not r:
            return
        self.db.execute(
            "INSERT INTO menu_plan(date, meal, recipe_id, title, notes) VALUES(?,?,?,?,?)",
            (r["date"], r["meal"], r["recipe_id"], r["title"], r["notes"]),
        )
        self.db.commit()
        self.refresh_menu()
        self._notify_menu_changed()

    # ---------- Dialog ----------
    def _menu_dialog(self, row: sqlite3.Row | None) -> None:
        dlg = tk.Toplevel(self)
        dlg.title("Menu item")
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()
        dlg.resizable(False, False)

        frm = ttk.Frame(dlg, padding=8)
        frm.grid(row=0, column=0, sticky="nsew")
        frm.grid_columnconfigure(1, weight=1)

        v_date = tk.StringVar(value=(row["date"] if row else _dt.date.today().isoformat()))
        v_meal = tk.StringVar(value=(row["meal"] if row else "Dinner"))
        v_notes = tk.StringVar(value=(row["notes"] if row else ""))

        recipes = self._all_recipes()
        titles = [r["title"] for r in recipes]
        id_by_title = {r["title"]: r["id"] for r in recipes}
        if row and row["recipe_id"]:
            cur_title = self.db.execute("SELECT title FROM recipes WHERE id=?", (row["recipe_id"],)).fetchone()
            cur_title = cur_title["title"] if cur_title else (row["title"] or "")
        else:
            cur_title = row["title"] if row else ""
        v_title = tk.StringVar(value=cur_title)

        ttk.Label(frm, text="Date").grid(row=0, column=0, sticky="e", padx=(0, 8), pady=(0, 4))
        date_line = ttk.Frame(frm)
        date_line.grid(row=0, column=1, sticky="w")
        e_date = ttk.Entry(date_line, textvariable=v_date, width=14)
        e_date.pack(side="left")
        ttk.Button(date_line, text="??", width=3, command=lambda: self._set_date_from_picker(v_date.get(), v_date)).pack(side="left", padx=(6,0))

        ttk.Label(frm, text="Meal").grid(row=1, column=0, sticky="e", padx=(0, 8), pady=(0, 4))
        cb_meal = ttk.Combobox(frm, values=["Breakfast", "Lunch", "Dinner", "Snack", "Other"], textvariable=v_meal, width=14, state="readonly")
        cb_meal.grid(row=1, column=1, sticky="w", pady=(0, 4))

        ttk.Label(frm, text="Recipe").grid(row=2, column=0, sticky="e", padx=(0, 8), pady=(0, 4))
        cb_title = ttk.Combobox(frm, values=titles, textvariable=v_title, width=40)
        cb_title.grid(row=2, column=1, sticky="ew", pady=(0, 4))

        ttk.Label(frm, text="Notes").grid(row=3, column=0, sticky="e", padx=(0, 8), pady=(0, 4))
        e_notes = ttk.Entry(frm, textvariable=v_notes)
        e_notes.grid(row=3, column=1, sticky="ew", pady=(0, 4))

        err = ttk.Label(frm, text="", foreground="red")
        err.grid(row=4, column=1, sticky="w")

        def save():
            d = v_date.get().strip()
            try:
                _dt.date.fromisoformat(d)
            except Exception:
                err.configure(text="Use YYYY-MM-DD")
                return
            meal = v_meal.get().strip() or "Dinner"
            title = v_title.get().strip()
            recipe_id = id_by_title.get(title, None)
            if not title and recipe_id is None:
                err.configure(text="Pick a recipe")
                return
            # Resolve title from recipe row if id present
            if recipe_id is not None:
                tr = self.db.execute("SELECT title FROM recipes WHERE id=?", (recipe_id,)).fetchone()
                title_resolved = tr["title"] if tr else title
            else:
                title_resolved = title
            notes = v_notes.get().strip()

            if row:
                self.db.execute(
                    "UPDATE menu_plan SET date=?, meal=?, recipe_id=?, title=?, notes=? WHERE id=?",
                    (d, meal, recipe_id, title_resolved, notes, int(row["id"])),
                )
            else:
                self.db.execute(
                    "INSERT INTO menu_plan(date, meal, recipe_id, title, notes) VALUES(?,?,?,?,?)",
                    (d, meal, recipe_id, title_resolved, notes),
                )
            self.db.commit()
            dlg.destroy()
            self.refresh_menu()
            self._notify_menu_changed()

        btns = ttk.Frame(dlg, padding=(8, 6))
        btns.grid(row=1, column=0, sticky="e")
        ttk.Button(btns, text="Cancel", command=dlg.destroy).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(btns, text="Save", command=save).grid(row=0, column=1)

    def _set_date_from_picker(self, initial: str, var: tk.StringVar) -> None:
        d = self._pick_date(initial)
        if d:
            var.set(d)

    # ---------- Delete ----------
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
        self._notify_menu_changed()

    # ---------- Export ----------
    def export_html_menu(self) -> None:
        tv = self._tree_menu
        if not isinstance(tv, ttk.Treeview):
            return
        items = tv.get_children("")
        rows = [list(tv.item(i, "values")) for i in items]
        headings = [hdr for _k, hdr, _w, _a in MENU_COLS]
        from utils.export import export_table_html

        export_table_html(
            path=None,
            title="Menu Plan",
            columns=headings,
            rows=rows,
            subtitle="Generated from Celiogix",
            meta={"Source": "Menu", "Rows": len(rows)},
            open_after=True,
        )
