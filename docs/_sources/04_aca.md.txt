# 4. ACA: Advanced Content Archive

*Counts written "N/120", "N/119", "on N discs", "listings", or as named discs are over the reference corpus of 120 archived retail HD DVD images [11]. `eNN` are the reproducible verification experiments [12].*


Path: `ADV_OBJ/*.ACA` (409 listed).  
Magic: `HDDVDACA`  
Referenced as `file:///dvddisc/ADV_OBJ/foo.aca` and as
`file:///dvddisc/ADV_OBJ/foo.aca/manifest.xmf`.

The book calls it an **archiving file** [23 §6.5.4]. It packs files uncompressed
so that they load into the File Cache as one item, and it is the only kind of file
the Advanced Stream (ADV_PCK, [08](08_evo.md) §8.6) carries. It may hold playlists,
manifests, markup (content, timing, style), Advanced Subtitle markup, scripts,
images, effect audio, fonts, and Secondary Video Set EVOBs and time maps. It may
not hold another archive, a certificate or a time-map backup. An archive that is
multiplexed into a P-EVOB is also stored under `ADV_OBJ/` with the same name.

In the File Cache an archive is stored whole, and its members are read in place
(§4.4). At most 2048 members; archive and member names at most 255 characters
[23 §4.3.20.5].

Header checks from the reference decoder (`HDDVDPLAYDLL`):

- magic is not `HDDVDACA` → reject
- version is not 1.0 → reject
- file type is not 0 → reject
- encoding type is not 1 → reject
- size less than header → reject
- per-entry CRC mismatch → reject (reference decoder). On this corpus, CRC of
  the raw member matches **only** when the member's MIME type code is not `0xff`;
  extract `0xff` members by offset/length and do not treat those CRCs as a
  raw-payload check.

File type 0 = uncompressed members; encoding type 1 = member names in ISO 8859-1
[23 §6.5.4.1.1]. These are two one-byte fields.

**Directory is not a fixed 58-byte stride.** A 58-byte MATRIX record is
`14 + namelen + 32` when the name is 12 characters (`manifest.xmf`). The same
formula parses **every member of every saved archive**: 885 members across 97
`*.aca` files, each with the name-length byte equal to `len(name)`, a 32-byte zero
pad, and CRC-matches-iff-MIME-code-≠-`0xff`.
`[11]` `[23 §6.5.4.1.2]`
**VERIFIED**. MIME code `0xff` on 868/885 (AACS-wrapped, CRC not a raw
check); `0x02` (3 `xmf`), `0x03` (5 `xmu`), `0x04` (1 `xts`), `0x07` (8 `js`) on the
other 17, each matching its name's extension, and their CRCs match the raw member.

## 4.1 Archive header

Big-endian. Total header before the directory is 32 bytes.

| Offset | Size | Field | Observed / required [23 §6.5.4.1.1] |
|---|---|---|---|
| 0 | 8 | `FILE_ID` | `"HDDVDACA"` |
| 8 | 2 | `VERN` | `0x0010` (1.0) on 97/97 |
| 10 | 1 | `FILE_TY` | `0x00` = uncompressed (the only value); 97/97 |
| 11 | 1 | `ENC_TY` | `0x01` = names in ISO 8859-1 (the only value); 97/97 |
| 12 | 2 | `SRP_Ns`, entry count `N` | 2–40 on the 97 saved archives |
| 14 | 4 | `FILE_SZ`, total size in bytes | equals file length on 97/97. The book allows `0` = unknown |
| 18 | 14 | reserved | zero on all 97 |
| 32 | … | directory (search pointers) | then member payloads |

## 4.2 Directory entry (variable length)

Walk `N` records starting at byte 32. The book calls each one a Resource Data
Search Pointer [23 §6.5.4.1.2]. Big-endian:

| Offset | Size | Field |
|---|---|---|
| 0 | 4 | `DATA_SA`, member byte offset from start of file |
| 4 | 4 | `DATA_SZ`, member length |
| 8 | 4 | `DATA_CRC`, CRC-32 of the member bytes (ISO 3309 / ITU-T V.42: polynomial `04C11DB7`, the zlib `crc32`), when it is valid |
| 12 | 1 | `DATA_MIME_TY`, MIME type code (table below). `0xff` on AACS-wrapped members |
| 13 | 1 | `DATA_FNAME_LEN`, **name length** |
| 14 | `namelen` | `DATA_FNAME`, member name, ISO 8859-1, no NUL inside the counted length |
| 14+`namelen` | 32 | reserved, **all zero** on 885/885 |

Record size = `46 + namelen`.

