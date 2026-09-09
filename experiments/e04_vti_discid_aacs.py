#!/usr/bin/env python3
"""E04 — VTI / DISCID / AACS file headers on saved bytes.

Claims:
  VTI starts ADVANCED-VTS (12-byte ID convention).
  DISCID.DAT is 128 bytes, ID HDDVD-V_CONF.
  VTKF/DKF/VTUF use DVD_HD_V_* IDs and size field equals file length.

Falsifier: a VTI without that magic; DISCID not 128 bytes; VTKF size field
not 2480.

ISO URLs: first line of each disc listing.
"""
from lib import CORPUS, discs, saved, parse_listing

vti = list(CORPUS.rglob("*.VTI"))
assert vti, "no VTI"
bad = [p.name for p in vti if p.read_bytes()[:12] != b"ADVANCED-VTS"]
print(f"vti={len(vti)} bad_magic={len(bad)}")
assert not bad

discid = list(CORPUS.rglob("*DISCID.DAT"))
print(f"discid={len(discid)}")
for p in discid:
    b = p.read_bytes()
    assert len(b) == 128, (p, len(b))
    assert b[:12] == b"HDDVD-V_CONF", p

# AACS headers: whatever was saved
checks = {
    b"DVD_HD_V_TKF": 2480,
    b"DVD_HD_V_DKF": 64,
    b"DVD_HD_V_TUF": 144,
}
n = 0
for p in CORPUS.rglob("*.AACS"):
    b = p.read_bytes()
    mag = b[:12]
    if mag in checks:
        size = int.from_bytes(b[12:16], "big")
        assert size == checks[mag] == len(b), (p, mag, size, len(b))
        n += 1
        if mag == b"DVD_HD_V_TKF":
            name = b[16:28]
            assert name.startswith(b"VPLST") or name.startswith(b"APLST") or name == b"\xff" * 12, name
print(f"aacs_headers_checked={n}")
print("E04 PASS")
