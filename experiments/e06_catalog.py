#!/usr/bin/env python3
"""E06 — on-disc catalog: root dirs, extensions, filename patterns.

Claim: retail HD DVD uses a small closed set of root directories and
filename grammars. This prints the census used by spec/clean/12_DISC_STRUCTURE.md.

ISO URLs: listing line 1.
"""
from collections import Counter, defaultdict
from lib import discs, parse_listing

root_dirs = Counter()
ext = Counter()
adv_ext = Counter()
hvdvd_pat = Counter()
aacs_names = Counter()
other_roots = Counter()
adv_names = Counter()
n_files = 0

for disc, listing in discs():
    _, rows = parse_listing(listing)
    files = [p for k, _, p in rows if k == "FILE"]
    dirs = [p for k, _, p in rows if k == "DIR"]
    n_files += len(files)
    for p in dirs:
        parts = p.strip("/").split("/")
        if len(parts) == 1:
            root_dirs[parts[0]] += 1
    for p in files:
        n_files += 0
        parts = p.strip("/").split("/")
        root = parts[0] if parts else ""
        if root not in ("HVDVD_TS", "ADV_OBJ", "ANY!", "AAC!", "ANY!_BAK", "AAC!_BAK"):
            other_roots[root] += 1
        base = parts[-1]
        e = base.rsplit(".", 1)[-1].upper() if "." in base else ""
        ext[e] += 1
        if p.startswith("/ADV_OBJ/"):
            adv_ext[e] += 1
            if e in ("XPL", "DAT", "ACA", "XMF", "JS", "PNG", "TTF", "CER", "XML", "HTM", "HTML", "JPG", "JPEG", "WAV", "MP3"):
                adv_names[base] += 1
            else:
                adv_names[f"*.{e}"] += 1
        if p.startswith("/HVDVD_TS/"):
            if base.endswith(".VTI"):
                hvdvd_pat["HVA*.VTI"] += 1
            elif base.endswith(".IFO"):
                hvdvd_pat["HV*I01.IFO"] += 1
            elif base.endswith(".BUP"):
                hvdvd_pat["HV*.BUP"] += 1
            elif base.endswith(".MAP"):
                hvdvd_pat["*.MAP"] += 1
            elif base.endswith(".EVO"):
                if "M" in base[2:6] or "M0" in base:
                    hvdvd_pat["HV*M*.EVO"] += 1
                else:
                    hvdvd_pat["*.EVO"] += 1
            else:
                hvdvd_pat[base] += 1
        if "/ANY!" in p or "/AAC!" in p:
            aacs_names[base] += 1

print("root dirs (DIR lines, one per disc that has it)", dict(root_dirs))
print("other file roots", dict(other_roots) or "none")
print("all ext", dict(ext.most_common()))
print("ADV_OBJ ext", dict(adv_ext.most_common()))
print("HVDVD_TS patterns", dict(hvdvd_pat.most_common()))
print("AACS basenames", dict(aacs_names.most_common(20)))
print("ADV_OBJ basename sample", dict(sorted(adv_names.items(), key=lambda x: -x[1])[:30]))
assert root_dirs["HVDVD_TS"] == 120
assert root_dirs["ADV_OBJ"] == 119
assert "VIDEO_TS" not in root_dirs
assert "AACS" not in root_dirs
assert not other_roots
print("E06 PASS")
