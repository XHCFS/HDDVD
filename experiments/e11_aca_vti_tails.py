#!/usr/bin/env python3
"""E11 — ACA directory formula; EVOBI/ATRI tails; listing absences.

Claims (spec/advanced/04, 06, 01, 09):
  ACA record size is 14 + (flags & 0xFF) + 32, not a fixed 58-byte stride.
  flags low 8 bits = name length; 32-byte pad is zero; N=6 saved archives, 30 members.
  IEEE CRC-32 of raw member bytes matches stored CRC iff flags high byte != 0xff.
  EVOBI+274 = listing EVO packs except PANS_LABYRINTH angles (2416/2431).
  EVOBI+278 = 1-based serial except SPARTACUS hole (2419/2431).
  EVOBI+280 = 0; +286 = 0xFF×16.
  ATRI AST_Ns at +14; bytes 16+4*AST_Ns .. 79 zero; +6 nonzero on 19/1131.
  7 ATRIs have dummy 7f7f7f00 words at +391 (palettes still not a closed table).
  SEARCH_FLG 0/1 = 106/13; no HVSO/APLST/Category 3; all listed VTUF are 144 B.

Falsifier: an ACA member whose (flags&0xFF) is not the name length; pack count
mismatch outside Pan's; a VTUF listing size other than 144.

Does not fetch ISOs. ACA files must already be saved under corpus/.
"""
import struct
import zlib
from collections import Counter
from pathlib import Path

from lib import CORPUS, discs, parse_listing


def parse_aca(path: Path):
    b = path.read_bytes()
    mag, vern, enc = b[:8], int.from_bytes(b[8:10], "big"), int.from_bytes(b[10:12], "big")
    n = int.from_bytes(b[12:14], "big")
    sz = int.from_bytes(b[14:18], "big")
    hdr18 = b[18:32]
    first = struct.unpack_from(">I", b, 32)[0]
    pos = 32
    rows = []
    for i in range(n):
        moff, mlen, crc, flags = struct.unpack_from(">IIIH", b, pos)
        namelen = flags & 0xFF
        name = b[pos + 14 : pos + 14 + namelen]
        pad = b[pos + 14 + namelen : pos + 14 + namelen + 32]
        rec = 14 + namelen + 32
        z = zlib.crc32(b[moff : moff + mlen]) & 0xFFFFFFFF
        rows.append(
            dict(
                i=i,
                pos=pos,
                moff=moff,
                mlen=mlen,
                crc=crc,
                flags=flags,
                name=name,
                rec=rec,
                pad=pad,
                crc_ok=z == crc,
            )
        )
        pos += rec
    return dict(
        mag=mag,
        vern=vern,
        enc=enc,
        n=n,
        size_ok=sz == len(b),
        hdr18_zero=hdr18 == b"\x00" * 14,
        first=first,
        dir_end=pos,
        gap=first - pos,
        rows=rows,
        body=b,
    )


acas = sorted(CORPUS.rglob("*.aca"))
assert len(acas) >= 6, [p.name for p in acas]
members = 0
crc_ok = crc_ff_fail = 0
for p in acas:
    r = parse_aca(p)
    assert r["mag"] == b"HDDVDACA", p
    assert r["vern"] == 0x0010 and r["enc"] == 1
    assert r["size_ok"] and r["hdr18_zero"]
    assert r["rows"][0]["moff"] == r["first"]
    for row in r["rows"]:
        members += 1
        assert (row["flags"] & 0xFF) == len(row["name"]), (p, row["name"], hex(row["flags"]))
        assert row["name"] and all(32 <= c < 127 for c in row["name"]), row["name"]
        assert row["pad"] == b"\x00" * 32
        assert row["moff"] + row["mlen"] <= len(r["body"]) and row["mlen"] > 0
        if (row["flags"] >> 8) == 0xFF:
            assert not row["crc_ok"], (p, row["name"])
            crc_ff_fail += 1
        else:
            assert row["crc_ok"], (p, row["name"])
            crc_ok += 1
    if (r["rows"][0]["flags"] >> 8) == 0xFF:
        assert r["gap"] == 283, (p, r["gap"])
        assert r["body"][r["dir_end"] : r["dir_end"] + 4] == b"AACS"
    else:
        assert r["gap"] == 0, (p, r["gap"])
print(f"ACA files={len(acas)} members={members} crc_ok={crc_ok} crc_ff_fail={crc_ff_fail}")
# per-record invariants above are the format claims; they held for every member.
# Totals are corpus-dependent (grew as more ACAs were saved); assert consistency only.
assert members == crc_ok + crc_ff_fail
assert len(acas) >= 6 and members >= 30, (len(acas), members)
print(f"  ACA invariants hold for all {members} members across {len(acas)} files "
      f"(crc_present_ok={crc_ok}, crc_absent_ff={crc_ff_fail})")


def parse_atri(vti):
    sa = struct.unpack_from(">I", vti, 184)[0]
    atrt = vti[sa * 2048 :]
    nr = struct.unpack_from(">H", atrt, 0)[0]
    offs = [struct.unpack_from(">I", atrt, 8 + 4 * i)[0] for i in range(nr)]
    return [atrt[o : o + 1024] for o in offs]


