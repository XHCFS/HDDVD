#!/usr/bin/env python3
"""E16 — ADV_PCK 0x80 layout and File Cache concat.

Positive specimen: STALINGRAD /HVDVD_TS/logo.EVO (31 617 024 B).
PlaylistApplicationResource multiplexed 1–6 are mainApp.aca … ineditsMenu.aca.

Negative (full-file, 0x80 = 0): OLIVER JpnTokuhou.EVO, LoopMenu.EVO;
ARMY_OF_SHADOWS advanced.EVO. multiplexed=N does not imply that title's EVO
contains ADV_PCK; the ACA still lives under ADV_OBJ.

Claim: private_stream_2 payload starts 0x80; packed byte is scramble 2b +
adv_pkt_status 2b + reserved 4b; first packet (status=01b) carries
slot + ACA filename then ADDTHD zeros then HDDVDACA; concat of one slot
equals the ADV_OBJ file.

Falsifier: reconstituted bytes ≠ /ADV_OBJ/<name>.aca.

Dump: spec/raw/adv_obj/samples/advpck_stalingrad_logo.bin (8 packs).
"""
from __future__ import annotations

import os
import struct
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from udfgrab import Remote, UDF  # noqa: E402

SAMPLES = ROOT / "spec" / "raw" / "adv_obj" / "samples"
DUMP = SAMPLES / "advpck_stalingrad_logo.bin"
DISC = "STALINGRAD"
EVO = "logo.EVO"
CHUNK = 4 * 1024 * 1024
FIRST_DATA = 259  # payload offset of HDDVDACA on first packets (this disc)


def iter_bf(pack: bytes):
    stuffing = pack[13] & 7
    i = 14 + stuffing
    while i + 6 <= len(pack):
        if pack[i : i + 3] != b"\x00\x00\x01":
            return
        sid = pack[i + 3]
        plen = struct.unpack_from(">H", pack, i + 4)[0]
        body = pack[i + 6 : min(len(pack), i + 6 + plen)]
        yield sid, plen, body, i
        i += 6 + plen


def parse_adv(pack: bytes, pack_index: int):
    if pack[:4] != b"\x00\x00\x01\xba":
        return None
    for sid, plen, payload, i in iter_bf(pack):
        if sid != 0xBF or not payload or payload[0] != 0x80:
            continue
        packed = payload[1] if len(payload) > 1 else 0
        return dict(
            pack_index=pack_index,
            i=i,
            pes_len=plen,
            packed=packed,
            scramble=(packed >> 6) & 3,
            status=(packed >> 4) & 3,
            reserved=packed & 0xF,
            slot=payload[2] if len(payload) > 2 else None,
            fname=payload[2:34] if len(payload) >= 34 else b"",
            payload=payload,
            pack=pack,
        )
    return None


def report(hits):
    for h in hits:
        raw = h["fname"].split(b"\x00", 1)[0]
        print(
            f"  pack {h['pack_index']} pes_at={h['i']} scramble={h['scramble']} "
            f"status={h['status']} reserved={h['reserved']} slot={h['slot']} "
            f"fname={raw!r} pes_len={h['pes_len']}",
            flush=True,
        )


def assert_sample_layout():
    assert DUMP.is_file() and DUMP.stat().st_size >= 2048, DUMP
    blob = DUMP.read_bytes()
    n = len(blob) // 2048
    hits = []
    for k in range(n):
        h = parse_adv(blob[k * 2048 : (k + 1) * 2048], k)
        assert h, f"sample pack {k} is not ADV_PCK"
        hits.append(h)
    print(f"# dump {DUMP} packs={n}", flush=True)
    report(hits)
    h0 = hits[0]
    assert h0["reserved"] == 0 and h0["scramble"] == 0
    assert h0["status"] == 1 and h0["slot"] == 1
    name = h0["fname"].split(b"\x00", 1)[0]
    assert name == b"\x01mainApp.aca", name
    assert h0["payload"][FIRST_DATA : FIRST_DATA + 8] == b"HDDVDACA"
    vern, enc, nent = struct.unpack_from(">HHH", h0["payload"], FIRST_DATA + 8)
    total = struct.unpack_from(">I", h0["payload"], FIRST_DATA + 14)[0]
    assert vern == 0x0010 and enc == 1 and nent == 9
    assert total == 260447, total  # listing FILE size of mainApp.aca
    assert all(x == 0 for x in h0["payload"][34:FIRST_DATA])
    assert hits[6]["status"] == 0
    assert hits[6]["slot"] == 1 and hits[6]["payload"][3] == 0
    print("# sample layout OK", flush=True)
    return hits


