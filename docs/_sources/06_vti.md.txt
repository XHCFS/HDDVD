# 6. HVA00001.VTI: Advanced VTSI

*Counts written "N/120", "N/119", "on N discs", "listings", or as named discs are over the reference corpus of 120 archived retail HD DVD images [11]. `eNN` are the reproducible verification experiments [12].*


Path: `HVDVD_TS/HVA00001.VTI`  
One file per Advanced disc (119/119).  
Magic: `ADVANCED-VTS`  
`VERN`: `0x0010`  
`VTSI_EA` == (file sectors − 1) on 119/119.

The book's layout is [23 §6.3.1]; the patent (US20080298219A1 TABLE 77) agrees on
identifiers and the SA fields. The VTSI is three tables, each starting on a sector
boundary and followed by up to 2047 zero bytes: `VTSI_MAT`, `VTS_EVOB_ATRT`,
`VTS_EVOBIT`. A backup `HVA00001.BUP` may follow the same layout; the VTSI and its
backup are never in the same ECC block [23 §3.3].

Addresses `*_SA` and `VTSI_EA` are **sector** numbers (RLBN) from the start of this
file (× 2048 = byte). `*_EA` inside a table and the search pointers are **byte**
offsets (RBN) from the start of that table.

## 6.1 VTSI_MAT (1024 bytes, padded to 2048)

| RBP | Size | Field | Value |
|---|---|---|---|
| 0 | 12 | `VTS_ID` | `"ADVANCED-VTS"`, ISO 8859-1 |
| 12 | 16 | reserved | 0 on 119/119. The patent calls 12–15 `VTS_EA`; the book reserves it. Do not add it to pack addresses |
| 28 | 4 | `VTSI_EA` | last sector of the VTSI (= file sectors − 1 on 119/119) |
| 32 | 2 | `VERN` | b7–b0 book version, `0x10` = 1.0; b15–b8 reserved. `0x0010` on 119/119 |
| 34 | 4 | `VTS_CAT` | b3–b0 application type: `0010b` Advanced VTS, `0011b` Interoperable VTS; the rest reserved. **2** on 119/119 |
| 38 | 90 | reserved | 0 |
| 128 | 4 | `VTSI_MAT_EA` | end of this table, byte offset |
| 132 | 52 | reserved | 0 |
| 184 | 4 | `VTS_EVOB_ATRT_SA` | **1** on 119/119 (ATRT starts at byte 2048) |
| 188 | 4 | `VTS_EVOBIT_SA` | varies (sector of the EVOBI table) |
| 192 | 832 | reserved | 0. The patent calls 196–199 `VTS_EVOBS_SA`; the book reserves it (EVOBs are separate `.EVO` files). 0 on 119/119 |
| 1024 | 1024 | padding to the sector | 0 on 119/119 |

## 6.2 VTS_EVOB_ATRT (at `VTS_EVOB_ATRT_SA` × 2048)

| Offset | Size | Field |
|---|---|---|
| 0 | 2 | `VTS_EVOB_ATR_Ns`, number of attribute records, 1–511 |
| 2 | 2 | reserved |
| 4 | 4 | `VTS_EVOB_ATRT_EA`, last byte of the table |
| 8 | 4×`Ns` | `VTS_EVOB_ATR_SA`, byte offset of each record from the start of this table |

First offset is always `8 + 4×Ns`.
`(last_byte+1 − first_SA) / Ns = 1024` on every specimen. One record may serve
several EVOBs; the EVOBs of an interleaved block for seamless angle change share
one record [23 §6.3.1.2].

### VTS_EVOB_ATR (1024 bytes)

