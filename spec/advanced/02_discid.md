# 2. DISCID.DAT: Config File

*Counts written "N/120", "N/119", "on N discs", "listings", or as named discs are over the reference corpus of 120 archived retail HD DVD images [11]. `eNN` are the reproducible verification experiments [12].*


Path: `ADV_OBJ/DISCID.DAT`  
Size: **128 bytes** on 119/119 Advanced discs  
Magic: `HDDVD-V_CONF`  
This is **not** AACS Volume ID.

The book calls it the Configuration File. It is required directly in `ADV_OBJ/` on
every Category 2 and 3 disc. It names the disc's area in persistent storage and
identifies the disc to a network server [23 §6.6]. Its presence is what marks a
disc as Category 2 or 3 [23 §4.1.1].

The Playlist Manager reads this **before** choosing a playlist.

`[11, 12]` **VERIFIED**
`[1]` `[23 §6.6]`

## 2.1 Layout

All fields big-endian where numeric. Strings are ASCII, not necessarily NUL-terminated
if they fill the field.

| Offset | Size | Field | Rule |
|---|---|---|---|
| 0 | 12 | `CONFIG_ID` | `"HDDVD-V_CONF"`, ISO 8859-1 |
| 12 | 16 | `DISC_ID` | Disc ID for the network, binary GUID [23 §9]. All `0xFF` if the disc uses no network. **Not** Volume ID. |
| 28 | 16 | `PROVIDER_ID` | Provider ID, binary GUID [23 §10.2]. All `0xFF` if the disc uses no provider directory in persistent storage. Discs: ASCII studio tag or 16-byte binary (below). Input to the persistent-storage provider directory name. |
| 44 | 16 | `CONTENT_ID` | Content ID, binary GUID [23 §10.2]. All `0xFF` if the provider directory is not used. |
| 60 | 1 | `SEARCH_FLG` | Bit 0: `0` = search persistent storage and the disc for the startup playlist; `1` = disc only. Bits 7–1 reserved. Must be `1` when `PROVIDER_ID` and `CONTENT_ID` are all `0xFF` |
| 61 | 67 | reserved | zeros |

The three IDs are stored as 16 binary bytes, not as text [23 §6.6]. Shown to people
and in paths, a GUID is the RFC 4122 string in upper case, for example
`F81D4FAE-7DEC-11D0-A765-00A0C91E6BF6` [23 §10.2].

`SEARCH_FLG`: 0 on 106 discs, 1 on 13. No other values (`e14`). A player in
Restricted Mode treats it as `1` ([10](10_playback.md), [23 Annex X.4.2]).
Reserved 61–127: **zeros 119/119** (`e11`). A non-zero byte is a different format
version. Fail closed.

Disc ID @12: `0xFF`×16 on **109**, other (UUID-shaped) on **10** (`e14`).
`PROVIDER_ID`: 9 distinct ASCII tags (95 discs) + **24 binary**. Binary shapes
include all-`FF`, UUID-like 16 bytes, and mixed (`BROTHERS_GRIMM` ends `SLY`).
The book wants a binary GUID [23 §6.6]; the ASCII tags are still 16 bytes and work
the same way. The book names the provider's persistent-storage directory with the
Provider ID [23 §10.3.2]. On an AACS disc it is **not** named `PROVIDER_ID`: it is
`PROVIDER_DIR = AES-G(KDIR, PROVIDER_ID)` written as a GUID, with `KDIR` from the
DKF ([09](09_aacs.md) §9.4, [4 §6.3]). Scripts never see it; they
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

The book's startup sequence [23 §4.3.22.2, §10.3.2]:

1. Read `PROVIDER_ID`, `CONTENT_ID`, `SEARCH_FLG`.
2. If the player is connected to a display, look for `VPLST$$$.XPL`; otherwise for
   `APLST###.XPL` (same steps, `000`–`999`).
3. If `SEARCH_FLG == 0`, search every connected persistent storage device for
   `/HD_DVD/<Provider ID>/<Content ID>/VPLST$$$.XPL`.
4. Search `ADV_OBJ/` (not subdirectories) for `VPLST$$$.XPL`.
5. Open the file with the **highest** `$$$` among all files found.
   Empty persistent storage under `SEARCH_FLG=0` still boots the disc playlist.
   No `VPLST` at all: run the same search for `APLST`. Neither: failure, and what
   happens next is up to the player.

A playlist read from persistent storage comes with its Assignment Information File
(`VPSAI$$$.TXT` / `APSAI###.TXT`, same directory, same number), which maps Base Paths
to additional storage devices [23 §10.6]. In Restricted Mode the persistent-storage
search is skipped, and a persistent-storage playlist must be signed like the disc
[23 Annex X.2.1, X.4.2].

See [10_playback.md](10_playback.md).
`[1]` `[23 §4.3.22.2]`
`[11, 12]` **VERIFIED** (disc half). P-storage search **SPEC** [23]; 0 specimens.
