#!/usr/bin/env python3
"""E14 — thorough adversarial search over saved XPL / listings / VTI / MAP / DISCID / JS.

Closes or narrows spec/clean/15 ASK items that are machine-checkable without
fetching ISOs or unpacking firmware.
"""
from __future__ import annotations

import re
import struct
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

from lib import CORPUS, discs, parse_listing

NS = "{http://www.dvdforum.org/2005/HDDVDVideo/Playlist}"


def t2f(s, tb=60):
    h, m, sec, f = map(int, s.split(":"))
    return ((h * 60 + m) * 60 + sec) * tb + f


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


# --- listings ---
ps = Counter()
meta_fe = Counter()
non_ascii = []
iso9660_hint = 0
for disc, listing in discs():
    meta, rows = parse_listing(listing)
    ps[meta.get("partition_start", "?")] += 1
    meta_fe[meta.get("meta_fe", "?")] += 1
    text = listing.read_text(errors="replace")
    if "ISO9660" in text or "ISO 9660" in text or "/VIDEO_TS" in text:
        iso9660_hint += 1
    for k, _, p in rows:
        if any(ord(c) > 127 for c in p):
            non_ascii.append((disc.name, p))
print("A04 partition_start", dict(ps))
print("A02 meta_fe", dict(meta_fe))
print("A03 iso9660_hint", iso9660_hint, "A06 non_ascii_paths", len(non_ascii), non_ascii[:3])
assert list(ps) == ["288"]
assert iso9660_hint == 0
assert not non_ascii

# --- DISCID ---
flg = Counter()
prov_ascii = Counter()
prov_bin = []
disc_id_ff = disc_id_uuid = 0
for p in sorted(CORPUS.rglob("*DISCID.DAT")):
    b = p.read_bytes()
    assert len(b) == 128
    flg[b[60]] += 1
    did = b[12:28]
    if did == b"\xff" * 16:
        disc_id_ff += 1
    else:
        disc_id_uuid += 1
    prov = b[28:44]
    if all(32 <= c < 127 or c == 0 for c in prov) and any(c >= 32 for c in prov):
        prov_ascii[prov.split(b"\x00", 1)[0].decode("ascii")] += 1
    else:
        prov_bin.append((p.parent.name, prov.hex()))
print("A10 SEARCH_FLG", dict(flg), "A12 disc_id FF", disc_id_ff, "other", disc_id_uuid)
print("A11 ascii providers", len(prov_ascii), "binary", len(prov_bin))
print("  binary sample", prov_bin[:5])
assert set(flg) <= {0, 1}

# --- XPL ---
xpl = sorted(CORPUS.glob("*/*VPLST*.XPL"))
assert len(xpl) == 247

sync_as = Counter()
sync_other = Counter()
loading_begin = 0
loading_begin_ex = []
nocache_true = 0
xml_base = 0
tb = Counter()
tick = Counter()
mux = Counter()
mux_par = Counter()
angle = Counter()
angle_omit_on_ilv = 0
seamless_true = 0
seamless_layer = []
dup_audio_track = 0
ff_ge_50 = 0
clip_nz_begin = 0
clip_odd_ff = 0
dur_eq_end = dur_gt_end = dur_lt_end = 0
dur_lt_ex = []
fpt_next = 0
appsync = Counter()
lang_pa = Counter()
http_src = 0

ilv_maps = {
    "death.MAP",
    "ofeliaDeath.MAP",
    "ofeliaEnters.MAP",
    "ofeliaFig.MAP",
}

selector_discs = {
    "MATRIX_REVOLUTIONS": 99,
    "BLADE_RUNNER": 2,
    "TRAINING_DAY": 3,
}

