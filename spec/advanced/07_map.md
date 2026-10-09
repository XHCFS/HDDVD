# 7. MAP: time map

*Counts written "N/120", "N/119", "on N discs", "listings", or as named discs are over the reference corpus of 120 archived retail HD DVD images [11]. `eNN` are the reproducible verification experiments [12].*


Path: `HVDVD_TS/<clip>.MAP`  
Magic: `HDDVD_TMAP00` (patent text says `"HDDVD-V_TMAP"`; **disc wins**)  
2421 files.

Playlists address clips **only** through this file. Seek is:

```
title time T
  → clip where titleTimeBegin ≤ T < titleTimeEnd
  → local = T − titleTimeBegin + clipTimeBegin
  → walk EVOBU_ENT until playback fields cover local
  → file offset = accumulated EVOBU_SZ × 2048 in sibling .EVO
```

## 7.1 File layout

The book's layout is [23 §6.3.2]. One map per EVOB of a contiguous block; one map
for all EVOBs of an interleaved block, with one TMAPI per EVOB in order. The map
is sector-aligned and may be followed by up to 2047 zero bytes.

```
[0 .. 383]     TMAP_GI (384 bytes)
[384 .. )      TMAPI_SRP, one 32-byte record per TMAPI
[TMAPI_SA ..)  TMAPI = EVOBU_ENT[EVOBU_ENT_Ns]
[ILVUI_SA ..)  ILVUI = ILVU_ENT[ILVU_ENT_Ns], only for an interleaved block
```

`TMAPI_SA` and `ILVUI_SA` are **byte offsets from the start of the file**: the book's
RBN, as on every disc (the patent says LBN).
`[23]` **SPEC**; `[11]` **VERIFIED**

## 7.2 TMAP_GI (384 bytes) [23 Table 6.3.2.1-1]

| RBP | Size | Field | Rule |
|---|---|---|---|
| 0 | 12 | `TMAP_ID` | `"HDDVD_TMAP00"` (patent text says `"HDDVD-V_TMAP"`; book and disc agree) |
| 12 | 4 | `TMAP_EA` | last sector of this map (RLBN, `file_sectors − 1`); 2421/2421 |
| 16 | 2 | reserved | 0 |
| 18 | 2 | `VERN` | `0x0010` (low byte = book version 1.0) |
| 20 | 2 | `TMAP_TY` | see below |
| 22 | 28 | reserved | |
| 50 | 5 | reserved for the Interoperable VTS | patent: `VTMAP_LAST_MOD_TM` |
| 55 | 2 | `TMAPI_Ns` | `1` for a contiguous block (2417/2421) |
| 57 | 4 | `ILVUI_SA` | byte offset, or `0xFFFFFFFF` if none |
| 61 | 4 | `EVOB_ATR_SA` | `0xFFFFFFFF` on primary maps |
| 65 | 49 | reserved | |
| 114 | 255 | `VTSI_FNAME` | VTI filename, ISO 8859-1, zero-filled: `"HVA00001.VTI"` on 2421/2421 |
| 369 | 1 | reserved for copy protection | 0 |
| 370 | 4 | `ILVU_ENT_Ns` | number of `ILVU_ENT` in the interleaved block; 0 when there is no ILVUI. Non-zero exactly on the four interleaved maps (`death` 180, `ofeliaDeath` 372, `ofeliaEnters` 500, `ofeliaFig` 240), equal to the walk until `ILVU_SZ=0` |
| 374 | 10 | reserved | 0 |

An earlier version of this sheet took the GI as 128 bytes with an unexplained
count at 372–373; the book's 384-byte GI explains both.

### TMAP_TY [23 §6.3.2.1]

16-bit, `b15` = MSB of byte 0. Patent figure:
`spec/raw/patents/figures/US20080298219A1/US20080298219A1-20081204-C00039.png`.

| Bits | Mask | Field |
|---|---|---|
| 15–12 | `0xF000` | Application type: `0001b` Standard VTS, `0010b` Advanced VTS, `0011b` Interoperable VTS; `0100b` Secondary Video Set (§7.6) |
| 11–10 | | reserved for copy protection |
| 9 | `0x0200` | `ILVUI`: `0b` no ILVUI (contiguous); `1b` ILVUI present (interleaved) |
| 8 | `0x0100` | `ATR`: `0b` Primary, no `EVOB_ATR` in this file; `1b` Secondary (`EVOB_ATR` present; **not allowed on Primary**) |
| 7–2 | | reserved |
| 1–0 | `0x0003` | Angle: `00b` none, `01b` non-seamless angle block, `10b` seamless angle block, `11b` reserved. `01b` or `10b` when `ILVUI` is 1 |

| Value | N | Meaning |
|---|---|---|
| `0x2000` | 2417 | Advanced VTS, contiguous (`TMAPI_Ns=1`, `TMAPI_SA=416`) |
| `0x2202` | 4 | Pan's interleaved: Advanced VTS + ILVUI + Angle `10b` seamless |

