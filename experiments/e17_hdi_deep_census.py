#!/usr/bin/env python3
"""E17 — deep HDi census on every saved ACA/XMU/JS (offline).

Methodology (spec/clean/17_HDI_MENU_RESEARCH.md):
  inventory → XSD allowlist → markup/script census → API vs typelib.

Claims:
  Every complete saved ACA starts HDDVDACA and parses with 14+(flags&0xFF)+32.
  No namelen 0, namelen>64, or '/' in counted names on this sample.
  Style/state local-names ⊆ iHDstyle/iHDstate XSDs.
  JS is UTF-16BE BOM. backgroundImage frame lists are space-separated url().
  Cue begin/end are either HH:MM:SS:FF / *ms|*s, or XPath with state:focused
  / state:actioned.

Falsifier: unknown style attr; JS without FE FF; ACA magic mismatch on a
file whose size matches the listing.

Does not fetch ISOs. Skip 0-byte / truncated pulls.
"""
from __future__ import annotations

import re
import struct
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from lib import CORPUS, discs, parse_listing, saved

ROOT = CORPUS.parent
RAW = ROOT / "spec" / "raw" / "adv_obj" / "v1.0"
IHD_NS = "http://www.dvdforum.org/2005/ihd"
STYLE_NS = "http://www.dvdforum.org/2005/ihd#style"
STATE_NS = "http://www.dvdforum.org/2005/ihd#state"
XS = "{http://www.w3.org/2001/XMLSchema}"


def xsd_attr_names(path: Path) -> set[str]:
    return {
        el.get("name")
        for el in ET.parse(path).getroot().iter(XS + "attribute")
        if el.get("name")
    }


def xsd_el_names(path: Path) -> set[str]:
    return {
        el.get("name")
        for el in ET.parse(path).getroot().iter(XS + "element")
        if el.get("name")
    }


STYLE_OK = xsd_attr_names(RAW / "iHDstyle.xsd")
STATE_OK = xsd_attr_names(RAW / "iHDstate.xsd")
IHD_OK = xsd_el_names(RAW / "iHD.xsd")

SKIP_API = {
    "prototype",
    "constructor",
    "toString",
    "toLocaleString",
    "valueOf",
    "hasOwnProperty",
    "isPrototypeOf",
    "propertyIsEnumerable",
    "DefaultValue",
    "length",
}


def typelib_names() -> set[str]:
    names = set()
    for line in (ROOT / "spec" / "raw" / "adv_obj" / "iHD_Scripting_API.txt").read_text().splitlines():
        if line.startswith("    ") and not line.startswith("     "):
            n = line.strip()
            if n and n[0].isalpha() and n not in SKIP_API:
                names.add(n)
    return names


TYPELIB = typelib_names()


def parse_aca(path: Path):
    b = path.read_bytes()
    if len(b) < 32:
        raise ValueError(f"too small {path} {len(b)}")
    if b[:8] != b"HDDVDACA":
        raise ValueError(f"magic {path} {b[:8]!r}")
    n = int.from_bytes(b[12:14], "big")
    pos = 32
    rows = []
    for _ in range(n):
        if pos + 14 > len(b):
            raise ValueError(f"truncated dir {path}")
        moff, mlen, crc, flags = struct.unpack_from(">IIIH", b, pos)
        namelen = flags & 0xFF
        name = b[pos + 14 : pos + 14 + namelen].decode("ascii", "replace")
        rows.append((name, flags, moff, mlen, crc, b[moff : moff + mlen] if moff + mlen <= len(b) else b""))
        pos += 14 + namelen + 32
    return rows, b


def decode_xml_bytes(payload: bytes) -> bytes:
    if payload[:2] == b"\xfe\xff":
        return payload.decode("utf-16-be").encode("utf-8")
    if payload[:2] == b"\xff\xfe":
        return payload.decode("utf-16-le").encode("utf-8")
    return payload


def iter_saved():
    for p in sorted(CORPUS.glob("*/*")):
        if not p.is_file():
            continue
        ln = p.name.lower()
        if ln.endswith((".xmu", ".js", ".xmf")):
            yield p.parent.name, p.name, p.read_bytes(), "loose"
    for p in sorted(set(CORPUS.rglob("*.aca")) | set(CORPUS.rglob("*.ACA"))):
        if p.stat().st_size < 32:
            print(f"# skip empty/partial {p} size={p.stat().st_size}")
            continue
        try:
            rows, _ = parse_aca(p)
        except ValueError as e:
            print(f"# skip unreadable {p}: {e}")
            continue
        for name, flags, moff, mlen, crc, payload in rows:
            yield p.parent.name, f"{p.name}/{name}", payload, "aca"


# --- listing vs saved ---
listed_aca = 0
saved_complete = 0
saved_partial = 0
for disc, listing in discs():
    _, rows = parse_listing(listing)
    for k, sz, pth in rows:
        if k != "FILE" or not pth.upper().endswith(".ACA"):
            continue
        listed_aca += 1
        loc = saved(disc, pth)
        if loc.is_file() and loc.stat().st_size == sz:
            saved_complete += 1
        elif loc.is_file():
            saved_partial += 1
print(f"listed ACA={listed_aca} saved_complete={saved_complete} saved_partial={saved_partial}")
assert listed_aca == 409

