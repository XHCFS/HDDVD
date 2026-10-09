# 1. Volume and directories

*Counts written "N/120", "N/119", "on N discs", "listings", or as named discs are over the reference corpus of 120 archived retail HD DVD images [11]. `eNN` are the reproducible verification experiments [12].*


## 1.1 Filesystem

HD DVD-Video is **UDF 2.50** with a Metadata Partition.

| Field | Value | Evidence |
|---|---|---|
| Logical block size | 2048 | LVD on 3 discs [11]; listings |
| UDF revision (LVD domain suffix) | `0x0250` | **N=3** LVD (MYSTERY_MEN, DOWNFALL, RESERVOIR_DOGS); not a 120-disc census |
| AVDP | sector 256 | `tools/udfgrab.py` (does **not** try `N−256`) |
| Partition start | **288** on 120/120 listings | `e01` / `e14` |
| File payload | physical partition | walker |
| Directories / File Entries | metadata partition | walker |

A UDF 1.02 DVD walker cannot mount this. Walk the metadata partition, then read
file extents from the physical partition.

`partition_start=288` is line 2 of every `corpus/<DISC>/_listing.txt`.
ISO URL is line 1 of that listing.

There is **no** `VIDEO_TS/` and **no** `AACS/` directory on these discs
(listings mention neither; `e06` / `e14`).

`[11, 12]` **VERIFIED**
`[11]` **VERIFIED** (N=3)
`[12]` **VERIFIED** (this walker). Backup AVDP at `N−256` is UDF-required and **untested** here.

## 1.2 Medium identification

Patent FIG.7: decide the medium is HD DVD, then look for a playlist.

| Probe | Result |
|---|---|
| Root contains `HVDVD_TS/` and UDF 2.50 | treat as HD DVD-Video and continue |
| Official “is this HD DVD?” MMC probe | `GET CONFIGURATION` current profile **`0x0050`** = HD DVD-ROM (`0x0051` HD DVD-R, `0x0052` HD DVD-RAM) [21]. Drive-level, not exercised on an ISO |
| `ADV_OBJ/DISCID.DAT` exists | **Category 2 or 3** → this spec. The book's test [23 §4.1.1]; DISCID.DAT is required on every Category 2/3 disc |
| No DISCID; `HVDVD_TS/HV000I01.IFO` magic `HVDVD-VMG100`, `VMG_CAT` b3–b0 = no Advanced VTS | Category 1 (Standard Content); **out of scope** |
| Neither | player-dependent [23 §4.1.1] |
| Advanced Content plus Standard VTSs | Category 3; **0/120** here |

Category 1 is Standard Content only; Category 2 is Advanced Content only (no VMG, no
Standard VTS); Category 3 is Advanced Content that may also play Standard VTSs.
A Category 3 disc always starts in Advanced Content and moves to Standard Content
through the script `StandardContentPlayer` object; Standard Content returns with the
`CallAdvancedContentPlayer` navigation command; SPRMs and GPRMs are shared
[23 §3.1, §4.3.22.4].

The startup playlist is `VPLST$$$.XPL` for a player connected to a display and
`APLST###.XPL` for a player without one (Display Mode system parameter) [23 §3.3.2,
§4.3.22.2]. **0** `APLST` files in this corpus.

`[1]`
`[11, 12]` **VERIFIED** as disc classification. `[21]` The official drive probe is `GET CONFIGURATION` → current profile `0x0050` (HD DVD-ROM); an ISO cannot answer it, the directory test does.

## 1.3 Root directories (N=120)

| Directory | N | Role |
|---|---|---|
| `HVDVD_TS/` | 120 | Video objects: Advanced VTI/MAP/EVO on 119; Standard IFO/EVO on 1 |
| `ADV_OBJ/` | 119 | Playlist, DISCID, ACA, assets |
| `ANY!/` | 96 | AACS files (book name is `AACS/`) |
| `ANY!_BAK/` | 96 | AACS backup |
| `AAC!/` | 8 | Alternate AACS directory name |
| `AAC!_BAK/` | 8 | Backup of `AAC!/` |