| Offset | Size | Field | Disc (1131 records) |
|---|---|---|---|
| 0 | 2 | `EVOB_TY` | b13–b12 Advanced Stream present (`01b`), b11–b10 sub video present, b9–b8 sub audio present; the rest reserved. `0x0000` 987, `0x1000` 125 (Advanced Stream), `0x0500` 16 (sub video + sub audio), `0x0400` 3 (sub video). In an interleaved block the sub video and sub audio bits are 0 |
| 2 | 4 | `EVOB_VM_ATR` | main video, bits below |
| 6 | 4 | `EVOB_VS_ATR` | sub video, same layout as `VM_ATR` (no closed caption; b9 = Luma flag). 0 when there is no sub video. 0 on 1112; 19 records carry one (`60105000` ×12: VC-1 480-line 4:3 progressive) |
| 10 | 2 | `EVOB_VS_LUMA` | high byte start, low byte end of the luma range (0–235) made transparent when the Luma flag is 1 (luma key). 0 on 1131 |
| 12 | 2 | reserved | 0 |
| 14 | 2 | `EVOB_AMST_Ns` | b3–b0 number of main audio streams, 0–8. 1 (793), 0 (136), 2 (59), 3 (42), … |
| 16 | 32 | `EVOB_AMST_ATRT` | 8 × 4-byte `AMST_ATR`, one per decoding audio stream number 0–7; unused all 0. Zero past `AMST_Ns` on 1131/1131 |
| 48 | 144 | `EVOB_DM_COEFTS` | 8 × 18-byte down-mix tables, only for multichannel LPCM; otherwise 0 [23 Annex D]. 0 on 1131 |
| 192 | 2 | `EVOB_ASST_Ns` | b3–b0 number of sub audio streams, 0–8. 1 on 16 records |
| 194 | 32 | `EVOB_ASST_ATRT` | 8 × 4-byte `ASST_ATR`. The 16 records each hold `1c00c400` (DD+ 48 kHz 2 ch) |
| 226 | 2 | reserved | 0 |
| 228 | 2 | `EVOB_SPST_Ns` | number of sub-picture streams, 0–32 (`0` on 826/1131) |
| 230 | 160 | `EVOB_SPST_ATRT` | 32 × 5-byte `SPST_ATR` |
| 390 | 64 | `EVOB_SDSP_PLT` | 16 colours for SD 2-bit sub-pictures: reserved, Y, Cr, Cb (BT.601) |
| 454 | 64 | `EVOB_HDSP_PLT` | 16 colours for HD 2-bit sub-pictures: reserved, Y, Cr, Cb (BT.709) |
| 518 | 506 | reserved | 0 |

`[23 §6.3.1.2.3]` **SPEC**; `[11, 12]` **VERIFIED** (every offset above against the
1131 records).

**Palettes.** Both palettes are all 0 when the EVOB has no 2-bit sub-picture; unused
entries must still be in range. 1124/1131 records are 0 there. 7 (`DOOM`,
`GOODFELLAS`, `LAST_SAMURAI`, `U2_RATTLE_AND_HUM`) fill both with `00 7f 7f 7f`
(mid-grey). Advanced Content discs use 8-bit sub-pictures, whose colours come from
the `SET_COLOR2` command in the sub-picture unit ([08](08_evo.md) §8.8), so these
palettes are not used for them.

`EVOB_VM_ATR` / `EVOB_VS_ATR` bit fields (MSB = bit 31 of the u32) [23 §6.3.1.2.3]:

| Bits | Field | Values | Disc (`VM_ATR`, 1131) |
|---|---|---|---|
| 31–29 | video compression | `000` reserved (MPEG-1, Interoperable only), `001` MPEG-2, `010` MPEG-4 AVC, `011` VC-1 | VC-1 635, MPEG-2 436, AVC 57, `000` 3 |
| 28–26 | TV system | `000` 525/60, `001` 625/50, `010` HD 60 Hz, `011` HD 50 Hz | HD/60 677, 525/60 454 |
| 25–24 | aspect ratio | `00` 4:3, `11` 16:9 | 16:9 764, 4:3 367 |
| 23 | CC1 | closed caption for field 1 in the video | 1 on 245 |
| 22 | CC2 | closed caption for field 2 | 0 |
| 21–20 | source picture progressive | `00` interlaced, `01` progressive, `10` unspecified | 552 / 506 / 73 |
| 19–18 | reserved | | 0 |
| 17 | source letterboxed | 0 for 16:9; 4:3 may be 1 | 0 |
| 16 | film camera mode | 625/50 only: 0 camera, 1 film | 0 |
| 15–12 | source resolution | `0000` 352×240/288, `0001` 352×480/576, `0010` 480×480/576, `0011` 544×480/576, `0100` 704×480/576, `0101` 720×480/576, `1000` 1280×720, `1001` 960×1080, `1010` 1280×1080, `1011` 1440×1080, `1100` 1920×1080 | 1920×1080 677, 720×480/576 451, 352×240/288 3 |
| 11–10 | reserved for the Interoperable application flag | | 0 |
| 9 | Luma flag (`VS_ATR` only) | `EVOB_VS_LUMA` is valid | |
| 9–0 | reserved (`VM_ATR`) | | `0x060` on 5 records, else 0 |

