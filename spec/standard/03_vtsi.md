# S3. `STANDARD-VTS`: Video Title Set (VTSI)

*Values are from `RESERVOIR_DOGS` VTS IFOs (`HVnnnI01.IFO`) [11]. VTSI_MAT is
corroborated by the patent RBP table [2].*

A Video Title Set groups titles that share attributes. Its info file `HVnnnI01.IFO` has
ID `STANDARD-VTS`. All fields are big-endian.

## 3.1 VTSI_MAT: Management Attribute Table

The patent RBP table and the disc agree on every field. `[SRC: PATENT | US20080298219A1
VTSI_MAT RBP table]` `[11]` **VERIFIED**. The pointer block sits at RBP 192 (0xC0),
where DVD-Video has it at 0x88, a shift of 0x38. Values below are from the feature VTS
`HV001I01.IFO`.

| RBP | Field | Specimen | Check |
|---|---|---|---|
| 0 | `VTS_ID` | `STANDARD-VTS` | |
| 12 | `VTS_EA` | 9851994 | end address in sectors |
| 28 | `VTSI_EA` | 49 | VTSI occupies 50 sectors |
| 32 | `VERN` | 0x0010 | specification 1.0 |
| 128 | `VTSI_MAT_EA` | 2047 | |
| 192 | `VTSM_EVOBS_SA` | 50 | equals VTSI_EA + 1 |
| 196 | `VTSTT_EVOBS_SA` | 275 | equals 50 + 225 (menu object size) |
| 200 | `VTS_PTT_SRPT_SA` | 1 | Part-of-Title search pointer table |
| 204 | `VTS_PGCIT_SA` | 2 | PGC info table |
| 212 | `VTS_TMAPT_SA` | 7 | time map table |
| 224 | `VTS_C_ADT_SA` | 25 | cell address table |
| 228 | `VTS_EVOBU_ADMAP_SA` | 26 | VOBU address map |
| 532 | `VTS_V_ATR` | 4 bytes | DVD has 2 |
| 536 | `VTS_AST_N` | 6 | number of audio streams |
| 538 | `VTS_AST_ATRT` | 8 x 8 B | audio attributes; languages `en` |
| 602 | `VTS_SPST_N` | 5 | number of sub-picture streams |
| 604 | `VTS_SPST_ATRT` | 32 x 6 B | sub-picture attributes; languages `nl` |
| 798 | `VTS_MU_AST_ATRT` | 8 x 8 B | multichannel audio attributes |

Cross-checks `[11]`: `VTS_AST_N=6` equals the count of non-zero `audio_control` entries
in the PGC; `VTS_SPST_N=5` equals the non-zero `subp_control` entries; the `nl`
sub-picture language matches a Benelux (PAL) release. **VERIFIED**.

The attribute widths (`V_ATR` 4 B, audio 8 B, sub-picture 6 B) match the Advanced `ATRI`
encodings in [Advanced §6](../advanced/06_vti.md). Standard and Advanced share the
stream-attribute vocabulary even though their containers differ.

## 3.2 VTS_PTT_SRPT: Part-of-Title Search Pointer Table

Identical to DVD-Video. `[11]` **SINGLE**. Header (`nr_of_srps` u16, reserved u16,
`last_byte` u32), then u32 offsets, then 4-byte PTT entries (`pgcn` u16, `pgn` u16). It
cross-validates: titles 1 through 5 have 8, 13, 10, 9, and 8 PTTs, and PGCs 1 through 5
have exactly 8, 13, 10, 9, and 8 programs. **VERIFIED** internally.

## 3.3 VTS_PGCIT: PGC Information Table (12-byte SRP)

The header is DVD-compatible (`nr_of_srps` u16 at 0, reserved u16 at 2, `last_byte`
u32 at 4). The SRP widened from 8 to 12 bytes. `[11]` **SINGLE**.

| Offset | Size | Field | DVD |
|---|---|---|---|
| 0x00 | 4 | `PGC_CAT` | 4 |
| 0x04 | 4 | reserved | new |
| 0x08 | 4 | `PGC_SA` (byte offset from PGCIT start) | 4 |

Self-validating: 5 SRPs at 12 B plus an 8 B header is 68, which equals the first
`PGC_SA`. The PGC bodies these point at are specified in [§4](04_pgc_vm.md).

## 3.4 VTS_TMAPT: Time Map Table (identical to DVD-Video)

`[11]` **VERIFIED** (fully cross-validated on all five maps). Header (`nr_of_tmaps` u16,
reserved u16, `last_byte` u32), u32 offsets, then per map: `tmu` u8 (seconds per entry),
reserved u8, `nr_of_entries` u16, then u32 entries where bit 31 marks a discontinuity,
exactly as in DVD. No HD DVD-specific time map was needed for Standard Content. The
standalone `.MAP` files on Advanced discs are a different structure
([Advanced §7](../advanced/07_map.md)).

| Map | tmu | entries | entries x tmu | PGC playback |
|---|---|---|---|---|
| 1 | 3 s | 1980 | 5940 s (99 m) | 5942 s |
| 2 | 2 s | 1057 | 2114 s (35 m) | 2114 s |
| 3 | 1 s | 1401 | 1401 s (23 m) | 1401 s |
| 4 | 1 s | 1601 | 1601 s (26 m) | 1561 s |
| 5 | 3 s | 1980 | 5940 s (99 m) | 5942 s |

Duration equals entries times tmu, and it matches the PGC playback time (99 minutes is
Reservoir Dogs' runtime). That semantic cross-check confirms the layout.

## 3.5 VTS_C_ADT and VTS_EVOBU_ADMAP (identical to DVD-Video)

`[11]` **SINGLE** (identical to DVD).

- `VTS_C_ADT`, the cell address table: `nr_of_vobs` u16, reserved, `last_byte` u32, then
  12-byte entries (`vob_id` u16, `cell_id` u16, `start_sector` u32, `last_sector` u32).
  Entries match `cell_playback` exactly (cell 1 is 0 through 9833, cell 2 is 9834
  through 10153, and so on).
- `VTS_EVOBU_ADMAP`, the EVOBU address map: `last_byte` u32 then ascending u32 VOBU
  start sectors, with 11 871 entries on the feature VTS.

The same `C_ADT` and `EVOBU_ADMAP` shape is reused for the VMG and VTS menu objects
(`VMGM_C_ADT`, `VTSM_C_ADT`, and the HD-DVD-new `FP_PGCM_C_ADT`).

## 3.6 VTS menu tables (patent only)

The VTS info also carries a menu program-chain unit table `HDVTSM_PGCI_UT` and menu
cell and VOBU-map tables (`HDVTSM_C_ADT`, `HDVTSM_VOBU_ADMAP`), FIG.20 [3]. The menu-PGC
category byte layout `HDVTSM_PGC_CAT` is in FIG.27 [3] (entry type, block mode and type,
audio-info selection, `PTL_ID_FLD`). These govern the VTS menu. Their bodies were not
decoded on the specimen, since the `HV009` and `HV010` menus were not dumped, so they
are **OPEN**.
