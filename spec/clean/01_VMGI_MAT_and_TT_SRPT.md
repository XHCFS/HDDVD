# `HVDVD-VMG100` — VMGI_MAT and TT_SRPT

Standard Content video manager. Provenance per `EVIDENCE_STANDARD.md`.

**Specimen:** `RESERVOIR_DOGS`, `/HVDVD_TS/HV000I01.IFO`, 20480 bytes.
The only Category 1 disc in 120 surveyed `[SRC: CORPUS | N=120 | tools/udfgrab.py --list]`.
Unencrypted — no `ANY!` directory, IFO is plaintext
`[SRC: DISC | RESERVOIR_DOGS _listing.txt | no ANY! entry]`.
Authored with Scenarist SCA 4.2 `[SRC: TOOL | udfclient | implementation id "*Sonic ScenaristSCA42"]`.
All fields big-endian, as DVD-Video.

## VMGI_MAT

`[SRC: PATENT | US20080298219A1 | VMGI_MAT RBP table]` + `[SRC: DISC | RESERVOIR_DOGS HV000I01.IFO]`
**VERIFIED** — patent and disc agree.

| RBP | Field | Value | Cross-check |
|---|---|---|---|
| 0 | `VMG_ID` | `HVDVD-VMG100` | vs DVD's `DVDVIDEO-VMG` |
| 12 | `VMG_EA` | 169536 | VTS#1 starts at 169537 |
| 28 | `VMGI_EA` | 9 | file is exactly 10 sectors |
| 32 | `VERN` | 0x0010 | matches TMAP `VERN` |
| 34 | `VMG_CAT` | 0 | |
| 62 | `VTS_N` | 11 | disc has exactly 11 VTS files |
| 128 | `VMGI_MAT_EA` | 1479 | |
| 132 | `FP_PGCI_SA` | 1158 | < `VMGI_MAT_EA` |
| 192 | `VMGM_EVOBS_SA` | 10 | first sector after VMGI |
| 196 | `TT_SRPT_SA` | 1 | valid table found there |
| 200 | `VMGM_PGCI_UT_SA` | 2 | body **not decoded** |
| 204 | `PTL_MAIT_SA` | 0 | absent on this disc |
| 208 | `VTS_ATRT_SA` | 3 | table reports `nr_of_vtss`=11 |
| 212 | `TXTDT_MG_SA` | 0 | absent |
| 216 | **`FP_PGCM_C_ADT_SA`** | 0 | **new in HD DVD** |
| 220 | **`FP_PGCM_EVOBU_ADMAP_SA`** | 0 | **new in HD DVD** |
| 224 | `VMGM_C_ADT_SA` | 8 | DVD has this at 0xD8 |
| 228 | `VMGM_EVOBU_ADMAP_SA` | 9 | DVD has this at 0xDC |

### Correction (2026-09-08)

An earlier version of this file claimed VMGI_MAT was **byte-identical to DVD-Video**.
That was wrong. HD DVD inserts `FP_PGCM_C_ADT_SA` and `FP_PGCM_EVOBU_ADMAP_SA` at
RBP 216/220 — cell address table and VOBU map for the *first-play menu*, which DVD has
no equivalent of. This shifts `VMGM_C_ADT` and `VMGM_EVOBU_ADMAP` to RBP 224/228.

Cause of the error: the DVD offsets 0xD8/0xDC were read, found to be zero, and recorded
as "absent". The real fields are at 0xE0/0xE4 and read 8 and 9.
`[SRC: DISC | RESERVOIR_DOGS HV000I01.IFO @0xE0,0xE4 | raw: ...00 00 00 08 00 00 00 09]`

The patent had this right. The check should have been against the patent table, which
covers this region, not against DVD-Video.

**Consequence:** `ifoRead_VMGI_MAT()` needs the new ID string **and** the two inserted
fields. RBP 0-215 matches DVD-Video; 216 onward does not.

## TT_SRPT — 16-byte entries (DVD: 12)

**No patent table exists for TT_SRPT.** Derived from disc bytes.
`[SRC: DISC | RESERVOIR_DOGS HV000I01.IFO sector 1]`
`[SRC: DERIVED | arithmetic: header says last_byte=247 -> 240 data bytes / 15 titles = 16-byte stride]`
**SINGLE**

Header is DVD-compatible: `nr_of_srps` u16 @0, `last_byte` u32 @4.

| Offset | Size | Field | DVD-Video |
|---|---|---|---|
| 0x00 | 1 | `TT_PB_TY` playback type | same |
| 0x01 | 1 | number of angles | same |
| 0x02 | 2 | number of PTTs | same |
| 0x04 | 2 | parental management mask | same |
| 0x06 | 2 | reserved | **new** |
| 0x08 | 2 | `VTSN` | 1 byte @0x06 |
| 0x0A | 2 | `VTS_TTN` | 1 byte @0x07 |
| 0x0C | 4 | VTS start sector | 4 bytes @0x08 |

**Why it widened:** the spec permits up to 511 VTS
`[SRC: PATENT | US20070091495A1 | "at least 1 with maximum 511 Video Title Set"]`,
which does not fit in DVD's single byte. Widening `VTSN`/`VTS_TTN` to u16 plus 2
reserved bytes accounts for all 4 extra bytes.

### Decoded specimen — 15 titles across 11 VTS
`[SRC: DISC | RESERVOIR_DOGS HV000I01.IFO sector 1]`
```
t1..t5    VTSN=1,     VTS_TTN=1..5,  start=169537   (= VMG_EA + 1)
t6        VTSN=2,     VTS_TTN=1,     start=0x0098e89c
t7        VTSN=3,     VTS_TTN=1,     start=0x00998c40
t8..t15   VTSN=4..11, VTS_TTN=1,     ascending
```
All 15 have `TT_PB_TY`=0x14 (one sequential PGC title) and 1 angle.
Title 1 starting at exactly `VMG_EA + 1` is the cross-check that the stride is right.

## Implications for libdvdread

- `vmgi_mat_t`: new ID constant, plus two inserted u32 fields at RBP 216/220.
- `title_info_t`: `title_set_nr` and `vts_ttn` widened to `uint16_t`, plus 2 reserved.
- `TT_SRPT` reader stride 12 -> 16.
- VTS arrays sized 99 must grow to 511 `[SRC: PATENT | US20070091495A1]` — **INFERRED**,
  highest VTS number actually observed is 11.

## Not decoded

`VMGM_PGCI_UT` body (sector 2) — required for menus. `VTS_ATRT` entry bodies beyond
the header. `PTL_MAIT` and `TXTDT_MGI` absent on this specimen, layout unconfirmed.
