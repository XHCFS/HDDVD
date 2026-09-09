# S3. `STANDARD-VTS` — Video Title Set (VTSI)

*From `RESERVOIR_DOGS` VTS IFOs (`HVnnnI01.IFO`) [11]; VTSI_MAT corroborated by the
patent RBP table [2].*

A Video Title Set groups titles that share attributes. Its info file `HVnnnI01.IFO`
has ID `STANDARD-VTS`. All big-endian.

## 3.1 VTSI_MAT — Management Attribute Table

`[SRC: PATENT | US20080298219A1 VTSI_MAT RBP table]` + `[11]` **VERIFIED** — agree on
every field. The pointer block sits at RBP 192 (0xC0); DVD-Video has it at 0x88 (shift
+0x38). Values below are from the feature VTS `HV001I01.IFO`.

| RBP | Field | Specimen | Check |
|---|---|---|---|
| 0 | `VTS_ID` | `STANDARD-VTS` | |
| 12 | `VTS_EA` | 9851994 | end address (sectors) |
| 28 | `VTSI_EA` | 49 | VTSI is 50 sectors |
| 32 | `VERN` | 0x0010 | spec 1.0 |
| 128 | `VTSI_MAT_EA` | 2047 | |
| 192 | `VTSM_EVOBS_SA` | 50 | = VTSI_EA+1 |
| 196 | `VTSTT_EVOBS_SA` | 275 | = 50 + 225 (`HV001M01.EVO` menu size) |
| 200 | `VTS_PTT_SRPT_SA` | 1 | Part-of-Title search pointer table |
| 204 | `VTS_PGCIT_SA` | 2 | PGC info table |
| 212 | `VTS_TMAPT_SA` | 7 | time map table |
| 224 | `VTS_C_ADT_SA` | 25 | cell address table |
| 228 | `VTS_EVOBU_ADMAP_SA` | 26 | VOBU address map |
| 532 | `VTS_V_ATR` | 4 bytes | **DVD has 2** — see [§5.5](05_evob_nv.md) / [Advanced §8.8] palette note |
| 536 | `VTS_AST_N` | 6 | number of audio streams |
| 538 | `VTS_AST_ATRT` | 8 × 8 B | audio attributes; langs `en` |
| 602 | `VTS_SPST_N` | 5 | number of sub-picture streams |
| 604 | `VTS_SPST_ATRT` | 32 × 6 B | sub-picture attributes; langs `nl` |
| 798 | `VTS_MU_AST_ATRT` | 8 × 8 B | multichannel audio attributes |

Cross-checks `[11]`: `VTS_AST_N=6` equals the count of non-zero `audio_control`
entries in the PGC; `VTS_SPST_N=5` equals the non-zero `subp_control` entries; the
`nl` sub-picture language is consistent with a Benelux (PAL) release. **VERIFIED**.

The attribute widths (`V_ATR` 4 B, audio 8 B, SP 6 B) match the Advanced `ATRI`
attribute encodings analysed in [Advanced §6](../advanced/06_vti.md) — Standard and
Advanced share the stream-attribute vocabulary even though their containers differ.

## 3.2 VTS_PTT_SRPT — Part-of-Title Search Pointer Table

Identical to DVD-Video. `[11]` **SINGLE** (found identical). Header (`nr_of_srps` u16,
reserved u16, `last_byte` u32); u32 offsets; PTT entries 4 B (`pgcn` u16, `pgn` u16).
Cross-validates: titles 1–5 have 8/13/10/9/8 PTTs, and PGCs 1–5 have exactly
8/13/10/9/8 programs. **VERIFIED** internally.

## 3.3 VTS_PGCIT — PGC Information Table (12-byte SRP)

Header DVD-compatible (`nr_of_srps` u16 @0, reserved u16 @2, `last_byte` u32 @4). SRP
widened 8→12: `[11]` **SINGLE**.

| Offset | Size | Field | DVD |
|---|---|---|---|
| 0x00 | 4 | `PGC_CAT` | 4 |
| 0x04 | 4 | reserved | **new** |
| 0x08 | 4 | `PGC_SA` (byte offset from PGCIT start) | 4 |

Self-validating: 5 SRPs × 12 B + 8 B header = 68 = the first `PGC_SA`. The PGC bodies
these point at are specified in [§4](04_pgc_vm.md).

## 3.4 VTS_TMAPT — Time Map Table (identical to DVD-Video)

`[11]` **VERIFIED** (fully cross-validated on all five maps). Header (`nr_of_tmaps` u16,
reserved u16, `last_byte` u32), u32 offsets, then per map: `tmu` u8 (seconds/entry),
reserved u8, `nr_of_entries` u16, then u32 entries with **bit 31 = discontinuity** —
exactly as DVD. **No HD DVD-specific TMAP was needed for Standard Content** (the `.MAP`
files on Advanced discs are a different structure — [Advanced §7](../advanced/07_map.md)).

| map | tmu | entries | entries×tmu | PGC playback |
|---|---|---|---|---|
| 1 | 3 s | 1980 | 5940 s (99 m) | 5942 s |
| 2 | 2 s | 1057 | 2114 s (35 m) | 2114 s |
| 3 | 1 s | 1401 | 1401 s (23 m) | 1401 s |
| 4 | 1 s | 1601 | 1601 s (26 m) | 1561 s |
| 5 | 3 s | 1980 | 5940 s (99 m) | 5942 s |

Duration `= entries × tmu` matching the PGC playback time (99 min = Reservoir Dogs'
runtime) is the semantic cross-check that the layout is right.

## 3.5 VTS_C_ADT and VTS_EVOBU_ADMAP (identical to DVD-Video)

`[11]` **SINGLE** (identical to DVD).

- **`VTS_C_ADT`** (cell address table): `nr_of_vobs` u16, reserved, `last_byte` u32,
  then 12-byte entries (`vob_id` u16, `cell_id` u16, `start_sector` u32,
  `last_sector` u32). Entries match `cell_playback` exactly (cell 1 = 0..9833,
  cell 2 = 9834..10153, …).
- **`VTS_EVOBU_ADMAP`** (EVOBU address map): `last_byte` u32 then ascending u32 VOBU
  start sectors. 11 871 entries on the feature VTS.

The same `C_ADT` / `EVOBU_ADMAP` shape is reused for the VMG and VTS **menu** objects
(`VMGM_C_ADT`, `VTSM_C_ADT`, and the HD-DVD-new `FP_PGCM_C_ADT`).

## 3.6 What the patent adds for VTS menus

The VTS info also carries a menu program-chain unit table `HDVTSM_PGCI_UT` and menu
cell/VOBU-map tables (`HDVTSM_C_ADT`, `HDVTSM_VOBU_ADMAP`), FIG.20 [3]. The menu PGC
category byte layout `HDVTSM_PGC_CAT` is given in FIG.27 [3] (entry type, block
mode/type, audio-info selection, `PTL_ID_FLD`). These govern the VTS menu; their
**bodies were not decoded** on the specimen (the specimen's `HV009`/`HV010` menus were
not dumped) — **OPEN**.
