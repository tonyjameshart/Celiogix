# path: panels/settings_panel.py
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import csv
from typing import List, Dict, Any, Optional, Tuple

from panels.base_panel import BasePanel

# ---- small helpers ----
def _ci_map(header_row: List[str]) -> Dict[str, int]:
    """case-insensitive header -> index"""
    return {(h or "").strip().lower(): i for i, h in enumerate(header_row)}


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


def _combo_dialog(parent: tk.Widget, title: str, prompt: str, options: List[str], *, allow_new: bool = True, initial: str = "") -> Optional[str]:
    """Simple modal combobox dialog. Returns chosen string or None.
    Why: we need a picker that also allows typing a new label.
    """
    top = tk.Toplevel(parent)
    top.title(title)
    top.transient(parent.winfo_toplevel())
    top.resizable(False, False)
    top.grab_set()

    frm = ttk.Frame(top, padding=10)
    frm.grid(row=0, column=0, sticky="nsew")

    ttk.Label(frm, text=prompt).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

    var = tk.StringVar(value=initial)
    cb = ttk.Combobox(frm, textvariable=var, values=sorted(options, key=str.lower), state="normal" if allow_new else "readonly", width=40)
    cb.grid(row=1, column=0, columnspan=2, sticky="ew")
    cb.focus_set()

    result: List[str] = []

    def ok() -> None:
        val = (var.get() or "").strip()
        if not val:
            messagebox.showerror(title, "Value cannot be empty.", parent=top)
            return
        result[:] = [val]
        top.destroy()

    def cancel() -> None:
        top.destroy()

    btn_ok = ttk.Button(frm, text="OK", command=ok)
    btn_ok.grid(row=2, column=0, pady=(8, 0), sticky="e")
    btn_cancel = ttk.Button(frm, text="Cancel", command=cancel)
    btn_cancel.grid(row=2, column=1, pady=(8, 0), sticky="w")

    top.bind("<Return>", lambda e: ok())
    top.bind("<Escape>", lambda e: cancel())

    parent.wait_window(top)
    return result[0] if result else None


