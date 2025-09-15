# path: panels/calendar_panel.py
from __future__ import annotations

import calendar
import datetime as _dt
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

from typing import Dict, List

from .base_panel import BasePanel


# ---------- small helpers ----------

def _iso(d: _dt.date) -> str:
    return d.isoformat()


def _clamp_int(s: str, lo: int, hi: int, default: int) -> int:
    try:
        v = int(s)
        if v < lo or v > hi:
            return default
        return v
    except Exception:
        return default


def _shift_year_month(year: int, month: int, delta_months: int) -> (int, int):
    # month is 1..12
    i = (year * 12 + (month - 1)) + delta_months
    y = i // 12
    m = (i % 12) + 1
    return y, m


class CalendarPanel(BasePanel):
    """
    Unified calendar: overlays Menu, Health Log, and simple Appointments.
    - Arrow keys navigate months/years.
    - Double-click a day or hit '+' to add a quick appointment.
    - Robust to schema drift: tries multiple known table/column names for menu/health.
    """

    # ------------- UI build -------------
    def build(self) -> None:
        # theme bits (safe defaults even if app.theme is a simple shim)
        theme = getattr(self.app, "theme", None)
        spacing = getattr(theme, "spacing", {"sm": 4, "md": 8, "lg": 12})
        primary = getattr(theme, "primary", "#2563eb")
        highlight = getattr(theme, "highlight", "#e0e7ff")
        background = getattr(theme, "background", None)
        font_family = getattr(theme, "font_family", "Segoe UI")

        st = ttk.Style(self)
        # base styles (app sets Card.TFrame / Muted.TLabel; we add/override a couple)
        try:
            st.configure("Today.TLabel", foreground=primary, font=(font_family, 10, "bold"))
            st.configure("Hover.TFrame", background=highlight)
            if background:
                st.configure("Card.TFrame", background=background, relief="flat")
        except Exception:
            pass

        # header (month controls)
        hdr = ttk.Frame(self, padding=(spacing["md"], spacing["sm"]))
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.columnconfigure(5, weight=1)

        ttk.Label(hdr, text="Year").grid(row=0, column=0, padx=(0, 6))
        self.year_var = tk.StringVar()
        y_now = _dt.date.today().year
        self.year_var.set(str(y_now))
        ent_year = ttk.Entry(hdr, width=6, textvariable=self.year_var)
        ent_year.grid(row=0, column=1, padx=(0, spacing["md"]))
        ent_year.bind("<Return>", lambda _e: self.refresh())

        ttk.Label(hdr, text="Month").grid(row=0, column=2, padx=(0, 6))
        self.month_var = tk.StringVar()
        m_now = _dt.date.today().month
        self.month_var.set(str(m_now))
        ent_month = ttk.Entry(hdr, width=4, textvariable=self.month_var)
        ent_month.grid(row=0, column=3, padx=(0, spacing["md"]))
        ent_month.bind("<Return>", lambda _e: self.refresh())

        ttk.Button(hdr, text="◀", width=3, command=lambda: self._shift_month(-1)).grid(row=0, column=4, padx=(0, 4))
        ttk.Button(hdr, text="▶", width=3, command=lambda: self._shift_month(+1)).grid(row=0, column=5, padx=(0, spacing["md"]))
        ttk.Button(hdr, text="Today", command=self._jump_today).grid(row=0, column=6)

        # weekday header (Mon..Sun or Sun..Sat based on settings)
        wk_hdr = ttk.Frame(self, padding=(spacing["md"], spacing["sm"]))
        wk_hdr.grid(row=1, column=0, sticky="ew")
        for i in range(7):
            lbl = ttk.Label(wk_hdr, text="", style="Muted.TLabel")
            lbl.grid(row=0, column=i, sticky="w", padx=(6, 0))
            wk_hdr.grid_columnconfigure(i, weight=1)
        self._weekday_labels = [c for c in wk_hdr.winfo_children() if isinstance(c, ttk.Label)]

        # calendar container
        self.container = ttk.Frame(self, padding=(spacing["md"], spacing["sm"]))
        self.container.grid(row=2, column=0, sticky="nsew")
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # DB table for lightweight appointments
        self._ensure_appointments_table()

        # first render
        self.refresh()

        # keyboard navigation
        self.bind_all("<Left>", self._move_calendar_left)
        self.bind_all("<Right>", self._move_calendar_right)
        self.bind_all("<Up>", self._move_calendar_up)
        self.bind_all("<Down>", self._move_calendar_down)

    # ------------- data helpers -------------
    def _ensure_appointments_table(self) -> None:
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id     INTEGER PRIMARY KEY,
                date   TEXT NOT NULL,        -- ISO YYYY-MM-DD
                time   TEXT DEFAULT '',      -- 'HH:MM' optional
                title  TEXT NOT NULL,
                notes  TEXT DEFAULT ''
            )
            """
        )
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(date)")
        self.db.commit()

    def _try_select(self, sql_list: List[str]):
        cur = self.db.cursor()
        for sql in sql_list:
            try:
                return cur.execute(sql).fetchall()
            except sqlite3.OperationalError:
                continue
        return []

    # ------------- UI refresh -------------
    def refresh(self) -> None:
        # spinner
        pb = ttk.Progressbar(self.container, mode="indeterminate")
        pb.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        pb.start()
        self.container.update_idletasks()

        try:
            # wipe existing month grid
            for w in list(self.container.winfo_children()):
                w.destroy()

            # parse month/year
            y = _clamp_int(self.year_var.get(), 1900, 3000, _dt.date.today().year)
            m = _clamp_int(self.month_var.get(), 1, 12, _dt.date.today().month)
            first = _dt.date(y, m, 1)

            # weekday header text (Mon/Sun first)
            start_day = getattr(getattr(self.app, "settings", object()), "START_DAY", "Monday")
            mon_first = (str(start_day).strip().lower().startswith("mon"))
            firstweekday = 0 if mon_first else 6
            for i, lab in enumerate(self._weekday_labels):
                idx = (i if mon_first else (i - 6))  # if Sunday first, show Sun..Sat
                lab.config(text=calendar.day_abbr[(firstweekday + i) % 7])

            cal = calendar.Calendar(firstweekday=firstweekday)
            weeks = cal.monthdatescalendar(y, m)

            # pull data (be forgiving to schema drift)
            menus = self._try_select([
                "SELECT substr(date,1,10) AS d, meal FROM menu_plan",
                "SELECT substr(date,1,10) AS d, meal_type AS meal FROM menu_plans",
            ])
            health = self._try_select([
                "SELECT substr(date,1,10) AS d, symptoms FROM health_logs",
                "SELECT substr(date,1,10) AS d, symptoms FROM health_log",
                "SELECT substr(date,1,10) AS d, notes AS symptoms FROM health_log",
            ])
            appts = self._try_select([
                "SELECT substr(date,1,10) AS d, time, title FROM appointments",
            ])

            menu_map: Dict[str, List[str]] = {}
            health_map: Dict[str, List[str]] = {}
            appt_map: Dict[str, List[str]] = {}

            for r in menus:
                menu_map.setdefault(r["d"], []).append((r["meal"] or "").strip())

            for r in health:
                txt = (r["symptoms"] or "").strip()
                if txt:
                    health_map.setdefault(r["d"], []).append(txt[:60])

            for r in appts:
                t = (r["time"] or "").strip()
                title = (r["title"] or "").strip()
                line = f"{t} {title}".strip() if t else title
                if line:
                    appt_map.setdefault(r["d"], []).append(line[:60])

            # build month grid
            today = _dt.date.today()
            for r, wk in enumerate(weeks):
                row = ttk.Frame(self.container)
                row.grid(row=r, column=0, sticky="ew")
                for c in range(7):
                    row.grid_columnconfigure(c, weight=1)

                for c, d in enumerate(wk):
                    in_month = (d.month == m)
                    box = ttk.Frame(row, style="Card.TFrame", padding=6)
                    box.grid(row=0, column=c, sticky="nsew", padx=4, pady=4)

                    # day header: number + quick add
                    hdr = ttk.Frame(box)
                    hdr.pack(fill="x")
                    lbl_style = "Today.TLabel" if d == today else ("Muted.TLabel" if not in_month else "TLabel")
                    day_lbl = ttk.Label(hdr, text=str(d.day), style=lbl_style)
                    day_lbl.pack(side="left", anchor="nw")

                    ttk.Button(hdr, text="+", width=2, command=lambda dd=d: self._add_appt_dialog(_iso(dd))).pack(side="right")

                    if not in_month:
                        try:
                            day_lbl.configure(style="Muted.TLabel")
                        except Exception:
                            pass

                    ds = _iso(d)

                    # entries
                    for mt in menu_map.get(ds, []):
                        ttk.Label(box, text=f"🍽 {mt}", style="Muted.TLabel").pack(anchor="w")
                    for s in health_map.get(ds, []):
                        ttk.Label(box, text=f"🩺 {s}", style="Muted.TLabel").pack(anchor="w")
                    for a in appt_map.get(ds, []):
                        ttk.Label(box, text=f"📌 {a}", style="Muted.TLabel").pack(anchor="w")

                    # interactions
                    box.bind("<Double-1>", lambda _e, dd=d: self._add_appt_dialog(_iso(dd)))
                    box.bind("<Button-1>", lambda _e, dd=ds: self._show_day_details(dd, menu_map, health_map, appt_map))
                    box.bind("<Enter>", lambda e: e.widget.configure(style="Hover.TFrame"))
                    box.bind("<Leave>", lambda e: e.widget.configure(style="Card.TFrame"))

            self.set_status(f"Calendar — {first.strftime('%B %Y')}")
        except Exception as ex:
            messagebox.showerror("Calendar", str(ex), parent=self.winfo_toplevel())
        finally:
            try:
                pb.stop()
                pb.destroy()
            except Exception:
                pass

    # ------------- navigation -------------
    def _shift_month(self, delta: int) -> None:
        y = _clamp_int(self.year_var.get(), 1900, 3000, _dt.date.today().year)
        m = _clamp_int(self.month_var.get(), 1, 12, _dt.date.today().month)
        y2, m2 = _shift_year_month(y, m, delta)
        self.year_var.set(str(y2))
        self.month_var.set(str(m2))
        self.refresh()

    def _jump_today(self) -> None:
        t = _dt.date.today()
        self.year_var.set(str(t.year))
        self.month_var.set(str(t.month))
        self.refresh()

    # arrow keys
    def _move_calendar_left(self, _e=None):  # previous month
        self._shift_month(-1)

    def _move_calendar_right(self, _e=None):  # next month
        self._shift_month(+1)

    def _move_calendar_up(self, _e=None):  # previous year
        self._shift_month(-12)

    def _move_calendar_down(self, _e=None):  # next year
        self._shift_month(+12)

    # ------------- dialogs -------------
    def _add_appt_dialog(self, date_iso: str) -> None:
        dlg = tk.Toplevel(self)
        dlg.title(f"Add Appointment — {date_iso}")
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()
        dlg.resizable(False, False)

        frm = ttk.Frame(dlg, padding=8); frm.grid(row=0, column=0, sticky="nsew")

        v_time = tk.StringVar(value="")
        v_title = tk.StringVar(value="")
        v_notes = tk.StringVar(value="")

        def row(label, widget, i):
            ttk.Label(frm, text=label).grid(row=i, column=0, sticky="e", padx=(0, 8), pady=(0, 4))
            widget.grid(row=i, column=1, sticky="ew", pady=(0, 4))
        row("Time (HH:MM)", ttk.Entry(frm, textvariable=v_time, width=10), 0)
        row("Title",        ttk.Entry(frm, textvariable=v_title, width=28), 1)
        row("Notes",        ttk.Entry(frm, textvariable=v_notes, width=32), 2)
        frm.grid_columnconfigure(1, weight=1)

        err = ttk.Label(frm, text="", foreground="red")
        err.grid(row=3, column=1, sticky="w")

        def save():
            title = v_title.get().strip()
            if not title:
                err.configure(text="Title is required")
                return
            time = v_time.get().strip()
            notes = v_notes.get().strip()
            self.db.execute(
                "INSERT INTO appointments(date,time,title,notes) VALUES(?,?,?,?)",
                (date_iso, time, title, notes),
            )
            self.db.commit()
            dlg.destroy()
            self.refresh()

        btns = ttk.Frame(dlg, padding=(8, 6)); btns.grid(row=1, column=0, sticky="e")
        ttk.Button(btns, text="Cancel", command=dlg.destroy).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(btns, text="Save",   command=save).grid(row=0, column=1)

    def _show_day_details(self, date_iso: str, menu_map, health_map, appt_map) -> None:
        dlg = tk.Toplevel(self)
        dlg.title(f"Details for {date_iso}")
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()
        dlg.resizable(False, False)

        frm = ttk.Frame(dlg, padding=8)
        frm.pack(fill="both", expand=True)

        def add_section(label: str, items: List[str], icon: str = ""):
            if items:
                ttk.Label(frm, text=f"{icon} {label}:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(6, 2))
                for it in items:
                    ttk.Label(frm, text=f"• {it}", style="Muted.TLabel").pack(anchor="w")

        add_section("Menu", menu_map.get(date_iso, []), "🍽")
        add_section("Health", health_map.get(date_iso, []), "🩺")
        add_section("Appointments", appt_map.get(date_iso, []), "📌")

        ttk.Frame(frm).pack(fill="x", pady=(8, 0))
        ttk.Button(frm, text="Close", command=dlg.destroy).pack(anchor="e", pady=(8, 0))
