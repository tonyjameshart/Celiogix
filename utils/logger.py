# utils/logger.py
from __future__ import annotations
import os, sys
from pathlib import Path
import logging, logging.config
from logging.handlers import RotatingFileHandler

def init_logging(log_path: str | Path | None = None, level: str | None = None) -> Path:
    # Build a safe path (no backslash-escapes) and ensure dirs exist
    project_root = Path(__file__).resolve().parents[1]  # adjust if this file moves
    default_log = project_root / "data" / "log" / "app.log"
    log_file = Path(os.getenv("CELIOGIX_LOG_FILE", log_path or default_log))
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # If the chosen path is unwritable, fall back to a temp location
    try:
        log_file.touch(exist_ok=True)
    except Exception:
        tmp_root = Path(os.getenv("TEMP", "/tmp"))
        log_file = tmp_root / "Celiogix" / "app.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        log_file.touch(exist_ok=True)

    # Configure logging (overrides any prior basicConfig)
    log_level = (os.getenv("CELIOGIX_LOG_LEVEL", level or "INFO")).upper()
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "std": {
                "format": "%(asctime)s.%(msecs)03dZ | %(levelname)s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S",
            }
        },
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "std", "stream": "ext://sys.stdout"},
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "std",
                "filename": str(log_file),
                "maxBytes": 2_000_000,
                "backupCount": 5,
                "encoding": "utf-8",
                "delay": True,  # create file on first write
            },
        },
        "root": {"level": log_level, "handlers": ["console", "file"]},
    })

    logging.getLogger(__name__).info("Logging initialized ? %s", log_file)
    return log_file
