# utils/importers.py

from __future__ import annotations
import csv, json, re
from typing import List, Dict, Any, Tuple

def parse_recipe_text_to_rows(text: str) -> List[Dict[str, Any]]:
    """
    Minimal text importer.
    Format:
      Title: ...
      Tags: tag1, tag2
      Ingredients:
        - 1 cup rice
        - 2 tbsp oil
      Instructions:
        1. step
        2. step
    Separate recipes with a line of ----
    """
    chunks = re.split(r"\n----+\n", text.strip(), flags=re.MULTILINE)
    out: List[Dict[str, Any]] = []
    for ch in chunks:
        title = _extract_after(ch, r"^Title:\s*(.+)$")
        tags = _extract_after(ch, r"^Tags:\s*(.+)$")
        ings = _collect_block(ch, r"^Ingredients:\s*$")
        instr = _collect_block(ch, r"^Instructions:\s*$")
        ing_items = []
        for line in ings:
            line = line.strip(" -\t")
            if not line: continue
            ing_items.append({"original": line, "name":"", "quantity": None, "unit": ""})
        out.append({
            "title": title or "Untitled",
            "ingredients": ing_items,
            "instructions": "\n".join(instr).strip(),
            "url": "",
            "tags": tags or "",
            "json": json.dumps({"source": "text"})
        })
    return out

def _extract_after(text: str, rx: str) -> str:
    m = re.search(rx, text, flags=re.MULTILINE)
    return (m.group(1).strip() if m else "")

def _collect_block(text: str, header_rx: str) -> List[str]:
    lines = text.splitlines()
    out: List[str] = []
    active = False
    for ln in lines:
        if re.match(header_rx, ln.strip()):
            active = True
            continue
        if active:
            if re.match(r"^[A-Z][A-Za-z ]+:$", ln.strip()):
                break
            out.append(ln)
    return out

def read_csv_preview(path: str, limit: int = 30) -> Tuple[List[str], List[List[str]]]:
    rows: List[List[str]] = []
    headers: List[str] = []
    with open(path, newline="", encoding="utf-8") as f:
        sniffer = csv.Sniffer()
        sample = f.read(2048)
        f.seek(0)
        dialect = sniffer.sniff(sample) if sample else csv.excel
        reader = csv.reader(f, dialect)
        for i, r in enumerate(reader):
            if i == 0:
                headers = r
            else:
                rows.append(r)
            if len(rows) >= limit:
                break
    return headers, rows
