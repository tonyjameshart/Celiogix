# path: utils/logger.py
from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

_LOGGER: logging.Logger | None = None


def _log_path() -> str:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "logs"))
    os.makedirs(root, exist_ok=True)
    return os.path.join(root, "app.log")


def get_logger(name: str = "celiac") -> logging.Logger:
    """
    Global app logger (rotating file + stdout).
    Call once and reuse via `app.log` or `get_logger()`.
    """
    global _LOGGER
    if _LOGGER:
        return _LOGGER

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    # File (rotate ~1MB, keep 5 backups)
    fh = RotatingFileHandler(_log_path(), maxBytes=1_000_000, backupCount=5, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # Console
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    _LOGGER = logger
    return logger


def install_excepthook(logger: logging.Logger) -> None:
    """
    Log uncaught exceptions (outside Tk callbacks).
    """
    def hook(exc_type, exc, tb):
        logger.exception("Uncaught exception", exc_info=(exc_type, exc, tb))
        try:
            import traceback
            sys.stderr.write("Uncaught exception:\n" + "".join(traceback.format_exception(exc_type, exc, tb)))
        except Exception:
            pass
    sys.excepthook = hook


def attach_tk_reporter(logger: logging.Logger) -> None:
    """
    Log exceptions raised from Tkinter callbacks and show a friendly dialog.
    """
    def _report_callback_exception(self, exc, val, tb):
        logger.exception("Tk callback exception", exc_info=(exc, val, tb))
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Unexpected Error", f"{exc.__name__}: {val}")
        except Exception:
            pass

    try:
        import tkinter as tk
        tk.Misc.report_callback_exception = _report_callback_exception
    except Exception:
        # If Tk isn't available yet, do nothing.
        pass