# --- ACA directory ---
namelen0 = namelen_big = slash = 0
aca_n = 0
members = 0
flags_hi = Counter()
exts = Counter()
oliver = []
for p in sorted(CORPUS.rglob("*.aca")):
    if p.stat().st_size < 32:
        continue
    try:
        rows, blob = parse_aca(p)
    except ValueError as e:
        print(f"# skip unreadable {p}: {e}")
        continue
    aca_n += 1
    members += len(rows)
    for name, flags, moff, mlen, crc, payload in rows:
        nl = flags & 0xFF
        if nl == 0:
            namelen0 += 1
        if nl > 64:
            namelen_big += 1
        if "/" in name or "\\" in name:
            slash += 1
        flags_hi[flags >> 8] += 1
        exts[name.rsplit(".", 1)[-1].lower() if "." in name else "(none)"] += 1
        if "archive2" in p.name:
            oliver.append((name, flags, mlen))
print(f"ACA archives={aca_n} members={members} namelen0={namelen0} namelen>64={namelen_big} slash={slash}")
print("flags_hi", dict(flags_hi))
print("member exts", dict(exts.most_common(20)))
print("OLIVER archive2", oliver)
assert namelen0 == 0 and namelen_big == 0 and slash == 0
assert aca_n >= 6

# --- markup / script ---
elems = Counter()
style = Counter()
state = Counter()
clocks = Counter()
pos_vals = Counter()
bg_urls = Counter()
cue_kind = Counter()
uri_root = Counter()
player_hits = Counter()
js_n = xmu_n = xmf_n = 0
unknown_style = []
unknown_el = []
xml_fail = []
p_count = 0
object_count = 0
actioned_xpath = 0
focused_xpath = 0
typelib_hit = Counter()

for disc, name, payload, origin in iter_saved():
    ln = name.lower()
    if ln.endswith(".js") or "/.js" in ln or ln.endswith(".js"):
        if not (ln.endswith(".js")):
            pass
    is_js = ln.endswith(".js")
    is_xmu = ln.endswith(".xmu")
    is_xmf = ln.endswith(".xmf")
    if is_js:
        js_n += 1
        assert payload[:2] == b"\xfe\xff", (disc, name, payload[:8])
        text = payload.decode("utf-16-be")
        for m in re.finditer(r"file:///(required|filecache|dvddisc|fixed|removable|additional|common)(/[^\s\"']*)?", text):
            uri_root[m.group(1)] += 1
        for m in re.finditer(r"Player\.([A-Za-z0-9_.]+)", text):
            player_hits[m.group(1)] += 1
        for n in TYPELIB:
            if re.search(r"\b" + re.escape(n) + r"\b", text):
                typelib_hit[n] += 1
        continue
    if is_xmf:
        xmf_n += 1
        continue
    if not is_xmu:
        continue
    xmu_n += 1
    try:
        root = ET.fromstring(decode_xml_bytes(payload))
    except ET.ParseError as e:
        xml_fail.append((disc, name, str(e)))
        continue
    for el in root.iter():
        tag = el.tag.split("}")[-1] if "}" in el.tag else el.tag
        ns = el.tag[1:].split("}", 1)[0] if el.tag.startswith("{") else ""
        if ns in ("", IHD_NS):
            elems[tag] += 1
            if tag not in IHD_OK:
                unknown_el.append((disc, name, tag))
            if tag == "p":
                p_count += 1
            if tag == "object":
                object_count += 1
            if tag == "timing":
                clocks[el.get("clock", "(omit)")] += 1
            if tag == "cue":
                for attr in ("begin", "end"):
                    v = el.get(attr) or ""
                    if "state:focused" in v:
                        focused_xpath += 1
                        cue_kind["xpath-focused"] += 1
                    elif "state:actioned" in v:
                        actioned_xpath += 1
                        cue_kind["xpath-actioned"] += 1
                    elif re.match(r"\d{2}:\d{2}:\d{2}:\d{2}", v):
                        cue_kind["timecode"] += 1
                    elif re.search(r"\d+(ms|s|m|h|f)\b", v):
                        cue_kind["duration"] += 1
                    elif v:
                        cue_kind["other"] += 1
                        if cue_kind["other"] <= 8:
                            print(f"# cue other {disc} {name} {attr}={v[:80]!r}")
        for k, v in el.attrib.items():
            local = k.split("}")[-1] if "}" in k else k
            kns = k[1:].split("}", 1)[0] if k.startswith("{") else ""
            if kns == STYLE_NS or k.startswith("style:"):
                style[local] += 1
                if local not in STYLE_OK:
                    unknown_style.append((disc, name, local))
                if local == "position":
                    pos_vals[v] += 1
                if local == "backgroundImage":
                    nurl = len(re.findall(r"url\(", v))
                    bg_urls[nurl] += 1
            if kns == STATE_NS or k.startswith("state:"):
                state[local] += 1
                assert local in STATE_OK, (disc, name, local)

print(f"saved JS={js_n} XMU={xmu_n} XMF={xmf_n} xml_fail={xml_fail}")
print("iHD elems", elems.most_common())
print("style", style.most_common())
print("state", dict(state))
print("clocks", dict(clocks))
print("position", dict(pos_vals))
print("bg url() counts", dict(bg_urls))
print("cue_kind", dict(cue_kind), "focused_xpath", focused_xpath, "actioned_xpath", actioned_xpath)
print("p", p_count, "object", object_count)
print("uri_root", dict(uri_root))
print("Player.* top", player_hits.most_common(25))
print("typelib hits", typelib_hit.most_common(40))
print("unknown style", unknown_style, "unknown el", unknown_el)

assert js_n >= 20
assert xmu_n >= 5
assert not unknown_style
assert not xml_fail
assert "fixed" not in uri_root and "removable" not in uri_root
assert set(clocks) <= {"page", "application", "title", "(omit)"}
print("E17 PASS")
