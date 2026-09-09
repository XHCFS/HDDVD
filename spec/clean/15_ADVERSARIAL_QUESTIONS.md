# Adversarial pass — C structs, remaining holes, hard questions

Second implementer pass after [14_IMPLEMENTER_QUESTIONS.md](14_IMPLEMENTER_QUESTIONS.md)
/ [14_IMPLEMENTER_ANSWERS.md](14_IMPLEMENTER_ANSWERS.md). Goal: what a C player
**cannot** `memcpy` as a packed struct, what this pass proved was wrongly closed,
and the questions that still desync video, File Cache, or AACS if guessed.

Experiment: `experiments/e13_adversarial_census.py`, `e14_adversarial_search.py`.
Source review (2026-09-08): every sheet-01/02 census fact now carries `[SRC:]`;
UDF 2.50/`0x0250` is N=3 LVD not 120; `VTS_EA` is 0 on disc; `loadingBegin` is
used. Sheets: 01–03, 06–07, 09–10.

No firmware reverse-engineering. No decryptor.

## Tags

| Tag | Meaning |
|---|---|
| `MEMCPY` | Fixed size, big-endian (video) or little-endian (UDF). Overlay with a packed struct + byte swaps. Still watch **NUL-less** `char[]`. |
| `SLOT` | Fixed slot larger than the live record (`sizeof` ≠ stride). |
| `VL` | Counted / pointer-table / walk-until-sentinel. Not one struct type. |
| `BITPACK` | Fields share a word. Use shifts. C bitfields will not match BE layout. |
| `XML` | Schema, not bytes. |
| `MPEG` | ISO 13818-1 + optional stuffing / system header / PES. Offsets from pack start move. |
| `UDF` | ISO/IEC 13346. |
| `ALGO` | Procedure. There is no struct. |
| `OPEN` | Not closed from this corpus (or needs a saved file / licensed disc). |

**Blocks** (same as 14): `L` linear, `S` seek/angles, `A` audio/SP, `M` HDi, `K` AACS, `U` skip/MVP.

---

## 1. What you cannot build as a literal C struct

These are not “hard to pack.” A `sizeof` / `__attribute__((packed))` overlay is
the wrong type.

| Object | Tag | Why a packed struct fails |
|---|---|---|
| UDF 2.50 volume (AVDP, LVD, PD, FE/EFE, FID, short/long/extended ADs, metadata partition, multi-extent file body) | `UDF` `VL` | Counted identifiers, allocation descriptors, ICB adtype 3 inline. Use a UDF walker. |
| `VPLST$$$.XPL` | `XML` | Playlist.xsd. |
| Manifest `.xmf`, iHD `.xmu`, ECMAScript | `XML` | Manifest.xsd / iHD.xsd. JS inside ACA is UTF-16BE. |
| ACA directory | `VL` | Record = `14 + (flags&0xFF) + 32`. Not 58-byte stride. |
| VTI ATRT / EVOBIT | `VL` + `SLOT` | `nr` + `nr×u32` pointer table, then 1024 / 320 **slots**. The table is not `ATRI[nr]`. |
| ATRI internals | `VL` inside `SLOT` | `4×AST_Ns` then a hole then `5×SP_Ns` inside 1024 bytes. |
| `V_ATR` / `EVOBU_ENT` | `BITPACK` | BE u32; C bitfields are compiler-endian. |
| Whole `.MAP` | `VL` `SLOT` | GI 128 + unnamed u16@372 + `Ns×` 10-in-32 SRP + `EVOBU_ENT[]` + optional `ILVU_ENT[]`. |
| MPEG-2 pack / PES | `MPEG` | SCR, stuffing 0–7, optional `00 00 01 BB`, variable PES header, VC-1 extension. |
| MKB | `VL` | Stop at End-of-MKB; listed size may be padding. |
| CHT #1 / #2 bodies | `VL` `OPEN` | Not saved; stride not constant. |
| File Cache / title timeline | `ALGO` | Runtime, not on-disc. |

## 2. What *can* be a packed overlay (with caveats)

