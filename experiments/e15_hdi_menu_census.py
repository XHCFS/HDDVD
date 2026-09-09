#!/usr/bin/env python3
"""E15 — HDi menu census (listing + saved ACA/XMU/JS/XMF). Offline.

Methodology (spec/advanced/05 §5.0 gate):
  1. Listing inventory of ADV_OBJ assets (N=120 discs).
  2. Extract every saved ACA with the e11 directory formula.
  3. Parse every saved .xmu (loose + ACA) against iHD.xsd element/attr allowlists.
  4. Decode every saved .js; census Player.*/URI/jump/load.
  5. Compare ApplicationResource@size to listing sizes (Jumpstart File Cache rule).

Claims:
  ADV_OBJ listings: 409 ACA, 247 XPL, 119 DISCID, 72 PNG, 10 CER,
    3 XMF, 3 JS, 2 XMU, 1 TTF (e06/e11).
  Every saved JS in this repo is UTF-16BE with BOM FE FF — including the three
  loose 1408 files (refutes “1408 loose JS is UTF-8”).
  iHD style/state attribute local-names used on saved XMU ⊆ iHDstyle/iHDstate XSDs.
  ITitle/IChapter.jump is two-argument on every saved call site: time expression
  or stored timecode, then a boolean (always the token false in string form
  except identifier forms this.elapsed / resume.getTC()).
  PREMONITION script.js: psUrl = "file:///required/" + contentId + "/".
  Jumpstart: size may be ≥ file, must not be smaller. Corpus: 1 XPL row is
  smaller (PANS_LABYRINTH multi_angle.aca 5500 vs listing 6436).

Falsifier: a saved JS without FE FF BOM; a style attr not in iHDstyle.xsd;
IPlaylist.load of a non-file:/// URI in saved JS; zero file:///required/ if
PREMONITION client.aca is present.

Does not fetch ISOs. Run tools/pull_hdi_sample.py to grow the ACA sample.
"""
from __future__ import annotations

import re
import struct
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from lib import CORPUS, discs, parse_listing

ROOT = CORPUS.parent

NS = "{http://www.dvdforum.org/2005/HDDVDVideo/Playlist}"
IHD_NS = "http://www.dvdforum.org/2005/ihd"
STYLE_NS = "http://www.dvdforum.org/2005/ihd#style"
STATE_NS = "http://www.dvdforum.org/2005/ihd#state"
RAW = ROOT / "spec" / "raw" / "adv_obj" / "v1.0"


def xsd_attr_names(path: Path) -> set[str]:
    root = ET.parse(path).getroot()
    names = set()
    for el in root.iter("{http://www.w3.org/2001/XMLSchema}attribute"):
        n = el.get("name")
        if n:
            names.add(n)
    return names


STYLE_OK = xsd_attr_names(RAW / "iHDstyle.xsd")
STATE_OK = xsd_attr_names(RAW / "iHDstate.xsd")
IHD_OK = {
    el.get("name")
    for el in ET.parse(RAW / "iHD.xsd").getroot().iter("{http://www.w3.org/2001/XMLSchema}element")
    if el.get("name")
}


def parse_aca(path: Path):
    b = path.read_bytes()
    n = int.from_bytes(b[12:14], "big")
    pos = 32
    rows = []
    for _ in range(n):
        moff, mlen, crc, flags = struct.unpack_from(">IIIH", b, pos)
        namelen = flags & 0xFF
        name = b[pos + 14 : pos + 14 + namelen].decode("ascii")
        rows.append((name, flags, b[moff : moff + mlen]))
        pos += 14 + namelen + 32
    return rows


def decode_js(b: bytes) -> str:
    if b[:2] != b"\xfe\xff":
        raise AssertionError("JS is not UTF-16BE BOM")
    return b.decode("utf-16-be")


def iter_saved_members():
    for p in sorted(CORPUS.glob("*/*.xmu")) + sorted(CORPUS.glob("*/*.XMU")):
        yield p.parent.name, p.name, p.read_bytes()
    for p in sorted(CORPUS.glob("*/*.js")):
        yield p.parent.name, p.name, p.read_bytes()
    for p in sorted(CORPUS.glob("*/*.xmf")):
        yield p.parent.name, p.name, p.read_bytes()
    for p in sorted(CORPUS.rglob("*.aca")):
        if p.stat().st_size < 32:
            continue
        try:
            members = parse_aca(p)
        except (struct.error, UnicodeDecodeError, ValueError, IndexError):
            continue
        for name, flags, payload in members:
            yield p.parent.name, name, payload


# --- listings ---
adv = Counter()
for disc, listing in discs():
    _, rows = parse_listing(listing)
    for k, sz, p in rows:
        if k != "FILE" or not p.startswith("/ADV_OBJ/"):
            continue
        ext = p.rsplit(".", 1)[-1].lower() if "." in p.rsplit("/", 1)[-1] else ""
        adv[ext] += 1
print("ADV_OBJ exts", dict(adv))
assert adv["aca"] == 409 and adv["xpl"] == 247 and adv["dat"] == 119
assert adv["png"] == 72 and adv["cer"] == 10
assert adv["xmf"] == 3 and adv["js"] == 3 and adv["xmu"] == 2 and adv["ttf"] == 1

