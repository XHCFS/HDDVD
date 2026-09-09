# HD DVD Advanced Content spec

Implementable spec: **`spec/advanced/`**. HTML uses the **Read the Docs** theme:

```
cd docs
../.venv/bin/sphinx-build -b html . _build/html
```

Open `docs/_build/html/index.html`. GitHub Pages serves `docs/` (`index.html` plus `_static/`). After a push, in the GitHub repo: **Settings → Pages → Deploy from a branch → `main` / `/docs`**. Site: https://xhcfs.github.io/HDDVD/

Category 2 (Advanced Content) only. 119/120 discs in `corpus/`. No PGC, no DVD VM.

Research log (not the spec): `spec/clean/`. Run `python3 experiments/run.py`.

## Layout

```
spec/advanced/   spec sheet (markdown)
docs/            Sphinx + sphinx_rtd_theme (conf.py copies the 10 sheets from spec/advanced on build)
spec/clean/      evidence / adversarial notes
spec/raw/        Playlist.xsd, Manifest.xsd, iHD.xsd, patent extracts
corpus/          120 discs: listings + saved MAP/VTI/XPL/DISCID
experiments/     verification
tools/udfgrab.py UDF 2.50 HTTP-range reader
```

Patents: https://patents.google.com/patent/US20080298219A1
https://patents.google.com/patent/US20070091495A1
AACS: https://aacsla.com/aacs-specifications/
HD DVD Pre-recorded Final 0.953 (Wayback).
Firmware catalog: http://hd-dvd.org/firmware.html
(intermittent; Wayback: https://web.archive.org/web/20231210144123/http://hd-dvd.org/firmware.html).
Player binaries are not in this repo and are not reverse-engineered.

## Corpus

120 ISOs. Line 1 of `corpus/<DISC>/_listing.txt` is the Archive.org URL.
119 Advanced, 1 Standard (`RESERVOIR_DOGS`, out of scope for `spec/advanced/`).
AACS dir is `ANY!/` (96) or `AAC!/` (8).
