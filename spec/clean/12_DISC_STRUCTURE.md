# Disc structure — directories and files

On-disc map a player has to open. Provenance: `EVIDENCE_STANDARD.md`. Census:
`experiments/e06_catalog.py`, `e01`, `e07`. Playback order is `13_PLAYBACK.md`.

This file is complete for **trees** and for **which file is which**. Byte layouts
live in `03`, `06`, `08`, `09`. A claim here without a `[SRC:]` tag is a bug.

---

## 0. What a disc is

HD DVD-Video is **UDF 2.50** with a Metadata Partition. Sector size 2048.
`partition_start=288` on 120/120 listings. File payload is in the physical
partition; directories/FEs are in metadata. `tools/udfgrab.py` walks this.
libdvdread’s UDF 1.02 reader cannot.

`[SRC: CORPUS | N=120 listings | partition_start=288]`
`[SRC: DISC | MYSTERY_MEN, DOWNFALL, RESERVOIR_DOGS LVD | LogicalBlockSize=2048, domain *OSTA UDF Compliant, revision 0x0250]`
`[SRC: SRCCODE | tools/udfgrab.py, libudfread udf_volume.c]`
**VERIFIED**

There is **no** `VIDEO_TS/` and **no** `AACS/` on any of these 120 discs.
`[SRC: CORPUS | e06 | other file roots = none]`

ISO URL for every specimen is line 1 of `corpus/<DISC>/_listing.txt`
(`https://archive.org/download/hd-dvd_archive_NN/<DISC>.iso`).

## 1. Categories (how the player decides what to run)

`[SRC: PATENT | US20070091495A1 FIG.5, FIG.7 “Medium Identification Processing Method”]`

| Category | Zone | This corpus |
|---|---|---|
| 1 | Standard Content only (`HVDVD_TS` IFO/EVO, no playlist) | 1 (`RESERVOIR_DOGS`) |
| 2 | Advanced Content only (`ADV_OBJ` + Advanced VTS) | 119 |
| 3 | Both | **0** |

Player algorithm (patent FIG.7):

1. Decide the medium is HD DVD (how: **OPEN** — not demonstrated here; empirically
   the presence of `HVDVD_TS/` plus UDF 2.50 is sufficient to start a walk).
2. Look for a playlist under `ADV_OBJ/` directly (not subdirectories).
   If found → Category 2 or 3 → Advanced startup (`13_PLAYBACK.md`).
3. Else read VMG ID / `VMG_CAT` → Category 1 → Standard Content VM.

`[SRC: PATENT | US20070091495A1 | “If the playlist file PLLST is found … category 2 or 3”]`
`[SRC: CORPUS | N=120 | 119 have ADV_OBJ+VPLST; 1 has HV000I01.IFO and no ADV_OBJ]`
**VERIFIED** as a disc classification. Step 1’s official probe is **OPEN**.

## 2. Root directories

`[SRC: CORPUS | e06 | DIR lines, N=120]`

| Directory | Discs | Function |
|---|---|---|
| `HVDVD_TS/` | 120 | Video objects and their maps / VTI or IFO. Patent name `HDDVD_TS` — **drift**. |
| `ADV_OBJ/` | 119 | Advanced navigation: playlists, config, applications. Absent on Category 1. |
| `ANY!/` | 96 | AACS data-area files. Book name `AACS/` — **drift**. |
| `AAC!/` | 8 | Same AACS file set, different directory name. |
| `ANY!_BAK/` | 96 | Backup of `ANY!` (see `09_AACS.md` § BAK). |
| `AAC!_BAK/` | 8 | Backup of `AAC!`. |

16 discs have no AACS directory (unencrypted). Every AACS disc has the matching `*_BAK`.
`[SRC: CORPUS | e01, e05]`

URI the player uses: `file:///dvddisc/<path>`.
`[SRC: CORPUS | XPL @src; 1408 extras.xmf]` **VERIFIED**

## 3. `HVDVD_TS/` — files

