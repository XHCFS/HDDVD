# S2. `HVDVD-VMG100` — Video Manager (VMGI)

*Byte-level claims are from `RESERVOIR_DOGS` `/HVDVD_TS/HV000I01.IFO` (20 480 B) [11]
unless a patent RBP table [2] corroborates; grades noted per section.*

The Video Manager is the disc-level index: one per disc, at `HV000I01.IFO`. Its ID
string is `HVDVD-VMG100` (cf. DVD's `DVDVIDEO-VMG`). All big-endian.

## 2.1 VMGI_MAT — Management Attribute Table

`[SRC: PATENT | US20080298219A1 VMGI_MAT RBP table]` + `[11]` **VERIFIED** — patent and
disc agree field-for-field. RBP 0–215 is byte-compatible with DVD-Video; **HD DVD
inserts two fields at RBP 216/220** and shifts the last two pointers.

| RBP | Field | Specimen | Notes |
|---|---|---|---|
| 0 | `VMG_ID` | `HVDVD-VMG100` | 12 ASCII |
| 12 | `VMG_EA` | 169536 | end address (sectors); VTS#1 starts at +1 |
| 28 | `VMGI_EA` | 9 | VMGI is 10 sectors |
| 32 | `VERN` | 0x0010 | spec 1.0 |
| 34 | `VMG_CAT` | 0 | region/category mask |
| 62 | `VTS_N` | 11 | matches 11 VTS files |
| 128 | `VMGI_MAT_EA` | 1479 | end of this table |
| 132 | `FP_PGCI_SA` | 1158 | first-play PGC (byte offset) |
| 192 | `VMGM_EVOBS_SA` | 10 | first sector after VMGI |
| 196 | `TT_SRPT_SA` | 1 | Title Search Pointer Table (sector) |
| 200 | `VMGM_PGCI_UT_SA` | 2 | menu PGC unit table (body **OPEN**) |
| 204 | `PTL_MAIT_SA` | 0 | parental mgmt — absent here |
| 208 | `VTS_ATRT_SA` | 3 | VTS attribute table (`nr_of_vtss`=11) |
| 212 | `TXTDT_MG_SA` | 0 | text data manager — absent here |
| 216 | **`FP_PGCM_C_ADT_SA`** | 0 | **new in HD DVD** — first-play menu cell address table |
| 220 | **`FP_PGCM_EVOBU_ADMAP_SA`** | 0 | **new in HD DVD** — first-play menu VOBU map |
| 224 | `VMGM_C_ADT_SA` | 8 | (DVD had this at 0xD8) |
| 228 | `VMGM_EVOBU_ADMAP_SA` | 9 | (DVD had this at 0xDC) |

**Implementation note.** A DVD `ifoRead_VMGI_MAT()` port needs (a) the new ID constant,
and (b) the two inserted `u32` fields at RBP 216/220, which push `VMGM_C_ADT`/
`VMGM_EVOBU_ADMAP` to 224/228. Reading DVD's 0xD8/0xDC yields the inserted (here zero)
fields and silently mis-parses. The patent table covers this region and is the correct
reference — not DVD-Video. `[2]` `[11]`

## 2.2 TT_SRPT — Title Search Pointer Table (16-byte entries)

**No patent RBP table exists**; derived from disc bytes by arithmetic closure. `[11]`
`[SRC: DERIVED | header last_byte=247 → 240 data bytes / 15 titles = 16-byte stride]`
**SINGLE**. Header is DVD-compatible (`nr_of_srps` u16 @0, `last_byte` u32 @4).

| Offset | Size | Field | DVD-Video |
|---|---|---|---|
| 0x00 | 1 | `TT_PB_TY` playback type | same |
| 0x01 | 1 | number of angles | same |
| 0x02 | 2 | number of PTTs (parts of title) | same |
| 0x04 | 2 | parental management mask | same |
| 0x06 | 2 | reserved | **new** |
| 0x08 | 2 | `VTSN` (title set number) | u8 @0x06 in DVD |
| 0x0A | 2 | `VTS_TTN` (title number within VTS) | u8 @0x07 in DVD |
| 0x0C | 4 | VTS start sector | u32 @0x08 in DVD |

**Why it widened (12→16).** The spec allows up to 511 VTS [1], which does not fit in a
byte, so `VTSN`/`VTS_TTN` become `u16`; with 2 reserved bytes that accounts for all 4
extra bytes. Every widening in Standard Content follows this pattern — fields grow
exactly where DVD's limits were raised.

Decoded specimen (15 titles) `[11]`:
```
t1..t5    VTSN=1,     VTS_TTN=1..5,  start=169537   (= VMG_EA + 1)
t6        VTSN=2,     VTS_TTN=1
t7        VTSN=3,     VTS_TTN=1
t8..t15   VTSN=4..11, VTS_TTN=1      ascending
```
All 15 have `TT_PB_TY=0x14` (one sequential PGC) and 1 angle. Title 1 beginning at
exactly `VMG_EA + 1` is the cross-check that the 16-byte stride is correct.

## 2.3 First-play PGC and VMG menus

- **`FP_PGCI`** (RBP 132 → byte 1158) is the first-play program chain — what runs on
  insert before any title. On the specimen its command decodes as **`JumpTT 15`**
  (§4), i.e. jump to title 15, which maps via TT_SRPT to VTSN=11, the last VTS — a
  warning/logo clip. `[11]` **SINGLE**.
- **`VMGM_PGCI_UT`** (RBP 200) is the VMG menu program-chain unit table (by language).
  Its body was **not decoded** — the menu-PGC unit-table layout is **OPEN**. Structure
  from patent [3] FIG.6/7 (`HDVMGM_PGCI_UT` → `HDVMGM_LU` → per-language PGCI), byte
  offsets unconfirmed.
- **`VMGM_C_ADT`** / **`VMGM_EVOBU_ADMAP`** (RBP 224/228) address the VMG menu object
  (`HV000M02.EVO`); same shape as DVD's `VMGM_C_ADT`/`VMGM_VOBU_ADMAP` ([§3.5](03_vtsi.md)).

## 2.4 Tables absent on the specimen (layout from patent only)

`PTL_MAIT_SA=0` and `TXTDT_MG_SA=0` — parental management and text-data manager are not
present on `RESERVOIR_DOGS`, so their on-disc layout is unconfirmed. Patent structures:

- **`PTL_MAIT`** — parental management (FIG.9/10 [3]): `PTL_MAITI` header (`CTY_Ns`
  countries, `HDVTS_Ns`, `EA`), then per-country `PTL_MAI_SRP` (`CTY_CD` country code,
  `SA`), then `PTL_MAI`/`PTL_LVLI` giving a `PTL_ID_FLD` per level per VMG/VTS.
- **`TXTDT_MG`** — text data manager (FIG.12–14 [3]): `TXTDT_MGI` (`TXTDT_ID`,
  `TXTDT_LU_Ns`, `EA`), language units `TXTDT_LU` with a character-set code, then
  per-title/volume `IT_TXT` item text. This is DVD's `TXTDT_MG` widened.
- **`VTS_ATRT`** — VTS attribute table (FIG.11 [3]): `HDVTS_ATRTI` header + per-VTS
  `HDVTS_ATR_SRP` + `HDVTS_ATR` (category + attribute block). Header reports
  `nr_of_vtss=11` on the specimen; entry **bodies OPEN**.

All three are graded **OPEN** (no specimen; patent structure only).
