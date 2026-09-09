#!/usr/bin/env python3
"""E08 — TABLE 83 figure bitfields, ATRI V_ATR, ATRN, MAP/VTI BUP identity.

Claims:
  EVOBU_ENT is the patent TABLE 83 figure (not the DOWNFALL-only 11-bit SZ
  reading): 1STREF_SZ b31-21 (11), EVOBU_PB_TM b20-13 (8), EVOBU_SZ b12-0 (13).
  Some corpus entries need the extra two SZ bits (sz > 2047).
  Each EVOBI.EVOB_ATRN is a 1-based index into that disc's ATRI table.
  ATRI+2 is TABLE 9/16 V_ATR; source-picture-resolution nibble is 1100b
  (1920×1080), 0101b (720×480/576), or 0000b (352×240/288).
  When a .BUP sits next to a .MAP or .VTI, the bytes are identical.

Falsifier: an EVOBU_ENT whose 13-bit SZ field is 0 on a nonempty map;
an ATRN of 0 or > ATRI count; a V_ATR resolution nibble outside {0,5,12};
a BUP that differs from its sibling.

Does not fetch ISOs. MAP vs DSI identity is in spec/clean/08 (HTTP range).
Patent figure: US20080298219A1-20081204-C00040.png (TABLE 83).
"""
import struct
from collections import Counter
from lib import CORPUS

RES_NIBBLE = {0, 5, 12}  # TABLE 9: 0000b / 0101b / 1100b


def decode_ent(w):
    return (w >> 21) & 0x7FF, (w >> 13) & 0xFF, w & 0x1FFF


sz_gt2047 = 0
ent_n = 0
sz0 = 0
for f in CORPUS.rglob("*.MAP"):
    b = f.read_bytes()
    if b[:12] != b"HDDVD_TMAP00":
        continue
    sa = struct.unpack_from(">I", b, 384)[0]
    nent = struct.unpack_from(">H", b, 390)[0]
    for i in range(nent):
        w = struct.unpack_from(">I", b, sa + 4 * i)[0]
        _ref, _pb, sz = decode_ent(w)
        ent_n += 1
        if sz == 0:
            sz0 += 1
        if sz > 2047:
            sz_gt2047 += 1

print(f"EVOBU_ENT n={ent_n} sz>2047={sz_gt2047} sz==0={sz0}")
assert ent_n > 2_000_000
assert sz0 == 0
assert sz_gt2047 > 0  # 13-bit field is used; 11-bit empirical was DOWNFALL-local


def parse_atri(vti_bytes):
    sa = struct.unpack_from(">I", vti_bytes, 184)[0]
    atrt = vti_bytes[sa * 2048 :]
    nr = struct.unpack_from(">H", atrt, 0)[0]
    offs = [struct.unpack_from(">I", atrt, 8 + 4 * i)[0] for i in range(nr)]
    return [atrt[o : o + 1024] for o in offs]


def parse_evobi(vti_bytes):
    esa = struct.unpack_from(">I", vti_bytes, 188)[0]
    ev = vti_bytes[esa * 2048 :]
    enr = struct.unpack_from(">H", ev, 2)[0]
    eoffs = [struct.unpack_from(">I", ev, 8 + 4 * i)[0] for i in range(enr)]
    out = []
    for sa in eoffs:
        e = ev[sa : sa + 320]
        atrn = struct.unpack_from(">H", e, 264)[0]
        out.append(atrn)
    return out


atrn_ok = atrn_bad = 0
res = Counter()
bad_res = []
n_atri = 0
for p in CORPUS.glob("*/HVDVD_TS__HVA00001.VTI"):
    b = p.read_bytes()
    atris = parse_atri(b)
    n_atri += len(atris)
    for a in atris:
        nib = (a[4] >> 4) & 0xF
        res[nib] += 1
        if nib not in RES_NIBBLE:
            bad_res.append((p.parent.name, a[2:6].hex(), nib))
    for atrn in parse_evobi(b):
        if 1 <= atrn <= len(atris):
            atrn_ok += 1
        else:
            atrn_bad += 1

print(f"ATRI n={n_atri} ATRN ok={atrn_ok} bad={atrn_bad} res_nibble={dict(res)}")
assert atrn_bad == 0 and atrn_ok > 2000
assert not bad_res, bad_res[:5]

map_same = map_diff = map_none = 0
for m in CORPUS.rglob("*.MAP"):
    bup = m.with_suffix(".BUP")
    if not bup.exists():
        map_none += 1
        continue
    if m.read_bytes() == bup.read_bytes():
        map_same += 1
    else:
        map_diff += 1
vti_same = vti_diff = vti_none = 0
for v in CORPUS.rglob("*.VTI"):
    bup = v.with_suffix(".BUP")
    if not bup.exists():
        vti_none += 1
        continue
    if v.read_bytes() == bup.read_bytes():
        vti_same += 1
    else:
        vti_diff += 1

print(f"MAP BUP same={map_same} diff={map_diff} missing={map_none}")
print(f"VTI BUP same={vti_same} diff={vti_diff} missing={vti_none}")
assert map_diff == 0 and vti_diff == 0
assert map_same > 0 and vti_same > 0
print("E08 PASS")
