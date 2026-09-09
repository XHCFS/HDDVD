#!/usr/bin/env python3
"""E13 — adversarial layout census (MAP pad/ILVU units, ATRI mid-slot, V_ATR, EVOBI names).

Claims (spec/advanced/06, 07; spec/clean/15):
  Bytes [128..371] and [374..383] of every MAP are zero.
  u16be @372 is 0 on contiguous maps and equals the ILVU walk-until-SZ=0
  count on the four interleaved maps. TMAPI_SRP.ILVU_ENT_Ns is still 0.
  ILVU records cycle TMAPI 0..Ns-1. Each record's SZ is how many EVOBUs of
  that angle sit contiguously at ADR (pack index). Next ADR = this ADR +
  sum of those SZ sizes from that TMAPI. SZ-as-packs never matches.
  V_ATR bits 31-30 are never AVC (10b) or VC-1 (11b) on 1131 ATRIs.
  ATRI bytes 80-228 are not always dead: some store 01 1c 00 c4 at @193.
  EVOBI filename is usually NUL-padded; at least one fills all 36 bytes.

Falsifier: a contiguous MAP with nonzero @372; an interleaved MAP whose
@372 ≠ walk count; an ILVU unit whose pack span ≠ sum of per-angle EVOBU_SZ;
a V_ATR compression nibble 10/11.

Does not fetch ISOs.
"""
from __future__ import annotations

import struct
from collections import Counter
from pathlib import Path

from lib import CORPUS


def decode_ent(w: int):
    return (w >> 21) & 0x7FF, (w >> 13) & 0xFF, w & 0x1FFF


def parse_map(b: bytes):
    ns = struct.unpack_from(">H", b, 55)[0]
    ilvui_sa = struct.unpack_from(">I", b, 57)[0]
    ty = struct.unpack_from(">H", b, 20)[0]
    srps = []
    for i in range(ns):
        off = 384 + 32 * i
        sa, vts, nent, ilvu_ns = struct.unpack_from(">IH2H", b, off)
        srps.append(dict(sa=sa, vts=vts, nent=nent, ilvu_ns=ilvu_ns, slot_tail=b[off + 10 : off + 32]))
        ents = []
        for j in range(nent):
            w = struct.unpack_from(">I", b, sa + 4 * j)[0]
            ents.append(decode_ent(w))
        srps[-1]["ents"] = ents
    ilvu = []
    if ilvui_sa != 0xFFFFFFFF:
        pos = ilvui_sa
        while pos + 6 <= len(b):
            adr, sz = struct.unpack_from(">IH", b, pos)
            if sz == 0 and adr == 0:
                break
            ilvu.append((adr, sz))
            pos += 6
            if sz == 0:
                break
    return dict(ty=ty, ns=ns, ilvui_sa=ilvui_sa, srps=srps, ilvu=ilvu, raw=b)


maps = sorted(CORPUS.rglob("*.MAP"))
assert maps, "no MAP on disk"

pad_ok = pad_fail = 0
u372_zero = 0
ilv_files = []
slot_tail_zero = 0
slot_n = 0
for f in maps:
    b = f.read_bytes()
    if b[:12] != b"HDDVD_TMAP00":
        raise SystemExit(f"bad magic {f}")
    m = parse_map(b)
    pad_a = b[128:372]
    pad_b = b[374:384]
    u372 = struct.unpack_from(">H", b, 372)[0]
    if pad_a == b"\x00" * 244 and pad_b == b"\x00" * 10:
        pad_ok += 1
    else:
        pad_fail += 1
        raise SystemExit(f"nonzero pad outside 372-373: {f} {[i for i,x in enumerate(b[128:384]) if x]}")
    for s in m["srps"]:
        slot_n += 1
        if s["slot_tail"] == b"\x00" * 22:
            slot_tail_zero += 1
        assert s["ilvu_ns"] == 0
    if m["ilvui_sa"] == 0xFFFFFFFF:
        assert u372 == 0, (f, u372)
        u372_zero += 1
    else:
        ilv_files.append((f, m, u372))

