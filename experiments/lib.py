"""Shared corpus helpers. Disc ISO URLs come from the first line of each listing."""
from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"


def discs():
    for d in sorted(CORPUS.iterdir()):
        listing = d / "_listing.txt"
        if listing.is_file():
            yield d, listing


def listing_url(listing: Path) -> str | None:
    first = listing.read_text(errors="replace").splitlines()[0]
    m = re.match(r"#\s+(https?://\S+)", first)
    return m.group(1) if m else None


def parse_listing(listing: Path):
    """Yield (kind, size_or_none, path) for FILE/DIR lines."""
    rows = []
    meta = {}
    for line in listing.read_text(errors="replace").splitlines():
        if line.startswith("# https"):
            meta["url"] = line[2:].strip()
        elif line.startswith("# partition_start="):
            for part in line[2:].split():
                if "=" in part:
                    k, v = part.split("=", 1)
                    meta[k] = v
        elif line.startswith("DIR"):
            rows.append(("DIR", None, line.split(maxsplit=1)[1].strip()))
        elif line.startswith("FILE"):
            _, size, path = line.split(maxsplit=2)
            rows.append(("FILE", int(size), path.strip()))
    return meta, rows


def saved(disc: Path, udf_path: str) -> Path:
    return disc / udf_path.lstrip("/").replace("/", "__")