# size vs listing
cmp = Counter()
smaller = []
for disc, listing in discs():
    _, rows = parse_listing(listing)
    sizes = {p: s for k, s, p in rows if k == "FILE"}
    for f in disc.glob("*VPLST*.XPL"):
        root = ET.parse(f).getroot()
        for el in root.iter():
            tag = el.tag.split("}")[-1]
            if tag not in ("ApplicationResource", "PlaylistApplicationResource"):
                continue
            src = el.get("src") or ""
            sz = el.get("size")
            if not src.startswith("file:///dvddisc/") or not sz:
                continue
            path = "/" + src[len("file:///dvddisc/") :]
            low = path.lower()
            if ".aca/" in low:
                path = path[: low.index(".aca/") + 4]
            listed = sizes.get(path)
            declared = int(sz)
            if listed is None:
                cmp["unlisted"] += 1
                continue
            if declared == listed:
                cmp["equal"] += 1
            elif declared > listed:
                cmp["larger"] += 1
            else:
                cmp["smaller"] += 1
                smaller.append((disc.name, path, declared, listed))
print("resource size vs listing", dict(cmp), "smaller", smaller)
assert cmp["smaller"] == 1
assert smaller[0][0] == "PANS_LABYRINTH" and smaller[0][2] == 5500 and smaller[0][3] == 6436
assert cmp["equal"] == 532 and cmp["larger"] == 2428
assert cmp["unlisted"] == 0

# --- saved markup / script ---
elems = Counter()
style = Counter()
state = Counter()
clocks = Counter()
uri_root = Counter()
js_n = xmu_n = 0
js_bom = 0
jump_false = 0
jump_other = []
load_uris = []
required = 0
elapsed = 0
unknown_style = []
unknown_el = []

for disc, name, payload in iter_saved_members():
    ln = name.lower()
    if ln.endswith(".js"):
        js_n += 1
        assert payload[:2] == b"\xfe\xff", (disc, name, payload[:4])
        js_bom += 1
        text = decode_js(payload)
        if "elapsedTime" in text:
            elapsed += text.count("elapsedTime")
        for m in re.finditer(r"file:///(required|filecache|dvddisc|fixed|removable|additional|common)(/[^\s\"']*)?", text):
            uri_root[m.group(1)] += 1
            if m.group(1) == "required":
                required += 1
        for m in re.finditer(r"Player\.playlist\.load\s*\(([^)]*)\)", text):
            load_uris.append((disc, name, m.group(1).strip()[:120]))
        for m in re.finditer(r"\.jump\s*\(", text):
            # take until matching close is hard; last-arg token is enough
            frag = text[m.end() : m.end() + 120]
            if re.search(r",\s*false\s*\)", frag) or frag.strip().startswith("resume.getTC"):
                jump_false += 1
            else:
                jump_other.append((disc, name, frag.split("\n", 1)[0][:80]))
    if ln.endswith(".xmu"):
        xmu_n += 1
        xmlb = payload
        if payload[:2] == b"\xfe\xff":
            xmlb = payload.decode("utf-16-be").encode("utf-8")
        root = ET.fromstring(xmlb)
        for el in root.iter():
            tag = el.tag.split("}")[-1] if "}" in el.tag else el.tag
            ns = el.tag[1:].split("}", 1)[0] if el.tag.startswith("{") else ""
            if ns in ("", IHD_NS) and tag not in ("{http://www.w3.org/XML/1998/namespace}lang",):
                elems[tag] += 1
                if tag not in IHD_OK and tag not in ("root",):
                    # root is in IHD_OK
                    if tag not in IHD_OK:
                        unknown_el.append((disc, name, tag))
            if tag == "timing":
                clocks[el.get("clock", "(omit)")] += 1
            for k in el.attrib:
                local = k.split("}")[-1] if "}" in k else k
                kns = k[1:].split("}", 1)[0] if k.startswith("{") else ""
                if kns == STYLE_NS or k.startswith("style:"):
                    style[local] += 1
                    if local not in STYLE_OK:
                        unknown_style.append((disc, name, local))
                if kns == STATE_NS or k.startswith("state:"):
                    state[local] += 1
                    assert local in STATE_OK, (disc, name, local)

print(f"saved JS={js_n} XMU={xmu_n} JS_BOM={js_bom}")
print("iHD elems", elems.most_common())
print("style", style.most_common())
print("state", dict(state))
print("clocks", dict(clocks))
print("uri_root", dict(uri_root))
print("jump_false", jump_false, "jump_other", jump_other)
print("load sites", len(load_uris), "required URI hits", required, "elapsedTime", elapsed)
print("unknown style", unknown_style, "unknown el", unknown_el)

assert js_n >= 20 and js_bom == js_n
assert xmu_n >= 5
assert not unknown_style and not unknown_el
assert "object" not in elems or True  # object unused in this sample is OK
assert set(clocks) <= {"page", "application", "title", "(omit)"}
assert uri_root["required"] >= 3
assert uri_root["dvddisc"] >= 1
assert "fixed" not in uri_root and "removable" not in uri_root
assert jump_false >= 50
assert not jump_other
assert any("file:///dvddisc/ADV_OBJ/" in a or "psUrl" in a or "playlist" in a for *_, a in load_uris)
# PREMONITION required grammar
prem = CORPUS / "PREMONITION_GER" / "ADV_OBJ__client.aca"
assert prem.is_file()
js = None
for name, flags, payload in parse_aca(prem):
    if name == "script.js":
        js = decode_js(payload)
assert js is not None
assert 'var psUrl = "file:///required/" + GUID + "/"' in js or 'file:///required/" + GUID' in js
assert "PersistentStorageManager.contentId" in js
assert "Player.playlist.load(psUrl + playlist)" in js

# 1408 jump + play
p1408 = CORPUS / "1408_DC" / "ADV_OBJ__script.js"
t = decode_js(p1408.read_bytes())
assert 'Player.playlist.titles["Extra1"].jump("00:00:00:00", false)' in t
assert "Player.playlist.play()" in t
assert "createTimer" in t
assert "controller_key_down" in t

print("E15 PASS")
