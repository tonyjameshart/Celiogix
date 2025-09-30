# path: celiogix/panels/_bindings.py  (keyboard affordances)
from __future__ import annotations

from collections.abc import Callable
from tkinter import ttk


def bind_list_nav(
    tv: ttk.Treeview, on_delete: Callable[[], None], on_edit: Callable[[], None]
) -> None:
    tv.bind("<Delete>", lambda e: on_delete(), add=True)
    tv.bind("<Return>", lambda e: on_edit(), add=True)
    tv.bind("<F2>", lambda e: on_edit(), add=True)
    tv.bind("<Control-f>", lambda e: tv.event_generate("<<FocusSearch>>"), add=True)