| Object | Size | Caveat |
|---|---|---|
| `DISCID.DAT` | 128 | Cleanest overlay. IDs are **not** C strings if they fill the field. Reserved 61–127 zeros 119/119. |
| ACA archive header | 32 | Then **stop**. Directory is `VL`. |
| `VTSI_MAT` | 2048 | SA fields are **sectors**, ×2048. |
| ATRI **slot** | 1024 | Internals still `VL`. |
| EVOBI **slot** | 320 | Filename may fill 36 with **no NUL** (1/2431). |
| `TMAP_GI` | 128 | VTI name at 114 is 12 bytes, often no NUL (`HVA00001.VTI`). |
| `TMAPI_SRP` | 10 in 32 | `SLOT`. Bytes 10–31 zero on every saved slot (`e13`). |
| `ILVU_ENT` | 6 | Array; count is **not** in the SRP. |
| DKF | 64 | |
| `CONTENT_CERT.AACS` | 120 | No 12-byte ASCII ID. |
| VTUF when `URS_NUM=0` | 144 | Book Table 3-10: HASH_SIZE **17–20**, PLAYLIST_NAME **23–34**. Unaligned u32. |
| VTKF header | 128 | Then `n×36` from `HD_VTKF_SIZE`. Do not assume 2480. |
| Title Key Entry | 36 | Not 32. |
| PCI GI / DSI GI / GCI 256 | from **substream-id byte** | Reserved **holes** (PCI +7/2, DSI +27/1). Not pack-absolute. |
| Encrypted-pack split | 128+1920 | Format only. Corpus packs are clear (`e09`). |

Endian: HVDVD_TS / ADV_OBJ / AACS video structs are **big-endian**. UDF descriptors
are **little-endian**. Mixing those in one `struct` is a class of bugs.

## 3. False-closed claims found this pass

| Was written | Disc | Fix |
|---|---|---|
| MAP `[128..383]` zero padding | Only 4 maps have live bytes there: **u16be @372** = ILVU record count | [07](../advanced/07_map.md); `e13` |
| `ILVU_SZ` “equals TMAPI_Ns except a 1-pack tail” | SZ is **EVOBUs of one angle**. ADR steps hundreds of packs. Records **cycle** TMAPI `i % Ns`. Tails are leftover EVOBUs, not 1-pack | [07](../advanced/07_map.md); `e13` 179+371+499+239 deltas |
| `spec/clean/09_AACS.md` VTUF name @ `0x18` | Book Table 3-10 + hex `00 00 00 00 80 00 00 56` → `'V'` at **23** | [09](../advanced/09_aacs.md) |
| PlaylistApplication `language` = ISO 639-2 (3-letter) | XSD type is *named* `ISO639-2`; enumeration is **2-letter** (`en`, `fr`) | [03](../advanced/03_playlist.md) |
| EVOBI name always NUL-padded | 1/2431 fills 36: `SMOKEYANDBANDIT_LOADEDUPMPEG2_HD.EVO` | [06](../advanced/06_vti.md); `e13` |
| ATRI 80–228 unused | 16/1131 have `01 1c 00 c4` @193 | [06](../advanced/06_vti.md); `e13` |
| V_ATR can name VC-1/AVC | compression `10b`/`11b` = **0/1131** | [06](../advanced/06_vti.md); `e13` |
| CPI always pack byte `0x3C` | True **iff** 14-byte pack + system header `0xBB` at 0x11. PCI-omitted / stuffing moves it | [08](../advanced/08_evo.md) [09](../advanced/09_aacs.md) |

`e04` still does not protect “VTKF size is always 2480” — Pan’s 2516 files are
listing-only. Size from `HD_VTKF_SIZE`.

---

## 4. Questions (by sheet)

Status: `ASK` = still unclear; `CLOSED` = answered this pass or already in 01–10
but easy to re-break; `RESEARCH` = need more saved bytes / licensed disc, not firmware.

### 01 — Volume / UDF (`UDF`)