### Advanced Content (119 discs)

| Pattern | Count | Role | Byte layout |
|---|---|---|---|
| `HVA00001.VTI` | 119 | Advanced VTSI. Magic `ADVANCED-VTS`. | `03` TABLE 77, ATRT 1024 B, EVOBI 320 B |
| `HVA00001.BUP` | 36 saved | Byte-identical copy of the VTI (`e08`). Player fallback **OPEN**. | same bytes as VTI |
| `*.MAP` | 2421 | Time map for one EVOB. Magic `HDDVD_TMAP00`. | `06_TMAP_solved.md` |
| `*.EVO` | 2456 listed | MPEG-2 program stream, 2048-byte packs. | `08_NV_PCK_PCI_DSI.md` |
| `*.BUP` next to a MAP | 773 saved | Byte-identical copy of the MAP (`e08`, 0 differ). Player fallback **OPEN**. | same bytes as MAP |
| `*_load.log` / `*_verify.log` | 4 | Authoring debris (`PARALOGO`, `INIT_BLACK`). | Ignore. |

Clip names are free-form (`FEATURE_1.EVO`, `PEVOB.MAP`, `EVOB-1408.MAP`). The
**playlist `src` is the `.MAP`**, never the `.EVO`. EVOBI@+2 holds the EVO filename.
`[SRC: CORPUS | e02, e07 | PrimaryAudioVideoClip src MAP=4847]`
`[SRC: CORPUS | N=2431 EVOBI | EVO name matches listing]`

`HVSO@@@@.MAP` (Standard VTS map referenced from Advanced): **0/120**.
`[SRC: PATENT | US20070091495A1]` + `[SRC: CORPUS | e06]`

### Standard Content (1 disc: `RESERVOIR_DOGS`)

| Pattern | Role |
|---|---|
| `HV000I01.IFO` / `.BUP` | VMG. Magic `HVDVD-VMG100`. |
| `HV%03dI01.IFO` / `.BUP` | Standard VTS. Magic `STANDARD-VTS`. 11 VTS + VMG = 12 IFOs, all `I01`. |
| `HV%03dT%02d.EVO` | Title EVOB. |
| `HV%03dM%02d.EVO` | Menu EVOB. VMG menu is `HV000M02.EVO` (**not** M01). VTS menus are `M01`. |

Byte layouts: `01_VMGI_MAT_and_TT_SRPT.md`, `02_VTSI_MAT_PGC_and_commands.md`.
**SINGLE** specimen.

## 4. `ADV_OBJ/` — files

`[SRC: CORPUS | e06 ADV_OBJ ext + e07 + saved 1408 / MATRIX samples]`

| Pattern | Listed | Function |
|---|---|---|
| `DISCID.DAT` | 119 | Config File. 128 B, `HDDVD-V_CONF`. | `03` §8 |
| `VPLST$$$.XPL` | 247 | Playlist XML. `$$$` = 000–999. **Boot file = highest `$$$` on disc** (and persistent storage if `SEARCH_FLG=0`). | this file + `04` + XSD |
| `VPLST$$$.BAK` | 3 | Leftover playlists **not** in the boot search (`.XPL` only). Same 3 discs as extra VTKF (`BALLS_OF_FURY`, `CHUCK_AND_LARRY`, `SHREK_THE_THIRD_EU`). | `[SRC: CORPUS \| listings]` |
| `APLST###.XPL` | **0** | Audio-only player playlist. Unused here. | e07 |
| `*.ACA` | 409 | Application archive. Magic `HDDVDACA`. Referenced as `file:///dvddisc/ADV_OBJ/foo.aca` and `foo.aca/manifest.xmf`. | below |
| `*.XMF` | 3 loose (+ inside ACA) | Manifest (`HDDVDVideo/Manifest`). `ApplicationSegment@src` and `PlaylistApplication@src` point here. | 1408 samples |
| `*.XMU` | 2 | HDi markup (`ihd` `root`). Manifest `<Markup src=…>`. | 1408 |
| `*.JS` | 3 loose (+ inside ACA) | ECMAScript. Loose 1408 is UTF-8; **inside ACA, UTF-16BE** (`FE FF`). | MATRIX `selector.aca` |
| `*.PNG` | 72 | Icons / assets. Also `ApplicationResource@src`. | |
| `*.TTF` | 1 loose | Font. | 1408 |
| `*.CER` | 10 | Studio/network certs (`ddsnsbu.cer`, `dynamichd.cer`). Not AACS `CONTENT_CERT`. | **OPEN** use |
| `Thumbs.db` | 2 | Windows junk. Ignore. | |

