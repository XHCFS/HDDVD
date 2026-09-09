# `.MAP` (TMAP) — solved

Time maps for Advanced Content. Playlists address clips through these, never directly
by EVO. Provenance per `EVIDENCE_STANDARD.md`.

## Layout

```
TMAP_GI          128 bytes (then zeros through byte 383)
TMAPI_SRP        one 10-byte record per TMAPI, in 32-byte slots starting at byte 384
TMAPI            array of EVOBU_ENT, at TMAPI_SA (byte offset)
ILVUI            only when TMAP_TY says interleaved; at ILVUI_SA (byte offset)
```
`[SRC: PATENT | US20080298219A1 | "This TMAP starts from TMAP General Information (TMAP_GI). A TMAPI Search pointer (TMAPI_SRP) and TMAP information (TMAPI) follow the TMAP_GI, and ILVU Information (ILVUI) is allocated at the end."]`

## TMAP_GI — TABLE 80

`[SRC: PATENT | US20080298219A1 TABLE 80]` + `[SRC: DISC | DOWNFALL /HVDVD_TS/EVOB002.MAP @0]`
**VERIFIED** (patent and disc agree on every field below)

| RBP | Size | Field | Observed | Patent wording |
|---|---|---|---|---|
| 0 | 12 | `TMAP_ID` | `HDDVD_TMAP00` | patent says `"HDDVD-V_TMAP"` — **drift** |
| 12 | 4 | `TMAP_EA` | 35 | end address, relative LBN (file = 36 sectors) |
| 16 | 2 | reserved | 0 | |
| 18 | 2 | `VERN` | 0x0010 | version (matches `VMGI_MAT.VERN`) |
| 20 | 2 | `TMAP_TY` | 0x2000 | ILVUI / ATR / Angle bits |
| 22 | 28 | reserved | | |
| 50 | 5 | reserved | | "reserved for VTMAP_LAST_MOD_TM" |
| 55 | 2 | `TMAPI_Ns` | 1 | *"In the TMAP for a Primary Video Set, the TMAPI_Ns is set to '1'"* |
| 57 | 4 | `ILVUI_SA` | FFFFFFFF | *"If no ILVUI exists in the TMAP (that for a contiguous block), the ILVUI_SA is padded with '1b or FFh'"* |
| 61 | 4 | `EVOB_ATR_SA` | FFFFFFFF | *"when the TMAP for a Primary Video Set does not include any EVOB_ATR, the EVOB_ATR is padded with '1b'"* |
| 65 | 49 | reserved | | OCR dropped the next row |
| 114 | 12 | VTI filename | `HVA00001.VTI` | missing TABLE 80 row |
| 126 | 2 | reserved | 00 00 | completes the stated 128-byte total |

Three fields carry conditional values the patent predicts exactly, and the disc matches
all three. That is what makes this VERIFIED rather than plausible.

**OCR gap closed.** Listed rows sum to 114 against a stated total of 128. The missing
14 bytes are RBP 114-127: a 12-byte VTI filename plus 2 NULs. The prose also mentions
copy-protection information (CPI) in TMAP_GI; that name is not needed to close the
arithmetic. After byte 127 the rest of the first 384 bytes is zero on every primary MAP.
`[SRC: CORPUS | N=2421 MAP @114-126 = "HVA00001.VTI", @126-127 = 00 00]`
**VERIFIED**

**`TMAPI_SRP` location — SOLVED (was WRONG/OPEN).** It is not at offset 128 (zeros;
that is padding after the 128-byte TMAP_GI). The search-pointer table starts at
**byte 384**. Each pointer is the patent's 10-byte TABLE 82 record, stored in a
**32-byte slot** (`384 + 32×i`).
`[SRC: CORPUS | N=2421 | first nonzero after TMAP_GI is the u32 at 384; decode as TABLE 82]`
**VERIFIED**

