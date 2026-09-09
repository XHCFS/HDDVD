# Implementer questions — Advanced Content player

Questions an implementer of a Category 2 player (titles, seek, demux, then
menus) still needs answered. Grounded in `spec/advanced/` 01–10, the v1.0
XSDs, and the corpus. Not firmware reverse-engineering.

**Answers (evidence-tagged):** [14_IMPLEMENTER_ANSWERS.md](14_IMPLEMENTER_ANSWERS.md)
(`e12` + selector `script.js` + patents/XSD/AACS book).

**Second pass (C-struct limits, remaining holes):**
[15_ADVERSARIAL_QUESTIONS.md](15_ADVERSARIAL_QUESTIONS.md) (`e13`).

**How to use:** pick a `Blocks` class, close with disc / XSD / patent figure /
more saved files, tag `[SRC]` + confidence, add an experiment if it is
machine-checkable. Disc wins over patents.

**Blocks**

| Class | Meaning |
|---|---|
| `L` | Linear feature playback (mount → playlist → MAP → packs → video/audio) |
| `S` | Seek, timeline, dual-layer, angles |
| `A` | Audio / subtitle / track selection correctness |
| `M` | Menus, File Cache, HDi, selectors |
| `K` | AACS on-disc layout (format only; no decryptor in this repo) |
| `U` | Uncloseable here, or skip for MVP |

---

## L — Linear playback

1. If `ADV_OBJ/` exists but has no `VPLST*.XPL` (only assets), is that Category 2
   failure, Category 1, or “try IFO”? Corpus always has both or neither except
   Standard. **Sheet 01 / 10.1**
2. Are UDF filenames case-sensitive on a real player? Listings are mixed
   (`menus.aca` vs `MainMenu.xmf`). Must URI match be exact?
3. Multi-extent `.EVO` / `.MAP`: `udfgrab` already walks extents. Is a player
   allowed to assume one extent? (DOWNFALL feature is huge — almost certainly
   multi-extent.)
4. When `FOO.MAP` exists and EVOBI names `FOO.EVO`, is a basename mismatch ever
   legal? If yes, EVOBI must win; if no, sibling path is enough.
5. `HVA00001.BUP` / `*.BUP`: when does a player open the BUP? Only if the
   primary read fails? Never observed. **Sheet 01.4**
6. `VPLST$$$.BAK` (3 discs): confirm players never boot from `.BAK` even if it
   is newer/higher? **Sheet 03**
7. After opening the highest XPL, is `FirstPlayTitle` auto-started, or does the
   player start `Title titleNumber="1"` unless HDi says otherwise? Patent
   restrictions (no `onEnd`) imply it is a bumper that must be left somehow.
8. The 4 `Title` elements without `onEnd` (3196−3192): which discs, last title
   vs broken authoring, and does the player **stop**, **loop**, or **return to
   menu**?
9. `titleTimeEnd` exclusive: confirm no sample has a clip with `begin ==
   next.begin` that would double-map a tick if end were inclusive.
10. Gaps on the title timeline (no `PrimaryAudioVideoClip` covering `T`): hold
    last frame, black + `MainVideoDefaultColor`, or error?
11. Overlapping `PrimaryAudioVideoClip` ranges on one title: last-wins,
    z-order, or authoring-forbidden? XSD does not forbid overlap.
12. `clipTimeBegin` default `00:00:00:00`: any clip where it is non-zero, and
    does MAP seek use that offset correctly today? **Need a corpus grep.**
13. `seamless="true"`: what exactly must the decoder do (no IDR flush, audio
    gapless, PCR continuity)? Packets still come from two MAPs/EVOs.
14. `StreamingBuffer@size`: units (bytes? KiB?) and whether a software player
    can ignore it when `size="0"`.
15. `Aperture@size` `1280x720` vs `1920x1080`: letterbox the 1080 plane, or is
    it only the HDi coordinate space?
16. `MainVideoDefaultColor`: applied under video, only in gaps, or only before
    first frame?
17. `Playlist@type` default `Advanced`: any non-Advanced type in 247 files?
18. `xml:base` on Playlist/Title: any disc uses it, and does it change URI
    resolution vs `file:///dvddisc/`?
19. Missing `MediaAttributeList` or `@mediaAttr` pointing past the list:
    reject the playlist or default codec?
20. `VideoAttributeItem@codec` vs VTI `V_ATR` disagreement (VC-1 vs MPEG-2
    nibble): confirm demuxer must key off XPL, and that EVO `stream_id` /
    `stream_id_extension` always matches XPL, never V_ATR. **Need pack census.**
