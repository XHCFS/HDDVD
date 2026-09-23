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
| `ADV_OBJ/` contains `VPLST*.XPL` (not in subdirectories) | **Category 2 or 3** → this spec |
| No playlist; `HVDVD_TS/HV000I01.IFO` magic `HVDVD-VMG100` | Category 1 (Standard Content); **out of scope** |
| Both playlist and Standard VMG | Category 3; **0/120** here |

Audio-only players search `APLST###.XPL` instead. **0** such files in this corpus.

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
| `HVA00001.BUP` | 36 saved | Byte-identical copy of the VTI (`e08`, 0 differ) | same as VTI; player fallback not observed |
| `*.MAP` | 2421 listed | Time map for one EVOB | [07_map.md](07_map.md) |
| `*.BUP` next to a MAP | **773 saved** (more may be listed) | Byte-identical copy of the MAP (`e08`, 0 differ) | same as MAP |
| `*.EVO` | 2456 listed | MPEG-2 program stream | [08_evo.md](08_evo.md) |

Clip basenames are free-form (`FEATURE_1`, `EVOB002`, `PEVOB`). The playlist `src`
is the **`.MAP`**, never the `.EVO`. The EVO filename is in EVOBI ([06](06_vti.md));
in practice the sibling of `FOO.MAP` is `FOO.EVO`.

`HVSO@@@@.MAP` (Standard VTS map referenced from Advanced): **0/120**.
Four `*_load.log` / `*_verify.log` files exist under `HVDVD_TS/` (`e06`). Authoring debris; ignore.
`[11, 12]` **VERIFIED**

## 1.5 `ADV_OBJ/`: files

| Pattern | Listed | Role | Layout |
|---|---|---|---|
| `DISCID.DAT` | 119 | Config File, always 128 bytes | [02_discid.md](02_discid.md) |
| `VPLST$$$.XPL` | 247 | Playlist. `$$$` = 000–999 | [03_playlist.md](03_playlist.md) |
| `VPLST$$$.BAK` | 3 | Not in the boot search (`.XPL` only) | ignore for boot |
| `APLST###.XPL` | 0 | Audio-only playlist | unused |
| `*.ACA` | 409 | Application archive | [04_aca.md](04_aca.md) |
| `*.XMF` | 3 loose + inside ACA | Manifest | [05_manifest_hdi.md](05_manifest_hdi.md) |
| `*.XMU` | 2 loose + inside ACA | HDi markup | [05](05_manifest_hdi.md) |
| `*.JS` | 3 loose + inside ACA | ECMAScript | [05](05_manifest_hdi.md) |
| `*.PNG` | 72 | Icons / resources | standard PNG |
| `*.TTF` | 1 loose | Font | standard |
| `*.CER` | 10 | **Standard X.509 DER certificates** (`30 82…`). TLS trust anchors for the HDi network layer (`IHTTPClient`/HTTPS to studio servers). Sample `dynamichd.cer` = *Thawte Premium Server CA* root [15]. Not AACS `CONTENT_CERT`. **Not used by linear playback.** Ignore. | X.509 |
| `Thumbs.db` | 2 | Junk | ignore |

`[11, 12]` **VERIFIED**

## 1.6 Disc URI

Players resolve assets as:

```
file:///dvddisc/ADV_OBJ/DISCID.DAT
file:///dvddisc/ADV_OBJ/VPLST000.XPL
file:///dvddisc/HVDVD_TS/FEATURE_1.MAP
file:///dvddisc/ADV_OBJ/menus.aca/MainMenu.xmf
```

`file:///dvddisc` is the UDF volume root.

Patent FIG.20 **drawing** (`US20070091495A1` `pages/page-024.png`) also lists
`file:///filecache/`, `file:///required/`, `file:///additional/`,
`file:///common/required/`, `file:///common/additional/`. The **same patent’s
prose** writes `file:///fixed/` and `file:///removable/` instead. Playlist.xsd
`DataSourceType` is `Disc` / `P-Storage` / `Network` / `FileCache`. Corpus `src`
is all `file:///dvddisc/` (**10 620 / 10 620** playlist `src`, `e12`). The persistent-storage **script** URI form is specified:
`file:///required/{contentId}/` ([05](05_manifest_hdi.md) §5.8); on the storage medium the player
nests it as `/HD_DVD/<PROVIDER_DIR>/<CONTENT_ID>/`, with `PROVIDER_DIR` derived from
`PROVIDER_ID` and the DKF key [4 §6.3] ([05](05_manifest_hdi.md) §5.8).
`[11, 12]` **VERIFIED** (`dvddisc` only)
`[1]`
