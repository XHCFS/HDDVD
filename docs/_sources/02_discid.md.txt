# 2. DISCID.DAT: Config File

*Counts written "N/120", "N/119", "on N discs", "listings", or as named discs are over the reference corpus of 120 archived retail HD DVD images [11]. `eNN` are the reproducible verification experiments [12].*


Path: `ADV_OBJ/DISCID.DAT`  
Size: **128 bytes** on 119/119 Advanced discs  
Magic: `HDDVD-V_CONF`  
This is **not** AACS Volume ID.

The Playlist Manager reads this **before** choosing a playlist.

`[11, 12]` **VERIFIED**
`[1]`

## 2.1 Layout

All fields big-endian where numeric. Strings are ASCII, not necessarily NUL-terminated
if they fill the field.

| Offset | Size | Field | Rule |
|---|---|---|---|
| 0 | 12 | `ID` | `"HDDVD-V_CONF"` |
| 12 | 16 | Disc ID (network) | `0xFF`×16 on 109 discs; UUID on 10. **Not** Volume ID. |
| 28 | 16 | `PROVIDER_ID` | ASCII studio tag or 16-byte binary. Input to the persistent-storage provider directory name (below). |
| 44 | 16 | `CONTENT_ID` | 16-byte UUID |
| 60 | 1 | `SEARCH_FLG` | `0` = also search persistent storage for `VPLST$$$.XPL`; `1` = disc only |
| 61 | 67 | reserved | zeros |

`SEARCH_FLG`: 0 on 106 discs, 1 on 13. No other values (`e14`).
Reserved 61–127: **zeros 119/119** (`e11`). A non-zero byte is a different format
version. Fail closed.

Disc ID @12: `0xFF`×16 on **109**, other (UUID-shaped) on **10** (`e14`).
`PROVIDER_ID`: 9 distinct ASCII tags (95 discs) + **24 binary**. Binary shapes
include all-`FF`, UUID-like 16 bytes, and mixed (`BROTHERS_GRIMM` ends `SLY`).
On an AACS disc the provider's persistent-storage directory is **not** named
`PROVIDER_ID`: it is `PROVIDER_DIR = AES-G(KDIR, PROVIDER_ID)` written as a GUID,
with `KDIR` from the DKF ([09](09_aacs.md) §9.4, [4 §6.3]). Scripts never see it; they
use `file:///required/{contentId}/` ([05](05_manifest_hdi.md) §5.8).

## 2.2 Observed `PROVIDER_ID` tags (ASCII)

`WHV***V1**HD-DVD` (25), `UNIVERSAL_HD-DVD` (22), `UNIVERSAL_HD-SLY` (18),
`PARAMOUNT_HD-DVD` (12), `PARAMOUNT_HD-SLY` (8), `WHV***V1**HD-SLY` (7),
plus `NEWLINE_HDDVD_V1`, `DREAMWORKS_HDDVD`, `DW_ANIM___HD-SLY`, and 24 binary IDs.

**`SLY` is not an authored value.** Every `PROVIDER_ID` ending in ASCII `SLY` (33
discs: the `-SLY` tags and five binary IDs ending `534c59`) differs from the DISCID
the disc's AACS hash table committed to; restoring `DVD` (or the recovered original
bytes) makes the hash match. These DISCIDs were rewritten after authoring, when the
image was processed; see [09](09_aacs.md) §9.2. Only the other 86 tags are as pressed.
`[11]` **VERIFIED** (`e22`)

## 2.3 Player use

1. Read `PROVIDER_ID`, `CONTENT_ID`, `SEARCH_FLG`.
2. If `SEARCH_FLG == 0`, search persistent storage for `VPLST000.XPL`…`VPLST999.XPL`
   under that provider/content.
3. Search `ADV_OBJ/` (not subdirectories) for `VPLST$$$.XPL`.
4. Open the file with the **highest** `$$$` among files that exist.
   Empty persistent storage under `SEARCH_FLG=0` still boots the disc playlist.

See [10_playback.md](10_playback.md).
`[1]`
`[11, 12]` **VERIFIED** (disc half). P-storage search **INFERRED** (0 specimens).
