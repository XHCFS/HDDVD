# Build specification — reading HD DVD

Every claim carries a provenance tag per `EVIDENCE_STANDARD.md`.
Format: `[SRC: class | locator | how]` + confidence.

Confidence: **VERIFIED** (patent+disc agree, or multi-specimen) · **SINGLE** (one
specimen) · **INFERRED** (reasoned, not observed) · **OPEN**.

---

## 1. Filesystem — UDF 2.50 with Metadata Partition

**Claim:** every HD DVD uses UDF with two partition maps: type 1 physical, type 2
`*UDF Metadata Partition`.
`[SRC: DISC | RESERVOIR_DOGS + MYSTERY_MEN LVD @ VDS sector 32 | partition map table at LVD+440]`
`[SRC: TOOL | udfclient -b 2048 <sparse image> | prints "mapping 1 on 0 as metadata only recording metadata"]`
**VERIFIED** (2 discs by direct parse, 24 discs by metadata-extent scan, plus independent tool)

**Claim:** libdvdread's `dvd_udf.c` cannot mount these.
`[SRC: SRCCODE | libdvdread dvd_udf.c | single-partition UDF 1.02 reader, no partition-map type 2 handling]`
**INFERRED** — read the source, did not run it against a disc.

**Claim:** libudfread does handle them.
`[SRC: SRCCODE | libudfread src/udf_volume.c:47-56,430-488 | UDF_FT_METADATA=250, meta_domain_id="*UDF Metadata Partition", _map_metadata_partition()]`
**VERIFIED** by source reading.

**Caveat — libudfread limitation:**
`[SRC: SRCCODE | libudfread src/udf_volume.c:430-441 | "Interim support level: only the first allocation extent of the metadata files is mapped"]`
It errors on fragmented metadata files. Tested: **120/120 discs produced a complete
listing** via `tools/udfgrab.py` (which uses the same first-extent mapping as
libudfread). Fragmented metadata files remain unseen.
`[SRC: CORPUS | N=120 corpus/*/_listing.txt]`
**VERIFIED** for this corpus — still possible on media we do not have.

**Claim:** `part_start` is 288 on every surveyed disc.
`[SRC: CORPUS | N=120 listings | "# partition_start=288"]`
**VERIFIED** in-corpus; still unknown whether the spec mandates 288 or Sonic/authoring
does.

**Claim:** sector size 2048 is both the reader constant and the LVD field.
`[SRC: SRCCODE | tools/udfgrab.py SECTOR=2048]` + `[SRC: CORPUS | N=120]`
`[SRC: DISC | MYSTERY_MEN, DOWNFALL, RESERVOIR_DOGS LVD @ VDS | LogicalBlockSize u32le @ descriptor+212 = 2048]`
`[SRC: DISC | same three LVDs | Domain Identifier `*OSTA UDF Compliant`, UDF revision suffix `0x0250`]`
**VERIFIED** — 120/120 listings plus a direct LVD parse on 3/3 categories (Advanced
AACS, Advanced, Standard).

### The rule that will bite you
FEs and **directory data** live in the metadata partition; **file payload** lives in
the physical partition. An ICB's allocation descriptors refer to the partition holding
that ICB — except regular file data, which is always physical.
`[SRC: DERIVED | tools/udfgrab.py debugging | reading root dir extents as physical gave tag 266; as metadata gave tag 257 (FID) - the correct one]`
**VERIFIED** empirically.

Working reference implementation: `tools/udfgrab.py`.

## 2. Namespace and naming

