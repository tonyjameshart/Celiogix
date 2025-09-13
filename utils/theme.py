# path: utils/theme.py
from __future__ import annotations
import json
import os
from tkinter import ttk

# sensible defaults
_DEFAULT = {
    "bg": "#F7F9FC",
    "surface": "#FFFFFF",
    "surface2": "#F0F2F5",
    "text": "#2E3440",
    "muted": "#6B7280",
    "accent": "#4F9DDE",
    "accent2": "#7BCFA9",
    "border": "#D1D5DB",
    "danger": "#E63946",
    "warning": "#F4A261",
}

class Theme:
    def __init__(self, colors: dict | None = None):
        self.colors = dict(_DEFAULT)
        if colors:
            self.colors.update(colors)
        self.spacing = {"xs": 2, "sm": 4, "md": 8, "lg": 18}
        self.fonts = {
            "heading": ("Segoe UI", 12, "bold"),
            "title": ("Segoe UI", 11, "bold"),
            "base": ("Segoe UI", 10),
            "mono": ("Consolas", 10),
        }

    def apply(self, root):
        c = self.colors
        style = ttk.Style(root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        root.configure(bg=c.get("bg", "#FFFFFF"))
        style.configure(
            ".",
            background=c.get("surface", "#FFFFFF"),
            foreground=c.get("text", "#111111"),
            fieldbackground=c.get("surface2", "#F0F2F5"),
        )
        style.configure("TFrame", background=c.get("surface", "#FFFFFF"))
        style.configure(
            "Card.TFrame",
            background=c.get("surface2", "#F0F2F5"),
            borderwidth=1,
            relief="solid",
        )
        style.configure("TLabel", background=c.get("surface", "#FFFFFF"), foreground=c.get("text", "#111111"))
        style.configure("Muted.TLabel", background=c.get("surface", "#FFFFFF"), foreground=c.get("muted", "#6B7280"))
        style.configure("TButton", padding=(8, 4), background=c.get("surface2", "#F0F2F5"))
        style.configure(
            "Treeview",
            background=c.get("surface2", "#F0F2F5"),
            fieldbackground=c.get("surface2", "#F0F2F5"),
            foreground=c.get("text", "#111111"),
            bordercolor=c.get("border", "#D1D5DB"),
        )
        style.configure("Treeview.Heading", background=c.get("surface", "#FFFFFF"), foreground=c.get("text", "#111111"))

def load_theme_from_file(path: str | None = None) -> dict:
    """
    Load a colors dict from JSON. Tries, in order:
      1) explicit 'path' if provided
      2) 'data/themes.json'
      3) './themes.json'
    Accepts either:
      - a flat color dict (bg/surface/text/etc), or
      - a mapping of named themes (e.g., {'light': {...}, 'dark': {...}})
        in which case 'light' or the first mapping is chosen.
    Returns a dict merged over _DEFAULT.
    """
    candidates = [path] if path else [
        os.path.join("data", "themes.json"),
        "themes.json",
    ]
    for p in candidates:
        try:
            if not p or not os.path.exists(p):
                continue
            with open(p, "r", encoding="utf-8") as f:
                obj = json.load(f)
            # Flat dict that already looks like colors
            if isinstance(obj, dict) and ("bg" in obj or "surface" in obj or "text" in obj):
                return {**_DEFAULT, **obj}
            # Map of named themes (prefer 'light', then 'default', else first)
            if isinstance(obj, dict):
                for key in ("light", "default"):
                    if key in obj and isinstance(obj[key], dict):
                        return {**_DEFAULT, **obj[key]}
                for _, v in obj.items():
                    if isinstance(v, dict):
                        return {**_DEFAULT, **v}
        except Exception:
            # fall through to defaults if anything goes sideways
            pass
    return dict(_DEFAULT)
