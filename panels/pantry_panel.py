# path: panels/pantry_panel.py
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Any, Dict, List, Optional, Tuple
import re

from panels.base_panel import BasePanel
from utils.export import export_table_html
from utils.categorize import (
    KNOWN_CATEGORIES,
    canonical_category,
    canonical_subcategory,
)

# ---------- GF helpers ----------
def _has_gf_tag(tags: str) -> bool:
    if not tags:
        return False
    parts = re.split(r"[;,]\s*|\s+", str(tags))
    return any(p.strip().lower() == "gf" for p in parts if p.strip())

try:
    from utils.gluten import classify_text as _classify_text  # type: ignore
    def _classify_gf_by_text(name: str, brand: str, tags: str, notes: str) -> str:
        blob = " ".join([name or "", brand or "", tags or "", notes or ""])
        return (_classify_text(blob) or "UNKNOWN").upper()
except Exception:
    try:
        from utils.gf_lexicon import classify_text as _classify_text2  # type: ignore
        def _classify_gf_by_text(name: str, brand: str, tags: str, notes: str) -> str:
            blob = " ".join([name or "", brand or "", tags or "", notes or ""])
            return (_classify_text2(blob) or "UNKNOWN").upper()
    except Exception:
        BAD = ("wheat","barley","rye","malt","farro","spelt","seitan","bulgur","semolina","graham")
        def _classify_gf_by_text(name: str, brand: str, tags: str, notes: str) -> str:
            blob = " ".join([name or "", brand or "", tags or "", notes or ""]).lower()
            if any(x in blob for x in BAD): return "NGF"
            if "gluten-free" in blob or "gluten free" in blob or "gf" in blob: return "GF"
            return "UNKNOWN"

def _normalize_gf_flag(gf_flag: str, tags: str) -> str:
    if _has_gf_tag(tags):
        return "GF"
    return (gf_flag or "UNKNOWN").upper()

# ---------- Columns ----------
COLS: List[Tuple[str, str, int, str]] = [
    ("name",        "Name",        220, "w"),
    ("brand",       "Brand",       140, "w"),
    ("category",    "Category",    120, "w"),
    ("subcategory", "SubCategory", 140, "w"),
    ("net_weight",  "Net.Wt",       70, "e"),
    ("unit",        "Unit",         60, "c"),
    ("quantity",    "Quantity",     80, "e"),
    ("store",       "Store",       100, "w"),
    ("expiration",  "Expiration",  110, "c"),
    ("gf_flag",     "GF",           80, "c"),
    ("tags",        "Tags",        160, "w"),
    ("notes",       "Notes",       220, "w"),
]