A01. `L` `ASK` Backup AVDP at `N−256`: listings never mention it. `udfgrab.py` reads **only** sector 256. UDF requires the backup; untested if 256 is unreadable.
A02. `L` `ASK` Metadata-partition **mirror** FE: listing `meta_fe` is 0 on 112/120, else 96/64/128/160 (`e14`). Meaning of that listing field vs a UDF mirror is **not** proven. Do not hard-code `meta_fe=0`.
A03. `L` `CLOSED` ISO 9660 / `VIDEO_TS`: **0/120** listing hits (`e14`). Treat images as UDF-only.
A04. `L` `CLOSED` as corpus fact: `partition_start=288` on 120/120 (`e01`/`e14`). **ASK** remains: a correctly mastered disc with another start is legal UDF — do not bake 288 into a walker; read the LVD.
A05. `L` `ASK` ICB `adtype=3` (inline data): any FID/FE in the metadata partition stores a small file inline? A walker that only follows extents will miss `DISCID.DAT` if it were inline (it is not, on saved files).
A06. `L` `CLOSED` as listing names: **0** non-ASCII paths in 120 listings (`e14`). FID CS1 on-disc vs listing transcoding still **ASK** for the walker.
A07. `L` `ASK` Multi-extent `.EVO` that is **not** concatenated in extent order — out-of-order ADs. `udfgrab` concatenates; is that always the file body order?
A08. `L` `ASK` `HVA00001.BUP` 36 saved: player fallback only on read error, or also if `VTSI_EA` disagrees with file size?
A09. `U` `ASK` Official MMC “is this HD DVD?” probe: still uncloseable from ISOs.

### 02 — DISCID (`MEMCPY` 128)

A10. `M` `CLOSED` values: only `0` (106) and `1` (13). A third value is a different format — fail closed (same policy as reserved 61–127).
A11. `M` `ASK` Binary `PROVIDER_ID` (24 discs): three observed shapes (`e14`) — all-`FF`, UUID-like, mixed ASCII tail (`…SLY`). Exact persistent-storage directory bytes still OPEN.
A12. `M` `ASK` Disc ID @12 `0xFF×16` (109) vs other (10). Network HDi use of the UUID when present is OPEN.
A13. `L` `CLOSED` Reserved 61–127: zeros 119/119. A non-zero byte is a different format version — fail closed.

### 03 — Playlist (`XML`)

A14. `M` `CLOSED` corpus: `ApplicationSegment@sync` is `hard` 2120 / omit 105 / `soft` 304 / **`none` 0** (`e14`). XSD `none` unused. Default `hard` is safe.
A15. `M` `CLOSED` as usage: `loadingBegin` on **110** `ApplicationResource` (7 discs), **always** `00:00:00:00` (`e14`). File Cache pull at title start. Not a delayed clock in this corpus.
A16. `M` `CLOSED` corpus: `noCache="true"` is **0**. If a future disc sets it, XSD meaning still ASK.
A17. `S` `CLOSED` as corpus: `timeBase` is `60fps` 247/247; FF≥50 occurs 3590 times (`e14`). Do not clamp FF to 00–49. `50fps` remains legal XSD with 0 specimens.
A18. `S` `ASK` `clipTimeBegin` as XML time vs patents calling it PTS: MAP walk uses title ticks (`e10`). **133** nonzero; **22** have odd FF (`e14`). Round how if not on an EVOBU boundary?
A19. `M` `CLOSED` `"0"` is XSD integer 0, not token `false`. No ADV_PCK slot 0
(`e16` starts at 1). The 12 PlaylistApplicationResource rows are URI ACA files.
Always load `src` (same as `false`). 14.Q57 “do not treat as URI” is **refuted**.
A20. `A` `CLOSED` as fail-closed: 718 titles omit `TrackNavigationList` + 15 carry
an empty one (733 total); use first mapped `Audio` child, else track 1. In corpus
all 493 first-Audio are `@track=1` (e18), so the rule resolves to track 1 either
way. Do not invent `defaultLanguage` matching.
A21. `S` `CLOSED` counts: duration == last clip end **3237**; duration **>** last end **70** (black tail); duration **<** last end **1** — `THE_SEARCHERS` FPT `00:00:23:00` vs clip end `00:00:23:55`. Timeline = `titleDuration`; do not extend past it.
A22. `L` `CLOSED` as fail-closed: ignore user title-nav (Next / Prev / FF / FR /
time-search / `jump`) until FirstPlayTitle ends, then Title 1. Patent (c)(d):
play start→end at normal speed, tracks 1+1. Next is not “skip to Title 1.”
Skip key not demonstrated.
A23. `M` `CLOSED` as fail-closed: missing File Cache resource mid-FPT → keep
playing FPT video, skip that resource (same as 64 MB overflow). Do not abort.
A24. `L` `CLOSED` `language` on PlaylistApplication is **2-letter** (`en` 186, `de` 11, `ja` 3, `fr` 3; `e14`) despite XSD type name `ISO639-2`. Matching `Player.menuLanguage` to `fra`/`fre` will miss `fr`.
A25. `L` `CLOSED` corpus: `xml:base` **0/247**. If a future disc sets it, does `file:///dvddisc/` still win for disc assets? (still ASK as policy)
A26. `S` `ASK` `tickBaseDivisor` 2/3/4: markup only, or also `ScheduledControlList` `@titleTime`? If both, MAP seek must **not** divide.
A27. `L` `CLOSED` corpus: `seamless="true"` on **157** `FEATURE_2`/`PEVOB_2` clips (`e14`). Decoder connection **plus** a dual-layer seek. Still two MAP/EVO files.
A28. `A` `CLOSED` corpus: **0** clips with two `Audio` children sharing `@track` (`e14`). Treat a future duplicate as authoring error (last-wins is player policy).
A29. `S` `CLOSED` Pan’s: `Video@angleNumber` is **never omitted** on the four interleaved MAP clips (`e14`). Default 1 is only for contiguous. Angle 2/3/4 exist (8+8+6).

