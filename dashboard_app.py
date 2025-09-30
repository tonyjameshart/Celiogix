# path: dashboard_app.py
from __future__ import annotations

import logging
import sys
from typing import Any, Protocol

from app import App
from panels import CookbookPanel, MenuPanel
from services.themes import get_active_theme_name, make_theme_instance  # theme façade


class _Closable(Protocol):
    def close(self) -> None: ...  # minimal protocol for .close()


def _safe_close(obj: Any | None) -> None:
    """Close if it looks closable; ignore close errors.
    Why: shutdown should not crash the GUI teardown.
    """
    try:
        if obj is not None and hasattr(obj, "close"):
            obj.close()
    except Exception:
        pass


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    app: App | None = None
    try:
        # 1) Construct the app/root first
        app = App()

        # 2) Initialize & apply the active theme
        app.theme = make_theme_instance(get_active_theme_name())
        app.theme.apply(app)  # ensures styles before panels mount

        # 3) Build panels
        app.cookbook_panel = CookbookPanel(master=app, app=app)
        app.menu_panel = MenuPanel(master=app, app=app)

        # 4) Go!
        app.mainloop()
        return 0

    except KeyboardInterrupt:
        # graceful interrupt during startup or loop
        return 130  # standard for SIGINT

    finally:
        if app is not None:
            # Close DB first so widgets using it don't try to access after destroy.
            _safe_close(getattr(app, "db", None))
            try:
                app.destroy()
            except Exception:
                # Tk can raise during late teardown; ignore to avoid masking real errors.
                pass


if __name__ == "__main__":
    sys.exit(main())