def parse_evobi(vti):
    esa = struct.unpack_from(">I", vti, 188)[0]
    ev = vti[esa * 2048 :]
    enr = struct.unpack_from(">H", ev, 2)[0]
    eoffs = [struct.unpack_from(">I", ev, 8 + 4 * i)[0] for i in range(enr)]
    return [ev[sa : sa + 320] for sa in eoffs]


def listing_sizes(disc: Path):
    sizes = {}
    for line in (disc / "_listing.txt").read_text(errors="replace").splitlines():
        if line.startswith("FILE"):
            _, sz, path = line.split(maxsplit=2)
            sizes[path.strip().split("/")[-1]] = int(sz)
    return sizes


pack_ok = pack_bad = idx_ok = idx_bad = extra282 = 0
n_ev = 0
pad280 = 0
ff286 = 0
zero38 = 0
for p in sorted(CORPUS.glob("*/HVDVD_TS__HVA00001.VTI")):
    sizes = listing_sizes(p.parent)
    for i, e in enumerate(parse_evobi(p.read_bytes()), 1):
        n_ev += 1
        name = e[2:38].split(b"\x00", 1)[0].decode("ascii", "replace")
        packs = struct.unpack_from(">I", e, 274)[0]
        idx = struct.unpack_from(">H", e, 278)[0]
        if struct.unpack_from(">H", e, 280)[0] == 0:
            pad280 += 1
        extra = struct.unpack_from(">I", e, 282)[0]
        if extra:
            extra282 += 1
        if e[286:302] == b"\xff" * 16:
            ff286 += 1
        if e[38:264] == b"\x00" * 226:
            zero38 += 1
        fsz = sizes.get(name)
        if fsz == packs * 2048:
            pack_ok += 1
        else:
            pack_bad += 1
        if idx == i:
            idx_ok += 1
        else:
            idx_bad += 1

print(
    f"EVOBI n={n_ev} pack_ok={pack_ok} pack_bad={pack_bad} "
    f"idx_ok={idx_ok} idx_bad={idx_bad} extra282={extra282}"
)
assert n_ev == 2431
assert pack_ok == 2416 and pack_bad == 15
assert idx_ok == 2419 and idx_bad == 12
assert pad280 == 2431 and ff286 == 2431 and zero38 == 2431
assert extra282 == 100

n_atri = ast_ok = plus6 = pal391 = 0
for p in CORPUS.glob("*/HVDVD_TS__HVA00001.VTI"):
    for a in parse_atri(p.read_bytes()):
        n_atri += 1
        astn = struct.unpack_from(">H", a, 14)[0]
        if astn <= 16 and a[16 + 4 * astn : 80] == b"\x00" * (80 - (16 + 4 * astn)):
            ast_ok += 1
        if a[6:14] != b"\x00" * 8:
            plus6 += 1
            assert a[10:14] == b"\x00" * 4
        if a[391:395] == b"\x7f\x7f\x7f\x00":
            pal391 += 1

print(f"ATRI n={n_atri} AST_tail_zero={ast_ok} plus6={plus6} pal391={pal391}")
assert n_atri == 1131 and ast_ok == 1131
assert plus6 == 19 and pal391 == 7

flg = Counter()
discid_n = 0
for p in CORPUS.rglob("*DISCID.DAT"):
    b = p.read_bytes()
    discid_n += 1
    assert len(b) == 128 and b[:12] == b"HDDVD-V_CONF"
    flg[b[60]] += 1
    assert b[61:] == b"\x00" * 67
print("DISCID", discid_n, dict(flg))
assert discid_n == 119 and flg[0] == 106 and flg[1] == 13

hvso = aplst = cat3 = 0
vtuf_n = vtuf_not144 = 0
aca = xpl = 0
for disc, listing in discs():
    _, rows = parse_listing(listing)
    files = [(s, p) for k, s, p in rows if k == "FILE"]
    has_xpl = has_ifo = False
    for s, p in files:
        base = p.rsplit("/", 1)[-1]
        if "HVSO" in base:
            hvso += 1
        if base.startswith("APLST") and base.upper().endswith(".XPL"):
            aplst += 1
        if p.startswith("/ADV_OBJ/") and base.upper().endswith(".ACA"):
            aca += 1
        if p.startswith("/ADV_OBJ/") and base.startswith("VPLST") and base.upper().endswith(".XPL"):
            xpl += 1
            has_xpl = True
        if p.endswith(".IFO"):
            has_ifo = True
        if "VTUF" in base and base.endswith(".AACS") and "_BAK" not in p:
            vtuf_n += 1
            if s != 144:
                vtuf_not144 += 1
    if has_xpl and has_ifo:
        cat3 += 1

print(
    f"listings aca={aca} xpl={xpl} hvso={hvso} aplst={aplst} cat3={cat3} "
    f"vtuf={vtuf_n} vtuf_not144={vtuf_not144}"
)
assert aca == 409 and xpl == 247
assert hvso == 0 and aplst == 0 and cat3 == 0
assert vtuf_n == 217 and vtuf_not144 == 0
print("E11 PASS")
