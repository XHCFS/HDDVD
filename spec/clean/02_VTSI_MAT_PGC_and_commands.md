# `STANDARD-VTS` — VTSI_MAT, VTS_PGCIT, PGC, and the command set

Provenance per `EVIDENCE_STANDARD.md`.

**Specimen:** `RESERVOIR_DOGS`, 11 VTS IFOs + VMG. The only Category 1 disc in 120
surveyed `[SRC: CORPUS | N=120]`. Unencrypted, big-endian.

**Everything in this file rests on ONE disc.** Claims marked SINGLE could be artifacts
of Sonic Scenarist SCA 4.2 rather than format properties.

Source key for the sections below:
- `VTSI_MAT` — `[SRC: PATENT | US20080298219A1 VTSI_MAT RBP table]` + `[SRC: DISC | RESERVOIR_DOGS HV001I01.IFO]` **VERIFIED** (both agree)
- `VTS_PGCIT`, PGC, `cell_playback`, commands — **no patent table exists**;
  `[SRC: DISC | RESERVOIR_DOGS]` + `[SRC: DERIVED | arithmetic closure / chain validation]` **SINGLE**
- `VTS_PTT_SRPT`, `VTS_C_ADT`, `VTS_EVOBU_ADMAP`, `VTS_TMAPT` — `[SRC: DISC | RESERVOIR_DOGS]`,
  found identical to DVD-Video **SINGLE**
- Command rotation — `[SRC: DISC | RESERVOIR_DOGS, 57 commands across 12 IFOs]` +
  `[SRC: SRCCODE | libdvdnav src/vm/vmcmd.c]` **SINGLE**

---

Every offset below was read from real bytes and cross-checked for internal consistency.

## VTSI_MAT — patent RBP tables match the disc exactly

`VTS_ID` = `STANDARD-VTS`. Patent `US20080298219A1` and the disc agree on every field:

| RBP | Field | Disc value | Check |
|---|---|---|---|
| 0 | VTS_ID | `STANDARD-VTS` | |
| 12 | VTS_EA | 9851994 | |
| 28 | VTSI_EA | 49 | file is exactly 50 sectors ✓ |
| 128 | VTSI_MAT_EA | 2047 | |
| 192 | VTSM_EVOBS_SA | 50 | = VTSI_EA+1 ✓ |
| 196 | VTSTT_EVOBS_SA | 275 | = 50 + 225 (`HV001M01.EVO`) ✓ |
| 200 | VTS_PTT_SRPT_SA | 1 | |
| 204 | VTS_PGCIT_SA | 2 | valid table found ✓ |
| 212 | VTS_TMAPT_SA | 7 | |
| 224 | VTS_C_ADT_SA | 25 | |
| 228 | VTS_EVOBU_ADMAP_SA | 26 | |
| 532 | VTS_V_ATR | 4 bytes | **DVD has 2** |
| 536 | VTS_AST_N | 6 | |
| 538 | VTS_AST_ATRT | 8 x 8 B | langs all `en` ✓ |
| 602 | VTS_SPST_N | 5 | |
| 604 | VTS_SPST_ATRT | 32 x 6 B | langs all `nl` ✓ |
| 798 | VTS_MU_AST_ATRT | 8 x 8 B | |

The whole pointer block sits at RBP 192 (0xC0); DVD-Video has it at 0x88. Shift +0x38.

## VTS_PGCIT — SRP is 12 bytes (DVD: 8)

Header is DVD-compatible: `nr_of_srps` u16 @0, reserved u16 @2, `last_byte` u32 @4.

| Offset | Size | Field |
|---|---|---|
| 0x00 | 4 | PGC_CAT |
| 0x04 | 4 | reserved (**new**) |
| 0x08 | 4 | PGC_SA (byte offset from PGCIT start) |

Self-validating: 5 SRPs x 12 B + 8 B header = 68, and the first `PGC_SA` is exactly 68.

## PGC — offsets moved ahead of the palettes, and there are TWO palettes

| Offset | Size | Field | vs DVD |
|---|---|---|---|
| 0x00 | 2 | nr_of_programs | u8 @0x02 |
| 0x02 | 2 | nr_of_cells | u8 @0x03 |
| 0x04 | 4 | playback_time | same |
| 0x08 | 4 | prohibited_ops | same |
| 0x0C | 16 | audio_control[8] (u16) | same |
| 0x1C | 128 | subp_control[32] (u32) | same |
| 0x9C | 2 | next_pgc_nr | same |
| 0x9E | 2 | prev_pgc_nr | same |
| 0xA0 | 2 | goup_pgc_nr | same |
| 0xA2 | 1 | pg_playback_mode | same |
| 0xA3 | 1 | still_time | same |
| 0xA4 | 4 | reserved | **new** |
| 0xA8 | 2 | command_tbl_offset | DVD @0xE4 |
| 0xAA | 2 | program_map_offset | DVD @0xE6 |
| 0xAC | 2 | cell_playback_offset | DVD @0xE8 |
| 0xAE | 2 | cell_position_offset | DVD @0xEA |
| 0xB0 | 64 | **palette #1** (16 x u32) | DVD @0xA4 |
| 0xF0 | 64 | **palette #2** (16 x u32) | **DVD has only one** |

Both palettes were byte-identical on this specimen — purpose unconfirmed (likely
SD/HD or 4:3/16:9 variants). Do not assume they always match.

Arithmetic closes exactly on PGC 1: `cell_playback` 386 + 58 cells x **28 B** = 2010
= `cell_position_offset`; 2010 + 58 x 4 = 2242 = next PGC start.
**cell_playback is 28 bytes (DVD: 24); cell_position stays 4.**

`audio_control` had exactly 6 non-zero entries (= VTS_AST_N) and `subp_control`
exactly 5 (= VTS_SPST_N).

