# path: panels/calendar_panel.py
from __future__ import annotations

import calendar
import datetime as _dt
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

from .base_panel import BasePanel


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


def _shift_year_month(year: int, month: int, delta_months: int) -> tuple[int, int]:
    i = (year * 12 + (month - 1)) + delta_months
    y = i // 12
    m = (i % 12) + 1
    return y, m


class CalendarPanel(BasePanel):
    """
    Standard month view with context menu:
      - 7×6 uniform grid, weekday header
      - Today highlighted, out-of-month dimmed
      - Double-click to add appt
      - Right-click menu: Add…, Delete last appt, Delete all appts, Details
    """

    def build(self) -> None:
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        st = ttk.Style(self)
        try:
            st.configure("Cal.Day.TFrame", padding=6)
            st.configure("Cal.DayMuted.TFrame", padding=6)
            st.configure("Cal.Today.TLabel", font=("Segoe UI", 10, "bold"))
            st.configure("Cal.Muted.TLabel", foreground="#6b7280")
        except Exception:
            pass

        # Header
        hdr = ttk.Frame(self, padding=(6, 6))
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.columnconfigure(7, weight=1)

        ttk.Label(hdr, text="Year").grid(row=0, column=0, padx=(0, 6))
        self.year_var = tk.StringVar(value=str(_dt.date.today().year))
        ent_year = ttk.Entry(hdr, width=6, textvariable=self.year_var)
        ent_year.grid(row=0, column=1, padx=(0, 12))
        ent_year.bind("<Return>", lambda _e: self.refresh())

        ttk.Label(hdr, text="Month").grid(row=0, column=2, padx=(0, 6))
        self.month_var = tk.StringVar(value=str(_dt.date.today().month))
        ent_month = ttk.Entry(hdr, width=4, textvariable=self.month_var)
        ent_month.grid(row=0, column=3, padx=(0, 12))
        ent_month.bind("<Return>", lambda _e: self.refresh())

        ttk.Button(hdr, text="◀", width=3, command=lambda: self._shift_month(-1)).grid(row=0, column=4, padx=(0, 4))
        ttk.Button(hdr, text="▶", width=3, command=lambda: self._shift_month(+1)).grid(row=0, column=5, padx=(0, 12))
        ttk.Button(hdr, text="Today", command=self._jump_today).grid(row=0, column=6)

        # Weekday header
        wk = ttk.Frame(self, padding=(6, 0))
        wk.grid(row=1, column=0, sticky="ew")
        self._weekday_labels: list[ttk.Label] = []
        for i in range(7):
            wk.grid_columnconfigure(i, weight=1, uniform="wk")
        for i in range(7):
            lbl = ttk.Label(wk, text="", anchor="center")
            lbl.grid(row=0, column=i, sticky="nsew", pady=(0, 4))
            self._weekday_labels.append(lbl)

        # Month grid container
        self.container = ttk.Frame(self, padding=6)
        self.container.grid(row=2, column=0, sticky="nsew")
        for r in range(6):
            self.container.grid_rowconfigure(r, weight=1, uniform="cal")
        for c in range(7):
            self.container.grid_columnconfigure(c, weight=1, uniform="cal")

        # Storage
        self._ensure_appointments_table()

        # Initial render
        self.refresh()

        # Keyboard navigation
        self.bind_all("<Left>", lambda _e: self._shift_month(-1))
        self.bind_all("<Right>", lambda _e: self._shift_month(+1))
        self.bind_all("<Up>", lambda _e: self._shift_month(-12))
        self.bind_all("<Down>", lambda _e: self._shift_month(+12))

    # ----- schema -----
    def _ensure_appointments_table(self) -> None:
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
              id     INTEGER PRIMARY KEY,
              date   TEXT NOT NULL,   -- YYYY-MM-DD
              time   TEXT DEFAULT '',
              title  TEXT NOT NULL,
              notes  TEXT DEFAULT ''
            )
            """
        )
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(date)")
        self.db.commit()

    # ----- refresh -----
    def refresh(self) -> None:
        for w in list(self.container.winfo_children()):
            w.destroy()

        y = _clamp_int(self.year_var.get(), 1900, 3000, _dt.date.today().year)
        m = _clamp_int(self.month_var.get(), 1, 12, _dt.date.today().month)

        # Week start from settings
        start_day = getattr(getattr(self.app, "settings", object()), "START_DAY", "Monday")
        mon_first = str(start_day).strip().lower().startswith("mon")
        firstweekday = 0 if mon_first else 6
        for i, lab in enumerate(self._weekday_labels):
            lab.config(text=calendar.day_abbr[(firstweekday + i) % 7])

        cal = calendar.Calendar(firstweekday=firstweekday)
        weeks = cal.monthdatescalendar(y, m)

        # Pull data
        menus = self._safe_select([
            "SELECT substr(date,1,10) AS d, meal FROM menu_plan",
            "SELECT substr(date,1,10) AS d, meal_type AS meal FROM menu_plans",
        ])
        health = self._safe_select([
            "SELECT substr(date,1,10) AS d, symptoms FROM health_logs",
            "SELECT substr(date,1,10) AS d, symptoms FROM health_log",
            "SELECT substr(date,1,10) AS d, notes AS symptoms FROM health_log",
        ])
        appts = self._safe_select([
            "SELECT id, substr(date,1,10) AS d, time, title FROM appointments",
        ])

        menu_map: dict[str, list[str]] = {}
        health_map: dict[str, list[str]] = {}
        appt_map: dict[str, list[tuple[int, str]]] = {}
        for r in menus:
            menu_map.setdefault(r["d"], []).append((r["meal"] or "").strip())
        for r in health:
            t = (r["symptoms"] or "").strip()
            if t:
                health_map.setdefault(r["d"], []).append(t)
        for r in appts:
            t = (r["time"] or "").strip()
            title = (r["title"] or "").strip()
            line = f"{t} {title}".strip() if t else title
            appt_map.setdefault(r["d"], []).append((int(r["id"]), line))

        today = _dt.date.today()

        # 6 rows always
        for r in range(6):
            row_days = weeks[r] if r < len(weeks) else [weeks[-1][-1] + _dt.timedelta(days=i) for i in range(1, 8)]
            for c, d in enumerate(row_days):
                in_month = d.month == m
                ds = _iso(d)

                style_frame = "Cal.Day.TFrame" if in_month else "Cal.DayMuted.TFrame"
                cell = ttk.Frame(self.container, style=style_frame)
                cell.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)

                # date
                date_wrap = ttk.Frame(cell)
                date_wrap.pack(fill="x")
                day_style = "Cal.Today.TLabel" if d == today else ("Cal.Muted.TLabel" if not in_month else "TLabel")
                ttk.Label(date_wrap, text=str(d.day), anchor="e", style=day_style).pack(side="right")

                # lines (compact)
                lines = [f"🍽 {x}" for x in menu_map.get(ds, [])]
                lines += [f"🩺 {x}" for x in health_map.get(ds, [])]
                lines += [f"📌 {txt}" for _id, txt in appt_map.get(ds, [])]
                for txt in lines[:4]:
                    ttk.Label(cell, text=txt, style="Cal.Muted.TLabel").pack(anchor="w")

                # interactions
                cell.bind("<Double-1>", lambda _e, dd=d: self._add_appt_dialog(_iso(dd)))
                for kid in cell.winfo_children():
                    kid.bind("<Double-1>", lambda _e, dd=d: self._add_appt_dialog(_iso(dd)))

                # right-click menu
                cell.bind("<Button-3>", lambda e, dd=ds: self._day_context_menu(e, dd))
                for kid in cell.winfo_children():
                    kid.bind("<Button-3>", lambda e, dd=ds: self._day_context_menu(e, dd))

        self.set_status(f"{_dt.date(y, m, 1).strftime('%B %Y')}")

    # ----- context menu -----
    def _day_context_menu(self, event: tk.Event, date_iso: str) -> None:
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Add appointment…", command=lambda d=date_iso: self._add_appt_dialog(d))

        appts = self._get_appts(date_iso)
        if appts:
            last_id, last_label = appts[-1]
            menu.add_command(
                label=f"Delete last appt: {self._shorten(last_label, 28)}",
                command=lambda i=last_id: self._delete_appt_by_id(i),
            )
            menu.add_command(
                label=f"Delete all {len(appts)} appt(s)",
                command=lambda d=date_iso: self._delete_all_appts(d),
            )
        else:
            menu.add_command(label="No appointments to delete", state="disabled")

        menu.add_separator()
        menu.add_command(label="Open details", command=lambda d=date_iso: self._open_details_for(d))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _shorten(self, s: str, n: int) -> str:
        return s if len(s) <= n else s[: max(0, n - 1)] + "…"

    def _open_details_for(self, date_iso: str) -> None:
        menus = self._safe_select([
            f"SELECT meal FROM menu_plan WHERE substr(date,1,10)='{date_iso}'",
            f"SELECT meal_type AS meal FROM menu_plans WHERE substr(date,1,10)='{date_iso}'",
        ])
        health = self._safe_select([
            f"SELECT symptoms FROM health_logs WHERE substr(date,1,10)='{date_iso}'",
            f"SELECT symptoms FROM health_log WHERE substr(date,1,10)='{date_iso}'",
            f"SELECT notes AS symptoms FROM health_log WHERE substr(date,1,10)='{date_iso}'",
        ])
        appts = self._get_appts(date_iso)
        menu_map = {date_iso: [(r["meal"] or "").strip() for r in menus if (r["meal"] or "").strip()]}
        health_map = {date_iso: [(r["symptoms"] or "").strip() for r in health if (r["symptoms"] or "").strip()]}
        appt_map = {date_iso: [label for _id, label in appts]}
        self._show_day_details(date_iso, menu_map, health_map, appt_map)

    # ----- DB helpers -----
    def _safe_select(self, sql_list: list[str]):
        cur = self.db.cursor()
        for sql in sql_list:
            try:
                return cur.execute(sql).fetchall()
            except sqlite3.OperationalError:
                continue
        return []

    def _get_appts(self, date_iso: str) -> list[tuple[int, str]]:
        try:
            rows = self.db.execute(
                "SELECT id, IFNULL(time,'') AS time, IFNULL(title,'') AS title "
                "FROM appointments WHERE date=? ORDER BY IFNULL(time,''), id",
                (date_iso,),
            ).fetchall()
        except sqlite3.OperationalError:
            return []
        out: list[tuple[int, str]] = []
        for r in rows:
            t = (r["time"] or "").strip()
            title = (r["title"] or "").strip()
            out.append((int(r["id"]), f"{t} {title}".strip() if t else title))
        return out

    def _delete_appt_by_id(self, appt_id: int) -> None:
        self.db.execute("DELETE FROM appointments WHERE id=?", (appt_id,))
        self.db.commit()
        self.refresh()

    def _delete_all_appts(self, date_iso: str) -> None:
        n = len(self._get_appts(date_iso))
        if not n:
            return
        if not messagebox.askyesno("Confirm", f"Delete all {n} appointment(s) on {date_iso}?", parent=self.winfo_toplevel()):
            return
        self.db.execute("DELETE FROM appointments WHERE date=?", (date_iso,))
        self.db.commit()
        self.refresh()

    # ----- navigation -----
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

    # ----- dialogs -----
    def _add_appt_dialog(self, date_iso: str) -> None:
        dlg = tk.Toplevel(self)
        dlg.title(f"Add Appointment — {date_iso}")
        dlg.transient(self.winfo_toplevel()); dlg.grab_set(); dlg.resizable(False, False)

        frm = ttk.Frame(dlg, padding=8); frm.grid(row=0, column=0, sticky="nsew")
        v_time = tk.StringVar(value=""); v_title = tk.StringVar(value=""); v_notes = tk.StringVar(value="")

        def row(label, widget, i):
            ttk.Label(frm, text=label).grid(row=i, column=0, sticky="e", padx=(0, 8), pady=(0, 4))
            widget.grid(row=i, column=1, sticky="ew", pady=(0, 4))

        row("Time (HH:MM)", ttk.Entry(frm, textvariable=v_time, width=10), 0)
        row("Title", ttk.Entry(frm, textvariable=v_title, width=28), 1)
        row("Notes", ttk.Entry(frm, textvariable=v_notes, width=32), 2)
        frm.grid_columnconfigure(1, weight=1)

        err = ttk.Label(frm, text="", foreground="red"); err.grid(row=3, column=1, sticky="w")

        def save():
            title = v_title.get().strip()
            if not title:
                err.configure(text="Title is required"); return
            time = v_time.get().strip(); notes = v_notes.get().strip()
            self.db.execute("INSERT INTO appointments(date,time,title,notes) VALUES(?,?,?,?)", (date_iso, time, title, notes))
            self.db.commit(); dlg.destroy(); self.refresh()

        btns = ttk.Frame(dlg, padding=(8, 6)); btns.grid(row=1, column=0, sticky="e")
        ttk.Button(btns, text="Cancel", command=dlg.destroy).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(btns, text="Save", command=save).grid(row=0, column=1)

    def _show_day_details(self, date_iso: str, menu_map, health_map, appt_map) -> None:
        dlg = tk.Toplevel(self)
        dlg.title(f"Details for {date_iso}")
        dlg.transient(self.winfo_toplevel()); dlg.grab_set(); dlg.resizable(False, False)

        frm = ttk.Frame(dlg, padding=8); frm.pack(fill="both", expand=True)

        def add_section(label: str, items: list[str], icon: str = ""):
            if items:
                ttk.Label(frm, text=f"{icon} {label}:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(6, 2))
                for it in items:
                    ttk.Label(frm, text=f"• {it}").pack(anchor="w")

        add_section("Menu", menu_map.get(date_iso, []), "🍽")
        add_section("Health", health_map.get(date_iso, []), "🩺")
        add_section("Appointments", appt_map.get(date_iso, []), "📌")

        ttk.Frame(frm).pack(fill="x", pady=(8, 0))
        ttk.Button(frm, text="Close", command=dlg.destroy).pack(anchor="e", pady=(8, 0))

    def _open_details_for(self, d: str) -> None:
        # alias kept for context menu
        menus = {d: [r["meal"] or "" for r in self._safe_select([f"SELECT meal FROM menu_plan WHERE substr(date,1,10)='{d}'",
                                                                 f"SELECT meal_type AS meal FROM menu_plans WHERE substr(date,1,10)='{d}'"]) if (r["meal"] or "").strip()]}
        health = {d: [r["symptoms"] or "" for r in self._safe_select([f"SELECT symptoms FROM health_logs WHERE substr(date,1,10)='{d}'",
                                                                      f"SELECT symptoms FROM health_log WHERE substr(date,1,10)='{d}'",
                                                                      f"SELECT notes AS symptoms FROM health_log WHERE substr(date,1,10)='{d}'"]) if (r["symptoms"] or "").strip()]}
        appts = {d: [label for _id, label in self._get_appts(d)]}
        self._show_day_details(d, menus, health, appts)
