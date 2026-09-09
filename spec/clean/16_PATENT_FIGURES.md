# Patent figures vs disc (vision pass)

Raster sources (not Google Patents D-series 80×120 thumbnails):

| Patent | Page rasters | Bit tables |
|---|---|---|
| US20080298219A1 | `spec/raw/patents/figures/US20080298219A1/pages/page-NNN.png` | `…-C00001.png` … `C00041.png` |
| US20070091495A1 | `…/US20070091495A1/pages/` | `…-D00000.png` … `D00107.png` |
| WO2006070920A1 | `…/WO2006070920A1/pages/` (drawings start ~page 265) | — |

**Page-image numbering.** `pages/page-NNN.png` is produced by
`pdftoppm -png -r 150 <patent>.pdf page` over the patent's own published PDF, so
it is **0-based with `page-000` = the PDF cover** (`page-NNN` = PDF sheet `NNN+1`).
A patent *sheet* header prints `Sheet S of T`; a WO drawing prints `S/138`; the
`FIG.n` label is on the sheet itself. Sheet number ≠ FIG number — cite the
`page-NNN.png` and the `FIG.n` label together, both taken from the image.

**Figure completeness audit** (all three patents, this pass):

| Patent | Individual figure PNGs | Full-page rasters | Status |
|---|---|---|---|
| US20070091495A1 | 109/109 (108 `D`-drawings + 1 `P` photo) vs `urls.txt` | 263 pages rendered | complete |
| US20080298219A1 | 128/128 (`D` + 41 `C` bit-tables) vs `urls.txt` | 156 pages rendered | complete |
| WO2006070920A1  | none published as D-series | 405 pages rendered (138 drawing sheets, FIG.1–FIG.147) | complete |

WO2006070920A1 has **no** Google-Patents D-series, so its 138 drawing sheets are
only available as full-page rasters — now all rendered. Spec-critical WO figures
were read and confirmed on the rendered pages: FIG.108 (GCI_PCK pack, `page-367`),
FIG.109/110 (GCI_PCK + Advanced VTSI, `page-368`), FIG.111/112 (ATRIT/EVOBIT trees,
`page-369`/`page-370`), FIG.119/120 (stream_id + private_stream1 sub_stream_id,
`page-377`), FIG.121/122 (private_stream2 sub_stream_id + stream_id, `page-378`).
These independently corroborate [08](../advanced/08_evo.md) §8.7 stream routing.

Disc still wins when a drawing and a file disagree.

## What the drawings actually specify

### Boot (91495 FIG.7, FIG.8, FIG.50, FIG.51)

**FIG.7** (`page-010.png`): HD DVD? → Category 2 or 3 → play Advanced; Category 1 → Standard; else player-dependent. Matches [01](../advanced/01_volume.md) / [10](../advanced/10_playback.md). The “is HD DVD?” diamond is not a byte in `DISCID`; on this corpus it is UDF 2.50 + `HVDVD_TS/` + `ADV_OBJ/VPLST*.XPL`.

**FIG.8** (`page-011.png`): audio-only player plays Advanced audio (`APLST`). **0** `APLST` files here.

**FIG.50** (`page-050.png`) read as a flowchart, not a caption:

1. S41 display mode
2. S42 Provider ID, Content ID, **search flag** from disc
3. S43 search flag `1b` → skip P-storage
4. S44 else search PLLST under a specified directory on every connected PRSTR
5. S45 search PLLST under **`ADV_OBJ`** on disc
6. S46 play the **highest numbered** PLLST
7. S47 config → S48 object mapping + title timeline TMLE → S49/S50 first track

That is the boot algorithm in sheet 10. Filenames on disc are `VPLST$$$.XPL` / `DISCID.DAT`, not `VPLIST.XML`.

**FIG.51** (`page-051.png`): after highest-PLLST playback, if a new PLLST is downloaded, optionally store it in PRSTR, then issue Soft Reset. **Body text** then runs Change System Configuration (wipe File Cache / Streaming Buffer, same as FIG.50 step 5 / S62) and restores the **new** playlist into File Cache, then mapping/timeline (S63). The **drawing** is easy to read as jumping to S63 and skipping S62. Drawing vs body — do not close A37. Soft reset is `IPlaylist.load` on the three selector discs; it is not a second FIG.50 boot (DISCID category probe is not re-run).

### URI grammar (91495 FIG.19–20) — drawing ≠ body text

**FIG.19** (`page-024.png`): schemes `file` (DISC / FLCCH / PRSTR), `http`, `https`.

