# path: services/themes.py
from __future__ import annotations

from typing import Any, Dict, List

from utils.theme import (
    list_themes as _list,
    get_theme as _get,
    save_theme as _save,
    delete_theme as _delete,
    set_active_theme as _set_active,
    get_active_theme_name as _get_active,
    Theme,
)

def list_theme_names() -> List[str]:
    return list(_list().keys())

def get_theme(name: str | None = None) -> Dict[str, Any]:
    return _get(name)

def save_theme(theme: Dict[str, Any]) -> None:
    _save(theme)

def delete_theme(name: str) -> None:
    _delete(name)

def set_active_theme(name: str) -> None:
    _set_active(name)

def get_active_theme_name() -> str:
    return _get_active()

def make_theme_instance(name: str | None = None) -> Theme:
    return Theme(_get(name))
