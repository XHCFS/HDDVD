#!/usr/bin/env python3
"""E12 — implementer-question census closed from saved XPL / listings / ACA.

Claims (spec/clean/14_IMPLEMENTER_ANSWERS.md):
  0 ADV_OBJ without VPLST; 1 disc neither (Standard).
  Playlist file:///dvddisc/ URIs match listing paths exactly (0 case-fold hits).
  Every HVDVD_TS MAP has a sibling EVO of the same basename.
  PrimaryAudioVideoClip ranges: 0 overlaps; abutting pairs exist.
  titleTimeEnd behaves as exclusive (abut would collide if inclusive).
  clipTimeBegin != 00:00:00:00 occurs.
  Aperture 1920x1080 on every playlist; timeBase 60fps on every playlist.
  xml:base unused; MediaAttributeList missing only on the 3 selector XPL.
  PrimaryAudioVideoClip dataSource is Disc or omitted.
  FirstPlayTitle on 119 XPL; onEnd on 3192/3196 Title.
  Selector ACA script.js calls Player.playlist.load with a full file:/// URI.

Falsifier: a clip overlap; a MAP without sibling EVO; a selector.js without load.
"""
import struct
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from lib import CORPUS, discs, parse_listing

NS = "{http://www.dvdforum.org/2005/HDDVDVideo/Playlist}"


def t2f(s, tb=60):
    h, m, sec, f = map(int, s.split(":"))
    return ((h * 60 + m) * 60 + sec) * tb + f


both = adv_no_v = neither = 0
for disc, listing in discs():
    _, rows = parse_listing(listing)
    files = [p for k, _, p in rows if k == "FILE"]
    adv = any(p.startswith("/ADV_OBJ/") for p in files)
    v = any(
        p.startswith("/ADV_OBJ/")
        and p.rsplit("/", 1)[-1].startswith("VPLST")
        and p.upper().endswith(".XPL")
        for p in files
    )
    if adv and v:
        both += 1
    elif adv:
        adv_no_v += 1
    else:
        neither += 1
print(f"Q1 both={both} adv_no_vplst={adv_no_v} neither={neither}")
assert both == 119 and adv_no_v == 0 and neither == 1

listings = {}
for disc, listing in discs():
    _, rows = parse_listing(listing)
    files = {p for k, _, p in rows if k == "FILE"}
    listings[disc.name] = files

nuri = exact_miss = 0
maps = sibling_miss = 0
for disc, listing in discs():
    _, rows = parse_listing(listing)
    files = {p.upper() for k, _, p in rows if k == "FILE"}
    for k, _, p in rows:
        if k != "FILE" or not p.upper().endswith(".MAP") or not p.startswith("/HVDVD_TS/"):
            continue
        maps += 1
        evo = p[:-4] + ".EVO"
        if evo.upper() not in files:
            sibling_miss += 1
print(f"Q4 maps={maps} sibling_miss={sibling_miss}")
assert maps == 2421 and sibling_miss == 0

xpl = sorted(set(CORPUS.glob("*/*VPLST*.XPL")))
assert len(xpl) == 247

abut = overlap = gap = clip_nz = 0
ap = Counter()
tb = Counter()
typ = Counter()
xmlb = mal_missing = 0
ds = Counter()
fp = titles = on_end = 0
forced_true = 0

for f in xpl:
    root = ET.parse(f).getroot()
    typ[root.get("type", "(omit)")] += 1
    if root.get("{http://www.w3.org/XML/1998/namespace}base"):
        xmlb += 1
    cfg = root.find(NS + "Configuration")
    if cfg is not None:
        ape = cfg.find(NS + "Aperture")
        if ape is not None:
            ap[ape.get("size")] += 1
    ts = root.find(NS + "TitleSet")
    if ts is not None:
        tb[ts.get("timeBase")] += 1
        if ts.get("{http://www.w3.org/XML/1998/namespace}base"):
            xmlb += 1
    if root.find(NS + "MediaAttributeList") is None:
        mal_missing += 1
        nclip = len(list(root.iter(NS + "PrimaryAudioVideoClip")))
        assert nclip == 0, (f, nclip)
    if list(root.iter(NS + "FirstPlayTitle")):
        fp += 1
    files = listings[f.parent.name]
    for el in root.iter():
        src = el.get("src") or ""
        if src.startswith("file:///dvddisc/"):
            path = "/" + src[len("file:///dvddisc/") :]
            low = path.lower()
            if ".aca/" in low:
                path = path[: low.index(".aca/") + 4]
            nuri += 1
            if path not in files:
                exact_miss += 1
        tag = el.tag.split("}")[-1]
        if tag == "Title":
            titles += 1
            if el.get("onEnd"):
                on_end += 1
        if tag == "PrimaryAudioVideoClip":
            ds[el.get("dataSource", "(omit)")] += 1
            cb = el.get("clipTimeBegin")
            if cb and cb != "00:00:00:00":
                clip_nz += 1
        if tag == "SubtitleTrack" and el.get("forced") == "true":
            forced_true += 1
    for title in list(root.iter(NS + "Title")) + list(root.iter(NS + "FirstPlayTitle")):
        clips = []
        for c in title.findall(NS + "PrimaryAudioVideoClip"):
            clips.append((t2f(c.get("titleTimeBegin")), t2f(c.get("titleTimeEnd"))))
        clips.sort()
        for i in range(len(clips) - 1):
            e0, b1 = clips[i][1], clips[i + 1][0]
            if e0 == b1:
                abut += 1
            elif e0 > b1:
                overlap += 1
            else:
                gap += 1

print(f"Q2 uris={nuri} exact_miss={exact_miss}")
print(f"Q9 abut={abut} overlap={overlap} gap={gap} clipTimeBegin_nz={clip_nz}")
print(f"aperture={dict(ap)} timeBase={dict(tb)} xml:base={xmlb} MAL_missing={mal_missing}")
print(f"dataSource={dict(ds)} FirstPlayTitle={fp} Title={titles} onEnd={on_end}")
assert exact_miss == 0 and nuri > 10000
assert overlap == 0 and abut > 1000 and gap == 12
assert clip_nz == 133
assert ap.get("1920x1080") == 247 and tb.get("60fps") == 247
assert xmlb == 0 and mal_missing == 3
assert set(ds) <= {"Disc", "(omit)"}
assert fp == 119 and titles == 3196 and on_end == 3192
assert forced_true == 0
assert typ.get("Advanced", 0) + typ.get("(omit)", 0) == 247

# Selector IPlaylist.load URI
loads = []
for disc, name in (
    ("MATRIX_REVOLUTIONS", "ADV_OBJ__selector.aca"),
    ("BLADE_RUNNER", "ADV_OBJ__selector.aca"),
    ("TRAINING_DAY", "ADV_OBJ__selector.aca"),
):
    p = CORPUS / disc / name
    assert p.is_file(), p
    b = p.read_bytes()
    n = int.from_bytes(b[12:14], "big")
    pos = 32
    js = None
    for _ in range(n):
        moff, mlen, _crc, flags = struct.unpack_from(">IIIH", b, pos)
        namelen = flags & 0xFF
        mem = b[pos + 14 : pos + 14 + namelen].decode("ascii")
        if mem == "script.js":
            js = b[moff : moff + mlen].decode("utf-16-be")
        pos += 14 + namelen + 32
    assert js and "Player.playlist.load(" in js, disc
    assert 'Player.playlist.load("file:///dvddisc/ADV_OBJ/VPLST' in js, disc
    loads.append(disc)

print("Q67 load URI in", loads)
print("E12 PASS")
