# path: utils/theme.py
from __future__ import annotations

from dataclasses import dataclass
import json
import os
import tkinter as tk
from tkinter import ttk
from typing import Any

# --------------------------------------------------------------------------------------
# Storage
# --------------------------------------------------------------------------------------

_PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
_THEME_PATH = os.path.join(_PROJECT_ROOT, "themes.json")

_DEFAULT_STORE = {
    "active": "Classic Light",
    "themes": {
        "Classic Light": {
            "name": "Classic Light",
            "colors": {
                "bg": "#FFFFFF",
                "surface": "#F7F7F9",
                "text": "#1F2937",
                "muted_text": "#6B7280",
                "border": "#E5E7EB",
                "accent": "#2563EB",
                "accent_fg": "#FFFFFF",
                "warning": "#F59E0B",
                "danger": "#DC2626",
                "zebra_even": "#FFFFFF",
                "zebra_odd": "#F6F7FB",
                "low_bg": "#FFE5E5",
                "low_fg": "#7F1D1D",
            },
            "fonts": {
                "base_family": "Segoe UI",
                "base_size": 10,
                "mono_family": "Consolas",
            },
            "spacing": {"xs": 2, "sm": 4, "md": 8, "lg": 12},
            "tree": {"row_height": 22},
        },
        "Classic Dark": {
            "name": "Classic Dark",
            "colors": {
                "bg": "#0F172A",
                "surface": "#111827",
                "text": "#E5E7EB",
                "muted_text": "#9CA3AF",
                "border": "#374151",
                "accent": "#60A5FA",
                "accent_fg": "#0B1020",
                "warning": "#FBBF24",
                "danger": "#F87171",
                "zebra_even": "#111827",
                "zebra_odd": "#0B1324",
                "low_bg": "#3B0D0D",
                "low_fg": "#FCA5A5",
            },
            "fonts": {
                "base_family": "Segoe UI",
                "base_size": 10,
                "mono_family": "Consolas",
            },
            "spacing": {"xs": 2, "sm": 4, "md": 8, "lg": 12},
            "tree": {"row_height": 22},
        },
    },
}


def _load_store() -> dict[str, Any]:
    if not os.path.exists(_THEME_PATH):
        return json.loads(json.dumps(_DEFAULT_STORE))
    try:
        with open(_THEME_PATH, encoding="utf-8") as f:
            data = json.load(f)
        # minimal normalization
        if not isinstance(data, dict) or "themes" not in data:
            raise ValueError("bad themes.json")
        data.setdefault("active", next(iter(data["themes"])) if data["themes"] else "Classic Light")
        return data
    except Exception:
        return json.loads(json.dumps(_DEFAULT_STORE))


def _save_store(store: dict[str, Any]) -> None:
    with open(_THEME_PATH, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)


# Public storage helpers


def list_themes() -> dict[str, dict[str, Any]]:
    return _load_store().get("themes", {})


def get_active_theme_name() -> str:
    return _load_store().get("active", "Classic Light")


def set_active_theme(name: str) -> None:
    store = _load_store()
    if name in store.get("themes", {}):
        store["active"] = name
        _save_store(store)


def save_theme(theme: dict[str, Any]) -> None:
    """Insert or overwrite by theme['name']."""
    name = (theme.get("name") or "").strip() or "Custom Theme"
    theme = dict(theme, name=name)
    store = _load_store()
    store.setdefault("themes", {})[name] = theme
    _save_store(store)


def delete_theme(name: str) -> None:
    store = _load_store()
    if name in store.get("themes", {}):
        del store["themes"][name]
        if store.get("active") == name:
            store["active"] = next(iter(store["themes"])) if store["themes"] else "Classic Light"
        _save_store(store)


def get_theme(name: str | None = None) -> dict[str, Any]:
    store = _load_store()
    if name is None:
        name = store.get("active") or "Classic Light"
    return store.get("themes", {}).get(name, _DEFAULT_STORE["themes"]["Classic Light"])


# --------------------------------------------------------------------------------------
# Runtime application
# --------------------------------------------------------------------------------------


@dataclass
class Theme:
    spec: dict[str, Any]

    # For existing code: Theme(...).spacing and .table_tag_colors()
    @property
    def spacing(self) -> dict[str, int]:
        sp = self.spec.get("spacing") or {}
        return {
            "xs": int(sp.get("xs", 2)),
            "sm": int(sp.get("sm", 4)),
            "md": int(sp.get("md", 8)),
            "lg": int(sp.get("lg", 12)),
        }

    def table_tag_colors(self) -> dict[str, dict[str, str]]:
        c = self.spec.get("colors") or {}
        return {
            "low": {
                "background": c.get("low_bg", "#FFE5E5"),
                "foreground": c.get("low_fg", "#7F1D1D"),
            },
            "ok": {},
            "zebra": {"background": c.get("zebra_odd", "#F6F7FB")},
        }

    def apply(self, widget: tk.Misc | None) -> None:
        """Apply ttk styles globally (clam theme) and adjust key components."""
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        c = self.spec.get("colors") or {}
        f = self.spec.get("fonts") or {}
        tree = self.spec.get("tree") or {}

        bg = c.get("bg", "#FFFFFF")
        surface = c.get("surface", "#F7F7F9")
        text = c.get("text", "#111827")
        muted = c.get("muted_text", "#6B7280")
        border = c.get("border", "#E5E7EB")
        accent = c.get("accent", "#2563EB")
        accent_fg = c.get("accent_fg", "#FFFFFF")

        base_family = f.get("base_family", "Segoe UI")
        base_size = int(f.get("base_size", 10))

        style.configure(".", background=bg, foreground=text, font=(base_family, base_size))
        style.configure("TFrame", background=bg)
        style.configure("Card.TFrame", background=surface, bordercolor=border, relief="flat")
        style.configure("TLabel", background=bg, foreground=text)
        style.configure("Muted.TLabel", background=bg, foreground=muted)
        style.configure(
            "TButton",
            padding=6,
            background=surface,
            foreground=text,
            bordercolor=border,
            focusthickness=2,
        )
        style.map("TButton", background=[("active", accent)], foreground=[("active", accent_fg)])

        # Treeview polish
        style.configure(
            "Treeview",
            background=surface,
            fieldbackground=surface,
            foreground=text,
            bordercolor=border,
            rowheight=int(tree.get("row_height", 22)),
        )
        style.configure(
            "Treeview.Heading", background=surface, foreground=muted, bordercolor=border
        )

        # Optional: apply bg to target widget tree
        if widget:
            try:
                widget.configure(style="TFrame")
            except Exception:
                pass
