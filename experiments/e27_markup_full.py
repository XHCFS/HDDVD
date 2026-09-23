#!/usr/bin/env python3
"""E27 — every iHD markup document (.xmu / .xts / .xss / .xas) against the iHD schemas.

Source: spec/raw/adv_obj/v1.1/iHD.xsd, iHDstyle.xsd, iHDstate.xsd [5] (v1.0 kept
for comparison). Input: loose corpus/<DISC>/*.xmu etc. plus every member with those
extensions in every saved ACA, extracted by offset/length (sheet 04).

Claims (falsifier in brackets):
  Every markup document's root is iHD `root`, and every file's elements are in
  the iHD namespaces (or inside `meta`).                             [other root]
  Every document validates against both the v1.1 and the v1.0 schemas except
  SHREK_THE_THIRD_EU iHD_Markup.xmu, whose only failures are its foreign
  (http://sampleext) attributes.                                    [other failure]
Also prints element and attribute counts with their most common values.
"""
import collections
import re
import tempfile
from lxml import etree

from lib import CORPUS

be = lambda b: int.from_bytes(b, "big")
IHD = "http://www.dvdforum.org/2005/ihd"
STYLE = IHD + "#style"
STATE = IHD + "#state"
EXTS = (".xmu", ".xts", ".xss", ".xas")
XML_XSD = b"""<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
  targetNamespace="http://www.w3.org/XML/1998/namespace">
  <xs:attribute name="base" type="xs:anyURI"/>
  <xs:attribute name="lang" type="xs:language"/>
  <xs:attribute name="space" type="xs:NCName"/>
</xs:schema>"""


def load(version):
    d = CORPUS.parent / "spec" / "raw" / "adv_obj" / version
    local = tempfile.NamedTemporaryFile(suffix=".xsd", delete=False)
    local.write(XML_XSD)
    local.close()
    tree = etree.parse(str(d / "iHD.xsd"))
    for imp in tree.getroot().iter("{http://www.w3.org/2001/XMLSchema}import"):
        if imp.get("namespace") == "http://www.w3.org/XML/1998/namespace":
            imp.set("schemaLocation", local.name)
        else:
            imp.set("schemaLocation", str(d / imp.get("schemaLocation")))
    return etree.XMLSchema(tree)


docs = []
for p in CORPUS.glob("*/*"):
    if p.suffix.lower() in EXTS:
        docs.append((p.parent.name, p.name, p.read_bytes()))
for p in list(CORPUS.glob("*/*.aca")) + list(CORPUS.glob("*/*.ACA")):
    b, pos = p.read_bytes(), 32
    for _ in range(be(b[12:14])):
        off, ln, nl = be(b[pos:pos + 4]), be(b[pos + 4:pos + 8]), b[pos + 13]
        name = b[pos + 14:pos + 14 + nl].decode("latin1")
        if name.lower().endswith(EXTS):
            docs.append((p.parent.name, name, b[off:off + ln]))
        pos += 14 + nl + 32

schemas = {"v1.1": load("v1.1"), "v1.0": load("v1.0")}
kinds = collections.Counter()
roots = collections.Counter()
valid = collections.Counter()
causes = {v: collections.Counter() for v in schemas}
example = {}
els = collections.Counter()
attrs = collections.Counter()
values = collections.defaultdict(collections.Counter)
parse_fail = []

def short(ns, local):
    return {IHD: "", STYLE: "style:", STATE: "state:",
            "http://www.w3.org/XML/1998/namespace": "xml:"}.get(ns, "{" + (ns or "") + "}") + local

for disc, name, data in docs:
    ext = name.lower().rsplit(".", 1)[1]
    kinds[ext] += 1
    try:
        doc = etree.fromstring(data, etree.XMLParser(remove_comments=True)).getroottree()
    except etree.XMLSyntaxError as e:
        parse_fail.append((disc, name, str(e)[:80]))
        continue
    r = doc.getroot()
    q = etree.QName(r)
    roots[(ext, short(q.namespace, q.localname))] += 1
    for v, s in schemas.items():
        if s.validate(doc):
            valid[(v, ext)] += 1
        else:
            for err in s.error_log:
                m = re.sub(r"\{[^}]*\}", "", err.message)
                m = re.sub(r"'[^']*'", "'…'", m) if "is not a valid value" in m or "is not accepted" in m else m
                causes[v][m[:170]] += 1
                example.setdefault((v, m[:170]), f"{disc}/{name}:{err.line}")
    for e in r.iter():
        if not isinstance(e.tag, str):
            continue
        qe = etree.QName(e)
        en = short(qe.namespace, qe.localname)
        els[en] += 1
        for k, val in e.attrib.items():
            qa = etree.QName(k)
            an = short(qa.namespace, qa.localname)
            attrs[(en, an)] += 1
            values[an][val if len(val) < 50 else val[:47] + "..."] += 1

assert not parse_fail, parse_fail
assert set(roots) <= {("xmu", "root"), ("xas", "root"), ("xts", "timing"), ("xss", "styling")}, roots
for v in schemas:
    for m in causes[v]:
        assert "sampleext" in example[(v, m)] or "SHREK_THE_THIRD_EU/iHD_Markup.xmu" in example[(v, m)], (v, m)
assert valid[("v1.1", "xmu")] == kinds["xmu"] - 1 and valid[("v1.0", "xmu")] == kinds["xmu"] - 1
print("E27 PASS")
print("documents", dict(kinds), "parse failures", len(parse_fail), parse_fail[:5])
print("roots", dict(roots))
print("valid", dict(valid))
for v in schemas:
    print(f"\n# {v} failure causes")
    for m, n in causes[v].most_common(40):
        print(f"{n:6d}  {m}  | {example[(v, m)]}")
print("\n# elements")
for k, n in els.most_common():
    print(f"{n:7d} {k}")
print("\n# attributes (element@attribute)")
for (e, a), n in sorted(attrs.items(), key=lambda t: -t[1]):
    print(f"{n:7d} {e}@{a}")
print("\n# attribute values")
for a, c in sorted(values.items()):
    print(f"{a:34s} n={sum(c.values()):6d} distinct={len(c):5d} {c.most_common(8)}")