### Playlist XML (`VPLST$$$.XPL`)

Namespace `http://www.dvdforum.org/2005/HDDVDVideo/Playlist`, all v1.0.
Schema: `spec/raw/adv_obj/v1.0/Playlist.xsd` (Spec. 6.2.3.14 annotations).
`[SRC: CORPUS | e02 | 247/247]`

What you must parse for titles/seek (goal 2):

| Element | N in corpus | `src` points at |
|---|---|---|
| `PrimaryAudioVideoClip` | 4847 | **`.MAP` only** |
| `ApplicationSegment` | 2529 | **`.XMF` only** |
| `ApplicationResource` | 2506 | ACA 2354, PNG 114, XMF 17, JS 17, … |
| `PlaylistApplication` | 203 files | `.XMF` (often `something.aca/manifest.xmf`) |
| `PlaylistApplicationResource` | 455 | ACA 409, PNG 46 |
| `Title` | 3196 | `titleNumber`, `titleDuration`, `onEnd` on 3192 |
| `FirstPlayTitle` | 119 of 247 playlists | logo/FBI clip mapped like a Title but no `titleNumber` |
| `Chapter` | 7665 | `titleTimeBegin` `HH:MM:SS:FF` |

Unused in this corpus (still in the XSD): `SecondaryAudioVideoClip`,
`SubstituteAudioVideoClip`, `SubstituteAudioClip`, `AdvancedSubtitleSegment`,
`NetworkSource`. **0** `APLST`.

**Highest-numbered playlist is not always the feature.**

| Highest `VPLST` contains | Discs |
|---|---|
| `PrimaryAudioVideoClip` (can play video from XPL alone) | 116 |
| `PlaylistApplication` only (language selector; script then `Player.playlist.load` another XPL) | 3: `MATRIX_REVOLUTIONS` 099, `BLADE_RUNNER` 002, `TRAINING_DAY` 003 |

`[SRC: DISC | MATRIX_REVOLUTIONS VPLST099.XPL | no clips; PlaylistApplication → selector.aca/manifest.xmf]`
`[SRC: DISC | selector.aca/script.js | `Player.playlist.load("…/VPLST000.XPL")` or `VPLST001.XPL` by `Player.menuLanguage`]`

A library that “plays the disc” without HDi must **not** assume highest = feature.
Expose: (a) spec boot playlist, (b) playlists that contain `PrimaryAudioVideoClip`,
(c) optional: follow `playlist.load` after running script (goal 5, later).

### `DISCID.DAT`

128 bytes. Layout `03` §8. `SEARCH_FLG=0` → also search persistent storage for
`VPLST$$$.XPL` under `PROVIDER_ID`/`CONTENT_ID`. `SEARCH_FLG=1` → disc only.
`[SRC: PATENT | US20070091495A1 FIG.50 step 1]`
`[SRC: TOOL | Scenarist AC 4.5 UserGuide “Config File is called DISCID.DAT”]`

### `.ACA`

Saved specimen: `corpus/MATRIX_REVOLUTIONS/ADV_OBJ__selector.aca` (2008 B).
`[SRC: DISC | that file]` **SINGLE** for body; header strings also in
`spec/raw/adv_obj/ACA_and_AdvancedStream_evidence.txt`.

