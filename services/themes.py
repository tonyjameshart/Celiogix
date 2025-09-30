# path: services/themes.py
from __future__ import annotations

from typing import Any

from utils.theme import Theme
from utils.theme import delete_theme as _delete
from utils.theme import get_active_theme_name as _get_active
from utils.theme import get_theme as _get
from utils.theme import list_themes as _list
from utils.theme import save_theme as _save
from utils.theme import set_active_theme as _set_active


def list_theme_names() -> list[str]:
    return list(_list().keys())


def get_theme(name: str | None = None) -> dict[str, Any]:
    return _get(name)


def save_theme(theme: dict[str, Any]) -> None:
    _save(theme)


def delete_theme(name: str) -> None:
    _delete(name)


def set_active_theme(name: str) -> None:
    _set_active(name)


def get_active_theme_name() -> str:
    return _get_active()


def make_theme_instance(name: str | None = None) -> Theme:
    return Theme(_get(name))
