#!/usr/bin/env python3
"""E22 — Content Hash Tables and Content Certificate digests, keyless.

Source: AACS HD DVD and DVD Pre-recorded Book, Final 0.953 [4]
  Table 3-17 (Content Certificate), 3-18 (CHT #1), 3-19 (CHT #2), §3.8.

No key is needed: every value below is a plain SHA-1 over files already on the
disc. Input under corpus/<DISC>/ (primary AACS tree): CONTENT_CERT.AACS,
CONTENT_HASH_TABLE1.AACS, CONTENT_HASH_TABLE2.AACS, MNGCPY_MANIFEST.XML, DKF.AACS,
VTUF###.AACS, and ADV_OBJ__DISCID.DAT. Fetch the hash tables and manifest with
  tools/udfgrab.py <iso-url> corpus/<DISC> \\
      --ext CONTENT_HASH_TABLE1.AACS,CONTENT_HASH_TABLE2.AACS,MNGCPY_MANIFEST.XML \\
      --max-bytes 6000000

Claims (falsifier in brackets):
  CHT #1: size = 8 + 8*NHV, NHV <= 500000, bytes 4-7 zero.      [size mismatch]
  CHT #2: size = 40060 + 8*NHA.                                   [size mismatch]
  Certificate digest #1 = SHA-1(CHT #1), digest #2 = SHA-1(CHT #2). [mismatch]
  CHT #2 bytes 0-7   = low 64 bits of SHA-1(DISCID.DAT), EXCEPT on discs whose
         PROVIDER_ID ends in ASCII "SLY": there it matches the DISCID with the
         original tail restored ("-DVD" for ASCII tags; brute-forced 3 bytes for
         HOT_FUZZ / PREMONITION_GER). Every "SLY" disc mismatches; no other disc
         does. BROTHERS_GRIMM / PHANTOM_OF_THE_OPERA / THE_JACKAL (identical
         DISCIDs) differ by more than 3 bytes: not recovered.   [any other pattern]
  CHT #2 bytes 8-15  = low 64 bits of SHA-1(DKF.AACS)              [mismatch]
  CHT #2 bytes 16-35 = SHA-1(MNGCPY_MANIFEST.XML)                  [mismatch]
  CHT #2 bytes 36-55 = FF*20 (no Category 1 VTUF.AACS)             [other]
  CHT #2 VTUF### slot (56 + 20*###) = SHA-1(first HASH_SIZE bytes);
         slots of absent VTUFs and all ATUF slots = FF*20.         [mismatch]
  Certificate Total_Number_of_HashUnits = NHV + NHA + 3 + (VTUF files present).
                                                                   [other count]
  "Low 64 bits" = the LAST 8 bytes of the 20-byte SHA-1 digest.   [first 8 match instead]
"""
import hashlib
import re
from collections import Counter

from lib import CORPUS

be = lambda b: int.from_bytes(b, "big")
sha1 = lambda b: hashlib.sha1(b).digest()
FF20 = b"\xff" * 20

ORIGINAL_TAIL = {"HOT_FUZZ": bytes.fromhex("66492d"),
                 "PREMONITION_GER": bytes.fromhex("4d01cf")}
UNRECOVERED = {"BROTHERS_GRIMM", "PHANTOM_OF_THE_OPERA", "THE_JACKAL"}

results = Counter()
hash8 = {}
units = []
discs = 0

for d in sorted(CORPUS.iterdir()):
    tree = next((t for t in ("ANY!", "AAC!") if (d / f"{t}__CONTENT_HASH_TABLE2.AACS").exists()), None)
    if not tree:
        continue
    f = lambda n: (d / f"{tree}__{n}").read_bytes()
    cert, c1, c2 = f("CONTENT_CERT.AACS"), f("CONTENT_HASH_TABLE1.AACS"), f("CONTENT_HASH_TABLE2.AACS")
    discs += 1

    nhv = be(c1[0:4])
    assert len(c1) == 8 + 8 * nhv and nhv <= 500000 and not any(c1[4:8]), d.name
    nha = be(c2[40056:40060])
    assert len(c2) == 40060 + 8 * nha, d.name

    assert cert[40:60] == sha1(c1), (d.name, "cert digest #1")
    assert cert[60:80] == sha1(c2), (d.name, "cert digest #2")

    discid = (d / "ADV_OBJ__DISCID.DAT").read_bytes()
    sly = discid[41:44] == b"SLY"
    if not sly:
        assert c2[0:8] == sha1(discid)[-8:], (d.name, "DISCID hash")
        assert c2[0:8] != sha1(discid)[:8], d.name
        results["DISCID hash matches as shipped"] += 1
    else:
        assert c2[0:8] != sha1(discid)[-8:], (d.name, "SLY disc unexpectedly matches")
        orig = ORIGINAL_TAIL.get(d.name, b"DVD" if discid[28:41].isascii() else None)
        if orig is None:
            assert d.name in UNRECOVERED, d.name
            results["DISCID SLY-rewritten, original not recovered"] += 1
        else:
            assert c2[0:8] == sha1(discid[:41] + orig + discid[44:])[-8:], (d.name, orig)
            results["DISCID SLY-rewritten, original tail restored"] += 1
    assert c2[8:16] == sha1(f("DKF.AACS"))[-8:], (d.name, "DKF hash")
    assert c2[16:36] == sha1(f("MNGCPY_MANIFEST.XML")), (d.name, "manifest hash")
    assert c2[36:56] == FF20, (d.name, "VTUF.AACS slot")

    present = {}
    for p in d.glob(f"{tree}__VTUF[0-9][0-9][0-9].AACS"):
        present[int(p.name[-8:-5])] = p.read_bytes()
    for k in range(1000):
        slot = c2[56 + 20 * k:76 + 20 * k]
        if k in present:
            t = present[k]
            hs = be(t[17:21])
            assert slot == sha1(t[:hs]), (d.name, k, hs)
            if hs != 128:
                hash8[d.name] = (hs, slot == sha1(t[:128]))
            results["VTUF slot = SHA-1(first HASH_SIZE bytes)"] += 1
        else:
            assert slot == FF20, (d.name, "absent VTUF slot", k)
    assert c2[20056:40056] == FF20 * 1000, (d.name, "ATUF slots")
    # Table 3-17 "total number of hashes in CHT #1 and CHT #2": the FF-filled
    # CHT #2 slots are not counted; DISCID, DKF and MNGCPY always are.
    assert be(cert[2:6]) == nhv + nha + 3 + len(present), (d.name, "hash units")
    units.append(be(cert[2:6]) - nhv - nha)

print(f"discs={discs}")
print(dict(results))
print("HASH_SIZE != 128 (value, would SHA-1 of 128 bytes also match?):", hash8)
print("Total_Number_of_HashUnits - NHV - NHA:", dict(Counter(units)))
assert discs >= 1
print("E22 PASS")