def fetch_all_adv(u: UDF):
    tgt = u.find(f"/HVDVD_TS/{EVO}")
    assert tgt, EVO
    (ext, _), sz = tgt
    print(f"# found {EVO} size={sz}", flush=True)
    hits = []
    scanned = 0
    pack_i = 0
    for pos, ln in ext:
        off = 0
        while off < ln:
            take = min(CHUNK, ln - off)
            blob = u.r.read((u.part_start + pos) * 2048 + off, take)
            n = len(blob) // 2048
            for k in range(n):
                h = parse_adv(blob[k * 2048 : (k + 1) * 2048], pack_i + off // 2048 + k)
                if h:
                    h.pop("pack", None)
                    hits.append(h)
            off += take
            scanned += take
            print(
                f"#   scanned {scanned/1e6:.1f}/{sz/1e6:.1f} MB hits={len(hits)}",
                flush=True,
            )
        pack_i += ln // 2048
    print(f"# ADV_PCK total={len(hits)}", flush=True)
    return hits


def piece(h, mid_skip: int):
    p = h["payload"]
    if h["status"] == 1:
        return p[FIRST_DATA:]
    return p[mid_skip:]


def try_recon(hits, files: dict[int, bytes]):
    by = defaultdict(list)
    for h in hits:
        by[h["slot"]].append(h)
    print("# slots", {s: len(v) for s, v in sorted(by.items())}, flush=True)
    for skip in list(range(0, 8)) + [34]:
        ok = []
        for slot, aca in files.items():
            blob = b"".join(piece(h, skip) for h in by[slot])
            ok.append(blob == aca)
            if slot == 1:
                print(
                    f"# skip={skip} slot1 recon={len(blob)} file={len(aca)} match={blob==aca}",
                    flush=True,
                )
        if all(ok):
            return skip
    return None


def main():
    SAMPLES.mkdir(parents=True, exist_ok=True)
    assert_sample_layout()
    if not os.environ.get("E16_FULL"):
        print("# skip network recon (set E16_FULL=1 to re-fetch logo.EVO)")
        print("E16 PASS")
        return

    listing = ROOT / "corpus" / DISC / "_listing.txt"
    url = listing.read_text().splitlines()[0].strip().lstrip("# ")
    print(f"# mount {url}", flush=True)
    u = UDF(Remote(url, chunk=CHUNK))
    hits = fetch_all_adv(u)
    assert hits, "no ADV_PCK in logo.EVO"

    status_c = {}
    for h in hits:
        status_c[h["status"]] = status_c.get(h["status"], 0) + 1
    print(f"# status_counts {status_c}", flush=True)
    assert 1 in status_c and 0 in status_c

    names = {}
    for h in hits:
        if h["status"] == 1:
            names[h["slot"]] = h["fname"][1:].split(b"\x00", 1)[0].decode("ascii")
    print(f"# first-packet names {names}", flush=True)

    files = {}
    for slot, name in names.items():
        tgt = u.find(f"/ADV_OBJ/{name}")
        assert tgt, name
        raw = u.fetch(*tgt)
        files[slot] = raw
        print(f"# pulled /ADV_OBJ/{name} {len(raw)}", flush=True)

    skip = try_recon(hits, files)
    assert skip is not None, "no mid-packet skip reconstituted the ACA files"
    print(f"# concat mid_skip={skip} matches all {len(files)} ACA files")
    print("E16 PASS")


if __name__ == "__main__":
    main()
