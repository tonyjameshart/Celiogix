# path: panels/shopping_list_panel.py
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Tuple, Any

from panels.base_panel import BasePanel
from utils.export import export_table_html

COLS: List[Tuple[str, str, int, str]] = [
    ("name",       "Name",       280, "w"),
    ("brand",      "Brand",      140, "w"),
    ("category",   "Category",   120, "w"),
    ("store",      "Store",      120, "w"),
    ("notes",      "Notes",      260, "w"),
    ("net_weight", "Net.Wt",      80, "e"),
    ("thresh",     "Thresh",      70, "e"),
]

class ShoppingListPanel(BasePanel):
    """
    Shopping list with: alphabetical listing, basic CRUD, export, and
    **Import to Pantry (↑ qty) & Remove** which updates Pantry quantities/inserts,
    then deletes those rows from the shopping_list table.
    """
    def __init__(self, master, app, **kw):
        self._tree: Optional[ttk.Treeview] = None
        self._search_var: Optional[tk.StringVar] = None
        super().__init__(master, app, **kw)

    # ---------- UI ----------
    def build(self) -> None:
        # Top bar
        bar = ttk.Frame(self)
        bar.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        ttk.Button(bar, text="Add", command=self.add_item).pack(side="left")
        ttk.Button(bar, text="Delete", command=self.delete_selected).pack(side="left", padx=(6, 0))
        ttk.Button(bar, text="Import to Pantry (↑ qty) & Remove", command=self.import_to_pantry_selected).pack(side="left", padx=(12, 0))
        ttk.Button(bar, text="Export HTML (visible)", command=self.export_html_visible).pack(side="left", padx=(12, 0))

        # Search
        sbar, svar, _ = self.build_search_bar(
            parent=self,
            on_return=lambda q: self.refresh_list(),
            refresh_text="Refresh",
        )
        self._search_var = svar
        sbar.grid(row=1, column=0, sticky="ew", pady=(0, 4))

        # Table
        wrap = ttk.Frame(self)
        wrap.grid(row=2, column=0, sticky="nsew")
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        tv = ttk.Treeview(wrap, columns=[c[0] for c in COLS], show="headings", selectmode="extended")
        tv.grid(row=0, column=0, sticky="nsew")
        wrap.grid_rowconfigure(0, weight=1)
        wrap.grid_columnconfigure(0, weight=1)

        for key, hdr, width, align in COLS:
            tv.heading(key, text=hdr)
            anc = {"w": "w", "e": "e", "c": "center"}.get(align, "w")
            tv.column(key, width=width, anchor=anc, stretch=True)

        vsb = ttk.Scrollbar(wrap, orient="vertical", command=tv.yview)
        hsb = ttk.Scrollbar(wrap, orient="horizontal", command=tv.xview)
        tv.configure(yscroll=vsb.set, xscroll=hsb.set)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self._tree = tv

        # Context menu
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Edit", command=self.edit_selected)
        menu.add_command(label="Delete", command=self.delete_selected)
        menu.add_separator()
        menu.add_command(label="Import to Pantry (↑ qty) & Remove", command=self.import_to_pantry_selected)
        menu.add_separator()
        menu.add_command(label="Export HTML (visible)", command=self.export_html_visible)

        def popup(event):
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()
        tv.bind("<Button-3>", popup)
        tv.bind("<Double-1>", lambda e: self.edit_selected())

        self.refresh_list()

    # ---------- Data ----------
    def _filters(self) -> str:
        return (self._search_var.get().strip() if isinstance(self._search_var, tk.StringVar) else "")

    def refresh_list(self) -> None:
        tv = self._tree
        if not isinstance(tv, ttk.Treeview):
            return
        for it in tv.get_children():
            tv.delete(it)

        q = self._filters()
        where = []
        args: List[Any] = []
        if q:
            where.append("""LOWER(
                COALESCE(name,'') || ' ' ||
                COALESCE(brand,'') || ' ' ||
                COALESCE(category,'') || ' ' ||
                COALESCE(store,'') || ' ' ||
                COALESCE(notes,'')
            ) LIKE ?""")
            args.append(f"%{q.lower()}%")
        wsql = (" WHERE " + " AND ".join(where)) if where else ""

        # ALWAYS alphabetical by name, then brand
        sql = f"""
            SELECT id, name, brand, category, store, notes,
                   IFNULL(net_weight,0) AS net_weight,
                   IFNULL(thresh,0)     AS thresh
              FROM shopping_list
              {wsql}
             ORDER BY LOWER(COALESCE(name,'')), LOWER(COALESCE(brand,''))
        """
        rows = self.db.execute(sql, args).fetchall()
        for r in rows:
            tv.insert("", "end", iid=str(r["id"]), values=[
                r["name"] or "", r["brand"] or "", r["category"] or "", r["store"] or "",
                r["notes"] or "", r["net_weight"] or "", r["thresh"] or ""
            ])
        self.set_status(f"{len(rows)} item(s)")

    # ---------- CRUD ----------
    def add_item(self) -> None:
        data = self._edit_dialog(None)
        if not data:
            return
        self.db.execute("""
            INSERT INTO shopping_list(name, brand, category, net_weight, thresh, store, notes)
            VALUES(?,?,?,?,?,?,?)
        """, (data["name"], data["brand"], data["category"], data["net_weight"], data["thresh"], data["store"], data["notes"]))
        self.db.commit()
        self.refresh_list()
        self.set_status("Item added")

    def edit_selected(self) -> None:
        tv = self._tree
        if not isinstance(tv, ttk.Treeview): return
        sel = tv.selection()
        if len(sel) != 1:
            messagebox.showinfo("Shopping List", "Select one item to edit.", parent=self.winfo_toplevel())
            return
        rid = int(sel[0])
        row = self.db.execute("SELECT * FROM shopping_list WHERE id=?", (rid,)).fetchone()
        if not row:
            return
        data = self._edit_dialog(row)
        if not data:
            return
        self.db.execute("""
            UPDATE shopping_list
               SET name=?, brand=?, category=?, net_weight=?, thresh=?, store=?, notes=?
             WHERE id=?
        """, (data["name"], data["brand"], data["category"], data["net_weight"], data["thresh"], data["store"], data["notes"], rid))
        self.db.commit()
        self.refresh_list()
        self.set_status("Item updated")

    def delete_selected(self) -> None:
        tv = self._tree
        if not isinstance(tv, ttk.Treeview): return
        sel = tv.selection()
        if not sel: return
        if not self.confirm_delete(len(sel)): return
        ids = [int(i) for i in sel]
        q = ",".join("?" for _ in ids)
        self.db.execute(f"DELETE FROM shopping_list WHERE id IN ({q})", ids)
        self.db.commit()
        self.refresh_list()
        self.set_status(f"Deleted {len(ids)} item(s)")

    # ---------- Import to Pantry (↑ qty) & Remove ----------
    def import_to_pantry_selected(self) -> None:
        """
        For each selected shopping_list row:
          - If Pantry has an item with same (name, brand), increment quantity by 1.
          - Else insert a new Pantry row with quantity = 1 and carry over category, net_weight, store, notes.
        After successful import, remove those rows from shopping_list.
        """
        tv = self._tree
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        if not sel:
            messagebox.showinfo("Import to Pantry", "Select one or more items.", parent=self.winfo_toplevel())
            return

        cur = self.db.cursor()
        n_new = 0
        n_upd = 0
        to_delete: List[int] = []

        for iid in sel:
            rid = int(iid)
            r = cur.execute("""
                SELECT id, name, brand, category, IFNULL(net_weight,0) AS net_weight,
                       IFNULL(thresh,0) AS thresh, store, notes
                  FROM shopping_list WHERE id=?
            """, (rid,)).fetchone()
            if not r:
                continue

            name = (r["name"] or "").strip()
            brand = (r["brand"] or "").strip()
            category = (r["category"] or "").strip()
            net_wt = float(r["net_weight"] or 0.0)
            store = (r["store"] or "").strip()
            notes = (r["notes"] or "").strip()

            if not name:
                continue

            try:
                existing = cur.execute("""
                    SELECT id, IFNULL(quantity,0) AS quantity, COALESCE(category,'') AS cat
                      FROM pantry
                     WHERE LOWER(COALESCE(name,'')) = LOWER(?)
                       AND LOWER(COALESCE(brand,'')) = LOWER(?)
                     LIMIT 1
                """, (name, brand)).fetchone()

                if existing:
                    cur.execute("UPDATE pantry SET quantity = IFNULL(quantity,0) + 1 WHERE id=?", (existing["id"],))
                    if category and not (existing["cat"] or "").strip():
                        cur.execute("UPDATE pantry SET category=? WHERE id=?", (category, existing["id"]))
                    n_upd += 1
                else:
                    cur.execute("""
                        INSERT INTO pantry(name, brand, category, subcategory, net_weight, unit, quantity, store, expiration, gf_flag, tags, notes)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                    """, (name, brand, category, "", net_wt, "", 1.0, store, "", "UNKNOWN", "", notes))
                    n_new += 1

                to_delete.append(rid)  # mark for deletion only if import didn't raise
            except Exception:
                # leave the row in shopping_list if anything failed for this item
                continue

        # Apply deletions for rows that were imported successfully
        if to_delete:
            q = ",".join("?" for _ in to_delete)
            cur.execute(f"DELETE FROM shopping_list WHERE id IN ({q})", to_delete)

        self.db.commit()
        self.refresh_list()
        self.set_status(f"Imported to Pantry → updated: {n_upd}, new: {n_new}; removed {len(to_delete)} from Shopping")

    # ---------- Export visible ----------
    def export_html_visible(self) -> None:
        tv = self._tree
        if not isinstance(tv, ttk.Treeview): return
        items = tv.get_children("")
        rows = [list(tv.item(iid, "values")) for iid in items]
        headings = [hdr for _key, hdr, _w, _a in COLS]
        export_table_html(
            path=None,
            title="Shopping List (Filtered View)",
            columns=headings,
            rows=rows,
            subtitle="Generated from Celiac Culinary",
            meta={"Source": "Shopping List", "Rows": len(rows)},
            open_after=True,
        )
        self.set_status(f"Exported {len(rows)} row(s) to HTML")

    # ---------- Edit dialog ----------
    def _edit_dialog(self, row: Optional[dict]) -> Optional[dict]:
        dlg = tk.Toplevel(self)
        dlg.title("Shopping Item")
        dlg.transient(self.winfo_toplevel()); dlg.grab_set()

        frm = ttk.Frame(dlg, padding=8); frm.grid(row=0, column=0, sticky="nsew")
        dlg.grid_columnconfigure(0, weight=1); dlg.grid_rowconfigure(0, weight=1)

        def g(k, d=""):
            if row and k in row.keys(): return row[k]
            return d

        sv = {k: tk.StringVar(value=str(g(k, ""))) for k in ("name","brand","category","store","notes")}
        sv_num = {
            "net_weight": tk.StringVar(value=str(g("net_weight","0") or "0")),
            "thresh":     tk.StringVar(value=str(g("thresh","0") or "0")),
        }

        r = 0
        def roww(label: str, widget: tk.Widget, col=1):
            nonlocal r
            ttk.Label(frm, text=label).grid(row=r, column=0, sticky="e", padx=(0,8), pady=(0,4))
            widget.grid(row=r, column=col, sticky="ew", pady=(0,4))
            frm.grid_columnconfigure(col, weight=1)
            r += 1

        roww("Name", ttk.Entry(frm, textvariable=sv["name"], width=40))
        roww("Brand", ttk.Entry(frm, textvariable=sv["brand"], width=30))
        roww("Category", ttk.Entry(frm, textvariable=sv["category"], width=20))
        roww("Store", ttk.Entry(frm, textvariable=sv["store"], width=20))
        roww("Notes", ttk.Entry(frm, textvariable=sv["notes"], width=50))
        roww("Net.Wt", ttk.Entry(frm, textvariable=sv_num["net_weight"], width=10))
        roww("Thresh", ttk.Entry(frm, textvariable=sv_num["thresh"], width=10))

        out: dict = {}

        def parse_float(s: str) -> float:
            try:
                return float((s or "0").strip())
            except Exception:
                return 0.0

        def on_save():
            name = (sv["name"].get() or "").strip()
            if not name:
                messagebox.showerror("Shopping List", "Name is required.", parent=dlg); return
            out.update({
                "name": name,
                "brand": (sv["brand"].get() or "").strip(),
                "category": (sv["category"].get() or "").strip(),
                "net_weight": parse_float(sv_num["net_weight"].get()),
                "thresh": parse_float(sv_num["thresh"].get()),
                "store": (sv["store"].get() or "").strip(),
                "notes": (sv["notes"].get() or "").strip(),
            })
            dlg.destroy()

        btns = ttk.Frame(dlg, padding=(8,6)); btns.grid(row=1, column=0, sticky="e")
        ttk.Button(btns, text="Cancel", command=dlg.destroy).grid(row=0, column=0, padx=(0,6))
        ttk.Button(btns, text="Save", command=on_save).grid(row=0, column=1)
        dlg.wait_window()
        return out or None
