# Tackling ADV_OBJ (Advanced Content) — what it is and how to attack it


> **Provenance.** `[SRC: CORPUS | N=120 listings, N=247 XPL, N=2421 MAP, N=119 VTI]` + `[SRC: DISC | MATRIX_REVOLUTIONS /ADV_OBJ/selector.aca]` + `[SRC: PATENT | US20070091495A1]` + `[SRC: SRCCODE | spec/raw/adv_obj/v1.0/Playlist.xsd]`
> See `EVIDENCE_STANDARD.md` for the tag format.

Advanced Content is **119 of 120** discs examined. Unlike Standard Content it has
*no PGC, no Cell, no navigation commands* — so libdvdnav's VM is irrelevant here.
The good news: it is overwhelmingly **declarative and self-describing**, and far more
tractable than the "it's basically BD-J" framing suggests.

## Composition (census over the corpus)

| Ext | Count | What it is | Format |
|---|---|---|---|
| `.XPL` | 247 saved / 247 listed | Playlist — the navigation model | **XML, official XSD** |
| `.ACA` | 409 listed, 1 saved (`selector.aca`) | Application package archive | **header VERIFIED on disc; 408 unread** |
| `.MAP` | 2421 | Per-clip time map | binary, magic `HDDVD_TMAP00` |
| `.VTI` | 119 | Advanced VTS info | binary, magic `ADVANCED-VTS` |
| `.DAT` | 119 | `DISCID.DAT` only | `HDDVD-V_CONF`, 128 B |
| `.PNG/.TTF` | 57 | assets | standard |
| `.JS` | 3+ | ECMAScript (also inside ACA) | **UTF-16BE text** |
| `.XMF` | 3+ | HDi markup (also inside ACA) | XML |
| `.CER` | 8 | certificates | X.509 |

## 1. XPL playlists — already solved, essentially

**247 playlists parsed with 0 failures**, all under one namespace:
`http://www.dvdforum.org/2005/HDDVDVideo/Playlist`
(files even carry `schemaLocation=".../Playlist.xsd"` from the authoring machine).

Empirically derived element/attribute model, complete over the corpus:

```
Playlist[majorVersion,minorVersion,displayName,type]
  Configuration > StreamingBuffer[size], Aperture[size], MainVideoDefaultColor[color]
  MediaAttributeList > VideoAttributeItem[codec,index]
                       AudioAttributeItem[codec,index,channels]
                       SubpictureAttributeItem[codec,index]
  TitleSet[tickBase,timeBase,defaultLanguage]
    FirstPlayTitle[titleDuration,alternativeSDDisplayMode]
    Title[id,titleNumber,titleDuration,onEnd,selectable,outputFrameRate,...]
      PrimaryAudioVideoClip[src,titleTimeBegin,titleTimeEnd,clipTimeBegin,seamless,dataSource]
        Video[track,mediaAttr,angleNumber]  Audio[...]  Subtitle[...]
      ApplicationSegment[src,autorun,zOrder,sync,titleTimeBegin,titleTimeEnd,group]
        ApplicationResource[src,size,priority,multiplexed,loadingBegin]
      ChapterList > Chapter[id,displayName,titleTimeBegin]
      TrackNavigationList > VideoTrack / AudioTrack[langcode,selectable] /
                            SubtitleTrack[langcode,forced,selectable]
      ScheduledControlList > Event[id,titleTime]
```

**This is the whole title/clip/chapter/stream model.** Note `PrimaryAudioVideoClip@src`
points at a **`.MAP`**, not the EVO — the time map is the addressing layer.

## 2. `.MAP` — magic `HDDVD_TMAP00`

> **Correction.** The DVD `VTS_TMAPT` hypothesis below is **refuted**. Solved layout
> is `06_TMAP_solved.md`: `TMAP_GI` 128 B, `TMAPI_SRP` at byte 384, `EVOBU_ENT` at
> `TMAPI_SA` (byte offset, 416 when `Ns=1`).

12-byte ASCII identifier, same convention as the IFOs (`HVDVD-VMG100`,
`STANDARD-VTS`, `ADVANCED-VTS`). Since `VTS_TMAPT` in Standard Content turned out to be
DVD-Video's structure unchanged, an early working hypothesis was that the entry payload
here is the same TMAPI form. That was wrong — see `06_TMAP_solved.md`.

