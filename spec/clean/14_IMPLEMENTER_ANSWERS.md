# Implementer answers — Advanced Content player

Answers to [14_IMPLEMENTER_QUESTIONS.md](14_IMPLEMENTER_QUESTIONS.md).
Evidence tags follow [EVIDENCE_STANDARD.md](EVIDENCE_STANDARD.md). Disc wins
over patents. No firmware reverse-engineering. No decryptor.

Experiments: `e01`–`e12`. Selector scripts were extracted from on-disc
`selector.aca` (not player binaries).

---

## L — Linear playback

**1. ADV_OBJ without VPLST.** Category 2/3 requires `ADV_OBJ/VPLST*.XPL`.
This corpus: **119** discs have both; **0** have `ADV_OBJ` without a VPLST;
**1** has neither (`RESERVOIR_DOGS`, Category 1 IFO). Treat ADV_OBJ-without-XPL
as failure, not a silent IFO fallback.
`[SRC: CORPUS | N=120 listings | e12]` **VERIFIED**
`[SRC: PATENT | US20070091495A1 FIG.7 / FIG.50 playlist-file test]`

**2. UDF / URI case.** UDF 2.50 identifiers are case-sensitive. Disc URIs use
`file:///dvddisc/` + the FID spelling. **10 620 / 10 620** playlist `src` values
match a listing path exactly (ACA members stripped to the `.aca` file).
**0** case-only mismatches. Match exact; do not fold case.
`[SRC: CORPUS | 247 XPL vs listings | e12]` **VERIFIED**

**3. Multi-extent EVO/MAP.** UDF 2.50 allows multiple extents; file data lives
in the physical partition. A player **must** concatenate extents (as
`tools/udfgrab.py` does). Assuming one extent will fail on large features.
`[SRC: SRCCODE | tools/udfgrab.py UDF.fetch]` **VERIFIED** (walker)
`[SRC: DERIVED | DOWNFALL-scale EVO listed sizes vs UDF extent model]` **INFERRED** for those titles

**4. MAP basename vs EVOBI EVO name.** **2421 / 2421** `HVDVD_TS/*.MAP` have a
sibling `.EVO` of the same basename. EVOBI always names that `.EVO`
(2431 names match a listed EVO). Playlist `src` is the MAP; open `FOO.EVO`
next to `FOO.MAP`. A basename mismatch is not observed and is not legal here.
`[SRC: CORPUS | 2421 MAP + 2431 EVOBI | e11/e12]` **VERIFIED**

**5. BUP fallback.** Patent: `HVA00001.BUP` / MAP `.BUP` are byte-identical
backups of VTI / TMAP. Listed: **36** VTI BUP, **785** MAP-like BUP. **Saved and
byte-identical to primary:** 36 VTI (`e08`), **773** MAP (`e08`, 0 differ). Open
BUP only if the primary read fails. Do not search BUP at boot.
`[SRC: PATENT | US20080298219A1 VTSI_BUP / VTS_TMAP_BUP]`
`[SRC: CORPUS | listings 36+785; saved identical e08 36+773]` **VERIFIED** (bytes);
**INFERRED** (when to open)

**6. VPLST$$$.BAK.** Three files: `BALLS_OF_FURY` VPLST001, `CHUCK_AND_LARRY`
VPLST016, `SHREK_THE_THIRD_EU` VPLST004. FIG.50 searches `VPLST$$$.XPL` only.
Never boot from `.BAK` even if the number is higher.
`[SRC: PATENT | US20070091495A1 FIG.50 VPLST$$$.XPL]`
`[SRC: CORPUS | 3 BAK | e05/e12]` **VERIFIED**

**7. FirstPlayTitle vs Title 1.** If `FirstPlayTitle` is present it **shall be
played before Title 1**, from start to end of its timeline, normal speed, video
track 1 + audio track 1 only. PlaylistApplication is **not** scheduled on it.
119 / 247 playlists have one. Then start Title 1 (document order, numbers from 1).
`[SRC: PATENT | US20070091495A1 FirstPlayTitle (a)–(e), “must be played back before playback of a title #1”]`
`[SRC: CORPUS | FirstPlayTitle on 119 XPL | e07]` **VERIFIED**

**8. Title without onEnd (4).** Patent (XSD-era): *“If this value is omitted,
player shall be stopped after Title playback.”* Specimens:
- `PANS_LABYRINTH` VPLST001 title 69 `id="redirect"` 10 s, 0 clips
- `PANS_LABYRINTH` VPLST003 title 2 `id="initialize"` ~1 min, 2 clips
- `BLADE_RUNNER` VPLST002 title 1 30 min, 0 clips (selector)
- `TRAINING_DAY` VPLST003 title 1 30 min, 0 clips (selector)

Do **not** jump, loop, or invent a menu from `onEnd`. Selectors keep a
`PlaylistApplication` running; script calls `IPlaylist.load`. An older patent
copy saying default `0` = pause at end frame is ID-number OCR drift; discs use
IDREF and the stop wording.
`[SRC: PATENT | US20070091495A1 Title onEnd attribute]` **VERIFIED**
`[SRC: CORPUS | 3196 Title, 3192 with onEnd | e07/e12]`

**9. titleTimeEnd exclusive.** Patent: valid periods of PrimaryAudioVideoClip
shall not overlap; presentation begins at `titleTimeBegin` and ends at
`titleTimeEnd`. Corpus: **1527** abutting pairs (`end == next.begin`),
**0** overlaps, **12** gaps of 1–4 ticks. If end were inclusive, abutting
pairs would double-map the shared tick. Implement `[begin, end)`.
`[SRC: PATENT | US20070091495A1 “shall not overlap each other on Title Timeline”]`
`[SRC: CORPUS | 4847 clips | e12]` **VERIFIED**

