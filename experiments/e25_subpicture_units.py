#!/usr/bin/env python3
"""E25 — HD DVD 8-bit Sub-picture Units (SPU) and SP_ATR, from real SP_PCKs.

Sources: US 2008/0298219 A1 [2] §5.5.4 (SPU for the pixel depth of 8 bits),
Table 66 (SPUH), §5.5.4.2 (run-length rule), Tables 61–62 (256 colour codes,
256 contrast values); sheet 08 §8.8, sheet 06 (ATRI).

Input:
  spec/raw/evo_samples/sppck_*.bin: the SP_PCKs of one SPU each from 12_MONKEYS
    (sub 0x21), 1408_DC (0x20, full-frame) and STALINGRAD (0x20, fade).
  corpus/*/HVDVD_TS__HVA00001.VTI for SP_ATR.
  E25_LIVE=1 additionally pulls 12 mid-feature EVOBUs from each disc in LIVE
    over HTTP ranges (tools/udfgrab.py) and checks every SPU in them.

Claims (falsifier in brackets):
  SPUH is 10 bytes: SPU_ID 0000h, SPU_SZ u32 (= reassembled size, even),
    SP_DCSQT_SA u32.                                                  [other]
  SP_DCSQ = STM u16 + next-DCSQ address u32 + commands to 0xFF; the last
    DCSQ points at itself and ends the SPU (FF padding only).       [other]
  Opcodes seen: 01 STA_DSP, 02 STP_DSP (no operand); 83 = 256 x (Y,Cr,Cb);
    84 = 256 contrast bytes; 85 = display area, two 12/12-bit pairs
    (x start/end, y start/end); 86 = top/bottom PXD addresses, u32 each.
    Nothing else.                                                   [other opcode]
  PXD 8bitRLC: unit = Comp(1) + flag(1) + 2-bit specified pixel (flag 0) or
    8-bit palette index (flag 1); Comp=1 adds LEXT(1) + RUN 3 bits (+2) or
    7 bits (+9), RUN=0 with LEXT=1 = to end of line. Lines byte-aligned.
    Top field at SPUH end (10); each field decodes to the next address
    within 0-2 zero pad bytes, after at most one extra empty line. [mismatch]
  Contrast FF = fully transparent: the most-used pixel value (the clear
    area around the text) has contrast FF on every SPU. It is index 0 on most
    discs; 1408_DC uses 8-bit index 227. STALINGRAD fades by stepping all
    contrasts FF -> 88 -> FF in contrast-only DCSQs.                 [other]
  STM unit = 1024 / 90000 s (DVD parity): STP_DSP time x 1024 is below the
    PTS gap to the next SPU of the same stream.                      [exceeds]
  SP_ATR (5 bytes): byte 0 = 80h (coding mode 100b, 8-bit), byte 1 =
    20h + stream index (the sub_stream_id), bytes 2–4 zero.          [other]
"""
import os
import sys
from collections import Counter
from pathlib import Path

from lib import CORPUS

be = lambda b: int.from_bytes(b, "big")
SAMPLES = Path(__file__).resolve().parent.parent / "spec" / "raw" / "evo_samples"
LEN = {0x01: 0, 0x02: 0, 0x83: 768, 0x84: 256, 0x85: 6, 0x86: 8}
LIVE = [("12_MONKEYS", "PEVOB_1.EVO"), ("1408_DC", "EVOB-Feature0.EVO"),
        ("16_BLOCKS", "PEVOB.EVO"), ("40YR_OLD_VIRGIN", "FEATURE_2.EVO"),
        ("DOOM", "FEATURE.EVO"), ("GOODFELLAS", "PEVOB1_1.EVO"),
        ("HOT_FUZZ", "L0_mainMovie.EVO"), ("MYSTERY_MEN", "FEATURE_1.EVO"),
        ("PANS_LABYRINTH", "feature_l0.EVO"), ("STALINGRAD", "L0_mainMovie.EVO"),
        ("TRANSFORMERS", "FEATURE_1.EVO"), ("U2_RATTLE_AND_HUM", "FEATURE_1.EVO")]


