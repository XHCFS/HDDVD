#!/usr/bin/env python3
"""E24 — every Manifest (.xmf) in the corpus against Manifest.xsd.

Source: spec/raw/adv_obj/v1.0/Manifest.xsd (Spec. 6.2.4.2).
Input: loose corpus/<DISC>/*.xmf plus every .xmf member of every saved ACA,
extracted by offset/length (sheet 04).

Claims (falsifier in brackets):
  Root is Application in the Manifest namespace; children in XSD order
    Region, Script*, Markup?, Resource+.                          [any other]
  Region is 0,0,1920,1080 on every manifest.                      [other value]
  Attributes seen are only those the XSD declares, plus
    xsi:schemaLocation on the root. xml:base never appears.       [other attribute]
  Resource never carries @id; Script/Markup/Application sometimes do.
  src is file:///dvddisc/... or a bare relative name. A relative src only
    appears in a manifest stored inside an ACA, and names a member of that
    same ACA: it resolves against the manifest's own location.   [else]
  Encoding is UTF-8; some files start with a UTF-8 BOM.           [other encoding]
  Every Script / Markup src is loadable through the Resource list: listed
    as a Resource itself, inside a listed .aca (x.aca/member), or a relative
    name inside the manifest's own ACA.                             [uncovered src]
  Specification [1]: every Resource src is one of the playlist's resource
    URIs (ApplicationResource / TitleResource / PlaylistApplicationResource
    src on the same disc). Holds for all but 8, all known: the selector
    manifests of BLADE_RUNNER and TRAINING_DAY (selector/script.js) and
    SHREK_THE_THIRD_EU iHD_Manifest.xmf (6 archives no saved playlist lists). [other]
"""
import re
import xml.etree.ElementTree as ET
from collections import Counter

from lib import CORPUS

be = lambda b: int.from_bytes(b, "big")
NS = "{http://www.dvdforum.org/2005/HDDVDVideo/Manifest}"
XSI = "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation"
ALLOWED = {"Application": {"id", XSI}, "Region": {"x", "y", "width", "height"},
           "Script": {"id", "src"}, "Markup": {"id", "src"}, "Resource": {"id", "src"}}

docs = [(p.parent.name, p.name, p.read_bytes(), None) for p in CORPUS.glob("*/*.xmf")]
for p in list(CORPUS.glob("*/*.aca")) + list(CORPUS.glob("*/*.ACA")):
    b, pos, found, names = p.read_bytes(), 32, [], set()
    for _ in range(be(b[12:14])):
        off, ln, nl = be(b[pos:pos + 4]), be(b[pos + 4:pos + 8]), b[pos + 13]
        name = b[pos + 14:pos + 14 + nl].decode("latin1")
        names.add(name)
        if name.lower().endswith(".xmf"):
            found.append((p.parent.name, name, b[off:off + ln]))
        pos += 14 + nl + 32
    docs += [(*f, names) for f in found]

c = Counter()
for disc, name, d, aca in docs:
    assert d.startswith(b"<?xml") or d.startswith(b"\xef\xbb\xbf<?xml"), (disc, name)
    c["BOM"] += d.startswith(b"\xef\xbb\xbf")
    assert re.search(rb'encoding="utf-8"', d[:120], re.I), (disc, name)
    r = ET.fromstring(d)
    assert r.tag == NS + "Application", (disc, name, r.tag)
    kids = "".join({"Region": "G", "Script": "S", "Markup": "M", "Resource": "R"}[x.tag[len(NS):]] for x in r)
    assert re.fullmatch("GS*M?R+", kids), (disc, name, kids)
    c["with Markup"] += "M" in kids
    c["max Script"] = max(c["max Script"], kids.count("S"))
    for x in [r, *r]:
        t = x.tag[len(NS):]
        assert set(x.attrib) <= ALLOWED[t], (disc, name, t, x.attrib)
        for k in x.attrib:
            c[f"{t}@{k.split('}')[-1]}"] += 1
        if t == "Region":
            assert [x.get(k) for k in ("x", "y", "width", "height")] == ["0", "0", "1920", "1080"], (disc, name)
        if "src" in x.attrib:
            u = x.get("src")
            rel = "://" not in u
            assert rel or u.startswith("file:///dvddisc/"), (disc, name, u)
            assert not rel or (aca is not None and u in aca), (disc, name, u)
            c["relative src"] += rel
    assert "Resource@id" not in c, (disc, name)
    res = {x.get("src") for x in r if x.tag == NS + "Resource"}
    for x in r:
        if x.tag in (NS + "Script", NS + "Markup"):
            u = x.get("src")
            k = u.lower().find(".aca/")
            assert u in res or (k >= 0 and u[:k + 4] in res) or ("://" not in u and aca is not None), (disc, name, u)
            c["script/markup covered by Resource"] += 1

from lxml import etree
PNS = "{http://www.dvdforum.org/2005/HDDVDVideo/Playlist}"
pres = {}
for pl in CORPUS.glob("*/ADV_OBJ__VPLST*.XPL"):
    r = etree.parse(str(pl)).getroot()
    for t in ("ApplicationResource", "TitleResource", "PlaylistApplicationResource"):
        pres.setdefault(pl.parent.name, set()).update(e.get("src") for e in r.iter(PNS + t))
KNOWN = {("BLADE_RUNNER", "file:///dvddisc/ADV_OBJ/selector/script.js"),
         ("TRAINING_DAY", "file:///dvddisc/ADV_OBJ/selector/script.js")}
for disc, name, d, aca in docs:
    for x in ET.fromstring(d):
        if x.tag != NS + "Resource":
            continue
        u = x.get("src")
        if u in pres.get(disc, ()):
            c["Resource is a playlist resource"] += 1
        else:
            assert (disc, u) in KNOWN or (disc == "SHREK_THE_THIRD_EU" and name == "iHD_Manifest.xmf"), (disc, name, u)
            c["Resource not in any saved playlist (known)"] += 1
print(f"manifests={len(docs)} discs={len({d for d, *_ in docs})}")
print(dict(sorted(c.items())))
print("E24 PASS")