class PantryPanel(BasePanel):
    """Pantry with Category→Subcategory filtering, search, GF auto-tagging, UPC import, alphabetical listing, and category cleanup."""
    def __init__(self, master, app, **kw):
        self._tree_cat: Optional[ttk.Treeview] = None
        self._tree: Optional[ttk.Treeview] = None
        self._search_var: Optional[tk.StringVar] = None
        self._current_cat: Optional[str] = None
        self._current_sub: Optional[str] = None
        super().__init__(master, app, **kw)

    # ---------------- UPC resolver ----------------
    def _resolve_upc(self, upc: str) -> Dict[str, Any]:
        upc = (upc or "").strip().replace(" ", "")
        data: Dict[str, Any] = {}

        def _apply(src: Optional[Dict[str, Any]]) -> bool:
            nonlocal data
            if isinstance(src, dict) and src:
                data = dict(src); return True
            return False

        # utils.gtin
        try:
            from utils import gtin as _gtin  # type: ignore
            for fn in ("lookup", "lookup_upc", "resolve_upc", "fetch", "search"):
                if hasattr(_gtin, fn):
                    try:
                        if _apply(getattr(_gtin, fn)(upc)): break  # type: ignore
                    except Exception:
                        pass
        except Exception:
            pass

        # utils.importers
        try:
            from utils import importers as _imp  # type: ignore
            for fn in ("lookup_upc", "fetch_upc", "import_by_upc", "resolve_upc"):
                if hasattr(_imp, fn):
                    try:
                        if _apply(getattr(_imp, fn)(upc)): break  # type: ignore
                    except Exception:
                        pass
        except Exception:
            pass

        name  = str(data.get("name")  or data.get("title") or data.get("product") or f"Item {upc}").strip()
        brand = str(data.get("brand") or data.get("manufacturer") or "").strip()
        cat   = canonical_category(str(data.get("category")    or ""))
        sub   = canonical_subcategory(str(data.get("subcategory") or ""))
        unit  = str(data.get("unit")        or "").strip()
        tags  = str(data.get("tags")        or "").strip()
        notes = str(data.get("notes")       or "").strip()

        def pf(x) -> float:
            s = str(x or "").strip()
            if not s: return 0.0
            try:
                if "/" in s and re.match(r"^\s*\d+\s*/\s*\d+\s*$", s):
                    a, b = s.split("/", 1); return float(a)/float(b)
                return float(s)
            except Exception:
                return 0.0

        net_wt = pf(data.get("net_weight") or data.get("net_wt") or data.get("weight_oz") or 0)
        qty    = pf(data.get("quantity") or 1)

        note_upc = f"UPC:{upc}"
        notes = note_upc if not notes else (notes if note_upc in notes else (notes + f"; {note_upc}"))

        if data.get("gf") is True or str(data.get("gf_flag","")).upper() == "GF":
            if "GF" not in [t.strip().upper() for t in re.split(r"[;,]\s*|\s+", tags) if t.strip()]:
                tags = (tags + "; GF").strip("; ").strip()

        gf_flag = _normalize_gf_flag(str(data.get("gf_flag") or ""), tags)

        return {
            "name": name, "brand": brand, "category": cat, "subcategory": sub,
            "net_weight": net_wt, "unit": unit, "quantity": qty,
            "store": "", "expiration": "", "gf_flag": gf_flag, "tags": tags, "notes": notes
        }

    # ---------------- UI ----------------
    def build(self) -> None:
        # top toolbar
        bar = ttk.Frame(self); bar.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,6))
        ttk.Button(bar, text="Add", command=self.add_item).pack(side="left")
        ttk.Button(bar, text="Add by UPC", command=self.add_by_upc).pack(side="left", padx=(6,0))
        ttk.Button(bar, text="Clean Categories", command=self.clean_categories).pack(side="left", padx=(12,0))

        # two columns: left = category tree, right = search + table
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Left: Category/Subcategory tree
        left = ttk.Frame(self, padding=(0, 0))
        left.grid(row=1, column=0, sticky="nsw", padx=(0,12))
        ttk.Label(left, text="Pantry Groups", style="Muted.TLabel").pack(anchor="w", padx=4, pady=(0,4))
        self._tree_cat = ttk.Treeview(left, show="tree", height=18)
        self._tree_cat.pack(fill="both", expand=True, padx=4, pady=(0,8))
        self._tree_cat.bind("<<TreeviewSelect>>", self._on_pick_group)

        # Right: search + table
        right = ttk.Frame(self, padding=(0,0))
        right.grid(row=1, column=1, sticky="nsew")
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        sbar, svar, _ = self.build_search_bar(
            parent=right,
            on_return=lambda q: self.refresh_list(),
            refresh_text="Refresh",
        )
        self._search_var = svar
        sbar.grid(row=0, column=0, sticky="ew")

        table_wrap = ttk.Frame(right)
        table_wrap.grid(row=1, column=0, sticky="nsew")
        table_wrap.grid_rowconfigure(0, weight=1)
        table_wrap.grid_columnconfigure(0, weight=1)

        self._tree = ttk.Treeview(table_wrap, columns=[c[0] for c in COLS], show="headings", selectmode="extended")
        self._tree.grid(row=0, column=0, sticky="nsew")

        for key, hdr, width, anchor in COLS:
            self._tree.heading(key, text=hdr)
            anc = {"w":"w", "e":"e", "c":"center"}.get(anchor, "w")
            self._tree.column(key, width=width, anchor=anc, stretch=True)

        vsb = ttk.Scrollbar(table_wrap, orient="vertical", command=self._tree.yview)
        hsb = ttk.Scrollbar(table_wrap, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Context menu
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Edit", command=self.edit_selected)
        menu.add_command(label="Delete", command=self.delete_selected)
        menu.add_separator()
        menu.add_command(label="Auto-tag GF", command=self.auto_tag_gf_selected)
        menu.add_separator()
        menu.add_command(label="Export HTML (visible)", command=self.export_html_visible)

        def popup(event):
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()
        self._tree.bind("<Button-3>", popup)
        self._tree.bind("<Double-1>", lambda e: self.edit_selected())

        # Load
        self.refresh_groups()
        self.refresh_list()

    # ---------------- Data refresh ----------------
    def _filters(self) -> Tuple[Optional[str], Optional[str], str]:
        q = (self._search_var.get().strip() if isinstance(self._search_var, tk.StringVar) else "")
        return self._current_cat, self._current_sub, q

    def refresh_groups(self) -> None:
        tv = self._tree_cat
        if not isinstance(tv, ttk.Treeview):
            return
        for it in tv.get_children():
            tv.delete(it)

        rows = self.db.execute("""
            SELECT 
                COALESCE(NULLIF(TRIM(category), ''), '(Uncategorized)') AS cat,
                COALESCE(NULLIF(TRIM(subcategory), ''), '(None)')       AS sub,
                COUNT(*) AS n
            FROM pantry
            GROUP BY cat, sub
            ORDER BY LOWER(cat), LOWER(sub)
        """).fetchall()

        root = tv.insert("", "end", iid="ALL", text=f"All Items", open=True)
        cats: Dict[str, str] = {}
        subtotal: Dict[str, int] = {}
        total = 0
        for r in rows:
            # Show canonicalized names in the tree labels
            cat = canonical_category(r["cat"])
            sub = "(None)" if r["sub"] == "(None)" else canonical_subcategory(r["sub"])
            n = int(r["n"] or 0)
            total += n
            subtotal[cat] = subtotal.get(cat, 0) + n
            key = (cat, sub)
            if key not in cats:
                cats[key] = ""  # placeholder

        # Insert categories first
        cat_ids: Dict[str, str] = {}
        for cat in sorted({c for (c, _s) in cats.keys()}, key=lambda s: s.lower()):
            cid = f"cat::{cat}"
            cat_ids[cat] = cid
            tv.insert(root, "end", iid=cid, text=f"{cat} ({subtotal.get(cat,0)})", open=False)

        # Insert subcategories
        # We need counts per (cat, sub) again
        counts: Dict[Tuple[str,str], int] = {}
        for r in rows:
            cat = canonical_category(r["cat"])
            sub = "(None)" if r["sub"] == "(None)" else canonical_subcategory(r["sub"])
            counts[(cat, sub)] = counts.get((cat, sub), 0) + int(r["n"] or 0)
        for (cat, sub), n in sorted(counts.items(), key=lambda kv: (kv[0][0].lower(), kv[0][1].lower())):
            pid = cat_ids.get(cat)
            if not pid: continue
            sid = f"sub::{cat}::{sub}"
            tv.insert(pid, "end", iid=sid, text=f"{sub} ({n})", open=False)

        tv.item(root, text=f"All Items ({total})")

        if self._current_cat is None and self._current_sub is None:
            tv.selection_set(("ALL",))
            tv.focus("ALL")

    def refresh_list(self) -> None:
        tv = self._tree
        if not isinstance(tv, ttk.Treeview):
            return
        for it in tv.get_children():
            tv.delete(it)

        cat, sub, q = self._filters()
        where = []
        args: List[Any] = []

        if cat and cat != "(Uncategorized)":
            where.append("LOWER(COALESCE(category,'')) = LOWER(?)"); args.append(cat)
        elif cat == "(Uncategorized)":
            where.append("COALESCE(NULLIF(TRIM(category),''), '(Uncategorized)') = '(Uncategorized)'")

        if sub and sub != "(None)":
            where.append("LOWER(COALESCE(subcategory,'')) = LOWER(?)"); args.append(sub)
        elif sub == "(None)":
            where.append("COALESCE(NULLIF(TRIM(subcategory),''), '(None)') = '(None)'")

        if q:
            where.append("""LOWER(
                COALESCE(name,'') || ' ' ||
                COALESCE(brand,'') || ' ' ||
                COALESCE(category,'') || ' ' ||
                COALESCE(subcategory,'') || ' ' ||
                COALESCE(tags,'') || ' ' ||
                COALESCE(notes,'')
            ) LIKE ?""")
            args.append(f"%{q.lower()}%")

        wsql = (" WHERE " + " AND ".join(where)) if where else ""
        order_by = "ORDER BY LOWER(COALESCE(name,'')), LOWER(COALESCE(brand,''))"
        sql = f"""
            SELECT id, name, brand, category, subcategory, net_weight, unit, quantity, store, expiration, gf_flag, tags, notes
            FROM pantry
            {wsql}
            {order_by}
        """
        rows = self.db.execute(sql, args).fetchall()
        for r in rows:
            gf = _normalize_gf_flag(r["gf_flag"] or "", r["tags"] or "")
            vals = [
                r["name"] or "", r["brand"] or "",
                canonical_category(r["category"] or ""),
                canonical_subcategory(r["subcategory"] or ""),
                r["net_weight"] if r["net_weight"] is not None else "", r["unit"] or "",
                r["quantity"] if r["quantity"] is not None else "", r["store"] or "",
                r["expiration"] or "", gf, r["tags"] or "", r["notes"] or "",
            ]
            tv.insert("", "end", iid=str(r["id"]), values=vals)

        self.set_status(f"{len(rows)} item(s)")

    # ---------------- Selection / events ----------------
    def _on_pick_group(self, _event=None) -> None:
        tv = self._tree_cat
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        cat = sub = None
        if sel:
            iid = sel[0]
            if iid == "ALL":
                cat = sub = None
            elif iid.startswith("cat::"):
                cat = iid.split("::", 1)[1]
            elif iid.startswith("sub::"):
                _, c, s = iid.split("::", 2)
                cat, sub = c, s
        self._current_cat, self._current_sub = cat, sub
        self.refresh_list()

    # ---------------- CRUD ----------------
    def add_item(self) -> None:
        data = self._edit_dialog(None)
        if not data: return
        # Canonicalize before save
        data["category"]    = canonical_category(data.get("category",""))
        data["subcategory"] = canonical_subcategory(data.get("subcategory",""))
        data["gf_flag"]     = _normalize_gf_flag(data.get("gf_flag",""), data.get("tags",""))
        self.db.execute("""
            INSERT INTO pantry(name,brand,category,subcategory,net_weight,unit,quantity,store,expiration,gf_flag,tags,notes)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
        """, (data["name"], data["brand"], data["category"], data["subcategory"], data["net_weight"], data["unit"],
              data["quantity"], data["store"], data["expiration"], data["gf_flag"], data["tags"], data["notes"]))
        self.db.commit()
        self.refresh_groups()
        self.refresh_list()
        self.set_status("Item added")

    def add_by_upc(self) -> None:
        upc = simpledialog.askstring("Add by UPC", "Enter UPC:", parent=self.winfo_toplevel())
        if not upc: return
        prefill = self._resolve_upc(upc)
        data = self._edit_dialog(prefill)
        if not data: return
        data["category"]    = canonical_category(data.get("category",""))
        data["subcategory"] = canonical_subcategory(data.get("subcategory",""))
        data["gf_flag"]     = _normalize_gf_flag(data.get("gf_flag",""), data.get("tags",""))
        self.db.execute("""
            INSERT INTO pantry(name,brand,category,subcategory,net_weight,unit,quantity,store,expiration,gf_flag,tags,notes)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
        """, (data["name"], data["brand"], data["category"], data["subcategory"], data["net_weight"], data["unit"],
              data["quantity"], data["store"], data["expiration"], data["gf_flag"], data["tags"], data["notes"]))
        self.db.commit()
        self.refresh_groups()
        self.refresh_list()
        self.set_status("Item added from UPC")

    def edit_selected(self) -> None:
        tv = self._tree
        if not isinstance(tv, ttk.Treeview): return
        sel = tv.selection()
        if len(sel) != 1:
            messagebox.showinfo("Pantry", "Select one item to edit.", parent=self.winfo_toplevel()); return
        rid = int(sel[0])
        row = self.db.execute("SELECT * FROM pantry WHERE id=?", (rid,)).fetchone()
        if not row: return
        data = self._edit_dialog(row)
        if not data: return
        data["category"]    = canonical_category(data.get("category",""))
        data["subcategory"] = canonical_subcategory(data.get("subcategory",""))
        data["gf_flag"]     = _normalize_gf_flag(data.get("gf_flag",""), data.get("tags",""))
        self.db.execute("""
            UPDATE pantry SET
                name=?, brand=?, category=?, subcategory=?, net_weight=?, unit=?, quantity=?, store=?, expiration=?, gf_flag=?, tags=?, notes=?
            WHERE id=?
        """, (data["name"], data["brand"], data["category"], data["subcategory"], data["net_weight"], data["unit"],
              data["quantity"], data["store"], data["expiration"], data["gf_flag"], data["tags"], data["notes"], rid))
        self.db.commit()
        self.refresh_groups()
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
        self.db.execute(f"DELETE FROM pantry WHERE id IN ({q})", ids)
        self.db.commit()
        self.refresh_groups()
        self.refresh_list()
        self.set_status(f"Deleted {len(ids)} item(s)")

    # ---------------- Auto-tag GF ----------------
    def auto_tag_gf_selected(self) -> None:
        tv = self._tree
        if not isinstance(tv, ttk.Treeview): return
        sel = tv.selection()
        if not sel:
            messagebox.showinfo("Auto-tag GF", "Select one or more items.", parent=self.winfo_toplevel()); return

        cur = self.db.cursor()
        n = 0
        for iid in sel:
            rid = int(iid)
            r = cur.execute("SELECT id, name, brand, tags, notes FROM pantry WHERE id=?", (rid,)).fetchone()
            if not r: continue
            new_flag = "GF" if _has_gf_tag(r["tags"] or "") else _classify_gf_by_text(r["name"], r["brand"], r["tags"], r["notes"])
            cur.execute("UPDATE pantry SET gf_flag=? WHERE id=?", (new_flag, rid))
            n += 1
        self.db.commit()
        self.refresh_list()
        self.set_status(f"Auto-tagged {n} item(s)")

    # ---------------- Export (visible rows) ----------------
    def export_html_visible(self) -> None:
        tv = self._tree
        if not isinstance(tv, ttk.Treeview): return
        items = tv.get_children("")
        rows = [list(tv.item(iid, "values")) for iid in items]
        headings = [hdr for _key, hdr, _w, _a in COLS]
        export_table_html(
            path=None,
            title="Pantry (Filtered View)",
            columns=headings,
            rows=rows,
            subtitle="Generated from Celiac Culinary",
            meta={"Source": "Pantry", "Rows": len(rows)},
            open_after=True,
        )
        self.set_status(f"Exported {len(rows)} row(s) to HTML")

    # ---------------- Clean Categories (fix duplicates) ----------------
    def clean_categories(self) -> None:
        """
        One-click fix: canonicalize category/subcategory across all pantry rows.
        Trims/normalizes casing and maps synonyms to the canonical buckets.
        """
        cur = self.db.cursor()
        rows = cur.execute("SELECT id, category, subcategory FROM pantry").fetchall()
        changed = 0
        for r in rows:
            cid = int(r["id"])
            old_cat = r["category"] or ""
            old_sub = r["subcategory"] or ""
            new_cat = canonical_category(old_cat)
            new_sub = canonical_subcategory(old_sub)
            if new_cat != old_cat or new_sub != old_sub:
                cur.execute("UPDATE pantry SET category=?, subcategory=? WHERE id=?", (new_cat, new_sub, cid))
                changed += 1
        self.db.commit()
        self.refresh_groups()
        self.refresh_list()
        self.set_status(f"Cleaned categories on {changed} item(s)")

    # ---------------- edit dialog ----------------
    def _edit_dialog(self, row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        dlg = tk.Toplevel(self)
        dlg.title("Pantry Item")
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()

        frm = ttk.Frame(dlg, padding=8)
        frm.grid(row=0, column=0, sticky="nsew")
        dlg.grid_columnconfigure(0, weight=1)
        dlg.grid_rowconfigure(0, weight=1)

        def g(k, d=""):
            if row and k in row.keys(): return row[k]
            return d

        # Build combobox values from DB + known canonical list
        cats_db = [canonical_category(r[0] or "") for r in self.db.execute(
            "SELECT DISTINCT COALESCE(category,'') FROM pantry").fetchall()]
        cats = sorted({c for c in (cats_db + KNOWN_CATEGORIES) if c})
        subs_db = [canonical_subcategory(r[0] or "") for r in self.db.execute(
            "SELECT DISTINCT COALESCE(subcategory,'') FROM pantry").fetchall()]
        subs = sorted({s for s in subs_db if s})

        sv = {k: tk.StringVar(value=str(g(k, ""))) for k in ("name","brand","unit","store","expiration","tags","notes")}
        sv_cat = tk.StringVar(value=canonical_category(str(g("category",""))))
        sv_sub = tk.StringVar(value=canonical_subcategory(str(g("subcategory",""))))
        gf_opts = ["UNKNOWN","GF","SAFE","MAYBE","RISK","NGF"]
        sv_gf  = tk.StringVar(value=_normalize_gf_flag(str(g("gf_flag","")), str(g("tags",""))))

        def ffloat(x, default="0"):
            s = str(x if x not in (None,"") else default)
            try: return str(float(s))
            except Exception: return default
        sv_num = {"net_weight": tk.StringVar(value=ffloat(g("net_weight",""))),
                  "quantity":   tk.StringVar(value=ffloat(g("quantity","") or "1"))}

        r = 0
        def roww(label: str, widget: tk.Widget, col=1):
            nonlocal r
            ttk.Label(frm, text=label).grid(row=r, column=0, sticky="e", padx=(0,8), pady=(0,4))
            widget.grid(row=r, column=col, sticky="ew", pady=(0,4))
            frm.grid_columnconfigure(col, weight=1)
            r += 1

        roww("Name", ttk.Entry(frm, textvariable=sv["name"], width=40))
        roww("Brand", ttk.Entry(frm, textvariable=sv["brand"], width=30))
        roww("Category", ttk.Combobox(frm, textvariable=sv_cat, values=cats, width=20))
        roww("SubCategory", ttk.Combobox(frm, textvariable=sv_sub, values=subs, width=20))
        roww("Net.Wt", ttk.Entry(frm, textvariable=sv_num["net_weight"], width=10))
        roww("Unit", ttk.Entry(frm, textvariable=sv["unit"], width=8))
        roww("Quantity", ttk.Entry(frm, textvariable=sv_num["quantity"], width=10))
        roww("Store", ttk.Entry(frm, textvariable=sv["store"], width=20))
        roww("Expiration", ttk.Entry(frm, textvariable=sv["expiration"], width=14))
        roww("GF Flag", ttk.Combobox(frm, textvariable=sv_gf, values=gf_opts, width=10))
        roww("Tags", ttk.Entry(frm, textvariable=sv["tags"], width=40))
        roww("Notes", ttk.Entry(frm, textvariable=sv["notes"], width=60))

        out: Dict[str, Any] = {}

        def parse_float(s: str) -> float:
            s = (s or "").strip()
            if not s: return 0.0
            try:
                if "/" in s and re.match(r"^\s*\d+\s*/\s*\d+\s*$", s):
                    a, b = s.split("/", 1); return float(a)/float(b)
                return float(s)
            except Exception:
                return 0.0

        def on_save():
            name = (sv["name"].get() or "").strip()
            if not name:
                messagebox.showerror("Pantry", "Name is required.", parent=dlg); return
            out.update({
                "name": name,
                "brand": (sv["brand"].get() or "").strip(),
                "category": canonical_category(sv_cat.get()),
                "subcategory": canonical_subcategory(sv_sub.get()),
                "net_weight": parse_float(sv_num["net_weight"].get()),
                "unit": (sv["unit"].get() or "").strip(),
                "quantity": parse_float(sv_num["quantity"].get()),
                "store": (sv["store"].get() or "").strip(),
                "expiration": (sv["expiration"].get() or "").strip(),
                "gf_flag": (sv_gf.get() or "UNKNOWN").strip().upper(),
                "tags": (sv["tags"].get() or "").strip(),
                "notes": (sv["notes"].get() or "").strip(),
            })
            dlg.destroy()

        btns = ttk.Frame(dlg, padding=(8,6))
        btns.grid(row=1, column=0, sticky="e")
        ttk.Button(btns, text="Cancel", command=dlg.destroy).grid(row=0, column=0, padx=(0,6))
        ttk.Button(btns, text="Save", command=on_save).grid(row=0, column=1)

        dlg.wait_window()
        return out or None