### 04 — ACA (`VL`)

A30. `M` `RESEARCH` File-type field in header bytes 18–31: all-zero on 6/6 saved; DLL rejects type ≠ 0. Where is type stored if not those 14 bytes?
A31. `M` `RESEARCH` 283-byte AACS sidecar: named fields besides leading `AACS` + `name.AACS` + length. Need more `0xff` archives **saved**.
A32. `M` `RESEARCH` CRC of decrypted `0xff` members: cannot test (no keys). Extract by offset/length only.
A33. `M` `RESEARCH` 403/409 archives not saved. Formula INFERRED. One archive with namelen 0, namelen > 64, or `/` in the counted name would break the walker.
A34. `M` `ASK` Member name Unicode / UTF-16: 30/30 ASCII. URI `foo.aca/bar` match — case-sensitive, exact length, no NUL.
A35. `M` `ASK` Directory overlapping payloads, or `offset+length` past `N` header `total size`: reject archive or clip?
A36. `M` `CLOSED` All 20 saved `.js` (including 3 loose `1408`) are UTF-16BE BOM `FE FF`. Do not sniff UTF-8 for script. XMU is UTF-8 (`e15`).

### 05 — HDi (`XML` `ALGO`)

A37. `M` `CLOSED` as fail-closed: `IPlaylist.load` wipes File Cache then loads the new XPL’s resources (FIG.51 body). Keep-on-overlap unproven.
A38. `M` `CLOSED` `ITitle.elapsedTime` is an `HH:MM:SS:FF` string: Jumpstart resume code matches it with a timecode regex; STALINGRAD/`1408` pass a stored elapsed value as `jump`’s first argument (`e15`). Not milliseconds / 90 kHz.
A39. `M` `CLOSED` as fail-closed: `ITitle.jump(time, pause)` /
`IChapter.jump(time, pause)`. `time` is `HH:MM:SS:FF`. Saved call sites are
**always `false`** (`e15` 258/258). `true` → seek then pause. `false` → seek
and do not force pause (a jump to another Title starts that title playing —
`1408` extras have no `play()`). If already paused, stay paused unless script
calls `play()` (`1408` chapter buttons after `menubarHide()`). Typelib:
`play`/`pause` live on `IPlaylist`, not on `jump`. Annex Z unpublished.
A40. `M` `CLOSED` Mapping `titleTimeBegin/End` gates the app; cues run only while it is active. Mapping wins if they disagree.
A41. `M` `CLOSED` as fail-closed: `@size` reservation; 64 MB cap; flush highest `@priority` first; if still over, skip the new resource (HDDVDPLAYDLL “Exceeded cache size”).
A42. `M` `RESEARCH` `.CER` 1419/811: X.509? TLS trust for network extras. Bodies not saved.
A43. `M` `RESEARCH` CVI / CDW binaries (if any listing): not in 01.5.
A44. `M` `CLOSED` as fail-closed: page/application clocks are independent of
the media clock. Mapped `clock="page"` cues keep ticking when video is paused.
`sync="soft"` is about File Cache *load* (timeline keeps running; app may miss
the window), not “freeze cues on pause.” Unmap at exclusive `titleTimeEnd`.
A45. `M` `CLOSED` Selectors `switch (Player.menuLanguage)` on two-letter
`en`/`fr`/`ja`/`de` (`MATRIX`/`BLADE`/`TRAINING` `selector.aca/script.js`).
`en` is `default`. Some other JS `slice(0,2)` before matching — host should
expose ISO 639-1 two-letter (or at least the first two characters).