assert pad_ok == len(maps) and pad_fail == 0
assert slot_tail_zero == slot_n
print(f"MAP n={len(maps)} pad128_371_and_374_383_zero={pad_ok} contiguous_u372_zero={u372_zero}")
assert u372_zero == len(maps) - 4
assert len(ilv_files) == 4

for f, m, u372 in ilv_files:
    walk = len(m["ilvu"])
    assert u372 == walk, (f.name, u372, walk)
    ns = m["ns"]
    recs = m["ilvu"]
    idx = [0] * ns
    ang = 0
    adr_ok = 0
    adr_bad = []
    for i, (adr, sz) in enumerate(recs):
        ents = m["srps"][ang]["ents"]
        span = sum(ents[idx[ang] + k][2] for k in range(sz))
        idx[ang] += sz
        if i + 1 < len(recs):
            nxt = recs[i + 1][0]
            if nxt == adr + span:
                adr_ok += 1
            else:
                adr_bad.append((i, ang, adr, sz, span, nxt))
        ang = (ang + 1) % ns
    leftover = [(a, idx[a], len(m["srps"][a]["ents"])) for a in range(ns)]
    print(
        f"  ILVU {f.name} ns={ns} walk={walk} u372={u372} "
        f"adr_delta_ok={adr_ok}/{len(recs) - 1} leftover={leftover}"
    )
    assert not adr_bad, adr_bad[:5]
    assert all(used == nent for _, used, nent in leftover)
    pack_misread = sum(1 for i, (adr, sz) in enumerate(recs[:-1]) if recs[i + 1][0] == adr + sz)
    assert pack_misread == 0, (f.name, pack_misread)

print("ILVU: records cycle angles; SZ = EVOBU count of that angle; ADR = pack index")


def parse_atri(vti: bytes):
    sa = struct.unpack_from(">I", vti, 184)[0]
    atrt = vti[sa * 2048 :]
    nr = struct.unpack_from(">H", atrt, 0)[0]
    offs = [struct.unpack_from(">I", atrt, 8 + 4 * i)[0] for i in range(nr)]
    return [atrt[o : o + 1024] for o in offs]


def parse_evobi(vti: bytes):
    esa = struct.unpack_from(">I", vti, 188)[0]
    ev = vti[esa * 2048 :]
    enr = struct.unpack_from(">H", ev, 2)[0]
    eoffs = [struct.unpack_from(">I", ev, 8 + 4 * i)[0] for i in range(enr)]
    return [ev[sa : sa + 320] for sa in eoffs]


comp = Counter()
at193 = 0
at193_hex = Counter()
mid_nonzero = 0
n_atri = 0
name_full = []
n_ev = 0
for p in sorted(CORPUS.glob("*/HVDVD_TS__HVA00001.VTI")):
    b = p.read_bytes()
    for a in parse_atri(b):
        n_atri += 1
        vatr = struct.unpack_from(">I", a, 2)[0]
        comp[(vatr >> 30) & 3] += 1
        mid = a[80:229]
        if mid != b"\x00" * 149:
            mid_nonzero += 1
            at193_hex[a[193:197].hex()] += 1
            if a[193:197] == b"\x01\x1c\x00\xc4":
                at193 += 1
    for e in parse_evobi(b):
        n_ev += 1
        name = e[2:38]
        if b"\x00" not in name:
            name_full.append((p.parent.name, name.decode("ascii")))

print(f"ATRI n={n_atri} V_ATR_comp={dict(comp)} mid80_228_nz={mid_nonzero} @193_011c00c4={at193} @193_hex={dict(at193_hex)}")
print(f"EVOBI n={n_ev} name_fills_36={name_full}")
assert n_atri == 1131
assert comp[2] == 0 and comp[3] == 0  # never AVC / VC-1 in V_ATR
assert at193 == mid_nonzero  # every mid-slot hit is that dword
assert at193 == 16
assert len(name_full) == 1
assert "SMOKEYANDBANDIT_LOADEDUPMPEG2_HD.EVO" in name_full[0][1]
print("E13 PASS")
