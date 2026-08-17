#!/usr/bin/env python3
"""
Local dataset browser for the Tata Steel Round-2 flagship dataset.
File picker + full rows/columns view with search, sort, page-jump.
Server-side pagination => even 585k-row CSVs open instantly.

Run:  .venv/bin/python view_dataset.py
Then open the printed URL in a browser.
"""
import json
import math
import os
from functools import lru_cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, quote

import pandas as pd

ROOT = os.environ.get("DS_ROOT") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "datasets", "steel-maintenance-flagship")
TITLE = os.environ.get("DS_TITLE", "FLAGSHIP DATASET")
PAGE = 100  # rows per page

# NASA C-MAPSS column layout (26 cols): unit, cycle, 3 op-settings, 21 sensors
CMAPSS_COLS = (["unit", "cycle", "op_setting_1", "op_setting_2", "op_setting_3"]
               + [f"sensor_{i}" for i in range(1, 22)])


def list_files():
    out = []
    for dirpath, _, names in os.walk(ROOT):
        for n in sorted(names):
            if n.lower().endswith((".csv", ".jsonl", ".txt")):
                full = os.path.join(dirpath, n)
                rel = os.path.relpath(full, ROOT)
                out.append((rel, os.path.getsize(full)))
    return sorted(out)


@lru_cache(maxsize=32)
def load(rel):
    full = os.path.join(ROOT, rel)
    low = rel.lower()
    if low.endswith(".jsonl"):
        rows = [json.loads(l) for l in open(full, encoding="utf-8") if l.strip()]
        df = pd.json_normalize(rows)
    elif low.endswith(".txt"):
        # C-MAPSS = whitespace-delimited; readme is plain text
        df = pd.read_csv(full, sep=r"\s+", header=None, engine="python")
        base = os.path.basename(low)
        if df.shape[1] == 26:
            df.columns = CMAPSS_COLS
        elif df.shape[1] == 1 and base.startswith("rul"):
            df.columns = ["RUL"]
    else:
        df = pd.read_csv(full, low_memory=False)
    return df


def human(n):
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f}{u}"
        n /= 1024
    return f"{n:.1f}TB"


CSS = """
*{box-sizing:border-box}body{margin:0;font:13px/1.4 ui-monospace,Menlo,Consolas,monospace;background:#0d1117;color:#c9d1d9}
.wrap{display:flex;height:100vh}
.side{width:300px;min-width:300px;background:#161b22;border-right:1px solid #30363d;overflow:auto;padding:10px}
.side h1{font-size:13px;color:#58a6ff;margin:0 0 10px}
.f{display:block;padding:6px 8px;border-radius:6px;color:#c9d1d9;text-decoration:none;margin-bottom:2px;font-size:12px}
.f:hover{background:#21262d}.f.on{background:#1f6feb33;color:#58a6ff}
.f .sz{color:#8b949e;font-size:10px}
.main{flex:1;overflow:auto;padding:14px}
.bar{position:sticky;top:0;background:#0d1117;padding-bottom:10px;z-index:5}
.bar h2{margin:0 0 4px;font-size:15px;color:#e6edf3}
.meta{color:#8b949e;margin-bottom:8px}
input[type=text]{background:#0d1117;border:1px solid #30363d;color:#c9d1d9;padding:6px 10px;border-radius:6px;width:280px}
.pg a,.pg span{display:inline-block;padding:4px 9px;margin-right:4px;border:1px solid #30363d;border-radius:6px;color:#58a6ff;text-decoration:none}
.pg .cur{background:#1f6feb;color:#fff;border-color:#1f6feb}
table{border-collapse:collapse;width:100%;margin-top:10px}
th,td{border:1px solid #21262d;padding:4px 8px;text-align:left;white-space:nowrap;max-width:420px;overflow:hidden;text-overflow:ellipsis}
th{background:#161b22;position:sticky;top:0;color:#79c0ff;font-weight:600}
tr:nth-child(even) td{background:#0f141a}
td{vertical-align:top}
.idx{color:#8b949e;background:#161b22!important}
"""