### 06 — VTI (`SLOT` `VL` `BITPACK`)

A46. `A` `ASK` ATRI @6 extra word (`60105000` etc., 19 rows): SubVideo ATR? Ignore for Advanced demux if XPL has 0 SubVideo.
A47. `A` `ASK` ATRI @193 `011c00c4` (16 rows): SP default? palette ptr? Must not be parsed as `SP_Ns`.
A48. `A` `ASK` Flags `1000`/`0500`/`0400`: copy-once? angle? Unneeded if XPL present.
A49. `A` `ASK` `AST_ATR` 4-byte vs DVD 8-byte: bit layout for codec/channels still OPEN. Needed only if XPL omits Audio.
A50. `A` `CLOSED` overrun: `SP_Ns` that would push `SP_ATR` past 391 is **0/1131** (`e14`). Max `SP_Ns` seen is 32 (1 ATRI). Dummy palettes @391 still OPEN as a usable table (A58).
A51. `S` `CLOSED` `VTS_EA` is **0** on 119/119 Advanced VTI (`e14`). `VTSI_EA` equals file sectors−1. Do not add `VTS_EA` to pack addresses. Patent “end of VTS” is unused because EVOBS are separate files.
A52. `S` `ASK` EVOBI+282: 100 nonzero; `0x80000000` ×7 (layer flag) vs unique LBNs/PTMs (`e14` 94 distinct). **Do not add to MAP pack addresses.** Units OPEN.
A53. `S` `CLOSED` EVOBI filename: `split(\0)` is wrong for SMOKEY (36-byte fill). Match listing with `bytes.rstrip('\0')` or full 36.
A54. `S` `ASK` `SPARTACUS` serial hole (skip 12): 1-based id for HDi `titles` vs table index?
A55. `S` `CLOSED` `ETERNAL_SUNSHINE` `DELEXT8` MAP not in EVOBI: follow XPL `src`, not the VTI list.
A56. `L` `CLOSED` `V_ATR` bits 31–30 never AVC/VC-1 (0/1131). Demux from XPL + PES `stream_id`.
A57. `L` `ASK` Aspect `10b` (677) not in patent 4:3/16:9 table. Treat as 16:9 HD; what if a 4:3 HD disc appears?
A58. `A` `ASK` Palette @391 `7f7f7f00`×32: ignore, or 8-bit SP still needs a real YCrCb table from SP_PCK headers?

### 07 — MAP (`BITPACK` `SLOT` `VL`)