## 3. `.ACA` — cracked

Trivial archive. Verified on `selector.aca` (2008 B, 2 entries):

| Offset | Size | Field | Observed |
|---|---|---|---|
| 0x00 | 8 | magic | `HDDVDACA` |
| 0x08 | 2 | ? (16) | |
| 0x0A | 2 | version | 1 |
| 0x0C | 2 | **entry count** | 2 ✓ (`manifest.xmf`, `script.js`) |
| 0x0E | 4 | **total size** | 2008 = file length ✓ |
| 0x20 | — | entry table, **variable** `14+(flags&0xFF)+32` | not a 58-byte stride |

Entry: `offset` u32, `length` u32, hash/CRC u32, flags u16, then NUL-padded name.
First entry offset 428 — and `<?xml` begins at exactly 428 ✓.
Payload holds `manifest.xmf` (XML markup) and `script.js` (**UTF-16BE** ECMAScript).
The ACA is a mountable namespace: XPL and markup reference paths *through* it
(`file:///dvddisc/ADV_OBJ/selector.aca/script.js`).

An extractor is a short afternoon's work and unlocks all markup and script on every disc.

## Staged plan

### Stage 1 — playback without interactivity  (high value, low effort)
Parse XPL + `.MAP`, demux EVO. Yields **title enumeration, linear playback, chapter
seek, and audio/subtitle/angle selection on all 119 Advanced discs.** Needs no HDi,
no scripting, no AACS for the navigation layer. This is the 90% result.

### Stage 2 — ACA extraction  (low effort, enabling)
Implement the container above; recover `.xmf` markup, `.js`, fonts, images. Turns the
interactive layer from opaque blobs into inspectable source, and is prerequisite for
any later work.

### Stage 3 — HDi  (large effort, low marginal value)
`.xmf` markup + ECMAScript + the HDi DOM, timing and event model. This is effectively
a small browser engine. Menus and interactivity live here.

## Architectural recommendation

**Do not put this behind libdvdnav.** The XPL model has no PGC, no cells, no VM
registers, no navigation commands — nothing libdvdnav's state machine represents.
It is structurally much closer to **libbluray's MPLS playlist model**. The natural
shape is an HD DVD backend presenting a playlist API, with libdvdread (extended per
`03_libdvdread_requirements.md`) supplying UDF 2.50 access and EVO reading underneath.

Standard Content — the PGC/VM path — remains a separate, small, 1-disc-in-120 concern.

---

# Addendum: official schemas, DISCID, ACA player constraints, HDi

## Official `Playlist.xsd` — the derived model is a subset of a real schema

`[SRC: SRCCODE | spec/raw/adv_obj/v1.0/Playlist.xsd and v1.1/Playlist.xsd | DVD Forum / Sonic / Toshiba / Microsoft]`
**VERIFIED** — this closes the "is there an official XSD?" question in `07_ADVERSARIAL_REVIEW.md`.

- Namespace `http://www.dvdforum.org/2005/HDDVDVideo/Playlist` matches all 247 corpus
  files. Annotations cite **Spec. 6.2.3.14** element-by-element.
- v1.0 schema date 16 Jul 2006; v1.1 date 5 Nov 2007 (build 595).
- All 247 saved playlists are `majorVersion="1" minorVersion="0"`.
  `[SRC: CORPUS | N=247 XPL]` Retail discs are the 1.0 language. v1.1 adds
  `outputFrameRate`, `sourcePictureProgressiveMode`, extra codecs (`HEAACV2`, `MP3`,
  `WMAPRO`, `HEAAC`, `MPEG-1`), and switches `ISO639-2` → `ISO639-1`.
- 0 parse failures. Every element in the corpus is in the XSD; the XSD has five
  elements **never used** in this corpus: `SecondaryAudioVideoClip`,
  `SubstituteAudioVideoClip`, `SubstituteAudioClip`, `AdvancedSubtitleSegment`,
  `NetworkSource` (network / PiP / substitute-audio path).
- Caps in the schema, not visible from discs alone: 999 `Title`, 299 clips per title,
  1999 `Chapter`, 9 video / 8 audio / 32 subtitle tracks, 1–299 playlist applications.
