# path: utils/window.py
from __future__ import annotations
import tkinter as tk
from typing import Any

def set_default_geometry_once(app_or_root: Any, geometry: str = "1385x680") -> None:
    """
    Set the application window size once at startup.
    Call this from your App.__init__ after creating Tk().
    """
    try:
        root: tk.Misc
        if isinstance(app_or_root, tk.Tk):
            root = app_or_root
        else:
            # App instance that owns the Tk root
            root = app_or_root if isinstance(app_or_root, tk.Misc) else app_or_root.winfo_toplevel()

        if not getattr(app_or_root, "_window_default_set", False):
            root.geometry(geometry)
            setattr(app_or_root, "_window_default_set", True)
    except Exception:
        # Fail safe: never crash app on geometry set
        pass