21. Error policy if the MAP URI does not exist, or EVO size ≠ EVOBI `+274`
    packs (non-angle): skip title, black, or fail the disc?
22. `Configuration/NetworkTimeout`: units, and does linear play ignore it?

## S — Seek, time, layers, angles

23. `TitleSet@timeBase` is `60fps` on 247/247. Is a `50fps` playlist legal to
    implement, or can the player hard-code 60?
24. `tickBase` vs `timeBase`: which clock does HDi `ITitle.elapsedTime` use,
    and which does MAP `EVOBU_PB_TM` sum against? Sheet 07 sums `PB_TM` as
    title ticks on 60fps — is that true for `tickBase="24fps"` titles?
25. `tickBaseDivisor`: any non-1 in corpus, and what does it divide?
26. Video at 23.976/29.97 inside a 60fps title: is `EVOBU_PB_TM=30` always 0.5 s
    of **title** time regardless of encoded frame rate? (Sheet 07 says yes —
    confirm on a 24fps VC-1 feature.)
27. Seek to `titleDuration` exactly: last EVOBU, or end-of-title event?
28. Chapter `titleTimeBegin` not on an EVOBU boundary: land on containing
    EVOBU (MAP walk) or require exact field match?
29. Fast-forward / trick: use `1STREF_SZ` / `DSI.vobu_1stref_ea` only, or
    also `vobu_2ndref_ea` / `3rdref_ea`? DSI tail still OPEN.
30. Dual-layer: is `FEATURE_1.EVO` + `FEATURE_2.EVO` always two clips on the
    timeline, or can one MAP/EVO span the layer break?
31. EVOBI `+282` non-zero / `0x80000000`: layer-1 LBN, part index, or
    something a seeker must add to pack addresses? **Named OPEN.**
32. `PANS_LABYRINTH` angles: XPL `Video@angleNumber` → which TMAPI (1-based
    vs 0-based), and how ILVU_ENT runs stitch into one EVO file.
33. Why is `TMAPI_SRP.ILVU_ENT_Ns` 0 on the four interleaved maps? Must every
    player ignore it (sheet 07 says yes) — any other interleaved disc exist
    outside this corpus?
34. Sequence-key / angle ILVU on a **player** (not just file parse): still
    OPEN. Needed for Pan’s only.
35. `ETERNAL_SUNSHINE` 28 EVOBI vs 29 MAP: which file is extra, and does
    playback break if we trust VTI over the playlist?
36. MAP `EVOB_ATR_SA` is `0xFFFFFFFF` on primary maps. When would it be set,
    and would a player read attributes from the MAP instead of VTI?
37. `TMAP_TY` bits besides 13 and the Pan `0x0202`: any other values in 2421
    maps? (e03 says only `0x2000` / `0x2202`.)
38. `TMAPI_Ns` 3 and 4 (non-1): which discs, are they angles or something
    else, and does the seek loop walk TMAPI[0] only?

## A — Audio, subtitles, tracks

39. `Audio@streamNumber` vs PES: what `stream_id` / `sub_stream_id` is
    stream 1 vs 2 for `DD+`, `DTS-HD`, `LPCM`, `MLP`, `AC-3`? Need a table
    from dumped packs, not patents alone.
40. `Subtitle@streamNumber` vs SP_PCK substream IDs for `2bitRLC` vs
    `8bitRLC`. HD DVD 8-bit SP format vs DVD 2-bit: byte-level OPEN.
41. Default track when `TrackNavigationList` is absent: first `Audio` child,
    `defaultLanguage`, or player locale?
42. `langcode` `xx:NN` vs `*:NN`: what is `NN`, and how does `*:NN` interact
    with `TitleSet@defaultLanguage`?
43. `SubtitleTrack@forced`: auto-enable even if user selected “off”?
44. `AST_ATR` 4-byte words at ATRI+16: bitfields (coding, channels, language)?
    Decoder must not use them if XPL is present — still need them if XPL omits
    `Audio` children?
45. `SP_ATR` 5-byte words: same question for subtitles.
46. ATRI flags `1000` / `0500` / `0400`: multi-angle, seamless, or unused?
47. ATRI+6 extra word on 19 ATRIs: second video stream (SubVideo) attributes?
    SubVideo is unused in XPL corpus (0).