The `0x2000` bit that the patent figure leaves unlabelled is the application type.
`[23]` **SPEC**; `[2]`; `[11, 12]` **VERIFIED**

## 7.3 TMAPI_SRP (32 bytes each) [23 §6.3.2.2]

Starts at **byte 384**: record `i` at `384 + 32×i`.

| Offset | Size | Field | Rule |
|---|---|---|---|
| 0 | 4 | `TMAPI_SA` | **byte** offset of this TMAPI |
| 4 | 2 | `EVOB_INDEX` | 1–1998: the `EVOB_INDEX` of the EVOB this TMAPI maps, as in its VTS_EVOBI ([06](06_vti.md) §6.3). Equal on 2420/2420 maps whose EVOB has an EVOBI. Look the EVOBI up by this number, not by position |
| 6 | 2 | `EVOBU_ENT_Ns` | entry count. `Ns×4 + TMAPI_SA` lands in the file |
| 8 | 24 | reserved | 0 on 2421/2421 (an earlier reading took 8–9 as an `ILVU_ENT_Ns`; the count is at 370 of the GI) |

When `TMAPI_Ns=1`, `TMAPI_SA=416` (2417/2417).  
When `Ns=3`, SA=480 (`PANS_LABYRINTH` `death.MAP`). When `Ns=4`, SA=512 (three `ofelia*` maps). Those four are the only `Ns≠1`. `Video@angleNumber` *n* is the *n*-th TMAPI (1-based) → TMAPI index `angleNumber − 1` [23 §6.2.3.3].

## 7.4 EVOBU_ENT: TABLE 83 (4 bytes)

Big-endian u32. Figure: https://patents.google.com/patent/US20080298219A1
image `US20080298219A1-20081204-C00040.png`.

| Bits | Width | Field | Unit |
|---|---|---|---|
| 31–21 | 11 | `1STREF_SZ` | packs from EVOBU start through the pack holding the last byte of the first I-coded-frame; 0 if the EVOBU has no video |
| 20–13 | 8 | `EVOBU_PB_TM` | playback time in **VSTUs** (video system time units: one field period, 1.001/60 s or 1/50 s) |
| 12–0 | 13 | `EVOBU_SZ` | packs in this EVOBU |

`[23 §6.3.2.3]` **SPEC**

Do not use an 11-bit size. Corpus: **108** entries have `EVOBU_SZ > 2047`, all on
**contiguous** maps (`e14` A69). **0** on the four interleaved maps. 13-bit SZ is
required even if you never play Pan’s.
No zero sizes in 2,343,256 entries (`e08`).

`EVOBU_SZ` equals `DSI.vobu_ea + 1` on Advanced EVOs checked (DOWNFALL first five
EVOBUs 5/5; MYSTERY_MEN VOBU0 = 81).

### Seek algorithm

Local title time → integer ticks on `TitleSet@timeBase`:

```
ticks(HH:MM:SS:FF) = ((HH*60 + MM)*60 + SS) * fps + FF
  fps = 60 if timeBase="60fps", 50 if "50fps"
```

On `60fps` titles, a 0.5 s VOBU has `EVOBU_PB_TM=30` (fields) and 30 title ticks.
Sum `EVOBU_PB_TM` directly against that tick count (do not ×2). Both count VSTUs
from the EVOB's first video frame: `sum(EVOBU_PB_TM) × 1501.5` equals
`EVOB_V_E_PTM − EVOB_V_S_PTM` to one 90 kHz tick on 2415/2417 contiguous maps with an
EVOBI (`e28`; the two others are `ETERNAL_SUNSHINE` `DELEXT8`, which has no EVOBI of
its own, and `DOWNFALL` `EVOB002`, whose map runs one 30-field EVOBU past
`EVOB_V_E_PTM`). The PTS of EVOBU *k* is `EVOB_V_S_PTM + 1501.5 × (sum of the
PB_TM before it)`, which is its GCI `EVOBU_S_PTM` (`ARMY_OF_DARKNESS` `BLACK.EVO`,
120/120 within two ticks).
`[23 §6.3.2.3]` **SPEC**; `[11, 12]` **VERIFIED**

```
need = ticks(local_time)
acc_tm = 0
acc_packs = 0
for each EVOBU_ENT:
    if acc_tm + EVOBU_PB_TM > need:
        return acc_packs * 2048          # byte offset of this EVOBU in the .EVO
    acc_tm += EVOBU_PB_TM
    acc_packs += EVOBU_SZ
```

Fast decode: skip `1STREF_SZ` packs to the first reference picture.

## 7.5 ILVU_ENT: TABLE 84 (6 bytes)

Only four maps (`PANS_LABYRINTH` `death.MAP`, `ofeliaDeath.MAP`, `ofeliaEnters.MAP`,
`ofeliaFig.MAP`). `ILVUI_SA` is a byte offset (`death.MAP`: `0xA38`).

