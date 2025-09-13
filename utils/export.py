# path: utils/export.py
from __future__ import annotations
import os, sys, webbrowser
from pathlib import Path
from typing import Iterable, Mapping, Sequence, Tuple, Any, Optional, List, Dict
from html import escape as _e
from datetime import datetime as _dt

# columns: list of headings (strings) shown in the table
# rows: iterable of row dicts or sequences aligned to columns

_BASE_CSS = """
:root{
  --bg:#ffffff; --ink:#111827; --muted:#6b7280; --surface:#f3f4f6; --border:#e5e7eb; --accent:#2563eb;
  --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
  --sans: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial, "Noto Sans", "Liberation Sans", sans-serif;
}
*{box-sizing:border-box}
body{margin:24px auto; max-width:1100px; font: 14px/1.5 var(--sans); color:var(--ink); background:var(--bg)}
h1{font-size:22px; margin:0 0 4px 0}
h2{font-size:14px; color:var(--muted); font-weight:600; margin:0 0 18px 0}
.meta{display:flex; flex-wrap:wrap; gap:10px; margin:10px 0 14px 0; color:var(--muted)}
.meta .kv{background:var(--surface); border:1px solid var(--border); padding:6px 8px; border-radius:8px}
.tablewrap{overflow:auto; border:1px solid var(--border); border-radius:10px; background:var(--surface)}
table{width:100%; border-collapse:separate; border-spacing:0}
thead th{position:sticky; top:0; background:#fff; border-bottom:1px solid var(--border); font-weight:700; text-align:left; padding:10px 12px}
tbody td{border-bottom:1px solid var(--border); padding:10px 12px; vertical-align:top}
tbody tr:nth-child(odd) td{background:rgba(0,0,0,0.015)}
tfoot td{padding:10px 12px; color:var(--muted)}
.small{font-size:12px}
code{font-family:var(--mono)}
@media print{
  body{margin:0; max-width:none}
  .meta{display:none}
  thead th{background:#fff !important}
}
"""

def _now_iso():
    return _dt.now().strftime("%Y-%m-%d %H:%M:%S")

def _coerce_row(row: Any, columns: Sequence[str]) -> List[str]:
    # Accept dict-like or sequence-like rows
    if isinstance(row, Mapping):
        return [str(row.get(k, "")) for k in columns]
    try:
        return [str(x) for x in row]
    except Exception:
        return ["" for _ in columns]

def render_table_html(
    title: str,
    columns: Sequence[str],
    rows: Iterable[Any],
    *,
    subtitle: Optional[str] = None,
    meta: Optional[Mapping[str, Any]] = None,
) -> str:
    cols = [str(c) for c in columns]
    trs = []
    count = 0
    for r in rows:
        vals = _coerce_row(r, cols)
        tds = "".join(f"<td>{_e(v)}</td>" for v in vals)
        trs.append(f"<tr>{tds}</tr>")
        count += 1

    meta_html = ""
    meta_items = dict(meta or {})
    meta_items.setdefault("Generated", _now_iso())
    if meta_items:
        items = "".join(f'<div class="kv"><b>{_e(str(k))}:</b> {_e(str(v))}</div>' for k, v in meta_items.items())
        meta_html = f'<div class="meta">{items}</div>'

    thead = "".join(f"<th>{_e(h)}</th>" for h in cols)
    tbody = "\n".join(trs) if trs else '<tr><td class="small" colspan="99">No rows.</td></tr>'
    subtitle_html = f"<h2>{_e(subtitle)}</h2>" if subtitle else ""

    return f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<title>{_e(title)}</title>
<style>{_BASE_CSS}</style>
<body>
  <h1>{_e(title)}</h1>
  {subtitle_html}
  {meta_html}
  <div class="tablewrap">
    <table>
      <thead><tr>{thead}</tr></thead>
      <tbody>
{tbody}
      </tbody>
      <tfoot><tr><td class="small" colspan="{len(cols)}">Rows: {count}</td></tr></tfoot>
    </table>
  </div>
</body>
</html>"""

def _open_file(path: Path) -> None:
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(path))  # type: ignore[attr-defined]
            return
    except Exception:
        pass
    try:
        webbrowser.open_new_tab(path.as_uri())
    except Exception:
        # last resort: try open without as_uri
        webbrowser.open(str(path))

def export_table_html(
    path: str | os.PathLike | None,
    title: str,
    columns: Sequence[str],
    rows: Iterable[Any],
    *,
    subtitle: Optional[str] = None,
    meta: Optional[Mapping[str, Any]] = None,
    open_after: bool = True,
) -> Path:
    """
    Render a table to HTML, save it, and (optionally) auto-open it.
    If 'path' is None, writes to 'export/<slugified-title>-YYYYMMDD-HHMMSS.html'.
    """
    # choose path
    if path is None or str(path).strip() == "":
        safe = "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in (title or "export"))
        ts = _dt.now().strftime("%Y%m%d-%H%M%S")
        path = Path("export") / f"{safe}-{ts}.html"
    else:
        path = Path(path)

    path.parent.mkdir(parents=True, exist_ok=True)
    html = render_table_html(title, columns, rows, subtitle=subtitle, meta=meta)
    path.write_text(html, encoding="utf-8")
    if open_after:
        _open_file(path)
    return path
