#!/usr/bin/env python3
"""mmdc-compatible Mermaid renderer using mermaid.ink (no Node or Chromium).

sphinxcontrib.mermaid invokes this like `mmdc -i in.mmd -o out.<ext>`. The output
extension selects the format:

  .png  -> raster PNG embedded by Sphinx as <img src>. This is the portable path:
           EPUB readers and print-to-PDF engines all render <img>, whereas the SVG
           path is embedded as <object> and collapses to zero height in paginated
           output. PNG is requested at scale 2 for a crisp result.
  .svg  -> vector SVG (kept for completeness; used only if output format is svg).

The diagram code is base64url-encoded into the mermaid.ink path.
"""

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

    if args.o.lower().endswith(".svg"):
        url = "https://mermaid.ink/svg/" + token
    else:
        # Raster PNG on white, upscaled for print and high-DPI screens.
        url = "https://mermaid.ink/img/" + token + "?type=png&scale=2&width=1400&bgColor=FFFFFF"

    req = urllib.request.Request(url, headers={"User-Agent": "hddvd-spec-sphinx"})

    # mermaid.ink can throttle or time out on rapid sequential requests during a
    # build; retry with backoff so every flowchart renders.
    import time

    last = ""
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
            if data:
                open(args.o, "wb").write(data)
                return 0
            last = "empty image"
        except urllib.error.URLError as exc:
            last = str(exc)
        time.sleep(3 * (attempt + 1))

    print(f"mermaid.ink failed after retries: {last}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
