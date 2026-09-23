#!/usr/bin/env python3
"""E26 — every playlist (VPLST$$$.XPL) against Playlist.xsd and the playlist rules.

Source: spec/raw/adv_obj/v1.0/Playlist.xsd [5]; the specification text quoted
in US 2007/0091495 [1] (the "Describes ..." attribute definitions).
Input: corpus/*/ADV_OBJ__VPLST*.XPL.

Claims (falsifier in brackets):
  Every playlist validates against the v1.1 Playlist.xsd (lxml), although
    all declare minorVersion="0". Against v1.0, only the 1.1 additions fail
    (outputFrameRate on Title / FirstPlayTitle, a Title with no clips). [invalid]
  titleNumber equals the Title's position in document order (1, 2, ...). [other]
  onEnd, when present, is the id of a Title in the same playlist.   [dangling]
  PauseAt / Event titleTime values increase strictly in document order
    inside a ScheduledControlList.                                 [not increasing]
  Every mediaAttr names an existing item of the matching type
    (Video/SubVideo -> VideoAttributeItem, Audio/SubAudio ->
    AudioAttributeItem, Subtitle -> SubpictureAttributeItem).      [missing index]
  Application Block rules: inside one appBlock value, every
    ApplicationSegment has a language, languages are unique, valid periods
    and autorun agree, and group is absent; language implies appBlock. [violation]
  PlaylistApplication languages are unique in a playlist.           [duplicate]
  Every PrimaryAudioVideoClip src names a .MAP whose .EVO has an EVOBI in
    the VTI; Audio@streamNumber <= that EVOB's AST_Ns and
    Subtitle@streamNumber <= its SP_Ns.                              [out of range]
  seamless="true" clips start exactly where the previous clip ends.  [gap]
  mediaAttr misses are limited to the two known authoring errors
    (DOWNFALL VPLST000 Subtitle 3-18, U2_RATTLE_AND_HUM VPLST000 Subtitle 1). [other]
  Chapter titleTimeBegin values increase in document order.         [other]
Also prints, for every element and attribute, how often it appears and its
most common values: the basis for the "on disc" notes in sheet 03.
"""
import collections
import re
from lxml import etree

from lib import CORPUS

XSD = CORPUS.parent / "spec" / "raw" / "adv_obj" / "v1.1" / "Playlist.xsd"
XSD10 = CORPUS.parent / "spec" / "raw" / "adv_obj" / "v1.0" / "Playlist.xsd"
NS = "{http://www.dvdforum.org/2005/HDDVDVideo/Playlist}"
XML_XSD = b"""<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
  targetNamespace="http://www.w3.org/XML/1998/namespace">
  <xs:attribute name="base" type="xs:anyURI"/>
  <xs:attribute name="lang" type="xs:language"/>
  <xs:attribute name="space" type="xs:NCName"/>
</xs:schema>"""


def load_schema(path):
    """The DVD Forum schemas import xml.xsd from w3.org; point them at a local copy."""
    import tempfile
    local = tempfile.NamedTemporaryFile(suffix=".xsd", delete=False)
    local.write(XML_XSD)
    local.close()
    tree = etree.parse(str(path))
    for imp in tree.getroot().iter("{http://www.w3.org/2001/XMLSchema}import"):
        if imp.get("namespace") == "http://www.w3.org/XML/1998/namespace":
            imp.set("schemaLocation", local.name)
    return etree.XMLSchema(tree)


schema = load_schema(XSD)
schema10 = load_schema(XSD10)
be = lambda b: int.from_bytes(b, "big")


def evob_streams(disc):
    """EVO filename -> (AST_Ns, SP_Ns) from the disc's VTI (sheet 06)."""
    v = disc / "HVDVD_TS__HVA00001.VTI"
    if not v.exists():
        return {}
    b = v.read_bytes()
    at, et = be(b[184:188]) * 2048, be(b[188:192]) * 2048
    out = {}
    for i in range(be(b[et + 2:et + 4])):
        e = b[et + be(b[et + 8 + 4 * i:et + 12 + 4 * i]):][:320]
        n = be(e[264:266])
        a = b[at + be(b[at + 8 + 4 * (n - 1):at + 12 + 4 * (n - 1)]):][:1024]
        out[e[2:38].rstrip(b"\0 ").decode().upper()] = (be(a[14:16]), a[229])
    return out

def frames(t, rate=60):
    h, m, s, f = map(int, t.split(":"))
    return (3600 * h + 60 * m + s) * rate + f

files = sorted(CORPUS.glob("*/ADV_OBJ__VPLST*.XPL"))
el_count = collections.Counter()
attr_count = collections.Counter()
values = collections.defaultdict(collections.Counter)
fails = collections.Counter()
invalid = []
checks = collections.Counter()

