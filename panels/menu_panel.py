# path: panels/menu_panel.py
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, List, Tuple

from panels.base_panel import BasePanel
from utils.export import export_table_html

# Menu items view
MENU_COLS: List[Tuple[str, str, int, str]] = [
    ("date","Date",100,"c"),
    ("meal","Meal",100,"w"),
    ("title","Recipe",300,"w"),
    ("prep_time","Prep",80,"c"),
    ("cook_time","Cook",80,"c"),
    ("servings","Servings",80,"c"),
    ("notes","Notes",240,"w"),
]

# Recipe library (picker) inside Menu tab
REC_COLS: List[Tuple[str, str, int, str]] = [
    ("title","Title",280,"w"),
    ("source","Source",140,"w"),
    ("prep_time","Prep",80,"c"),
    ("cook_time","Cook",80,"c"),
    ("servings","Servings",80,"c"),
]

MEALS = ["Breakfast","Lunch","Dinner","Snack","Other"]

class MenuPanel(BasePanel):
    """Simple planner: left = planned menu; right = recipe library with new time/servings columns."""
    def __init__(self, master, app, **kw):
        self._tree_menu: Optional[ttk.Treeview] = None
        self._tree_rec: Optional[ttk.Treeview] = None
        super().__init__(master, app, **kw)

    def build(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Left: planned menu
        left = ttk.Frame(self, padding=6); left.grid(row=0, column=0, sticky="ns")
        ttk.Label(left, text="Menu").pack(anchor="w")
        wrap_m = ttk.Frame(left); wrap_m.pack(fill="both", expand=True)
        tvm = ttk.Treeview(wrap_m, columns=[c[0] for c in MENU_COLS], show="headings", height=16, selectmode="extended")
        for k,h,w,a in MENU_COLS:
            tvm.heading(k, text=h); anc={"w":"w","c":"center","e":"e"}.get(a,"w"); tvm.column(k, width=w, anchor=anc, stretch=True)
        tvm.pack(fill="both", expand=True)
        self._tree_menu = tvm

        btns = ttk.Frame(left); btns.pack(fill="x", pady=(6,0))
        ttk.Button(btns, text="Add From Selection →", command=self.add_from_selection).pack(fill="x")
        ttk.Button(btns, text="Edit", command=self.edit_selected).pack(fill="x", pady=(4,0))
        ttk.Button(btns, text="Delete", command=self.delete_selected).pack(fill="x")
        ttk.Button(btns, text="Export HTML", command=self.export_html_menu).pack(fill="x", pady=(6,0))

        # Right: recipe library (for picking)
        right = ttk.Frame(self, padding=6); right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(1, weight=1); right.grid_columnconfigure(0, weight=1)
        ttk.Label(right, text="Recipes").grid(row=0, column=0, sticky="w")
        tvr = ttk.Treeview(right, columns=[c[0] for c in REC_COLS], show="headings", selectmode="extended")
        for k,h,w,a in REC_COLS:
            tvr.heading(k, text=h); anc={"w":"w","c":"center","e":"e"}.get(a,"w"); tvr.column(k, width=w, anchor=anc, stretch=True)
        tvr.grid(row=1, column=0, sticky="nsew")
        self._tree_rec = tvr

        vsb = ttk.Scrollbar(right, orient="vertical", command=tvr.yview)
        tvr.configure(yscroll=vsb.set); vsb.grid(row=1, column=1, sticky="ns")

        # Menus
        m_menu = tk.Menu(self, tearoff=0)
        m_menu.add_command(label="Edit", command=self.edit_selected)
        m_menu.add_command(label="Delete", command=self.delete_selected)
        def popm(e): 
            try: m_menu.tk_popup(e.x_root, e.y_root)
            finally: m_menu.grab_release()
        tvm.bind("<Button-3>", popm)
        tvm.bind("<Double-1>", lambda e: self.edit_selected())

        self.refresh_recipes()
        self.refresh_menu()

    # ---------- Data ----------
    def refresh_recipes(self) -> None:
        tv = self._tree_rec
        if not isinstance(tv, ttk.Treeview): return
        for it in tv.get_children(): tv.delete(it)
        rows = self.db.execute("""
            SELECT id, title, source,
                   COALESCE(prep_time,'') AS prep_time,
                   COALESCE(cook_time,'') AS cook_time,
                   COALESCE(servings,0)   AS servings
              FROM recipes
             ORDER BY LOWER(title)
        """).fetchall()
        for r in rows:
            tv.insert("", "end", iid=f"rec::{r['id']}", values=[
                r["title"] or "", r["source"] or "", r["prep_time"] or "", r["cook_time"] or "", r["servings"] or 0
            ])

    def refresh_menu(self) -> None:
        tv = self._tree_menu
        if not isinstance(tv, ttk.Treeview): return
        for it in tv.get_children(): tv.delete(it)
        rows = self.db.execute("""
            SELECT mp.id, mp.date, mp.meal, mp.title,
                   COALESCE(r.prep_time,'') AS prep_time,
                   COALESCE(r.cook_time,'') AS cook_time,
                   COALESCE(r.servings,0)   AS servings,
                   mp.notes
              FROM menu_plan mp
              LEFT JOIN recipes r ON r.id = mp.recipe_id
             ORDER BY mp.date ASC, mp.meal ASC, LOWER(mp.title)
        """).fetchall()
        for r in rows:
            tv.insert("", "end", iid=str(r["id"]), values=[
                r["date"] or "", r["meal"] or "", r["title"] or "",
                r["prep_time"] or "", r["cook_time"] or "", r["servings"] or 0,
                r["notes"] or ""
            ])

    # ---------- Actions ----------
    def add_from_selection(self) -> None:
        tvr = self._tree_rec
        if not isinstance(tvr, ttk.Treeview): return
        sel = [i for i in tvr.selection() if i.startswith("rec::")]
        if not sel:
            messagebox.showinfo("Menu", "Select recipe(s) on the right.", parent=self.winfo_toplevel()); return
        date = simpledialog.askstring("Menu Planner", "Date (YYYY-MM-DD):", parent=self.winfo_toplevel())
        if not date: return
        meal = simpledialog.askstring("Menu Planner", "Meal:", initialvalue="Dinner", parent=self.winfo_toplevel()) or "Dinner"

        cur = self.db.cursor()
        for iid in sel:
            rid = int(iid.split("::",1)[1])
            r = cur.execute("SELECT title FROM recipes WHERE id=?", (rid,)).fetchone()
            if r:
                cur.execute("INSERT INTO menu_plan(date, meal, recipe_id, title, notes) VALUES(?,?,?,?,?)",
                            (date.strip(), meal.strip(), rid, r["title"], ""))
        self.db.commit()
        self.refresh_menu()
        self.set_status(f"Added {len(sel)} item(s) to Menu")

    def edit_selected(self) -> None:
        tv = self._tree_menu
        if not isinstance(tv, ttk.Treeview): return
        sel = tv.selection()
        if len(sel) != 1:
            messagebox.showinfo("Menu", "Select one row to edit.", parent=self.winfo_toplevel()); return
        rid = int(sel[0])
        r = self.db.execute("SELECT date, meal, title, notes FROM menu_plan WHERE id=?", (rid,)).fetchone()
        if not r: return
        dlg = tk.Toplevel(self); dlg.title("Edit Menu Item"); dlg.transient(self.winfo_toplevel()); dlg.grab_set()
        frm = ttk.Frame(dlg, padding=8); frm.grid(row=0, column=0, sticky="nsew")
        v_date = tk.StringVar(value=r["date"] or "")
        v_meal = tk.StringVar(value=r["meal"] or "Dinner")
        v_title= tk.StringVar(value=r["title"] or "")
        v_notes= tk.StringVar(value=r["notes"] or "")
        def row(label,w,rowi):
            ttk.Label(frm,text=label).grid(row=rowi,column=0,sticky="e",padx=(0,8),pady=(0,4)); w.grid(row=rowi,column=1,sticky="ew",pady=(0,4))
        row("Date", ttk.Entry(frm,textvariable=v_date,width=12), 0)
        row("Meal", ttk.Combobox(frm,textvariable=v_meal,values=MEALS,state="readonly",width=12), 1)
        row("Title", ttk.Entry(frm,textvariable=v_title,width=36), 2)
        row("Notes", ttk.Entry(frm,textvariable=v_notes,width=48), 3)
        frm.grid_columnconfigure(1,weight=1)
        out={}
        def save(): out.update({"date":v_date.get().strip(),"meal":v_meal.get().strip(),"title":v_title.get().strip(),"notes":v_notes.get().strip()}); dlg.destroy()
        bt=ttk.Frame(dlg,padding=(8,6)); bt.grid(row=1,column=0,sticky="e")
        ttk.Button(bt,text="Cancel",command=dlg.destroy).grid(row=0,column=0,padx=(0,6))
        ttk.Button(bt,text="Save",command=save).grid(row=0,column=1)
        dlg.wait_window()
        if not out: return
        self.db.execute("UPDATE menu_plan SET date=?, meal=?, title=?, notes=? WHERE id=?",(out["date"],out["meal"],out["title"],out["notes"],rid))
        self.db.commit()
        self.refresh_menu()

    def delete_selected(self) -> None:
        tv = self._tree_menu
        if not isinstance(tv, ttk.Treeview): return
        sel = tv.selection()
        if not sel: return
        if not self.confirm_delete(len(sel)): return
        ids = [int(i) for i in sel]
        q = ",".join("?" for _ in ids)
        self.db.execute(f"DELETE FROM menu_plan WHERE id IN ({q})", ids)
        self.db.commit()
        self.refresh_menu()

    def export_html_menu(self) -> None:
        tv = self._tree_menu
        if not isinstance(tv, ttk.Treeview): return
        items = tv.get_children("")
        rows = [list(tv.item(i, "values")) for i in items]
        headings = [hdr for _k, hdr, _w, _a in MENU_COLS]
        export_table_html(
            path=None,
            title="Menu Plan",
            columns=headings,
            rows=rows,
            subtitle="Generated from Celiac Culinary",
            meta={"Source":"Menu","Rows":len(rows)},
            open_after=True,
        )