The compression field is the codec source: it matches the stream on every EVO
read, where the playlist's `MediaAttributeList` is wrong on 125 clip videos
([03](03_playlist.md) §3.6). An earlier version of this sheet read the word with
the patent-figure layout (compression at 31–30) and wrongly concluded the field was
unreliable.

**`AMST_ATR`** (main audio) [23 §6.3.1.2.3]:

| Bits | Field | Values |
|---|---|---|
| 31–26 | audio coding mode | `000000` reserved (AC-3, Interoperable), `000001` MLP, `000010` MPEG-1 / MPEG-2 without extension, `000011` MPEG-2 with extension, `000100` reserved (LPCM 1/600 s, Interoperable), `000101` LPCM (1/1200 s), `000110` DTS-HD, `000111` DD+ |
| 25–24 | reserved | |
| 23–21 | sampling frequency | `000` 48 kHz, `001` 96 kHz, `010` 192 kHz |
| 20–16 | reserved | |
| 15–14 | quantization / DRC | DD+, DTS-HD: `11`; MPEG: `00` no DRC, `01` DRC; MLP, LPCM: `00` 16-bit, `01` 20-bit, `10` 24-bit |
| 13–10 | number of channels − 1 | `0000` 1 ch … `0111` 8 ch; the `.1` counts as one (5.1 = `0101`) |
| 9–8 | reserved for the Interoperable application flag | |
| 7–0 | reserved | |

**`ASST_ATR`** (sub audio): the same layout with coding modes `000110` DTS-HD,
`000111` DD+, and the optional `100000` mp3, `100001` MPEG-4 HE-AAC v2, `100010`
WMA Pro [23 Annex Q]; sampling `000` 48 kHz, `100` 12 kHz, `101` 24 kHz; channels
`0000` mono, `0001` stereo.

On disc (`e14`, 9 unique words): `1c00c400` ×878 = DD+ 48 kHz 2 ch,
`1c00d400` ×474 = DD+ 48 kHz 6 ch, plus 7 rarer. Language is not in this word
(XPL `langcode`). WO FIG.111 draws the ATR as a logical tree; C00010's 64-bit
`A_ATR` is not this word.

**`SPST_ATR`** (5 bytes per sub-picture stream; unused 0) [23 §6.3.1.2.3]:

| Byte | Bits | Field |
|---|---|---|
| 0 | 7–5 | coding mode: `000` 2-bit RLC with `PRE_HEAD` ≠ 0, `001` 2-bit RLC with `PRE_HEAD` = 0, `100` 8-bit RLC ([08](08_evo.md) §8.8); 4–0 reserved |
| 1 | 5 / 4–0 | HD stream present / its decoding sub-picture stream number |
| 2 | 5 / 4–0 | SD wide (16:9) stream present / number |
| 3 | 5 / 4–0 | SD letterbox (4:3) stream present / number, only if the title allows letterbox |
| 4 | 5 / 4–0 | SD pan-scan (4:3) stream present / number, only if the title allows pan-scan |

The decoding number is the low 5 bits of the sub-picture `sub_stream_id`
(`001nnnnn`). A flag of 0 makes its number meaningless (it is not stream 0). With
the HD flag 0 every SD flag is 0. On disc 1258/1258 are `80 2n 00 00 00` (`e25`):
8-bit RLC, HD stream `n` only; `0x20 | n` therefore equals the `sub_stream_id`.
The player picks the number for its output: HD, or SD wide / letterbox / pan-scan
when it down-converts [23 §4.3.13.3.6].

`[23]` **SPEC**; `[11, 12]` **VERIFIED**

## 6.3 VTS_EVOBIT (at `VTS_EVOBIT_SA` × 2048)