**FIG.20** (same sheet), the path table **in the drawing**:

| URI | Location |
|---|---|
| `file:///dvddisc/` | disc |
| `file:///filecache/` | File Cache (app contemporary directory) |
| `file:///required/` | own provider area, required PRSTR |
| `file:///additional/` | own provider area, additional PRSTR |
| `file:///common/required/` | common area, required PRSTR |
| `file:///common/additional/` | common area, additional PRSTR |

The **same patent’s prose** (and Q73) writes `file:///fixed/` and `file:///removable/` instead of required/additional. Playlist.xsd `DataSourceType` is `Disc` / `P-Storage` / `Network` / `FileCache` — not either URI family. Corpus `src` is **10 620 / 10 620** `file:///dvddisc/…`. Persistent-storage path grammar remains **OPEN**; do not memcpy FIG.20 into a C parser.

`[SRC: PATENT | US20070091495A1 FIG.20 | pages/page-024.png]`
`[SRC: PATENT | US20070091495A1 body | "file:///fixed/" / "file:///removable/"]`
`[SRC: CORPUS | playlist src | 10620/10620 dvddisc]`

### Clip table (91495 FIG.18)

`page-023.png` maps patent abbreviations (`PRAVCP`/`PTMAP`/`PRMAV`) to Primary / Secondary / Advanced Subtitle / Application. Retail XML is `PrimaryAudioVideoClip` + `src=` MAP. FIG.18 is a glossary, not an on-disc tag set.

Primary objects: disc only. Secondary: DISC / PRSTR / NTSRV / FLCCH. Advanced subtitle and application: **must stage in File Cache** before use (footnote). Matches multiplexed ACA → File Cache, not a new binary.

### Playlist XML (91495 FIG.21, 98219 FIG.85)

FIG.21 (`page-025.png`): `<playlist>` children **Configuration → MediaAttribute → Title** in that order, so a one-pass parser can init system then share attributes. Retail files are `<Playlist>` with `Configuration` / `MediaAttributeList` / `TitleSet` (XSD). Same idea; **do not** parse the patent’s placeholder tag names.

FIG.85 (`98219 page-073.png`) is an older object-mapping XML. Ignore for Category 2; use Playlist.xsd.

### TMAP file shape (98219 FIG.72–77)

**FIG.72A** (`page-062.png`): Advanced Navigation (Playlist, Loading Info, Markup, Script) vs Advanced Data (Primary = VTSI+TMAP+P-EVOB; Secondary = TMAP+S-EVOB, **no VTSI**; Advanced Element = JPEG/PNG/MNG/L-PCM/OpenType). Matches Category 2.

**FIG.72B**: TMAP = `TMAP_GI` then `TMAPI_SRP` then `TMAPI` then `ILVUI`. Order matches [07](../advanced/07_map.md). The drawing does **not** show the 256-byte hole + u16@372.

**FIG.73** (`page-063.png`): VTSI = `VTSI_MAT` + `VTS_EVOB_ATRT` + `VTS_EVOBIT` (all mandatory). The left column also draws `VTSI_BUP` and `VTS_TMAPI` as siblings of VTSI. On disc, TMAP is a **separate `.MAP` file**, not a table inside the VTI. `HVA00001.BUP` is a copy of the VTI, not of the maps.

**FIG.74**: TMAPI = array of `EVOBU_ENTI`. **FIG.75**: ILVUI = array of `ILVU_ENTI`. ILVUI is a sibling of TMAPI, not nested inside it.

**FIG.76** (`page-064.png`, contiguous): each `EVOBU_ENTI #n` arrows to `EVOBU #n` in one EVOB. Seek = sum of sizes. Matches every `TMAP_TY=0x2000` map.

**FIG.77** (`page-065.png`, interleaved) — **authoring family, not this corpus’s MAP**:

- Drawing: **two TMAP files**, `TMAPI#1`+`ILVUI#1` for `EVOB_IDN=1` and `TMAPI#2`+`ILVUI#2` for `EVOB_IDN=2`.
- Each `ILVU_ENTI` covers a **run of consecutive** `EVOBU_ENTI` (variable EVOBU count per ILVU).
- Both ILVUIs have the **same number of ILVU entries** (`r`), even if EVOBU counts inside a pair differ.
- Physical ILVB: EVOB#1 chunk, EVOB#2 chunk, EVOB#1 chunk, …

