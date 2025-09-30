# path: panels/health_log_panel.py
from __future__ import annotations

import datetime as _dt
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from panels.base_panel import BasePanel
from utils.export import export_table_html

GI_SYMPTOMS = ["Abdominal pain", "Bloating", "Diarrhea", "Constipation", "Nausea", "Vomiting"]
NEURO_SYMPTOMS = ["Brain fog", "Headache", "Dizziness"]
SKIN_SYMPTOMS = ["Dermatitis herpetiformis", "Itching", "Rash"]
SYSTEMIC_SYMPTOMS = ["Fatigue", "Joint pain"]

RISK_OPTS = ["none", "low", "med", "high"]
MEALS = ["Breakfast", "Lunch", "Dinner", "Snack", "Other"]

# Table columns
COLS = [
    ("date", "Date", 100, "c"),
    ("time", "Time", 70, "c"),
    ("meal", "Meal", 90, "w"),
    ("items", "Items", 260, "w"),
    ("risk", "Risk", 60, "c"),
    ("severity", "Sev", 60, "c"),
    ("stool", "BM", 50, "c"),  # shows numeric code for compactness
    ("recipe", "Recipe", 200, "w"),
    ("symptoms", "Symptoms", 260, "w"),
    ("notes", "Notes", 280, "w"),
]

# ---- Bristol helpers ----
BRS_OPTIONS: list[tuple[int, str]] = [
    (0, "0 – not recorded"),
    (1, "1 – separate hard lumps (constipation)"),
    (2, "2 – sausage-shaped but lumpy"),
    (3, "3 – sausage with cracks"),
    (4, "4 – smooth, soft sausage/snake (normal)"),
    (5, "5 – soft blobs, clear edges (low fiber)"),
    (6, "6 – fluffy pieces, ragged edges (mushy)"),
    (7, "7 – watery, no solid pieces (diarrhea)"),
]
BRS_VALUES = [label for _n, label in BRS_OPTIONS]


def bristol_label(n: int) -> str:
    for code, label in BRS_OPTIONS:
        if int(code) == int(n):
            return label
    return BRS_OPTIONS[0][1]


def bristol_code(label: str) -> int:
    if not label:
        return 0
    s = str(label).strip()
    try:
        return int(s.split("–", 1)[0].strip())
    except Exception:
        pass
    for code, lab in BRS_OPTIONS:
        if lab == label:
            return code
    return 0


def _today() -> str:
    return _dt.date.today().isoformat()


def _now_hhmm() -> str:
    t = _dt.datetime.now().time()
    return f"{t.hour:02d}:{t.minute:02d}"