| Item | DVD | HD DVD | Provenance |
|---|---|---|---|
| content dir | `VIDEO_TS` | `HVDVD_TS` | `[SRC: CORPUS \| N=120 listings]` **VERIFIED** |
| VMG | `VIDEO_TS.IFO` | `HV000I01.IFO`/`.BUP` | `[SRC: DISC \| RESERVOIR_DOGS]` **SINGLE** |
| VTS info | `VTS_%02d_0.IFO` | `HV%03dI01.IFO` | same **SINGLE** |
| menu obj | `VTS_%02d_0.VOB` | `HV%03dM%02d.EVO` | same **SINGLE** |
| title obj | `VTS_%02d_%d.VOB` | `HV%03dT%02d.EVO` | same **SINGLE** |
| max VTS | 99 | 511 | `[SRC: PATENT \| US20070091495A1 \| "at least 1 with maximum 511 Video Title Set"]` **INFERRED** (highest observed = 11) |
| Advanced VTI | — | `HVA00001.VTI` | `[SRC: CORPUS \| N=119]` **VERIFIED** |
| other dirs | — | `ADV_OBJ/`, `ANY!/`, `ANY!_BAK/` | `[SRC: CORPUS \| N=120]` **VERIFIED** |

**OPEN:** why the VMG menu object is `HV000M02.EVO` and not `M01`. Numbering rule
unknown. VTS menus on the same disc *do* use `M01` (`HV001M01.EVO`, `HV009M01.EVO`,
`HV010M01.EVO`). `I02` never appears; every IFO is `HV%03dI01.IFO`.
`[SRC: DISC | RESERVOIR_DOGS listing | 12 IFOs, 4 menu EVOs]`

**Never seen:** `HVSO@@@@.MAP` (patent names this for Standard VTS time maps
referenced from Advanced Content). Zero hits in 120 listings.
`[SRC: PATENT | US20070091495A1]` + `[SRC: CORPUS | N=120 listings | grep HVSO → 0]`

**`DISCID.DAT` — solved.** See addendum below and `04_ADV_OBJ.md`. 119/119 Advanced
discs; absent on the one Standard Content disc.

## 3. Standard Content IFO structures

**All of §3 rests on ONE disc** (`RESERVOIR_DOGS`, the only Category 1 disc in 120
surveyed) `[SRC: CORPUS | N=120 | tools/udfgrab.py --list classification]`.
Anything marked SINGLE could be a Sonic Scenarist SCA 4.2 artifact rather than a
format property. `[SRC: TOOL | udfclient | implementation id "*Sonic ScenaristSCA42"]`

### Identifiers — 12-byte ASCII, DVD convention
`HVDVD-VMG100`, `STANDARD-VTS`, `ADVANCED-VTS`
`[SRC: DISC | RESERVOIR_DOGS HV000I01.IFO @0, HV001I01.IFO @0; corpus VTI N=119]`
**VERIFIED**

### `VMGI_MAT` — patent-specified
`[SRC: PATENT | US20080298219A1 | VMGI_MAT RBP table]` + `[SRC: DISC | RESERVOIR_DOGS HV000I01.IFO]`
**VERIFIED** (both sources agree)

Key offsets: `VMG_ID` 0, `VMG_EA` 12, `VMGI_EA` 28, `VERN` 32, `VMG_CAT` 34,
`VTS_N` 62, `VMGI_MAT_EA` 128, `FP_PGCI_SA` 132, then the pointer block:
`VMGM_EVOBS_SA` 192, `TT_SRPT_SA` 196, `VMGM_PGCI_UT_SA` 200, `PTL_MAIT_SA` 204,
`VTS_ATRT_SA` 208, `TXTDT_MG_SA` 212, **`FP_PGCM_C_ADT_SA` 216**,
**`FP_PGCM_EVOBU_ADMAP_SA` 220**, `VMGM_C_ADT_SA` 224, `VMGM_EVOBU_ADMAP_SA` 228.

> **Correction.** An earlier draft called this "byte-identical to DVD-Video". It is
> not: RBP 216/220 are new in HD DVD and push `VMGM_C_ADT`/`VMGM_EVOBU_ADMAP` from
> DVD's 0xD8/0xDC to 0xE0/0xE4. Disc reads 8 and 9 there.
> `[SRC: DISC | RESERVOIR_DOGS HV000I01.IFO @0xE0,0xE4]`

### `VTSI_MAT` (STANDARD-VTS) — patent-specified
`[SRC: PATENT | US20080298219A1 | VTSI_MAT RBP table]` + `[SRC: DISC | RESERVOIR_DOGS HV001I01.IFO]`
**VERIFIED**

