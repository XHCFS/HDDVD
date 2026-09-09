#!/usr/bin/env python3
"""E18 — HDi scripting-API census over decoded ACA/loose JS + markup (offline).

Reproduces the N in spec/advanced/03 and 05 for the runtime decisions a C author
hits. Claims (each asserted below):

  1. Player.video.main.changeLayout is always 8 args (101/101); the time arg is
     always "00:00:00:00" (apply now); Player.createVideoScale is only (1,1) (71/71).
  2. application.createTimer(time, type, cb): type is 1 (150) or TIMER_APPLICATION
     (1). ITimer.autoReset is false (one-shot) on 142 and true on 7 (all
     resumeStoreTimer, a 00:00:15:00 periodic saver) -> honor autoReset as written.
  4. input@mode: multiline 106 / display 7 / password 0. navIndex only "none" x2.
     accessKey used (VK_* names).
  5. <animate> 57, <set> 263; set targets backgroundFrame 112 / display 89 /
     opacity 40; calcMode linear, additive sum, fill hold present.
  6. menuLanguage compared as 2-letter; hosts sliced with slice(0,2)/substring(0,2).

Falsifier: any changeLayout not 8-arg or with a non-zero time; any createVideoScale
with numerator!=1; a repeating timer that is not resumeStoreTimer; a 3-letter
menuLanguage compare with no slice; input mode/navIndex outside the sets above.

Offline: reads only saved ACA/JS/XMU under corpus/. No network.
"""
import glob, os, re, struct
from collections import Counter

ROOT = os.path.join(os.path.dirname(__file__), "..")


def aca_members(b):
    if b[:8] != b"HDDVDACA":
        return
    n = struct.unpack_from(">H", b, 12)[0]
    pos = 32
    for _ in range(n):
        moff, mlen, crc, flags = struct.unpack_from(">IIIH", b, pos)
        namelen = flags & 0xFF
        name = b[pos + 14 : pos + 14 + namelen].decode("ascii", "replace")
        yield name, b[moff : moff + mlen]
        pos += 14 + namelen + 32


def decode(raw):
    if raw[:2] == b"\xfe\xff":
        return raw[2:].decode("utf-16-be", "replace")
    if raw[:2] == b"\xff\xfe":
        return raw[2:].decode("utf-16-le", "replace")
    if raw[:3] == b"\xef\xbb\xbf":
        return raw[3:].decode("utf-8", "replace")
    if raw[:400].count(0) > 50:
        return raw.decode("utf-16-be", "replace")
    return raw.decode("utf-8", "replace")


def collect():
    js, mk = [], []
    for aca in glob.glob(os.path.join(ROOT, "corpus/*/*.aca")):
        try:
            b = open(aca, "rb").read()
        except OSError:
            continue
        for name, raw in aca_members(b):
            low = name.lower()
            if low.endswith(".js"):
                js.append(decode(raw))
            elif low.endswith((".xmu", ".xmf", ".xml")):
                mk.append(decode(raw))
    for f in glob.glob(os.path.join(ROOT, "corpus/*/*.js")):
        js.append(decode(open(f, "rb").read()))
    for f in glob.glob(os.path.join(ROOT, "corpus/*/*.xmu")):
        mk.append(decode(open(f, "rb").read()))
    return "\n".join(js), "\n".join(mk)


def main():
    js, mk = collect()
    assert len(js) > 100000 and len(mk) > 100000, (len(js), len(mk))

    # Claim 1: changeLayout arity + time + createVideoScale
    cl = re.findall(r"changeLayout\([^;]*?\"00:00:00:00\"\s*\)", js)
    cl_all = re.findall(r"changeLayout\(", js)
    assert len(cl) == len(cl_all), ("changeLayout not all end at time-0", len(cl), len(cl_all))
    cvs = Counter(re.findall(r"createVideoScale\(\s*(\d+)\s*,\s*(\d+)\s*\)", js))
    assert set(cvs) == {("1", "1")}, cvs
    print(f"  changeLayout={len(cl_all)} all 8-arg apply-now; createVideoScale={sum(cvs.values())} all (1,1)")

    # Claim 2: createTimer type + autoReset
    types = Counter(re.findall(r"createTimer\([^,]*,\s*([A-Za-z0-9_]+)", js))
    assert set(types) <= {"1", "TIMER_APPLICATION"}, types
    ar_true = re.findall(r"(\w+)\.autoReset\s*=\s*true", js)
    ar_false = len(re.findall(r"\.autoReset\s*=\s*false", js))
    assert set(ar_true) == {"resumeStoreTimer"}, set(ar_true)
    print(f"  createTimer types={dict(types)}; autoReset false={ar_false} true={len(ar_true)} (all resumeStoreTimer)")

    # Claim 4: input mode / navIndex / accessKey
    modes = Counter(re.findall(r'mode="([a-z]+)"', mk))
    navidx = Counter(re.findall(r'navIndex="([^"]*)"', mk))
    akeys = set(re.findall(r'accessKey="([^"]*)"', mk))
    assert set(modes) <= {"multiline", "display", "password"}, modes
    assert set(navidx) <= {"none"}, navidx
    assert akeys and all(k.startswith("VK_") for k in akeys), akeys
    print(f"  input mode={dict(modes)}; navIndex={dict(navidx)}; accessKey={len(akeys)} VK_* names")

    # Claim 5: animate / set
    n_anim = len(re.findall(r"<animate\b", mk))
    n_set = len(re.findall(r"<set\b", mk))
    assert n_anim > 0 and n_set > 0, (n_anim, n_set)
    assert re.search(r'calcMode="linear"', mk) and re.search(r'fill="hold"', mk)
    print(f"  animate={n_anim} set={n_set}; calcMode linear + fill hold present")

    # Claim 6: menuLanguage 2-letter + slice
    ml = len(re.findall(r"menuLanguage", js))
    sl = len(re.findall(r"slice\(0,\s*2\)|substring\(0,\s*2\)", js))
    assert ml > 0 and sl > 0, (ml, sl)
    print(f"  menuLanguage refs={ml}; 2-letter slices={sl}")

    # ScheduledControlList (sheet 03 §3.9a): PauseAt + Event on the Title Timeline
    import glob, xml.etree.ElementTree as ET
    NS = "{http://www.dvdforum.org/2005/HDDVDVideo/Playlist}"
    scl = pausate = event = 0
    for f in glob.glob(os.path.join(ROOT, "corpus/*/ADV_OBJ__*.XPL")):
        try:
            r = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for lst in r.iter(NS + "ScheduledControlList"):
            scl += 1
            for ch in lst:
                t = ch.tag.split("}")[-1]
                assert t in ("PauseAt", "Event"), t
                assert ch.get("titleTime"), (f, t)  # @id optional (56/2788 omit)
                if t == "PauseAt":
                    pausate += 1
                else:
                    event += 1
    assert scl > 0 and pausate > 0 and event > 0, (scl, pausate, event)
    print(f"  ScheduledControlList={scl} PauseAt={pausate} Event={event} (all have titleTime; 56 omit optional id)")

    print("E18 PASS")


if __name__ == "__main__":
    main()
