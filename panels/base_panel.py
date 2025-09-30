# path: panels/base_panel.py
from __future__ import annotations

from collections.abc import Callable
import contextlib
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Literal

from utils.table_mixin import BaseTableMixin  # provides make_scrolling_tree, fit_columns_now, autosize_tree_columns

ColumnDef = tuple[str, str, int, str]
_ANCHOR: dict[str, str] = {"w": "w", "e": "e", "c": "center"}


class BasePanel(BaseTableMixin, ttk.Frame):
    """Common helpers shared by panels."""

    def __init__(self, master: tk.Misc, app: Any, **kw: Any) -> None:
        super().__init__(master, **kw)
        self.app = app
        self.db: sqlite3.Connection | None = getattr(app, "db", None)
        if self.db is None:
            raise RuntimeError("App database is not initialized. Ensure App sets self.db before creating panels.")
        self._widgets: dict[str, Any] = {}
        self.build()

    # ---- to be overridden by panels ----
    def build(self) -> None:  # pragma: no cover
        pass

    # ---- UX helpers ----
    def set_status(self, msg: str) -> None:
        with contextlib.suppress(Exception):
            if hasattr(self.app, "set_status"):
                self.app.set_status(msg)

    def info(self, msg: str) -> None:
        self.set_status(msg)
        with contextlib.suppress(Exception):
            messagebox.showinfo("Info", msg, parent=self.winfo_toplevel())

    def warn(self, msg: str) -> None:
        self.set_status(msg)
        with contextlib.suppress(Exception):
            messagebox.showwarning("Warning", msg, parent=self.winfo_toplevel())

    def error(self, msg: str) -> None:
        self.set_status(msg)
        with contextlib.suppress(Exception):
            messagebox.showerror("Error", msg, parent=self.winfo_toplevel())

    def confirm_delete(self, count: int, *, title: str = "Confirm Delete") -> bool:
        plural = "s" if int(count) != 1 else ""
        msg = f"Delete {count} item{plural}?"
        return bool(
            messagebox.askyesno(
                title, msg, parent=self.winfo_toplevel(), default="no", icon="warning"
            )
        )

    # ---- lifecycle hook (kept for compatibility) ----
    def on_show(self) -> None:
        return

    # ---- Reusable UI builders ----
    def build_search_bar(  # noqa: PLR0913
        self,
        parent: tk.Misc | None = None,
        *,
        label: str = "Search",
        width: int = 36,
        on_return: Callable[[str], None] | None = None,
        add_refresh_button: bool = True,
        refresh_text: str = "Refresh",
        padding: tuple[int, int] = (8, 4),
    ) -> tuple[ttk.Frame, tk.StringVar, ttk.Entry]:
        """Simple search label + entry + optional refresh button."""
        parent = parent or self
        frm = ttk.Frame(parent)
        frm.grid_columnconfigure(2, weight=1)

        ttk.Label(frm, text=label).grid(row=0, column=0, padx=(0, 8), pady=padding, sticky="w")

        var = tk.StringVar()
        ent = ttk.Entry(frm, textvariable=var, width=width)
        ent.grid(row=0, column=1, pady=padding, sticky="w")

        if add_refresh_button:
            ttk.Button(frm, text=refresh_text, command=lambda: self.refresh() if hasattr(self, "refresh") else None).grid(
                row=0, column=3, padx=(8, 0), pady=padding, sticky="w"
            )

        if on_return is not None:
            ent.bind("<Return>", lambda _e: on_return(var.get().strip()), add=True)
        return frm, var, ent

    def make_treeview(  # noqa: PLR0913
        self,
        parent: tk.Misc | None,
        columns: list[ColumnDef],
        *,
        selectmode: Literal["extended", "browse", "none"] = "extended",
        height: int = 16,
        show: Literal["tree", "headings", "tree headings", ""] | None = None,
        show_headings: bool | None = None,
        add_scrollbars: bool = True,
        bind_double_click: bool = False,
        tree_key: str = "tree",
    ) -> ttk.Treeview:
        """Create a Treeview + optional scrollbars; registers in self._widgets."""
        parent = parent or self
        wrap = ttk.Frame(parent, padding=0)
        wrap.grid_rowconfigure(0, weight=1)
        wrap.grid_columnconfigure(0, weight=1)
        if show is None:
            show = "headings" if show_headings or show_headings is None else ""
        tv = ttk.Treeview(
            wrap,
            columns=[c[0] for c in columns],
            selectmode=selectmode,
            height=height,
            show=show,
        )
        tv.grid(row=0, column=0, sticky="nsew")
        for key, heading, width, anchor in columns:
            tv.heading(key, text=heading, anchor=_ANCHOR.get(anchor, "w"))
            tv.column(key, width=width, anchor=_ANCHOR.get(anchor, "w"), stretch=True)
        if add_scrollbars:
            vsb = ttk.Scrollbar(wrap, orient="vertical", command=tv.yview)
            hsb = ttk.Scrollbar(wrap, orient="horizontal", command=tv.xview)
            tv.configure(yscroll=vsb.set, xscroll=hsb.set)
            vsb.grid(row=0, column=1, sticky="ns")
            hsb.grid(row=1, column=0, sticky="ew")
        self._widgets[tree_key] = tv
        return tv