for f in xpl:
    root = ET.parse(f).getroot()
    ts = root.find(f"{NS}TitleSet")
    if ts is not None:
        tb[ts.get("timeBase") or "omit"] += 1
        tick[ts.get("tickBase") or "omit"] += 1
    for el in root.iter():
        tag = el.tag.replace(NS, "")
        if el.get("{http://www.w3.org/XML/1998/namespace}base"):
            xml_base += 1
        src = el.get("src") or ""
        if src.startswith("http"):
            http_src += 1
        if tag == "ApplicationSegment":
            sync_as[el.get("sync") or "omit"] += 1
        elif tag in (
            "SecondaryAudioVideoClip",
            "SubstituteAudioVideoClip",
            "SubstituteAudioClip",
            "AdvancedSubtitleSegment",
        ):
            sync_other[(tag, el.get("sync") or "omit")] += 1
        if el.get("loadingBegin"):
            loading_begin += 1
            if len(loading_begin_ex) < 8:
                loading_begin_ex.append(
                    (f.parent.name, f.name, tag, el.get("src", "")[-40:], el.get("loadingBegin"))
                )
        if (el.get("noCache") or "").lower() == "true":
            nocache_true += 1
        if tag in ("ApplicationResource", "PlaylistApplicationResource"):
            mux[el.get("multiplexed") or "omit"] += 1
            if tag == "PlaylistApplicationResource":
                mux_par[el.get("multiplexed") or "omit"] += 1
        if tag == "PlaylistApplication":
            lang_pa[el.get("language") or "omit"] += 1
        if tag == "Video":
            a = el.get("angleNumber")
            angle[a or "omit"] += 1
        times = []
        for attr in ("titleTimeBegin", "titleTimeEnd", "clipTimeBegin", "titleDuration", "titleTime", "loadingBegin"):
            v = el.get(attr)
            if v:
                times.append(v)
                ff = int(v.split(":")[-1])
                if ff >= 50:
                    ff_ge_50 += 1
        if tag == "PrimaryAudioVideoClip":
            if (el.get("seamless") or "").lower() == "true":
                seamless_true += 1
                srcn = (el.get("src") or "").rsplit("/", 1)[-1]
                if "FEATURE_2" in srcn or "PEVOB_2" in srcn:
                    seamless_layer.append((f.parent.name, f.name, srcn, el.get("seamless")))

    for title in list(root.iter(f"{NS}Title")) + list(root.iter(f"{NS}FirstPlayTitle")):
        dur = title.get("titleDuration")
        clips = list(title.findall(f"{NS}PrimaryAudioVideoClip"))
        if dur and clips:
            ends = [t2f(c.get("titleTimeEnd")) for c in clips if c.get("titleTimeEnd")]
            if ends:
                mx = max(ends)
                d = t2f(dur)
                if d == mx:
                    dur_eq_end += 1
                elif d > mx:
                    dur_gt_end += 1
                else:
                    dur_lt_end += 1
                    dur_lt_ex.append(
                        (f.parent.name, f.name, title.get("id") or title.get("titleNumber"), dur, mx)
                    )
        tracks = defaultdict(list)
        for clip in clips:
            ctb = clip.get("clipTimeBegin") or "00:00:00:00"
            if ctb != "00:00:00:00":
                clip_nz_begin += 1
                if int(ctb.split(":")[-1]) % 2:
                    clip_odd_ff += 1
            srcn = (clip.get("src") or "").rsplit("/", 1)[-1]
            for vid in clip.findall(f"{NS}Video"):
                if srcn in ilv_maps and vid.get("angleNumber") is None:
                    angle_omit_on_ilv += 1
            seen = defaultdict(list)
            for au in clip.findall(f"{NS}Audio"):
                seen[au.get("track") or "1"].append(au.get("streamNumber") or "1")
            for tr, sns in seen.items():
                if len(sns) > 1:
                    dup_audio_track += 1

print("A14 ApplicationSegment@sync", dict(sync_as), "other", dict(sync_other))
print("A15 loadingBegin", loading_begin, "ex", loading_begin_ex)
print("A16 noCache=true", nocache_true, "A25 xml:base", xml_base)
print("A17 timeBase", dict(tb), "tickBase", dict(tick), "FF>=50", ff_ge_50)
print("A19 multiplexed", dict(mux), "PlaylistApplicationResource", dict(mux_par))
print("A18 clipTimeBegin nonzero", clip_nz_begin, "odd FF", clip_odd_ff)
print("A21 dur==lastEnd", dur_eq_end, "dur>end", dur_gt_end, "dur<end", dur_lt_end, "ex", dur_lt_ex)
print("A24 PlaylistApplication language", dict(lang_pa))
print("A27 seamless=true", seamless_true, "on FEATURE_2/PEVOB_2", seamless_layer[:8], "n", len(seamless_layer))
print("A28 dup Audio@track in one clip", dup_audio_track)
print("A29 Video@angleNumber", dict(angle), "omit on Pan maps", angle_omit_on_ilv)
print("http src", http_src)

assert sync_as.get("none", 0) == 0
assert xml_base == 0
assert tb.get("50fps", 0) == 0
assert http_src == 0
# loadingBegin is used (A15). dur<end exists (A21) — do not assert zero.

# selector fallback: lower XPL with PrimaryAudioVideoClip
for disc, high in selector_discs.items():
    files = sorted(CORPUS.glob(f"{disc}/*VPLST*.XPL"))
    has_clip = {}
    for f in files:
        m = re.search(r"VPLST(\d+)", f.name)
        n = int(m.group(1)) if m else -1
        root = ET.parse(f).getroot()
        has_clip[n] = bool(list(root.iter(f"{NS}PrimaryAudioVideoClip")))
    print(f"A97 {disc} highest={high} clips_by_$$$={has_clip}")
    assert has_clip.get(high) is False
    lower = [n for n, c in has_clip.items() if n < high and c]
    assert lower, (disc, has_clip)