class HealthLogPanel(BasePanel):
    """
    Health Log: Add/Edit form + filterable table + HTML export.
    Uses table `health_log(date,time,meal,items,risk,onset_min,severity,stool,recipe,symptoms,notes)`.
    """

    def __init__(self, master, app, **kw):
        # form vars
        self.var_date = tk.StringVar(value=_today())
        self.var_time = tk.StringVar(value=_now_hhmm())
        self.var_meal = tk.StringVar(value="Dinner")
        self.var_recipe = tk.StringVar(value="")
        self.var_items = tk.StringVar(value="")
        self.var_risk = tk.StringVar(value="none")
        self.var_sev = tk.IntVar(value=0)
        self.var_onset = tk.IntVar(value=0)
        # store the descriptive label in the UI; convert to int on save
        self.var_bristol_label = tk.StringVar(value=BRS_OPTIONS[0][1])
        self.var_notes = tk.StringVar(value="")

        # symptoms vars
        self.sym_vars: dict[str, tk.BooleanVar] = {}

        # filter vars
        self.f_from = tk.StringVar(value=(_dt.date.today() - _dt.timedelta(days=6)).isoformat())
        self.f_to = tk.StringVar(value=_today())
        self.f_minsev = tk.IntVar(value=0)
        self.f_risk = tk.StringVar(value="any")
        self.f_kw = tk.StringVar(value="")

        self._tree: ttk.Treeview | None = None
        super().__init__(master, app, **kw)

    # ---------- UI ----------
    def build(self) -> None:
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Add/Edit frame (top)
        addf = ttk.LabelFrame(self, text="Add / Edit Entry")
        addf.grid(row=0, column=0, sticky="ew", padx=6, pady=(4, 6))
        addf.grid_columnconfigure(8, weight=1)

        r = 0
        ttk.Label(addf, text="Date").grid(row=r, column=0, padx=(6, 6), pady=4, sticky="e")
        ttk.Entry(addf, textvariable=self.var_date, width=12).grid(
            row=r, column=1, pady=4, sticky="w"
        )

        ttk.Label(addf, text="Time (HH:MM)").grid(row=r, column=2, padx=(12, 6), pady=4, sticky="e")
        ttk.Entry(addf, textvariable=self.var_time, width=8).grid(
            row=r, column=3, pady=4, sticky="w"
        )

        ttk.Label(addf, text="Meal").grid(row=r, column=4, padx=(12, 6), pady=4, sticky="e")
        ttk.Combobox(
            addf,
            textvariable=self.var_meal,
            width=12,
            values=["Breakfast", "Lunch", "Dinner", "Snack", "Other"],
            state="readonly",
        ).grid(row=r, column=5, pady=4, sticky="w")

        ttk.Label(addf, text="Recipe (optional)").grid(
            row=r, column=6, padx=(12, 6), pady=4, sticky="e"
        )
        self.cb_recipe = ttk.Combobox(
            addf,
            textvariable=self.var_recipe,
            width=28,
            values=self._recipe_titles(),
            state="normal",
        )
        self.cb_recipe.grid(row=r, column=7, pady=4, sticky="w")

        r += 1
        ttk.Label(addf, text="Items/Consumed").grid(
            row=r, column=0, padx=(6, 6), pady=4, sticky="e"
        )
        ttk.Entry(addf, textvariable=self.var_items, width=60).grid(
            row=r, column=1, columnspan=5, pady=4, sticky="ew"
        )

        ttk.Label(addf, text="Risk").grid(row=r, column=6, padx=(12, 6), pady=4, sticky="e")
        ttk.Combobox(
            addf, textvariable=self.var_risk, width=8, values=RISK_OPTS, state="readonly"
        ).grid(row=r, column=7, pady=4, sticky="w")

        r += 1
        ttk.Label(addf, text="Onset (min)").grid(row=r, column=0, padx=(6, 6), pady=4, sticky="e")
        ttk.Spinbox(addf, from_=0, to=720, textvariable=self.var_onset, width=6).grid(
            row=r, column=1, pady=4, sticky="w"
        )

        ttk.Label(addf, text="Bristol").grid(row=r, column=2, padx=(12, 6), pady=4, sticky="e")
        cb_bristol = ttk.Combobox(
            addf, textvariable=self.var_bristol_label, width=44, state="readonly", values=BRS_VALUES
        )
        cb_bristol.grid(row=r, column=3, columnspan=3, pady=4, sticky="w")

        ttk.Label(addf, text="Severity (0–10)").grid(
            row=r, column=6, padx=(12, 6), pady=4, sticky="e"
        )
        ttk.Spinbox(addf, from_=0, to=10, textvariable=self.var_sev, width=4).grid(
            row=r, column=7, pady=4, sticky="w"
        )

        # Symptoms blocks
        r += 1
        grid = ttk.Frame(addf)
        grid.grid(row=r, column=0, columnspan=5, sticky="w", padx=4, pady=(4, 6))
        self._sym_block(grid, "GI", GI_SYMPTOMS, col=0)
        self._sym_block(grid, "Neuro", NEURO_SYMPTOMS, col=1)
        self._sym_block(grid, "Skin", SKIN_SYMPTOMS, col=2)
        self._sym_block(grid, "Systemic", SYSTEMIC_SYMPTOMS, col=3)

        ttk.Label(addf, text="Notes").grid(row=r, column=6, padx=(12, 6), sticky="ne")
        self.txt_notes = tk.Text(addf, height=6, width=40, wrap="word")
        self.txt_notes.grid(row=r, column=7, padx=(0, 6), pady=(2, 6), sticky="nsew")

        # Buttons
        r += 1
        btns = ttk.Frame(addf)
        btns.grid(row=r, column=0, columnspan=8, sticky="w", padx=6, pady=(0, 6))
        ttk.Button(btns, text="Add Entry", command=self.add_entry).pack(side="left")
        ttk.Button(btns, text="Clear", command=self.clear_form).pack(side="left", padx=(8, 0))

        # Filter / Export bar
        filt = ttk.LabelFrame(self, text="Filter / Export")
        filt.grid(row=2, column=0, sticky="ew", padx=6, pady=(0, 6))
        for i in range(20):
            filt.grid_columnconfigure(i, weight=0)
        filt.grid_columnconfigure(19, weight=1)

        ttk.Label(filt, text="From").grid(row=0, column=0, padx=(6, 6), pady=6, sticky="e")
        ttk.Entry(filt, textvariable=self.f_from, width=12).grid(
            row=0, column=1, pady=6, sticky="w"
        )
        ttk.Label(filt, text="To").grid(row=0, column=2, padx=(10, 6), pady=6, sticky="e")
        ttk.Entry(filt, textvariable=self.f_to, width=12).grid(row=0, column=3, pady=6, sticky="w")
        ttk.Button(filt, text="This Week", command=self._this_week).grid(
            row=0, column=4, padx=(8, 0), pady=6, sticky="w"
        )

        ttk.Button(filt, text="Load", command=self.load_rows).grid(
            row=0, column=5, padx=(14, 0), pady=6
        )

        ttk.Label(filt, text="Min Severity").grid(row=0, column=6, padx=(14, 6), pady=6, sticky="e")
        ttk.Spinbox(filt, from_=0, to=10, textvariable=self.f_minsev, width=4).grid(
            row=0, column=7, pady=6, sticky="w"
        )

        ttk.Label(filt, text="Risk").grid(row=0, column=8, padx=(14, 6), pady=6, sticky="e")
        ttk.Combobox(
            filt, textvariable=self.f_risk, width=8, values=["any"] + RISK_OPTS, state="readonly"
        ).grid(row=0, column=9, pady=6, sticky="w")

        ttk.Label(filt, text="Keyword").grid(row=0, column=10, padx=(14, 6), pady=6, sticky="e")
        ttk.Entry(filt, textvariable=self.f_kw, width=24).grid(row=0, column=11, pady=6, sticky="w")

        ttk.Button(filt, text="Copy", command=self.copy_visible_to_clipboard).grid(
            row=0, column=12, padx=(12, 0), pady=6
        )
        ttk.Button(filt, text="Export HTML", command=self.export_html_visible).grid(
            row=0, column=13, padx=(8, 0), pady=6
        )

        # Table
        wrap = ttk.Frame(self)
        wrap.grid(row=3, column=0, sticky="nsew", padx=6, pady=(0, 6))
        wrap.grid_rowconfigure(0, weight=1)
        wrap.grid_columnconfigure(0, weight=1)

        tv = ttk.Treeview(
            wrap, columns=[c[0] for c in COLS], show="headings", selectmode="extended"
        )
        for k, hdr, width, align in COLS:
            tv.heading(k, text=hdr)
            anc = {"w": "w", "c": "center", "e": "e"}.get(align, "w")
            tv.column(k, width=width, anchor=anc, stretch=True)
        tv.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(wrap, orient="vertical", command=tv.yview)
        hsb = ttk.Scrollbar(wrap, orient="horizontal", command=tv.xview)
        tv.configure(yscroll=vsb.set, xscroll=hsb.set)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self._tree = tv

        # Context menu + bindings
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Edit", command=self.edit_selected)
        menu.add_command(label="Delete", command=self.delete_selected)
        menu.add_separator()
        menu.add_command(label="Export HTML (visible)", command=self.export_html_visible)

        def popup(ev):
            try:
                menu.tk_popup(ev.x_root, ev.y_root)
            finally:
                menu.grab_release()

        tv.bind("<Button-3>", popup)
        tv.bind("<Double-1>", lambda e: self.edit_selected())

        # initial load
        self.load_rows()

    def _sym_block(self, parent: tk.Widget, title: str, options: list[str], *, col: int) -> None:
        box = ttk.LabelFrame(parent, text=title)
        box.grid(row=0, column=col, padx=(0 if col == 0 else 8, 8), sticky="nw")
        for i, name in enumerate(options):
            var = self.sym_vars.setdefault(name, tk.BooleanVar(value=False))
            ttk.Checkbutton(box, text=name, variable=var).grid(row=i, column=0, sticky="w")

    def _recipe_titles(self) -> list[str]:
        try:
            rows = self.db.execute("SELECT title FROM recipes ORDER BY LOWER(title)").fetchall()
            return [r["title"] for r in rows if (r["title"] or "").strip()]
        except Exception:
            return []

    # ---------- Add / Clear ----------
    def _collect_symptoms(self) -> str:
        sel = [name for name, v in self.sym_vars.items() if v.get()]
        return ", ".join(sel)

    def add_entry(self) -> None:
        notes = self.txt_notes.get("1.0", "end").strip()
        try:
            self.db.execute(
                """
                INSERT INTO health_log(date,time,meal,items,risk,onset_min,severity,stool,recipe,symptoms,notes)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)
            """,
                (
                    (self.var_date.get() or "").strip(),
                    (self.var_time.get() or "").strip(),
                    (self.var_meal.get() or "").strip(),
                    (self.var_items.get() or "").strip(),
                    (self.var_risk.get() or "").strip(),
                    int(self.var_onset.get() or 0),
                    int(self.var_sev.get() or 0),
                    bristol_code(self.var_bristol_label.get()),
                    (self.var_recipe.get() or "").strip(),
                    self._collect_symptoms(),
                    notes,
                ),
            )
            self.db.commit()
            self.set_status("Entry added")
            self.clear_form()
            self.load_rows()
        except Exception as e:
            self.error(f"Failed to add entry:\n{e!s}")

    def clear_form(self) -> None:
        self.var_date.set(_today())
        self.var_time.set(_now_hhmm())
        self.var_meal.set("Dinner")
        self.var_recipe.set("")
        self.var_items.set("")
        self.var_risk.set("none")
        self.var_sev.set(0)
        self.var_onset.set(0)
        self.var_bristol_label.set(BRS_OPTIONS[0][1])
        self.txt_notes.delete("1.0", "end")
        for v in self.sym_vars.values():
            v.set(False)

    # ---------- Filtering / loading ----------
    def _this_week(self) -> None:
        today = _dt.date.today()
        start = today - _dt.timedelta(days=today.weekday())  # Monday
        self.f_from.set(start.isoformat())
        self.f_to.set(today.isoformat())

    def _filters_sql(self) -> tuple[str, list[Any]]:
        where = []
        args: list[Any] = []
        f, t = (self.f_from.get() or "").strip(), (self.f_to.get() or "").strip()
        if f:
            where.append("date >= ?")
            args.append(f)
        if t:
            where.append("date <= ?")
            args.append(t)
        if (self.f_minsev.get() or 0) > 0:
            where.append("IFNULL(severity,0) >= ?")
            args.append(int(self.f_minsev.get()))
        risk = (self.f_risk.get() or "any").strip().lower()
        if risk != "any":
            where.append("LOWER(COALESCE(risk,'')) = ?")
            args.append(risk)
        kw = (self.f_kw.get() or "").strip().lower()
        if kw:
            where.append(
                """LOWER(
                COALESCE(items,'') || ' ' ||
                COALESCE(symptoms,'') || ' ' ||
                COALESCE(recipe,'') || ' ' ||
                COALESCE(notes,'')
            ) LIKE ?"""
            )
            args.append(f"%{kw}%")
        wsql = (" WHERE " + " AND ".join(where)) if where else ""
        return wsql, args

    def load_rows(self) -> None:
        tv = self._tree
        if not isinstance(tv, ttk.Treeview):
            return
        for it in tv.get_children():
            tv.delete(it)

        wsql, args = self._filters_sql()
        sql = f"""
            SELECT date,time,meal,items,risk,IFNULL(severity,0) AS severity,IFNULL(stool,0) AS stool,
                   recipe, symptoms, notes, rowid AS _id
              FROM health_log
              {wsql}
             ORDER BY date ASC, time ASC
        """
        rows = self.db.execute(sql, args).fetchall()
        for r in rows:
            tv.insert(
                "",
                "end",
                iid=str(r["_id"]),
                values=[
                    r["date"] or "",
                    r["time"] or "",
                    r["meal"] or "",
                    r["items"] or "",
                    r["risk"] or "",
                    r["severity"] or "",
                    r["stool"] or "",
                    r["recipe"] or "",
                    r["symptoms"] or "",
                    r["notes"] or "",
                ],
            )
        self.set_status(f"{len(rows)} entrie(s)" if len(rows) == 1 else f"{len(rows)} entries")

    # ---------- Edit/Delete ----------
    def edit_selected(self) -> None:
        tv = self._tree
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        if len(sel) != 1:
            messagebox.showinfo(
                "Health Log", "Select one row to edit.", parent=self.winfo_toplevel()
            )
            return
        rid = int(sel[0])
        row = self.db.execute(
            """
            SELECT date,time,meal,items,risk,onset_min,severity,stool,recipe,symptoms,notes
              FROM health_log WHERE rowid=?
        """,
            (rid,),
        ).fetchone()
        if not row:
            return
        data = self._edit_dialog(row)
        if not data:
            return
        self.db.execute(
            """
            UPDATE health_log
               SET date=?, time=?, meal=?, items=?, risk=?, onset_min=?, severity=?, stool=?, recipe=?, symptoms=?, notes=?
             WHERE rowid=?
        """,
            (
                data["date"],
                data["time"],
                data["meal"],
                data["items"],
                data["risk"],
                data["onset_min"],
                data["severity"],
                data["stool"],
                data["recipe"],
                data["symptoms"],
                data["notes"],
                rid,
            ),
        )
        self.db.commit()
        self.load_rows()
        self.set_status("Entry updated")

    def delete_selected(self) -> None:
        tv = self._tree
        if not isinstance(tv, ttk.Treeview):
            return
        sel = tv.selection()
        if not sel:
            return
        if not self.confirm_delete(len(sel)):
            return
        ids = [int(i) for i in sel]
        q = ",".join("?" for _ in ids)
        self.db.execute(f"DELETE FROM health_log WHERE rowid IN ({q})", ids)
        self.db.commit()
        self.load_rows()
        self.set_status(f"Deleted {len(ids)} entries")

    # ---------- Export / copy ----------
    def export_html_visible(self) -> None:
        tv = self._tree
        if not isinstance(tv, ttk.Treeview):
            return
        items = tv.get_children("")
        rows = [list(tv.item(iid, "values")) for iid in items]
        headings = [hdr for _k, hdr, _w, _a in COLS]
        export_table_html(
            path=None,
            title="Health Log",
            columns=headings,
            rows=rows,
            subtitle="Generated from Celiac Culinary",
            meta={"Source": "Health Log", "Rows": len(rows)},
            open_after=True,
        )
        self.set_status(f"Exported {len(rows)} entries to HTML")

    def copy_visible_to_clipboard(self) -> None:
        tv = self._tree
        if not isinstance(tv, ttk.Treeview):
            return
        items = tv.get_children("")
        cols = [c[0] for c in COLS]
        out = [",".join(cols)]
        for iid in items:
            vals = tv.item(iid, "values")
            line = ",".join(str(v).replace("\n", " ").replace(",", ";") for v in vals)
            out.append(line)
        s = "\n".join(out)
        self.clipboard_clear()
        self.clipboard_append(s)
        self.set_status("Copied")

    # ---------- small edit dialog ----------
    def _edit_dialog(self, row: dict[str, Any]) -> dict[str, Any] | None:
        dlg = tk.Toplevel(self)
        dlg.title("Edit Health Entry")
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()
        frm = ttk.Frame(dlg, padding=8)
        frm.grid(row=0, column=0, sticky="nsew")
        dlg.grid_columnconfigure(0, weight=1)
        dlg.grid_rowconfigure(0, weight=1)

        sv = {
            "date": tk.StringVar(value=row["date"] or ""),
            "time": tk.StringVar(value=row["time"] or ""),
            "meal": tk.StringVar(value=row["meal"] or ""),
            "items": tk.StringVar(value=row["items"] or ""),
            "risk": tk.StringVar(value=row["risk"] or "none"),
            "onset_min": tk.StringVar(value=str(row["onset_min"] or 0)),
            "severity": tk.StringVar(value=str(row["severity"] or 0)),
            "stool_label": tk.StringVar(value=bristol_label(int(row["stool"] or 0))),
            "recipe": tk.StringVar(value=row["recipe"] or ""),
            "symptoms": tk.StringVar(value=row["symptoms"] or ""),
            "notes": tk.StringVar(value=row["notes"] or ""),
        }

        r = 0

        def roww(label, widget, col=1):
            nonlocal r
            ttk.Label(frm, text=label).grid(row=r, column=0, sticky="e", padx=(0, 8), pady=(0, 4))
            widget.grid(row=r, column=col, sticky="ew", pady=(0, 4))
            frm.grid_columnconfigure(col, weight=1)
            r += 1

        roww("Date", ttk.Entry(frm, textvariable=sv["date"], width=12))
        roww("Time (HH:MM)", ttk.Entry(frm, textvariable=sv["time"], width=8))
        roww(
            "Meal",
            ttk.Combobox(frm, textvariable=sv["meal"], values=MEALS, state="readonly", width=12),
        )
        roww("Items", ttk.Entry(frm, textvariable=sv["items"], width=50))
        roww(
            "Risk",
            ttk.Combobox(frm, textvariable=sv["risk"], values=RISK_OPTS, state="readonly", width=8),
        )
        roww("Onset (min)", ttk.Entry(frm, textvariable=sv["onset_min"], width=6))
        roww("Severity (0-10)", ttk.Entry(frm, textvariable=sv["severity"], width=6))
        roww(
            "Bristol",
            ttk.Combobox(
                frm, textvariable=sv["stool_label"], values=BRS_VALUES, state="readonly", width=44
            ),
        )
        roww(
            "Recipe",
            ttk.Combobox(frm, textvariable=sv["recipe"], values=self._recipe_titles(), width=30),
        )
        roww("Symptoms", ttk.Entry(frm, textvariable=sv["symptoms"], width=60))
        roww("Notes", ttk.Entry(frm, textvariable=sv["notes"], width=60))

        out: dict[str, Any] = {}

        def on_save():
            out.update(
                {
                    "date": (sv["date"].get() or "").strip(),
                    "time": (sv["time"].get() or "").strip(),
                    "meal": (sv["meal"].get() or "").strip(),
                    "items": (sv["items"].get() or "").strip(),
                    "risk": (sv["risk"].get() or "").strip(),
                    "onset_min": int((sv["onset_min"].get() or "0").strip() or 0),
                    "severity": int((sv["severity"].get() or "0").strip() or 0),
                    "stool": bristol_code(sv["stool_label"].get()),
                    "recipe": (sv["recipe"].get() or "").strip(),
                    "symptoms": (sv["symptoms"].get() or "").strip(),
                    "notes": (sv["notes"].get() or "").strip(),
                }
            )
            dlg.destroy()

        btns = ttk.Frame(dlg, padding=(8, 6))
        btns.grid(row=1, column=0, sticky="e")
        ttk.Button(btns, text="Cancel", command=dlg.destroy).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(btns, text="Save", command=on_save).grid(row=0, column=1)
        dlg.wait_window()
        return out or None
