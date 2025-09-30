# path: utils/export.py
from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime as _dt
from html import escape as _e
import os
from pathlib import Path
import sys
from typing import Any
import webbrowser

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


def _coerce_row(row: Any, columns: Sequence[str]) -> list[str]:
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
    subtitle: str | None = None,
    meta: Mapping[str, Any] | None = None,
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
        items = "".join(
            f'<div class="kv"><b>{_e(str(k))}:</b> {_e(str(v))}</div>'
            for k, v in meta_items.items()
        )
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
    subtitle: str | None = None,
    meta: Mapping[str, Any] | None = None,
    open_after: bool = True,
) -> Path:
    """
    Render a table to HTML, save it, and (optionally) auto-open it.
    If 'path' is None, writes to 'export/<slugified-title>-YYYYMMDD-HHMMSS.html'.
    """
    # choose path
    if path is None or str(path).strip() == "":
        safe = "".join(
            ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in (title or "export")
        )
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


# ---------- Printable Recipe Export ----------

_RECIPE_CSS = (
    _BASE_CSS
    + """
.recipe{border:1px solid var(--border); border-radius:10px; padding:16px; margin:16px 0; background:#fff}
.recipe h3{font-size:18px; margin:0 0 8px 0}
.recipe .meta{margin:6px 0 12px 0}
.recipe .section{margin-top:10px}
.recipe .section h4{font-size:14px; margin:0 0 6px 0; color:var(--muted)}
.recipe .grid{display:grid; grid-template-columns: 1fr 1fr; gap:14px}
.recipe ul{margin:6px 0 0 18px}
.recipe pre{background:var(--surface); border:1px solid var(--border); padding:10px; border-radius:8px; white-space:pre-wrap}
@media print{
  .meta .kv{display:none}
  .recipe{page-break-inside: avoid}
}
"""
)


def _fmt_if(v: Any, label: str) -> str:
    v = (v or "").strip()
    return f"<div class='kv'><strong>{_e(label)}:</strong> {_e(v)}</div>" if v else ""


def render_recipes_html(
    title: str,
    recipes: Sequence[Mapping[str, Any]],
    *,
    subtitle: str | None = None,
    meta: Mapping[str, Any] | None = None,
) -> str:
    head = f"""<!doctype html>
<html><head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>{_e(title or 'Recipes')}</title>
<style>{_RECIPE_CSS}</style>
</head>
<body>
  <h1>{_e(title or 'Recipes')}</h1>
  {f"<h2>{_e(subtitle)}</h2>" if subtitle else ""}
  <div class='meta'>
    <div class='kv'>Generated: {_e(_now_iso())}</div>
    {''.join(f"<div class='kv'><strong>{_e(str(k))}:</strong> {_e(str(v))}</div>" for k,v in (meta or {}).items())}
  </div>
"""

    blocks: list[str] = []
    for r in recipes:
        title = str(r.get("title", "") or "Untitled")
        source = r.get("source", "") or ""
        url = (r.get("url", "") or "").strip()
        tags = r.get("tags", "") or ""
        rating = r.get("rating", "") or ""
        prep = r.get("prep_time", "") or ""
        cook = r.get("cook_time", "") or ""
        servings = r.get("servings", "") or ""
        ingredients = r.get("ingredients", "") or ""
        instructions = r.get("instructions", "") or ""

        # prefer bullet list when ingredients look like lines
        ing_block = ""
        if ingredients.strip():
            # split lines, keep non-empty
            lines = [ln.strip() for ln in ingredients.replace("\r", "").split("\n") if ln.strip()]
            if lines and len(lines) <= 1:
                ing_block = f"<pre>{_e(ingredients)}</pre>"
            else:
                items = "".join(f"<li>{_e(ln)}</li>" for ln in lines)
                ing_block = f"<ul>{items}</ul>"

        inst_block = f"<pre>{_e(instructions)}</pre>" if instructions.strip() else ""
        url_block = (
            f"<a href='{_e(url)}' target='_blank' rel='noopener'>{_e(url)}</a>" if url else ""
        )

        block = f"""<article class='recipe'>
  <h3>{_e(title)}</h3>
  <div class='meta'>
    {_fmt_if(source, 'Source')}
    {f"<div class='kv'><strong>URL:</strong> {url_block}</div>" if url else ''}
    {_fmt_if(tags, 'Tags')}
    {_fmt_if(str(rating), 'Rating')}
    {_fmt_if(prep, 'Prep')}{_fmt_if(cook, 'Cook')}{_fmt_if(str(servings), 'Servings')}
  </div>
  <div class='grid'>
    <div class='section'>
      <h4>Ingredients</h4>
      {ing_block or '<div class="small">No ingredients entered.</div>'}
    </div>
    <div class='section'>
      <h4>Instructions</h4>
      {inst_block or '<div class="small">No instructions entered.</div>'}
    </div>
  </div>
</article>"""
        blocks.append(block)

    body = "\n\n".join(blocks)
    return head + body + "\n</body></html>"


def export_recipes_html(
    recipes: Sequence[Mapping[str, Any]],
    *,
    path: Path | str | None = None,
    title: str = "Recipes",
    subtitle: str | None = None,
    meta: Mapping[str, Any] | None = None,
    open_after: bool = True,
) -> Path:
    if path is None or str(path).strip() == "":
        safe = "".join(
            ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in (title or "recipes")
        )
        ts = _dt.now().strftime("%Y%m%d-%H%M%S")
        path = Path("export") / f"{safe}-{ts}.html"
    else:
        path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    html = render_recipes_html(title, recipes, subtitle=subtitle, meta=meta)
    path.write_text(html, encoding="utf-8")
    if open_after:
        _open_file(path)
    return path