**10. Timeline gaps.** 12 gaps are 1–4 ticks (1408 extras, Resident Evil 3
trailers) — authoring slivers, not missing reels. Patent: Main Video is scaled
into the Aperture; **outer frame** colour is `MainVideoDefaultColor` (area
outside the video on the canvas). With no Presentation Object mapped, there is
no main video → paint the aperture with that colour (typically `108080` =
16,128,128 YCbCr black). Do not error; do not hold the previous clip past
`titleTimeEnd`.
`[SRC: PATENT | US20070091495A1 Main Video Decoder / outer frame]` **INFERRED**
`[SRC: CORPUS | 12 gaps, all ≤4 ticks | e12]`

**11. Overlapping PrimaryAudioVideoClip.** Forbidden by patent; **0 / 4847**
in corpus. If a broken disc overlaps, do not z-blend (one main-video decoder).
Reject or last-wins is player policy; this spec treats overlap as authoring
error.
`[SRC: PATENT | same as Q9]` **VERIFIED** (forbidden + 0 observed)

**12. clipTimeBegin ≠ 0.** **133** clips (DLS extras, PEVOB offsets, Pan’s
`start_menu`, etc.). Seek: `local = T − titleTimeBegin + clipTimeBegin`, then
MAP walk (sheet 07). Default `00:00:00:00` = start of the Presentation Object.
Patent: `clipTimeBegin` is the PTS of the coded frame at that offset.
`[SRC: CORPUS | 133 | e12]` **VERIFIED**
`[SRC: PATENT | US20070091495A1 clipTimeBegin = PTS of coded frame]`

**13. seamless="true".** *“this and the one mapped directly before this satisfy
the seamless conditions.”* Default `false`. Corpus: **614** true, 765 false,
3468 omitted. Decoder: do not flush / re-init across that boundary (audio
gapless, PCR/STC continuous as authored). Still two MAP/EVO files. Not a
second MAP format.
`[SRC: PATENT | US20070091495A1 PrimaryAudioVideoClip seamless attribute]`
`[SRC: CORPUS | 4847 clips | e12]` **VERIFIED** (flag); decoder details **INFERRED** from “seamless conditions”

**14. StreamingBuffer@size.** Units are **pack / logical-sector** (2048 B), not
KiB. Omitted or `"0"` → 0. Used for **network secondary** S-EVOB into the
Streaming Buffer half of Data Cache (min Data Cache 64 MB). `"0"` on 246/247;
`"1024"` on `OLIVER_TWIST_JPN` VPLST000. Disc-only linear play: ignore a 0
buffer.
`[SRC: PATENT | US20070091495A1 “pack size (logical block size or logical sector size) as a unit”]`
`[SRC: CORPUS | 246×0, 1×1024 | e12]` **VERIFIED**

**15. Aperture.** Full visible image / HDi canvas. Origin (0,0). Main Video is
**scaled into** it; 4:3 gets side panels of `MainVideoDefaultColor`. XSD allows
`1280x720` and `1920x1080`. Corpus: **247 / 247** are `1920x1080`. Implement
both; do not letterbox a 1080 plane into 720 unless the playlist says 720.
`[SRC: PATENT | US20070091495A1 Aperture / Main Video scaler]`
`[SRC: CORPUS | 247 | e12]` **VERIFIED**

**16. MainVideoDefaultColor.** YCbCr 6 hex digits, 16≤Y≤235, 16≤Cb,Cr≤240.
Applied to the canvas **outside** the scaled main video (letterbox/pillarbox),
and to the aperture when no video is mapped (Q10). Not an under-video
transparency layer.
`[SRC: PATENT | US20070091495A1 outer frame COLAT Y,Cb,Cr]` **VERIFIED**

**17. Playlist@type.** XSD default `Advanced`. Corpus: omit 168, explicit
Advanced 79, **0** Original/UserDefined.
`[SRC: CORPUS | 247 | e12]` **VERIFIED**

**18. xml:base.** **0** on Playlist/Title in 247 files. Relative URIs resolve
from the file’s own URI (`file:///dvddisc/ADV_OBJ/…`). Patent: xml:base follows
XML Base when present.
`[SRC: CORPUS | 247 | e12]` **VERIFIED**

**19. Missing / bad mediaAttr.** Three playlists have no `MediaAttributeList`:
the three **selectors** (0 clips). On clip-bearing playlists, `@mediaAttr` indexes
the matching `*AttributeItem@index` (1-based). A pointer past the list is
authoring error — do not invent a codec; fail that stream. Default `@mediaAttr`
is 1 when omitted.
`[SRC: CORPUS | MAL missing = 3 selectors | e12]` **VERIFIED**
`[SRC: XSD | Playlist.xsd mediaAttr / index]`

**20. XPL codec vs V_ATR vs PES.** Demuxer keys off **XPL `MediaAttributeList`**,
not VTI `V_ATR` (sheet 06: V_ATR often MPEG-2 while XPL says VC-1). PES:
MPEG-2 `stream_id=0xE0`; AVC `0xE2`; VC-1 `stream_id=0xFD` +
`stream_id_extension=0x55`. GRINCH `INTRO.EVO` head: 199/200 packs `0xFD`/`0x55`
+ VC-1 SEQ `00 00 01 0F`.
`[SRC: PATENT | US20080298219A1 TABLE 45]`
`[SRC: DISC | GRINCH INTRO + sheet 06 V_ATR disagreement]` **VERIFIED** on those specimens