48. Palette at ATRI+391: ignore for Advanced (HDi draws subs?) or required
    for SP_PCK? Uncloseable as a named YCrCb table from this corpus.
49. `SubVideo` / `SubAudio` / `SecondaryAudioVideoClip`: 0 in corpus. Can MVP
    reject them, or must demux still route VS/AS packs if present in an EVO?

## M — Menus, ACA, HDi, selectors

50. After `FirstPlayTitle` finishes with no `onEnd`, does a `PlaylistApplication`
    become the menu, or is Title 1 started? Needs XPL+script reading on a
    typical WHV disc, not firmware.
51. `ApplicationSegment@autorun="false"`: wait for script, or never start?
    Any corpus examples?
52. `sync="hard"` vs `"soft"`: timeline-locked vs fire-and-forget? Effect on
    File Cache load vs video start.
53. `zOrder`: compositing rule with primary video (video always plane 0?).
54. `language` / `group` / `appBlock` on ApplicationSegment: selection
    algorithm when several apps overlap.
55. `ApplicationResource@priority`: load order / eviction. Any non-default
    in corpus?
56. `ApplicationResource@size`: bytes of the ACA/file, and must File Cache
    reject if on-disc size differs?
57. `multiplexed="false"` vs `"0"` vs `"1"`: sheet 03 documents XSD. Confirm
    `"0"` on PlaylistApplicationResource (12 rows) means File Cache from
    ADV_OBJ or slot 0.
58. GRINCH `multiplexed="1"`: ADV_PCK still not found in INTRO head. Where in
    the feature EVO is slot 1, and what is the pack payload layout
    (`loading_info_fname`, member bytes)? **Needs a deeper EVO range, not RE.**
59. ADV_PCK `0x80`: PES header vs payload vs ACA-like directory. Uncloseable
    until a small muxed clip is dumped. Demux rule (never AV decoder) is
    enough for linear play.
60. ACA formula `14+(flags&0xFF)+32` on the other **405** listed archives
    (only 4 saved). Fetch a few more (encrypted-flag vs STALINGRAD-style)
    before treating N=4 as corpus-wide.
61. ACA flags high byte `0x02`–`0x07` vs `0xff`: compression, encryption, or
    only CRC-valid? Encoding type is 1 on all four.
62. ACA 283-byte `AACS` sidecar: field breakdown (the u8 after magic, length
    echo). Needed only if a player must verify AACS of members; extract does
    not.
63. `0xff` member CRC: CRC of decrypted bytes? Of UTF-16? Skip forever for
    archival extract?
64. JS encoding: always UTF-16BE inside ACA? Any UTF-8 ACA member? BOM-less?
65. Manifest without `Markup`: script-only app (1408 extras). Does the engine
    still create a Region and run Script?
66. Manifest `Resource` duplicating `Script@src`: required preload vs noise?
67. `IPlaylist.load` argument: full `file:///dvddisc/ADV_OBJ/VPLST000.XPL`,
    bare `VPLST000.XPL`, or playlist number? Selector discs (MATRIX 099,
    BLADE_RUNNER 002, TRAINING_DAY 003) are the specimens — read their
    saved `.js` / markup for the call site. **No firmware.**
68. Soft reset vs full FIG.51: does `load` wipe File Cache and re-read
    DISCID, or only replace the playlist document?
69. HDi markup `clock="page"` vs title timeline: who is master when both
    ApplicationSegment `titleTimeBegin` and SMIL `begin` exist?
70. `cue` / `state:focused()`: minimum event set for a “Play movie” button
    (`click`, `focus`, remote OK). Typelib has 106 interfaces — which
    subset is required for the 3 selectors + a typical menu?
71. Fonts: TTF from ACA vs player-builtin. Any disc that will not render
    menus without a bundled TTF?
72. `.CER` (10 files, 811 or 1419 bytes): TLS trust for HDi network only?
    Fetch bodies (small) to see if they are standard X.509. Linear play
    ignores them.
73. Persistent storage directory grammar: `PROVIDER_ID` + `CONTENT_ID` path
    on the box. Binary PROVIDER_ID (24 discs) as filename?
74. `SEARCH_FLG=0` without persistent VPLST: fall through to disc (almost
    certainly). Confirm from patent wording, not firmware.
75. NetworkSource / `dataSource` other than `Disc` on
    PrimaryAudioVideoClip: XSD forbids; other clip types default
    `P-Storage`. Any saved XPL uses non-Disc dataSource?
76. `ScheduledControlList` / `Event@titleTime`: what API fires (`jump`,
    `pause`, app start)? Read a disc that uses it (sheet 03 says used).
