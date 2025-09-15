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
        months = [str(i) for i in range(1, 13)]
        ttk.Combobox(top, values=months, textvariable=self.month_var, width=5, state="readonly").pack(side="right")
        years = [str(y) for y in range(2000, 2101)]
        ttk.Combobox(top, values=years, textvariable=self.year_var, width=7, state="readonly").pack(side="right")

        # Bind selection changes to refresh:
        self.month_var.trace_add("write", lambda *_, sv=self.month_var: self.refresh())
        self.year_var.trace_add("write", lambda *_, sv=self.year_var: self.refresh())

        # Use grid for the main container
        self.container = ttk.Frame(self)
        self.container.grid(row=1, column=0, sticky="nsew", padx=s["md"], pady=s["sm"])
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Ensure our lightweight appointments table exists
        self._ensure_appointments_table()

        self.refresh()

        self.bind_all("<Left>", self._move_calendar_left)
        self.bind_all("<Right>", self._move_calendar_right)
        self.bind_all("<Up>", self._move_calendar_up)
        self.bind_all("<Down>", self._move_calendar_down)

        # --- NEW THEME CODE ---
        theme = self.app.theme
        style = ttk.Style()
        style.configure("Today.TLabel", foreground=theme.primary, font=(theme.font_family, 10, "bold"))
        style.configure("Hover.TFrame", background=theme.highlight)
        style.configure("Card.TFrame", background=theme.background)
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
        # Show spinner/progress bar
        self._progress = ttk.Progressbar(self.container, mode="indeterminate")
        self._progress.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self._progress.start()
        self.container.update_idletasks()
        try:
            # Clear current month grid
            for w in self.container.winfo_children():
                w.destroy()

            # Parse month/year (ignore bad input)
            try:
                y = int(self.year_var.get()); m = int(self.month_var.get())
                first = datetime.date(y, m, 1)
            except Exception:
                return

            start_day = getattr(self.app.settings, "START_DAY", "Monday")
            firstweekday = 0 if start_day == "Monday" else 6
            cal = calendar.Calendar(firstweekday=firstweekday)
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

            # Build month grid using grid layout
            for r, wk in enumerate(weeks):
                row = ttk.Frame(self.container)
                row.grid(row=r, column=0, sticky="ew")
                row.columnconfigure(tuple(range(7)), weight=1)  # 7 days per week

                for c, d in enumerate(wk):
                    box = ttk.Frame(row, style="Card.TFrame", padding=6)
                    box.grid(row=0, column=c, sticky="nsew", padx=4, pady=4)
                    row.columnconfigure(c, weight=1)

                    # Day header: day number + quick add
                    hdr = ttk.Frame(box); hdr.pack(fill="x")
                    is_today = (d == datetime.date.today())
                    lbl_style = "Today.TLabel" if is_today else ("Muted.TLabel" if not in_month else "TLabel")
                    day_lbl = ttk.Label(hdr, text=str(d.day), style=lbl_style)
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

                    def on_enter(e):
                        e.widget.configure(style="Hover.TFrame")
                    def on_leave(e):
                        e.widget.configure(style="Card.TFrame")

                    style.configure("Hover.TFrame", background="#e0e7ff")  # light blue highlight

                    box.bind("<Enter>", on_enter)
                    box.bind("<Leave>", on_leave)

                    has_event = ds in menu_map or ds in health_map or ds in appt_map
                    if has_event:
                        ttk.Label(hdr, text="•", foreground="#2563eb").pack(side="right", padx=(2,0))

                    box.bind("<Button-1>", lambda e, dd=ds: self._show_day_details(dd, menu_map, health_map, appt_map))

            # Highlight today's date
            today_iso = _iso(datetime.date.today())
            for child in self.container.winfo_children():
                if isinstance(child, ttk.Frame):
                    for label in child.winfo_children():
                        if isinstance(label, ttk.Label):
                            text = label.cget("text")
                            if text and text.startswith(today_iso):
                                label.configure(style="Today.TLabel")
        except Exception as ex:
            self._show_error_message(str(ex))
        finally:
            # Remove spinner/progress bar
            self._progress.stop()
            self._progress.destroy()

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

    def _show_day_details(self, date_iso: str, menu_map, health_map, appt_map):
        dlg = tk.Toplevel(self)
        dlg.title(f"Details for {date_iso}")
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()
        dlg.resizable(False, False)

        frm = ttk.Frame(dlg, padding=8)
        frm.pack(fill="both", expand=True)

        def add_section(label, items, icon=""):
            if items:
                ttk.Label(frm, text=f"{icon} {label}:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(6,0))
                for item in items:
                    ttk.Label(frm, text=f"  {item}", wraplength=400).pack(anchor="w")

        add_section("Menu", menu_map.get(date_iso, []), "🍽")
        add_section("Health", health_map.get(date_iso, []), "🩺")
        add_section("Appointments", appt_map.get(date_iso, []), "📌")

        ttk.Button(frm, text="Close", command=dlg.destroy).pack(anchor="e", pady=(12,0))

    def _move_calendar_left(self, event=None):
        self._move_day(-1)

    def _move_calendar_right(self, event=None):
        self._move_day(1)

    def _move_calendar_up(self, event=None):
        self._move_day(-7)

    def _move_calendar_down(self, event=None):
        self._move_day(7)

    def _move_day(self, delta):
        try:
            y = int(self.year_var.get())
            m = int(self.month_var.get())
            d = getattr(self, "selected_day", datetime.date.today())
            new_date = d + datetime.timedelta(days=delta)
            self.year_var.set(str(new_date.year))
            self.month_var.set(str(new_date.month))
            self.selected_day = new_date
            self.refresh()
        except Exception:
            pass

    def _show_error_message(self, msg):
        tk.messagebox.showerror("Calendar Error", msg, parent=self.winfo_toplevel())