Pointer block at RBP 184-231 (DVD has it at 0x88): `VTSM_EVOBS_SA` 192,
`VTSTT_EVOBS_SA` 196, `VTS_PTT_SRPT_SA` 200, `VTS_PGCIT_SA` 204,
`VTSM_PGCI_UT_SA` 208, `VTS_TMAPT_SA` 212, `VTSM_C_ADT_SA` 216,
`VTSM_EVOBU_ADMAP` 220, `VTS_C_ADT_SA` 224, `VTS_EVOBU_ADMAP_SA` 228.
Attributes: `VTS_V_ATR` 532 (**4 bytes**, DVD has 2), `VTS_AST_N` 536 (u16),
`VTS_AST_ATRT` 538 (8x8 B), `VTS_SPST_N` 602 (u16), `VTS_SPST_ATRT` 604 (32x6 B),
`VTS_MU_AST_ATRT` 798.

### `VTSI_MAT` (ADVANCED-VTS) — patent-specified, disc-verified
`[SRC: PATENT | US20080298219A1 TABLE 77]` + `[SRC: CORPUS | N=119 corpus/*/HVDVD_TS__HVA00001.VTI]`
**VERIFIED** — 119/119 have `VTS_ID`=`ADVANCED-VTS`, `VERN`=0x0010, and
`VTSI_EA` == (file sectors - 1).

`VTS_ID` 0, `VTS_EA` 12, `VTSI_EA` 28, `VERN` 32, `VTS_CAT` 34,
`VTSI_MAT_EA` 128, `VTS_EVOB_ATRT_SA` 184, `VTS_EVOBIT_SA` 188, `VTS_EVOBS_SA` 196,
rest reserved to 2047.
`VTS_CAT` low bits = application type; `0010b` = Advanced VTS
`[SRC: PATENT | US20080298219A1 TABLE 79]`; observed value 2 `[SRC: CORPUS | N=119]`.
`VTS_EVOB_ATRT_SA` is **1** (sector) on 119/119; `VTS_EVOBS_SA` is **0** on 119/119
(EVOBs are separate files, not stored in the VTI). `VTS_EVOBIT_SA` varies.

#### `VTS_EVOB_ATRT` body — DVD-style table, 1024-byte entries
`[SRC: PATENT | WO2006070920A1 FIG.111 AHDVTS_ATRIT | ATRITI + ATRI_SRP + ATRI]`
`[SRC: CORPUS | N=119 VTI, ATRT at sector VTS_EVOB_ATRT_SA]`
**VERIFIED** (arithmetic 119/119)

Header at the start of that sector: `nr` u16 @0, reserved u16 @2, `last_byte` u32 @4,
then `nr` × u32 start offsets. First offset is always `8 + 4×nr`. Each `ATRI` is
**1024 bytes**: `(last_byte+1 - first_SA) / nr = 1024` on every specimen.

Bytes **2–5** are TABLE 9/16 `V_ATR` (same 4-byte video-attribute word as
`VMGM_V_ATR` / `VTS_V_ATR`). Bit boxes from the patent figure; enums from the
prose. Bytes 0–1 are flags (`0000` on 987/1131, `1000` on 125, `0500`/`0400` rare).

`[SRC: PATENT | US20080298219A1 TABLE 9 figure C00003 + TABLE 16 figure C00008]`
`[SRC: CORPUS | e08 | N=1131 ATRI]`
**VERIFIED** for `V_ATR` placement and the resolution nibble.

| `V_ATR` bits | Field | Disc |
|---|---|---|
| b31–b30 | Video compression mode | `01b` MPEG-2 on most feature ATRIs — **does not match** XPL `VideoAttributeItem codec="VC-1"` on the same titles. Decoder setup must follow the playlist, not this field. |
| b29–b28 | TV system | often `10b` HD/60; some `00b` 525/60 with HD resolution (STARDUST) |
| b27–b26 | Aspect ratio | `10b` on 1920×1080 features (TABLE 9 only defines `00b` 4:3 / `11b` 16:9 — **drift**; treat `10b` as 16:9 HD) |
| b15–b12 | Source picture resolution | `1100b` 1920×1080 (677), `0101b` 720×480/576 (451), `0000b` 352×240/288 (3) |