320-byte entries. `EVOB_Ns` equals `.MAP` count on 117/119 discs
(exceptions: `PANS_LABYRINTH` extra EVOBIs for angles; `ETERNAL_SUNSHINE` 28 EVOBI vs 29 MAP; extra is `DELEXT8`, not in VTI).

| Offset | Size | Field |
|---|---|---|
| 0 | 4 | `EVOB_Ns`, number of EVOBs, at most 1998 |
| 4 | 4 | `VTS_EVOBIT_EA`, last byte of the table |
| 8 | 4×`Ns` | `VTS_EVOBI_SA`, byte offset of each entry from the start of this table |

First offset = `8 + 4×Ns`.

### VTS_EVOBI (320 bytes) [23 §6.3.1.3.3]

| Offset | Size | Field | Disc |
|---|---|---|---|
| 0 | 2 | `EVOB_ID` | b15–b12 application type (`0001b` Standard, `0010b` Advanced, `0011b` Interoperable); b6–b5 `A0_GAP_LOC`, b4–b3 `A1_GAP_LOC` (Interoperable only, else 0); the rest reserved. `0x2000` on 2431/2431 |
| 2 | 255 | `EVOB_FNAME` | EVO filename, ISO 8859-1, zero-filled. 1/2431 has a 36-byte name (`SMOKEY_AND_THE_BANDIT` `SMOKEYANDBANDIT_LOADEDUPMPEG2_HD.EVO`); match a listed `.EVO` |
| 257 | 1 | reserved | 0 |
| 258 | 4 | `EVOB_ADR_OFS` | RLBN of the EVOB in its EVOBS for Standard/Interoperable; 0 for Advanced |
| 262 | 4 | `EVOB_ATRN` | 1-based `VTS_EVOB_ATR` number, 1–511; all EVOBs of one angle block have the same. 2431/2431 in `1…Ns` |
| 266 | 4 | `EVOB_V_S_PTM` | first video presentation time, 90 kHz. Matches the first EVOBU's start PTM on DOWNFALL |
| 270 | 4 | `EVOB_V_E_PTM` | video presentation end time; two-part features: part 2 start = part 1 end |
| 274 | 4 | `EVOB_SZ` | size in **packs** (sectors). Equals listing `.EVO` size / 2048 on **2416/2431**. The 15 misses are `PANS_LABYRINTH` interleaved angles (several EVOBI share one EVO file; each row is one angle's pack count) |
| 278 | 2 | `EVOB_INDEX` | 1–1998, unique in the VTS; the same number as `EVOB_INDEX` in this EVOB's time-map search pointer ([07](07_map.md)). Equals table position on 2419/2431; `SPARTACUS` skips 12. Find an EVOB by this number, not by position |
| 280 | 2 | reserved | 0 |
| 282 | 4 | `EVOB_FIRST_SCR` | SCR of the first pack, 90 kHz; used when the clip joins the previous one seamlessly. `0` on first/only parts; non-zero on 100 rows, almost all `FEATURE_2` / `PEVOB_2` / dual-layer tails (`0x80000000` on some) |
| 286 | 4 | `PREV_EVOB_LAST_SCR` | Interoperable only; Advanced: all 1s. `FF` ×4 |
| 290 | 8 | `EVOB_A_STP_PTM` ×2 | audio stop times (Interoperable); Advanced: all 1s. `FF` ×8 |
| 298 | 4 | `EVOB_A_GAP_LEN` ×2 | audio gap lengths (Interoperable); Advanced: all 1s. `FF` ×4 |
| 302 | 4 | reserved for copy protection | 0 |
| 306 | 14 | reserved | 0 |

There is **no** MAP filename in EVOBI. Playlist `src` is the MAP; EVOBI names the EVO.
The book gives the map the same name body as its EVO file ([01](01_volume.md) §1.4):
`FEATURE_1.MAP` ↔ `FEATURE_1.EVO`. WO FIG.112 labels this field `TMAP_FILE_NAME`;
the book and the disc say EVO.

A seamless join converts time between EVOBs with
`STC offset = EVOB_V_E_PTM(earlier) − EVOB_V_S_PTM(later)` [23 §4.2.3.2].

`[23]` **SPEC**; `[11, 12]` **VERIFIED**