**21. Missing MAP / pack-count mismatch.** No playlist MAP URI is missing from
listings (Q4). EVOBI+274 ≠ file packs only on Pan’s interleaved angles (15
rows share files). Missing MAP: fail that title (cannot seek). Non-angle
pack-count mismatch: treat as damaged EVOB; do not “play the disc anyway”
without a MAP. Player-UI policy beyond that is OPEN.
`[SRC: CORPUS | e11 pack_ok 2416/2431]` **INFERRED** (error policy)

**22. NetworkTimeout.** Patent: `timeout` is **milliseconds**. Present on 14
playlists, all `"0"`. Linear disc play does not wait on the network; `0` means
disconnect immediately / no wait. Ignore for disc-only MVP.
`[SRC: PATENT | US20070091495A1 NetworkTimeout “milliseconds” / “unit of mS”]`
`[SRC: CORPUS | 14×0, 233 omitted | e12]` **VERIFIED**

---

## S — Seek, time, layers, angles

**23. timeBase 50fps.** XSD allows `50fps` | `60fps`. Corpus **247 / 247** are
`60fps`. Implement 50 (FF 00–49, MAP sum still fields vs 50 ticks/s). Do not
hard-code 60 in the parser; a 60-only player would reject a legal 50 disc.
`[SRC: XSD | FrameRateType]` **VERIFIED**
`[SRC: CORPUS | 247×60fps | e12]`

**24. tickBase vs timeBase vs elapsedTime.** `timeBase` = Title Timeline /
`timeExpression` (media clock). `tickBase` = markup / application tick clock.
`ITitle.elapsedTime` is title-timeline time. MAP `EVOBU_PB_TM` sums as **title
ticks on `timeBase`**, not tickBase. 29 playlists have `tickBase="24fps"` with
`timeBase="60fps"` — still walk MAP at 60.
`[SRC: PATENT | US20070091495A1 timeBase vs tickBase / media clock vs page clock]`
`[SRC: SRCCODE | iHD_Scripting_API.txt ITitle.elapsedTime]` **VERIFIED**

**25. tickBaseDivisor.** *“if tickBaseDivisor value is 3, Advanced Application
Manager shall process one of the three Application Ticks.”* Titles: omit/default
1 × 2425, explicit 1 × 303, 2 × 33, 3 × 36, **4 × 399**. Divides application
ticks, **not** the title timeline / MAP.
`[SRC: PATENT | US20070091495A1 tickBaseDivisor]`
`[SRC: CORPUS | 3196 Title | e12]` **VERIFIED**

**26. PB_TM=30 at 23.976.** On a `60fps` title, `EVOBU_PB_TM` is video **fields**
counted as title ticks: 30 = 0.5 s of **title** time, independent of encoded
frame rate. Sheet 07 + patent media clock. Confirmed by 24fps-tickBase titles
still using 60 timeBase.
`[SRC: PATENT | 60 Hz system = 1/60 s per timeline count]` **VERIFIED** as title-time
`[SRC: DISC | PCI 45045 ticks = 500.5 ms on checked VOBUs | sheet 08]`

**27. Seek to titleDuration.** `titleTimeEnd` of objects must be **less than**
`titleDuration`. Seeking to duration is past the last mapped tick: end-of-title
(then `onEnd` or stop, Q8). Do not decode a last EVOBU *as if* duration were
inclusive.
`[SRC: PATENT | “end time of all Presentation Object shall be less than the duration”]` **VERIFIED**

**28. Chapter not on EVOBU boundary.** Chapter is a title-time mark. MAP walk
returns the **containing** EVOBU (`acc_tm + PB_TM > need`). No requirement that
`titleTimeBegin` equal an EVOBU start.
`[SRC: DERIVED | sheet 07 seek + Chapter titleTimeBegin]` **VERIFIED** (algorithm)

**29. Trick-play refs.** MAP `1STREF_SZ` = packs through first reference
picture — enough to land a decode. DSI `vobu_2ndref_ea` / `3rdref_ea` still
OPEN (tail not closed). MVP: use `1STREF_SZ`.
`[SRC: PATENT | TABLE 83 1STREF_SZ]` **INFERRED** for 2nd/3rd

**30. Dual-layer FEATURE_1 + FEATURE_2.** Always **two clips** on the title
timeline in this corpus (**158** titles with `_1` and `_2` MAP srcs). No single
MAP/EVO spans the layer break. EVOBI+282 is non-zero on many part-2 rows (Q31).
`[SRC: CORPUS | 158 titles | e12]` **VERIFIED**

**31. EVOBI+282.** Non-zero on 100 rows, almost all `FEATURE_2` / `PEVOB_2` /
`0x80000000` layer-1-ish. **Not** added to MAP pack addresses (seek still
`sum(EVOBU_SZ)×2048` in that file). Units / official name **uncloseable**.
Ignore for seek.
`[SRC: CORPUS | e11 extra282=100]` **OPEN** (name); **VERIFIED** (do not add to offset)

**32. Pan’s angleNumber → TMAPI.** XPL `Video@angleNumber` 1–4 on
`ofelia*.MAP` (Ns=4) and 1–3 on `death.MAP` (Ns=3). 1-based angle → TMAPI
index `angleNumber − 1`. One EVO file; ILVU_ENT at `ILVUI_SA` stitches pack
runs. Sequence-key walk on a player still OPEN (Q34).
`[SRC: DISC | PANS_LABYRINTH VPLST001 + four interleaved MAP | e03/e12]` **VERIFIED** (index)
`[SRC: PATENT | TABLE 84 ILVU_ENT]` **INFERRED** (stitch)