- `TimeExpressionType` is `HH:MM:SS:FF` with the frame field `00–59` regardless of
  `tickBase`. `timeBase` is `50fps|60fps` (corpus: **60fps on 247/247**). `tickBase`
  is `24fps|50fps|60fps` (corpus: 148×`60fps`, 29×`24fps` among TitleSets that set it).
- Codecs actually used: video MPEG-2 (269) / VC-1 (251) / AVC (124); audio DD+ (344),
  DTS-HD (85), MLP (71), AC-3 (21), LPCM (11); subpicture **only** `8bitRLC` (302)
  — `2bitRLC` is in the XSD, unseen.
- `@src` by element (do not lump them): `PrimaryAudioVideoClip` → `.MAP` 4847;
  `ApplicationSegment` → `.XMF` 2529; `ApplicationResource` → ACA 2354 / PNG / …;
  `PlaylistApplication` → `.XMF` (203 files). An earlier mix of every `@src` in the
  file wrongly looked like clips pointing at ACA. `[SRC: CORPUS | e07]`

`schemaLocation` is leftover authoring debris: DVD Forum URL (138), missing (77),
`file:/X:/RND/current_schemas/Playlist.xsd` (10), Oxygen editor path (3). Not a
runtime requirement.

Sister schemas in the same drop: `Manifest.xsd` (Application / Region / Script /
Markup / Resource — Spec. 6.2.4.2), `iHD.xsd` + `iHDstate.xsd` + `iHDstyle.xsd`
(HDi markup, namespace `http://www.dvdforum.org/2005/ihd`, Spec. 7.5.3.1). Markup
root element is `root`; `object@type` enumerates `image/jpeg|png|cvi|cdw|mng`,
`audio/x-wav`, `application/x-clearrect|x-graphic`. Scripting surface extracted from
Scenarist `IHDScriptingTLB`: 106 typeinfos / 954 names; `IApplication` exposes
`FileIO`, `Network`, `document`, title/application timers (`spec/raw/adv_obj/iHD_Scripting_API.txt`).

## `DISCID.DAT`

Layout in `03_libdvdread_requirements.md` §8. Player string
`file:///dvddisc/ADV_OBJ/DISCID.DAT`. After Category 2/3 detection the Playlist
Manager reads it **before** choosing a playlist; the chosen file is the
`VPLST$$$.XPL` with the **highest** number on the disc (and, if `SEARCH_FLG=0`,
also under persistent storage).
`[SRC: PATENT | US20070091495A1 DISCID.DAT playback sequence]`

## `.ACA` — player-enforced header (still one-sample on disc)

`[SRC: SRCCODE | HDDVDPLAYDLL strings in spec/raw/adv_obj/ACA_and_AdvancedStream_evidence.txt]`
The reference decoder rejects: magic not `HDDVDACA`; version not 1.0; file type not 0;
encoding type not 1; size less than header; CRC mismatch. That maps onto the cracked
header: `VERN`-style `0x0010` at 0x08 is the same 1.0 encoding used everywhere else;
encoding-type=1 is the constant 1 at 0x0A. CRC is the previously unnamed u32 per
entry. Compression is still **OPEN** (encoding type 1 may mean "none").

**Scale validation still not run:** `udfgrab.py` default `--ext` does not include
`.ACA`, so 0 of 409 listed archives are on disk. Fetch them before treating the
58-byte stride as VERIFIED.

**Update (four saved ACAs):** the 58-byte stride is **refuted**. Record size is
`14 + (flags & 0xFF) + 32`. See `spec/advanced/04_aca.md` and
`experiments/e11_aca_vti_tails.py`.

## ADV_PCK vs NV_PCK substream `0x04`

Patents: Advanced stream packs are `private_stream_2` with **`sub_stream_id = 0x80`**,
not `0x04`. Private data: `PES_scrambling_control`, `adv_pkt_status`,
`loading_info_fname`. `[SRC: PATENT | US20070091495A1 / US20080298219A1 TABLE 85]`
NV_PCK's third packet (`0x04`) is therefore **not** ADV_PCK. TABLE 85 names NV_PCK
contents as **GCI + DSI**; `0x04` is the candidate for GCI. The AACS HD DVD book
puts a 16-byte CPI field in that GCI_PKT (`TITLE_KEY_PTR`). See
`08_NV_PCK_PCI_DSI.md` and `09_AACS.md`.
