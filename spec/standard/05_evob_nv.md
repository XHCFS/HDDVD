# S5. EVOB, NV_PCK, cells and highlight buttons

*From `RESERVOIR_DOGS` (unencrypted) and cross-referenced to `MYSTERY_MEN`/`DOWNFALL`
(Advanced) where the container is shared [11]. The EVO container and NV_PCK are
common to both content categories; only the navigation *around* them differs.*

## 5.1 The EVO container (shared with Advanced)

`.EVO` is an **MPEG-2 program stream** in 2048-byte packs — pack start `00 00 01 BA` at
every 2048-byte boundary, MPEG-2 marker bits `01`. `[11]` **VERIFIED** (2 discs, one
encrypted, one not). Identical to [Advanced §8.1](../advanced/08_evo.md); any MPEG-2 PS
demuxer that accepts 2048-byte packs consumes EVO. Pack and system headers are always
in the clear; AACS (when present) covers elementary-stream payload only ([§7](07_aacs.md)).

## 5.2 Stream identifiers

Standard Content uses the same `stream_id` / `sub_stream_id` assignments as Advanced
(patent TABLE 45–47 [2]; WO FIG.119–125 [3]): video `0xE0` (MPEG-2) / `0xE2` / `0xFD`+
extension (VC-1/AVC); audio and sub-picture inside `private_stream_1` (`0xBD`) keyed by
the first payload byte; PCI/DSI/GCI inside `private_stream_2` (`0xBF`). Full routing:
[Advanced §8.7](../advanced/08_evo.md). Sub-picture RLE/DCSQC decoding: [Advanced §8.8].
**VERIFIED** (shared layer).

## 5.3 Cells and interleaved blocks

A cell is a contiguous or interleaved run of VOBUs addressed by `cell_playback`
([§4.2](04_pgc_vm.md)) and `VTS_C_ADT` ([§3.5](03_vtsi.md)). Interleaved blocks (multi-
angle / seamless branching) place ILVUs from several VOBs on disc in the pattern
VOB#1-chunk, VOB#2-chunk, … addressed by `first_ilvu_end_sector` /
`last_vobu_start_sector` — DVD's ILVU model, drawn in patent FIG.69/93/94 [3]. The
specimen's titles are single-angle contiguous (`TT_PB_TY=0x14`, 1 angle), so the
interleaved path is **patent-only** here. **OPEN** for Standard Content specifically.

## 5.4 NV_PCK — PCI, DSI, GCI

The first pack of each EVOBU is the NV_PCK: three `private_stream_2` (`0x000001BF`)
packets distinguished by a sub-stream byte. `[11]` **VERIFIED** (packet set on 3 discs);
GI offsets **SINGLE** (first proven on this Standard disc, then confirmed on Advanced).

| Sub-stream | PES length | Identity |
|---|---|---|
| `0x00` | 977 | **PCI** — Presentation Control Information |
| `0x01` | 755 | **DSI** — Data Search Information |
| `0x04` | 257 | **GCI_PKT** — General Control Information (16 B `GCI_GI` + 189 B `RECI` + reserved) |

DVD-Video uses the same mechanism and IDs (`0x00`/`0x01`) at different lengths
(980/1018). `0x04` (GCI) is HD DVD-new (patent TABLE 50–52 [2]); it also carries the
AACS Copy Protection Information on protected discs ([§7](07_aacs.md), CPI at pack
offset `0x3C` — [Advanced §9.6](../advanced/09_aacs.md)). `GCI_CAT` reads `0x00` on this
Standard disc vs `0x40` on Advanced.

### PCI general information (`pci_gi`) — DVD layout holds
Offsets relative to the sub-stream byte; `[11]` (VOBU 0/1, 40-VOBU chain) **SINGLE**:
`nv_pck_lbn` @1, `vobu_cat` @5, `vobu_uop_ctl` @9, `vobu_s_ptm` @13, `vobu_e_ptm` @17.
Cross-check: `vobu_e_ptm − vobu_s_ptm` = 45045 ticks @90 kHz = 500.5 ms = 15 frames at
29.97; VOBU 1's `vobu_s_ptm` == VOBU 0's `vobu_e_ptm`.

### DSI general information (`dsi_gi`) — DVD layout holds
`nv_pck_scr` @1, `nv_pck_lbn` @5, `vobu_ea` @9, `vobu_1stref_ea` @13, 2nd/3rd @17/21,
`vobu_vob_idn` @25, `vobu_c_idn` @28. **`vobu_ea` is RELATIVE to the VOBU start**, not
absolute — walk `next = lbn + vobu_ea + 1`. Chain-validated 40/40 VOBUs. `[11]` **SINGLE**.

## 5.5 Highlight information and menu buttons (HLI)

Standard-Content menu buttons live in the stream, not in a markup document. Two places:

- **PCI HLI** (`hli`/`hl_gi`, `btn_colit`, `btni` in DVD's `pci_t`) — the run-time
  highlight state, following `pci_gi` in the NV_PCK PCI packet. Region **not examined**
  on the specimen — **OPEN**.
- **Sub-picture / Graphics Unit (GU)** — the button graphics. Patent FIG.45 [3] gives
  the GU data structure: `GU pack` sequence → Graphics Unit = header + **HLI** +
  mask-data#1..n + graphics data; the HLI block (b21–b23) carries general info, a
  **color palette** (normal / selection / set-action color), and per-button info
  (`b231` start address of mask data, `b232` size, `b233` neighbouring-button position
  for D-pad navigation, `b234` **button command**). The button command is a VM command
  ([§4.3](04_pgc_vm.md)) executed on activation. This is DVD's highlight/button model
  extended for HD sub-picture. Byte offsets within GU **OPEN** (no specimen dumped).

The graphics-plane composition (main → sub-picture → highlight → graphics → cursor) is
the same order given in [Advanced §8.8](../advanced/08_evo.md) / WO FIG.102/144 [3];
the graphics decoder pipeline (video/SP/highlight/graphics decoders + mixers) is patent
FIG.39 [3].

## 5.6 Seek within a PGC

Two addressing layers, both DVD's:
1. **Time → sector** via `VTS_TMAPT` ([§3.4](03_vtsi.md)): entry index = `t / tmu`,
   entry value = VOBU start sector (bit 31 = discontinuity).
2. **Sector → VOBU-accurate** via `VTS_EVOBU_ADMAP` and in-stream **DSI** (`vobu_ea`,
   `vobu_1stref_ea` for the first decodable I-frame). `[11]` **VERIFIED** (TMAPT
   durations match PGC playback time; DSI chain 40/40).

No `.MAP` sidecar files exist for Standard Content — the time map is the in-IFO
`VTS_TMAPT`, unlike Advanced Content which uses standalone `.MAP` files
([Advanced §7](../advanced/07_map.md)).
