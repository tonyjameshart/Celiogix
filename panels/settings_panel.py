# path: panels/settings_panel.py
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import csv
from typing import List, Dict, Any, Optional

from panels.base_panel import BasePanel

# ---- small helpers ----
def _ci_map(header_row: List[str]) -> Dict[str, int]:
    """case-insensitive header -> index"""
    return { (h or "").strip().lower(): i for i, h in enumerate(header_row) }

def _read_csv_rows(path: str) -> List[List[str]]:
    rows: List[List[str]] = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        sniffer = csv.Sniffer()
        content = f.read()
        f.seek(0)
        dialect = sniffer.sniff(content[:4096]) if content else csv.excel
        reader = csv.reader(f, dialect)
        for r in reader:
            if not any(cell.strip() for cell in r):
                continue
            rows.append(r)
    return rows

class SettingsPanel(BasePanel):
    """Settings with Notebook tabs: General, Import/Export, Search URLs."""
    def __init__(self, master, app, **kw):
        super().__init__(master, app, **kw)

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

        nb.add(t_general, text="General")
        nb.add(t_io, text="Import / Export")
        nb.add(t_urls, text="Search URLs")

        # ---- General tab ----
        self._build_general(t_general)

        # ---- Import/Export tab ----
        self._build_io(t_io)

        # ---- Search URLs tab ----
        self._build_urls(t_urls)

    # ------------- General -------------
    def _build_general(self, parent: tk.Widget) -> None:
        box = ttk.Frame(parent, padding=10)
        box.pack(fill="both", expand=True)

        ttk.Label(box, text="Celiac Culinary – Settings", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0,6))
        # show DB path if available
        db_path = ""
        try:
            db_path = getattr(self.db, "database", "") or ""
        except Exception:
            pass
        ttk.Label(box, text=f"Database: {db_path or '(in-memory or unknown)'}").pack(anchor="w")

        ttk.Separator(box).pack(fill="x", pady=10)
        ttk.Label(box, text="Theme applied.", style="Muted.TLabel").pack(anchor="w")

    # ------------- Import / Export -------------
    def _build_io(self, parent: tk.Widget) -> None:
        pad = dict(padx=10, pady=6)
        colw = (0,1)
        parent.columnconfigure(1, weight=1)

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

    # ------------- Search URLs tab -------------
    def _build_urls(self, parent: tk.Widget) -> None:
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        top = ttk.Frame(parent, padding=(10,8))
        top.grid(row=0, column=0, sticky="ew")
        ttk.Label(top, text="Sites to search when importing recipes:", font=("Segoe UI", 10, "bold")).pack(side="left")
        ttk.Button(top, text="Import (CSV/TXT)", command=self._urls_import).pack(side="left", padx=(12,0))
        ttk.Button(top, text="Export CSV", command=self._urls_export).pack(side="left", padx=(6,0))
        ttk.Button(top, text="Add", command=self._urls_add).pack(side="left", padx=(12,0))
        ttk.Button(top, text="Edit", command=self._urls_edit).pack(side="left", padx=(6,0))
        ttk.Button(top, text="Delete", command=self._urls_delete).pack(side="left", padx=(6,0))

        wrap = ttk.Frame(parent, padding=(10,0))
        wrap.grid(row=1, column=0, sticky="nsew")
        wrap.grid_rowconfigure(0, weight=1)
        wrap.grid_columnconfigure(0, weight=1)

        tv = ttk.Treeview(wrap, columns=("url","label","enabled"), show="headings", selectmode="extended")
        tv.heading("url", text="URL")
        tv.heading("label", text="Label")
        tv.heading("enabled", text="Enabled")
        tv.column("url", width=520, anchor="w")
        tv.column("label", width=220, anchor="w")
        tv.column("enabled", width=80, anchor="center")
        tv.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(wrap, orient="vertical", command=tv.yview)
        tv.configure(yscroll=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns")

        self._urls_tree = tv  # save
        self._urls_refresh()

        # right-click menu
        menu = tk.Menu(parent, tearoff=0)
        menu.add_command(label="Add", command=self._urls_add)
        menu.add_command(label="Edit", command=self._urls_edit)
        menu.add_command(label="Delete", command=self._urls_delete)
        def popup(e):
            try: menu.tk_popup(e.x_root, e.y_root)
            finally: menu.grab_release()
        tv.bind("<Button-3>", popup)
        tv.bind("<Double-1>", lambda e: self._urls_edit())

    # ------------- DB bootstrap -------------
    def _ensure_search_urls_table(self) -> None:
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS search_urls(
                id INTEGER PRIMARY KEY,
                url TEXT UNIQUE,
                label TEXT,
                enabled INTEGER DEFAULT 1
            )
        """)
        self.db.commit()

    # ------------- Pantry Import/Export -------------
    def _import_pantry_csv(self) -> None:
        path = filedialog.askopenfilename(
            title="Import Pantry CSV",
            filetypes=[("CSV","*.csv"), ("All Files","*.*")]
        )
        if not path: return
        try:
            rows = _read_csv_rows(path)
            if not rows:
                self.warn("File appears to be empty."); return
            hdr = _ci_map(rows[0]); data = rows[1:]
            # expected headers (case-insensitive):
            # name, brand, category, subcategory, net.wt, unit, quantity, store, expiration, gf_flag, tags, notes
            def get(row, key, default=""):
                i = hdr.get(key)
                return (row[i].strip() if (i is not None and i < len(row)) else default)

            n = 0
            for r in data:
                name = get(r, "name")
                if not name: continue
                brand = get(r, "brand")
                category = get(r, "category")
                subcat = get(r, "subcategory")
                net_wt = get(r, "net.wt") or get(r, "net wt") or get(r, "net_wt") or "0"
                unit    = get(r, "unit")
                quantity= get(r, "quantity") or "0"
                store   = get(r, "store")
                exp     = get(r, "expiration")
                gf      = (get(r, "gf_flag") or "UNKNOWN").upper()
                tags    = get(r, "tags")
                notes   = get(r, "notes")
                try:
                    self.db.execute("""
                        INSERT INTO pantry(name,brand,category,subcategory,net_weight,unit,quantity,store,expiration,gf_flag,tags,notes)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                    """, (name,brand,category,subcat,float(net_wt or 0),unit,float(quantity or 0),store,exp,gf,tags,notes))
                    n += 1
                except Exception:
                    # try update if exists (name+brand)
                    self.db.execute("""
                        UPDATE pantry
                           SET category=?, subcategory=?, net_weight=?, unit=?, quantity=?, store=?, expiration=?, gf_flag=?, tags=?, notes=?
                         WHERE LOWER(COALESCE(name,''))=LOWER(?) AND LOWER(COALESCE(brand,''))=LOWER(?)
                    """, (category,subcat,float(net_wt or 0),unit,float(quantity or 0),store,exp,gf,tags,notes,name,brand))
                    n += 1
            self.db.commit()
            self.info(f"Imported/updated {n} pantry item(s).")
        except Exception as e:
            self.error(f"Failed to import pantry CSV:\n{e!s}")

    def _export_pantry_csv(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Export Pantry CSV",
            defaultextension=".csv",
            filetypes=[("CSV","*.csv")]
        )
        if not path: return
        try:
            rows = self.db.execute("""
                SELECT name, brand, category, subcategory, IFNULL(net_weight,0) AS "Net.Wt",
                       unit, IFNULL(quantity,0) AS quantity, store, expiration, gf_flag, tags, notes
                FROM pantry
                ORDER BY LOWER(name), LOWER(brand)
            """).fetchall()
            with open(path, "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["name","brand","category","subcategory","Net.Wt","unit","quantity","store","expiration","gf_flag","tags","notes"])
                for r in rows:
                    w.writerow([r["name"],r["brand"],r["category"],r["subcategory"],r["Net.Wt"],r["unit"],r["quantity"],
                                r["store"],r["expiration"],r["gf_flag"],r["tags"],r["notes"]])
            self.info(f"Exported {len(rows)} pantry row(s).")
        except Exception as e:
            self.error(f"Failed to export pantry CSV:\n{e!s}")

    # ------------- Cookbook Import/Export -------------
    def _import_recipes_csv(self) -> None:
        path = filedialog.askopenfilename(
            title="Import Recipes CSV",
            filetypes=[("CSV","*.csv"), ("All Files","*.*")]
        )
        if not path: return
        try:
            rows = _read_csv_rows(path)
            if not rows: self.warn("File appears to be empty."); return
            hdr = _ci_map(rows[0]); data = rows[1:]
            def get(row, key, default=""):
                i = hdr.get(key)
                return (row[i].strip() if (i is not None and i < len(row)) else default)
            n = 0
            for r in data:
                title = get(r, "title")
                if not title: continue
                source = get(r, "source")
                url    = get(r, "url")
                tags   = get(r, "tags")
                ingredients = get(r, "ingredients")
                instructions= get(r, "instructions")
                rating = float(get(r, "rating", "0") or 0)
                self.db.execute("""
                    INSERT INTO recipes(title, source, url, tags, ingredients, instructions, rating)
                    VALUES(?,?,?,?,?,?,?)
                    ON CONFLICT(url) DO UPDATE SET
                        title=excluded.title, source=excluded.source, tags=excluded.tags,
                        ingredients=excluded.ingredients, instructions=excluded.instructions, rating=excluded.rating
                """, (title,source,url,tags,ingredients,instructions,rating))
                n += 1
            self.db.commit()
            self.info(f"Imported/updated {n} recipe(s).")
        except Exception as e:
            self.error(f"Failed to import recipes CSV:\n{e!s}")

    def _export_recipes_csv(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Export Recipes CSV",
            defaultextension=".csv",
            filetypes=[("CSV","*.csv")]
        )
        if not path: return
        try:
            rows = self.db.execute("""
                SELECT title, source, url, tags, ingredients, instructions, IFNULL(rating,0) AS rating
                FROM recipes
                ORDER BY LOWER(title)
            """).fetchall()
            with open(path, "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["title","source","url","tags","ingredients","instructions","rating"])
                for r in rows:
                    w.writerow([r["title"],r["source"],r["url"],r["tags"],r["ingredients"],r["instructions"],r["rating"]])
            self.info(f"Exported {len(rows)} recipe(s).")
        except Exception as e:
            self.error(f"Failed to export recipes CSV:\n{e!s}")

    # ------------- Shopping Import/Export -------------
    def _import_shopping_csv(self) -> None:
        path = filedialog.askopenfilename(
            title="Import Shopping CSV",
            filetypes=[("CSV","*.csv"), ("All Files","*.*")]
        )
        if not path: return
        try:
            rows = _read_csv_rows(path)
            if not rows: self.warn("File appears to be empty."); return
            hdr = _ci_map(rows[0]); data = rows[1:]
            def get(row, key, default=""):
                i = hdr.get(key)
                return (row[i].strip() if (i is not None and i < len(row)) else default)
            n = 0
            for r in data:
                name = get(r, "name")
                if not name: continue
                brand = get(r, "brand")
                category = get(r, "category")
                store = get(r, "store")
                notes = get(r, "notes")
                net_weight = float(get(r, "net_weight", "0") or get(r, "net wt", "0") or 0)
                thresh = float(get(r, "thresh", "0") or 0)
                self.db.execute("""
                    INSERT INTO shopping_list(name, brand, category, net_weight, thresh, store, notes)
                    VALUES(?,?,?,?,?,?,?)
                """, (name,brand,category,net_weight,thresh,store,notes))
                n += 1
            self.db.commit()
            self.info(f"Imported {n} shopping item(s).")
        except Exception as e:
            self.error(f"Failed to import shopping CSV:\n{e!s}")

    def _export_shopping_csv(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Export Shopping CSV",
            defaultextension=".csv",
            filetypes=[("CSV","*.csv")]
        )
        if not path: return
        try:
            rows = self.db.execute("""
                SELECT name, brand, category, IFNULL(net_weight,0) AS net_weight,
                       IFNULL(thresh,0) AS thresh, store, notes
                  FROM shopping_list
                 ORDER BY LOWER(name), LOWER(brand)
            """).fetchall()
            with open(path, "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["name","brand","category","net_weight","thresh","store","notes"])
                for r in rows:
                    w.writerow([r["name"], r["brand"], r["category"], r["net_weight"], r["thresh"], r["store"], r["notes"]])
            self.info(f"Exported {len(rows)} shopping row(s).")
        except Exception as e:
            self.error(f"Failed to export shopping CSV:\n{e!s}")

    # ------------- Bulk UPC import -------------
    def _import_upcs_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Import UPCs (CSV/TXT)",
            filetypes=[("CSV/TXT","*.csv;*.txt"), ("CSV","*.csv"), ("Text","*.txt"), ("All Files","*.*")]
        )
        if not path: return
        upcs: List[str] = []
        try:
            if path.lower().endswith(".txt"):
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        s = "".join(ch for ch in line if ch.isdigit())
                        if s: upcs.append(s)
            else:
                rows = _read_csv_rows(path)
                if rows:
                    hdr = _ci_map(rows[0])
                    if "upc" in hdr:
                        for r in rows[1:]:
                            v = r[hdr["upc"]] if hdr["upc"] < len(r) else ""
                            v = "".join(ch for ch in v if ch.isdigit())
                            if v: upcs.append(v)
                    else:
                        # first column fallback
                        for r in rows:
                            s = "".join(ch for ch in (r[0] if r else "") if ch.isdigit())
                            if s: upcs.append(s)
            upcs = [u for u in upcs if u]
            if not upcs:
                self.warn("No UPCs found.")
                return
        except Exception as e:
            self.error(f"Failed to read file:\n{e!s}")
            return

        added = updated = 0
        for upc in upcs:
            data = self._resolve_upc(upc)
            if not data.get("name"):
                continue
            # try update existing by (name,brand), else insert
            row = self.db.execute("""
                SELECT id FROM pantry
                 WHERE LOWER(COALESCE(name,''))=LOWER(?) AND LOWER(COALESCE(brand,''))=LOWER(?)
                 LIMIT 1
            """, (data["name"], data["brand"])).fetchone()
            if row:
                self.db.execute("""
                    UPDATE pantry SET category=?, subcategory=?, net_weight=?, unit=?, quantity=IFNULL(quantity,0)+?
                                   , store=?, notes=?, tags=?, gf_flag=?
                     WHERE id=?
                """, (data["category"], data["subcategory"], data["net_weight"], data["unit"], 1.0,
                      data["store"], data["notes"], data["tags"], data["gf_flag"], row["id"]))
                updated += 1
            else:
                self.db.execute("""
                    INSERT INTO pantry(name,brand,category,subcategory,net_weight,unit,quantity,store,expiration,gf_flag,tags,notes)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                """, (data["name"], data["brand"], data["category"], data["subcategory"], data["net_weight"],
                      data["unit"], data["quantity"] or 1.0, data["store"], data["expiration"], data["gf_flag"], data["tags"], data["notes"]))
                added += 1
        self.db.commit()
        self.info(f"UPCs processed → added: {added}, updated: {updated}")

    def _resolve_upc(self, upc: str) -> Dict[str, Any]:
        """Lightweight resolver—mirrors PantryPanel logic so Settings can bulk-import."""
        from utils.categorize import canonical_category, canonical_subcategory
        import re
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

        # normalize
        name  = str(data.get("name")  or data.get("title") or data.get("product") or f"Item {upc}").strip()
        brand = str(data.get("brand") or data.get("manufacturer") or "").strip()
        cat   = canonical_category(str(data.get("category") or ""))
        sub   = canonical_subcategory(str(data.get("subcategory") or ""))
        unit  = str(data.get("unit") or "").strip()
        tags  = str(data.get("tags") or "").strip()
        notes = str(data.get("notes") or "").strip()

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

        # GF hint passthrough
        if data.get("gf") is True or str(data.get("gf_flag","")).upper() == "GF":
            if "GF" not in [t.strip().upper() for t in re.split(r"[;,]\s*|\s+", tags) if t.strip()]:
                tags = (tags + "; GF").strip("; ").strip()
        gf_flag = (str(data.get("gf_flag") or "UNKNOWN").upper())

        return {
            "name": name, "brand": brand, "category": cat, "subcategory": sub,
            "net_weight": net_wt, "unit": unit, "quantity": qty,
            "store": "", "expiration": "", "gf_flag": gf_flag, "tags": tags, "notes": notes
        }

    # ------------- URLs tab actions -------------
    def _urls_refresh(self) -> None:
        tv = getattr(self, "_urls_tree", None)
        if not isinstance(tv, ttk.Treeview): return
        for it in tv.get_children(): tv.delete(it)
        rows = self.db.execute("""
            SELECT id, url, COALESCE(label,'') AS label, IFNULL(enabled,1) AS enabled
              FROM search_urls
             ORDER BY LOWER(url)
        """).fetchall()
        for r in rows:
            tv.insert("", "end", iid=str(r["id"]), values=[r["url"], r["label"], "yes" if r["enabled"] else "no"])
        self.set_status(f"{len(rows)} URL(s) configured")

    def _urls_add(self) -> None:
        url = simpledialog.askstring("Add URL", "Enter URL:", parent=self.winfo_toplevel())
        if not url: return
        label = simpledialog.askstring("Add URL", "Label (optional):", parent=self.winfo_toplevel()) or ""
        self.db.execute("INSERT OR IGNORE INTO search_urls(url, label, enabled) VALUES(?,?,1)", (url.strip(), label.strip()))
        self.db.commit()
        self._urls_refresh()

    def _urls_edit(self) -> None:
        tv = getattr(self, "_urls_tree", None)
        if not isinstance(tv, ttk.Treeview): return
        sel = tv.selection()
        if len(sel) != 1:
            messagebox.showinfo("Search URLs", "Select one item to edit.", parent=self.winfo_toplevel()); return
        rid = int(sel[0])
        row = self.db.execute("SELECT url,label,enabled FROM search_urls WHERE id=?", (rid,)).fetchone()
        if not row: return
        url = simpledialog.askstring("Edit URL", "URL:", initialvalue=row["url"], parent=self.winfo_toplevel()) or row["url"]
        label = simpledialog.askstring("Edit URL", "Label:", initialvalue=row["label"], parent=self.winfo_toplevel()) or row["label"]
        enabled = messagebox.askyesno("Search URLs", "Enabled for search?", parent=self.winfo_toplevel())  # simple toggle
        self.db.execute("UPDATE search_urls SET url=?, label=?, enabled=? WHERE id=?", (url.strip(), label.strip(), 1 if enabled else 0, rid))
        self.db.commit()
        self._urls_refresh()

    def _urls_delete(self) -> None:
        tv = getattr(self, "_urls_tree", None)
        if not isinstance(tv, ttk.Treeview): return
        sel = tv.selection()
        if not sel: return
        if not self.confirm_delete(len(sel)): return
        ids = [int(i) for i in sel]
        q = ",".join("?" for _ in ids)
        self.db.execute(f"DELETE FROM search_urls WHERE id IN ({q})", ids)
        self.db.commit()
        self._urls_refresh()

    def _urls_import(self) -> None:
        path = filedialog.askopenfilename(
            title="Import Search URLs (CSV/TXT)",
            filetypes=[("CSV/TXT","*.csv;*.txt"), ("CSV","*.csv"), ("Text","*.txt"), ("All Files","*.*")]
        )
        if not path: return
        added = 0
        try:
            if path.lower().endswith(".txt"):
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        s = line.strip()
                        if s:
                            self.db.execute("INSERT OR IGNORE INTO search_urls(url, enabled) VALUES(?,1)", (s,))
                            added += 1
            else:
                rows = _read_csv_rows(path)
                if not rows: self.warn("File appears to be empty."); return
                hdr = _ci_map(rows[0]); data = rows[1:]
                # accept columns: url, label, enabled
                for r in data:
                    url = r[hdr["url"]].strip() if "url" in hdr and hdr["url"] < len(r) else (r[0].strip() if r else "")
                    if not url: continue
                    label = r[hdr["label"]].strip() if "label" in hdr and hdr["label"] < len(r) else ""
                    enabled = r[hdr["enabled"]].strip().lower() if "enabled" in hdr and hdr["enabled"] < len(r) else "1"
                    en = 0 if enabled in ("0","no","false","off") else 1
                    self.db.execute("""
                        INSERT INTO search_urls(url, label, enabled)
                        VALUES(?,?,?)
                        ON CONFLICT(url) DO UPDATE SET label=excluded.label, enabled=excluded.enabled
                    """, (url, label, en))
                    added += 1
            self.db.commit()
            self._urls_refresh()
            self.info(f"Imported {added} URL(s).")
        except Exception as e:
            self.error(f"Failed to import URLs:\n{e!s}")

    def _urls_export(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Export Search URLs",
            defaultextension=".csv",
            filetypes=[("CSV","*.csv")]
        )
        if not path: return
        try:
            rows = self.db.execute("SELECT url,label,enabled FROM search_urls ORDER BY LOWER(url)").fetchall()
            with open(path, "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["url","label","enabled"])
                for r in rows:
                    w.writerow([r["url"], r["label"] or "", r["enabled"] or 1])
            self.info(f"Exported {len(rows)} URL(s).")
        except Exception as e:
            self.error(f"Failed to export URLs:\n{e!s}")