A59. `S` `ASK` Official name of u16@372. Equals ILVU walk count on 4/4. Patent TABLE 80 reserved at 22–49 — this is **after** GI, in the “padding.”
A60. `S` `CLOSED` `TMAPI_SRP.ILVU_ENT_Ns` is 0 on interleaved maps. Using it yields **no** ILVU.
A61. `S` `CLOSED` named bits (C00039): b9 ILVUI `0x0200`, b8 ATR `0x0100`, b1–b0 Angle. `0x2202` = b13 + ILVUI + seamless. `ASK` only: unnamed b13, and fail-policy if a future map sets any other bit.
A62. `S` `ASK` `1STREF_SZ` if the first reference picture **spans** packs vs “packs through last byte.” Trick-play off-by-one.
A63. `S` `ASK` Seek `>` vs `>=` on the last tick of an EVOBU (`e10` is N=1 clip). Inclusive end of VOBU vs start of next.
A64. `S` `ASK` Chapter on a **field** vs coded frame: `PB_TM` is fields. `titleTimeBegin` on an odd field — which EVOBU if PB_TM is even?
A65. `S` `CLOSED` ILVU stitch: record `i` → TMAPI `i % Ns`; `ADR` pack index; `SZ` EVOBU count of that angle; next ADR = ADR + sum of those `EVOBU_SZ`. `e13`.
A66. `S` `ASK` Playing angle A, does audio/SP come from the **same** ILVU run (muxed in those EVOBUs) or from a parallel non-interleaved stream? If muxed, skipping other angles’ packs is enough.
A67. `S` `ASK` `EVOB_ATR_SA` 0xFFFFFFFF on primary maps. If a future map sets it, does it override VTI ATRI for that clip?
A68. `S` `ASK` `TMAPI_SA` as LBN×2048 (patent). Disc uses **byte** offsets. Dual-read heuristic: if `SA*2048 < filesize` and `SA>2048`, it is **not** this corpus’s encoding — do not “support both.”
A69. `S` `CLOSED` the 108 `SZ>2047` entries are **all contiguous** (`e14`). 0 on interleaved maps. 13-bit field is mandatory for ordinary titles.
A70. `S` `ASK` Summing MAP `PB_TM` at `tickBase` (24fps) instead of `timeBase` (60fps) — 29 vs 60. Confirm no disc documents otherwise.

### 08 — EVO (`MPEG`)

A71. `L` `ASK` Pack stuffing (0–7 bytes) moving “byte 20” `PES_scrambling_control` and Dtk@84. Rule: parse pack header length, do not index 20 from 0.
A72. `L` `CLOSED` PCI omitted (`STALINGRAD` `black.EVO` 35/35). Parse by `sub_stream_id`, not “PCI then DSI then GCI.”
A73. `K` `ASK` GCI_CAT `0x40` vs CPI `KEY_VF`. Treating `0x40` as segment-key with no SKF decrypts with a garbage key.
A74. `M` `CLOSED` ADV_PCK `0x80`: first packet slot+filename+ADDTHD+`HDDVDACA`;
middle/last skip 4 bytes; concat = `ADV_OBJ` file. Specimen: `STALINGRAD`
`logo.EVO` N=2383 (`e16`). OLIVER `JpnTokuhou`/`LoopMenu` have the ACA file
and **0** packs — still load `src`. ADDTHD length is not a constant: locate
`HDDVDACA` after the 32-byte name field (STALINGRAD is 225 zeros; do not
hard-code 259).
A75. `A` `ASK` Audio PES after `sub_stream_id`: DVD-style first-AU pointer / padding. DD+ vs AC-3 vs DTS-HD vs LPCM — different headers. No feature-EVO pack census.
A76. `A` `ASK` Sub-picture `001*****b` vs patent `011*****b` “extended Sub-picture.” 8-bit RLC might **not** be `001*****`.
A77. `A` `ASK` 8-bit vs 2-bit RLC inside SP_PCK: XPL `SubpictureAttributeItem@codec` vs bytes. Layout OPEN.
A78. `A` `ASK` VS/AS packs if present despite 0 XPL SubVideo/SubAudio children: drop or decode into PIP?
A79. `L` `ASK` `stream_id=0xE2` AVC and `0xFD/0x55` VC-1 vs MPEG-2 `0xE0` on the **same** clip (seamless join). Flush policy.
A80. `L` `ASK` NV_PCK not at pack 0 of a file (clipTimeBegin ≠ 0): first pack of the **EVOBU**, not of the file.
A81. `S` `ASK` DSI `vobu_ea` as **absolute LBN**: walk `this + ea + 1` is relative. Absolute would jump to a physical sector and look like success on small files.
A82. `K` `ASK` `PES_scrambling_control` on NV_PCK (shall be 00). If a disc encrypts nav, headers-in-the-clear rule is broken — fail closed.
A83. `L` `ASK` System header omitted on VM_PCK: common. “Byte 20” scrambling then **is** in the pack header flags, but Dtk@84 may still be in the PES. Need a pack-grammar walk, not a fixed overlay.