## Navigation commands — DVD-Video VM, rotated 16 bits

Command table header is DVD-shaped (`nr_pre`, `nr_post`, `nr_cell`, `last_byte` as u16),
commands are 8 bytes as in DVD.

Across all **57 commands** on the disc, `bytes[0]` is always `0x00`, so the DVD type
field (top 3 bits of byte 0) yields type 0 for everything — meaningless. The type
field is at **byte[2]**.

**HD DVD command word = DVD-Video command word rotated right 16 bits.**
```
DVD[0..5] = HD[2..7]      DVD[6..7] = HD[0..1]
```

Decoded with libdvdnav's own bit positions (`src/vm/vmcmd.c`):

| | raw bytes | rotated |
|---|---|---|
| type histogram | `{0: 57}` — all invalid | `{1:16, 2:5, 3:36}` = Link/Jump, SetSystem, Set |

Semantics come out coherent:

| Source | Bytes | Decodes as |
|---|---|---|
| VMG first-play | `00 11 30 02 00 00 00 0f` | **JumpTT 15** |
| VTS1 PGC1 post | `00 00 30 08 00 00 00 92` | **CallSS VTSM** (call VTS menu) |
| VTS1 PGC1 pre | `00 00 41 00 00 81 82 00` | **SetSystem op=1** (audio/subp/angle); operands `0x81 0x82` are stream selectors |
| various pre | `00 00 71 00 00 0a 00 00` | Set GPRM, immediate 10 |

A first-play that jumps to a title, and a feature PGC whose post-command calls the
VTS menu, are exactly the expected shapes. Title 15 maps via TT_SRPT to VTSN=11 —
the last VTS, consistent with a warning/logo clip.

**This collapses gap #2 of the analysis.** libdvdnav's `vmcmd.c` and the VM itself
are reusable; the adapter is a 16-bit rotation at command load.

### Caveat
The GPRM register field decoded as `g0` for every Set command, which is implausible —
libdvdnav has three `print_set_version_*` variants with different register bit
positions and the right one is not yet established. The *type* dispatch is solid;
the Set operand layout needs refinement against more specimens.

Single specimen. Everything here needs confirming on a second Standard Content disc.

---

# Addendum: PTT_SRPT, cell_playback, C_ADT, EVOBU_ADMAP, TMAPT

## VTS_PTT_SRPT — identical to DVD-Video
Header `nr_of_srps` u16, reserved u16, `last_byte` u32; then u32 offsets; PTT entries
4 B (`pgcn` u16, `pgn` u16). Cross-validates perfectly: titles 1-5 have
8/13/10/9/8 PTTs, and PGCs 1-5 have exactly 8/13/10/9/8 programs.

## cell_playback — 28 bytes (DVD: 24)
DVD's 24-byte layout holds, with **4 trailing bytes** added (zero on this specimen):

| Offset | Size | Field |
|---|---|---|
| 0x00 | 2 | cell category / flags |
| 0x02 | 1 | still_time |
| 0x03 | 1 | cell_cmd_nr |
| 0x04 | 4 | playback_time |
| 0x08 | 4 | first_sector |
| 0x0C | 4 | first_ilvu_end_sector |
| 0x10 | 4 | last_vobu_start_sector |
| 0x14 | 4 | last_sector |
| 0x18 | 4 | **reserved (new)** |

Verified by chaining: every cell's `first_sector` equals the previous cell's
`last_sector + 1`, across all 204 cells.

### playback_time — one unresolved detail
Format is DVD's BCD `hour, minute, second, frame`. The frame byte's top 2 bits are
`0b10` (25 fps) in **all 204 cells** — DVD's frame-rate encoding, consistent with a
PAL release. But the **seconds byte also carries 2 varying bits** (`0b10` x128,
`0b11` x76), which DVD does not have. Masking them yields valid BCD in 204/204
cells, so the mask is certainly right; the meaning is not.
They are **not** frame rate — both values occur within a single PGC. They correlate
loosely with cell category but not deterministically. **Unresolved.**

## VTS_C_ADT — identical to DVD-Video
`nr_of_vobs` u16, reserved, `last_byte` u32, then 12-byte entries
(`vob_id` u16, `cell_id` u16, `start_sector` u32, `last_sector` u32).
Entries match cell_playback exactly (cell 1 = 0..9833, cell 2 = 9834..10153).

## VTS_EVOBU_ADMAP — identical to DVD-Video
`last_byte` u32 then ascending u32 VOBU start sectors. 11871 entries here.

## VTS_TMAPT — identical to DVD-Video  (gap #3 closed)
`nr_of_tmaps` u16, reserved u16, `last_byte` u32, u32 offsets, then per map:
`tmu` u8 (seconds per entry), reserved u8, `nr_of_entries` u16, then u32 entries
with **bit 31 = discontinuity**, exactly as DVD.

Fully cross-validated on all five maps — every one contiguous, and duration matches:

| map | tmu | entries | entries x tmu | PGC playback |
|---|---|---|---|---|
| 1 | 3 s | 1980 | 5940 s (99 m) | 5942 s (99 m) |
| 2 | 2 s | 1057 | 2114 s (35 m) | 2114 s (35 m) |
| 3 | 1 s | 1401 | 1401 s (23 m) | 1401 s (23 m) |
| 4 | 1 s | 1601 | 1601 s (26 m) | 1561 s (26 m) |
| 5 | 3 s | 1980 | 5940 s (99 m) | 5942 s (99 m) |

`tmu` varies per map (3/2/1/1/3 s). No HD DVD-specific TMAP format was needed for
Standard Content. The `.MAP` files on Advanced discs are a different structure —
solved in `06_TMAP_solved.md`.
