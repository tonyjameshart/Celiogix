from __future__ import annotations

from contextlib import suppress
import logging
from pathlib import Path
import shutil
import sqlite3
import time


def _db_sidecars(db_path: Path) -> list[Path]:
    return [
        db_path,
        db_path.with_suffix(db_path.suffix + "-wal"),
        db_path.with_suffix(db_path.suffix + "-shm"),
    ]


def factory_reset(  # noqa: PLR0913
    conn: sqlite3.Connection,
    project_root: Path,
    backup: bool = True,
    wipe_logs: bool = False,
    wipe_exports: bool = False,
    logger: logging.Logger | None = None,
    restart_after: bool = False,
) -> Path | None:
    """Backup current DB to backups/ then delete DB and sidecars. Optionally wipe logs/exports."""
    with suppress(Exception):
        conn.close()

    data_dir = project_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    db_path = data_dir / "celiogix.db"

    backup_zip: Path | None = None
    if backup and db_path.exists():
        backups_dir = project_root / "backups"
        backups_dir.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        archive_base = backups_dir / f"backup-{stamp}"
        created = shutil.make_archive(archive_base.as_posix(), "zip", data_dir.as_posix())
        backup_zip = Path(created)

    for p in _db_sidecars(db_path):
        if p.exists():
            p.unlink(missing_ok=True)

    if wipe_logs:
        logdir = Path.home() / ".celiogix"
        if logdir.exists():
            shutil.rmtree(logdir, ignore_errors=True)

    if wipe_exports:
        exports = project_root / "exports"
        if exports.exists():
            shutil.rmtree(exports, ignore_errors=True)

    if logger:
        logger.info("Factory reset complete. Backup: %s", backup_zip)

    return backup_zip