class SettingsPanel(BasePanel):
    """Settings with Notebook tabs: General, Import/Export, Search URLs, Categories."""

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
        t_cats = ttk.Frame(nb)

        nb.add(t_general, text="General")
        nb.add(t_io, text="Import / Export")
        nb.add(t_urls, text="Search URLs")
        nb.add(t_cats, text="Categories")

        # ---- General tab ----
        self._build_general(t_general)

        # ---- Import/Export ----
        self._build_io(t_io)

        # ---- Search URLs ----
        self._build_urls(t_urls)

        # ---- Categories (now with sub-tabs for Category + Subcategory) ----
        self._build_categories(t_cats)

    # ------------- General -------------
    def _build_general(self, parent: tk.Widget) -> None:
        box = ttk.Frame(parent, padding=10)
        box.pack(fill="both", expand=True)

        ttk.Label(box, text="Celiac Culinary – Settings", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 6))
        # show DB path if available
        db_path = ""
        try:
            db_path = getattr(self.db, "database", "") or ""
        except Exception:
            pass
        ttk.Label(box, text=f"Database: {db_path or '(in-memory or unknown)'}").pack(anchor="w")

        ttk.Separator(box).pack(fill="x", pady=10)
        ttk.Label(box, text="Theme applied.", style="Muted.TLabel").pack(anchor="w")

    # ------------- Import / Export (placeholder) -------------
    def _build_io(self, parent: tk.Widget) -> None:
        wrap = ttk.Frame(parent, padding=10)
        wrap.pack(fill="both", expand=True)
        ttk.Label(wrap, text="Import/Export tools live here.").pack(anchor="w")
        ttk.Label(wrap, text="This build focuses on the new Categories tab.", style="Muted.TLabel").pack(anchor="w")

    # ------------- Search URLs -------------
    def _ensure_search_urls_table(self) -> None:
        try:
            self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS search_urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE,
                    label TEXT,
                    enabled INTEGER
                )
                """
            )
            self.db.commit()
        except Exception:
            pass

    def _build_urls(self, parent: tk.Widget) -> None:
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        # toolbar
        bar = ttk.Frame(parent, padding=(8, 6))
        bar.grid(row=0, column=0, sticky="ew")
        ttk.Button(bar, text="Add", command=self._urls_add).pack(side="left")
        ttk.Button(bar, text="Edit", command=self._urls_edit).pack(side="left", padx=(6, 0))
        ttk.Button(bar, text="Delete", command=self._urls_delete).pack(side="left", padx=(6, 0))
        ttk.Button(bar, text="Import…", command=self._urls_import).pack(side="left", padx=(12, 0))
        ttk.Button(bar, text="Export…", command=self._urls_export).pack(side="left", padx=(6, 0))

        # table
        tv = ttk.Treeview(parent, columns=("url", "label", "enabled"), show="headings", selectmode="extended")
        tv.heading("url", text="URL")
        tv.heading("label", text="Label")
        tv.heading("enabled", text="Enabled")
        tv.column("url", width=360, anchor="w")
        tv.column("label", width=160, anchor="w")
        tv.column("enabled", width=90, anchor="center")
        tv.grid(row=1, column=0, sticky="nsew")
        self._urls_tree = tv

        vsb = ttk.Scrollbar(parent, orient="vertical", command=tv.yview)
        tv.configure(yscroll=vsb.set)
        vsb.grid(row=1, column=1, sticky="ns")

        self._urls_refresh()

    def _urls_refresh(self) -> None:
        tv = getattr(self, "_urls_tree", None)
        if not isinstance(tv, ttk.Treeview):
            return
        for it in tv.get_children():
            tv.delete(it)
        rows = self.db.execute(
            """
            SELECT id, url, COALESCE(label,'') AS label, IFNULL(enabled,1) AS enabled
              FROM search_urls
             ORDER BY LOWER(url)
            """
        ).fetchall()
        for r in rows:
            tv.insert("", "end", iid=str(r["id"]), values=[r["url"], r["label"], "yes" if r["enabled"] else "no"])
        self.set_status(f"{len(rows)} URL(s) configured")

    def _urls_add(self) -> None:
        url = simpledialog.askstring("Add URL", "Enter URL:", parent=self.winfo_toplevel())
        if not url:
            return
        label = simpledialog.askstring("Add URL", "Label (optional):", parent=self.winfo_toplevel()) or ""
        self.db.execute("INSERT OR IGNORE INTO search_urls(url, label, enabled) VALUES(?,?,1)", (url.strip(), label.strip()))
        self.db.commit()
        self._urls_refresh()

    def _urls_edit(self) -> None:
        tv = getattr(self, "_urls_tree", None)
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        if len(sel) != 1:
            messagebox.showinfo("Search URLs", "Select one item to edit.", parent=self.winfo_toplevel())
            return
        rid = int(sel[0])
        row = self.db.execute("SELECT url,label,enabled FROM search_urls WHERE id=?", (rid,)).fetchone()
        if not row:
            return
        url = simpledialog.askstring("Edit URL", "URL:", initialvalue=row["url"], parent=self.winfo_toplevel()) or row["url"]
        label = simpledialog.askstring("Edit URL", "Label:", initialvalue=row["label"], parent=self.winfo_toplevel()) or row["label"]
        enabled = messagebox.askyesno("Search URLs", "Enabled for search?", parent=self.winfo_toplevel())
        self.db.execute("UPDATE search_urls SET url=?, label=?, enabled=? WHERE id=?", (url.strip(), label.strip(), 1 if enabled else 0, rid))
        self.db.commit()
        self._urls_refresh()

    def _urls_delete(self) -> None:
        tv = getattr(self, "_urls_tree", None)
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        if not sel:
            return
        if not self.confirm_delete(len(sel)):
            return
        ids = [int(i) for i in sel]
        q = ",".join("?" for _ in ids)
        self.db.execute(f"DELETE FROM search_urls WHERE id IN ({q})", ids)
        self.db.commit()
        self._urls_refresh()

    def _urls_import(self) -> None:
        path = filedialog.askopenfilename(
            title="Import Search URLs (CSV/TXT)",
            filetypes=[("CSV/TXT", "*.csv;*.txt"), ("CSV", "*.csv"), ("Text", "*.txt"), ("All Files", "*.*")],
        )
        if not path:
            return
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
                if not rows:
                    self.warn("File appears to be empty.")
                    return
                hdr = _ci_map(rows[0])
                data = rows[1:]
                # accept columns: url, label, enabled
                for r in data:
                    url = r[hdr["url"]].strip() if "url" in hdr and hdr["url"] < len(r) else (r[0].strip() if r else "")
                    if not url:
                        continue
                    label = r[hdr["label"]].strip() if "label" in hdr and hdr["label"] < len(r) else ""
                    enabled = r[hdr["enabled"]].strip().lower() if "enabled" in hdr and hdr["enabled"] < len(r) else "1"
                    en = 0 if enabled in ("0", "no", "false", "off") else 1
                    self.db.execute(
                        """
                        INSERT INTO search_urls(url, label, enabled) VALUES(?,?,?)
                        ON CONFLICT(url) DO UPDATE SET label=excluded.label, enabled=excluded.enabled
                        """,
                        (url, label, en),
                    )
                    added += 1
            self.db.commit()
            self._urls_refresh()
            self.info(f"Imported {added} URL(s).")
        except Exception as e:
            self.error(f"Failed to import URLs:\n{e!s}")

    def _urls_export(self) -> None:
        path = filedialog.asksaveasfilename(title="Export Search URLs", defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        try:
            rows = self.db.execute("SELECT url,label,enabled FROM search_urls ORDER BY LOWER(url)").fetchall()
            with open(path, "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["url", "label", "enabled"])
                for r in rows:
                    w.writerow([r["url"], r["label"] or "", r["enabled"] or 1])
            self.info(f"Exported {len(rows)} URL(s).")
        except Exception as e:
            self.error(f"Failed to export URLs:\n{e!s}")

    # ------------- Categories (Pantry + Shopping) -------------
    def _build_categories(self, parent: tk.Widget) -> None:
        # Notebook: Categories & Subcategories
        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True)

        cat_tab = ttk.Frame(nb)
        sub_tab = ttk.Frame(nb)
        nb.add(cat_tab, text="Categories")
        nb.add(sub_tab, text="Subcategories (Pantry)")

        # Build individual tabs
        self._build_categories_tab(cat_tab)
        self._build_subcategories_tab(sub_tab)

    # ----- Category tab -----
    def _build_categories_tab(self, parent: tk.Widget) -> None:
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        bar = ttk.Frame(parent, padding=(8, 6))
        bar.grid(row=0, column=0, sticky="ew")

        ttk.Button(bar, text="Rename / Merge…", command=self._cats_rename).pack(side="left")
        ttk.Button(bar, text="Bulk Reassign…", command=self._cats_reassign).pack(side="left", padx=(6, 0))
        ttk.Button(bar, text="Delete → (Uncategorized)", command=self._cats_delete).pack(side="left", padx=(6, 0))
        ttk.Button(bar, text="Clean (fix duplicates)", command=self._cats_clean_all).pack(side="left", padx=(12, 0))
        ttk.Button(bar, text="Refresh", command=self._cats_refresh).pack(side="left", padx=(12, 0))

        cols = ("category", "pantry", "shopping", "total")
        tv = ttk.Treeview(parent, columns=cols, show="headings", selectmode="browse")
        tv.heading("category", text="Category")
        tv.heading("pantry", text="Pantry")
        tv.heading("shopping", text="Shopping")
        tv.heading("total", text="Total")
        tv.column("category", width=240, anchor="w")
        tv.column("pantry", width=80, anchor="e")
        tv.column("shopping", width=90, anchor="e")
        tv.column("total", width=80, anchor="e")
        tv.grid(row=1, column=0, sticky="nsew")
        self._cats_tree = tv

        vsb = ttk.Scrollbar(parent, orient="vertical", command=tv.yview)
        tv.configure(yscroll=vsb.set)
        vsb.grid(row=1, column=1, sticky="ns")

        self._cats_refresh()

    def _cats_selected(self) -> Optional[str]:
        tv = getattr(self, "_cats_tree", None)
        if not isinstance(tv, ttk.Treeview):
            return None
        sel = tv.selection()
        if len(sel) != 1:
            return None
        vals = tv.item(sel[0], "values")
        return str(vals[0]) if vals else None

    def _cats_collect_counts(self) -> Dict[str, Tuple[int, int]]:
        """Return {category_label: (pantry_n, shopping_n)} using canonical labels and mapping blanks to (Uncategorized)."""
        from utils.categorize import canonical_category  # lazy import to avoid cycles

        counts: Dict[str, Tuple[int, int]] = {}

        # Pantry
        for r in self.db.execute("SELECT category FROM pantry").fetchall():
            raw = (r["category"] or "").strip()
            label = canonical_category(raw)
            if not label:
                label = "(Uncategorized)"
            p, s = counts.get(label, (0, 0))
            counts[label] = (p + 1, s)

        # Shopping
        try:
            for r in self.db.execute("SELECT category FROM shopping_list").fetchall():
                raw = (r["category"] or "").strip()
                label = canonical_category(raw)
                if not label:
                    label = "(Uncategorized)"
                p, s = counts.get(label, (0, 0))
                counts[label] = (p, s + 1)
        except Exception:
            # shopping_list table might not exist in some deployments
            pass

        return counts

    def _cats_refresh(self) -> None:
        tv = getattr(self, "_cats_tree", None)
        if not isinstance(tv, ttk.Treeview):
            return
        for it in tv.get_children():
            tv.delete(it)
        counts = self._cats_collect_counts()
        total_rows = 0
        for cat in sorted(counts.keys(), key=lambda s: s.lower()):
            p, s = counts[cat]
            t = p + s
            total_rows += t
            tv.insert("", "end", values=(cat, p, s, t))
        self.set_status(f"{len(counts)} categories • {total_rows} rows across Pantry + Shopping")

    def _cats_reassign(self) -> None:
        """Move everything from the selected category to a picked/typed target category across Pantry+Shopping.
        Why: faster than rename when target already exists.
        """
        from utils.categorize import canonical_category  # lazy import

        old_label = self._cats_selected()
        if not old_label:
            messagebox.showinfo("Categories", "Select a category to reassign.", parent=self.winfo_toplevel())
            return

        # Gather choices excluding the selected label, but allow new typing.
        choices = [c for c in self._cats_collect_counts().keys() if c != old_label and c != "(Uncategorized)"]
        target = _combo_dialog(self, "Bulk Reassign", f"Move all items from '{old_label}' to:", choices, allow_new=True)
        if target is None:
            return
        target = target.strip()
        if not target:
            return
        if target == "(Uncategorized)":
            # Treat as delete → NULL
            return self._cats_delete()

        def match_row(cat_val: Optional[str]) -> bool:
            s = (cat_val or "").strip()
            if old_label == "(Uncategorized)":
                return s == ""
            return canonical_category(s) == old_label

        cur = self.db.cursor()
        # Pantry
        p_ids = [int(r["id"]) for r in cur.execute("SELECT id, category FROM pantry").fetchall() if match_row(r["category"])]
        # Shopping
        try:
            s_ids = [int(r["id"]) for r in cur.execute("SELECT id, category FROM shopping_list").fetchall() if match_row(r["category"])]
        except Exception:
            s_ids = []

        changed = 0
        if p_ids:
            qp = ",".join("?" for _ in p_ids)
            cur.execute(f"UPDATE pantry SET category=? WHERE id IN ({qp})", [target, *p_ids])
            changed += cur.rowcount if cur.rowcount is not None else 0
        if s_ids:
            qs = ",".join("?" for _ in s_ids)
            cur.execute(f"UPDATE shopping_list SET category=? WHERE id IN ({qs})", [target, *s_ids])
            changed += cur.rowcount if cur.rowcount is not None else 0
        self.db.commit()
        self._cats_refresh()
        self.info(f"Reassigned → {changed} row(s) updated.")

    def _cats_rename(self) -> None:
        from utils.categorize import canonical_category  # lazy import

        old_label = self._cats_selected()
        if not old_label:
            messagebox.showinfo("Categories", "Select a category to rename/merge.", parent=self.winfo_toplevel())
            return
        new_label = simpledialog.askstring("Rename / Merge", f"Rename '{old_label}' to:", parent=self.winfo_toplevel())
        if new_label is None:
            return
        new_label = new_label.strip()
        if not new_label:
            messagebox.showerror("Categories", "Category cannot be empty.", parent=self.winfo_toplevel())
            return
        if new_label == "(Uncategorized)":
            messagebox.showerror("Categories", "'(Uncategorized)' is a display label, not a storable name.", parent=self.winfo_toplevel())
            return

        def match_row(cat_val: Optional[str]) -> bool:
            s = (cat_val or "").strip()
            if old_label == "(Uncategorized)":
                return s == ""
            return canonical_category(s) == old_label

        cur = self.db.cursor()
        # Pantry
        p_ids = [int(r["id"]) for r in cur.execute("SELECT id, category FROM pantry").fetchall() if match_row(r["category"])]
        # Shopping
        try:
            s_ids = [int(r["id"]) for r in cur.execute("SELECT id, category FROM shopping_list").fetchall() if match_row(r["category"])]
        except Exception:
            s_ids = []

        changed = 0
        if p_ids:
            qp = ",".join("?" for _ in p_ids)
            cur.execute(f"UPDATE pantry SET category=? WHERE id IN ({qp})", [new_label, *p_ids])
            changed += cur.rowcount if cur.rowcount is not None else 0
        if s_ids:
            qs = ",".join("?" for _ in s_ids)
            cur.execute(f"UPDATE shopping_list SET category=? WHERE id IN ({qs})", [new_label, *s_ids])
            changed += cur.rowcount if cur.rowcount is not None else 0
        self.db.commit()
        self._cats_refresh()
        self.info(f"Renamed/Merged → {changed} row(s) updated.")

    def _cats_delete(self) -> None:
        from utils.categorize import canonical_category  # lazy import

        old_label = self._cats_selected()
        if not old_label:
            return
        if not self.confirm_delete(1):
            return

        def match_row(cat_val: Optional[str]) -> bool:
            s = (cat_val or "").strip()
            if old_label == "(Uncategorized)":
                return s == ""
            return canonical_category(s) == old_label

        cur = self.db.cursor()
        # Pantry
        p_ids = [int(r["id"]) for r in cur.execute("SELECT id, category FROM pantry").fetchall() if match_row(r["category"])]
        # Shopping
        try:
            s_ids = [int(r["id"]) for r in cur.execute("SELECT id, category FROM shopping_list").fetchall() if match_row(r["category"])]
        except Exception:
            s_ids = []

        changed = 0
        if p_ids:
            qp = ",".join("?" for _ in p_ids)
            cur.execute(f"UPDATE pantry SET category=NULL WHERE id IN ({qp})", p_ids)
            changed += cur.rowcount if cur.rowcount is not None else 0
        if s_ids:
            qs = ",".join("?" for _ in s_ids)
            cur.execute(f"UPDATE shopping_list SET category=NULL WHERE id IN ({qs})", s_ids)
            changed += cur.rowcount if cur.rowcount is not None else 0
        self.db.commit()
        self._cats_refresh()
        self.info(f"Deleted category label → {changed} row(s) set to (Uncategorized).")

    def _cats_clean_all(self) -> None:
        """Canonicalize category/subcategory across Pantry; canonicalize category across Shopping."""
        from utils.categorize import canonical_category, canonical_subcategory  # lazy import

        cur = self.db.cursor()
        changed = 0

        # Pantry: category + subcategory
        try:
            prows = cur.execute("SELECT id, category, subcategory FROM pantry").fetchall()
            for r in prows:
                cid = int(r["id"])
                old_cat = r["category"] or ""
                old_sub = r["subcategory"] or ""
                new_cat = canonical_category(old_cat)
                new_sub = canonical_subcategory(old_sub)
                if new_cat != old_cat or new_sub != old_sub:
                    cur.execute("UPDATE pantry SET category=?, subcategory=? WHERE id=?", (new_cat, new_sub, cid))
                    changed += 1
        except Exception:
            pass

        # Shopping: category only
        try:
            srows = cur.execute("SELECT id, category FROM shopping_list").fetchall()
            for r in srows:
                cid = int(r["id"])
                old_cat = r["category"] or ""
                new_cat = canonical_category(old_cat)
                if new_cat != old_cat:
                    cur.execute("UPDATE shopping_list SET category=? WHERE id=?", (new_cat, cid))
                    changed += 1
        except Exception:
            pass

        self.db.commit()
        self._cats_refresh()
        self.info(f"Cleaned categories on {changed} row(s).")

    # ----- Subcategory tab (Pantry only) -----
    def _build_subcategories_tab(self, parent: tk.Widget) -> None:
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        bar = ttk.Frame(parent, padding=(8, 6))
        bar.grid(row=0, column=0, sticky="ew")

        ttk.Button(bar, text="Rename / Merge…", command=self._subcats_rename).pack(side="left")
        ttk.Button(bar, text="Bulk Reassign…", command=self._subcats_reassign).pack(side="left", padx=(6, 0))
        ttk.Button(bar, text="Delete → (Uncategorized)", command=self._subcats_delete).pack(side="left", padx=(6, 0))
        ttk.Button(bar, text="Clean (canonicalize)", command=self._subcats_clean).pack(side="left", padx=(12, 0))
        ttk.Button(bar, text="Refresh", command=self._subcats_refresh).pack(side="left", padx=(12, 0))

        cols = ("subcategory", "pantry")
        tv = ttk.Treeview(parent, columns=cols, show="headings", selectmode="browse")
        tv.heading("subcategory", text="Subcategory")
        tv.heading("pantry", text="Pantry")
        tv.column("subcategory", width=260, anchor="w")
        tv.column("pantry", width=90, anchor="e")
        tv.grid(row=1, column=0, sticky="nsew")
        self._subcats_tree = tv

        vsb = ttk.Scrollbar(parent, orient="vertical", command=tv.yview)
        tv.configure(yscroll=vsb.set)
        vsb.grid(row=1, column=1, sticky="ns")

        self._subcats_refresh()

    def _subcats_selected(self) -> Optional[str]:
        tv = getattr(self, "_subcats_tree", None)
        if not isinstance(tv, ttk.Treeview):
            return None
        sel = tv.selection()
        if len(sel) != 1:
            return None
        vals = tv.item(sel[0], "values")
        return str(vals[0]) if vals else None

    def _subcats_collect_counts(self) -> Dict[str, int]:
        from utils.categorize import canonical_subcategory  # lazy import
        counts: Dict[str, int] = {}
        try:
            for r in self.db.execute("SELECT subcategory FROM pantry").fetchall():
                raw = (r["subcategory"] or "").strip()
                label = canonical_subcategory(raw)
                if not label:
                    label = "(Uncategorized)"
                counts[label] = counts.get(label, 0) + 1
        except Exception:
            pass
        return counts

    def _subcats_refresh(self) -> None:
        tv = getattr(self, "_subcats_tree", None)
        if not isinstance(tv, ttk.Treeview):
            return
        for it in tv.get_children():
            tv.delete(it)
        counts = self._subcats_collect_counts()
        total = 0
        for sub in sorted(counts.keys(), key=lambda s: s.lower()):
            n = counts[sub]
            total += n
            tv.insert("", "end", values=(sub, n))
        self.set_status(f"{len(counts)} subcategories • {total} pantry rows")

    def _subcats_reassign(self) -> None:
        from utils.categorize import canonical_subcategory  # lazy import

        old_label = self._subcats_selected()
        if not old_label:
            messagebox.showinfo("Subcategories", "Select a subcategory to reassign.", parent=self.winfo_toplevel())
            return

        choices = [c for c in self._subcats_collect_counts().keys() if c != old_label and c != "(Uncategorized)"]
        target = _combo_dialog(self, "Bulk Reassign Subcategory", f"Move all items from '{old_label}' to:", choices, allow_new=True)
        if target is None:
            return
        target = target.strip()
        if not target:
            return
        if target == "(Uncategorized)":
            # set to NULL
            return self._subcats_delete()

        def match_row(sub_val: Optional[str]) -> bool:
            s = (sub_val or "").strip()
            if old_label == "(Uncategorized)":
                return s == ""
            return canonical_subcategory(s) == old_label

        cur = self.db.cursor()
        ids = [int(r["id"]) for r in cur.execute("SELECT id, subcategory FROM pantry").fetchall() if match_row(r["subcategory"])]
        changed = 0
        if ids:
            q = ",".join("?" for _ in ids)
            cur.execute(f"UPDATE pantry SET subcategory=? WHERE id IN ({q})", [target, *ids])
            changed = cur.rowcount if cur.rowcount is not None else len(ids)
        self.db.commit()
        self._subcats_refresh()
        self.info(f"Reassigned subcategory → {changed} row(s) updated.")

    def _subcats_rename(self) -> None:
        from utils.categorize import canonical_subcategory  # lazy import

        old_label = self._subcats_selected()
        if not old_label:
            messagebox.showinfo("Subcategories", "Select a subcategory to rename/merge.", parent=self.winfo_toplevel())
            return
        new_label = simpledialog.askstring("Rename / Merge Subcategory", f"Rename '{old_label}' to:", parent=self.winfo_toplevel())
        if new_label is None:
            return
        new_label = new_label.strip()
        if not new_label:
            messagebox.showerror("Subcategories", "Subcategory cannot be empty.", parent=self.winfo_toplevel())
            return
        if new_label == "(Uncategorized)":
            messagebox.showerror("Subcategories", "'(Uncategorized)' is a display label, not a storable name.", parent=self.winfo_toplevel())
            return

        def match_row(sub_val: Optional[str]) -> bool:
            s = (sub_val or "").strip()
            if old_label == "(Uncategorized)":
                return s == ""
            return canonical_subcategory(s) == old_label

        cur = self.db.cursor()
        ids = [int(r["id"]) for r in cur.execute("SELECT id, subcategory FROM pantry").fetchall() if match_row(r["subcategory"])]
        changed = 0
        if ids:
            q = ",".join("?" for _ in ids)
            cur.execute(f"UPDATE pantry SET subcategory=? WHERE id IN ({q})", [new_label, *ids])
            changed = cur.rowcount if cur.rowcount is not None else len(ids)
        self.db.commit()
        self._subcats_refresh()
        self.info(f"Renamed/Merged subcategory → {changed} row(s) updated.")

    def _subcats_delete(self) -> None:
        from utils.categorize import canonical_subcategory  # lazy import

        old_label = self._subcats_selected()
        if not old_label:
            return
        if not self.confirm_delete(1):
            return

        def match_row(sub_val: Optional[str]) -> bool:
            s = (sub_val or "").strip()
            if old_label == "(Uncategorized)":
                return s == ""
            return canonical_subcategory(s) == old_label

        cur = self.db.cursor()
        ids = [int(r["id"]) for r in cur.execute("SELECT id, subcategory FROM pantry").fetchall() if match_row(r["subcategory"])]
        changed = 0
        if ids:
            q = ",".join("?" for _ in ids)
            cur.execute(f"UPDATE pantry SET subcategory=NULL WHERE id IN ({q})", ids)
            changed = cur.rowcount if cur.rowcount is not None else len(ids)
        self.db.commit()
        self._subcats_refresh()
        self.info(f"Deleted subcategory label → {changed} row(s) set to (Uncategorized).")

    def _subcats_clean(self) -> None:
        from utils.categorize import canonical_subcategory  # lazy import

        cur = self.db.cursor()
        changed = 0
        try:
            rows = cur.execute("SELECT id, subcategory FROM pantry").fetchall()
            for r in rows:
                cid = int(r["id"])
                old = r["subcategory"] or ""
                new = canonical_subcategory(old)
                if new != old:
                    cur.execute("UPDATE pantry SET subcategory=? WHERE id=?", (new, cid))
                    changed += 1
        except Exception:
            pass
        self.db.commit()
        self._subcats_refresh()
        self.info(f"Cleaned subcategories on {changed} row(s).")
