#!/usr/bin/env python3
"""E20 — HDi scripting ABI (sheet 12). Offline.

Claim: the type library `spec/raw/adv_obj/typelib/iHDScripting.tlb` is a real MSFT
OLE type library with 106 typeinfos / 954 names; the extracted name list
`iHD_Scripting_API.txt` carries the object model + the runtime constants scripts use
(TIMER_TITLE/TIMER_APPLICATION, PLAYSTATE_*, DOMAIN_*, STORAGE_*, FILE_IOMODE_*,
CODEC_*, CHANNEL_*). The iHD v1.0 XSDs give 26 markup elements + the full style/state
attribute sets.

Falsifier: tlb magic not MSFT; header typeinfo count != 106; a named constant the
spec cites (e.g. TIMER_TITLE) absent from the extract; XSD element set drifts.

Offline: reads the saved .tlb, the name list, and the XSDs. No network.
"""
import os, re, struct

ROOT = os.path.join(os.path.dirname(__file__), "..")


def main():
    tlb = open(os.path.join(ROOT, "spec/raw/adv_obj/typelib/iHDScripting.tlb"), "rb").read()
    assert tlb[:4] == b"MSFT", "not an MSFT type library"
    nrtypeinfos = struct.unpack_from("<i", tlb, 0x20)[0]
    nametablecount = struct.unpack_from("<i", tlb, 0x30)[0]
    assert nrtypeinfos == 106, nrtypeinfos
    assert nametablecount == 954, nametablecount

    api = open(os.path.join(ROOT, "spec/raw/adv_obj/iHD_Scripting_API.txt"),
               encoding="utf-8", errors="replace").read()
    ti = len(re.findall(r"^(?:dispinterface|interface|coclass)\s+\S+\s+\(\d+ members\)", api, re.M))
    assert ti == 106, ti
    for c in ("TIMER_TITLE", "TIMER_APPLICATION", "PLAYSTATE_PLAY", "PLAYSTATE_PAUSE",
              "DOMAIN_TITLE", "DOMAIN_MENU", "STORAGE_REQUIRED", "FILE_IOMODE_READ",
              "CODEC_DD", "CHANNEL_5_1"):
        assert c in api, c
    consts = len(re.findall(r"^\s+[A-Z][A-Z0-9_]{2,}$", api, re.M))
    assert consts >= 190, consts

    def xsd_names(fn, tag):
        s = open(os.path.join(ROOT, "spec/raw/adv_obj/v1.0", fn), encoding="utf-8",
                 errors="replace").read()
        return set(re.findall(rf'<xs:{tag}[^>]*name="([^"]+)"', s))
    el = xsd_names("iHD.xsd", "element")
    for e in ("root", "body", "div", "button", "input", "p", "cue", "animate", "set", "object"):
        assert e in el, e
    assert len(el) == 26, len(el)

    print(f"  tlb MSFT ok: {nrtypeinfos} typeinfos / {nametablecount} names")
    print(f"  name list: {ti} typeinfos, {consts} constants (TIMER_TITLE etc. present)")
    print(f"  iHD.xsd elements: {len(el)}")
    print("E20 PASS")


if __name__ == "__main__":
    main()