def page_html(rel, page, q):
    files = list_files()
    side = f"<h1>{TITLE}</h1>"
    for f, sz in files:
        on = "on" if f == rel else ""
        side += (f'<a class="f {on}" href="/?f={quote(f)}">{f}'
                 f'<span class="sz"> · {human(sz)}</span></a>')

    if not rel:
        body = "<div class='main'><div class='bar'><h2>← koi file chuno</h2>" \
               "<div class='meta'>Left panel se koi bhi CSV / JSONL kholo. " \
               "Saari rows + columns yahin scroll honge.</div></div></div>"
        return f"<!doctype html><html><head><meta charset=utf-8><title>Dataset</title>" \
               f"<style>{CSS}</style></head><body><div class=wrap>" \
               f"<div class=side>{side}</div>{body}</div></body></html>"

    df = load(rel)
    total_cols = df.shape[1]
    view = df
    if q:
        mask = df.apply(lambda c: c.astype(str).str.contains(q, case=False, na=False))
        view = df[mask.any(axis=1)]
    n = len(view)
    pages = max(1, math.ceil(n / PAGE))
    page = max(1, min(page, pages))
    chunk = view.iloc[(page - 1) * PAGE: page * PAGE]

    # table
    th = "<th class=idx>#</th>" + "".join(f"<th>{c}</th>" for c in df.columns)
    rows = ""
    for ridx, (_, r) in enumerate(chunk.iterrows(), start=(page - 1) * PAGE + 1):
        cells = "".join(f"<td title=\"{str(v)}\">{'' if pd.isna(v) else str(v)}</td>"
                        for v in r.values)
        rows += f"<tr><td class=idx>{ridx}</td>{cells}</tr>"
    table = f"<table><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table>"

    # pager
    def lnk(p, label=None, cur=False):
        if cur:
            return f"<span class=cur>{label or p}</span>"
        qp = f"&q={quote(q)}" if q else ""
        return f"<a href='/?f={quote(rel)}&p={p}{qp}'>{label or p}</a>"
    pg = ""
    if pages > 1:
        if page > 1:
            pg += lnk(1, "« first") + lnk(page - 1, "‹ prev")
        lo, hi = max(1, page - 3), min(pages, page + 3)
        for p in range(lo, hi + 1):
            pg += lnk(p, cur=(p == page))
        if page < pages:
            pg += lnk(page + 1, "next ›") + lnk(pages, "last »")

    qval = q.replace('"', "&quot;")
    bar = (f"<div class=bar><h2>{rel}</h2>"
           f"<div class=meta>{n:,} rows" + (f" (filtered from {len(df):,})" if q else "")
           + f" · {total_cols} columns · page {page}/{pages} · {PAGE}/page</div>"
           f"<form method=get><input type=hidden name=f value=\"{rel}\">"
           f"<input type=text name=q placeholder='search all columns…' value=\"{qval}\" autofocus>"
           f" <span style='color:#8b949e'>Enter to search</span></form>"
           f"<div class=pg style='margin-top:8px'>{pg}</div></div>")
    main = f"<div class=main>{bar}{table}<div class=pg style='margin-top:10px'>{pg}</div></div>"
    return f"<!doctype html><html><head><meta charset=utf-8><title>{rel}</title>" \
           f"<style>{CSS}</style></head><body><div class=wrap>" \
           f"<div class=side>{side}</div>{main}</div></body></html>"


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        u = urlparse(self.path)
        qs = parse_qs(u.query)
        rel = qs.get("f", [""])[0]
        page = int(qs.get("p", ["1"])[0] or 1)
        q = qs.get("q", [""])[0]
        try:
            html = page_html(rel, page, q)
        except Exception as e:
            html = f"<pre style='color:#f85149'>Error: {e}</pre>"
        b = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)


if __name__ == "__main__":
    port = int(os.environ.get("DS_PORT", "8799"))
    print(f"\n  Dataset browser:  http://127.0.0.1:{port}/\n")
    print(f"  Files: {len(list_files())}  ·  Root: {ROOT}\n")
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