WO2006070920A1 FIG.111 also names `AHDVTS_AST_ATR`, palettes, etc. inside ATRI.
Audio-count at +6 is **not** a small `AST_Ns` (almost always 0 or a huge junk
u16). Occupied tails exist around 229–256. Those slots stay **OPEN**.

#### `VTS_EVOBIT` body — DVD-style table, 320-byte entries
`[SRC: PATENT | WO2006070920A1 FIG.112 AHDVTS_EVOBIT | EVOBITI + EVOBI_SRP + EVOBI]`
`[SRC: CORPUS | N=119 VTI; N=2431 EVOBI]`
**VERIFIED** (arithmetic 119/119)

Header: reserved u16 @0, `nr` u16 @2, `last_byte` u32 @4, then `nr` × u32 start
offsets. First offset = `8 + 4×nr`. Each `EVOBI` is **320 bytes**.
`nr` equals the disc's `.MAP` count on 117/119 (exceptions: `PANS_LABYRINTH` 52 vs 41
maps — extra EVOBIs for interleaved angles; `ETERNAL_SUNSHINE` 28 vs 29).

| EVOBI offset | Size | Field | Observed |
|---|---|---|---|
| 0 | 2 | type/flags | `0x2000` on **2431/2431** (same constant as contiguous `TMAP_TY`) |
| 2 | 36 | EVOB filename | ASCII, NUL-padded; max observed 36 chars; **2431/2431** match a `.EVO` in that disc's listing |
| 38–263 | | reserved | always zero |
| 264 | 2 | `EVOB_ATRN` | 1-based ATRI index; **2431/2431** in `1…nr` (`e08`) |
| 266 | 4 | candidate EVOB start PTM (90 kHz) | DOWNFALL `EVOB002` `0x0000208c` = PCI `vobu_s_ptm` of VOBU0 **and** GCI bytes 4–5 |
| 270 | 4 | candidate EVOB end PTM | `FEATURE_2` start equals `FEATURE_1` end on MYSTERY_MEN / BATMAN two-part features |
| 286–301 | 16 | padded `FFh` | always `FF` — unused SA/key-sized slot |
| 302–319 | | reserved | always zero |

Patent `TMAP_FILE_NAME` is not at a located offset; disc leads with the **EVO** name.

**OPEN:** ATRI palettes (after SP_ATR); EVOBI+282 units (layer/part start, not PTM).

### Structures with NO patent table — derived from disc bytes only
All **SINGLE**. `[SRC: DISC | RESERVOIR_DOGS]` + `[SRC: DERIVED | arithmetic closure]`

| Structure | Finding | Validation |
|---|---|---|
| `TT_SRPT` | 16-byte entries (DVD 12); `VTSN`,`VTS_TTN` u8→u16 | `last_byte`=247 → 240/15 titles = 16 |
| `VTS_PGCIT` SRP | 12 bytes; `PGC_SA` at +8 | 5x12+8 = 68 = first `PGC_SA` |
| PGC header | counts u16 @0/@2; offsets @0xA8; **two** palettes @0xB0,@0xF0 | cell arithmetic closes exactly |
| `cell_playback` | 28 bytes (DVD 24) | 386 + 58x28 = 2010 = `cell_position_offset`; +58x4 = next PGC |
| `VTS_PTT_SRPT` | identical to DVD | titles have 8/13/10/9/8 PTTs; PGCs have 8/13/10/9/8 programs |
| `VTS_C_ADT` | identical to DVD | entries match `cell_playback` sector ranges |
| `VTS_EVOBU_ADMAP` | identical to DVD | ascending u32, 11871 entries |
| `VTS_TMAPT` | identical to DVD incl. bit-31 discontinuity | 5 maps, `entries x tmu` == each PGC runtime |

**OPEN in this group:** the 4 trailing `cell_playback` bytes (always zero); the second
palette's purpose (byte-identical to the first on this specimen); 2 extra varying bits
in the `playback_time` seconds byte — not frame rate, not cell category, unexplained
`[SRC: CORPUS | N=204 cells | masking gives valid BCD 204/204]`.

