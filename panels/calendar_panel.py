# panels/calendar_panel.py

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import calendar, datetime
from .base_panel import BasePanel

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
        ttk.Spinbox(top, from_=1, to=12, textvariable=self.month_var, width=5, command=self.refresh).pack(side="right")
        ttk.Spinbox(top, from_=2000, to=2100, textvariable=self.year_var, width=7, command=self.refresh).pack(side="right")

        self.container = ttk.Frame(self); self.container.pack(fill="both", expand=True, padx=s["md"], pady=s["sm"])
        self.refresh()

    def refresh(self):
        for w in self.container.winfo_children():
            w.destroy()
        try:
            y = int(self.year_var.get()); m = int(self.month_var.get())
        except Exception:
            return
        cal = calendar.Calendar()
        weeks = cal.monthdatescalendar(y, m)

        cur = self.db.cursor()
        menus = cur.execute("SELECT date, meal_type FROM menu_plans").fetchall()
        health = cur.execute("SELECT date, symptoms FROM health_logs").fetchall()
        menu_map, health_map = {}, {}
        for r in menus:
            menu_map.setdefault(r["date"], []).append(r["meal_type"])
        for r in health:
            health_map.setdefault(r["date"], []).append((r["symptoms"] or "")[:24])

        for wk in weeks:
            row = ttk.Frame(self.container); row.pack(fill="x", expand=True)
            for d in wk:
                box = ttk.Frame(row, style="Card.TFrame", padding=6)
                box.pack(side="left", fill="both", expand=True, padx=4, pady=4)
                ttk.Label(box, text=str(d.day)).pack(anchor="ne")
                ds = d.strftime("%Y-%m-%d")
                for mt in menu_map.get(ds, []):
                    ttk.Label(box, text=f"🍽 {mt}", style="Muted.TLabel").pack(anchor="w")
                for s in health_map.get(ds, []):
                    ttk.Label(box, text=f"🩺 {s}", style="Muted.TLabel").pack(anchor="w")