### 09 — AACS (`SLOT` `VL` `ALGO`) — format only

A84. `K` `ASK` CPI overlay vs `GCI_GI` named fields: 16 bytes at GCI-payload +12 overlap `DCI`/`CCI`? Or CPI is a **different** 16-byte window? Book deferred; BackupHDDVD used pack 0x3C. Encrypted pack would decide. Corpus cannot.
A85. `K` `ASK` `CH_PTR` vs CHT #1 index: 1-based? hash-unit size for EVOB vs 2048-byte pack?
A86. `K` `ASK` VTKF 65 slots (Pan’s 2516) vs book/Scenarist 64. Occupied `AV_FLG` count vs `TITLE_KEY_PTR` max.
A87. `K` `ASK` Extra VTKF with no VPLST (`BALLS_OF_FURY`, …): ignore, or a hidden playlist?
A88. `K` `CLOSED` VTUF `PLAYLIST_NAME` at **23**, HASH_SIZE u32 at **17** (unaligned). `char playlist[12]` at 0x18 is a 5-byte miss.
A89. `K` `RESEARCH` VTUF `URS_NUM>0` body (Table 3-12). 217/217 listed 144 bytes — no specimen.
A90. `K` `RESEARCH` CHT #2 mixed 8/20-byte stride (book). Bodies not saved.
A91. `K` `RESEARCH` `BEE` on the other 103 certs (MATRIX BEE=0 SINGLE).
A92. `K` `ASK` Volume ID MMC `80h` after AACS auth. Stripped ISO: `Kvu` impossible. Player on a real drive vs this corpus.
A93. `K` `ASK` `TITLE_KEY_PTR` 1-based into **occupied** slots vs physical slot index 1…64.
A94. `K` `ASK` MKB padding after End-of-MKB: hash the listed file or up to EOMKB?
A95. `K` `ASK` `ANY!` vs `AAC!` vs book `AACS/`: probe order if **two** exist (0/120 here).
A96. `K` `ASK` BAK omit `MKBRECORDABLE` (99 discs): if primary MKB fails, is BAK MKBROM enough?

### 10 — Playback (`ALGO`)

A97. `L` `CLOSED` 3/3: MATRIX 000+001, BLADE 000+001, TRAINING 000+001+002 all have `PrimaryAudioVideoClip`; the highest numbered XPL does not (`e14`).
A98. `M` `ASK` After `IPlaylist.load`, is DISCID `SEARCH_FLG` persistent-storage search re-run? Sheet 05: no (not a disc re-insert).
A99. `S` `ASK` Dual-layer: two clips vs one MAP spanning the break. Corpus: always two clips. A single MAP whose EVO is multi-extent **across** layers — seek still byte offset in concatenated file?
A100. `L` `ASK` Error policy: missing MAP URI, EVOBI pack count mismatch (non-angle), ACA CRC fail on non-`0xff`. Skip title vs fail disc vs continue with holes?
A101. `A` `ASK` User changes audio mid-title: switch PES `sub_stream_id` immediately vs next EVOBU vs next ILVU run?
A102. `S` `ASK` Pause at exclusive `titleTimeEnd`: fire `onEnd` before or after the last decoded frame of the last EVOBU?

---

## 5. What still needs research (no firmware)

Priority is **saved on-disc bytes**, then licensed hardware, never player RE.

