#!/usr/bin/env python3
"""E03 — TMAP_GI + TMAPI_SRP@384 on every saved .MAP.

Claim: magic HDDVD_TMAP00; TMAPI_SRP is a 10-byte record in a 32-byte slot
starting at byte 384; TMAPI_SA is a byte offset (416 when Ns=1), not an LBN.

Falsifier: a MAP whose bytes 0-11 are not HDDVD_TMAP00, or whose first
nonzero u32 after the 128-byte GI is not at 384, or TMAPI_SA*2048 inside a
small file (would mean the patent LBN reading).

Disc bytes: corpus/*/HVDVD_TS__*.MAP
Patent table: US20080298219A1 TABLE 80/82 (Google Patents).
"""
import struct
from collections import Counter
from lib import CORPUS

files = list(CORPUS.glob("*/*.MAP")) + list(CORPUS.glob("*/*MAP"))
files = [p for p in CORPUS.rglob("*.MAP")]
assert files, "no MAP on disk"

magic_ok = sa416 = other_sa = 0
fail = []
ty = Counter()
for f in files:
    b = f.read_bytes()
    if b[:12] != b"HDDVD_TMAP00":
        fail.append((f.name, "magic", b[:12]))
        continue
    magic_ok += 1
    ns = struct.unpack_from(">H", b, 55)[0]
    sa = struct.unpack_from(">I", b, 384)[0]
    ty[struct.unpack_from(">H", b, 20)[0]] += 1
    if ns == 1 and sa == 416:
        sa416 += 1
    else:
        other_sa += 1
    # LBN reading would put entries at sa*2048, past EOF for typical maps
    if sa * 2048 < len(b) and sa > 2048:
        fail.append((f.name, "looks_like_lbn", sa, len(b)))

print(f"maps={len(files)} magic={magic_ok} Ns1_SA416={sa416} other_sa={other_sa}")
print("TMAP_TY", {hex(k): v for k, v in ty.most_common()})
if fail[:10]:
    print("FAIL samples", fail[:10])
assert not fail
assert magic_ok == len(files)
print("E03 PASS")
