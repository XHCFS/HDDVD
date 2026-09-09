# S1. Volume and directories (Standard Content)

*Disc counts here — "N/120", "on the specimen" — refer to the 120-disc reference
corpus [11]; the single Category-1 disc is `RESERVOIR_DOGS`. `eNN` are the verification
experiments [12].*

## 1.1 Filesystem

Identical to Advanced Content: **UDF 2.50** with a Metadata Partition, 2048-byte
sectors, `partition_start=288` on 120/120 listings [11]. File payload lives in the
physical partition; File Entries and directory data live in the metadata partition. A
DVD-era UDF 1.02 reader (e.g. libdvdread's bundled `dvd_udf.c`) cannot mount the disc;
libudfread (libbluray) can. See [Advanced §1.1](../advanced/01_volume.md) — the volume
layer does not differ by content category. **VERIFIED**.

`RESERVOIR_DOGS` is authored with **Sonic Scenarist SCA 4.2** (UDF implementation ID
`*Sonic ScenaristSCA42`), which matters because every SINGLE-graded claim below could
be a property of that authoring tool rather than of the format. `[11]` **VERIFIED**.

## 1.2 Category detection

`[SRC: PATENT | US20070091495A1 FIG.7 / FIG.147]` `[11]` **VERIFIED** as a classifier.

A player decides what to run before opening any IFO:

1. Recognise the medium as HD DVD (official probe **OPEN**; in practice UDF 2.50 +
   `HVDVD_TS/` is sufficient to begin).
2. If `ADV_OBJ/VPLST$$$.XPL` is present → **Category 2 or 3** → Advanced startup
   ([Advanced §10](../advanced/10_playback.md)).
3. Else read the VMG (`HV000I01.IFO`), whose ID is `HVDVD-VMG100` and `VMG_CAT`
   distinguishes → **Category 1** → Standard Content VM (this set, [§6](06_playback.md)).

| Category | Contents | This corpus |
|---|---|---|
| 1 | Standard Content only (`HVDVD_TS` IFO/EVO, **no** `ADV_OBJ`) | 1 — `RESERVOIR_DOGS` |
| 2 | Advanced Content only | 119 |
| 3 | Both (Standard playable via VM, Advanced via HDi) | 0 |

Category 3 was never observed; the transition rules between Standard and Advanced state
(patent FIG.87 [3]) are therefore **OPEN** for lack of a specimen.

## 1.3 `HVDVD_TS/` file naming

Standard Content uses fixed 8.3 names, the HD analogue of DVD's `VIDEO_TS.IFO` /
`VTS_nn_x.VOB`. `[11]` **VERIFIED** on the specimen; patent proposes `HDDVD_TS` (drift,
disc wins).

| Pattern | Role | DVD-Video analogue |
|---|---|---|
| `HV000I01.IFO` / `.BUP` | Video Manager info (VMGI) + backup | `VIDEO_TS.IFO` / `.BUP` |
| `HV000M02.EVO` | VMG menu video object set (VMGM_EVOBS) | `VIDEO_TS.VOB` |
| `HVnnnI01.IFO` / `.BUP` | Video Title Set nnn info (VTSI) + backup | `VTS_nn_0.IFO` |
| `HVnnnM01.EVO` | VTS nnn menu video object set (VTSM_EVOBS) | `VTS_nn_0.VOB` |
| `HVnnnTmm.EVO` | VTS nnn title video object (VTSTT_EVOBS), fragment mm | `VTS_nn_m.VOB` |
| max VTS | **511** (`nnn`) [1] — vs DVD's 99 | 99 |
| max title fragments | 99 (`mm`) — `T19` seen on the specimen | 9 |

Notes derived from the specimen `[11]` **VERIFIED**:

- The **VMG menu object is `HV000M02.EVO`** — note `M02`, not `M01`. VTS menus are
  `M01`. (Same "menu is a separate object stream" idea as DVD.)
- A single feature is split into ~1 GB `.EVO` fragments exactly as DVD splits `.VOB`s:
  the feature VTS (`HV001`) has one title spread over `HV001T01.EVO … HV001T19.EVO`.
- Backups: every `.IFO` has a byte-identical `.BUP`. The specimen has **12 IFOs**
  (VMG + 11 VTS), all with the `I01` infix.

## 1.4 Specimen inventory (`RESERVOIR_DOGS`)

ISO: `https://archive.org/download/hd-dvd_archive_03/RESERVOIR_DOGS.iso` [11].

- `HV000I01.IFO` (20 480 B) — VMG; `VMG_CAT=0`, `VTS_N=11`, `HV000M02.EVO` menu (347 MB).
- `HV001` — feature VTS: `HV001M01.EVO` menu, `HV001T01…T19.EVO` (~1 GB each), 5 titles
  (`VTS_TTN` 1–5), PGC playback 99 min.
- `HV002 … HV011` — 10 further VTS, each 1 title. `HV009`/`HV010` add a menu (`M01`) and
  a second title each.
- No `ADV_OBJ/`, no `ANY!/` (unencrypted).

TT_SRPT accordingly lists **15 titles across 11 VTS** ([§2.2](02_vmgi.md)). "Title" is
the navigation object (PGC), not the `.EVO` fragment count.
