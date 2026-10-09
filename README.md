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
fixtures/        test discs for libhddvd (gitignored, built by the tools below)
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

## Test fixtures

Disc trees and images for libhddvd's disc access tests. Built locally into
`fixtures/` (gitignored); nothing from a disc is committed.

```
tools/corpustree.py corpus fixtures/tree           every corpus disc as a folder tree
tools/sparseiso.py <iso-url> fixtures/iso/X.iso    real UDF 2.50 image, sparse
tools/isotree.py fixtures/iso/X.iso fixtures/isotree/X   same disc as a folder tree
cc -O2 -o udfcheck tools/udfcheck.c $(pkg-config --cflags --libs libudfread)
./udfcheck fixtures/iso/X.iso | tools/checkiso.py corpus X
```

`fixtures/tree/<DISC>/` has every directory and file of the disc with its real
name and size. Files the corpus saved are hard links; the rest (EVOs, most
ACAs, AACS files) are zero-filled sparse placeholders, listed in
`<DISC>.placeholders`. Apparent size is terabytes, real size ~100 MB: copy
with `cp --sparse=always` or `rsync -S`.

`fixtures/iso/X.iso` has the full logical size of the disc. Real bytes: the
first and last MiB, every UDF structure, every file except EVOs, and the
first `--evo-bytes` (default 32 MiB) of each EVO; the rest are holes.
`X.iso.ranges` lists the real byte ranges. `--resume` fetches only what an
existing image lacks. `udfcheck` opens the image with libudfread, reports any
read that hits a hole, and `checkiso.py` compares paths, sizes and bytes with
the corpus.
