# HD DVD-Video Standard Content — Format Specification (archival)

A complete, implementable specification of **HD DVD-Video Standard Content** — the
"Category 1" playback mode: the DVD-Video navigation model (Video Manager, Video Title
Sets, Program Chains, cells, the navigation-command VM) evolved to high definition.

> **Status: archival / out of scope for `libhddvd`.** Essentially no retail HD DVD
> ships Standard Content — a survey of 120 discs found **1** Standard, 119 Advanced,
> 0 mixed [11]. The product (a VLC HD DVD player) targets **Advanced Content**; that
> specification is in [`spec/advanced/`](../advanced/INDEX.md). This set exists to
> preserve the Standard-Content reverse-engineering so the work is not lost, and to
> document the format completely for the record. It is written to the same evidence
> standard as the Advanced set, but rests heavily on a **single specimen** and should
> be treated accordingly (see [08_gaps.md](08_gaps.md)).

## What Standard Content is

Standard Content is "DVD-Video, widened for HD". The DVD Forum defined it so a very
inexpensive player — no Internet, no interactive engine — could play an HD disc while
staying structurally compatible with DVD-Video [1]. It keeps everything a DVD reader
knows and adds HD codecs:

| | DVD-Video | HD DVD Standard Content |
|---|---|---|
| Navigation model | VMG + VTS + PGC + Cell + PTT + command VM | **same**, fields widened |
| Content dir | `VIDEO_TS/` | `HVDVD_TS/` |
| Info file | `VIDEO_TS.IFO` / `VTS_nn_0.IFO` | `HV000I01.IFO` / `HVnnnI01.IFO` |
| Media object | `.VOB` | `.EVO` (Enhanced Video Object) |
| Video codecs | MPEG-2 | MPEG-2 + **VC-1 + H.264/AVC** |
| Audio codecs | AC-3 / DTS / LPCM / MPEG | + **DD+ / TrueHD / DTS-HD** |
| Interactivity | VM + NV_PCK highlight buttons | **same** (VM + HLI); no HDi |
| Filesystem | UDF 1.02 (+ISO bridge) | UDF 2.50 (Metadata Partition) |
| Encryption | CSS | AACS |

The patents put the design goal bluntly: Advanced VTS *removes* the layered
structure — "No Title, no PGC, no PTT and no Cell. No support of Navigation Command
and UOP control" [1]. Standard Content is the mode that *keeps* all of that.

## About this specification

Reconstructed from three source classes, each fact stated with its evidence:

- **Primary specifications** — the Toshiba patents, which transcribe the (unpublished)
  DVD Forum books near-verbatim, including byte-level `RBP` (Relative Byte Position)
  tables and 138 drawing sheets. Cited `[1]`/`[2]`/`[3]` → [09_references.md](09_references.md).
- **One reference disc** — **`RESERVOIR_DOGS`** (Reservoir Dogs 15th Anniversary,
  Region-B/PAL, `hd-dvd_archive_03`), the sole Category-1 image among the 120-disc
  corpus [11]. Unencrypted (no `ANY!`), authored with Sonic Scenarist SCA 4.2. Every
  byte-level claim here was read from this disc unless marked otherwise.
- **DVD-Video prior art** — libdvdread `ifo_types.h` and libdvdnav `vm/vmcmd.c`, which
  the format is a delta from.

**Evidence grades** (as in the Advanced set): **VERIFIED** (patent RBP table and disc
agree, or chain/arithmetic-validated), **SINGLE** (read from the one specimen; no
patent table and no second disc to confirm — may be a Scenarist artifact), **INFERRED**
(fail-closed rule reasoned from a source), **OPEN** (not yet decoded). Because there is
only one disc, **SINGLE is the dominant grade** — the honest ceiling of this set.

## Sheets

| Sheet | What it specifies |
|---|---|
| [01_volume.md](01_volume.md) | UDF 2.50, `HVDVD_TS/`, IFO/EVO/BUP naming, categories |
| [02_vmgi.md](02_vmgi.md) | `HVDVD-VMG100` — VMGI_MAT, TT_SRPT, first-play PGC, menus |
| [03_vtsi.md](03_vtsi.md) | `STANDARD-VTS` — VTSI_MAT, PTT_SRPT, attributes, C_ADT, EVOBU_ADMAP, TMAPT |
| [04_pgc_vm.md](04_pgc_vm.md) | PGC layout, dual palette, cell_playback, the navigation-command VM |
| [05_evob_nv.md](05_evob_nv.md) | `.EVO` MPEG-2 PS, NV_PCK (PCI/DSI/GCI), cells/ILVU, HLI buttons, stream IDs |
| [06_playback.md](06_playback.md) | Category-1 boot, first-play, PGC chaining, menus, seek |
| [07_aacs.md](07_aacs.md) | AACS overlay as it applies to Standard Content |
| [08_gaps.md](08_gaps.md) | Single-specimen caveats and what is still OPEN |
| [09_references.md](09_references.md) | Numbered sources (shared with the Advanced set) + Standard-Content figures |

## Conventions

| Item | Rule |
|---|---|
| Endian | All IFO structures are **big-endian**, exactly as DVD-Video. UDF descriptors are little-endian. |
| Sector / pack | 2048 bytes. |
| RBP | Relative Byte Position — offset from the start of the structure (patent term). |
| Identifiers | 12-byte ASCII, DVD convention: `HVDVD-VMG100`, `STANDARD-VTS`. |
| Version word | `VERN` `0x0010` = specification 1.0. |
| Drift | Patent identifiers differ from disc (`HDDVD_TS`→`HVDVD_TS`); **the disc wins**. |
| Command word | DVD-Video 8-byte VM command **rotated right 16 bits** (§4). |
| Citations | Inline `[n]` → [09_references.md](09_references.md). Grades are evidence strength. |

**Reading / printing.** This set is part of the same Sphinx build as the Advanced
specification; it appears as an appendix in the browsable site and the single-page
printable build (`docs/_build/singlehtml/`).
