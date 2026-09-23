# 6. HVA00001.VTI: Advanced VTSI

*Counts written "N/120", "N/119", "on N discs", "listings", or as named discs are over the reference corpus of 120 archived retail HD DVD images [11]. `eNN` are the reproducible verification experiments [12].*


Path: `HVDVD_TS/HVA00001.VTI`  
One file per Advanced disc (119/119).  
Magic: `ADVANCED-VTS`  
`VERN`: `0x0010`  
`VTSI_EA` == (file sectors − 1) on 119/119.

Patent: US20080298219A1 TABLE 77. Disc agrees on identifiers and the SA fields below.

Addresses `*_SA` are **sector** numbers from the start of this file (× 2048 = byte).

## 6.1 VTSI_MAT (first 2048 bytes)

| RBP | Size | Field | Value |
|---|---|---|---|
| 0 | 12 | `VTS_ID` | `"ADVANCED-VTS"` |
| 12 | 4 | `VTS_EA` | patent: end of VTS as RLBN. **Disc: `0` on 119/119** (`e14`). EVOBs are separate files (`VTS_EVOBS_SA=0`). Do not add this to pack addresses. |
| 16 | 12 | reserved | 0 |
| 28 | 4 | `VTSI_EA` | last sector of this file |
| 32 | 2 | `VERN` | `0x0010` |
| 34 | 4 | `VTS_CAT` | **2** = Advanced VTS (`0010b` application type) |
| 38 | 90 | reserved | 0 |
| 128 | 4 | `VTSI_MAT_EA` | end of this MAT |
| 132 | 52 | reserved | 0 |
| 184 | 4 | `VTS_EVOB_ATRT_SA` | **1** on 119/119 (ATRT starts at byte 2048) |
| 188 | 4 | `VTS_EVOBIT_SA` | varies (sector of EVOBI table) |
| 192 | 4 | reserved | 0 |
| 196 | 4 | `VTS_EVOBS_SA` | **0** on 119/119 (EVOBs are separate `.EVO` files) |
| 200 | 1848 | reserved | 0 |

## 6.2 VTS_EVOB_ATRT (at `VTS_EVOB_ATRT_SA` × 2048)

DVD-style search table, 1024-byte entries.

| Offset | Size | Field |
|---|---|---|
| 0 | 2 | `nr` number of ATRI |
| 2 | 2 | reserved |
| 4 | 4 | `last_byte` |
| 8 | 4×`nr` | start offsets of each ATRI (from start of this table) |

First offset is always `8 + 4×nr`.  
`(last_byte+1 − first_SA) / nr = 1024` on every specimen.

### ATRI (1024 bytes)