`[11, 12]` **VERIFIED**. 16 discs have no AACS dir.

## 1.4 `HVDVD_TS/`: Advanced Content files

| Pattern | Listed | Role | Layout |
|---|---|---|---|
| `HVA00001.VTI` | 119 | Advanced VTSI | [06_vti.md](06_vti.md) |
| `HVA00001.BUP` | 36 saved | Byte-identical copy of the VTI (`e08`, 0 differ). Optional [23 §3.3.2] | same as VTI; player fallback not observed |
| `*.MAP` | 2421 listed | Time map for one EVOB | [07_map.md](07_map.md) |
| `*.BUP` next to a MAP | **773 saved** (more may be listed) | Byte-identical copy of the MAP (`e08`, 0 differ). Optional | same as MAP |
| `*.EVO` | 2456 listed | MPEG-2 program stream | [08_evo.md](08_evo.md) |

Clip basenames are free-form (`FEATURE_1`, `EVOB002`, `PEVOB`). The playlist `src`
is the **`.MAP`**, never the `.EVO`. The EVO filename is in EVOBI ([06](06_vti.md)).
The book fixes the pairing: a map has the same name body as its EVOB file, with
extension `MAP`; its backup has the same body with extension `BUP` [23 §3.3.2].

One Advanced VTS holds up to 1998 EVOBs. An EVOB in a Contiguous Block is one `.EVO`
file with its own `.MAP`. All EVOBs of one Interleaved Block share one `.EVO` file and
one `.MAP` [23 §3.3.1].

`HVS0@@@@.MAP` (the map of a Standard VTS played from Advanced Content, Category 3;
`@@@@` = `0001`–`1998`, the EVOB index of that EVOBI and TMAP) [23 §3.3.2]: **0/120**.
The Standard VTS's PCI and HLI are ignored in that case [23 §3.2].
Four `*_load.log` / `*_verify.log` files exist under `HVDVD_TS/` (`e06`). Authoring debris; ignore.
`[11, 12]` **VERIFIED**

## 1.5 `ADV_OBJ/`: files

| Pattern | Listed | Role | Layout |
|---|---|---|---|
| `DISCID.DAT` | 119 | Configuration File, always 128 bytes. Required directly in `ADV_OBJ/` even when the disc uses no network or persistent storage [23 §3.3.2] | [02_discid.md](02_discid.md) |
| `VPLST$$$.XPL` | 247 | Startup playlist for a player with a display. `$$$` = 000–999, highest wins. Must be directly in `ADV_OBJ/` | [03_playlist.md](03_playlist.md) |
| `*.XPL` / `*.xpl` elsewhere under `ADV_OBJ/` | — | Other playlists (loaded by script, `IPlaylist.load`); subdirectories allowed [23 §3.3.2] | [03](03_playlist.md) |
| `VPLST$$$.BAK` | 3 | Not in the boot search (`.XPL` only) | ignore for boot |
| `APLST###.XPL` | 0 | Startup playlist for a player without a display | unused |
| `*.ACA` | 409 | Application archive | [04_aca.md](04_aca.md) |
| `*.XMF` | 3 loose + inside ACA | Manifest | [05_manifest_hdi.md](05_manifest_hdi.md) |
| `*.XMU` | 2 loose + inside ACA | HDi markup | [05](05_manifest_hdi.md) |
| `*.JS` | 3 loose + inside ACA | ECMAScript | [05](05_manifest_hdi.md) |
| `*.PNG` | 72 | Icons / resources | standard PNG |
| `*.TTF` | 1 loose | Font | standard |
| `*.CER` | 10 | **Standard X.509 DER certificates** (`30 82…`). Book: X.509v3, directly in `ADV_OBJ/`, for server authentication [23 §3.2, §9.3]. TLS trust anchors for the HDi network layer (`IHTTPClient`/HTTPS to studio servers). Sample `dynamichd.cer` = *Thawte Premium Server CA* root [15]. Not AACS `CONTENT_CERT`. **Not used by linear playback.** Ignore. | X.509 |
| `Thumbs.db` | 2 | Junk | ignore |

`[11, 12]` **VERIFIED**

