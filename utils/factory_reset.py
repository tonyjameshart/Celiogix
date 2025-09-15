# utils/factory_reset.py
from __future__ import annotations
import os, sys, sqlite3, shutil, zipfile
from pathlib import Path
from datetime import datetime
from typing import Iterable, Optional

def _nowstamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")

def _safe(path: Optional[str]) -> Optional[Path]:
    return Path(path) if path else None

def _db_files(conn: sqlite3.Connection, explicit_db: Path | None) -> list[Path]:
    """
    Return [app.db, app.db-wal?, app.db-shm?] if present.
    Uses live connection to discover the main DB path unless explicit_db is given.
    """
    main_db = explicit_db
    if main_db is None:
        row = next((r for r in conn.execute("PRAGMA database_list") if r[1] == "main"), None)
        if row and row[2]:
            main_db = _safe(row[2])
    if not main_db:
        raise RuntimeError("Could not resolve database path (is it in-memory?)")
    files = [main_db]
    for suffix in ("-wal", "-shm"):
        p = _safe(str(main_db) + suffix)
        if p and p.exists():
            files.append(p)
    return files

def _zip_paths(zip_path: Path, paths: Iterable[Path]) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            if not p.exists():
                continue
            if p.is_file():
                zf.write(p, arcname=p.name)
            else:
                # zip directory contents, keeping top-level folder name for clarity
                for sub in p.rglob("*"):
                    if sub.is_file():
                        zf.write(sub, arcname=p.name + "/" + sub.relative_to(p).as_posix())

def factory_reset(
    conn: sqlite3.Connection,
    *,
    project_root: Path | None = None,
    explicit_db_path: Path | None = None,
    backup: bool = True,
    wipe_logs: bool = False,
    wipe_exports: bool = False,
    logger=None,
    restart_after: bool = True,
) -> Path:
    """
    Perform a factory reset:
      - optional backup (db + optional logs/exports) into backups/FactoryReset-<timestamp>.zip
      - checkpoint WAL, close connection
      - remove app.db (+ wal/shm)
      - optionally wipe logs & exports
      - optionally restart the current process

    Returns the backup zip path (even if backup=False it returns the would-be path for logging).
    Raises on errors; UI should catch and show a messagebox.
    """
    pr = project_root or Path(__file__).resolve().parents[1]
    data_dir = pr / "data"
    log_dir = data_dir / "log"
    export_dir = pr / "export"
    backups_dir = pr / "backups"
    backups_dir.mkdir(parents=True, exist_ok=True)

    # Discover DB files while connection is live
    db_files = _db_files(conn, explicit_db_path)

    # Try to flush WAL safely (ignore if not in WAL)
    try:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    except sqlite3.OperationalError:
        pass

    # Backup (best-effort; continues if backup fails)
    backup_zip = backups_dir / f"FactoryReset-{_nowstamp()}.zip"
    if backup:
        try:
            to_backup = list(db_files)
            if wipe_logs and log_dir.exists():
                to_backup.append(log_dir)
            if wipe_exports and export_dir.exists():
                to_backup.append(export_dir)
            _zip_paths(backup_zip, to_backup)
            if logger: logger.info("Backup created at %s", backup_zip)
        except Exception as e:
            if logger: logger.exception("Backup failed (continuing with reset): %s", e)

    # Close DB cleanly
    try:
        conn.close()
    except Exception:
        pass

    # Delete DB files
    for p in db_files:
        try:
            if p.exists():
                p.unlink()
                if logger: logger.info("Deleted %s", p)
        except PermissionError as e:
            raise RuntimeError(f"Could not delete {p} (is the app still holding a lock?): {e}") from e

    # Optionally wipe logs & exports
    if wipe_logs and log_dir.exists():
        shutil.rmtree(log_dir, ignore_errors=True)
        log_dir.mkdir(parents=True, exist_ok=True)
        if logger: logger.info("Wiped logs at %s", log_dir)

    if wipe_exports and export_dir.exists():
        shutil.rmtree(export_dir, ignore_errors=True)
        export_dir.mkdir(parents=True, exist_ok=True)
        if logger: logger.info("Wiped exports at %s", export_dir)

    # Restart (best effort)
    if restart_after:
        if logger: logger.info("Restarting application process...")
        try:
            # Re-launch same interpreter with same args
            os.environ["CELIOGIX_JUST_RESET"] = "1"
            if getattr(sys, "frozen", False):
                # pyinstaller/packaged exe path
                exe = sys.executable
                os.spawnl(os.P_NOWAIT, exe, exe, *sys.argv[1:])
            else:
                os.spawnl(os.P_NOWAIT, sys.executable, sys.executable, *sys.argv)
            os._exit(0)  # immediate exit of current process
        except Exception as e:
            # If restart fails, just return; UI can prompt user to reopen manually
            if logger: logger.exception("Automatic restart failed: %s", e)

    return backup_zip