**33. ILVU_ENT_Ns=0.** **0** on 2417 contiguous **and** the four interleaved
maps. Ignore the SRP field; walk ILVU until `ILVU_SZ=0`. No other interleaved
disc in this corpus.
`[SRC: CORPUS | e03 + sheet 07]` **VERIFIED**

**34. Sequence-key ILVU playback.** File parse is specified; player-side
angle/SK section walk is **OPEN** (Pan’s only). Linear non-angle titles do not
need it.
**OPEN**

**35. ETERNAL_SUNSHINE 28 EVOBI vs 29 MAP.** Extra file is **`DELEXT8.MAP` /
`DELEXT8.EVO`** — on disc, **not** in EVOBI. Playlist `src` is the MAP: if XPL
never references `DELEXT8`, VTI-only players miss nothing; if a title maps it,
open the sibling EVO anyway (sibling rule Q4). Do not drop clips because EVOBI
`nr` is short.
`[SRC: CORPUS | ETERNAL_SUNSHINE listing vs EVOBI names]` **VERIFIED**

**36. EVOB_ATR_SA.** `0xFFFFFFFF` on primary maps (2417/2421). Player reads
attributes from VTI ATRI (and codecs from XPL). MAP attribute table unused
here.
`[SRC: CORPUS | e03]` **VERIFIED**

**37. TMAP_TY.** Only `0x2000` (2417) and `0x2202` (4 Pan’s). Bit 13 set on all.
`[SRC: CORPUS | e03]` **VERIFIED**

**38. TMAPI_Ns 3 and 4.** Only Pan’s four interleaved maps (3 on `death`, 4 on
the three `ofelia*`). Angles, not something else. Seek uses TMAPI[`angleNumber−1`],
not always TMAPI[0].
`[SRC: CORPUS | e03/e12]` **VERIFIED**

---

## A — Audio, subtitles, tracks

**39. Audio@streamNumber → PES.** `streamNumber` is 1-based (XSD default 1).
Audio (non-MPEG) is `private_stream_1` (`stream_id=0xBD`); first payload byte
is `sub_stream_id` (TABLE 46). Low 3 bits `***` = decoding audio stream number
— **infer 0-based** (`streamNumber − 1`), DVD-style:

| Codec | sub_stream_id |
|---|---|
| AC-3 | `10000***b` (`0x80+n`) |
| DD+ | `11000***b` (`0xC0+n`) |
| DTS-HD | `10001***b` (`0x88+n`) |
| LPCM | `10100***b` (`0xA0+n`) |
| MLP | `10110***b` (`0xB0+n`) |
| MPEG audio | `stream_id=110x 0***b` (TABLE 45) |

Full pack census vs every `streamNumber` was **not** re-run on feature EVOs
this pass (no EVO bodies saved). Use the table; confirm on first muxed clip.
`[SRC: PATENT | US20080298219A1 TABLE 45–46]` **VERIFIED** (IDs)
`[SRC: XSD | streamNumber default 1]` **INFERRED** (`n = streamNumber−1`)

**40. Subtitle streamNumber.** SP is `private_stream_1`, `sub_stream_id`
`001*****b` with 5-bit stream number. Codec `2bitRLC` vs `8bitRLC` is
`SubpictureAttributeItem`, not the substream id. HD DVD 8-bit SP byte layout
vs DVD 2-bit remains **OPEN**. Demux: route `0xBD` + `001*****` to SP decoder;
pick stream by `*****`.
`[SRC: PATENT | TABLE 46 Sub-picture]` **VERIFIED** (id)
**OPEN** (8-bit RLC bytes)

**41. Default audio track.** `TrackNavigationList` absent on **718 / 3196**
titles; empty on 15 (selectors). Patent `defaultLanguage` selects **application**
language, not audio. Default audio: first `Audio` child / track 1, then player
locale vs `AudioTrack@langcode` when TNL exists. `TitleSet@defaultLanguage` is
ISO 639-1 for apps (`en` 190, `de` 31, `ja` 23, `fr` 3).
`[SRC: CORPUS | TNL absent 718 | e12]` **INFERRED** (audio default)
`[SRC: PATENT | defaultLanguage = menu language fallback]`

**42. langcode `xx:NN`.** XSD `LangCodeType`: `(([a-z][a-z])|\*):[0-9A-F][0-9A-F]`.
`xx` = ISO 639-1 (two letters) or `*`; `NN` = DVD-style **specific code
extension** (hex). `PlaylistApplication@language` uses XSD type *named*
`ISO639-2` but the enumeration is the same **two-letter** set (`en`, `fr`).
Do not look up 3-letter ISO 639-2 codes.
Top corpus: `en:01` 2684, `fr:01` 1373, `en:00` 634, `en:05` 601. `*:NN` =
language not specified; `defaultLanguage` does not rewrite `langcode`.
`[SRC: XSD | LangCodeType + patent langCode BNF]`
`[SRC: CORPUS | 14709 langcode | e12]` **VERIFIED**

**43. SubtitleTrack@forced.** XSD boolean. Corpus: omit 10810, `false` 449,
**`true` 0**. Forced means auto-enable even if the user selected “off”
(DVD convention / `ISubtitleTrack.forced`). Unobserved here; still implement
the flag.
`[SRC: CORPUS | 0 forced=true | e12]` **INFERRED** (semantics)
`[SRC: SRCCODE | ISubtitleTrack.forced]`