77. `PlaylistApplication` vs in-title `ApplicationSegment`: both on screen?
    Language-matched PlaylistApplication for the whole playlist lifetime?

## K — AACS layout (format; no keys in-repo)

78. Licensed boot: must CHT verify before first decrypted pack? Book yes;
    this corpus cannot test (stripped packs). Document as book-only.
79. CHT #1 vs #2: hash unit size, stride, which EVOs they cover. Bodies not
    saved; listed sizes vary. Fetch headers only (first 64–128 bytes) if we
    want a table without storing megabytes.
80. `CONTENT_CERT` `BEE` (bus encryption): any disc has bit 7 set, and does
    a software player ignore bus encryption?
81. CPI `TITLE_KEY_PTR`: AACS table says bytes 1–2; BackupHDDVD uses
    `CPIField[2]`. Which does a pack with `KEY_VF=10b` actually use? Cannot
    test on stripped ISOs.
82. CPI at pack `0x3C` if NV_PCK **omits** the system header (`0xBB`)? All
    confirmed dumps have it. A different framing would move GCI.
83. VTKF without matching VPLST (BALLS_OF_FURY, CHUCK_AND_LARRY,
    SHREK_THE_THIRD_EU extra numbers): ignore, or used after `IPlaylist.load`?
84. VTKF 2516 / 65 slots vs book cap 64: player must size from
    `HD_VTKF_SIZE` (sheet 09). Any other size?
85. `AAC!` vs `ANY!`: mutually exclusive in corpus. If both appeared, probe
    order `ANY!` then `AAC!` then `AACS` — confirm book.
86. 16 discs with no AACS directory: all Category 2 unencrypted, or mix?
    Player must not require `MKBROM`.
87. Volume ID: MMC `READ DISC STRUCTURE` 80h after AACS auth — command
    bytes / timeout for a drive. ISO cannot answer. **Uncloseable from this
    corpus.**
88. VTUF `URS_NUM>0`: book Table 3-12 only. 217/217 files are 144 bytes.
    Implement the zero case; treat >0 as future.
89. DKF / persistent-storage directory key: needed for downloaded VPLST
    under `SEARCH_FLG=0`. Linear disc-only play can ignore.
90. AES-G and CBC IV are in sheet 09.11 for a **licensed** port. Research
    demux of Archive.org ISOs must not decrypt (already clear). Do not
    ship keys.

## U — Out of scope / uncloseable / later

91. Official MMC “this is HD DVD” probe: not in corpus. UDF 2.50 +
    `HVDVD_TS` is the working probe.
92. Category 3 (XPL + Standard VMG) and `HVSO@@@@.MAP`: 0/120. Do not
    invent a hybrid navigator.
93. `APLST###.XPL` audio-only: 0/120.
94. Firmware vs FIG.50: catalog is public; binaries are not in scope.
    OEM notes do not name VPLST. Flowchart stays patent + XPL.
95. PCI HLI / DSI `sml_pbi` / `vobu_sri` / `synci`: Advanced shall ignore
    HLI; DSI tail not needed if MAP seek works. Close only if trick-play
    needs it.
96. GCI `DCI` / `CCI` / `RECI` ISRC: copy-control display, not demux.
97. ParentalLevel enforcement: player policy vs disc field.
98. Region: HD DVD region codes vs CSS region — any disc field besides
    HDi script?
99. `Thumbs.db` / `*.log` in `HVDVD_TS`: ignore.
100. Standard Content (`RESERVOIR_DOGS`) VMG/PGC: out of scope for
     `spec/advanced/`.

---

## Suggested research order (no firmware)

**Done (2026-09-08):** corpus greps, selector `script.js` (`IPlaylist.load` URI),
ACA N=6, CHT/BEE book+one cert, TABLE 45–47. Answers:
[14_IMPLEMENTER_ANSWERS.md](14_IMPLEMENTER_ANSWERS.md). Experiment `e12`.

Still optional (not blocking linear play): more ACA to 409, feature-EVO
`streamNumber` pack census, ADV_PCK dump, `.CER` ASN.1, CHT body headers.

Linear MVP that does **not** need the rest: UDF 2.50 → DISCID → highest
VPLST with clips (or lower VPLST on 3 selectors as documented fallback) →
FirstPlayTitle or Title 1 → MAP walk (13-bit SZ) → 2048-byte packs →
decode using XPL `MediaAttributeList`.
