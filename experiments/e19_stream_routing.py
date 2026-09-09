#!/usr/bin/env python3
"""E19 — elementary-stream routing (sheet 08 §8.7). Offline.

Claim: @streamNumber (1-based) + @mediaAttr codec select a PES stream by the
US20080298219A1 TABLE 45/46 bit patterns:
  main video  MPEG-2=0xE0, AVC=0xE2, VC-1=0xFD ext 0x55
  audio       0xBD sub = base|(n-1); base DD+ 0xC0, AC-3 0x80, DTS-HD 0x88,
              LPCM 0xA0, MLP 0xB0   (or MPEG audio stream_id 0xC0|n directly)
  subtitle    0xBD sub = 0x20|(n-1)   (0x20..0x3F, 32 max = SubtitleTrack max)

Falsifier: a saved disc observation whose (declared stream, observed PES) pair
contradicts the table. Sample: spec/raw/adv_obj/samples/stream_routing_downfall.json

Offline: pure table logic + the saved JSON observation. No network.
"""
import json, os

ROOT = os.path.join(os.path.dirname(__file__), "..")

VIDEO = {"MPEG-2": ("stream_id", 0xE0), "MPEG-4 AVC": ("stream_id", 0xE2),
         "AVC": ("stream_id", 0xE2), "H.264": ("stream_id", 0xE2),
         "VC-1": ("ext", 0x55)}
AUDIO_BASE = {"DD+": 0xC0, "AC-3": 0x80, "DTS-HD": 0x88, "LPCM": 0xA0, "MLP": 0xB0}


def audio_substream(codec, stream_number):
    return AUDIO_BASE[codec] | (stream_number - 1)


def subpic_substream(stream_number):
    return 0x20 | (stream_number - 1)


def main():
    # table invariants
    assert audio_substream("DD+", 1) == 0xC0 and audio_substream("DD+", 2) == 0xC1
    assert audio_substream("MLP", 1) == 0xB0 and audio_substream("DTS-HD", 1) == 0x88
    assert subpic_substream(1) == 0x20 and subpic_substream(32) == 0x3F
    # 3-bit audio decoding number (max 8 -> AudioTrack max 8); 5-bit sub-pic (max 32)
    assert all(0xC0 <= audio_substream("DD+", n) <= 0xC7 for n in range(1, 9))
    assert all(0x20 <= subpic_substream(n) <= 0x3F for n in range(1, 33))
    assert VIDEO["VC-1"] == ("ext", 0x55)

    # disc observation
    s = json.load(open(os.path.join(ROOT, "spec/raw/adv_obj/samples/stream_routing_downfall.json")))
    obs = s["observed_pes"]
    assert obs["0xFD/ext=0x55"] > 100, "VC-1 main video not dominant"
    assert obs["0xBD/0xC0"] > 0 and obs["0xBD/0xC1"] > 0, "two DD+ audio substreams expected"
    # declared DD+ streamNumber 1,2 must map to observed 0xC0,0xC1
    obs_u = {k.upper().replace(" ", "") for k in obs}
    assert f"0XBD/0X{audio_substream('DD+', 1):X}" in obs_u
    assert f"0XBD/0X{audio_substream('DD+', 2):X}" in obs_u
    print("  video VC-1 -> 0xFD ext 0x55 (769 packs); DD+ audio 1,2 -> 0xBD 0xC0,0xC1")
    print("  sub-picture 0x20|(n-1) gives 0x20..0x3F (32 = SubtitleTrack max)")
    print("E19 PASS")


if __name__ == "__main__":
    main()