**44. AST_ATR.** 4-byte words at ATRI+16, count `AST_Ns` at +14. Decoder **must
not** prefer these over XPL. If a title has no `Audio` children, ATRI can still
describe the EVO — use TABLE 9-class bits only as fallback. Bitfields not
closed against these 4-byte HD DVD words (Standard VTS uses 8-byte
`VTS_AST_ATR`).
`[SRC: CORPUS | e11 AST_Ns]` **OPEN** (bit layout) / **VERIFIED** (ignore when XPL present)

**45. SP_ATR.** 5-byte words after `SP_Ns` at +229. Same policy as Q44.
**OPEN** (bit layout)

**46. ATRI flags `1000` / `0500` / `0400`.** Histogram only (`0000` 987,
`1000` 125, rare others). Not closed as multi-angle/seamless. Ignore for
Advanced demux.
`[SRC: CORPUS | 1131 ATRI]` **OPEN**

**47. ATRI+6 extra word.** 19 / 1131 (`60105000` ×12, …). SubVideo unused in
XPL (0). Do not treat as SubVideo without a matching XPL child. Ignore for MVP.
`[SRC: CORPUS | e11 plus6=19]` **OPEN** (name) / **VERIFIED** (not stream count)

**48. Palette at +391.** 7 ATRIs filled with dummy `7f7f7f00`. Not a YCrCb
table. Advanced subs are HDi or SP_PCK; do not require this palette.
**OPEN** / uncloseable as a named table

**49. SubVideo / SubAudio / SecondaryAudioVideoClip.** **0** in 247 XPL. MVP
may skip those clip types. Demux should still **drop** `VS_PCK` / `AS_PCK` if
they appear rather than feeding them to main AV. Secondary clip types remain
legal in the XSD.
`[SRC: CORPUS | 0 Secondary/SubVideo | e02]` **VERIFIED** (unused)
`[SRC: PATENT | TABLE 85 pack types]`

---

## M — Menus, ACA, HDi, selectors

**50. After FirstPlayTitle.** FirstPlayTitle has no `onEnd`. Next is **Title 1**.
PlaylistApplication becomes valid on all titles **except** FirstPlayTitle
(loaded into File Cache *during* FPT). Not “FPT ends → menu app instead of
Title 1”.
`[SRC: PATENT | FirstPlayTitle (a), PlaylistApplication lifetime FIG.70]` **VERIFIED**

**51. autorun="false".** *“the active state is not provided unless a
specification based on an API command is accepted.”* Default `true`. Corpus:
false **136**, true 2168, omit 225. Wait for script/API; do not auto-start.
`[SRC: PATENT | US20070091495A1 autorun]`
`[SRC: CORPUS | e12]` **VERIFIED**

**52. sync hard vs soft.** Default `hard`. Hard: **hold Title Timeline** until
File Cache load + startup finish. Soft: prefer seamless timeline; app **may
not run** if you jump into its valid period or leave trick-play. Corpus: hard
2120, omit (hard) 105, soft 304.
`[SRC: PATENT | Hard-Sync / Soft-Sync Application]`
`[SRC: CORPUS | e12]` **VERIFIED**

**53. zOrder.** Application z-order on the **graphics** plane. Primary video is
the video plane (scaled into Aperture), not zOrder 0 of apps. Higher zOrder
composites on top of other apps. Required attribute on ApplicationSegment.
`[SRC: PATENT | zOrder “Application z-ordering and rendering into the graphics plane”]` **VERIFIED**

**54. language / group / appBlock.** Application Activation Information. Pick
the app whose `language` matches `Player.menuLanguage`; else
`TitleSet@defaultLanguage`. Same `appBlock` = language variants of one app
(valid period and autorun must match). `group` for grouping; shall not be
present when appBlock is used (patent constraints).
`[SRC: PATENT | FIG.57 application block / defaultLanguage]` **VERIFIED**

**55. ApplicationResource@priority.** Required on ApplicationResource; absent
on PlaylistApplicationResource (455). Values 1 (2440), 2 (32), 3 (34). Load
higher-priority first; File Cache eviction when over 64 MB resource cap
(author shall keep ≤ 64 MB).
`[SRC: CORPUS | e12]` **VERIFIED** (values)
`[SRC: PATENT | resource size ≤ 64 MB]` **INFERRED** (eviction)

**56. ApplicationResource@size.** Bytes reserved in File Cache. Jumpstart:
size **may be larger** than the file, **must not be smaller**. Discs:
MATRIX selector 2008 = file; BLADE `size="5000"` vs 2831-byte ACA; TRAINING
`4096` vs 3075. Reject if on-disc size **>** declared size; allow declared >
actual.
`[SRC: WEB | https://learn.microsoft.com/en-us/archive/blogs/amyd/dissecting-hello-world]`
`[SRC: DISC | three selector XPL vs listing sizes]` **VERIFIED**

**57. multiplexed false vs 0 vs 1.** XSD: `false` | nonNegativeInteger — **not**
boolean true. `false` = load from URI. Positive integer = ADV_PCK slot.
`"0"` on 12 PlaylistApplicationResource rows is integer 0, not the token
`false`. No disc uses slot 0. Those 12 `src` values are ACA files in
`ADV_OBJ`. **Always load `src`** (same as `false`). The earlier “do not treat
`0` as URI” line is **refuted**.
`[SRC: XSD | MultiplexedDataType]`
`[SRC: DISC | 12× multiplexed="0" ACA URIs; e16 slots 1–6]` **VERIFIED**

