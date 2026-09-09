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

```
[0 .. 127]     TMAP_GI
[128 .. 371]   zero on 2421/2421
[372 .. 373]   u16be ILVU record count on the four interleaved maps (equals the walk until ILVU_SZ=0); **zero on 2417 contiguous maps**. TMAPI_SRP.ILVU_ENT_Ns is still 0. Do not use the SRP field.
[374 .. 383]   zero
[384 .. )      TMAPI_SRP, 10-byte record in a 32-byte slot, one per TMAPI
[TMAPI_SA ..)  TMAPI = EVOBU_ENT[EVOBU_ENT_Ns]
[ILVUI_SA ..)  ILVUI only if present (not 0xFFFFFFFF)
```

`[128 .. 383]` is **not** reserved-zero on Pan’s four maps: only bytes **372–373** are live (`death` 180, `ofeliaDeath` 372, `ofeliaEnters` 500, `ofeliaFig` 240).
`[11]` **VERIFIED**

`TMAPI_SA` and `ILVUI_SA` are **byte offsets from the start of the file**, not LBNs
(patent says LBN; every disc uses bytes).

## 7.2 TMAP_GI (128 bytes): TABLE 80

| RBP | Size | Field | Rule |
|---|---|---|---|
| 0 | 12 | `TMAP_ID` | `"HDDVD_TMAP00"` |
| 12 | 4 | `TMAP_EA` | last sector of this file (`file_sectors − 1`); 2421/2421 |
| 16 | 2 | reserved | 0 |
| 18 | 2 | `VERN` | `0x0010` |
| 20 | 2 | `TMAP_TY` | see below |
| 22 | 28 | reserved | |
| 50 | 5 | reserved | “VTMAP_LAST_MOD_TM” in patent |
| 55 | 2 | `TMAPI_Ns` | `1` on Primary Video Set (2417/2421) |
| 57 | 4 | `ILVUI_SA` | byte offset, or `0xFFFFFFFF` if none |
| 61 | 4 | `EVOB_ATR_SA` | `0xFFFFFFFF` on primary maps |
| 65 | 49 | reserved | |
| 114 | 12 | VTI filename | `"HVA00001.VTI"` on 2421/2421 |
| 126 | 2 | reserved | 0 |

### TMAP_TY: TABLE 81 figure C00039

16-bit, `b15` = MSB of byte 0. Figure: `spec/raw/patents/figures/US20080298219A1/US20080298219A1-20081204-C00039.png`.

| Bits | Mask | Field |
|---|---|---|
| 15–10 | | reserved (corpus always has **b13** set → `0x2000`) |
| 9 | `0x0200` | `ILVUI`: `0b` no ILVUI (contiguous); `1b` ILVUI present (interleaved) |
| 8 | `0x0100` | `ATR`: `0b` Primary, no `EVOB_ATR` in this file; `1b` Secondary (`EVOB_ATR` present; **not allowed on Primary**) |
| 7–2 | | reserved |
| 1–0 | `0x0003` | Angle: `00b` none, `01b` non-seamless, `10b` seamless, `11b` reserved |

| Value | N | Meaning |
|---|---|---|
| `0x2000` | 2417 | contiguous primary (`TMAPI_Ns=1`, `TMAPI_SA=416`): b13 only |
| `0x2202` | 4 | Pan’s interleaved: b13 + ILVUI + Angle `10b` seamless |

`[2]`
`[11, 12]` **VERIFIED** for the named bits. Bit 13 has no label in the figure.

## 7.3 TMAPI_SRP: TABLE 82

Starts at **byte 384**. One 10-byte record in a **32-byte slot**: `384 + 32×i`.

| Size | Field | Rule |
|---|---|---|
| 4 | `TMAPI_SA` | **byte** offset of this TMAPI |
| 2 | `VTS_EVOBIN` | EVOBI index (not always the `EVOBnnn` number) |
| 2 | `EVOBU_ENT_Ns` | entry count. `Ns×4 + TMAPI_SA` lands in the file |
| 2 | `ILVU_ENT_Ns` | **0** on 2417 contiguous maps **and** on the four interleaved maps |

When `TMAPI_Ns=1`, `TMAPI_SA=416` (2417/2417).  
When `Ns=3`, SA=480 (`PANS_LABYRINTH` `death.MAP`). When `Ns=4`, SA=512 (three `ofelia*` maps). Those four are the only `Ns≠1`. `Video@angleNumber` is **1-based** → TMAPI index `angleNumber − 1`.

## 7.4 EVOBU_ENT: TABLE 83 (4 bytes)

Big-endian u32. Figure: https://patents.google.com/patent/US20080298219A1
image `US20080298219A1-20081204-C00040.png`.

| Bits | Width | Field | Unit |
|---|---|---|---|
| 31–21 | 11 | `1STREF_SZ` | packs from EVOBU start through last byte of first reference picture |
| 20–13 | 8 | `EVOBU_PB_TM` | video **fields** in this EVOBU |
| 12–0 | 13 | `EVOBU_SZ` | packs in this EVOBU |

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
Sum `EVOBU_PB_TM` directly against that tick count (do not ×2).

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
| 4 | `ILVU_ADR` | pack index in the sibling `.EVO`, ascending |
| 2 | `ILVU_SZ` | **EVOBU count of this angle** in this contiguous run (patent TABLE 84), **not packs**. Authoring quantum is usually `TMAPI_Ns` (3 or 4) with a leftover tail (`death` SZ=1×3; `ofelia*` SZ=3×4) |

**No ILVUI header.** `ILVUI_SA` points at the first `ILVU_ENT`. Walk 6-byte records until `ILVU_SZ=0`. Count lives at **u16be @372** (equals the walk). `TMAPI_SRP.ILVU_ENT_Ns` is **0**. Do not use it.

Records **cycle angles**: record `i` belongs to TMAPI `i % TMAPI_Ns`. `ILVU_ADR` is a pack index in the sibling `.EVO`. The next `ADR` is this `ADR` plus the sum of that angle’s next `ILVU_SZ` `EVOBU_SZ` values. Verified 179/179 + 371 + 499 + 239 consecutive deltas (`e13`). Treating `SZ` as packs never matches (would step by 3 or 4, not hundreds).

To play angle `A` (1-based `Video@angleNumber` → `A = angleNumber − 1`): skip ILVU records whose `i % Ns ≠ A`; at each matching record, decode `SZ` EVOBUs from `TMAPI[A]` starting at `ADR × 2048`. The walk consumes every EVOBU on every TMAPI.

Contiguous titles (`TMAP_TY=0x2000`) never need this. AACS sequence-key files (`SKF`) are **0/120** here; user angle selection is the observed mechanism. Player SK path remains **OPEN**.

Patent FIG.77 draws **one TMAP file per angle EVOB**, each with its own ILVUI; FIG.88 draws two EVOBs sharing one TMAP name. This corpus is neither: one `.MAP`, `Ns` TMAPIs, one cycling ILVU array, one `.EVO`. Implement the disc walk (`spec/clean/16_PATENT_FIGURES.md`).