**Pan’s Labyrinth (disc):** one `.MAP`, `TMAPI_Ns` = 3 or 4, **one** ILVU array; record `i` belongs to TMAPI `i % Ns`; one sibling `.EVO`. `ILVU_SZ` is the EVOBU count of **that angle’s** run — that part of FIG.77 matches `e13`. Do not allocate “one ILVUI per TMAPI file.”

`[SRC: PATENT | US20080298219A1 FIG.77 | pages/page-065.png]`
`[SRC: DISC | PANS_LABYRINTH four MAP | e13]`

**FIG.88** (`page-076.png`): `EVOB4` and `EVOB5` share **`TMAP4_5`**, then that TMAP maps onto one timeline block `P-Video4_5`. A third authoring: two EVO files, one TMAP name. Also shows a **hole** on the title timeline (600–800) with Application only — primary video need not cover every tick. Implement playlist `titleTimeBegin`/`End`, not “EVOBs are contiguous on the timeline.”

### TMAP_TY — TABLE 81 figure (C00039)

`US20080298219A1-20081204-C00039.png` (16-bit, `b15` = MSB of byte 0):

| Bits | Field |
|---|---|
| 15–10 | reserved |
| 9 | `ILVUI` — `0b` contiguous / no ILVUI; `1b` interleaved / ILVUI present |
| 8 | `ATR` — `0b` Primary (no `EVOB_ATR` in this TMAP); `1b` Secondary (`EVOB_ATR` present; **forbidden on Primary**) |
| 7–2 | reserved |
| 1–0 | Angle: `00b` none, `01b` non-seamless, `10b` seamless, `11b` reserved |

Corpus:

| Value | Bits that are 1 | N |
|---|---|---|
| `0x2000` | **b13 only** (inside “reserved” 15–10) | 2417 contiguous |
| `0x2202` | b13 + **b9 ILVUI** + Angle **`10b` seamless** | 4 Pan’s |

Named flags match TABLE 81 text. Bit 13 is always set and **unnamed** in the figure — do not treat it as ILVUI. `ATR` (b8) is 0 on all 2421 primary maps (`EVOB_ATR_SA = 0xFFFFFFFF`).

`[SRC: PATENT | US20080298219A1 TABLE 81 figure C00039]`
`[SRC: CORPUS | TMAP_TY | 2417×0x2000 + 4×0x2202]` **VERIFIED** for named bits

### EVOBU_ENT — TABLE 83 figure (C00040)

Already in sheet 07: 11 + 8 + 13. Re-read of the PNG agrees: `1STREF_SZ = (u32>>21)&0x7FF`, `EVOBU_PB_TM = (u32>>13)&0xFF`, `EVOBU_SZ = u32&0x1FFF`.

### EVOB_TY (C00041)

8-bit: b7–4 reserved, b3–0 `EVOB_TY`. The figure **duplicates** meanings (`0001b`=`0010b` sub-video only; `0011b`=`0100b` complementary audio). This is **not** EVOBI `type/flags` (`0x2000` on 2431/2431). Likely Secondary-EVOB attribute in `EVOB_ATR` inside a Secondary TMAP (0 specimens). Ignore for Primary.

### V_ATR (C00003 vs C00008)

Both are the same 32-bit word as ATRI+2. C00008 (VTSTT_EVOBS) puts **Film camera mode** at b16; C00003 leaves b17–16 reserved. Other fields match: compression 31–30, TV 29–28, aspect 27–26, display mode 25–24, CC1/CC2, progressive 21–20, letterboxed b18, resolution 15–12. Disc: never AVC/VC-1 in this word (0/1131). **Use the playlist for codec.**

### AST_ATR (C00010) vs ATRI

C00010 is a **64-bit** DVD-style `A_ATR` (coding mode, channels, 16-bit specific code / language). On-disc Advanced ATRI stores **4-byte** `AST_ATR` words at +16. FIG.111 (WO) lists `AHDVTS_AST_ATR` then `AHDVTS_MU_AST_ATR` as logical fields — not a memcpy of C00010. Bit layout of the 4-byte disc word remains **OPEN** (A49). Decoder follows XPL.

C00013 is 8×1-byte `ACH0…ACH7` mix flags (bits 191–128 of a larger MU-ATR). Not observed as a named table in the 1024-byte ATRI.

### Application type (C00038)

32-bit word, only b3–0 live: `0010b` Advanced VTS, `0011b` Interoperable VTS. Matches `VTS_CAT = 2` at VTI RBP 34.