**Not present on the specimen, layout unconfirmed:** `PTL_MAIT`, `TXTDT_MGI`,
`VMGM_PGCI_UT` body, `VTSM_PGCI_UT` body, `VTS_ATRT` entry bodies.

### Navigation commands
**Claim:** HD DVD command word = DVD-Video command word rotated right 16 bits
(`DVD[0..5] = HD[2..7]`, `DVD[6..7] = HD[0..1]`).
`[SRC: DISC | RESERVOIR_DOGS, all 57 commands across 12 IFOs]`
`[SRC: SRCCODE | libdvdnav src/vm/vmcmd.c | vm_getbits bit positions]`
`[SRC: DERIVED | type histogram: raw = {0:57} all invalid; rotated = {1:16,2:5,3:36} = Link/Jump, SetSystem, Set]`
**SINGLE** (one disc, 57 commands)

Corroborating decodes: VMG first-play → `JumpTT 15`; feature PGC post-command →
`CallSS VTSM`; pre-command with operands `0x81 0x82` → `SetSystem op=1`.

**KNOWN WRONG:** the Set-command operand layout. Decodes `g0` for all 36 Set
commands, which is implausible. libdvdnav has three `print_set_version_*` variants;
the applicable one is unresolved. **OPEN.**

## 4. NV_PCK — see `08_NV_PCK_PCI_DSI.md`

Previously OPEN, now largely closed. EVO is MPEG-2 PS; NV_PCK is the first pack of
each EVOBU and carries three `private_stream_2` packets (substream `0x00` = PCI,
`0x01` = DSI, `0x04` = GCI_PKT). PCI and DSI follow DVD-Video's `pci_gi_t` /
`dsi_gi_t` layouts. `vobu_ea` is **relative** to the VOBU start. MAP `EVOBU_SZ`
equals `vobu_ea+1` on Advanced content (DOWNFALL 5/5). CPI offset inside GCI is
**pack `0x3C`** (`spec/advanced/09_aacs.md`). Full detail in `08`. **VERIFIED**
packet set on 3 discs.

## 5. Encryption

**Claim:** navigation files are never encrypted, on any disc.
`[SRC: CORPUS | MYSTERY_MEN, BATMAN_BEGINS, PANS_LABYRINTH | HVA00001.VTI magic reads ASCII "ADVANCED-VTS" while ANY! present]`
**VERIFIED** (3 AACS discs)

**Claim:** AACS does not encrypt the EVO container either — pack and system headers
are in the clear.
`[SRC: DISC | MYSTERY_MEN FEATURE_1.EVO vs RESERVOIR_DOGS HV001T01.EVO | first 32 bytes byte-identical except rate bound]`
`[SRC: SPEC | AACS HD DVD Pre-recorded Final 0.953 §4.3.1 | NV_PCK/ADV_PCK not encryptable; §4.3.2 Table 4-7 | 128-byte Unencrypted Portion]`
**VERIFIED** (2 discs + format book). Encrypted packs keep bytes 0–127 clear and
CBC-cover bytes 128–2047 under a Content Key, not under BD's 6144-byte Aligned Unit.
**Consequence: the entire navigation and container layer is parseable with no keys.**

**Claim:** libaacs has no HD DVD support, and `aacs_decrypt_unit` cannot be the EVO
decrypt path.
`[SRC: SRCCODE | libaacs src/libaacs/aacs.c ALIGNED_UNIT_LEN=6144, _verify_ts, aacs_decrypt_unit]`
`[SRC: SRCCODE | grep -riE "hd.?dvd|HVDVD|ANY!|VTKF|MKBROM" libaacs/src → no matches]`
`[SRC: SPEC | HD DVD Pre-recorded Final 0.953 Table 4-7 vs BD Pre-recorded 0.921 Aligned Unit]`
**VERIFIED**. MKB walk + AES-G + title-key ECB unwrap are the reusable core. See
`09_AACS.md`.

