# panels/calendar_panel.py
from __future__ import annotations
import sqlite3
import tkinter as tk
from tkinter import ttk
import calendar, datetime
from .base_panel import BasePanel

def _iso(d: datetime.date) -> str:
    return d.strftime("%Y-%m-%d")

class CalendarPanel(BasePanel):
    def build(self):
        s = self.app.theme.spacing
        top = ttk.Frame(self); top.pack(fill="x", padx=s["md"], pady=s["sm"])
        ttk.Label(top, text="Calendar").pack(side="left")

        self.month_var = tk.StringVar()
        self.year_var = tk.StringVar()

        today = datetime.date.today()
        self.month_var.set(str(today.month))
        self.year_var.set(str(today.year))

        # Controls
        ttk.Button(top, text="Today", command=self._jump_today).pack(side="right")
        ttk.Spinbox(top, from_=2000, to=2100, textvariable=self.year_var, width=7, command=self.refresh).pack(side="right")
        ttk.Spinbox(top, from_=1, to=12, textvariable=self.month_var, width=5, command=self.refresh).pack(side="right")

        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True, padx=s["md"], pady=s["sm"])

        # Ensure our lightweight appointments table exists
        self._ensure_appointments_table()

        self.refresh()

    # ---------- data helpers ----------
    def _ensure_appointments_table(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id     INTEGER PRIMARY KEY,
                date   TEXT NOT NULL,        -- ISO YYYY-MM-DD
                time   TEXT DEFAULT '',      -- 'HH:MM' optional
                title  TEXT NOT NULL,
                notes  TEXT DEFAULT ''
            )
        """)
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(date)")
        self.db.commit()

    def _try_select(self, sql_list):
        cur = self.db.cursor()
        for sql in sql_list:
            try:
                return cur.execute(sql).fetchall()
            except sqlite3.OperationalError:
                continue
        return []

    # ---------- UI refresh ----------
    def refresh(self):
        # Clear current month grid
        for w in self.container.winfo_children():
            w.destroy()

        # Parse month/year (ignore bad input)
        try:
            y = int(self.year_var.get()); m = int(self.month_var.get())
            first = datetime.date(y, m, 1)
        except Exception:
            return

        cal = calendar.Calendar()
        weeks = cal.monthdatescalendar(y, m)

        # Pull data, robust to schema drift:
        # Menu (prefer correct schema, fallback to old)
        menus = self._try_select([
            "SELECT substr(date,1,10) AS d, meal FROM menu_plan",
            "SELECT substr(date,1,10) AS d, meal_type AS meal FROM menu_plans",
        ])
        # Health logs (several potential names/columns)
        health = self._try_select([
            "SELECT substr(date,1,10) AS d, symptoms FROM health_logs",
            "SELECT substr(date,1,10) AS d, symptoms FROM health_log",
            "SELECT substr(date,1,10) AS d, notes AS symptoms FROM health_log",
        ])
        # Appointments (we control this)
        appts = self._try_select([
            "SELECT substr(date,1,10) AS d, time, title FROM appointments"
        ])

        menu_map, health_map, appt_map = {}, {}, {}

        for r in menus:
            menu_map.setdefault(r["d"], []).append((r["meal"] or "").strip())

        for r in health:
            txt = (r["symptoms"] or "").strip()
            if txt:
                health_map.setdefault(r["d"], []).append(txt[:40])

        for r in appts:
            t = (r["time"] or "").strip()
            title = (r["title"] or "").strip()
            line = f"{t} {title}".strip() if t else title
            if line:
                appt_map.setdefault(r["d"], []).append(line[:40])

        # Build month grid
        for wk in weeks:
            row = ttk.Frame(self.container); row.pack(fill="x", expand=True)
            for d in wk:
                box = ttk.Frame(row, style="Card.TFrame", padding=6)
                box.pack(side="left", fill="both", expand=True, padx=4, pady=4)

                # Day header: day number + quick add
                hdr = ttk.Frame(box); hdr.pack(fill="x")
                day_lbl = ttk.Label(hdr, text=str(d.day))
                day_lbl.pack(side="left", anchor="nw")

                add_btn = ttk.Button(hdr, text="+", width=2, command=lambda dd=d: self._add_appt_dialog(_iso(dd)))
                add_btn.pack(side="right")

                # Dim days outside the current month
                in_month = (d.month == m)
                if not in_month:
                    try:
                        day_lbl.configure(style="Muted.TLabel")
                    except Exception:
                        pass

                ds = _iso(d)

                # Render entries
                for mt in menu_map.get(ds, []):
                    ttk.Label(box, text=f"🍽 {mt}", style="Muted.TLabel").pack(anchor="w")
                for s in health_map.get(ds, []):
                    ttk.Label(box, text=f"🩺 {s}", style="Muted.TLabel").pack(anchor="w")
                for a in appt_map.get(ds, []):
                    ttk.Label(box, text=f"📌 {a}", style="Muted.TLabel").pack(anchor="w")

                # Double-click anywhere in the day box to add appt
                box.bind("<Double-1>", lambda e, dd=d: self._add_appt_dialog(_iso(dd)))

    def _jump_today(self):
        t = datetime.date.today()
        self.year_var.set(str(t.year))
        self.month_var.set(str(t.month))
        self.refresh()

    # ---------- appointment dialog ----------
    def _add_appt_dialog(self, date_iso: str):
        dlg = tk.Toplevel(self)
        dlg.title(f"Add Appointment — {date_iso}")
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()
        dlg.resizable(False, False)

        frm = ttk.Frame(dlg, padding=8); frm.grid(row=0, column=0, sticky="nsew")

        v_time  = tk.StringVar(value="")
        v_title = tk.StringVar(value="")
        v_notes = tk.StringVar(value="")

        def row(label, widget, i):
            ttk.Label(frm, text=label).grid(row=i, column=0, sticky="e", padx=(0,8), pady=(0,4))
            widget.grid(row=i, column=1, sticky="ew", pady=(0,4))

        row("Time (HH:MM)", ttk.Entry(frm, textvariable=v_time, width=10), 0)
        row("Title",        ttk.Entry(frm, textvariable=v_title, width=28), 1)
        row("Notes",        ttk.Entry(frm, textvariable=v_notes, width=32), 2)
        frm.grid_columnconfigure(1, weight=1)

        def save():
            title = v_title.get().strip()
            if not title:
                ttk.Label(frm, text="Title is required", foreground="red").grid(row=3, column=1, sticky="w")
                return
            time = v_time.get().strip()
            notes = v_notes.get().strip()
            self.db.execute(
                "INSERT INTO appointments(date,time,title,notes) VALUES(?,?,?,?)",
                (date_iso, time, title, notes)
            )
            self.db.commit()
            dlg.destroy()
            self.refresh()

        btns = ttk.Frame(dlg, padding=(8,6)); btns.grid(row=1, column=0, sticky="e")
        ttk.Button(btns, text="Cancel", command=dlg.destroy).grid(row=0, column=0, padx=(0,6))
        ttk.Button(btns, text="Save",   command=save).grid(row=0, column=1)
