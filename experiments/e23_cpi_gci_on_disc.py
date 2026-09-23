#!/usr/bin/env python3
"""E23 — AACS CPI and GCI layout read from real NV_PCKs.

Claims (spec/advanced/08_evo.md §8.5, 09_aacs.md §9.6), falsifier in brackets:
  GCI sub_stream_id 0x04 at pack offset 47, so CPI starts at pack 0x3C. [other]
  GCI payload byte 1 = 0x40; bytes 2-6 = EVOBU start PTM (90 kHz), equal to the
    VTI EVOBI start PTM at the EVOB's first EVOBU; bytes 7-12 zero.    [mismatch]
  CPI (payload 13-28), AACS discs: CH_PTR +1 per EVOBU and within 1..NHV of CHT #1;
    URMI = 0x7FFF; KEY_VF = 00; TITLE_KEY_PTR, if non-zero, is an occupied
    VTKF slot. Non-AACS disc (1408_DC): all 16 CPI bytes zero.        [any other]
  DSI vobu_ea + 1 = MAP EVOBU_SZ; a zero-filled PCI slot is skipped by scanning
    for the next 00 00 01 BF (RAMBO_1_FRA).                          [mismatch]

HTTP-ranges the Archive.org ISOs like e09 (tools/udfgrab.py). Results cached in
/tmp/e23_cache.json. Default: 4 discs; E23_ALL=1 probes all 12 in DISCS.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
from udfgrab import Remote, UDF  # noqa: E402

from lib import CORPUS  # noqa: E402

be = lambda b: int.from_bytes(b, "big")
DISCS = ["12_MONKEYS", "RAMBO_1_FRA", "HOT_FUZZ", "1408_DC",
         "BATMAN_BEGINS", "TRANSFORMERS", "RESIDENT_EVIL3_GER", "AEON_FLUX",
         "DEATH_PROOF_GER", "KING_OF_CALIFORNIA", "MYSTERY_MEN", "PANS_LABYRINTH"]
K = 24
CACHE = "/tmp/e23_cache.json"


def bf_packets(pk):
    """Every private_stream_2 payload in a pack, found by scanning for start codes."""
    out, i = {}, 0
    while (i := pk.find(b"\x00\x00\x01\xbf", i)) >= 0:
        ln = be(pk[i + 4:i + 6])
        pl = pk[i + 6:i + 6 + ln]
        if pl:
            out[pl[0]] = (i + 6, pl)
        i += 6 + ln
    return out


def probe(disc):
    d = CORPUS / disc
    listing = (d / "_listing.txt").read_text(errors="replace")
    url = listing.splitlines()[0].lstrip("# ").strip()
    maps = sorted(d.glob("HVDVD_TS__*.MAP"), key=lambda p: p.stat().st_size, reverse=True)
    mp = next(m for m in maps if f"/HVDVD_TS/{m.name[10:-4]}.EVO" in listing)
    evo = mp.name[10:-4] + ".EVO"
    b = mp.read_bytes()
    sa, n = be(b[384:388]), be(b[390:392])
    sizes = [be(b[sa + 4 * i:sa + 4 * i + 4]) & 0x1FFF for i in range(n)]
    u = UDF(Remote(url))
    ext = next(e for p, e, s, dr in u.walk() if not dr and p.endswith("/HVDVD_TS/" + evo))[0]
    segs, cum = [], 0
    for pos, ln in ext:
        segs.append((cum, ln // 2048, pos))
        cum += ln // 2048
    rows, acc = [], 0
    for j in range(min(K, len(sizes))):
        st, _, pos = next(s for s in segs if s[0] <= acc < s[0] + s[1])
        pk = u.r.read((u.part_start + pos + acc - st) * 2048, 2048)
        bf = bf_packets(pk)
        rows.append({"gci_off": bf[0x04][0], "gci": bf[0x04][1][:64].hex(),
                     "dsi_ea": be(bf[0x01][1][9:13]) if 0x01 in bf else None,
                     "sz": sizes[j]})
        acc += sizes[j]
    return {"evo": evo, "rows": rows}


def evobi_start(disc, evo):
    v = (CORPUS / disc / "HVDVD_TS__HVA00001.VTI").read_bytes()
    t = be(v[188:192]) * 2048
    nr, first = be(v[t + 2:t + 4]), be(v[t + 8:t + 12])
    for i in range(nr):
        e = v[t + first + 320 * i:t + first + 320 * (i + 1)]
        if e[2:38].rstrip(b"\x00 ") == evo.encode():
            return be(e[266:270])


cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
todo = DISCS if os.environ.get("E23_ALL") else DISCS[:4]
for disc in todo:
    if disc not in cache:
        cache[disc] = probe(disc)
        json.dump(cache, open(CACHE, "w"))
    r = cache[disc]
    rows = r["rows"]
    g = [bytes.fromhex(x["gci"]) for x in rows]
    assert all(x["gci_off"] == 47 for x in rows), disc
    assert all(x[1] == 0x40 and not any(x[7:13]) for x in g), disc
    assert be(g[0][2:7]) == evobi_start(disc, r["evo"]), (disc, "PTM vs EVOBI")
    assert all(be(b[2:7]) > be(a[2:7]) for a, b in zip(g, g[1:])), disc
    assert all(x["dsi_ea"] + 1 == x["sz"] for x in rows), (disc, "DSI vs MAP")
    cpi = [x[13:29] for x in g]
    tree = next((t for t in ("ANY!", "AAC!") if (CORPUS / disc / f"{t}__CONTENT_HASH_TABLE1.AACS").exists()), None)
    if tree is None:
        assert all(not any(c) for c in cpi), (disc, "non-AACS CPI not zero")
        print(f"{disc:20s} non-AACS: CPI zero")
        continue
    nhv = be((CORPUS / disc / f"{tree}__CONTENT_HASH_TABLE1.AACS").read_bytes()[:4])
    ch = [be(c[4:8]) for c in cpi]
    assert all(b - a == 1 for a, b in zip(ch, ch[1:])) and 1 <= ch[0] and ch[-1] <= nhv, (disc, ch[:3], nhv)
    assert all(c[0] >> 6 == 0 and be(c[8:10]) == 0x7FFF for c in cpi), disc
    vtkf = sorted((CORPUS / disc).glob(f"{tree}__VTKF*.AACS"))[0].read_bytes()
    for ptr in {be(c[1:3]) for c in cpi} - {0}:
        assert vtkf[128 + 36 * (ptr - 1)] >> 7 == 1, (disc, "pointer to empty slot", ptr)
    print(f"{disc:20s} CH_PTR {ch[0]}..{ch[-1]} of NHV {nhv}, TITLE_KEY_PTR "
          f"{sorted({be(c[1:3]) for c in cpi})}, CCI_SS {cpi[0][10:12].hex()}")
print("E23 PASS")