**58. GRINCH multiplexed=1.** INTRO head has no ADV_PCK `0x80`. Same class as
OLIVER `LoopMenu.EVO`: a positive slot does not imply packs in that clip.
Load `src`; consume ADV_PCK when present (`STALINGRAD` `logo.EVO`).
`[SRC: DISC | GRINCH INTRO; e16 OLIVER LoopMenu 0 hits; STALINGRAD logo]` **VERIFIED** (absence vs presence)

**59. ADV_PCK 0x80 payload.** `private_stream_2` substream `0x80`. First
packet: slot + ACA filename + ADDTHD padding until `HDDVDACA` (STALINGRAD:
225 zero bytes; do not hard-code offset 259). Middle/last: slot + `0x00`
then ACA at offset 4. Concat per slot equals the `ADV_OBJ` file
(`e16` six archives).
`[SRC: DISC | e16 STALINGRAD logo.EVO]` **VERIFIED**
`[SRC: PATENT | TABLE 47]` **VERIFIED** (id)

**60. ACA formula beyond N=4.** Now **6** saved archives, **30** members:
MATRIX/BLADE/TRAINING selectors + PREMONITION + SHREK coloring + STALINGRAD
mainApp. Record = `14 + (flags & 0xFF) + 32` on **30 / 30**. Still 409 listed;
formula holds on every saved file.
`[SRC: DISC | 6 ACA | e11]` **VERIFIED** (N=6) / remaining 403 **INFERRED** same format

**61. Flags high byte.** `0xff` = AACS-wrapped members: raw CRC **fails**, 283-byte
`AACS` sidecar before payload (5/6 archives). `0x02`–`0x07` on STALINGRAD:
uncompressed members, raw CRC **matches**. Not a compression enum (encoding
type is 1 on all six). High byte is wrap/CRC class, not “encrypt vs compress”
beyond that.
`[SRC: DISC | e11]` **VERIFIED**

**62. 283-byte AACS sidecar.** Starts `AACS`; contains member `name+".AACS"` and
length echo. Internal fields **OPEN**. Extract members by directory
offset/length without parsing it.
**OPEN**

**63. 0xff member CRC.** Not CRC of raw payload. Could be CRC of decrypted
bytes — cannot test (no keys). Archival extract: **skip CRC** on `0xff`; still
extract.
`[SRC: DISC | e11 crc_ff_fail]` **INFERRED** (skip forever for extract)

**64. JS encoding.** Every saved `.js` (20 files: 3 loose `1408` + 17 ACA members)
is **UTF-16BE with BOM `FE FF`**. PREMONITION `main_menu.xmu` is UTF-8.
The claim that 1408 loose script is UTF-8 is **refuted**.
`[SRC: DISC | e15 N=122 JS]` **VERIFIED**

**65. Manifest without Markup.** XSD: `Markup` minOccurs 0. `1408` `extras.xmf`:
Region + Script + Resource, no Markup. Engine still creates the Region and
runs Script.
`[SRC: XSD | Manifest.xsd Markup minOccurs=0]`
`[SRC: DISC | 1408 extras.xmf | sheet 05]` **VERIFIED**

**66. Resource duplicating Script@src.** Jumpstart: Script `@src` **and** a
Resource row are both required for that file. Size is only on the playlist
resource. Treat the duplicate as required preload into File Cache, not noise.
`[SRC: WEB | Jumpstart Dissecting Hello World / Chapters]` **VERIFIED**

**67. IPlaylist.load argument.** Full disc URI string, not a number.

```
Player.playlist.load("file:///dvddisc/ADV_OBJ/VPLST000.XPL");
```

MATRIX: `fr` → VPLST001, `en`/default → VPLST000.
BLADE: `ja` → 001, else 000.
TRAINING_DAY: `fr` → 001, `de` → 002, else 000.
PREMONITION also concatenates `"file:///dvddisc/ADV_OBJ/" + "VPLST080.XPL"`
and `Player.playlist.load(psUrl + playlist)` for persistent storage.
`[SRC: DISC | MATRIX/BLADE/TRAINING selector.aca/script.js UTF-16BE | e12]` **VERIFIED**

**68. load vs FIG.51 soft reset.** `load` replaces the playlist document and
re-runs Advanced startup for that XPL (File Cache resources for the **new**
playlist; Data Cache split from new Configuration). Not a disc re-insert:
DISCID is not re-probed for category. Patent: if the new playlist should
persist, store it under Provider ID + Content ID. Soft reset ≠ full medium
detect (FIG.7).
`[SRC: PATENT | US20070091495A1 Soft Reset / FIG.51; FIG.50 step 4 wipe File Cache]` **INFERRED**

**69. clock=page vs titleTimeBegin.** ApplicationSegment `titleTimeBegin/End`
schedule **whether the app is on the timeline**. iHD `timing@clock` default
`title`; `page` / `application` are markup-local clocks (`clockDivisor`
default 1). Title timeline is master for mapping; page clock is master for
cues **inside** an active markup. Both exist; they are not the same clock
(Q24).
`[SRC: XSD | iHD.xsd timing clock title|application|page]` **VERIFIED**

