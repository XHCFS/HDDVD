#!/usr/bin/env python3
"""E28 — the title timeline counts video fields, from the start of the EVOB.

Claims (spec/advanced/03_playlist.md §3.2, 07_map.md §7.4), falsifier in brackets:
  For every contiguous MAP with an EVOBI (found by EVOB_INDEX), the sum of
    EVOBU_PB_TM times 1501.5 equals EVOB_V_E_PTM - EVOB_V_S_PTM to one 90 kHz
    tick (an odd count gives a half tick), so one VSTU is 1.001/60 s on every
    disc.                                                      [any mismatch]
  A PrimaryAudioVideoClip with clipTimeBegin 00:00:00:00 that ends where its
    MAP ends spans (titleTimeEnd - titleTimeBegin) * 1501.5 = E - S (to one
    tick): one title
    count is one VSTU, not 1/60 s.                             [any mismatch]
  clipTimeBegin counts from EVOB_V_S_PTM: every clip fits in its EVOB as
    clipTimeBegin + duration <= sum(PB_TM), while EVOB_V_S_PTM is above zero
    on those EVOBs, so an absolute PTS reading would start before the EVOB.
                                                               [a clip overruns]
"""
import struct
import xml.etree.ElementTree as ET
from collections import Counter

from lib import CORPUS

# known: DELEXT8 has no EVOBI of its own (06 §6.3), so its EVOB_INDEX names
# another EVOB; DOWNFALL EVOB002's map runs exactly one 30-field EVOBU past
# EVOB_V_E_PTM
EXCEPTIONS = {("ETERNAL_SUNSHINE", "HVDVD_TS__DELEXT8.MAP"), ("DOWNFALL", "HVDVD_TS__EVOB002.MAP")}

NS = "{http://www.dvdforum.org/2005/HDDVDVideo/Playlist}"


def count(s):
    h, m, sec, f = map(int, s.split(":"))
    return (3600 * h + 60 * m + sec) * 60 + f


def evobis(vti):
    sa = struct.unpack_from(">I", vti, 188)[0] * 2048
    n = struct.unpack_from(">I", vti, sa)[0]
    out = {}
    for i in range(n):
        e = sa + struct.unpack_from(">I", vti, sa + 8 + 4 * i)[0]
        s, en = struct.unpack_from(">II", vti, e + 266)
        out[struct.unpack_from(">H", vti, e + 278)[0]] = (s, en)
    return out


def vstu(n, ticks):
    return abs(n * 3003 - ticks * 2) <= 2


def map_info(b):
    if struct.unpack_from(">H", b, 55)[0] != 1:
        return None
    sa, index, n = struct.unpack_from(">IHH", b, 384)
    pb = sum((struct.unpack_from(">I", b, sa + 4 * j)[0] >> 13) & 0xFF for j in range(n))
    return index, pb


maps_ok = maps_bad = 0
whole_ok = whole_1500 = whole_bad = 0
fits = overruns = start_above_zero = 0
bad = []
for vti_path in sorted(CORPUS.glob("*/HVDVD_TS__HVA00001.VTI")):
    disc = vti_path.parent
    ev = evobis(vti_path.read_bytes())
    info = {}
    for m in disc.glob("HVDVD_TS__*.MAP"):
        r = map_info(m.read_bytes())
        if not r or r[0] not in ev:
            continue
        s, e = ev[r[0]]
        info[m.name[len("HVDVD_TS__"):].upper()] = (r[1], s, e)
        if vstu(r[1], e - s):
            maps_ok += 1
        elif (disc.name, m.name) in EXCEPTIONS:
            print(f"known exception {disc.name} {m.name}: {r[1]} VSTU, E - S {e - s} "
                  f"({(r[1] * 1501.5 - (e - s)) / 1501.5:+.2f} VSTU)")
        else:
            maps_bad += 1
            bad.append((disc.name, m.name, r[1], e - s))
    for x in disc.glob("ADV_OBJ__VPLST[0-9][0-9][0-9].XPL"):
        root = ET.parse(x).getroot()
        for ts in root.iter(NS + "TitleSet"):
            if ts.get("timeBase", "60fps") != "60fps":
                continue
            for c in ts.iter(NS + "PrimaryAudioVideoClip"):
                key = c.get("src", "").rsplit("/", 1)[-1].upper()
                if key not in info:
                    continue
                pb, s, e = info[key]
                begin = count(c.get("clipTimeBegin", "00:00:00:00"))
                dur = count(c.get("titleTimeEnd")) - count(c.get("titleTimeBegin"))
                if begin + dur <= pb:
                    fits += 1
                    start_above_zero += s > 0
                else:
                    overruns += 1
                    bad.append((disc.name, key, begin + dur, pb))
                if begin == 0 and dur == pb:
                    if vstu(dur, e - s):
                        whole_ok += 1
                    elif abs(dur * 1500 - (e - s)) <= 1:
                        whole_1500 += 1
                    else:
                        whole_bad += 1

print(f"maps: sum(PB_TM) x 1501.5 == E - S on {maps_ok}, other {maps_bad}")
print(f"whole-EVOB clips: x 1501.5 {whole_ok}, x 1500 {whole_1500}, other {whole_bad}")
print(f"clips fit from EVOB start {fits} (EVOB start PTM > 0 on {start_above_zero}), overrun {overruns}")
for b in bad[:10]:
    print("  ", b)
assert maps_ok and not maps_bad, "PB_TM sum is not 1.001/60 s per unit"
assert whole_ok and not whole_1500 and not whole_bad, "title count is not one VSTU"
assert fits and not overruns, "a clip does not fit when counted from the EVOB start"
print("E28 PASS")