Patent vs disc on `TMAPI_SA`: the patent says *"relative logical block number from the
first logical block of the TMAP"*. On every disc it is a **byte offset** from the start
of the file. LBN 416 would be far past a 36-sector MAP; byte 416 is exactly where
`EVOBU_ENT` begins for `TMAPI_Ns=1`. Disc wins.
`[SRC: PATENT | US20080298219A1 TABLE 82 TMAPI_SA]`
`[SRC: CORPUS | N=2417 Ns=1 | TMAPI_SA=416, EVOBU_ENT_Ns×4+416 ≤ file size]`

### TMAP_TY bits
`[SRC: PATENT | US20080298219A1 TABLE 81 figure C00039 | b9 ILVUI, b8 ATR, b1–b0 Angle]`
**VERIFIED** against 2417×`0x2000` and 4×`0x2202` (`0x2202` = reserved b13 + ILVUI + seamless).
- `ILVUI` (b9, `0x0200`): 0b = contiguous block, 1b = interleaved block
- `ATR` (b8, `0x0100`): 0b = Primary Video Set, 1b = Secondary Video Set
- `Angle` (b1–b0): 00b none, 01b non-seamless angle block, 10b seamless angle block,
  11b reserved. *"may be set if the value of 'Block' in ILVUI = '1b'"*
- b13 (`0x2000`) is in the figure’s reserved 15–10 and is set on every map here.

## TMAPI_SRP — TABLE 82, 10 bytes, on-disc at offset 384

`[SRC: PATENT | US20080298219A1 TABLE 82 | field names]`
`[SRC: CORPUS | N=2421 MAP @384]`
**VERIFIED**

| Size | Field | On disc |
|---|---|---|
| 4 | `TMAPI_SA` | **byte** offset of this TMAPI (patent: LBN — drift) |
| 2 | `VTS_EVOBIN` | index of the `VTS_EVOBI` this TMAPI refers to (varies; not always the `EVOBnnn` filename number) |
| 2 | `EVOBU_ENT_Ns` | entry count; `Ns×4 + TMAPI_SA` lands inside the file, then sector-pad |
| 2 | `ILVU_ENT_Ns` | 0 on all 2417 contiguous maps |

Slotting: one 32-byte slot per `TMAPI_Ns`, so `TMAPI_SA` is `384 + 32×TMAPI_Ns`:

| `TMAPI_Ns` | N | `TMAPI_SA` | `TMAP_TY` |
|---|---|---|---|
| 1 | 2417 | 416 | `0x2000` |
| 3 | 1 | 480 | `0x2202` (`PANS_LABYRINTH/death.MAP`) |
| 4 | 3 | 512 | `0x2202` (three other Pan's Labyrinth angle maps) |

`[SRC: CORPUS | N=2421]`
**VERIFIED** — `TMAP_EA == (file_sectors - 1)` on 2421/2421.

`ILVU_ENT_Ns` is 0 even on the four `0x2202` maps; interleaved entries live in the
separate ILVUI region (below), not in this field. **OPEN** why the SRP count is zero
there.

## EVOBU_ENT — TABLE 83, 4 bytes, packed bitfields

TABLE 83's bit boxes are a chemistry drawing, not HTML text. The figure was read
as pixels.

`[SRC: PATENT | US20080298219A1 TABLE 83 figure C00040 | https://patentimages.storage.googleapis.com/e8/d8/6f/5f52512ba7b091/US20080298219A1-20081204-C00040.png]`
`[SRC: CORPUS | e08 | N=2,343,256 EVOBU_ENT]`
`[SRC: DISC | DOWNFALL EVOB002.MAP @416 + EVOB002.EVO NV_PCK DSI | 5/5 VOBU chain]`
**VERIFIED**

Big-endian 32-bit word, `b31` = MSB of byte 0:

| Bits | Field | Width | Units |
|---|---|---|---|
| b31–b21 | `1STREF_SZ` (Upper + Lower) | 11 | packs, first reference picture |
| b20–b13 | `EVOBU_PB_TM` (Upper + Lower) | 8 | video fields |
| b12–b0 | `EVOBU_SZ` (Upper + Lower) | 13 | packs, this EVOBU |

An earlier DOWNFALL-only reading treated b12–b11 and b31–b29 as reserved (always
zero on that title). Corpus-wide **108** entries have `EVOBU_SZ > 2047` (need the
13th bit). `e08` asserts no zero sizes.

DOWNFALL `EVOB002.EVO` pack count still matches the **sum** of 13-bit `EVOBU_SZ`
(11,471,010). First five MAP sizes `{290,418,460,457,510}` equal `DSI.vobu_ea+1`
at walk positions `{0,290,708,1168,1625}` **5/5**.

Ground truth for the file-size check:
`[SRC: DISC | DOWNFALL _listing.txt | EVOB002.EVO = 23,492,628,480 bytes = 11,471,010 packs]`
`[SRC: CORPUS | DOWNFALL VPLST*.XPL | clip duration 9322.05 s, TitleSet@tickBase="60fps"]`

Semantics, verbatim `[SRC: PATENT | US20080298219A1 TABLE 83 text]`:
- `EVOBU_SZ` — *"the size of this EVOBU, which is specified by the number of packs"*
- `EVOBU_PB_TM` — *"the Playback Time of this EVOBU, which is specified by the number
  of video fields in this EVOBU"*
- `1STREF_SZ` — *"the number of packs from the first pack of this EVOBU to the pack
  which includes the last byte of the first encoded reference picture"*

`1STREF_SZ` is what makes seeking land on a decodable frame rather than approximately.

## ILVU_ENT — TABLE 84, 6 bytes

`[SRC: PATENT | US20080298219A1 TABLE 84 | names and units]`
`[SRC: DISC | PANS_LABYRINTH death.MAP / ofeliaDeath.MAP / ofeliaEnters.MAP / ofeliaFig.MAP]`
**SINGLE** disc, 4 files (the only `TMAP_TY=0x2202` / `TMAPI_Ns>1` specimens in 2421)

On these four, `ILVUI_SA` (TMAP_GI RBP 57) is a **byte offset**, not an LBN — same
drift as `TMAPI_SA`. `EVOB_ATR_SA` remains `FFFFFFFF`.
`[SRC: DISC | death.MAP ILVUI_SA=0xA38=2616, file size 4096]`

At that offset, 6-byte records parse as TABLE 84: `ILVU_ADR` u32 ascending,
`ILVU_SZ` u16. On `death.MAP` the first entries are `(ADR=0, SZ=3), (396, 3), (792, 3),
…` — `SZ=3` matches `TMAPI_Ns=3` (one EVOBU per angle per ILVU). Full ILVUI header
before/around the array is **OPEN**.

`TMAP_TY` `0x2000` (2417) vs `0x2202` (4): both have bit 13 set; the angle maps add
`0x0202` = C00039 `ILVUI` + Angle `10b`. Named bits **VERIFIED**. Bit 13 still unnamed.

## Why the first RE attempt failed

Cumulative offsets and monotonic timestamps were ruled out early. **Both
conclusions were correct.** Entries are per-EVOBU sizes and durations, not
addresses — so nothing is monotonic, and entries-per-second is non-integer because
entries are per EVOBU rather than per time unit.

## Using it

- **time to byte**: accumulate `EVOBU_PB_TM` until the target field count; the
  accumulated `EVOBU_SZ` x 2048 is the byte offset into the EVOB.
- **fast seek**: at the landing EVOBU read `1STREF_SZ` packs to reach a reference
  picture.
- Cross-check: DSI in the stream carries the same information per VOBU
  (`vobu_ea`, `vobu_1stref_ea`) — see `08_NV_PCK_PCI_DSI.md`. **Run:** DOWNFALL
  EVOB002 first five EVOBUs, MAP `EVOBU_SZ == DSI.vobu_ea+1` and
  `DSI.nv_pck_lbn ==` walk position, 5/5. MYSTERY_MEN FEATURE_1 VOBU0: MAP 81 =
  `vobu_ea+1`.
