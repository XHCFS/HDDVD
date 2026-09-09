# S1. Volume and directories (Standard Content)

*Counts written "N/120" or "on the specimen" are over the 120-disc reference corpus
[11]. The single Category 1 disc is `RESERVOIR_DOGS`. `eNN` are the verification
experiments [12].*

## 1.1 Filesystem

The volume layer is identical to Advanced Content and does not vary by content
category. HD DVD-Video is UDF 2.50 with a Metadata Partition, 2048-byte sectors, and
`partition_start=288` on 120/120 listings [11]. File payload is in the physical
partition; File Entries and directory data are in the metadata partition. A DVD-era UDF
1.02 reader such as libdvdread's bundled `dvd_udf.c` cannot mount the disc; libudfread
(libbluray) can. See [Advanced §1.1](../advanced/01_volume.md). **VERIFIED**.

`RESERVOIR_DOGS` was authored with Sonic Scenarist SCA 4.2 (UDF implementation ID
`*Sonic ScenaristSCA42`). This matters because any SINGLE-graded claim below could be a
property of that authoring tool rather than of the format. `[11]` **VERIFIED**.

## 1.2 Category detection

A player decides what to run before opening any IFO. `[SRC: PATENT | US20070091495A1
FIG.7, FIG.147]` `[11]` **VERIFIED** as a classifier.

1. Recognise the medium as HD DVD. The official probe is **OPEN**. In practice UDF 2.50
   plus a `HVDVD_TS/` directory is enough to begin a walk.
2. If `ADV_OBJ/VPLST$$$.XPL` is present, the disc is Category 2 or 3 and Advanced
   startup runs ([Advanced §10](../advanced/10_playback.md)).
3. Otherwise read the VMG (`HV000I01.IFO`). Its ID is `HVDVD-VMG100` and `VMG_CAT`
   confirms Category 1, which runs the Standard Content VM ([§6](06_playback.md)).

| Category | Contents | This corpus |
|---|---|---|
| 1 | Standard Content only (`HVDVD_TS` IFO and EVO, no `ADV_OBJ`) | 1 (`RESERVOIR_DOGS`) |
| 2 | Advanced Content only | 119 |
| 3 | Both | 0 |

Category 3 was never observed, so the rules for transitioning between Standard and
Advanced state (patent FIG.87 [3]) are **OPEN** for lack of a specimen.

## 1.3 `HVDVD_TS/` file naming

Standard Content uses fixed 8.3 names, the HD analogue of DVD's `VIDEO_TS.IFO` and
`VTS_nn_x.VOB`. `[11]` **VERIFIED** on the specimen. The patent proposes `HDDVD_TS`,
which is drift; the disc wins.

| Pattern | Role | DVD-Video analogue |
|---|---|---|
| `HV000I01.IFO`, `.BUP` | Video Manager info (VMGI) and backup | `VIDEO_TS.IFO`, `.BUP` |
| `HV000M02.EVO` | VMG menu video object set (VMGM_EVOBS) | `VIDEO_TS.VOB` |
| `HVnnnI01.IFO`, `.BUP` | Video Title Set nnn info (VTSI) and backup | `VTS_nn_0.IFO` |
| `HVnnnM01.EVO` | VTS nnn menu video object set (VTSM_EVOBS) | `VTS_nn_0.VOB` |
| `HVnnnTmm.EVO` | VTS nnn title video object (VTSTT_EVOBS), fragment mm | `VTS_nn_m.VOB` |
| max VTS | 511 (`nnn`) [1] | 99 |
| max title fragments | 99 (`mm`); `T19` seen on the specimen | 9 |

Observations from the specimen `[11]` **VERIFIED**:

- The VMG menu object is `HV000M02.EVO`, with infix `M02` rather than `M01`. VTS menus
  are `M01`. This follows DVD's "menu is a separate object stream" model.
- A single feature is split into roughly 1 GB `.EVO` fragments, exactly as DVD splits
  `.VOB` files. The feature VTS `HV001` holds one title across `HV001T01.EVO` through
  `HV001T19.EVO`.
- Every `.IFO` has a byte-identical `.BUP`. The specimen has 12 IFOs (VMG plus 11 VTS),
  all with the `I01` infix.

## 1.4 Specimen inventory (`RESERVOIR_DOGS`)

ISO: `https://archive.org/download/hd-dvd_archive_03/RESERVOIR_DOGS.iso` [11].

- `HV000I01.IFO` (20 480 B): VMG with `VMG_CAT=0`, `VTS_N=11`, and a 347 MB menu object
  `HV000M02.EVO`.
- `HV001`: feature VTS with menu `HV001M01.EVO`, title fragments `HV001T01.EVO` through
  `HV001T19.EVO` (about 1 GB each), 5 titles (`VTS_TTN` 1 through 5), PGC playback 99
  minutes.
- `HV002` through `HV011`: ten further VTS, each with one title. `HV009` and `HV010`
  add a menu (`M01`) and a second title each.
- No `ADV_OBJ/` and no `ANY!/` (unencrypted).

TT_SRPT accordingly lists 15 titles across 11 VTS ([§2.2](02_vmgi.md)). A title is the
navigation object (a PGC), not an `.EVO` fragment.