def spus(d):
    """Reassemble SPUs per sub_stream_id from 0xBD packets with sub 0x20-0x3F."""
    buf, need, pts = {}, {}, {}
    for k in range(len(d) // 2048):
        p, i = d[k * 2048:(k + 1) * 2048], 14 + (d[k * 2048 + 13] & 7)
        while i + 6 <= 2048 and p[i:i + 3] == b"\0\0\1":
            sid, ln = p[i + 3], be(p[i + 4:i + 6])
            if sid == 0xBD:
                pl = p[i + 9 + p[i + 8]:i + 6 + ln]
                sub = pl[0]
                if 0x20 <= sub <= 0x3F:
                    if not buf.get(sub):
                        buf[sub], need[sub] = bytearray(), be(pl[3:7])
                        t = p[i + 9:i + 14]
                        pts[sub] = (((t[0] >> 1) & 7) << 30 | be(t[1:3]) >> 1 << 15
                                    | be(t[3:5]) >> 1) if p[i + 7] & 0x80 else None
                    buf[sub] += pl[1:]
                    if len(buf[sub]) >= need[sub]:
                        yield sub, pts[sub], bytes(buf[sub][:need[sub]])
                        buf[sub] = bytearray()
            i += 6 + ln


def dcsqs(u):
    sa, out = be(u[6:10]), []
    while True:
        stm, nxt, i, cmds = be(u[sa:sa + 2]), be(u[sa + 2:sa + 6]), sa + 6, []
        while u[i] != 0xFF:
            assert u[i] in LEN, f"opcode {u[i]:02x}"
            cmds.append((u[i], u[i + 1:i + 1 + LEN[u[i]]]))
            i += 1 + LEN[u[i]]
        out.append((stm, cmds, i + 1))
        if nxt == sa:
            return out
        assert nxt > sa
        sa = nxt


def field_end(u, pos, width, lines, hist=None):
    bit = pos * 8

    def get(n):
        nonlocal bit
        v = 0
        for _ in range(n):
            v = v << 1 | (u[bit >> 3] >> (7 - (bit & 7))) & 1
            bit += 1
        return v
    for _ in range(lines):
        x = 0
        while x < width:
            comp = get(1)
            pix = get(8) if get(1) else get(2)
            if not comp:
                run = 1
            elif not get(1):
                run = get(3) + 2
            else:
                r = get(7)
                run = width - x if r == 0 else r + 9
            x += run
            if hist is not None:
                hist[pix] += run
        assert x == width, "line overrun"
        bit = (bit + 7) & ~7
    return bit >> 3


def check(u, c):
    assert u[:2] == b"\0\0" and len(u) % 2 == 0, "SPUH / even size"
    q = dcsqs(u)
    assert all(x == 0xFF for x in u[q[-1][2]:]), "tail"
    for stm, cmds, _ in q:
        for op, _ in cmds:
            c[f"op {op:02x}"] += 1
    first = dict(q[0][1])
    a = first[0x85]
    x0, x1, y0, y1 = be(a[:3]) >> 12, be(a[:3]) & 0xFFF, be(a[3:]) >> 12, be(a[3:]) & 0xFFF
    top, bot, sa = be(first[0x86][:4]), be(first[0x86][4:]), be(u[6:10])
    w, h = x1 - x0 + 1, y1 - y0 + 1
    assert top == 10 and x1 < 1920 and y1 < 1080
    hist = Counter()
    for start, stop, lines in ((top, bot, (h + 1) // 2), (bot, sa, h // 2)):
        e = field_end(u, start, w, lines, hist)
        if stop - e > 2:
            e = field_end(u, start, w, lines + 1)
            c["extra empty line"] += 1
        assert 0 <= stop - e <= 2 and not any(u[e:stop]), (start, e, stop, u[e:stop].hex())
        c[f"field pad {stop - e}"] += 1
    dominant = hist.most_common(1)[0][0]
    assert first[0x84][dominant] == 0xFF, ("dominant pixel not transparent", dominant)
    c[f"dominant index {'0' if dominant == 0 else 'other'}"] += 1
    c["SPU"] += 1
    c["multi-DCSQ"] += len(q) > 2
    return next((stm for stm, cmds, _ in q if any(op == 2 for op, _ in cmds)), None)


def check_all(d, c):
    last = {}
    for sub, pts, u in spus(d):
        stp = check(u, c)
        if sub in last and pts is not None and last[sub][0] is not None and last[sub][1] is not None:
            assert last[sub][1] * 1024 <= pts - last[sub][0], ("STP after next SPU", sub)
            c["STM pairs"] += 1
        last[sub] = (pts, stp)


c = Counter()
for f in sorted(SAMPLES.glob("sppck_*.bin")):
    check_all(f.read_bytes(), c)
print("samples:", dict(sorted(c.items())))

if os.environ.get("E25_LIVE"):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
    from udfgrab import Remote, UDF
    for disc, evo in LIVE:
        L = (CORPUS / disc / "_listing.txt").read_text(errors="replace")
        m = (CORPUS / disc / f"HVDVD_TS__{evo[:-4]}.MAP").read_bytes()
        sa, n = be(m[384:388]), be(m[390:392])
        sz = [be(m[sa + 4 * i:sa + 4 * i + 4]) & 0x1FFF for i in range(n)]
        j = n // 2
        u = UDF(Remote(L.splitlines()[0].lstrip("# ").strip()))
        ext = next(e for p, e, s, dr in u.walk() if not dr and p.endswith("/HVDVD_TS/" + evo))[0]
        acc, left, data, cum, segs = sum(sz[:j]), sum(sz[j:j + 12]), bytearray(), 0, []
        for pos, ln in ext:
            segs.append((cum, ln // 2048, pos))
            cum += ln // 2048
        while left:
            st, sl, pos = next(s for s in segs if s[0] <= acc < s[0] + s[1])
            k = min(left, st + sl - acc, 2048)
            data += u.r._get((u.part_start + pos + acc - st) * 2048, k * 2048)
            acc, left = acc + k, left - k
        before = c["SPU"]
        check_all(bytes(data), c)
        print(f"{disc:20s} SPUs {c['SPU'] - before}")
    print("live:", dict(sorted(c.items())))

atr = Counter()
for v in sorted(CORPUS.glob("*/HVDVD_TS__HVA00001.VTI")):
    b = v.read_bytes()
    at = be(b[184:188]) * 2048
    for i in range(be(b[at:at + 2])):
        a = b[at + be(b[at + 8 + 4 * i:at + 12 + 4 * i]):][:1024]
        for j in range(a[229]):
            w = a[230 + 5 * j:235 + 5 * j]
            assert w[0] == 0x80 and w[1] == 0x20 + j and not any(w[2:]), (v.parent.name, i, j, w.hex())
            atr["SP_ATR"] += 1
print(dict(atr))
print("E25 PASS")