**Full WO drawing-set read:** every one of the 138 WO2006070920A1 drawing sheets
(FIG.1–FIG.147) was inspected image-by-image; the FIG→page map and scope of each is in
[16b_WO_FIGURE_INDEX.md](16b_WO_FIGURE_INDEX.md). No Category-2 format detail is missing.

### ATRI / EVOBI trees (WO FIG.111 / 112)

**FIG.111** (`WO …/pages/page-369.png`): `ATRIT` = header (`SRP_Ns`, `EA`) + `ATRI_SRP[].SA` + `ATRI[]`. Logical ATRI field **order**: `V_ATR`, `AST_Ns`, `AST_ATR`, `MU_AST_ATR`, `SPST_Ns`, `SPST_ATR`, `SPST_SDPLT`, `SPST_HDPLT`. That is a **tree**, not the 1024-byte packing in sheet 06 (`V_ATR` at +2, `AST_Ns` at +14, `SP_Ns` at +229, dummy palettes at +391 on 7 titles). Offset 193 (`01 1c 00 c4` on 16/1131) is still unnamed.

**FIG.112** (`page-370.png`): `EVOBIT` = header + SRP + `EVOBI{ EVOB_IDN, EVOB_ATRN, TMAP_FILE_NAME }`. Disc EVOBI+2 is the **`.EVO` filename**, 36 bytes; there is **no** MAP name in the VTI. Playlist `src` is the MAP. Patent field list is incomplete and mis-named relative to the file.

### Stream IDs (WO FIG.119–124)

**FIG.119–120** (`page-377.png`): Primary `stream_id` `0xE0` video, `0xBD` private_stream1, `0xBF` private_stream2. Inside `0xBD`, besides DVD audio/SP ranges, **Secondary Content** video `0x91` MPEG-2 / `0x92` AVC / `0x93` VC-1, plus secondary DD+ / DTSHD / LPCM ranges. Primary feature AVC/VC-1 on this corpus uses `0xE2` / `0xFD`+ext `0x55` ([08](../advanced/08_evo.md)), not `0x91–0x93`. Treat `0x91–0x93` as PiP/secondary, not as “HD DVD video is always private_stream1.”

**FIG.121** (`page-378.png`) `private_stream2` sub_stream: `0x00` PCI, `0x01` DSI, `0xFF` provider. **GCI `0x04` is not in this WO table** (falls under “others / reserved”). 98219 Tables 50–51 and every Advanced NV_PCK here use `0x04`. Disc + 98219 win. FIG.121 is the DVD-shaped subset.

FIG.123–124 (`page-379.png`) repeat the Standard private_stream1/2 map (AC-3 `10000***b`, PCI/DSI). Do not use them to reject GCI or ADV_PCK `0x80`.

### SP_ATR (C00004 / C00012)

48-bit sub-picture attribute: coding mode b47–45, HD/SD-Wide/SD-PS/SD-LB flags in byte 1. C00012 fills language “specific code” in bytes 2–3; C00004 marks those reserved. Disc ATRI uses **5-byte** `SP_ATR` after `SP_Ns`. Do not paste either 6-byte figure into the 1024-byte slot.

## Implementer rules from the pictures

1. **TMAP_TY** decode with C00039 masks: ILVUI `0x0200`, ATR `0x0100`, Angle `0x0003`. Accept `0x2000` and `0x2202`. Any other live named bit → fail that clip (A61 still ASK for unknown values).
2. **Interleaved MAP:** one file, `Ns` TMAPIs, one ILVU array cycling `i % Ns`. FIG.77/88 are other authoring shapes.
3. **Seek contiguous:** FIG.76 1:1 ENT→EVOBU; sum `EVOBU_SZ`.
4. **Boot:** FIG.50 then, on `IPlaylist.load`, FIG.51 soft reset to mapping init — not a second highest-number search.
5. **URI:** implement `file:///dvddisc/` from disc+XSD. Do not hard-code FIG.20’s required/additional vs the body’s fixed/removable until a P-storage specimen exists.
6. **VTI:** FIG.111/112 name fields; sheet 06 has the strides. EVOBI names the EVO, not the MAP.
7. **NV_PCK:** parse `0x00`/`0x01`/`0x04` by sub_stream_id. WO FIG.121 is incomplete.

## Not used (Standard / out of scope)

98219 `page-051.png` = **FIG.61 PGC**. `page-007` of 91495 is **FIG.4** Standard VMG, not FIG.7. C00036 is 13-bit SP RLE, not TMAP.