| Code | MIME type | Extension |
|---|---|---|
| `0x00` | reserved | |
| `0x01` | `text/hddvdpl+xml` | `xpl` |
| `0x02` | `text/hddvdmf+xml` | `xmf` |
| `0x03` | `text/hddvdmu+xml` | `xmu` |
| `0x04` | `text/hddvdts+xml` | `xts` |
| `0x05` | `text/hddvdas+xml` | `xas` |
| `0x06` | `text/hddvdvss+xml` as printed in the archive table; §3.3.5 writes `text/hddvdss+xml` | `xss` |
| `0x07` | `application/ecmascript` | `js` |
| `0x08` | `video/evob` | `evo` |
| `0x09` | `application/tmap` | `map` |
| `0x0A` | `image/jpeg` | `jpg` |
| `0x0B` | `image/png` | `png` |
| `0x0C` | `image/mng` | `mng` |
| `0x0D` | `image/cvi` | `cvi` |
| `0x0E` | `image/cdw` | `cdw` |
| `0x0F` | `audio/x-wav` | `wav` |
| `0x10` | `application/font` | `otf` `ttf` `ttc` |
| `0x11`–`0xFE` | reserved | |
| `0xFF` | `application/x-data`, any other data | |

On disc every member whose bytes are AACS-wrapped is typed `0xFF`, whatever its
name says (`js` 111, `png` 585, `ttf` 7, `xas` 2, `xmf` 83, `xmu` 77, `xts` 1,
`xul` 2). The type of a member is its name's extension once it is unwrapped
([01](01_volume.md) §1.5).

Then `pos += record size` and parse the next entry. First member offset is the
u32 at byte 32, **not** `32 + 58×N`.

| Archive | N | Formula holds | CRC matches raw bytes | Gap before first payload |
|---|---|---|---|---|
| `STALINGRAD` `mainApp.aca` | 9 | yes | **9/9** (MIME code `0x02`–`0x07`) | 0 (directory ends at first payload) |
| `MATRIX_REVOLUTIONS` `selector.aca` | 2 | yes | 0/2 (`0xff`) | 283 |
| `BLADE_RUNNER` `selector.aca` | 3 | yes | 0/3 (`0xff`) | 283 |
| `TRAINING_DAY` `selector.aca` | 3 | yes | 0/3 (`0xff`) | 283 |
| `PREMONITION_GER` `client.aca` | 6 | yes | 0/6 (`0xff`) | 283 |
| `SHREK_THE_THIRD_EU` `shrekcoloring_code.aca` | 7 | yes | 0/7 (`0xff`) | 283 |

IEEE CRC-32 of the slice `[offset, offset+length)` matches the stored CRC **iff**
the MIME code is not `0xff`. On `0xff` members the stored CRC is not the
raw-payload CRC (likely a wrapped/AACS digest). Extract anyway by offset/length;
do not reject the archive because those CRCs fail.

The 283-byte gap (`0xff` archives) is an **AACS per-member content-protection
descriptor**, parsed from the bytes (`PANS_LABYRINTH gal_common.aca` and the five
selector/client archives):

```
0   4   "AACS"
4   2   0x0200        version
6   2   0x0100        subtype
8   3   len/flags     (e.g. 00 23 11)
11  var  "<member>.AACS"   protected member name + ".AACS", NUL-terminated
...      zero pad to 283
```

It names the first/protected member's `<name>.AACS` sidecar; it is **not** extra
entries in `N`. Its inner length/flags meaning is the AACS layer's, not the ACA's;
linear extract by offset/length does not need it.

**Refuted:** fixed 58-byte name field. It only looked true on MATRIX because
the first name is 12 bytes (`14+12+32=58`); the second MATRIX name is 9 bytes
(record 55). PREMONITION/SHREK/STALINGRAD names vary (7–20 bytes).

## 4.3 Members

| Name | Content |
|---|---|
| `*.xmf` | Manifest XML ([05](05_manifest_hdi.md)) |
| `*.xpl` | Playlist (allowed by the book; 0 on disc) |
| `*.xmu` | HDi markup |
| `*.js` | ECMAScript. **UTF-16BE with BOM `FE FF`** on every saved file (`e15` N≥77, including three loose `1408`; 122/122 readable scripts in 2026-10), which is what the book requires [23 §8.2.1]. The earlier “1408 loose JS is UTF-8” claim is **refuted**. |
| `*.xas` | Advanced Subtitle markup (empty iHD stub on HOT_FUZZ / ARMY_OF_SHADOWS) |
| `*.xts` | Timing-only iHD document (`include` target) |
| `*.xul` | Mozilla XUL, **not** iHD (PANS_LABYRINTH). Ignore in the HDi engine. |
| fonts, PNG, etc. | as named |

Extract: for each entry, slice `[offset, offset+length)`. CRC-check that slice
when the MIME code is not `0xff`.

## 4.4 Namespace

XPL writes:

```
ApplicationSegment src="file:///dvddisc/ADV_OBJ/menus.aca/MainMenu.xmf"
ApplicationResource src="file:///dvddisc/ADV_OBJ/menus.aca" size="…" multiplexed="false"
```

Resolve `foo.aca/bar.xmf` by opening `ADV_OBJ/foo.aca` and taking directory name
`bar.xmf`. The resource line names the whole archive (preload into File Cache).
The book's general form is `file:///<source>/<archive>/<member>`, for any data
source; the File Cache gives script and markup direct access to members of a
cached archive [23 §4.3.20.4].