**Names and limits under `ADV_OBJ/`** [23 §3.3.2]:

| Rule | Value |
|---|---|
| Subdirectories of `ADV_OBJ/` | fewer than 512 in total; depth at most 8 below `ADV_OBJ/` |
| Files | at most 512 × 2047 under `ADV_OBJ/`; fewer than 2048 per directory |
| Name characters | `A–Z a–z 0–9`, space, `! $ % & ' ( ) + , - . ; = @ _` (ISO 8859-1) |
| Name length | at most 255 characters |
| Case | names may mix case; two names in one directory may not differ only in case; a reference must match the case exactly. If the case does not match, behave as if the file is not found (a case-insensitive system may open it) |
| Zero-byte files | allowed |

**Extensions and MIME types** [23 §3.3.5]. The extension decides the type; each
extension is all upper or all lower case (`Xpl` is not allowed).

| Extension | MIME type | Content |
|---|---|---|
| `XPL` | `text/hddvdpl+xml` | Playlist |
| `XMF` | `text/hddvdmf+xml` | Manifest |
| `XMU` | `text/hddvdmu+xml` | Markup |
| `XTS` | `text/hddvdts+xml` | Timing sheet |
| `XSS` | `text/hddvdss+xml` | Style sheet |
| `XAS` | `text/hddvdas+xml` | Advanced Subtitle markup |
| `JS` | `application/ecmascript` | Script |
| `EVO` | `video/evob` | Secondary Video Set EVOB |
| `MAP` | `application/tmap` | Time map |
| `BUP` | `application/tmap` | Time map backup |
| `JPG` | `image/jpeg` | Image |
| `PNG` | `image/png` | Image |
| `MNG` | `image/mng` | Animation |
| `CVI` | `image/cvi` | Capture Video image |
| `CDW` | `image/cdw` | Capture Drawing image |
| `WAV` | `audio/x-wav` | Effect audio |
| `OTF` `TTF` `TTC` | `application/font` | Font |
| `ACA` | `application/archiving` | Archive ([04](04_aca.md)) |
| `CER` | `application/x-x509-ca-cert` | Certificate |
| anything else | `application/x-data` | Data |

## 1.6 Disc URI

Players resolve assets as:

```
file:///dvddisc/ADV_OBJ/DISCID.DAT
file:///dvddisc/ADV_OBJ/VPLST000.XPL
file:///dvddisc/HVDVD_TS/FEATURE_1.MAP
file:///dvddisc/ADV_OBJ/menus.aca/MainMenu.xmf
```

`file:///dvddisc` is the UDF volume root.

The book's URI roots [23 §6.2.2, §4.3.20.4, §10.3.1] match the patent FIG.20
**drawing** (`US20070091495A1` `pages/page-024.png`): `file:///dvddisc/`,
`file:///filecache/` (the File Cache's API area, stored as `temp/`),
`file:///required/`, `file:///additional/<BasePath>/`,
`file:///common/required/`, `file:///common/additional/<BasePath>/`. The patent's
prose writes `file:///fixed/` and `file:///removable/` instead; the book does not.
A file inside an archive is `file:///<source>/<archive>/<member>`, for example
`file:///dvddisc/ADV_OBJ/app_0001.aca/app_0001_01.xmu` [23 §4.3.20.4]. Playlist.xsd
`DataSourceType` is `Disc` / `P-Storage` / `Network` / `FileCache`. Corpus `src`
is all `file:///dvddisc/` (**10 620 / 10 620** playlist `src`, `e12`). The persistent-storage **script** URI form is specified:
`file:///required/{contentId}/` ([05](05_manifest_hdi.md) §5.8); on the storage medium the player
nests it as `/HD_DVD/<PROVIDER_DIR>/<CONTENT_ID>/`. The book names `PROVIDER_DIR` with
the Provider ID itself [23 §10.3.2]; on an AACS disc the AACS book replaces it with a
keyed transform of `PROVIDER_ID` [4 §6.3] ([05](05_manifest_hdi.md) §5.8).
`[11, 12]` **VERIFIED** (`dvddisc` only)
`[1]`
