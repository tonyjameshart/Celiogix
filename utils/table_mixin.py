# path: utils/table_mixin.py
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from typing import Iterable, Mapping, Tuple


class BaseTableMixin:
    """Shared Treeview behavior: scrollbars, wheel, autosize, bindings."""

    # ---- Build a scrolling Treeview like Health Log ----
    def make_scrolling_tree(
        self,
        parent: tk.Misc,
        columns: Iterable[str],
        *,
        show: str = "headings",
        selectmode: str = "extended",
        height: int | None = None,
    ) -> Tuple[ttk.Frame, ttk.Treeview, ttk.Scrollbar, ttk.Scrollbar]:
        wrap = ttk.Frame(parent)
        wrap.grid_rowconfigure(0, weight=1)
        wrap.grid_columnconfigure(0, weight=1)

        tv = ttk.Treeview(wrap, columns=list(columns), show=show, selectmode=selectmode)
        if height is not None:
            tv.configure(height=height)
        tv.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(wrap, orient="vertical", command=tv.yview)
        hsb = ttk.Scrollbar(wrap, orient="horizontal", command=tv.xview)
        tv.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.bind_mouse_wheel(tv)
        self.bind_home_end(tv)
        return wrap, tv, vsb, hsb

    # ---- Wheel like Health Log ----
    def bind_mouse_wheel(self, tree: ttk.Treeview) -> None:
        def _on_wheel(e):
            delta = -1 if e.delta > 0 else 1  # Win/mac
            tree.yview_scroll(delta, "units")
            return "break"
        tree.bind("<MouseWheel>", _on_wheel, add=True)
        tree.bind("<Button-4>", lambda e: (tree.yview_scroll(-1, "units"), "break"), add=True)  # X11
        tree.bind("<Button-5>", lambda e: (tree.yview_scroll(+1, "units"), "break"), add=True)

    # ---- Home/End navigation ----
    def bind_home_end(self, tree: ttk.Treeview) -> None:
        def _goto_edge(last: bool) -> str:
            kids = tree.get_children("")
            if not kids:
                return "break"
            item = kids[-1] if last else kids[0]
            tree.selection_set(item); tree.focus(item); tree.see(item)
            return "break"
        tree.bind("<Home>", lambda e: _goto_edge(False), add=True)
        tree.bind("<End>",  lambda e: _goto_edge(True),  add=True)

    # ---- Fast autosize (samples rows) ----
    def autosize_tree_columns(
        self,
        tree: ttk.Treeview,
        *,
        sample: int = 2000,
        pad: int = 24,
        min_px: int = 56,
        max_px: int = 900,
        max_px_map: Mapping[str, int] | None = None,
    ) -> None:
        try:
            fnt = tkfont.nametofont(tree.cget("font"))
        except tk.TclError:
            fnt = tkfont.nametofont("TkDefaultFont")

        cols: list[str] = list(tree["columns"])
        kids = list(tree.get_children(""))

        if kids and len(kids) > sample:
            step = len(kids) / float(sample)
            idxs = [min(len(kids) - 1, int(i * step)) for i in range(sample)]
            sample_ids = [kids[i] for i in idxs]
        else:
            sample_ids = kids

        cache = {iid: tree.item(iid, "values") for iid in sample_ids}
        caps = dict(max_px_map or {})

        for idx, col in enumerate(cols):
            header_text = tree.heading(col).get("text", "") or str(col)
            max_text_px = fnt.measure(header_text)
            for iid in sample_ids:
                vals = cache[iid]
                if idx < len(vals):
                    w = fnt.measure(str(vals[idx]))
                    if w > max_text_px:
                        max_text_px = w
            cap = int(caps.get(col, max_px))
            width = max(min_px, min(max_text_px + pad, cap))
            tree.column(col, width=width, stretch=False, anchor="w")

    # ---- Exact autosize (scans all rows) ----
    def autosize_tree_columns_exact(
        self,
        tree: ttk.Treeview,
        *,
        pad: int = 24,
        min_px: int = 56,
        max_px: int = 2000,
        max_px_map: Mapping[str, int] | None = None,
    ) -> None:
        tree.update_idletasks()
        try:
            fnt = tkfont.nametofont(tree.cget("font"))
        except tk.TclError:
            fnt = tkfont.nametofont("TkDefaultFont")

        cols: list[str] = list(tree["columns"])
        items = list(tree.get_children(""))
        caps = dict(max_px_map or {})

        for idx, col in enumerate(cols):
            header_text = tree.heading(col).get("text", "") or str(col)
            max_text_px = fnt.measure(header_text)
            for iid in items:
                vals = tree.item(iid, "values")
                if idx < len(vals):
                    w = fnt.measure(str(vals[idx]))
                    if w > max_text_px:
                        max_text_px = w
            cap = int(caps.get(col, max_px))
            width = max(min_px, min(max_text_px + pad, cap))
            tree.column(col, width=width, stretch=False, anchor="w")

    # ---- Convenience ----
    def fit_columns_now(
        self,
        tree: ttk.Treeview,
        *,
        exact: bool = True,
        max_px_map: Mapping[str, int] | None = None,
    ) -> None:
        if exact:
            self.autosize_tree_columns_exact(tree, max_px_map=max_px_map)
        else:
            self.autosize_tree_columns(tree, max_px_map=max_px_map)
