# panels/base_panel.py
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Iterable, List, Tuple, Optional, Any, Dict

# Theme services (provides make_theme_instance/get_active_theme_name)
# Falls back gracefully if services are unavailable during early boot.
try:
    from services.themes import make_theme_instance, get_active_theme_name  # theme façade
except Exception:  # pragma: no cover
    make_theme_instance = None
    get_active_theme_name = None

# Column spec: (key, heading, width, anchor) where anchor in {"w","e","c"}
ColumnDef = Tuple[str, str, int, str]
_ANCHOR = {"w": tk.W, "e": tk.E, "c": tk.CENTER}


class BasePanel(tk.Frame):
    """
    Common panel base with shared UI builders:
      - build_search_bar(): compact 'Search' label + Entry + optional refresh button
      - make_treeview(): standardized Treeview with scrollbars and column setup
      - bind_edit_on_double_click(): wire double-click to edit_selected() (or a handler)
      - confirm_delete(): Yes/No helper for bulk delete prompts
      - set_status(): proxy to app.set_status
    Panels should subclass this and implement build().
    """
    def __init__(self, master, app, **kw):
        super().__init__(master, **kw)
        self.app = app
        self.db = app.db
        self.bus = getattr(app, "bus", None)

        # Prefer an app-provided theme; otherwise initialize from active theme.
        self.theme = getattr(app, "theme", None)
        if self.theme is None and make_theme_instance and get_active_theme_name:
            try:
                self.theme = make_theme_instance(get_active_theme_name())
                # stash back on app so other panels share it
                setattr(self.app, "theme", self.theme)
                # apply to the toplevel immediately
                self.theme.apply(self.winfo_toplevel())
            except Exception:
                # Don’t crash panels if theming isn’t ready
                pass

        self._widgets: Dict[str, Any] = {}
        self.build()

    # ---------- lifecycle ----------
    def build(self) -> None:  # to be overridden by subclasses
        pass

    # ---------- messaging ----------
    def show_info(self, title, message):
        messagebox.showinfo(title, message, parent=self.winfo_toplevel())

    def show_error(self, title, message):
        messagebox.showerror(title, message, parent=self.winfo_toplevel())

    def confirm_delete(self, count):
        return messagebox.askyesno("Delete", f"Delete {count} item(s)?", parent=self.winfo_toplevel())

    def set_status(self, msg: str):
        if hasattr(self.app, "set_status") and callable(self.app.set_status):
            self.app.set_status(msg)

    # ---------- shared builders ----------
    def build_search_bar(
        self,
        parent: Optional[tk.Misc] = None,
        *,
        label: str = "Search",
        width: int = 36,
        on_return: Optional[Callable[[str], None]] = None,
        add_refresh_button: bool = True,
        refresh_text: str = "Refresh",
        padding: Tuple[int, int] = (8, 4),
    ) -> Tuple[ttk.Frame, tk.StringVar, ttk.Entry]:
        """
        Create a compact search row.
        Returns (frame, var, entry). Bind <Return> to on_return if provided.
        """
        host = parent or self
        sp = getattr(getattr(self, "theme", None), "spacing", {"md": 8, "sm": 4})
        frm = ttk.Frame(host, padding=(sp.get("md", 8), sp.get("sm", 4)), style="Card.TFrame")
        lbl = ttk.Label(frm, text=label)
        var = tk.StringVar()
        ent = ttk.Entry(frm, textvariable=var, width=width)

        lbl.grid(row=0, column=0, sticky="e")
        ent.grid(row=0, column=1, sticky="w", padx=(6, 8))

        if on_return:
            ent.bind("<Return>", lambda _e: on_return(var.get()))

        if add_refresh_button:
            btn = ttk.Button(frm, text=refresh_text, command=lambda: on_return and on_return(var.get()))
            btn.grid(row=0, column=2, padx=(0, 6))
            self._widgets["search_refresh_btn"] = btn

        self._widgets["search_frame"] = frm
        self._widgets["search_var"] = var
        self._widgets["search_entry"] = ent
        return frm, var, ent

    def make_treeview(
        self,
        parent: Optional[tk.Misc],
        columns: List[ColumnDef],
        *,
        selectmode: str = "extended",
        show_headings: bool = True,
        bind_double_click: bool = True,
        tree_key: str = "tree",
    ) -> ttk.Treeview:
        """
        Create a Treeview with vertical & horizontal scrollbars and configured columns.
        Returns the Treeview instance.
        """
        if parent is None:
            parent = self
        sp = getattr(getattr(self, "theme", None), "spacing", {"md": 8, "sm": 4})
        frame = ttk.Frame(parent, padding=(sp.get("md", 8), sp.get("sm", 4)), style="Card.TFrame")
        frame.grid(row=0, column=0, sticky="nsew")
        # Make parent area resizable by default
        try:
            parent.grid_rowconfigure(0, weight=1)
            parent.grid_columnconfigure(0, weight=1)
        except Exception:
            pass

        col_keys = [c[0] for c in columns]
        tv = ttk.Treeview(
            frame,
            columns=col_keys,
            show="headings" if show_headings else "tree",
            selectmode=selectmode,
        )
        tv.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        for key, heading, width, anc in columns:
            tv.heading(key, text=heading, anchor=_ANCHOR.get(anc, tk.W))
            tv.column(
                key,
                width=width,
                anchor=_ANCHOR.get(anc, tk.W),
                stretch=(key in {c[0] for c in columns if c[3] in ("w", "c")}),
            )

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tv.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tv.xview)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tv.configure(yscroll=vsb.set, xscroll=hsb.set)

        if bind_double_click:
            # If subclass defines edit_selected(), use it by default
            handler = getattr(self, "edit_selected", None)
            if callable(handler):
                tv.bind("<Double-1>", lambda _e: handler())

        self._widgets[tree_key] = tv
        self._widgets[f"{tree_key}_frame"] = frame
        return tv

    def freeze_treeview_size(self, tree_key: str = "tree") -> None:
        """
        Stop a Treeview from resizing with the window:
          - make columns non-stretch
          - lock the wrapper frame’s size
          - remove 'nsew' stickiness
          - set that grid row/col weight to 0
        Works with trees created via make_treeview() (uses *_frame key).
        """
        tv = self._widgets.get(tree_key)
        frame = self._widgets.get(f"{tree_key}_frame")
        if not isinstance(tv, ttk.Treeview) or frame is None:
            return

        # 1) Make columns fixed width (no stretch)
        cols = tv.cget("columns")
        for c in cols:
            try:
                tv.column(c, stretch=False)
            except Exception:
                pass

        # 2) Compute a sensible fixed pixel width/height for wrapper frame
        frame.update_idletasks()
        try:
            total_w = sum(int(tv.column(c, "width")) for c in cols) + 24  # scrollbar allowance
        except Exception:
            total_w = tv.winfo_reqwidth()
        total_h = tv.winfo_reqheight() + 18  # header + hscroll allowance

        # 3) Lock the frame size and stop geometry propagation
        try:
            frame.configure(width=total_w, height=total_h)
            frame.grid_propagate(False)
        except Exception:
            pass

        # 4) Remove 'nsew' stickiness on the frame (keep it top-left)
        info = {}
        try:
            info = frame.grid_info()
            frame.grid(sticky="nw")
        except Exception:
            pass

        # 5) Ensure that grid cell doesn’t expand
        parent = frame.master
        try:
            r = int(info.get("row", 0))
            c = int(info.get("column", 0))
            parent.grid_rowconfigure(r, weight=0)
            parent.grid_columnconfigure(c, weight=0)
        except Exception:
            pass


    def bind_edit_on_double_click(self, tv: ttk.Treeview, handler: Optional[Callable[[], None]] = None) -> None:
        """
        Bind a double-click handler for a given Treeview. Defaults to self.edit_selected().
        """
        fn = handler or getattr(self, "edit_selected", None)
        if callable(fn):
            tv.bind("<Double-1>", lambda _e: fn())

    # ---------- convenience helpers ----------
    def get_search_text(self) -> str:
        var = self._widgets.get("search_var")
        return var.get().strip() if isinstance(var, tk.StringVar) else ""

    def clear_tree(self, tv: Optional[ttk.Treeview] = None) -> None:
        tv = tv or self._widgets.get("tree")
        if isinstance(tv, ttk.Treeview):
            for item in tv.get_children():
                tv.delete(item)
