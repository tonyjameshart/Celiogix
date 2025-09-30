# scripts/fix_json_encoding.py
"""
Fix JSON load failing with: "'utf-8' codec can't decode byte 0xe9 ...".

Strategy
- Try multiple common encodings (UTF-8/UTF-8-SIG/Windows-1252/Latin-1/MacRoman).
- Validate by actually parsing JSON for each successful decode.
- Optional: rewrite the file to canonical UTF-8 once successfully decoded.

Why this matters
- 0xE9 is 'é' in Windows-1252/Latin-1, invalid in UTF-8 at that position.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterable
import json
from pathlib import Path
from typing import Any

# Ordered by likelihood on Windows.
CANDIDATE_ENCODINGS: tuple[str, ...] = (
    "utf-8",
    "utf-8-sig",
    "cp1252",  # Windows-1252 (é = 0xE9)
    "latin-1",  # ISO-8859-1
    "mac_roman",
)


def try_load_json_bytes(data: bytes, encodings: Iterable[str]) -> tuple[Any, str, str]:
    """Return (obj, encoding, text) by attempting JSON parse under candidate encodings.

    Raises
    ------
    UnicodeDecodeError
        If decoding fails for all encodings.
    json.JSONDecodeError
        If decoded text never parses as JSON.
    """
    last_decode_error: Exception | None = None
    last_json_error: Exception | None = None
    last_text: str | None = None

    for enc in encodings:
        try:
            text = data.decode(enc)
            last_text = text
        except UnicodeDecodeError as e:  # not this encoding
            last_decode_error = e
            continue
        try:
            obj = json.loads(text)
            return obj, enc, text
        except json.JSONDecodeError as e:  # decodes but not valid JSON under this text
            last_json_error = e
            continue

    # Prefer surfacing JSON error if we *could* decode but JSON was malformed.
    if last_json_error is not None and last_text is not None:
        raise json.JSONDecodeError(
            msg=f"Decoded text (len={len(last_text)}) but JSON is invalid: {last_json_error.msg}",
            doc=last_text,
            pos=last_json_error.pos,
        ) from last_json_error

    # Otherwise, all decodes failed.
    if last_decode_error is not None:
        raise UnicodeDecodeError(
            encoding="unknown",
            object=data,
            start=0,
            end=min(1, len(data)),
            reason=f"All candidate encodings failed: {', '.join(encodings)}",
        ) from last_decode_error

    # Fallback guard; we should never reach here.
    raise RuntimeError("Unexpected state during encoding trials.")


def read_json_auto(path: Path) -> tuple[Any, str, str]:
    """Read bytes and return (json_obj, detected_encoding, decoded_text)."""
    raw = path.read_bytes()
    return try_load_json_bytes(raw, CANDIDATE_ENCODINGS)


def rewrite_utf8(path: Path, text: str, create_backup: bool = True) -> None:
    """Rewrite file as UTF-8 (no BOM). Backup as *.bak if requested."""
    if create_backup:
        bak = path.with_suffix(path.suffix + ".bak")
        if not bak.exists():
            bak.write_bytes(path.read_bytes())
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto-detect encoding and load/repair JSON.")
    parser.add_argument("file", type=Path, help="Path to JSON file")
    parser.add_argument(
        "--inplace",
        action="store_true",
        help="Rewrite the file in UTF-8 if decoding+parsing succeeds (creates .bak)",
    )
    parser.add_argument(
        "--print",
        dest="do_print",
        action="store_true",
        help="Print loaded JSON to stdout (pretty)",
    )
    args = parser.parse_args()

    path: Path = args.file
    if not path.exists():
        raise SystemExit(f"File not found: {path}")

    try:
        obj, enc, text = read_json_auto(path)
    except Exception as e:  # surface clear error to user
        raise SystemExit(f"Failed to load JSON with auto-encoding: {e}") from e

    print(f"Detected encoding: {enc}")

    if args.inplace:
        # Normalize to UTF-8 only if current enc is not already utf-8.
        if enc.lower() != "utf-8":
            rewrite_utf8(path, text)
            print(f"Rewritten in UTF-8: {path}")
        else:
            print("File already UTF-8; no rewrite performed.")

    if args.do_print:
        print(json.dumps(obj, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