HD DVD AACS directory is **`ANY!/`** on 96 discs and **`AAC!/`** on 8, each mirrored
in `*_BAK/`. File set: `MKBROM.AACS`, `MKBRECORDABLE.AACS` (primary only — see
`09_AACS.md`), `DKF.AACS`, `VTKF###.AACS`, `VTUF###.AACS`, `CONTENT_CERT.AACS`,
`CONTENT_HASH_TABLE1/2.AACS`, `CONTENT_REVOCATION_LIST.AACS`, `MNGCPY_MANIFEST.XML`.
`[SRC: CORPUS | N=120 listings]` **VERIFIED**

Unencrypted discs exist: **16/120** have neither `ANY!` nor `AAC!` (includes
`RESERVOIR_DOGS` plus 15 Advanced discs).
`[SRC: CORPUS | N=120 listings]`

**Resolved vs OPEN:** VTKF/DKF/CERT layouts, 128/1920 pack split, `TITLE_KEY_PTR`,
and libaacs reuse boundaries are in `09_AACS.md`. Still **OPEN:** CHT bodies, VTUF
body, `ANY!`/`AAC!` vs reserved `AACS`, extra VTKF without VPLST.

## 6. Advanced Content

See `04_ADV_OBJ.md` (components) and `06_TMAP_solved.md` (`.MAP`).

Summary: `.XPL` playlists are XML, 247 files, 0 parse failures, all
`majorVersion=1 minorVersion=0`; official `Playlist.xsd` is in `spec/raw/adv_obj/`.
`.MAP` is TMAP_GI + TMAPI_SRP@384 + TMAPI(EVOBU_ENT) + ILVUI; `.ACA` container
cracked on **one** sample (298–409 on discs; not fetched by default `udfgrab.py`).
`DISCID.DAT` is `HDDVD-V_CONF`, 128 bytes, 119/119 Advanced discs. Full layout in §8.

## 7. Scope reality

**119 of 120 discs in the on-disk corpus are Advanced Content.** The patents describe
Advanced VTS as:
*"Elimination of a layered structure. No Title, no PGC, no PTT and no Cell.
No supports of Navigation Command and UOP control."*
`[SRC: PATENT | US20070091495A1 | Advanced VTS section]`
`[SRC: CORPUS | N=120 listings | 1 Category 1, 119 Category 2, 0 Category 3]`

Everything in §3 Standard Content concerns the format on **one disc**.

## 8. `DISCID.DAT` — Config File

`[SRC: CORPUS | N=119 ADV_OBJ/DISCID.DAT, all 128 bytes]`
`[SRC: PATENT | US20070091495A1 | Playlist Manager reads PROVIDER_ID, CONTENT_ID, SEARCH_FLG]`
`[SRC: TOOL | Scenarist_AC_4.5_UserGuide.txt p.114 | "The Config File is called DISCID.DAT"]`
**VERIFIED**

| Offset | Size | Field | Observed |
|---|---|---|---|
| 0 | 12 | ID | `HDDVD-V_CONF` (119/119) |
| 12 | 16 | Disc ID (network) | `FFh`×16 on 109; a UUID on 10 |
| 28 | 16 | `PROVIDER_ID` | ASCII studio tag, or 16-byte binary |
| 44 | 16 | `CONTENT_ID` | 16-byte UUID |
| 60 | 1 | `SEARCH_FLG` | 0 on 106, 1 on 13 |
| 61–127 | | reserved | zeros |

`SEARCH_FLG=0` means the player also searches persistent storage for `VPLST$$$.XPL` /
`APLST###.XPL` under that provider/content; `1` skips that step (patent, verbatim).
Studio tags seen: `WHV***V1**HD-DVD` (25), `UNIVERSAL_HD-DVD` (22),
`UNIVERSAL_HD-SLY` (18), `PARAMOUNT_HD-DVD` (12), `PARAMOUNT_HD-SLY` (8),
`WHV***V1**HD-SLY` (7), plus `NEWLINE_HDDVD_V1`, `DREAMWORKS_HDDVD`, `DW_ANIM___HD-SLY`,
and 24 binary/UUID providers.

Absent on `RESERVOIR_DOGS` (no `ADV_OBJ/`).
