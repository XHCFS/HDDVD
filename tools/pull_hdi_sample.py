#!/usr/bin/env python3
"""Pull small ADV_OBJ ACA archives for the HDi menu census (e15).

Fetches every listed .ACA whose size is <= MAX_BYTES (default 320 KiB) plus
any already-partial disc walks. One UDF walk per disc.

Does not decrypt. Does not pull EVOs.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
from lib import discs, listing_url, parse_listing, saved  # noqa: E402

MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 320 * 1024
py = sys.executable
udf = ROOT / "tools" / "udfgrab.py"

todo = []
for disc, listing in discs():
    url = listing_url(listing)
    if not url:
        continue
    _, rows = parse_listing(listing)
    need = []
    for k, sz, p in rows:
        if k != "FILE" or not p.upper().endswith(".ACA") or sz > MAX:
            continue
        loc = saved(disc, p)
        if loc.is_file() and loc.stat().st_size == sz:
            continue
        need.append((sz, p))
    if need:
        todo.append((disc, url, need))

print(f"# discs to walk={len(todo)} files={sum(len(n) for _,_,n in todo)} max_bytes={MAX}")
fail = 0
for disc, url, need in todo:
    print(f"# {disc.name} pull {len(need)} ACA")
    r = subprocess.run(
        [py, str(udf), url, str(disc), "--max-bytes", str(MAX), "--ext", ".ACA"],
        cwd=ROOT,
    )
    if r.returncode != 0:
        print(f"# FAIL {disc.name} rc={r.returncode}")
        fail += 1
print(f"# done fail={fail}")
sys.exit(1 if fail else 0)
