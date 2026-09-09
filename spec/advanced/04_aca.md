# 4. ACA: Advanced Content Archive

*Counts written "N/120", "N/119", "on N discs", "listings", or as named discs are over the reference corpus of 120 archived retail HD DVD images [11]. `eNN` are the reproducible verification experiments [12].*


Path: `ADV_OBJ/*.ACA` (409 listed).  
Magic: `HDDVDACA`  
Referenced as `file:///dvddisc/ADV_OBJ/foo.aca` and as
`file:///dvddisc/ADV_OBJ/foo.aca/manifest.xmf`.

Header checks from the reference decoder (`HDDVDPLAYDLL`):

- magic is not `HDDVDACA` → reject
- version is not 1.0 → reject
- file type is not 0 → reject
- encoding type is not 1 → reject
- size less than header → reject
- per-entry CRC mismatch → reject (reference decoder). On this corpus, CRC of
  the raw member matches **only** when `flags` high byte is not `0xff`; extract
  `0xff` members by offset/length and do not treat those CRCs as a raw-payload check.

Encoding type 1 is treated as **uncompressed** members (XML, JS, TTF magics).

**Directory is not a fixed 58-byte stride.** A 58-byte MATRIX record is
`14 + namelen + 32` when the name is 12 characters (`manifest.xmf`). The same
formula parses **every member of every saved archive**: 885 members across 97
`*.aca` files, each satisfying `flags & 0xFF == len(name)`, 32-byte zero pad,
and CRC-matches-iff-`flags`-high-byte-≠-`0xff`.
`[11]`
**VERIFIED**. `flags` high byte `0xff` on 868/885 (AACS-wrapped, CRC not a raw
check); `0x02`–`0x07` on the other 17 (CRC matches the raw member).

## 4.1 Archive header

Big-endian. Total header before the directory is 32 bytes.

| Offset | Size | Field | Observed / required |
|---|---|---|---|
| 0 | 8 | magic | `"HDDVDACA"` |
| 8 | 2 | `VERN` | `0x0010` (1.0) |
| 10 | 2 | encoding type | `1` |
| 12 | 2 | `N` entry count | 2–10 on saved files (`archive2.aca` = 10) |
| 14 | 4 | total size | equals file length |
| 18 | 14 | remainder of 32-byte header | file type `0`; zero on all 97 |
| 32 | … | directory | then member payloads |

## 4.2 Directory entry (variable length)

Walk `N` records starting at byte 32. Each record is big-endian:

| Offset | Size | Field |
|---|---|---|
| 0 | 4 | member byte offset from start of file |
| 4 | 4 | member length |
| 8 | 4 | CRC-32 (ISO 3309 / zlib) of the member bytes, when it is valid |
| 12 | 2 | `flags`. Low 8 bits = **name length**. High 8 bits: `0xff` on AACS-wrapped members; `0x02`–`0x07` on STALINGRAD |
| 14 | `namelen` | member name, ASCII, no NUL inside the counted length |
| 14+`namelen` | 32 | padding, **all zero** on 885/885 |

Record size = `46 + namelen` = `14 + (flags & 0xFF) + 32`.

Then `pos += record size` and parse the next entry. First member offset is the
u32 at byte 32, **not** `32 + 58×N`.

| Archive | N | Formula holds | CRC matches raw bytes | Gap before first payload |
|---|---|---|---|---|
| `STALINGRAD` `mainApp.aca` | 9 | yes | **9/9** (`flags` high byte `0x02`–`0x07`) | 0 (directory ends at first payload) |
| `MATRIX_REVOLUTIONS` `selector.aca` | 2 | yes | 0/2 (`0xff`) | 283 |
| `BLADE_RUNNER` `selector.aca` | 3 | yes | 0/3 (`0xff`) | 283 |
| `TRAINING_DAY` `selector.aca` | 3 | yes | 0/3 (`0xff`) | 283 |
| `PREMONITION_GER` `client.aca` | 6 | yes | 0/6 (`0xff`) | 283 |
| `SHREK_THE_THIRD_EU` `shrekcoloring_code.aca` | 7 | yes | 0/7 (`0xff`) | 283 |

IEEE CRC-32 of the slice `[offset, offset+length)` matches the stored CRC **iff**
the flags high byte is not `0xff`. On `0xff` members the stored CRC is not the
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
| `*.xmu` | HDi markup |
| `*.js` | ECMAScript. **UTF-16BE with BOM `FE FF`** on every saved file (`e15` N≥77, including three loose `1408`). The earlier “1408 loose JS is UTF-8” claim is **refuted**. |
| `*.xas` | Advanced Subtitle markup (empty iHD stub on HOT_FUZZ / ARMY_OF_SHADOWS) |
| `*.xts` | Timing-only iHD document (`include` target) |
| `*.xul` | Mozilla XUL, **not** iHD (PANS_LABYRINTH). Ignore in the HDi engine. |
| fonts, PNG, etc. | as named |

Extract: for each entry, slice `[offset, offset+length)`. CRC-check that slice
when `flags` high byte is not `0xff`.

## 4.4 Namespace

XPL writes:

```
ApplicationSegment src="file:///dvddisc/ADV_OBJ/menus.aca/MainMenu.xmf"
ApplicationResource src="file:///dvddisc/ADV_OBJ/menus.aca" size="…" multiplexed="false"
```

Resolve `foo.aca/bar.xmf` by opening `ADV_OBJ/foo.aca` and taking directory name
`bar.xmf`. The resource line names the whole archive (preload into File Cache).