| Offset | Size | Field |
|---|---|---|
| 0 | 2 | flags | `0000` on 987/1131, `1000` on 125, rare `0500`/`0400` |
| 2 | 4 | `V_ATR` | TABLE 9/16 video-attribute word (big-endian) |
| 6 | 4 | extra attr / reserved | **zero on 1112/1131**. 19 ATRIs store a second 4-byte word here (`60105000` ×12, `63105000` ×3, `40105040` ×2, `63015000`, `60005000`); bytes 10–13 stay zero. Official name **OPEN** |
| 10 | 4 | reserved | zero on 1131/1131 |
| 14 | 2 | `AST_Ns` | audio-stream count. Histogram: 1 (793), 0 (136), 2 (59), 3 (42), … |
| 16 | 4×`AST_Ns` | `AST_ATR` | 4-byte words. Bytes `16+4×AST_Ns … 79` are zero on **1131/1131** |
| 80 | 149 | mid-slot | **zero on 1115/1131**. **16/1131** store `01 1c 00 c4` at offset **193** (BATMAN, PANS, T2 GER, 40YR, TRANSFORMERS, …). Official name **OPEN**. Do not assume 80–228 is unused padding |
| 229 | 1 | `SP_Ns` | sub-picture count (`0` on 826/1131) |
| 230 | 5×`SP_Ns` | `SP_ATR` | 5-byte words, one per stream: byte 0 = `80h` (bits 7–5 = coding mode `100b`, 8-bit SPU, [08](08_evo.md) §8.8), byte 1 = `20h` + stream index (the stream's `sub_stream_id`), bytes 2–4 zero. 1258/1258 (`e25`) |

`AST_Ns` is **not** at +6 (that slot is usually zero; never the stream count).
Decoder setup still follows the playlist, not these ATR words.
`[11, 12]` **VERIFIED**

**SP palettes: uncloseable as a named table.** After `SP_ATR`, 1124/1131 ATRIs
are zero through the rest of the 1024-byte slot. 7 ATRIs (`DOOM`, `GOODFELLAS`,
`LAST_SAMURAI`, `U2_RATTLE_AND_HUM`) fill 32×4-byte words from offset **391**
with `7f7f7f00` (dummy gray, not a Y/Cr/Cb palette). No specimen has a
DVD-style 16-colour YCrCb palette in the ATRI, and none is needed: the sub-picture
colour/contrast comes from the `83h` colour-table and `84h` contrast-table commands in the
SP_DCSQ ([08](08_evo.md) §8.8), not from the ATRI. The ATRI palette slot being unused is
expected, not a decoder gap.
`[11, 12]` **OPEN** / uncloseable from this corpus.

`V_ATR` bit fields (MSB = bit 31 of the u32). Layout from patent figures C00003 / C00008
(C00008 names b16 **Film camera mode**; C00003 leaves b17–16 reserved):

| Bits | Field | Disc |
|---|---|---|
| 31–30 | compression | `01b` MPEG-2 ×692, `00b` reserved ×439, **`10b` AVC = 0, `11b` VC-1 = 0** of 1131. Feature VC-1/AVC is in the XPL, never here. **Use the playlist.** |
| 29–28 | TV system | often `10b` HD/60 |
| 27–26 | aspect | `10b` on 1920×1080; patent only defines `00b` 4:3 / `11b` 16:9; treat `10b` as 16:9 HD |
| 25–24 | display mode | `11b` ×764, `00b` ×367 (`e14`) |
| 23, 22 | CC1, CC2 | patent field; not separately histogrammed |
| 21–20 | source progressive | `00b` ×552, `01b` ×506, `10b` ×73 (`e14`) |
| 18 | source letterboxed | **0** on 1131/1131 |
| 16 | film camera (C00008 only) | **0** on 1131/1131 |
| 15–12 | source resolution | `1100b` 1920×1080 (677), `0101b` 720×480/576 (451), `0000b` 352×240/288 (3) |

WO FIG.111 draws ATRI as `V_ATR`, `AST_Ns`, `AST_ATR`, `MU_AST_ATR`, `SPST_*`, palettes,
a **logical tree**, not these 1024-byte offsets. C00010’s 64-bit `A_ATR` is not the
4-byte disc `AST_ATR`. Observed 4-byte words (`e14`, 9 unique): `1c00c400` ×878,
`1c00d400` ×474, plus 7 rarer. Bit layout vs C00010’s 64-bit `A_ATR` remains **OPEN**.
Language is not in this word (XPL `langcode`).

## 6.3 VTS_EVOBIT (at `VTS_EVOBIT_SA` × 2048)

320-byte entries. `nr` equals `.MAP` count on 117/119 discs
(exceptions: `PANS_LABYRINTH` extra EVOBIs for angles; `ETERNAL_SUNSHINE` 28 EVOBI vs 29 MAP; extra is `DELEXT8`, not in VTI).

| Offset | Size | Field |
|---|---|---|
| 0 | 2 | reserved |
| 2 | 2 | `nr` |
| 4 | 4 | `last_byte` |
| 8 | 4×`nr` | start offsets |

First offset = `8 + 4×nr`.

### EVOBI (320 bytes)

| Offset | Size | Field |
|---|---|---|
| 0 | 2 | type/flags | `0x2000` on 2431/2431 (same as contiguous `TMAP_TY`) |
| 2 | 36 | EVOB **filename** | ASCII, usually NUL-padded. **1/2431** fills all 36 with no NUL (`SMOKEY_AND_THE_BANDIT` `SMOKEYANDBANDIT_LOADEDUPMPEG2_HD.EVO`). Match a listed `.EVO` |
| 38 | 226 | reserved | zero |
| 264 | 2 | `EVOB_ATRN` | 1-based ATRI index; 2431/2431 in `1…nr` |
| 266 | 4 | EVOB start PTM (90 kHz) | matches PCI `vobu_s_ptm` of VOBU0 on DOWNFALL |
| 270 | 4 | EVOB end PTM | two-part features: part2 start = part1 end |
| 274 | 4 | EVOB size in **packs** | equals listing `.EVO` size / 2048 on **2416/2431**. The 15 misses are `PANS_LABYRINTH` interleaved angles (several EVOBI share one EVO file; each row is one angle’s pack count, not the whole file) |
| 278 | 2 | EVOB serial | 1-based. Equals table position on 2419/2431; `SPARTACUS` skips number 12 (idx = position+1 after that hole) |
| 280 | 2 | reserved | 0 |
| 282 | 4 | part/layer start | `0` on first/only parts. Non-zero on 100 rows, almost all `FEATURE_2` / `PEVOB_2` / dual-layer tails. `0x80000000` on some part-2 rows (layer-1 flag). Not the PTM. **Units / official name uncloseable** |
| 286 | 16 | | `0xFF`×16 |
| 302 | 18 | reserved | zero |

There is **no** MAP filename in EVOBI. Playlist `src` is the MAP; EVOBI names the EVO.
Same basename: `FEATURE_1.MAP` ↔ `FEATURE_1.EVO`.
WO FIG.112 labels the third field `TMAP_FILE_NAME`. **Disc wins** (`.EVO` name at +2).