| Size | Field | Rule |
|---|---|---|
| 4 | `ILVU_ADR` | start of the ILVU as an RLBN from the first sector of the interleaved block [23 §6.3.2.4]; the block is the whole `.EVO` file, so this is the pack index in it, ascending |
| 2 | `ILVU_SZ` | **EVOBU count of this angle** in this ILVU (book and patent TABLE 84), **not packs**. Authoring quantum is usually `TMAPI_Ns` (3 or 4) with a leftover tail (`death` SZ=1×3; `ofelia*` SZ=3×4) |

**No ILVUI header.** `ILVUI_SA` points at the first `ILVU_ENT`. There are
`ILVU_ENT_Ns` records (GI offset 370); walking 6-byte records until `ILVU_SZ=0`
gives the same count.

Records **cycle angles**: record `i` belongs to TMAPI `i % TMAPI_Ns`. `ILVU_ADR` is a pack index in the sibling `.EVO`. The next `ADR` is this `ADR` plus the sum of that angle’s next `ILVU_SZ` `EVOBU_SZ` values. Verified 179/179 + 371 + 499 + 239 consecutive deltas (`e13`). Treating `SZ` as packs never matches (would step by 3 or 4, not hundreds).

To play angle `A` (1-based `Video@angleNumber` → `A = angleNumber − 1`): skip ILVU records whose `i % Ns ≠ A`; at each matching record, decode `SZ` EVOBUs from `TMAPI[A]` starting at `ADR × 2048`. The walk consumes every EVOBU on every TMAPI.

Contiguous titles (`TMAP_TY=0x2000`) never need this. AACS sequence-key files (`SKF`) are **0/120** here; user angle selection is the observed mechanism. Player SK path remains **OPEN**.

Patent FIG.77 draws **one TMAP file per angle EVOB**, each with its own ILVUI; FIG.88 draws two EVOBs sharing one TMAP name. This corpus is neither: one `.MAP`, `Ns` TMAPIs, one cycling ILVU array, one `.EVO`. Implement the disc walk (`spec/clean/16_PATENT_FIGURES.md`).

## 7.6 Secondary Video Set maps

The map of a Secondary Video Set ([03](03_playlist.md) §3.10) differs [23 §6.4.1].
0 on disc.

| RBP | Size | Field |
|---|---|---|
| 0 | 12 | `TMAP_ID` `"HDDVD_TMAP00"` |
| 12 | 4 | `TMAP_EA` |
| 16 | 2 | reserved |
| 18 | 2 | `VERN` |
| 20 | 2 | `TMAP_TY`: application type `0100b`, `ILVUI` 0, `ATR` 1, Angle `00b` |
| 22 | 33 | reserved |
| 55 | 2 | `TMAPI_Ns`: 0 or 1 (0 allowed, for example for a live stream) |
| 57 | 4 | `ILVUI_SA`: all 1s |
| 61 | 4 | `EVOB_ATR_SA`: byte offset of the `EVOB_ATR` |
| 65 | 49 | reserved |
| 114 | 255 | `VTSI_FNAME`: all 1s |
| 369 | 1 | reserved |
| 370 | 255 | `EVOB_FNAME`: the S-EVOB this map belongs to; a network player fetches it from the map's location [23 §9.2.2.2] |
| 625 | 1 | reserved |
| 626 | 4 | `EVOB_V_S_PTM` (90 kHz; the first audio time if there is no video) |
| 630 | 4 | `EVOB_FIRST_SCR` |
| 634 | 6 | reserved |

The GI is 640 bytes. Then at most one `TMAPI_SRP` (`TMAPI_SA`, 2 reserved bytes,
`EVOBU_ENT_Ns`, 24 reserved), the TMAPI, and one 1024-byte `EVOB_ATR`: `EVOB_TY`
(b3–b0 content: `0001b` Substitute Audio, `0010b` Secondary AV with sub video,
`0100b` with sub audio, `0110b` with both, `1001b` Substitute AV), `EVOB_VM_ATR`,
`EVOB_VS_ATR`, `EVOB_VS_LUMA`, reserved 2, `EVOB_AMST_Ns`, `EVOB_AMST_ATRT` (32),
`EVOB_DM_COEFTS` (144), `EVOB_ASST_Ns`, `EVOB_ASST_ATRT` (32), reserved, laid out
as in [06](06_vti.md) §6.2.

An S-EVOB with video is mapped by `EVOBU_ENT` as above. One without video is
divided into **Time Units** (each starting with a navigation pack, 0.4–1.001 s,
the last at most 1.2012 s, a whole number of audio frames) and mapped by `TU_ENT`:

| Bits | Field |
|---|---|
| 31–13 | `TU_DIFF` (19 bits): PTS of the next TU's first frame minus this TU's (90 kHz); for the last TU, its last frame minus its first |
| 12–0 | `TU_SZ` (13 bits): packs in this TU |

`[23 §6.4]` **SPEC**; 0 on disc.
