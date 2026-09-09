#!/usr/bin/env python3
"""E05 — BAK omits only MKBRECORDABLE; VTKF numbers vs VPLST.

Claim (AACS HD DVD Pre-recorded Book Final 0.953 §3.11 + corpus): backup tree
usually mirrors the primary AACS dir except MKBRECORDABLE.AACS.
Five discs (12,628-byte MKBROM titles) copy MKBRECORDABLE into BAK anyway.

Claim: VTKF### tracks VPLST### on most discs; extras exist (listed in 09_AACS.md).

ISO URLs from listing line 1.
"""
from lib import discs, parse_listing

bak_omit_only_rec = 0
bak_pairs = 0
bak_copies_recordable = 0
vtkf_eq = 0
vtkf_extra = []
no_aacs = 0

for disc, listing in discs():
    _, rows = parse_listing(listing)
    files = {p: s for k, s, p in rows if k == "FILE"}
    primary = None
    for cand in ("/ANY!", "/AAC!"):
        if any(p.startswith(cand + "/") for p in files):
            primary = cand
            break
    if not primary:
        no_aacs += 1
        continue
    bak = primary + "_BAK"
    pset = {p[len(primary) + 1 :] for p in files if p.startswith(primary + "/")}
    bset = {p[len(bak) + 1 :] for p in files if p.startswith(bak + "/")}
    if not bset:
        continue
    bak_pairs += 1
    extra_p = pset - bset
    extra_b = bset - pset
    if extra_p == {"MKBRECORDABLE.AACS"} and not extra_b:
        bak_omit_only_rec += 1
    elif not extra_p and not extra_b and "MKBRECORDABLE.AACS" in pset:
        bak_copies_recordable += 1
        print("BAK_COPIES_MKBRECORDABLE", disc.name)
    else:
        print("BAK_UNEXPECTED", disc.name, "primary_only", sorted(extra_p), "bak_only", sorted(extra_b))

    def nums(prefix, suffix):
        out = set()
        for p in files:
            base = p.rsplit("/", 1)[-1]
            if base.startswith(prefix) and base.endswith(suffix):
                mid = base[len(prefix) : -len(suffix)]
                if mid.isdigit():
                    out.add(int(mid))
        return out

    vk, vp = nums("VTKF", ".AACS"), nums("VPLST", ".XPL")
    # VTKF also appears under BAK — use primary tree only
    vk = set()
    for p in files:
        if p.startswith(primary + "/") and "/VTKF" in p:
            mid = p.rsplit("VTKF", 1)[-1].split(".", 1)[0]
            if mid.isdigit():
                vk.add(int(mid))
    if vk == vp:
        vtkf_eq += 1
    elif vk:
        vtkf_extra.append((disc.name, sorted(vk), sorted(vp)))

print(f"bak_pairs={bak_pairs} omit_only_MKBRECORDABLE={bak_omit_only_rec} copies_recordable={bak_copies_recordable}")
print(f"no_aacs={no_aacs} vtkf_eq_vplst={vtkf_eq} mismatches={len(vtkf_extra)}")
for row in vtkf_extra:
    print(" ", row)
assert bak_pairs == 104
assert bak_omit_only_rec == 99
assert bak_copies_recordable == 5
print("E05 PASS")
