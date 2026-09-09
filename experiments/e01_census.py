#!/usr/bin/env python3
"""E01 — corpus census from UDF listings.

Claim: 120 discs; 119 Advanced; 1 Standard; AACS in ANY! (96) or AAC! (8);
partition_start=288 always; VTKF size 2480 except PANS_LABYRINTH 2516;
MKBROM usually 1e6, not always.

Sources: corpus/<DISC>/_listing.txt line 1 is the Internet Archive ISO URL.
"""
from collections import Counter
from lib import discs, parse_listing

n = 0
adv = std = 0
aacs_any = aacs_aac = aacs_none = 0
part288 = 0
vtkf_sizes = Counter()
mkbrom_sizes = Counter()
ext = Counter()
urls_ok = 0

for disc, listing in discs():
    n += 1
    meta, rows = parse_listing(listing)
    if meta.get("url", "").startswith("http"):
        urls_ok += 1
    if meta.get("partition_start") == "288":
        part288 += 1
    paths = {p for k, _, p in rows}
    files = [(s, p) for k, s, p in rows if k == "FILE"]
    has_vti = any(p.endswith(".VTI") for _, p in files)
    has_ifo = any("/HV" in p and p.endswith(".IFO") for _, p in files)
    has_adv = any(p.startswith("/ADV_OBJ/") for _, p in files)
    if has_vti or has_adv:
        adv += 1
    elif has_ifo and not has_vti:
        std += 1
    if any(p.startswith("/ANY!/") for _, p in files):
        aacs_any += 1
    elif any(p.startswith("/AAC!/") for _, p in files):
        aacs_aac += 1
    else:
        aacs_none += 1
    for s, p in files:
        ext[p.rsplit(".", 1)[-1].upper() if "." in p else ""] += 1
        if "VTKF" in p and p.endswith(".AACS") and "_BAK" not in p:
            vtkf_sizes[s] += 1
        if p.endswith("/MKBROM.AACS") and "_BAK" not in p:
            mkbrom_sizes[s] += 1

print(f"discs={n} urls={urls_ok} partition_start=288:{part288}/{n}")
print(f"advanced={adv} standard={std}")
print(f"AACS ANY!={aacs_any} AAC!={aacs_aac} none={aacs_none}")
print("listed ext", dict(ext.most_common(12)))
print("primary VTKF sizes", dict(vtkf_sizes))
print("primary MKBROM sizes", dict(mkbrom_sizes))
assert n == 120 and urls_ok == 120
assert part288 == 120
assert adv == 119 and std == 1
assert aacs_any == 96 and aacs_aac == 8 and aacs_none == 16
# Spec Table 3-8 says 2480. PANS_LABYRINTH VTKF001/003 are 2516
# (= 128 + 65*36 + 32 + 16): one extra title-key slot vs the book's 64.
assert vtkf_sizes[2480] >= 200
assert set(vtkf_sizes) <= {2480, 2516}
assert 2516 in vtkf_sizes
assert mkbrom_sizes[1000000] >= 80
assert set(mkbrom_sizes) <= {1000000, 1048576, 12628, 20480}
assert 20480 in mkbrom_sizes
assert 1048576 in mkbrom_sizes
assert 12628 in mkbrom_sizes
print("E01 PASS")
