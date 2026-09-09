#!/usr/bin/env python3
"""E07 — playlist boot facts a player must follow.

Claims:
  0 APLST in this corpus (audio-only playlist path unused).
  Boot playlist = highest VPLST$$$.XPL number under ADV_OBJ (patent FIG.50).
  FirstPlayTitle is common but not universal.
  PrimaryAudioVideoClip@src is .MAP (already e02); ApplicationSegment@src is .ACA/.XMF.

ISO URLs: listing line 1.
"""
import xml.etree.ElementTree as ET
from collections import Counter
from lib import CORPUS, discs, parse_listing

NS = "{http://www.dvdforum.org/2005/HDDVDVideo/Playlist}"
aplst = 0
vplst_files = 0
first_play = 0
no_first_play = 0
on_end = 0
titles = 0
app_src = Counter()
clip_src = Counter()
highest_ok = 0
adv = 0

for disc, listing in discs():
    _, rows = parse_listing(listing)
    files = [p for k, _, p in rows if k == "FILE"]
    vplst_n = []
    for p in files:
        base = p.rsplit("/", 1)[-1]
        if base.startswith("APLST") and base.upper().endswith(".XPL"):
            aplst += 1
        if p.startswith("/ADV_OBJ/") and base.startswith("VPLST") and base.upper().endswith(".XPL"):
            mid = base[5:8]
            if mid.isdigit():
                vplst_n.append(int(mid))
            vplst_files += 1
    if any(p.startswith("/ADV_OBJ/") for p in files):
        adv += 1
        if vplst_n:
            highest_ok += 1

xpl = sorted(set(CORPUS.glob("*/*VPLST*.XPL")))
for f in xpl:
    root = ET.parse(f).getroot()
    fp = list(root.iter(NS + "FirstPlayTitle")) or [
        el for el in root.iter() if el.tag.endswith("FirstPlayTitle")
    ]
    if fp:
        first_play += 1
    else:
        no_first_play += 1
    for el in root.iter():
        tag = el.tag.split("}")[-1]
        if tag == "Title":
            titles += 1
            if el.get("onEnd"):
                on_end += 1
        if tag == "PrimaryAudioVideoClip":
            src = (el.get("src") or "").rsplit(".", 1)[-1].upper()
            clip_src[src] += 1
        if tag == "ApplicationSegment":
            src = (el.get("src") or "").rsplit(".", 1)[-1].upper()
            app_src[src] += 1

print(f"adv_discs={adv} vplst_files={vplst_files} aplst={aplst} discs_with_vplst_number={highest_ok}")
print(f"xpl={len(xpl)} FirstPlayTitle={first_play} none={no_first_play}")
print(f"Title elements={titles} with onEnd={on_end}")
print("PrimaryAudioVideoClip src", dict(clip_src))
print("ApplicationSegment src", dict(app_src))
assert aplst == 0
assert highest_ok == 119
assert first_play + no_first_play == len(xpl)
assert first_play == 119
assert titles == 3196 and on_end == 3192
assert clip_src.get("MAP", 0) == 4847
assert app_src.get("XMF", 0) == 2529
print("E07 PASS")