| Offset | Size | Field | This file |
|---|---|---|---|
| 0 | 8 | magic | `HDDVDACA` |
| 8 | 2 | version | `00 10` (= 1.0, same `VERN` encoding as VTI/MAP) |
| 10 | 2 | encoding type | `00 01` (player requires 1; compression **OPEN**) |
| 12 | 2 | entry count | 2 |
| 14 | 4 | total size | 2008 = file length |
| 0x20 | 58×N | directory | offset u32, length u32, CRC u32, flags, NUL name |

Entries: `manifest.xmf` @0x1AC len 0x1EB; `script.js` @0x4B6 len 0x31E.
Payload XML is UTF-8; JS is UTF-16BE. Paths inside:
`file:///dvddisc/ADV_OBJ/selector.aca/script.js`.

409 listed, 1 saved. Fetch more with
`python3 tools/udfgrab.py <url> corpus/<DISC> --ext .ACA --max-bytes …`

### Manifest vs markup

- **Manifest** (`.xmf`, also `manifest.xmf` inside ACA): namespace
  `http://www.dvdforum.org/2005/HDDVDVideo/Manifest`. Lists `Region`, `Script`,
  `Markup`, `Resource`. Schema `Manifest.xsd`.
- **Markup** (`.xmu` on 1408; often packed in ACA): namespace
  `http://www.dvdforum.org/2005/ihd`, root `root`. Schema `iHD.xsd`. This is the
  HDi document (buttons, timing, `Player.*` API).

`[SRC: DISC | 1408 extras.xmf, popupMenu.xmf, menu.xmu]`
`[SRC: SRCCODE | spec/raw/adv_obj/v1.0/Manifest.xsd, iHD.xsd]`

Linear titles do not need a markup/script engine. Identical HDi menus do.

## 5. AACS trees (`ANY!` / `AAC!`)

Filenames match Final 0.953; directory name does not. Layouts: `09_AACS.md`.
Do not put a decryptor in this repo. A reader probes `ANY!`, `AAC!`, then `AACS`;
parses VTKF Table 3-8 sized from `HD_VTKF_SIZE`; takes Volume ID from the drive
(`READ DISC STRUCTURE` 80h), not from `DISCID.DAT`.

| File | Typical | Notes |
|---|---|---|
| `MKBROM.AACS` | four sizes | stop at End-of-MKB |
| `MKBRECORDABLE.AACS` | | omitted from BAK on 99 discs; copied into BAK on 5 |
| `DKF.AACS` | 64 | Table 6-2; not a title key |
| `VTKF$$$.AACS` | 2480; 2516 on two Pan’s files | playlist name @16 |
| `VTUF$$$.AACS` | 144 | usage rules; body **OPEN** |
| `CONTENT_CERT.AACS` | 120 | Table 3-17 |
| `CONTENT_HASH_TABLE1/2.AACS` | vary | bodies **OPEN** |
| `CONTENT_REVOCATION_LIST.AACS` | usually 1e6 | Pan’s 61440 |
| `MNGCPY_MANIFEST.XML` | ~200–304 | Managed Copy; not playback |

## 6. Walk order (what “workable” means here)

A spec is workable when this path can be followed without guessing a byte layout:

1. UDF 2.50 walk → directory catalog.
2. Classify category: playlist present vs VMG IFO.
3. Parse `VPLST*.XPL` → titles, chapters, clip `@src` MAP paths.
   Spec-boot playlist is the highest `VPLST$$$`; three discs are selectors.
4. Parse `.MAP` → `EVOBU_ENT` → byte offset in the sibling `.EVO`.
5. Read EVO as 2048-byte MPEG-2 program-stream packs.
6. Cross-check EVOB filename / `V_ATR` in `HVA00001.VTI` when needed.
7. AACS overlay: pack 128/1920, VTKF, CPI in GCI. Decrypt only with Volume ID from a drive.
8. ACA + Manifest + HDi for menus (not required for linear video).

Standard Content (step 2 → IFO/PGC) is a separate, 1-disc path (`01`, `02`).
