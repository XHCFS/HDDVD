#!/usr/bin/env python3
"""E21 — every field of DKF / VTKF / VTUF / CONTENT_CERT against the AACS book.

Source: AACS HD DVD and DVD Pre-recorded Book, Final 0.953 [4]:
  Table 3-8 (TKF), 3-9 (BIFO), 3-10 (TUF), 3-17 (Content Certificate),
  Table 6-2 (DKF), p.21 (residue allowed only after MKB/SKBF/CRL).

Input: every *.AACS under corpus/ whose name is DKF, VTKF###, VTUF### or
CONTENT_CERT (primary and _BAK trees). Fetch with
  tools/udfgrab.py <iso-url> corpus/<DISC> --ext .AACS --max-bytes 3000
(ISO URL = line 1 of corpus/<DISC>/_listing.txt).

Claims (falsifier in brackets):
  DKF: 64 bytes, DKF_ID, HD_VDKF_SIZE=64, reserved 16-31 and 34-47 zero,
       VERN@32-33 = 0, KDIRe is real data, one KDIRe per disc.
       [any field differs]
  VTKF: TKF_ID; HD_VTKF_SIZE = 2480 on every file (book: fixed);
       64 entries; BIFO = AV_FLG(b7) | BIND_TYPE(b6-4) | 0000; every used
       slot BIND_TYPE=000 with Binding MAC = FF*16; reserved 2432-2463 zero;
       PLAYLIST_NAME = VPLSTnnn.XPL with nnn = file number.
       Exception expected: PANS_LABYRINTH VTKF001/003 are 2516 bytes =
       2480-byte TKF + 36 zero bytes after the TKF MAC (book p.21 forbids it).
       [HD_VTKF_SIZE != 2480; trailing bytes non-zero; BIND_TYPE != 000]
  VTUF: URF_ID; HD_VURF_SIZE = length = 144; URS_NUM = 0; VERN@21-22 = 0;
       PLAYLIST_NAME@23; HASH_SIZE = 128 except KING_OF_CALIFORNIA and
       RESIDENT_EVIL3_GER (= 8).  [any other value]
  CONTENT_CERT: 120 bytes; type 0; BEE = 0; layers 1; layer 0;
       Number_of_Digests 2; Length_Format_Specific_Section 0x000E;
       reserved zero.  [any field differs]
  primary tree == _BAK tree byte for byte.  [a mismatch]
"""
import re
from collections import Counter

from lib import CORPUS

be = lambda b: int.from_bytes(b, "big")
zero = lambda b: not any(b)
FILL = (bytes(16), b"\xff" * 16)
HASH8 = {"KING_OF_CALIFORNIA", "RESIDENT_EVIL3_GER"}
PADDED = {("PANS_LABYRINTH", "VTKF001"), ("PANS_LABYRINTH", "VTKF003")}

n = Counter()
kdire = Counter()
applicant = Counter()
used_slots = 0
unused_slots = 0

for p in sorted(CORPUS.glob("*/*.AACS")):
    disc = p.parent.name
    name = p.name.split("__")[-1][:-5]
    b = p.read_bytes()

    if name == "DKF":
        assert len(b) == 64, p
        assert b[:12] == b"DVD_HD_V_DKF", p
        assert be(b[12:16]) == 64, p
        assert zero(b[16:32]) and zero(b[34:48]), p
        assert be(b[32:34]) == 0, p
        assert b[48:64] not in FILL, p
        kdire[(disc, b[48:64])] += 1
        n["DKF"] += 1

    elif re.fullmatch(r"VTKF\d{3}", name):
        assert b[:12] == b"DVD_HD_V_TKF", p
        size = be(b[12:16])
        assert size == 2480, (p, size)
        if (disc, name) in PADDED:
            assert len(b) == 2516 and zero(b[2480:]), p
            n["VTKF padded"] += 1
        else:
            assert len(b) == 2480, (p, len(b))
        pl = b[16:28]
        assert re.fullmatch(rb"VPLST\d{3}\.XPL", pl) and pl[5:8].decode() == name[4:], p
        assert zero(b[28:32]) and zero(b[32:36]) and zero(b[36:128]), p
        for i in range(64):
            e = b[128 + 36 * i:164 + 36 * i]
            assert e[0] & 0x0F == 0 and zero(e[1:4]), (p, i)
            if e[0] >> 7:
                assert (e[0] >> 4) & 7 == 0, (p, i)          # BIND_TYPE 000
                assert e[20:36] == b"\xff" * 16, (p, i)       # Binding MAC fill
                assert e[4:20] not in FILL, (p, i)
                used_slots += 1
            else:
                unused_slots += 1
        assert zero(b[2432:2464]) and b[2464:2480] not in FILL, p
        n["VTKF"] += 1

    elif re.fullmatch(r"VTUF\d{3}", name):
        assert b[:12] == b"DVD_HD_V_TUF", p
        assert be(b[12:16]) == len(b) == 144, p
        assert b[16] == 0, p                                   # URS_NUM
        hs = be(b[17:21])
        assert hs == (8 if disc in HASH8 else 128), (p, hs)
        assert zero(b[21:23]), p
        pl = b[23:35]
        assert re.fullmatch(rb"VPLST\d{3}\.XPL", pl) and pl[5:8].decode() == name[4:], p
        assert zero(b[35:128]) and b[128:144] not in FILL, p
        n["VTUF"] += 1

    elif name == "CONTENT_CERT":
        assert len(b) == 120 and b[0] == 0, p
        assert b[1] == 0, p                                    # BEE 0, reserved 0
        assert b[6] == 1 and b[7] == 0, p
        assert zero(b[8:12]) and be(b[12:14]) == 2, p
        assert zero(b[22:24]) and be(b[24:26]) == 0x000E and zero(b[26:40]), p
        assert not zero(b[40:120]), p
        applicant[be(b[14:16])] += 1
        n["CONTENT_CERT"] += 1

# primary == backup
pairs = 0
for p in CORPUS.glob("*/*.AACS"):
    for a, bk in (("ANY!__", "ANY!_BAK__"), ("AAC!__", "AAC!_BAK__")):
        if p.name.startswith(a):
            q = p.with_name(p.name.replace(a, bk, 1))
            if q.exists():
                assert p.read_bytes() == q.read_bytes(), p
                pairs += 1

discs_with_dkf = {d for d, _ in kdire}
assert len({k for _, k in kdire}) == len(discs_with_dkf), "KDIRe shared across discs"

print(dict(n))
print(f"title key slots used={used_slots} unused={unused_slots}")
print(f"KDIRe distinct={len(discs_with_dkf)} (one per disc)")
print(f"CONTENT_CERT Applicant ID: {dict(applicant.most_common())}")
print(f"primary==BAK pairs={pairs}")
assert n["DKF"] >= 1 and n["VTKF"] >= 1 and n["VTUF"] >= 1 and n["CONTENT_CERT"] >= 1
print("E21 PASS")
