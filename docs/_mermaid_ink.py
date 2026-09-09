#!/usr/bin/env python3
"""mmdc-compatible renderer using mermaid.ink (no Node/Chromium)."""

from __future__ import annotations

import argparse
import base64
import sys
import urllib.error
import urllib.request


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    parser.add_argument("-o", required=True)
    args, _unknown = parser.parse_known_args()
    code = open(args.i, encoding="utf-8").read().strip()
    token = base64.urlsafe_b64encode(code.encode("utf-8")).decode("ascii").rstrip("=")
    url = "https://mermaid.ink/svg/" + token
    req = urllib.request.Request(url, headers={"User-Agent": "hddvd-spec-sphinx"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
    except urllib.error.URLError as exc:
        print(f"mermaid.ink failed: {exc}", file=sys.stderr)
        return 1
    if not data:
        print("mermaid.ink returned an empty image", file=sys.stderr)
        return 1
    open(args.o, "wb").write(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
