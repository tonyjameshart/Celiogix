# path: utils/csvio.py
from __future__ import annotations

from collections.abc import Iterable, Mapping
import csv
import datetime as _dt
from pathlib import Path
from typing import Any

# Default alias map used by read/write helpers (extend per-call if needed)
DEFAULT_ALIASES: dict[str, str] = {
    # pantry common
    "net.wt": "net_weight",
    "net wt": "net_weight",
    "net_wt": "net_weight",
    "net weight": "net_weight",
    "gf": "gf_flag",
    # general normalizations
    "qty": "quantity",
    "amount": "quantity",
    "cat": "category",
    "sub cat": "subcategory",
    "sub-cat": "subcategory",
    "sub_category": "subcategory",
}


def _norm_key(k: str) -> str:
    return (k or "").strip().lower()


def merge_aliases(*maps: Mapping[str, str]) -> dict[str, str]:
    """Left-to-right merge of alias maps; later maps override earlier ones."""
    out: dict[str, str] = {}
    for m in maps:
        for k, v in m.items():
            out[_norm_key(k)] = v.strip()
    return out


def normalize_headers(
    headers: Iterable[str], aliases: Mapping[str, str] | None = None
) -> list[str]:
    """
    Normalize a header list:
      - lowercases/strips
      - applies alias mapping (e.g., 'Net.Wt' -> 'net_weight')
    """
    amap = merge_aliases(DEFAULT_ALIASES, aliases or {})
    normed: list[str] = []
    for h in headers:
        base = _norm_key(h)
        normed.append(amap.get(base, base))
    return normed


def normalize_row_keys(
    row: Mapping[str, Any], aliases: Mapping[str, str] | None = None
) -> dict[str, Any]:
    """Return a new dict with normalized keys via normalize_headers()."""
    amap = merge_aliases(DEFAULT_ALIASES, aliases or {})
    out: dict[str, Any] = {}
    for k, v in row.items():
        key = amap.get(_norm_key(k), _norm_key(k))
        out[key] = v
    return out


# --------------------------
# Safe parsers (shared)
# --------------------------
def parse_float(val: Any, default: float = 0.0) -> float:
    try:
        s = str(val).strip()
        if s == "":
            return default
        return float(s)
    except Exception:
        return default


def parse_int(val: Any, default: int = 0) -> int:
    try:
        s = str(val).strip()
        if s == "":
            return default
        return int(float(s))  # accept "1.0"
    except Exception:
        return default


def parse_bool(val: Any, default: bool = False) -> bool:
    s = str(val).strip().lower()
    if s in {"1", "true", "t", "yes", "y"}:
        return True
    if s in {"0", "false", "f", "no", "n"}:
        return False
    return default


def parse_iso_date(val: Any, default: str = "") -> tuple[str, bool]:
    """
    Accept a variety of common date formats and return ISO 'YYYY-MM-DD'.
    Returns (value, ok).
    """
    s = str(val or "").strip()
    if not s:
        return default, True
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%Y/%m/%d", "%d-%b-%Y", "%b %d, %Y"):
        try:
            dt = _dt.datetime.strptime(s, fmt).date()
            return dt.isoformat(), True
        except Exception:
            pass
    # Try to parse year-month only (YYYY-MM)
    try:
        if len(s) == 7 and s[4] in "-/":
            y, m = int(s[:4]), int(s[5:7])
            return _dt.date(y, m, 1).isoformat(), True
    except Exception:
        pass
    return default, False


# --------------------------
# Reading & writing
# --------------------------
def read_csv_rows(
    path: str | Path,
    aliases: Mapping[str, str] | None = None,
    *,
    keep_unknown_headers: bool = True,
) -> tuple[list[str], list[dict[str, Any]]]:
    """
    Read CSV with UTF-8 BOM handling, normalize headers with aliases,
    and return (headers, rows) where headers are normalized names.
    """
    p = Path(path)
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return [], []
        norm_headers = normalize_headers(reader.fieldnames, aliases)

        rows: list[dict[str, Any]] = []
        for raw in reader:
            norm = {}
            for raw_key, value in raw.items():
                key = _norm_key(raw_key)
                key = merge_aliases(DEFAULT_ALIASES, aliases or {}).get(key, key)
                # If header was unknown and we drop unknowns, skip
                if not keep_unknown_headers and key not in norm_headers:
                    continue
                norm[key] = value
            rows.append(norm)
        return norm_headers, rows


def write_csv_rows(
    path: str | Path, headers: Iterable[str], rows: Iterable[Mapping[str, Any]]
) -> None:
    """
    Write rows to CSV with UTF-8 encoding and correct newline handling on Windows.
    Headers are written exactly as provided.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(headers), extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def export_table_to_csv(
    path: str | Path, headers: list[str], records: Iterable[Iterable[Any]]
) -> None:
    """
    Convenience writer for already-ordered data (e.g., DB cursor tuples).
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)
        for rec in records:
            w.writerow(list(rec))