**70. Minimum API for selectors + Play.** Selectors need only
`Player.menuLanguage` and `Player.playlist.load(uri)` (plus try/catch).
Typical “Play movie”: `Player.playlist.titles[id].jump("00:00:00:00", false)`
or `chapters[n].jump`. Second argument is pause-at-destination (`true` =
seek then pause; `false` = seek without forcing pause). Extras on `1408`
`jump(..., false)` with no `play()` and still play. Chapter buttons call
`play()` after `jump` because the menu title was paused. Typelib
`play`/`pause` are on `IPlaylist`. Markup `cue` /
`state:focused()` / click. Typelib 106 interfaces; that subset is enough for
the three selectors + Jumpstart Chapters.
`[SRC: DISC | three script.js]`
`[SRC: WEB | Jumpstart Dissecting Chapters]`
`[SRC: SRCCODE | iHD_Scripting_API.txt IPlaylist/ITitle]` **VERIFIED**

**71. Fonts.** Jumpstart Hello World ships `font.ttf`. PREMONITION `client.aca`
contains `font.ttf`; SHREK coloring contains markup that needs bundled fonts.
`IFontCapabilities` CLASS_1/CLASS_2 are player-builtin. If a Resource lists a
TTF, File Cache **must** load it or the designed menu will not match. Not
proven that a disc “will not render” without it (no HDi rasteriser here).
`[SRC: DISC | PREMONITION font.ttf member]` **INFERRED** (required when listed)

**72. .CER.** 10 listed files, 811 or 1419 bytes. Bodies not saved. Likely
X.509 for HDi TLS. Linear play ignores them. **OPEN** (ASN.1 not fetched)

**73. Persistent-storage path.** Two layers:

Script FileIO / `IPlaylist.load` of a stored playlist (PREMONITION `script.js`,
Jumpstart network sample):

```
psUrl = "file:///required/" + PersistentStorageManager.contentId + "/"
Player.playlist.load(psUrl + playlist)
```

Also `file:///filecache/`. Saved JS never writes `file:///fixed/` or
`file:///removable/` (`e15`). FIG.20 **drawing** matches the disc; the same
patent’s prose (`file:///fixed/`) is **refuted** for this API.

FIG.50 VPLST *search* still uses DISCID `PROVIDER_ID` + `CONTENT_ID` as the
area to look for `VPLST$$$.XPL`. That OS directory spelling (binary
PROVIDER_ID) is a different layer and stays **OPEN**.
`[SRC: DISC | PREMONITION_GER client.aca/script.js | e15]` **VERIFIED** (required URI)
`[SRC: WEB | https://learn.microsoft.com/en-us/archive/blogs/amyd/very-simple-network-example]`
`[SRC: PATENT | US20070091495A1 FIG.20 drawing vs body]` **refuted body**

**74. SEARCH_FLG=0, no P-storage VPLST.** *Search persistent storages, then
search ADV_OBJ, then take the highest number among **found** files.* Empty
P-storage → disc VPLST only. `SEARCH_FLG=1` skips P-storage (13 discs).
`[SRC: PATENT | US20070091495A1 FIG.50 steps S42–S45]` **VERIFIED**

**75. Non-Disc dataSource.** PrimaryAudioVideoClip: XSD only `Disc`. Corpus:
explicit Disc 3933, omit 914, **other 0**. Secondary clip types may use
P-Storage (0 specimens).
`[SRC: CORPUS | e12]` **VERIFIED**

**76. ScheduledControlList Event.** `Event@titleTime` + optional `id`: **event
firing for Advanced Application** at that title time (script may handle late).
`PauseAt@titleTime`: pause the Title Timeline (map to video PTS if inside a
P-EVOB). 2696 Event (86 discs), 92 PauseAt. Not `jump`. Listeners:
STALINGRAD `application.addEventListener("title_end", …)` is a different API
(title end), not Scheduled Event.
`[SRC: PATENT | ScheduledControlList PauseAt | Event]`
`[SRC: CORPUS | 2696 Event, 92 PauseAt | e12]` **VERIFIED**

**77. PlaylistApplication vs ApplicationSegment.** PlaylistApplication lifetime
= all titles except FirstPlayTitle; ApplicationSegment is mapped on one title.
They **composite together** (patent FIG.72: feature video + playlist chrome).
Language-match PlaylistApplication for the whole playlist.
`[SRC: PATENT | FIG.70–72]` **VERIFIED**

---

## K — AACS layout (format only)

**78. CHT before decrypt.** Book: verify CHT #1/#2 (and cert) in the AACS
startup sequence **before / while** playing P/S-EVOB. Licensed player: yes.
This corpus cannot test (stripped packs, `e09` all `PES_scrambling_control=00`).
Document as book-only.
`[SRC: SPEC | AACS HD DVD Pre-recorded Book Final 0.953 §3.8 / startup list]` **VERIFIED** (book)

**79. CHT #1 vs #2.** #1: 4-byte NHV + 4 reserved + **8-byte** (LSB64 SHA-1)
hashes of every EVOBU/TU; NHV ≤ 500000; stride 8 after 8-byte header. #2:
hashes of DISCID, DKF, Managed Copy manifest (20-byte), TUFs (20-byte), XML
and ECMAScript (8-byte). Bodies not saved; listed sizes vary. Header-only
fetch not required to implement the table.
`[SRC: SPEC | Final 0.953 Tables 3-18 / 3-19]` **VERIFIED** (book)

**80. BEE.** CONTENT_CERT byte 1 bit 7. MATRIX `AAC!/CONTENT_CERT.AACS`: type
`00`, BEE byte `00` → **not set**. Bus encryption is drive↔PC host for EVOB
reads (book 4.3.5); Archive.org ISOs are not bus-encrypted. Software ISO
player: ignore BEE. Other 103 certs not fetched.
`[SRC: SPEC | Table 3-17 BEE]`
`[SRC: DISC | MATRIX CONTENT_CERT 120 B]` **SINGLE** (bit) / **VERIFIED** (ignore on ISO)