| Need | Why | Unblocks |
|---|---|---|
| More ACA (beyond 6) | Directory formula INFERRED on 403 archives | A33 |
| Feature EVO pack census (`streamNumber` ↔ TABLE 46 `***`) | 1-based vs 0-based INFERRED | A75, 14.Q39 |
| One EVO that contains ADV_PCK `0x80` | Muxed File Cache | A74 **CLOSED** (`STALINGRAD` `logo.EVO`) |
| `.CER` bodies | HDi network trust | A42 |
| CHT1/CHT2 file heads | Hash-unit stride | A85, A90 |
| VTUF with `URS_NUM>0` | Table 3-12 | A89 |
| Encrypted pack on a **licensed** disc | CPI window vs GCI_GI; Dtk; KEY_VF=10b | A84, A92 |
| Persistent-storage dump from a real player | FIG.20 directory bytes for binary PROVIDER_ID | A11 |
| 50fps playlist (0/247) | FF range, PB_TM vs ticks | A17 |
| Category 3 / `HVSO` / `APLST` | 0/120 | format of those files |

Linear MVP does **not** wait on this list: UDF 2.50 → DISCID → highest VPLST
(with the 3-selector fallback) → FirstPlayTitle then Title 1 → 13-bit `EVOBU_SZ`
walk → 2048-byte packs → codec from XPL `MediaAttributeList`.

---

## 6. Worst remaining desync traps

1. 11-bit `EVOBU_SZ` (108 entries > 2047).
2. `PB_TM` as frames or ×2; or summing MAP at `tickBase` (24fps) instead of `timeBase` (60fps).
3. Wall-clock seconds × 90000 vs title ticks; NTSC VOBU is **45045** ticks = 500.5 ms for `PB_TM=30`.
4. Contiguous `sum(SZ)` on interleaved maps (plays the wrong angle’s packs).
5. `ILVU_SZ` as packs; `ILVU_ADR` as MAP file bytes; `TMAPI_SA` as LBN×2048.
6. Decoder from `V_ATR` (never VC-1/AVC in 1131 ATRIs) while PES is `0xFD`/`0x55` or `0xE2`.
7. EVOBI+282 added to pack addresses (100 nonzero).
8. Hard-coded PCI/GCI at pack `0x3C` when PCI is omitted or stuffing is present.
9. DSI `vobu_ea` as absolute LBN.
10. CPI 1-byte `TITLE_KEY_PTR` / BD 6144 path / `DISCID@12` as Volume ID.
11. ACA 58-byte stride; VTKF 32-byte stride; VTUF name at 0x18.
12. `ISO639-2` type name → 3-letter lookup for `PlaylistApplication@language`.
13. `char name[36]` C-string on SMOKEY EVOBI (no NUL).
14. `e08` / MVP seek using **TMAPI[0] only** on Pan’s.

---

## 7. Closed this pass (short)

| Item | Result | Evidence |
|---|---|---|
| MAP bytes 128–371 and 374–383 | Zero on 2421/2421 | `e13` |
| u16be @372 | 0 on 2417 contiguous; 180/372/500/240 on Pan’s four = ILVU walk | `e13` |
| TMAPI_SRP bytes 10–31 | Zero on every slot | `e13` |
| ILVU rotation + SZ as EVOBU of that angle | All consecutive ADR deltas match; every TMAPI consumed | `e13` |
| `ILVU_SZ` as packs | 0 matching deltas | `e13` |
| V_ATR compression 10b/11b | 0/1131 | `e13` |
| ATRI @193 | 16/1131 = `01 1c 00 c4`; only mid-slot pattern | `e13` |
| EVOBI 36-byte fill | 1/2431 SMOKEY | `e13` |
| VTUF PLAYLIST_NAME | Offset **23** (book Table 3-10) | AACS 0.953 + MYSTERY_MEN dump |
| XSD `ISO639-2` | 2-letter enums | Playlist.xsd |

`[SRC: DISC | e13 + Pan’s four MAP + 119 VTI]`
`[SRC: SPEC | HD DVD Pre-recorded Final 0.953 Table 3-10]`
`[SRC: SPEC | spec/raw/adv_obj/v1.0/Playlist.xsd type ISO639-2]`