for p in files:
    doc = etree.parse(str(p))
    if not schema.validate(doc):
        invalid.append((p.parent.name, p.name, str(schema.error_log.last_error)[:160]))
    if not schema10.validate(doc):
        for err in schema10.error_log:
            m = err.message
            ok = "outputFrameRate" in m or ("ChapterList" in m and "not expected" in m)
            checks["v1.0-only failures explained by 1.1" if ok else "UNEXPLAINED v1.0 failure"] += 1
            if not ok:
                fails["v1.0 failure not a 1.1 addition"] += 1
    root = doc.getroot()
    for e in root.iter():
        if not isinstance(e.tag, str):
            continue
        name = e.tag.replace(NS, "")
        el_count[name] += 1
        for k, v in e.attrib.items():
            k = k.split("}")[-1]
            attr_count[(name, k)] += 1
            values[(name, k)][v if len(v) < 40 else v[:37] + "..."] += 1

    titles = root.findall(f"{NS}TitleSet/{NS}Title")
    ids = {t.get("id") for t in titles if t.get("id")}
    for i, t in enumerate(titles, 1):
        checks["titleNumber"] += 1
        if int(t.get("titleNumber")) != i:
            fails["titleNumber != document order"] += 1
        if t.get("onEnd") is not None:
            checks["onEnd"] += 1
            if t.get("onEnd") not in ids:
                fails["onEnd dangling"] += 1
        for scl in t.findall(f"{NS}ScheduledControlList"):
            ts = [frames(x.get("titleTime")) for x in scl if isinstance(x.tag, str)]
            checks["ScheduledControlList"] += 1
            if any(b <= a for a, b in zip(ts, ts[1:])):
                fails["ScheduledControlList not strictly increasing"] += 1
        chs = [frames(c.get("titleTimeBegin")) for c in t.iter(f"{NS}Chapter")]
        if chs:
            checks["ChapterList"] += 1
            if any(b < a for a, b in zip(chs, chs[1:])):
                fails["Chapter times decrease"] += 1
        blocks = collections.defaultdict(list)
        for seg in t.findall(f"{NS}ApplicationSegment"):
            checks["ApplicationSegment"] += 1
            if seg.get("language") and not seg.get("appBlock"):
                fails["language without appBlock"] += 1
            if seg.get("appBlock"):
                blocks[seg.get("appBlock")].append(seg)
        for b, segs in blocks.items():
            checks["Application Block"] += 1
            langs = [s.get("language") for s in segs]
            if None in langs or len(set(langs)) != len(langs):
                fails["block language missing or repeated"] += 1
            if len({(s.get("titleTimeBegin"), s.get("titleTimeEnd")) for s in segs}) > 1:
                fails["block valid periods differ"] += 1
            if len({s.get("autorun", "true") for s in segs}) > 1:
                fails["block autorun differs"] += 1
            if any(s.get("group") for s in segs):
                fails["block member has group"] += 1

    mal = root.find(f"{NS}MediaAttributeList")
    idx = collections.defaultdict(set)
    if mal is not None:
        for it in mal:
            idx[it.tag.replace(NS, "")].add(int(it.get("index"))) if isinstance(it.tag, str) else None
    target = {"Video": "VideoAttributeItem", "SubVideo": "VideoAttributeItem",
              "Audio": "AudioAttributeItem", "SubAudio": "AudioAttributeItem",
              "Subtitle": "SubpictureAttributeItem"}
    for tag, item in target.items():
        for e in root.iter(NS + tag):
            checks["mediaAttr"] += 1
            if int(e.get("mediaAttr", "1")) not in idx[item]:
                known = tag == "Subtitle" and (p.parent.name, p.name) in {
                    ("DOWNFALL", "ADV_OBJ__VPLST000.XPL"), ("U2_RATTLE_AND_HUM", "ADV_OBJ__VPLST000.XPL")}
                checks["mediaAttr misses (known authoring errors)" if known else "x"] += 1
                if not known:
                    fails[f"mediaAttr of {tag} not in {item}"] += 1

    streams = evob_streams(p.parent)
    for clip in root.iter(NS + "PrimaryAudioVideoClip"):
        m = re.search(r"/([^/]+)\.MAP$", clip.get("src"), re.I)
        key = m.group(1).upper() + ".EVO" if m else None
        if key not in streams:
            fails["clip MAP has no EVOBI"] += 1
            continue
        ast, sp = streams[key]
        checks["clip resolved to EVOBI"] += 1
        for a in clip.findall(NS + "Audio"):
            if int(a.get("streamNumber", "1")) > ast:
                fails["Audio streamNumber > AST_Ns"] += 1
        for sub in clip.findall(NS + "Subtitle"):
            if int(sub.get("streamNumber", "1")) > sp:
                fails["Subtitle streamNumber > SP_Ns"] += 1
    for t in root.iter(NS + "Title", NS + "FirstPlayTitle"):
        prev = None
        for k in t.findall(NS + "PrimaryAudioVideoClip"):
            if k.get("seamless") == "true":
                checks["seamless clip"] += 1
                if prev is None or prev.get("titleTimeEnd") != k.get("titleTimeBegin"):
                    fails["seamless clip does not abut"] += 1
            prev = k

    langs = [a.get("language") for a in root.iter(NS + "PlaylistApplication")]
    checks["PlaylistApplication set"] += 1
    if len(set(langs)) != len(langs):
        fails["PlaylistApplication language repeated"] += 1

print(f"playlists={len(files)} invalid(v1.1)={len(invalid)}")
for x in invalid[:10]:
    print("  INVALID", x)
print("checks", dict(checks))
print("fails", dict(fails))
assert not invalid and not fails, (invalid[:3], fails)
print("E26 PASS")
print("\n# element counts")
for k, v in sorted(el_count.items()):
    print(f"{k:30s} {v}")
print("\n# attribute counts and top values")
for (e, a), n in sorted(attr_count.items()):
    top = values[(e, a)].most_common(6)
    print(f"{e + '@' + a:44s} {n:6d}  distinct {len(values[(e, a)]):5d}  {top}")
