# S4. Program Chain and the navigation-command VM

*From `RESERVOIR_DOGS` [11]. No patent RBP table exists for the PGC body or the command
encoding; everything here is disc-derived and **SINGLE** unless noted.*

The Program Chain (PGC) is the unit of playback: an ordered list of programs and cells,
plus pre/post/cell command blocks executed by a small register VM. This is DVD-Video's
model, kept intact and widened.

## 4.1 PGC layout

Offsets moved ahead of the palettes, and there are **two** palettes. `[11]`
`[SRC: DERIVED | arithmetic closure on PGC 1: cell_playback 386 + 58×28 = 2010 =
cell_position_offset; +58×4 = 2242 = next PGC]` **SINGLE**.

| Offset | Size | Field | vs DVD |
|---|---|---|---|
| 0x00 | 2 | `nr_of_programs` | u8 @0x02 |
| 0x02 | 2 | `nr_of_cells` | u8 @0x03 |
| 0x04 | 4 | `playback_time` | same (BCD, see §4.4) |
| 0x08 | 4 | `prohibited_ops` (UOP) | same |
| 0x0C | 16 | `audio_control[8]` (u16) | same |
| 0x1C | 128 | `subp_control[32]` (u32) | same |
| 0x9C | 2 | `next_pgc_nr` | same |
| 0x9E | 2 | `prev_pgc_nr` | same |
| 0xA0 | 2 | `goup_pgc_nr` | same |
| 0xA2 | 1 | `pg_playback_mode` | same |
| 0xA3 | 1 | `still_time` | same |
| 0xA4 | 4 | reserved | **new** |
| 0xA8 | 2 | `command_tbl_offset` | DVD @0xE4 |
| 0xAA | 2 | `program_map_offset` | DVD @0xE6 |
| 0xAC | 2 | `cell_playback_offset` | DVD @0xE8 |
| 0xAE | 2 | `cell_position_offset` | DVD @0xEA |
| 0xB0 | 64 | **palette #1** (16 × u32) | DVD @0xA4 |
| 0xF0 | 64 | **palette #2** (16 × u32) | **DVD has one** |

The two palettes were byte-identical on the specimen; purpose unconfirmed (likely
SD/HD or 4:3/16:9 variants). **Do not assume they always match.** `audio_control` had
exactly 6 non-zero entries (= `VTS_AST_N`) and `subp_control` 5 (= `VTS_SPST_N`).

## 4.2 cell_playback — 28 bytes (DVD: 24)

`[11]` `[SRC: DERIVED | chain-validated: cell[n+1].first_sector == cell[n].last_sector+1
across all 204 cells]` **SINGLE**. DVD's 24-byte layout holds with **4 trailing bytes**
appended (zero on the specimen):

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

`cell_position` stays 4 bytes (`vob_id` u16, reserved u8, `cell_id` u8).

## 4.3 The navigation-command VM — DVD's instruction set, rotated 16 bits

**HD DVD command word = DVD-Video command word rotated right 16 bits.** `[11]`
(57 commands across 12 IFOs) + `[SRC: SRCCODE | libdvdnav src/vm/vmcmd.c]` **SINGLE**.

```
DVD[0..5] = HD[2..7]      DVD[6..7] = HD[0..1]
```

The command table header is DVD-shaped (`nr_pre`, `nr_post`, `nr_cell`, `last_byte` as
u16); commands are 8 bytes as in DVD. The proof is statistical: across all 57 commands
`byte[0]` is `0x00` every time (so it cannot be the opcode); the type field is at
`byte[2]`. Testing `byte[2]>>5` yields `{1,2,3}` = DVD's Link/Jump, SetSystem, Set —
whereas the raw reading yields type 0 (invalid) for everything.

| | raw bytes | rotated |
|---|---|---|
| type histogram | `{0: 57}` all invalid | `{1:16, 2:5, 3:36}` = Link/Jump, SetSystem, Set |

Decoded with libdvdnav's own bit positions, the semantics are coherent:

| Source | Bytes | Decodes as |
|---|---|---|
| VMG first-play | `00 11 30 02 00 00 00 0f` | **JumpTT 15** |
| VTS1 PGC1 post | `00 00 30 08 00 00 00 92` | **CallSS VTSM** (call VTS menu) |
| VTS1 PGC1 pre | `00 00 41 00 00 81 82 00` | **SetSystem op=1** (audio/subp/angle) |
| various pre | `00 00 71 00 00 0a 00 00` | Set GPRM, immediate 10 |

A first-play that jumps to a title and a feature PGC whose post-command calls the VTS
menu are exactly the expected shapes. **Consequence:** libdvdnav's `vm.c`/`vmcmd.c` and
the VM (16 SPRM + 16 GPRM registers, Link/Jump/Call/SetSystem/Set/Compare families) are
reusable after a single 16-bit rotation at command load. The instruction set, register
model, and UOP mask semantics are DVD's [SRCCODE].

### Caveat — Set-operand register field
The GPRM register field decoded as `g0` for every Set command, which is implausible.
libdvdnav has three `print_set_version_*` variants with different register bit
positions and the correct one is not yet established. **The type dispatch is solid; the
Set operand layout needs a second specimen.** **OPEN**.

## 4.4 playback_time — one unresolved detail

Format is DVD's BCD `hour, minute, second, frame`. The frame byte's top 2 bits are
`0b10` (25 fps) in all 204 cells — DVD's frame-rate encoding, consistent with PAL. But
the **seconds byte carries 2 additional varying bits** (`0b10` ×128, `0b11` ×76) that
DVD does not have. Masking them yields valid BCD in 204/204 cells (so the mask is
right), but they are **not** frame rate (both values occur within one PGC) and their
meaning is **unresolved / OPEN**.

## 4.5 Menu PGC category (`HDVTSM_PGC_CAT` / `HDVMGM_PGC_CAT`)

Patent [3] FIG.8 (VMG menu) and FIG.27 (VTS menu) give a 4-byte category word: entry
type (b7), block mode/type, audio-info selection (audio in VOB stop/continue/ignore,
plus `HDMENU_AOBS` triggering), audio number, and `PTL_ID_FLD` (upper/lower). These
drive menu-PGC selection and the still-menu audio object (`HDMENU_AOBS`, the HD analogue
of DVD's menu audio). Bodies not decoded on the specimen — structure from patent only,
**OPEN**.