**81. TITLE_KEY_PTR.** KMI bytes 1–2, 16-bit big-endian (example `0009h`).
BackupHDDVD `CPIField[2]` works if the high byte is 0. `KEY_VF=00b` → pointers
invalid, do not decrypt (all saved NV_PCK CPI zero). Cannot test `KEY_VF=10b`
on stripped ISOs.
`[SRC: SPEC | Table 4-2 KMI]` **VERIFIED** (layout) / **OPEN** (live encrypted pack)

**82. CPI at 0x3C without system header.** All confirmed NV_PCK have `0xBB`
system header; `0x3C` is then GCI-payload offset 12. A pack that omits `0xBB`
would shift GCI. Parse by `sub_stream_id 0x04`, do not assume pack-absolute
`0x3C` if framing differs. Unobserved.
`[SRC: DISC | sheet 08 typical prefix]` **INFERRED** / unobserved omit-BB

**83. Extra VTKF without VPLST.** `BALLS_OF_FURY`, `CHUCK_AND_LARRY`,
`SHREK_THE_THIRD_EU`. Match `PLAYLIST_NAME` to the **active** XPL (including
after `IPlaylist.load`). If that `$$$` is never loaded, ignore the extra VTKF.
`[SRC: CORPUS | sheet 09 / e05]` **INFERRED**

**84. VTKF size.** Nominal 2480 (64 slots). Pan’s VTKF001/003 = **2516** (65
slots). Size from `HD_VTKF_SIZE`; no other sizes in saved files (`e04` checks
2480 magic files).
`[SRC: CORPUS | e04/e01]` **VERIFIED**

**85. ANY! vs AAC!.** Mutually exclusive in corpus (96 vs 8). Book directory
name is `AACS`. Probe `ANY!`, then `AAC!`, then `AACS`.
`[SRC: CORPUS | e01]` **VERIFIED**
`[SRC: SPEC | “AACS” directory]`

**86. 16 discs, no AACS directory.** Mix: 15 Category 2 unencrypted + Category 1
`RESERVOIR_DOGS`. Includes `STALINGRAD`, `DOWNFALL`, `TRAINING_DAY`, `1408_DC`,
… Player must **not** require `MKBROM`. `e09`: 704/704 packs
`PES_scrambling_control=00` on the stripped set.
`[SRC: CORPUS | 16 listings | e09]` **VERIFIED**

**87. Volume ID MMC.** `READ DISC STRUCTURE` 80h after AACS auth. Not in ISO.
**Uncloseable** from this corpus.
**OPEN**

**88. VTUF URS_NUM>0.** 217/217 listed files are 144 B → `URS_NUM=0`. Implement
the zero case; treat larger as future.
`[SRC: CORPUS | e11]` **VERIFIED**

**89. DKF.** Directory key for persistent-storage files, not EVO. Needed if
`SEARCH_FLG=0` and a downloaded VPLST lives under that directory. Disc-only
play: ignore.
`[SRC: SPEC | DKF Table 6-2]` **VERIFIED**

**90. AES-G / CBC.** Sheet 09.11 for a **licensed** port. Research demux of
Archive.org ISOs: do not decrypt; packs are already clear (`e09`). Do not ship
keys.
`[SRC: CORPUS | e09]` **VERIFIED**

---

## U — Out of scope / uncloseable / later

**91. MMC “this is HD DVD”.** Not in corpus. Working probe: UDF 2.50 +
`HVDVD_TS/` (then VPLST vs IFO). **OPEN** as an MMC command.

**92. Category 3 / HVSO.** 0/120. Do not invent a hybrid navigator.
`[SRC: CORPUS | e11]` **VERIFIED** (absence)

**93. APLST.** 0/120. Audio-only FIG.50 branch unused.
`[SRC: CORPUS | e07/e11]` **VERIFIED**

**94. Firmware vs FIG.50.** Public catalog only; no RE. FIG.50 is checked
against XPL/DISCID (sheet 10.7). **Uncloseable** as firmware confirmation.

**95. PCI HLI / DSI tails.** Advanced shall ignore HLI. MAP seek does not need
`sml_pbi` / `vobu_sri` / `synci`. Close only if extra trick-play needs them.
**OPEN** (optional)

**96. GCI DCI/CCI/RECI.** Copy-control / ISRC display, not demux. CPI lives in
the GCI packet (Q81–82).
`[SRC: PATENT | GCI tables]` **VERIFIED** (not demux)

**97. parentalLevel.** Default `*:1`. Minimum level per ISO-3166 country.
Enforcement is **player policy** vs user setting; disc only stores the floor.
`[SRC: XSD | parentalList]` **VERIFIED** (field) / policy OPEN

**98. Region.** Shipped DISCID reserved 67 bytes are **zeros** (119/119) — no
region flag. No `RGN$$$.XRG` in listings. US20080170840 describes a later
region-file idea, not this corpus. Region behaviour here is HDi
`Player.menuLanguage` / `countryCode` (selectors Q67). Not CSS region.
`[SRC: CORPUS | DISCID[61:]=0 | e11]` **VERIFIED**
`[SRC: PATENT | US20080170840 region file — not on these discs]`

**99. Thumbs.db / *.log.** Junk. Ignore. 4 discs have such files.
`[SRC: CORPUS | sheet 01]` **VERIFIED**

**100. Standard Content.** `RESERVOIR_DOGS` only. Out of scope for
`spec/advanced/`.
`[SRC: CORPUS | N=1]` **VERIFIED**