# --- JS menuLanguage ---
js_langs = Counter()
jump_calls = []
elapsed_use = 0
for p in CORPUS.rglob("*"):
    if p.suffix.lower() not in {".js", ".JS"} and "script.js" not in p.name.lower():
        continue
    raw = p.read_bytes()
    if raw[:2] == b"\xfe\xff":
        text = raw[2:].decode("utf-16-be", "replace")
    elif raw[:2] == b"\xff\xfe":
        text = raw[2:].decode("utf-16-le", "replace")
    else:
        text = raw.decode("utf-8", "replace")
    for m in re.finditer(r"menuLanguage\s*[=!]=\s*[\"']([^\"']+)[\"']", text):
        js_langs[m.group(1)] += 1
    if ".jump(" in text:
        jump_calls.append(p.name)
    if "elapsedTime" in text:
        elapsed_use += 1
print("A45 menuLanguage compares", dict(js_langs), "jump files", jump_calls, "elapsedTime refs", elapsed_use)

# --- VTI ---
spn = Counter()
astn = Counter()
overrun391 = 0
at193 = []
extra282 = Counter()
vts_ea_vs_vtsi = []
v_atr_comp = Counter()
v_atr_disp = Counter()
v_atr_prog = Counter()
v_atr_lb = Counter()
v_atr_film = Counter()
ast_atr = Counter()
for p in sorted(CORPUS.glob("*/HVDVD_TS__HVA00001.VTI")):
    b = p.read_bytes()
    vts_ea = struct.unpack_from(">I", b, 12)[0]
    vtsi_ea = struct.unpack_from(">I", b, 28)[0]
    if vts_ea != vtsi_ea:
        vts_ea_vs_vtsi.append((p.parent.name, vts_ea, vtsi_ea, len(b) // 2048 - 1))
    for a in parse_atri(b):
        nsp = a[229]
        spn[nsp] += 1
        astn[struct.unpack_from(">H", a, 14)[0]] += 1
        if nsp and 230 + 5 * nsp > 391:
            overrun391 += 1
        if a[193:197] == b"\x01\x1c\x00\xc4":
            at193.append(p.parent.name)
        v = struct.unpack_from(">I", a, 2)[0]
        v_atr_comp[(v >> 30) & 3] += 1
        v_atr_disp[(v >> 24) & 3] += 1
        v_atr_prog[(v >> 20) & 3] += 1
        v_atr_lb[(v >> 18) & 1] += 1
        v_atr_film[(v >> 16) & 1] += 1
        ns_a = struct.unpack_from(">H", a, 14)[0]
        for i in range(ns_a):
            ast_atr[a[16 + 4 * i : 20 + 4 * i].hex()] += 1
    for e in parse_evobi(b):
        extra = struct.unpack_from(">I", e, 282)[0]
        if extra:
            extra282[extra] += 1
print("A47 ATRI@193 discs", sorted(set(at193)), "n", len(at193))
print("A50 SP_Ns", dict(spn), "overrun391", overrun391, "AST_Ns top", astn.most_common(6))
print("A51 VTS_EA!=VTSI_EA", len(vts_ea_vs_vtsi), vts_ea_vs_vtsi[:4])
print("A52 EVOBI+282 unique", extra282.most_common(8), "nvals", len(extra282))
print("V_ATR compression", dict(v_atr_comp), "display", dict(v_atr_disp), "prog", dict(v_atr_prog), "letterbox", dict(v_atr_lb), "film", dict(v_atr_film))
print("AST_ATR unique", len(ast_atr), "top", ast_atr.most_common(12))

# --- MAP SZ>2047 vs interleaved ---
sz_big_ilv = 0
sz_big_cont = 0
for f in CORPUS.rglob("*.MAP"):
    b = f.read_bytes()
    if b[:12] != b"HDDVD_TMAP00":
        continue
    ty = struct.unpack_from(">H", b, 20)[0]
    ns = struct.unpack_from(">H", b, 55)[0]
    for i in range(ns):
        sa, _, nent, _ = struct.unpack_from(">IH2H", b, 384 + 32 * i)
        for j in range(nent):
            w = struct.unpack_from(">I", b, sa + 4 * j)[0]
            if (w & 0x1FFF) > 2047:
                if ty == 0x2202:
                    sz_big_ilv += 1
                else:
                    sz_big_cont += 1
print("A69 SZ>2047 interleaved", sz_big_ilv, "contiguous", sz_big_cont)
assert sz_big_ilv == 0 and sz_big_cont == 108
assert overrun391 == 0
assert loading_begin == 110
assert dur_lt_end == 1
assert angle_omit_on_ilv == 0
assert all(t[1] == 0 for t in vts_ea_vs_vtsi)
print("E14 PASS")
