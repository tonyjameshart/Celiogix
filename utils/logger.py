from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Final

APP_NAME: Final = "Celiogix"


def log_dir() -> Path:
    base = Path(os.getenv("CELIOGIX_LOGDIR") or Path.home() / f".{APP_NAME.lower()}")
    base.mkdir(parents=True, exist_ok=True)
    return base


def init_logging(level: int = logging.INFO) -> Path:
    p = log_dir() / "app.log"
    if getattr(init_logging, "_inited", False):
        return p

    root = logging.getLogger()
    root.setLevel(level)

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s :: %(message)s")

    fh = logging.FileHandler(p, encoding="utf-8")
    fh.setFormatter(fmt)
    root.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    root.addHandler(ch)

    logging.getLogger(APP_NAME).info("Logging initialized at %s", p)
    init_logging._inited = True
    return p
