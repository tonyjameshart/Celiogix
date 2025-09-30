# path: utils/scroll.py
from __future__ import annotations

import tkinter as tk
from tkinter import ttk


def _frame_bg(widget: tk.Widget) -> str:
    try:
        st = ttk.Style(widget)
        return st.lookup("TFrame", "background") or st.lookup(".", "background") or "#ffffff"
    except Exception:
        return "#ffffff"


class ScrollFrame(ttk.Frame):
    """
    A scrollable container with both vertical and horizontal scrollbars.
    Place your real content inside .content (a ttk.Frame).
    """

    def __init__(self, parent, *, autohide: bool = False) -> None:
        super().__init__(parent)

        bg = _frame_bg(self)

        self.canvas = tk.Canvas(self, highlightthickness=0, borderwidth=0, background=bg)
        self.vbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.hbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self._yset, xscrollcommand=self._xset)

        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vbar.grid(row=0, column=1, sticky="ns")
        self.hbar.grid(row=1, column=0, sticky="ew")

        # content frame
        self.content = ttk.Frame(self, style="Content.TFrame")
        self._win = self.canvas.create_window(0, 0, window=self.content, anchor="nw")

        # Keep scrollregion updated
        self.content.bind("<Configure>", self._on_content_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Mousewheel
        self.content.bind("<Enter>", lambda e: self._bind_wheel(True))
        self.content.bind("<Leave>", lambda e: self._bind_wheel(False))

        self._autohide = autohide
        self._maybe_hide_bars()

    # --- layout/scroll helpers ---
    def _on_content_configure(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._maybe_hide_bars()

    def _on_canvas_configure(self, event):
        if self.canvas.bbox(self._win):
            self.canvas.coords(self._win, 0, 0)

    def _yset(self, first, last):
        self.vbar.set(first, last)
        self._maybe_hide_bars()

    def _xset(self, first, last):
        self.hbar.set(first, last)
        self._maybe_hide_bars()

    def _maybe_hide_bars(self):
        if not self._autohide:
            return
        try:
            vfirst, vlast = map(float, self.vbar.get())
            hfirst, hlast = map(float, self.hbar.get())
        except Exception:
            vfirst = vlast = hfirst = hlast = 0.0
        self.vbar.grid_remove() if (vlast - vfirst) >= 0.999 else self.vbar.grid()
        self.hbar.grid_remove() if (hlast - hfirst) >= 0.999 else self.hbar.grid()

    def _bind_wheel(self, on: bool):
        t = self.canvas
        if on:
            t.bind_all("<MouseWheel>", self._on_mousewheel_y, add="+")
            t.bind_all("<Shift-MouseWheel>", self._on_mousewheel_x, add="+")
            t.bind_all("<Button-4>", self._on_linux_up, add="+")
            t.bind_all("<Button-5>", self._on_linux_down, add="+")
        else:
            t.unbind_all("<MouseWheel>")
            t.unbind_all("<Shift-MouseWheel>")
            t.unbind_all("<Button-4>")
            t.unbind_all("<Button-5>")

    def _on_mousewheel_y(self, event):
        self.canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

    def _on_mousewheel_x(self, event):
        self.canvas.xview_scroll(-1 if event.delta > 0 else 1, "units")

    def _on_linux_up(self, _event):
        self.canvas.yview_scroll(-1, "units")

    def _on_linux_down(self, _event):
        self.canvas.yview_scroll(1, "units")
