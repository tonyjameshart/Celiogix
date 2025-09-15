# path: dashboard_app.py
from __future__ import annotations

import sys
import logging
from typing import Any, Optional, Protocol

from app import App


class _Closable(Protocol):
    def close(self) -> None: ...  # minimal protocol for .close()


def _safe_close(obj: Optional[Any]) -> None:
    """Close if it looks closable; ignore close errors.
    Why: shutdown should not crash the GUI teardown.
    """
    try:
        if obj is not None and hasattr(obj, "close"):
            getattr(obj, "close")()
    except Exception:
        pass


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    app: Optional[App] = None
    try:
        app = App()
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
