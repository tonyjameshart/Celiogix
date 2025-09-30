# panels/shopping_list_panel.py
from __future__ import annotations

import re
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from typing import Any

from panels.base_panel import BasePanel
from utils.export import export_table_html  # ensure this exists in your project


COLS = [
    ("purchased", "✓", 32, "c"),
    ("name", "Item", 260, "w"),
    ("brand", "Brand", 120, "w"),
    ("category", "Category", 120, "w"),
    ("store", "Store", 100, "w"),
    ("net_weight", "Size", 80, "c"),
    ("thresh", "Qty", 60, "c"),
    ("notes", "Notes", 260, "w"),
]


class ShoppingListPanel(BasePanel):
    def __init__(self, master, app, **kw):
        self.tree: ttk.Treeview | None = None
        self._hide_purchased: tk.BooleanVar | None = None
        super().__init__(master, app, **kw)

    def build(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._ensure_purchased_column()

        wrap = ttk.Frame(self, padding=6)
        wrap.grid(row=0, column=0, sticky="nsew")
        wrap.grid_rowconfigure(1, weight=1)
        wrap.grid_columnconfigure(0, weight=1)

        bar = ttk.Frame(wrap)
        bar.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        ttk.Button(bar, text="Add…", command=self.add_item).pack(side="left")
        ttk.Button(bar, text="Edit", command=self.edit_selected).pack(side="left", padx=(6, 0))
        ttk.Button(bar, text="Delete", command=self.delete_selected).pack(side="left", padx=(6, 0))
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Button(bar, text="Add from Recipe…", command=self.add_from_recipe).pack(side="left")
        ttk.Button(bar, text="Add from Recipes…", command=self.add_from_multiple_recipes).pack(side="left", padx=(6,0))
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Button(bar, text="Mark Purchased", command=self.mark_selected_purchased).pack(side="left")
        ttk.Button(bar, text="Unmark Purchased", command=self.unmark_selected_purchased).pack(side="left", padx=(6,0))
        self._hide_purchased = tk.BooleanVar(value=False)
        ttk.Checkbutton(bar, text="Hide purchased", variable=self._hide_purchased, command=self.refresh_list).pack(side="left", padx=(12,0))
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Button(bar, text="Copy", command=self.copy_visible_to_clipboard).pack(side="left")
        ttk.Button(bar, text="Open HTML", command=lambda: self.export_visible_html(open_after=True)).pack(side="left", padx=(6, 0))
        ttk.Button(bar, text="Print", command=lambda: self.export_visible_html(open_after=True, invoke_print=True)).pack(side="left", padx=(6, 0))
        ttk.Button(bar, text="Fit Columns", command=lambda: self.fit_columns_now(self.tree, exact=True, max_px_map={"notes": 1200})).pack(side="left", padx=(12, 0))

        wrap_tv, tv, vsb, hsb = self.make_scrolling_tree(wrap, [c[0] for c in COLS])
        for key, hdr, width, align in COLS:
            tv.heading(key, text=hdr)
            tv.column(key, width=width, anchor={"w": "w", "e": "e", "c": "center"}.get(align, "w"), stretch=False)
        wrap_tv.grid(row=1, column=0, sticky="nsew")
        self.tree = tv

        tv.bind("<Double-1>", lambda _e: self.edit_selected())

        m = tk.Menu(self, tearoff=0)
        m.add_command(label="Add…", command=self.add_item)
        m.add_command(label="Edit…", command=self.edit_selected)
        m.add_command(label="Delete", command=self.delete_selected)
        m.add_separator()
        m.add_command(label="Add from Recipe…", command=self.add_from_recipe)
        m.add_command(label="Add from Recipes…", command=self.add_from_multiple_recipes)
        m.add_separator()
        m.add_command(label="Mark Purchased", command=self.mark_selected_purchased)
        m.add_command(label="Unmark Purchased", command=self.unmark_selected_purchased)
        m.add_separator()
        m.add_command(label="Copy", command=self.copy_visible_to_clipboard)
        m.add_command(label="Open HTML", command=lambda: self.export_visible_html(open_after=True))
        m.add_command(label="Print", command=lambda: self.export_visible_html(open_after=True, invoke_print=True))
        m.add_separator()
        m.add_command(label="Fit Columns", command=lambda: self.fit_columns_now(self.tree, exact=True, max_px_map={"notes": 1200}))
        tv.bind("<Button-3>", lambda e, menu=m: self._popup_menu(e, menu))

        self.refresh_list()
        self.after(0, lambda: self.fit_columns_now(self.tree, exact=True, max_px_map={"notes": 1200}))

    def _ensure_purchased_column(self) -> None:
        try:
            cols = {r[1] for r in self.db.execute("PRAGMA table_info(shopping_list)").fetchall()}
            if "purchased" not in cols:
                self.db.execute("ALTER TABLE shopping_list ADD COLUMN purchased INTEGER NOT NULL DEFAULT 0")
                self.db.commit()
        except Exception:
            pass

    def refresh_list(self) -> None:
        tv = self.tree
        if not isinstance(tv, ttk.Treeview):
            return
        for iid in tv.get_children():
            tv.delete(iid)

        hide = bool(self._hide_purchased.get()) if isinstance(self._hide_purchased, tk.BooleanVar) else False
        where_clause = "WHERE purchased=0" if hide else ""
        rows = self.db.execute(
            f"""
            SELECT id, name, brand, category, store,
                   COALESCE(net_weight, '') AS net_weight,
                   COALESCE(thresh, '')     AS thresh,
                   COALESCE(notes, '')      AS notes,
                   IFNULL(purchased,0)      AS purchased
              FROM shopping_list
             {where_clause}
             ORDER BY LOWER(COALESCE(category,'')), LOWER(COALESCE(name,''))
            """
        ).fetchall()
        for r in rows:
            tick = "✓" if r["purchased"] else ""
            tv.insert(
                "",
                "end",
                iid=str(r["id"]),
                values=[tick, r["name"], r["brand"], r["category"], r["store"], r["net_weight"], r["thresh"], r["notes"]],
            )
        self.set_status(f"{len(rows)} item(s)")

    def add_item(self) -> None:
        data = self._item_dialog(None)
        if not data:
            return
        self.db.execute(
            """
            INSERT INTO shopping_list(name, brand, category, store, net_weight, thresh, notes, purchased)
            VALUES(?,?,?,?,?,?,?,?)
            """,
            (data["name"], data["brand"], data["category"], data["store"], data["net_weight"], data["thresh"], data["notes"], 0),
        )
        self.db.commit()
        self.refresh_list()

    def edit_selected(self) -> None:
        tv = self.tree
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        if len(sel) != 1:
            messagebox.showinfo("Shopping List", "Select one row to edit.", parent=self.winfo_toplevel())
            return
        sid = int(sel[0])
        r = self.db.execute(
            """
            SELECT id, name, brand, category, store,
                   COALESCE(net_weight,'') AS net_weight,
                   COALESCE(thresh,'')     AS thresh,
                   COALESCE(notes,'')      AS notes,
                   IFNULL(purchased,0)     AS purchased
              FROM shopping_list WHERE id=?
            """,
            (sid,),
        ).fetchone()
        if not r:
            return
        data = self._item_dialog(r)
        if not data:
            return
        self.db.execute(
            """
            UPDATE shopping_list
               SET name=?, brand=?, category=?, store=?, net_weight=?, thresh=?, notes=?
             WHERE id=?
            """,
            (data["name"], data["brand"], data["category"], data["store"], data["net_weight"], data["thresh"], data["notes"], sid),
        )
        self.db.commit()
        self.refresh_list()

    def delete_selected(self) -> None:
        tv = self.tree
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        if not sel:
            return
        if not self.confirm_delete(len(sel)):
            return
        ids = [int(i) for i in sel]
        q = ",".join("?" for _ in ids)
        self.db.execute(f"DELETE FROM shopping_list WHERE id IN ({q})", ids)
        self.db.commit()
        self.refresh_list()

    def mark_selected_purchased(self) -> None:
        tv = self.tree
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        if not sel:
            return
        ids = [int(i) for i in sel]
        q = ",".join("?" for _ in ids)
        self.db.execute(f"UPDATE shopping_list SET purchased=1 WHERE id IN ({q})", ids)
        self.db.commit()
        self.refresh_list()

    def unmark_selected_purchased(self) -> None:
        tv = self.tree
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        if not sel:
            return
        ids = [int(i) for i in sel]
        q = ",".join("?" for _ in ids)
        self.db.execute(f"UPDATE shopping_list SET purchased=0 WHERE id IN ({q})", ids)
        self.db.commit()
        self.refresh_list()

    def add_from_recipe(self) -> None:
        r = self._pick_recipe()
        if not r:
            return
        ingredients = (r.get("ingredients") or "").strip()
        if not ingredients:
            messagebox.showinfo("Shopping List", "Recipe has no ingredients.", parent=self.winfo_toplevel())
            return
        lines = [ln for ln in (ingredients.replace("\r\n", "\n").split("\n")) if ln.strip()]
        count = 0
        for raw in lines:
            name = self._normalize_ingredient(raw)
            if not name:
                continue
            self.db.execute(
                """
                INSERT INTO shopping_list(name, brand, category, store, net_weight, thresh, notes, purchased)
                VALUES(?,?,?,?,?,?,?,?)
                """,
                (name, "", "", "", "", "", f"from recipe: {r.get('title','')}", 0),
            )
            count += 1
        if count:
            self.db.commit()
            self.refresh_list()
            self.set_status(f"Added {count} item(s) from recipe")

    def add_from_multiple_recipes(self) -> None:
        choices = self.db.execute("SELECT id, title, COALESCE(ingredients,'') AS ingredients FROM recipes ORDER BY LOWER(title)").fetchall()
        if not choices:
            messagebox.showinfo("Recipes", "No recipes found.", parent=self.winfo_toplevel()); return

        dlg = tk.Toplevel(self)
        dlg.title("Select recipes to import ingredients from")
        dlg.transient(self.winfo_toplevel()); dlg.grab_set()
        frm = ttk.Frame(dlg, padding=8); frm.grid(row=0, column=0, sticky="nsew")
        dlg.grid_rowconfigure(0, weight=1); dlg.grid_columnconfigure(0, weight=1)
        lb_frame = ttk.Frame(frm); lb_frame.grid(row=0, column=0, sticky="nsew")
        sv = tk.StringVar()
        ttk.Entry(frm, textvariable=sv).grid(row=1, column=0, sticky="ew", pady=(6,0))
        listbox = tk.Listbox(lb_frame, selectmode="multiple", width=60, height=18)
        listbox.grid(row=0, column=0, sticky="nsew")
        sby = ttk.Scrollbar(lb_frame, orient="vertical", command=listbox.yview); sby.grid(row=0, column=1, sticky="ns")
        listbox.configure(yscrollcommand=sby.set)
        items = [(r["id"], r["title"], r["ingredients"]) for r in choices]

        def populate(filter_q=""):
            listbox.delete(0, "end")
            for rid, title, _ing in items:
                if not filter_q or filter_q.lower() in title.lower():
                    listbox.insert("end", f"{rid:>4}  {title}")
        populate()

        def on_filter(_e=None):
            populate(sv.get().strip())
        sv.trace_add("write", lambda *a: on_filter())

        # capture selection before destroying dialog
        selected_indices: list[int] = []

        def on_ok():
            nonlocal selected_indices
            sel = listbox.curselection()
            selected_indices = list(sel)
            dlg.destroy()

        btns = ttk.Frame(frm); btns.grid(row=2, column=0, sticky="e", pady=(6,0))
        ttk.Button(btns, text="Cancel", command=dlg.destroy).grid(row=0, column=0, padx=(0,6))
        ttk.Button(btns, text="Import Selected", command=on_ok).grid(row=0, column=1)
        dlg.wait_window()

        if not selected_indices:
            return

        q = sv.get().strip().lower()
        filtered = [(rid, title, ing) for rid, title, ing in items if not q or q in title.lower()]
        selected_rows = [filtered[i] for i in selected_indices if 0 <= i < len(filtered)]

        count = 0
        for rid, title, ingredients in selected_rows:
            lines = [ln for ln in (ingredients.replace("\r\n", "\n").split("\n")) if ln.strip()]
            for raw in lines:
                name = self._normalize_ingredient(raw)
                if not name:
                    continue
                self.db.execute(
                    """
                    INSERT INTO shopping_list(name, brand, category, store, net_weight, thresh, notes, purchased)
                    VALUES(?,?,?,?,?,?,?,?)
                    """,
                    (name, "", "", "", "", "", f"from recipe: {title}", 0),
                )
                count += 1
        if count:
            self.db.commit()
            self.refresh_list()
            self.set_status(f"Imported {count} item(s) from {len(selected_rows)} recipe(s)")

    def _normalize_ingredient(self, s: str) -> str:
        s = s.strip()
        s = re.sub(r"^\s*[-*•]\s*", "", s)
        s = re.sub(r"^\d+([\/.]\d+)?\s*(cups?|tsp|tbsp|tablespoons?|teaspoons?|pounds?|lbs?|oz|ounces?|grams?|g|kg|ml|l)\b\.?,?\s*", "", s, flags=re.I)
        s = re.sub(r"^\d+([\/.]\d+)?\s+", "", s)
        return s.strip()

    def _pick_recipe(self) -> dict[str, Any] | None:
        rows = self.db.execute("SELECT id, title, COALESCE(ingredients,'') AS ingredients FROM recipes ORDER BY LOWER(title)").fetchall()
        if not rows:
            messagebox.showinfo("Recipes", "No recipes found.", parent=self.winfo_toplevel()); return None

        dlg = tk.Toplevel(self)
        dlg.title("Choose a recipe")
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()
        dlg.resizable(True, True)
        dlg.geometry("520x380")

        frm = ttk.Frame(dlg, padding=8)
        frm.grid(row=0, column=0, sticky="nsew")
        dlg.grid_rowconfigure(0, weight=1)
        dlg.grid_columnconfigure(0, weight=1)

        sv = tk.StringVar()
        e = ttk.Entry(frm, textvariable=sv)
        e.grid(row=0, column=0, sticky="ew", pady=(0,6))
        frm.grid_columnconfigure(0, weight=1)

        lb = tk.Listbox(frm, activestyle="dotbox")
        lb.grid(row=1, column=0, sticky="nsew")
        sby = ttk.Scrollbar(frm, orient="vertical", command=lb.yview)
        lb.configure(yscrollcommand=sby.set)
        sby.grid(row=1, column=1, sticky="ns")

        data = [(r["id"], r["title"], r["ingredients"]) for r in rows]

        def refresh_listbox():
            q = (sv.get() or "").lower().strip()
            lb.delete(0, "end")
            for rid, title, _ing in data:
                if not q or q in title.lower():
                    lb.insert("end", f"{rid:>4}  {title}")
        refresh_listbox()

        sv.trace_add("write", lambda *a: refresh_listbox())

        selected_index: list[int] = []

        def on_ok_single():
            nonlocal selected_index
            sel = lb.curselection()
            selected_index = list(sel)
            dlg.destroy()

        lb.bind("<Double-1>", lambda _e: on_ok_single())

        btns = ttk.Frame(dlg, padding=(0,8))
        btns.grid(row=2, column=0, sticky="e")
        ttk.Button(btns, text="Cancel", command=lambda: (dlg.destroy())).grid(row=0, column=0, padx=(0,6))
        ttk.Button(btns, text="Add ingredients", command=on_ok_single).grid(row=0, column=1)

        dlg.wait_window()

        if not selected_index:
            return None
        idx = selected_index[0]
        q = (sv.get() or "").lower().strip()
        filtered = [(rid, title, ing) for rid, title, ing in data if not q or q in title.lower()]
        if idx < 0 or idx >= len(filtered):
            return None
        rid, title, ing = filtered[idx]
        return {"id": rid, "title": title, "ingredients": ing}

    def copy_visible_to_clipboard(self) -> None:
        tv = self.tree
        if not isinstance(tv, ttk.Treeview):
            return
        headings = [hdr for _k, hdr, _w, _a in COLS]
        rows = [headings]
        for iid in tv.get_children(""):
            vals = tv.item(iid, "values")
            rows.append([str(v) for v in vals])
        tsv = "\n".join(["\t".join(row) for row in rows])
        try:
            self.clipboard_clear()
            self.clipboard_append(tsv)
            self.set_status("Copied to clipboard")
        except Exception:
            messagebox.showinfo("Shopping List", "Failed to access clipboard.", parent=self.winfo_toplevel())

    def export_visible_html(self, *, open_after: bool = True, invoke_print: bool = False) -> None:
        tv = self.tree
        if not isinstance(tv, ttk.Treeview):
            return
        headings = [hdr for _k, hdr, _w, _a in COLS]
        rows = [list(tv.item(i, "values")) for i in tv.get_children("")]
        html_path = export_table_html(
            path=None,
            title="Shopping List",
            columns=headings,
            rows=rows,
            subtitle="Celiogix",
            meta={"Rows": len(rows)},
            open_after=open_after,
            extra_head=("<script>window.onload=function(){if(location.hash==='#print'){window.print();}}</script>" if invoke_print else ""),
        )
        if invoke_print and open_after and isinstance(html_path, str):
            try:
                import webbrowser
                webbrowser.open(f"file:///{html_path}#print", new=2)
            except Exception:
                pass

    def _item_dialog(self, row: sqlite3.Row | None) -> dict[str, Any] | None:
        dlg = tk.Toplevel(self)
        dlg.title("Shopping item"); dlg.transient(self.winfo_toplevel()); dlg.grab_set()
        frm = ttk.Frame(dlg, padding=8); frm.grid(row=0, column=0, sticky="nsew")
        frm.grid_columnconfigure(1, weight=1)

        def g(k: str, d: str = "") -> str:
            if row is None:
                return d
            return str(row[k]) if k in row.keys() and row[k] is not None else d

        v = {
            "name": tk.StringVar(value=g("name")),
            "brand": tk.StringVar(value=g("brand")),
            "category": tk.StringVar(value=g("category")),
            "store": tk.StringVar(value=g("store")),
            "net_weight": tk.StringVar(value=g("net_weight")),
            "thresh": tk.StringVar(value=str(g("thresh", ""))),
            "notes": tk.StringVar(value=g("notes")),
        }

        r = 0
        def roww(label: str, widget: tk.Widget):
            nonlocal r
            ttk.Label(frm, text=label).grid(row=r, column=0, sticky="e", padx=(0,8), pady=(0,4))
            widget.grid(row=r, column=1, sticky="ew", pady=(0,4))
            r += 1

        roww("Item *", ttk.Entry(frm, textvariable=v["name"], width=36))
        roww("Brand", ttk.Entry(frm, textvariable=v["brand"]))
        roww("Category", ttk.Entry(frm, textvariable=v["category"]))
        roww("Store", ttk.Entry(frm, textvariable=v["store"]))
        roww("Size", ttk.Entry(frm, textvariable=v["net_weight"], width=10))
        roww("Qty", ttk.Entry(frm, textvariable=v["thresh"], width=8))
        roww("Notes", ttk.Entry(frm, textvariable=v["notes"]))

        err = ttk.Label(frm, text="", foreground="red")
        err.grid(row=r, column=1, sticky="w"); r += 1

        out: dict[str, Any] = {}
        def save():
            name = (v["name"].get() or "").strip()
            if not name:
                err.config(text="Item name is required"); return
            out.update({k: (vv.get() or "").strip() for k, vv in v.items()})
            dlg.destroy()

        btns = ttk.Frame(dlg, padding=(8, 6)); btns.grid(row=1, column=0, sticky="e")
        ttk.Button(btns, text="Cancel", command=dlg.destroy).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(btns, text="Save", command=save).grid(row=0, column=1)
        dlg.wait_window()
        return out or None

    def _popup_menu(self, ev: tk.Event, menu: tk.Menu) -> None:
        try:
            menu.tk_popup(ev.x_root, ev.y_root)
        finally:
            menu.grab_release()
