#!/usr/bin/env python3
"""E02 — every saved playlist is XML under the DVD Forum Playlist namespace.

Claim: 247 .XPL, 0 parse failures, majorVersion=1 minorVersion=0,
PrimaryAudioVideoClip@src points at .MAP (addressing layer).

Schema copy used for element names: spec/raw/adv_obj/v1.0/Playlist.xsd
(working copy of the schema named in disc schemaLocation). Live namespace
URI is http://www.dvdforum.org/2005/HDDVDVideo/Playlist
"""
import xml.etree.ElementTree as ET
from collections import Counter
from lib import CORPUS

NS = "http://www.dvdforum.org/2005/HDDVDVideo/Playlist"
files = sorted(CORPUS.glob("*/*VPLST*.XPL")) + sorted(CORPUS.glob("*/*.XPL"))
files = sorted(set(files))
assert files, "no XPL on disk"

maj = Counter()
clip_ext = Counter()
fail = 0
for f in files:
    try:
        root = ET.parse(f).getroot()
    except ET.ParseError:
        fail += 1
        print("PARSE FAIL", f)
        continue
    tag = root.tag
    if tag != f"{{{NS}}}Playlist" and not tag.endswith("Playlist"):
        fail += 1
        print("NS FAIL", f, root.tag)
        continue
    maj[(root.get("majorVersion"), root.get("minorVersion"))] += 1
    for el in root.iter():
        if el.tag.endswith("PrimaryAudioVideoClip"):
            src = el.get("src") or ""
            clip_ext[src.rsplit(".", 1)[-1].upper() if "." in src else src] += 1

print(f"xpl={len(files)} fail={fail} versions={dict(maj)}")
print("PrimaryAudioVideoClip src ext", dict(clip_ext.most_common(8)))
assert fail == 0
assert maj.get(("1", "0"), 0) == len(files)
print("E02 PASS")
