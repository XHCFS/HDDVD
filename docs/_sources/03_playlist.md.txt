# 3. Playlist: VPLST$$$.XPL

*Counts written "N/120", "N/119", "on N discs", "listings", or as named discs are over the reference corpus of 120 archived retail HD DVD images [11]. `eNN` are the reproducible verification experiments [12].*

The playlist is the disc's table of contents and its schedule. It says which
titles exist, which video clips play on each title's timeline and when, which
audio and subtitle streams become which user-visible tracks, which HDi
applications run (and which files they need loaded first), where the chapters
are, and where playback pauses or fires events. There is no PGC and no binary
navigation table on Advanced Content: this XML file **is** the navigation model.

This sheet documents every element and attribute the schema allows, in document
order. Each element section gives its content model, then one table of
attributes (type, required, default, what it is for), then the rules that
connect it to other elements, then what the discs carry.

Sources: the DVD Forum schemas [5] (v1.0, 16 Jul 2006, and v1.1, 5 Nov 2007);
the specification text quoted in US 2007/0091495 [1] (every "Describes …"
attribute definition below comes from there); the Scenarist AC 4.5 User Guide
[7]; and the corpus, checked by `e26` (all 247 playlists) together with the
earlier `e12` / `e14`.

## 3.1 File, versions, schema

| | |
|---|---|
| Path | `ADV_OBJ/VPLST$$$.XPL`, `$$$` = `000`…`999` (see §3.20 for which one plays) |
| Namespace | `http://www.dvdforum.org/2005/HDDVDVideo/Playlist` |
| Root element | `Playlist` (one per file) |
| Encoding | UTF-8 XML |
| Schema | `spec/raw/adv_obj/v1.1/Playlist.xsd` (use this one); `v1.0/Playlist.xsd` for reference |

**Two schema versions.** Every playlist in the corpus declares
`majorVersion="1" minorVersion="0"`, but all 247 validate against the **v1.1**
schema and 33 of them fail v1.0 (`e26`). The failures are exactly the v1.1
additions, so discs were authored with the 1.1 tools. Read against v1.1. The
differences:

| v1.1 change | Effect |
|---|---|
| `Title@outputFrameRate`, `FirstPlayTitle@outputFrameRate` added | 182 Titles and 3 FirstPlayTitles carry it (§3.8) |
| `VideoAttributeItem@sourcePictureProgressiveMode` added | 0 on disc (§3.6) |
| `AudioAttributeItem@codec` gains `HEAACV2`, `MP3`, `WMAPRO`, `HEAAC` | 0 on disc |
| A `Title` may have no presentation clip (`choice minOccurs="0"`) | `MATRIX_REVOLUTIONS` `VPLST099` has a clip-less title |
| `FirstPlayTitle` needs at least one clip; clips need at least one `Video` | (v1.0 allowed none) |
| Language type renamed `ISO639-2` → `ISO639-1` | same two-letter values |

**Reading rules.**

- Match elements and attributes by namespace and local name, never by prefix.
- Ignore XML comments (discs put them inside lists) and `xsi:schemaLocation`
  (170 roots carry one; the URLs are dead authoring debris).
- Apply the defaults in the tables below when an optional attribute is absent;
  the defaults are part of the meaning.
- Keep URIs exactly as written (§3.2, §3.19).

## 3.2 Data types

| Type | Syntax | Meaning |
|---|---|---|
| time expression | `HH:MM:SS:FF`; HH `00`–`23`, MM and SS `00`–`59`, FF `00`–`49` at 50 fps or `00`–`59` at 60 fps | A **non-drop frame count** on a title timeline: `(3600·HH + 60·MM + SS) · rate + FF`, where `rate` is `TitleSet@timeBase`. `00:00:01:00` at 60 fps is 60 counts, not one second of 29.97 video. FF ≥ 50 appears 3590 times on 60 fps titles (`e14`): do not clamp to 49. |
| frame rate | `50fps` \| `60fps` | Rate of the title timeline (the media clock) |
| tick rate | `24fps` \| `50fps` \| `60fps` | Rate of the application tick clock (page and application clocks). Must be `50fps` or `24fps` when the frame rate is 50, `60fps` or `24fps` when it is 60 |
| language | two lowercase letters, ISO 639-1 (`en`, `fr`, `ja`, …) | A menu / application language. The v1.0 type is *named* `ISO639-2` but its values are two-letter codes; match two letters |
| langCode | `xx:NN` or `*:NN`; `xx` ISO 639-1, `NN` two hex digits | Track language plus **code extension** (what kind of track in that language). `*` = language not specified. Table below |
| parentalList | space-separated `CC:n` or `*:n`; `CC` ISO 3166 alpha-2 country, `n` `1`–`8` | Minimum parental level needed to play, per country. `*` = every country not listed. Each country (and `*`) at most once |
| multiplexed | `false` or a non-negative integer | How a resource reaches the File Cache (§3.14) |
| URI | `anyURI`, at most 1024 bytes | `file:///dvddisc/…` (the disc), `file:///filecache/…` (File Cache), `file:///fixed/…` and `file:///removable/…` (persistent storage), `http://…` / `https://…` (network). An ACA member is addressed as `…/name.aca/member` |
| boolean | `true` \| `false` | |
| ID / IDREF | XML name | `id` values are unique in the document; `onEnd` refers to one |

**Language code extension** (`NN` in langCode). The table is the
specification's Annex B, which is not among the available sources. The one
value the sources quote, **`09` = Forced Caption** for sub-pictures [2], matches
DVD-Video's code-extension numbering, and the values on disc fit that numbering:

| NN | Audio | Subtitle | On disc (audio / subtitle tracks) |
|---|---|---|---|
| `00` | not specified | not specified | 866 / 606 |
| `01` | normal | normal | 2336 / 9305 |
| `02` | for the visually impaired | large characters | 23 / 23 |
| `03` | director's comments | for children | 210 / 271 |
| `04` | alternate director's comments | | 14 / 0 |
| `05` | | normal captions | 1 / 601 |
| `09` | | **forced** caption | 0 / 97 |
| `0D` | | director's comments | 0 / 356 |

`[2, 11, 12]` **INFERRED** (DVD parity; `09` quoted).

## 3.3 Document tree

`?` = optional, `*` = any number, `+` = at least one. Children appear in exactly
this order.

```
Playlist                                  §3.4
├── Configuration                         §3.5
│   ├── StreamingBuffer
│   ├── Aperture
│   ├── MainVideoDefaultColor
│   └── NetworkTimeout?
├── MediaAttributeList?                   §3.6
│   ├── VideoAttributeItem*
│   ├── AudioAttributeItem*
│   └── SubpictureAttributeItem*
└── TitleSet                              §3.7
    ├── FirstPlayTitle?                   §3.9
    │   └── (PrimaryAudioVideoClip | SubstituteAudioVideoClip)+
    ├── Title  (1–999)                    §3.8
    │   ├── (PrimaryAudioVideoClip        §3.10  ┐
    │   │   | SecondaryAudioVideoClip     §3.10  │
    │   │   | SubstituteAudioVideoClip    §3.10  │ 0–299, any order
    │   │   | SubstituteAudioClip         §3.10  │ (the object mapping)
    │   │   | AdvancedSubtitleSegment     §3.13  │
    │   │   | ApplicationSegment)         §3.13  ┘
    │   ├── TitleResource*                §3.14
    │   ├── ScheduledControlList?         §3.18
    │   ├── ChapterList?                  §3.16
    │   └── TrackNavigationList?          §3.17
    └── PlaylistApplication*              §3.15
        └── PlaylistApplicationResource*  §3.14
```

Inside the clips and segments:

```
PrimaryAudioVideoClip     Video+ Audio* Subtitle* SubVideo? SubAudio*     §3.12
SecondaryAudioVideoClip   NetworkSource* SubVideo? SubAudio*               §3.11 §3.12
SubstituteAudioVideoClip  NetworkSource* Video Audio*                      §3.11 §3.12
SubstituteAudioClip       NetworkSource* Audio+                            §3.11 §3.12
AdvancedSubtitleSegment   Subtitle+ ApplicationResource*                   §3.12 §3.14
ApplicationSegment        ApplicationResource*                             §3.14
ApplicationResource       NetworkSource*                                   §3.11
TitleResource             NetworkSource*                                   §3.11
```

The XSD builds several elements from shared base types; each attribute below
is listed once per element with the base type named:

| Base type | Attributes | Used by |
|---|---|---|
| `ClipMappingType` | `titleTimeBegin`, `titleTimeEnd`, `clipTimeBegin`, `src`, `id`, `description` | the four `…Clip` elements |
| `ObjectMappingType` | `titleTimeBegin`, `titleTimeEnd`, `src`, `id`, `description` | `ApplicationSegment`, `AdvancedSubtitleSegment` |
| `ResourceType` | `src`, `size`, `priority`, `multiplexed`, `loadingBegin`, `noCache`, `description` | `ApplicationResource`, `TitleResource` |
| `TrackNumberAssignmentType` | `mediaAttr`, `description` | `Video`, `Audio`, `Subtitle`, `SubVideo`, `SubAudio` |
| `TrackNavigationType` | `selectable`, `description` | `VideoTrack`, `AudioTrack`, `SubtitleTrack` |

## 3.4 Playlist

The root. One per file.

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `majorVersion` | non-negative integer | yes | | Integer part of the Advanced Content version (`1`) |
| `minorVersion` | non-negative integer | yes | | Fractional part (`0`; see §3.1) |
| `type` | `Advanced` \| `Interoperable` | no | `Advanced` | `Interoperable` marks content recorded in the user-recordable HD DVD video format rather than authored Advanced Content |
| `displayName` | string | no | | Human-readable name |
| `description` | string | no | | Free text |

On disc: `1`/`0` on 247/247; `type="Advanced"` on 79, absent on the rest;
`displayName` on 96 (often `Dummy`).

## 3.5 Configuration

System settings the player applies before any title starts. Children, in order:

| Element | Occurs | Attribute | Type | Req. | What it is for |
|---|---|---|---|---|---|
| `StreamingBuffer` | 1 | `size` | even integer | yes | Size of the Streaming Buffer carved out of the Data Cache, **in 2048-byte packs** (`1024` = 2 MB). It holds network-streamed secondary video. `0` = none. The File Cache gets what remains |
| `Aperture` | 1 | `size` | `1920x1080` \| `1280x720` | yes | Full visible image size: the size of the graphics plane that applications draw on |
| `MainVideoDefaultColor` | 1 | `color` | six hex digits `YYCrCb` | yes | Colour of the main-video plane outside the (scaled) main video. Y 16–235, Cr and Cb 16–240 |
| `NetworkTimeout` | 0–1 | `timeout` | non-negative integer | yes | Network request timeout, in milliseconds |

The Data Cache is at least 64 MB; the Streaming Buffer comes out of it, and
applications' resources must fit in the rest (§3.14).

On disc: `StreamingBuffer` `0` on 246, `1024` on 1; `Aperture` `1920x1080` on
247/247; `MainVideoDefaultColor` `108080` (112) or `107F7F` (135), both black;
`NetworkTimeout` on 14 playlists, all `0` (the meaning of 0 is not defined in
the sources).

## 3.6 MediaAttributeList

Codec and format of the elementary streams the clips use, indexed so that track
elements can point at them (`@mediaAttr`, §3.12). Children, in order: any number
of `VideoAttributeItem`, then `AudioAttributeItem`, then
`SubpictureAttributeItem`. `index` is unique per item type (a video item and an
audio item can both be `1`). Values should match the stream attributes in the
VTI; in practice the **playlist is the source of the codec** because the VTI
`V_ATR` codec field is unreliable ([06](06_vti.md)).

**`VideoAttributeItem`** (main and sub video):

| Attribute | Type | Req. | What it is for |
|---|---|---|---|
| `index` | positive integer | yes | Number that `Video@mediaAttr` / `SubVideo@mediaAttr` refer to |
| `codec` | `MPEG-2` \| `VC-1` \| `AVC` \| `MPEG-1` | yes | Video codec. `MPEG-1` only in Interoperable content |
| `sampleAspectRatio` | `16:9` \| `4:3` | no | Shape of the encoded samples ("pixels") |
| `horizontalResolution` | positive integer | no | Encoded samples per line (not the displayed pixel count) |
| `verticalResolution` | positive integer | no | Encoded lines |
| `encodedFrameRate` | positive integer | no | Encoded frame rate, in frames (30 interlaced frames, not 60 fields) |
| `sourceFrameRate` | positive integer | no | Approximate frame rate of the source: `24` for film even when it is 23.976 and encoded with repeat-field flags at 29.97 |
| `bitrate` | positive integer | no | Approximate average bit rate, kbit/s, for choosing between streams by bandwidth |
| `activeAreaX1`, `activeAreaY1`, `activeAreaX2`, `activeAreaY2` | non-negative integer | no | The active image rectangle, in full-screen coordinates, when a solid colour fills the rest of the encoded frame |
| `sourcePictureProgressiveMode` (v1.1) | `Progressive` \| `Interlaced` \| `Unspecified` | no | Whether the source pictures are progressive |

**`AudioAttributeItem`** (main and sub audio):

| Attribute | Type | Req. | What it is for |
|---|---|---|---|
| `index` | positive integer | yes | Number that `Audio@mediaAttr` / `SubAudio@mediaAttr` refer to |
| `codec` | `LPCM` \| `DD+` \| `DTS-HD` \| `MLP` \| `MPEG` \| `AC-3`; v1.1 adds `HEAACV2`, `MP3`, `WMAPRO`, `HEAAC` | yes | Audio codec. The v1.1 schema notes: `AC-3` and `HEAAC` only in Interoperable content; `LPCM`, `MLP`, `MPEG` only for main audio; `HEAACV2`, `MP3`, `WMAPRO` optional, sub audio only |
| `sampleRate` | positive integer | no | Sampling rate, **kHz** |
| `sampleDepth` | positive integer | no | Bits per sample |
| `channels` | positive integer | no | Channel count; the ".1" counts as one (5.1 → `6`) |
| `bitrate` | positive integer | no | Bit rate, kbit/s |

**`SubpictureAttributeItem`**:

| Attribute | Type | Req. | What it is for |
|---|---|---|---|
| `index` | positive integer | yes | Number that `Subtitle@mediaAttr` refers to |
| `codec` | `2bitRLC` \| `8bitRLC` | yes | Sub-picture coding: 2 or 8 bits per pixel ([08](08_evo.md) §8.8) |

On disc: the list is present in 244 playlists. Only `index` and `codec` are used,
plus `channels` on 107 audio items (`6`, `2`, `1`, `8`). Video codecs: `MPEG-2`
269, `VC-1` 251, `AVC` 124. Audio: `DD+` 344, `DTS-HD` 85, `MLP` 71, `AC-3` 21
(despite the Interoperable-only note), `LPCM` 11. Sub-picture: `8bitRLC` 302/302.

## 3.7 TitleSet

The set of titles, in order: an optional `FirstPlayTitle`, then 1–999 `Title`,
then any number of `PlaylistApplication`.

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `timeBase` | frame rate | yes | | Rate of every title timeline; every time expression in the playlist counts at this rate |
| `tickBase` | tick rate | no | same as `timeBase` | Rate of the application tick clock used by markup (page and application clocks). Independent of the media clock, so menus animate at normal speed while video is paused or fast-forwarded |
| `defaultLanguage` | language | no | | Fallback menu language: when a title has no `ApplicationSegment` whose `language` matches the player's menu language, the one with this language is activated (§3.13) |

On disc: `timeBase="60fps"` 247/247; `tickBase` `60fps` 148, `24fps` 29, absent
70; `defaultLanguage` `en` 190, `de` 31, `ja` 23, `fr` 3.

## 3.8 Title

One title: a timeline (the **title timeline**) of length `titleDuration`, the
objects mapped onto it, the resources they need, and its chapters, tracks and
scheduled controls. Titles are **numbered by document order from 1**.

Children, in order: 0–299 presentation clips and segments in any mix (the
**object mapping**, §3.10 and §3.13), then `TitleResource*` (§3.14),
`ScheduledControlList?` (§3.18), `ChapterList?` (§3.16),
`TrackNavigationList?` (§3.17).

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `titleNumber` | positive integer | yes | | The title's number. Must equal its position among the `Title` elements (1, 2, …) |
| `id` | ID | no | | Name used by `onEnd` and by script |
| `type` | `Advanced` \| `Original` \| `UserDefined` | no | `Advanced` | `Original` / `UserDefined`: original or user-edited title of Interoperable (recorded) content |
| `selectable` | boolean | no | `true` | `false`: the user cannot navigate to this title (title menu, title search, next/previous title); script still can |
| `titleDuration` | time expression | yes | | Length of the title timeline. Every mapped object ends at or before it |
| `onEnd` | IDREF | no | | `id` of the title to play when this one ends. **Absent: stop** after the title (script may still continue) |
| `tickBaseDivisor` | positive integer | no | `1` | Reduces the application tick rate for this title: with `3`, the Advanced Application Manager processes one tick in three and ignores the rest |
| `parentalLevel` | parentalList | no | `*:1` | Minimum parental level to play the title, per country |
| `alternativeSDDisplayMode` | `panscanOrLetterbox` \| `panscan` \| `letterbox` | no | `panscanOrLetterbox` | Display modes allowed when outputting to a 4:3 monitor; the player must use an allowed one |
| `displayName` | string | no | | Title name a player may show |
| `description` | string | no | | Free text |
| `xml:base` | URI | no | | Base URI for relative URIs inside this title (XML Base) |
| `outputFrameRate` (v1.1) | `24p` \| `Other` \| `Unspecified` | no | `Unspecified` | Declares whether the title is 24-frame content, so a player can choose 24 Hz output. Meaning beyond the value names is not in the sources |

**Rules.**

- Presentation objects on one title timeline must not overlap within a kind:
  no two `PrimaryAudioVideoClip`, no two `SecondaryAudioVideoClip`, no two
  `SubstituteAudioClip`, no two `SubstituteAudioVideoClip`, and a
  `PrimaryAudioVideoClip` must not overlap a `SubstituteAudioVideoClip`.
  There is one main-video decoder and one sub-video decoder.
- Where no clip is mapped, the timeline still runs and the main-video plane shows
  `MainVideoDefaultColor`.
- `titleDuration` is authoritative. On disc (`e14`, titles with clips): last
  clip end equals `titleDuration` 3237 times, is shorter 70 times (the tail
  shows the default colour), and longer once (`THE_SEARCHERS` FirstPlayTitle,
  `00:00:23:55` vs `00:00:23:00`: authoring error; stop at `titleDuration`).
- `onEnd` omitted means stop; it is not a loop and not a hidden menu.

On disc (3196 titles): `titleNumber` equals document order 3196/3196; `onEnd`
on 3192, all resolving to a title `id`; `selectable` only ever `true` (265);
`tickBaseDivisor` `4` 399, `1` 303, `3` 36, `2` 33; `alternativeSDDisplayMode`
`letterbox` 2226; `outputFrameRate` `Other` 116, `24p` 66; `type` only
`Advanced` (183).

`[1, 5, 11, 12]` **VERIFIED**

## 3.9 FirstPlayTitle

A title played once, before Title 1, when the playlist starts: logos, warnings.
It has no number and cannot be navigated to.

Children: `PrimaryAudioVideoClip` and `SubstituteAudioVideoClip`, any order
(v1.1: at least one). Only video track 1 and audio track 1 may be assigned;
no subtitle, sub-video or sub-audio.

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `titleDuration` | time expression | yes | | Length of its timeline; every object ends before it |
| `alternativeSDDisplayMode` | as `Title` | no | `panscanOrLetterbox` | As `Title` |
| `xml:base` | URI | no | | As `Title` |
| `outputFrameRate` (v1.1) | as `Title` | no | `Unspecified` | As `Title` |

Playback rules [1]: play it start to end at normal speed, video track 1 and audio
track 1; ignore user title navigation (next, previous, fast-forward, rewind, time
search, `jump`) until it ends; then play Title 1. `PlaylistApplication` is not
active during it. If a File Cache resource is missing, keep playing the video and
skip the resource. `[1]` **INFERRED** (fail-closed; skip key not demonstrated).

On disc: 119 of 247 playlists; `alternativeSDDisplayMode` `letterbox` 90.

## 3.10 Presentation clips

A clip maps a stretch of a video object onto the title timeline. All four clip
elements share `ClipMappingType`:

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `src` | URI | yes | | The object's **index file**, the time map (`.MAP`, [07](07_map.md)), not the `.EVO` (§3.19) |
| `titleTimeBegin` | time expression | yes | | Where the clip starts on the title timeline |
| `titleTimeEnd` | time expression | yes | | Where it ends; **exclusive** (`[begin, end)`) |
| `clipTimeBegin` | time expression | no | `00:00:00:00` | Where playback starts **inside** the object, on the object's own clock. Must be the PTS of a coded video frame |
| `id` | ID | no | | Name for script |
| `description` | string | no | | Free text |

**Time model.** At title time `t` in `[titleTimeBegin, titleTimeEnd)` the clip
shows object time `clipTimeBegin + (t − titleTimeBegin)`. The span must fit in
the object: `clipTimeBegin + titleTimeEnd − titleTimeBegin` ≤ the object's
length. The object time converts to a disc address through the time map.

The four clip elements:

| Element | Plays | Object | Children | `dataSource` (default) | `sync` (default) |
|---|---|---|---|---|---|
| `PrimaryAudioVideoClip` | main video, main audio, sub-pictures, and the P-EVOB's sub video / sub audio | P-EVOB, or an interleaved block of P-EVOBs (angles) | `Video+ Audio* Subtitle* SubVideo? SubAudio*` | `Disc` only (`Disc`) | always synchronised |
| `SecondaryAudioVideoClip` | sub video and/or sub audio (picture-in-picture, commentary) | S-EVOB of the Secondary Video Set | `NetworkSource* SubVideo? SubAudio*` | any (`P-Storage`) | `hard` \| `soft` \| `none` (`soft`) |
| `SubstituteAudioVideoClip` | main video and main audio, replacing the primary clip | S-EVOB | `NetworkSource* Video Audio*` | any (`P-Storage`) | `hard` \| `none` (`hard`) |
| `SubstituteAudioClip` | main audio, replacing the primary audio | S-EVOB | `NetworkSource* Audio+` | any (`P-Storage`) | `hard` \| `soft` (`soft`) |

Extra attributes:

| Attribute | On | Type | Req. | Default | What it is for |
|---|---|---|---|---|---|
| `dataSource` | all four | `Disc` \| `P-Storage` \| `Network` \| `FileCache` | no | see table | Where the object lives: the disc, persistent storage (pre-downloaded), streamed from a server, or already in the File Cache. `PrimaryAudioVideoClip` allows only `Disc` |
| `seamless` | `PrimaryAudioVideoClip` | boolean | no | `false` | `true`: this clip and the one mapped directly before it meet the seamless-connection conditions, so the decoder must not break between them |
| `sync` | the three secondary / substitute clips | `hard` \| `soft` \| `none` | no | see table | What happens if the object is not ready at `titleTimeBegin`. **hard**: the title timeline stops until it is. **soft**: the timeline keeps running and the object starts late. **none**: the object is not synchronised to the timeline |
| `preload` | the three | time expression | no | | Title time at which the player should start prefetching the object |
| `noCache` | the three | boolean | no | `false` | Only with `dataSource="Network"` (otherwise absent): `true` adds `no-cache` to both `Cache-Control` and `Pragma` in the HTTP request; `false` adds it to neither |

Streaming (`Network`) objects go through the Streaming Buffer (§3.5);
`P-Storage`, `FileCache` and some `Disc` objects are read from the Data Cache so
the disc head is not shared with the primary clip.

On disc: only `PrimaryAudioVideoClip` (4847; the other three 0). Every `src` is
a `.MAP` whose `.EVO` has an EVOBI in the VTI (4847/4847). `seamless` on 1379:
`true` 614, and all 614 start exactly at the previous clip's `titleTimeEnd`.
`clipTimeBegin` on 558 (`00:00:00:00` 425). Clip end-to-start abutting pairs
1527, overlaps 0 (`e14`). `dataSource="Disc"` written on 3933.

`[1, 5, 11, 12]` **VERIFIED** (disc-side); network and substitute clips
specified only.

## 3.11 NetworkSource

Alternative network locations for one object or resource, chosen by the
player's network throughput.

| Attribute | Type | Req. | What it is for |
|---|---|---|---|
| `src` | URI (`http`/`https`) | yes | In a clip: the time map of the alternative stream. In a resource: the alternative archive or file |
| `networkThroughput` | non-negative integer | yes | Minimum network throughput needed to use this source, in **1000 bit/s** units. Unique within the parent |

Allowed in a clip only when its `dataSource="Network"` and its `src` is
`http`/`https`; in `ApplicationResource` / `TitleResource` only when their `src`
is `http`/`https`.

Selection, done once while the title timeline is being set up: take the
`NetworkSource` entries whose `networkThroughput` ≤ the player's Network
Throughput parameter. If exactly one qualifies, use it; if several, use the one
with the largest `networkThroughput`; if none, use the parent's own `src`. For
resources, the file is still **referred to** by the parent's `src` URI whichever
source it was fetched from.

On disc: 0.

## 3.12 Track number assignment

Inside a clip, these elements say which elementary streams exist and which
**track number** each becomes. Track numbers are what the user and script select
(`TrackNavigationList`, §3.17); stream numbers are what the demuxer filters on
([08](08_evo.md) §8.7). All share `TrackNumberAssignmentType`:

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `mediaAttr` | positive integer | no | `1` | `index` of the matching item in `MediaAttributeList` (§3.6): `VideoAttributeItem` for `Video` / `SubVideo`, `AudioAttributeItem` for `Audio` / `SubAudio`, `SubpictureAttributeItem` for `Subtitle` |
| `description` | string | no | | Free text (`English 5.1`, `Director's Commentary`) |

| Element | `track` | Stream attribute | Maps to |
|---|---|---|---|
| `Video` | 1–9 | `angleNumber` 1–9, default `1` | Main video (VM_PCK). `angleNumber` is used only when the clip's `src` is an **interleaved block**: it picks which P-EVOB of the block (which angle) this track is. Otherwise omit it; main video is track 1 |
| `Audio` | 1–8 | `streamNumber` 1–8, default `1` | Main audio (AM_PCK). `streamNumber` = audio stream number **+ 1**: the low 3 bits of `sub_stream_id` for LPCM / DD+ / DTS-HD / MLP, of `stream_id` for MPEG audio |
| `Subtitle` | 1–32 | `streamNumber` 1–32, default `1` | Sub-picture (SP_PCK). `streamNumber` = sub-picture stream number **+ 1**; the stream number converts to the decoding stream through the VTI `SP_ATR` table, whose entry gives the `sub_stream_id` ([06](06_vti.md)). In `AdvancedSubtitleSegment`: `streamNumber` omitted, `mediaAttr` ignored |
| `SubVideo` | fixed `1` | | Sub video (VS_PCK) of the P-EVOB, or of the S-EVOB in a secondary clip. Present = enabled |
| `SubAudio` | 1–8 | `streamNumber` 1–8, default `1` | Sub audio (AS_PCK); `streamNumber` = audio stream number + 1 |

Only streams listed here are available in that clip. The assignment can change
from clip to clip, so a track number means "whatever stream the current clip
maps to it".

On disc: `Video` 4869, `track` 1 on 4847 (the rest are Pan's Labyrinth angles
2–4 with `angleNumber` 2–4); `Audio` 6399; `Subtitle` 19992; `SubVideo` 84;
`SubAudio` 38. Every `Audio@streamNumber` and `Subtitle@streamNumber` is within
the stream count of the EVOB's VTI record (`AST_Ns`, `SP_Ns`). Every `mediaAttr`
names an existing item **except** two authoring errors: `DOWNFALL` `VPLST000`
(`Subtitle@mediaAttr` 3–18, only items 1–2 exist) and `U2_RATTLE_AND_HUM`
`VPLST000` (subtitles with no `SubpictureAttributeItem`). A reader should fall
back to the one sub-picture codec Advanced Content uses, `8bitRLC`.

`[1, 5, 11, 12]` **VERIFIED**

## 3.13 ApplicationSegment and AdvancedSubtitleSegment

A segment maps an HDi application (or an Advanced Subtitle) onto the title
timeline. Both share `ObjectMappingType`:

| Attribute | Type | Req. | What it is for |
|---|---|---|---|
| `src` | URI | yes | The application's **manifest** (`.xmf`, [05](05_manifest_hdi.md) §5.1), usually inside an ACA |
| `titleTimeBegin` | time expression | yes | Start of the **valid period** |
| `titleTimeEnd` | time expression | yes | End of the valid period (exclusive) |
| `id` | ID | no | Name for script |
| `description` | string | no | Free text |

**`ApplicationSegment`** (children: `ApplicationResource*`, §3.14):

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `sync` | `hard` \| `soft` | no | `hard` | Start-up mode. **hard**: the title timeline holds until the resources are loaded and the application has started. **soft**: the timeline keeps running; the application appears late, or not at all if its window passes |
| `zOrder` | non-negative integer | yes | | Stacking order of this application on the graphics plane relative to other applications |
| `language` | language | no | | The application's language. Absent: any language |
| `appBlock` | positive integer | no | | Application Block this segment belongs to (see below) |
| `group` | positive integer | no | | Application Group this segment belongs to (see below) |
| `autorun` | boolean | no | `true` | `true`: becomes active when the timeline enters the valid period. `false`: stays inactive until script activates it |

`language`, `appBlock`, `group` and `autorun` are the **Application Activation
Information**: they decide whether the application runs in its valid period.

- **Application Block**: the segments of one title with the same `appBlock`
  value, the same application in different languages. Only the one whose
  `language` matches the player's menu language is activated; if none matches,
  the one matching `TitleSet@defaultLanguage`. In a block: every segment has a
  `language`, languages are unique, valid periods are identical, `autorun` is
  identical, and `group` is absent. A segment with `language` must have `appBlock`
  (a block of one is allowed).
- **Application Group**: segments with the same `group` value that script
  activates and deactivates together (for example a row of buttons).
- **Decision** (per segment, when the timeline enters its valid period; patent
  FIG.58 [1]):
  1. `autorun="false"` → inactive. Script may activate it later.
  2. Else, if `group` is present → active only while that group is the selected
     (valid) group. Script can change which group is selected.
  3. Else, if `appBlock` and `language` are present → active if `language`
     equals the player's menu language; if no segment of the block matches the
     menu language, the one whose `language` equals `TitleSet@defaultLanguage`
     is active; the others are inactive.
  4. Else (no activation information) → **active**. The patent's prose for this
     branch says "invalid", which contradicts its own resource rule ("loads the
     Resource … if these Application Segments do not have any Application
     Activation Information") and every disc: 2275 segments with no activation
     information (or only `autorun="true"`) are the discs' working menus.
- Resources are loaded only for segments that will run: no activation
  information, or selected and `autorun="true"`.

Timing: the title timeline keeps counting while a soft application's resources
load; the application's execution period starts at or after `titleTimeBegin`.
Page and application clocks are independent of the media clock, so a markup
page with `timing@clock="page"` keeps ticking while the user pauses video.
Unmap at the exclusive `titleTimeEnd`.

On disc: 2529 `ApplicationSegment`; `sync` `hard` 2120, `soft` 304, absent 105
(= hard); `autorun` `true` 2168, `false` 136; `zOrder` `0` on 2227; `group` on
118 (values 1–8); `language` and `appBlock` on 0 (no disc uses Application Blocks;
language-specific menus appear as `PlaylistApplication` languages, §3.15, and
as separate playlists chosen by a selector, §3.20). `titleTimeBegin`
`00:00:00:00` on 2366. `[1, 11, 12]` **VERIFIED** (load); pause behaviour
**INFERRED** (independent clocks).

**`AdvancedSubtitleSegment`** maps an Advanced Subtitle (timed-text markup)
onto the timeline. `src` is the Advanced Subtitle's manifest. Extra attribute
`sync` (`hard` \| `soft`, default `hard`). Children: `Subtitle+` (which subtitle
track numbers this segment provides; `streamNumber` omitted), then
`ApplicationResource*`. On disc: 0 ([11](11_gaps.md) B3).

## 3.14 Resources

A resource is a file (usually an ACA archive) that must be in the File Cache
before something uses it. Three elements:

| Element | Belongs to | Lifetime |
|---|---|---|
| `ApplicationResource` | one `ApplicationSegment` or `AdvancedSubtitleSegment` | that application's valid period |
| `TitleResource` | one `Title` (shared by its applications) | its own `titleTimeBegin`–`titleTimeEnd` |
| `PlaylistApplicationResource` | one `PlaylistApplication` | every title except FirstPlayTitle |

`ApplicationResource` and `TitleResource` share `ResourceType` (children:
`NetworkSource*`, §3.11):

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `src` | URI | yes | | The file to load. With `NetworkSource`, the file is still referred to by this URI |
| `size` | positive integer | yes | | Size in bytes to reserve. May be larger than the file, **must not be smaller** ([05](05_manifest_hdi.md) §5.7) |
| `priority` | non-negative integer | yes | | Removal priority when the File Cache needs space and the resource is no longer used by an active application or title. `ApplicationResource` ≥ 1, `TitleResource` ≥ 0, so application resources are removed before title resources |
| `multiplexed` | `false` \| non-negative integer | yes | | `false`: load from `src`. An integer: the resource is also multiplexed into the video as ADV_PCK packs with that slot number ([08](08_evo.md) §8.6) |
| `loadingBegin` | time expression | no | application: its `titleTimeBegin`; title resource: `00:00:00:00` | When loading starts on the title timeline |
| `noCache` | boolean | no | `false` | Only when `src` is `http`/`https`: `true` adds `no-cache` to `Cache-Control` and `Pragma` |
| `description` | string | no | | Free text |

`TitleResource` adds `titleTimeBegin` and `titleTimeEnd` (required): the
resource's valid period.

`PlaylistApplicationResource`:

| Attribute | Type | Req. | What it is for |
|---|---|---|---|
| `src` | URI | yes | File to load; must be on the disc or in persistent storage (not the network, not the script-managed File Cache area) |
| `size` | positive integer | yes | Bytes to reserve (as above) |
| `multiplexed` | `false` \| non-negative integer | yes | As above |
| `description` | string | no | Free text |

**`multiplexed` is not a boolean.** An integer is an ADV_PCK slot, and the packs
may be absent from the clip that plays (OLIVER_TWIST_JPN `LoopMenu.EVO`), so
**always load `src`**. `"0"` is the integer 0, not `false`; no ADV_PCK uses slot 0,
and the 12 rows with `"0"` are ordinary ACA files. Load them from `src` like
`false`.

**File Cache state machine.** Each resource is in one of five states:
non-exist → loading → ready (loaded, application not yet active) → used (at least
one active application uses it) → available (loaded, no valid application uses
it) → non-exist when the File Cache Manager discards it. Loading starts at
`loadingBegin` (or `titleTimeBegin`), is skipped for applications with
`autorun="false"` or not selected, and is cancelled if `autorun` turns false
during loading. When several applications share a resource the strongest state
wins: used > ready > available > loading > non-exist; a resource already loaded
or loading is never loaded twice. On a jump to another title, every resource the
new title does not use becomes available, with the new title's priorities. On a
jump inside a title, every resource whose valid period (or loading period)
contains the target time must be fully loaded before playback resumes there.
Resources in the loading, ready and used states must fit in 64 MB minus the
Streaming Buffer; that is the author's obligation ([05](05_manifest_hdi.md) §5.7).

On disc: `ApplicationResource` 2506 (`multiplexed` `false` 2495, `1` 8, `2` 3;
`priority` `1` 2440, `2` 32, `3` 34; `loadingBegin` on 30, all `00:00:00:00`;
`noCache` 0; `src` ACA 2354, PNG 114, XMF 17, JS 17, …). `TitleResource` 80
(`priority` `0`, `multiplexed` `false`, `loadingBegin` `00:00:00:00` on all).
`PlaylistApplicationResource` 455 (`multiplexed` `false` 126, `"0"` 12, slots
`1`–`19` on the rest; ACA 409, PNG 46).

`[1, 5, 11, 12]` **VERIFIED** (attributes); state machine from [1].

## 3.15 PlaylistApplication

An application that lives for the whole playlist: it is active on every title
except FirstPlayTitle, typically the persistent menu bar. Children:
`PlaylistApplicationResource*` (§3.14).

| Attribute | Type | Req. | What it is for |
|---|---|---|---|
| `src` | URI | yes | Its manifest (`.xmf`, or `something.aca/manifest.xmf`) |
| `language` | language | yes | Its language. Unique among the playlist's `PlaylistApplication` elements |
| `id` | ID | no | Name for script |
| `description` | string | no | Free text |

Rules [1]: all `PlaylistApplication` elements form one Application Block; only
the one matching the player's menu language is activated. It is always
hard-synchronised; its resources come from the disc or persistent storage; its
markup must not use the title clock. Match `language` as two letters (script
compares `Player.menuLanguage`, sometimes after `.slice(0,2)`).

On disc: 203 playlists; `language` `en` 186, `de` 11, `ja` 3, `fr` 3, unique in
every playlist.

## 3.16 ChapterList

The title's chapters. Children: `Chapter` (1–1999). Chapters are **numbered by
document order from 1**.

| Attribute | Type | Req. | What it is for |
|---|---|---|---|
| `titleTimeBegin` | time expression | yes | Where the chapter starts on the title timeline |
| `displayName` | string | no | Chapter name a player may show |
| `id` | ID | no | Name for script |
| `description` | string | no | Free text |

Seeking to a chapter goes title time → clip (§3.10) → object time → time map
([07](07_map.md)).

On disc: 1014 lists, 7665 chapters, `titleTimeBegin` never decreasing in a list.

## 3.17 TrackNavigationList

The user-visible description of the title's tracks: languages, whether the user
may select them, forced subtitles. Children, in order: `VideoTrack` (0–9),
`AudioTrack` (0–8), `SubtitleTrack` (0–32). All share `TrackNavigationType`:

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `selectable` | boolean | no | `true` | `false`: the user cannot select this track (script still can) |
| `description` | string | no | | Free text |

| Element | Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|---|
| `VideoTrack` | `track` | 1–9 | yes | | The video track number (§3.12) described |
| `AudioTrack` | `track` | 1–8 | yes | | The audio track number described |
| | `langcode` | langCode | yes | | Language and code extension (§3.2) |
| `SubtitleTrack` | `track` | 1–32 | yes | | The subtitle track number described |
| | `langcode` | langCode | yes | | Language and code extension |
| | `forced` | boolean | no | `false` | `true`: display this subtitle track even when the user has subtitles off |

`forced` and the langCode extension `09` (forced caption) are separate signals:
95 of the 97 `…:09` subtitle tracks do not set `forced`.

When a title has no usable list (718 omit it, 15 have an empty one): use the
first mapped `Audio` track, else track 1, and video track 1. On disc these never
differ from track 1 (all 493 list-less titles with an `Audio` child start with
track 1). Do not invent a `defaultLanguage` match. `[11, 12]` **VERIFIED**
(fail-closed).

On disc: 2478 lists; `AudioTrack` 3450 (`selectable="false"` 59), `SubtitleTrack`
11259 (`selectable="false"` 260; `forced` only ever `false`), `VideoTrack` 956.

## 3.18 ScheduledControlList

Frame-accurate pauses and script events on the title timeline. Children:
`PauseAt` and `Event`, any mix, at least one, in **strictly increasing**
`titleTime` order (no two at the same time).

| Element | Attribute | Type | Req. | What it is for |
|---|---|---|---|---|
| `PauseAt` | `titleTime` | time expression | yes | When the timeline reaches it, **pause** the title timeline (video freezes on that frame) until script resumes (`Player.playlist.play()`, or a `jump`). Inside a clip's valid period the time must fall on a coded video frame's PTS |
| | `id` | ID | no | Name for script |
| `Event` | `titleTime` | time expression | yes | When the timeline reaches it, the Playlist Manager fires a **Playlist Manager Event** named by `id`; script catches it with `addEventListener("<id>", …)` ([05](05_manifest_hdi.md) §5.3). No effect on video. Script may handle it late |
| | `id` | ID | no | Event name. Without one, nothing can listen |

Fire each entry once, when the timeline clock crosses `titleTime`; after a
backward `jump` a re-crossing may fire it again (edge-triggered). This is how a
menu-loop clip holds its last frame: `BATMAN_BEGINS` has a loader clip with
`PauseAt id="end-loader" titleTime="00:00:04:59"` and `Event
id="enable-mainmenu" titleTime="00:00:05:01"`.

On disc: 435 lists, all strictly increasing; `PauseAt` 92 (`id` on 36), `Event`
2696. `[1, 11, 12]` **VERIFIED** (structure); pause and dispatch semantics from
[1].

## 3.19 URI of a clip's MAP

`src="file:///dvddisc/HVDVD_TS/UNILOGO.MAP"` (`MYSTERY_MEN` `VPLST000`)
resolves to the volume root + `HVDVD_TS/UNILOGO.MAP`; the video is the sibling
`HVDVD_TS/UNILOGO.EVO`, confirmed by the EVOBI filename in the VTI
([06](06_vti.md)). Relative URIs resolve against `xml:base` (Title or
FirstPlayTitle) and then the playlist's own location.

## 3.20 Which playlist to open

Boot file: **the highest `$$$` present** among `ADV_OBJ/VPLST$$$.XPL`
(Scenarist: "The highest-numbered Playlist is loaded first"). `.BAK` playlists
are not searched. Audio-only players search `APLST$$$.XPL` instead (0 on disc).

| Rule | N |
|---|---|
| Highest `VPLST$$$` has a `PrimaryAudioVideoClip` (video from the XPL alone) | 116/119 |
| Highest is a **selector** (application only; loads another playlist at run time) | 3 |

Selector discs: `MATRIX_REVOLUTIONS` (`VPLST099`), `BLADE_RUNNER` (`VPLST002`),
`TRAINING_DAY` (`VPLST003`). Each `selector.aca/script.js` (UTF-16BE) calls
`Player.playlist.load("file:///dvddisc/ADV_OBJ/VPLST000.XPL")` chosen by
`Player.menuLanguage`, switching on two-letter tokens (`en`, `fr`, `ja`, `de`;
`en` default). A player that follows the startup sequence must run HDi on these
three. Opening a lower `VPLST` without HDi is a research fallback only (`e14`:
3/3 have one with clips).

`FirstPlayTitle`, if present, plays before Title 1 (§3.9).

`[1, 7, 11]` **VERIFIED** (`e12`)

## 3.21 Specification text versus schema and discs

Where the sources disagree, the schema wins over the specification text, and
the discs show what players accept.

| Point | Specification text [1] | Schema / discs |
|---|---|---|
| `Title@onEnd` | an early passage calls it a title **number**, `0` = pause | XSD: IDREF to a Title `id`; normative text: absent = stop. Discs: 3192/3192 resolve to an `id` |
| Titles per playlist | "512 or less" | XSD: 999 |
| Chapters per list | "512 or less" | XSD: 1999 |
| `ApplicationResource@size` | "can be omitted" | XSD: required; present on every row |
| `PlaylistApplication` z-order | "Describes the Application z-order" | no `zOrder` attribute in either XSD |
| `noCache` on resources | "if the URI scheme **is** http, the attribute shall be absent" | a typo for "is not": the attribute only has meaning for http/https |
| Version | `minorVersion` `0` | discs declare `0` but use v1.1 attributes (§3.1) |
| `mediaAttr` | must name an existing item | 2 discs point at missing sub-picture items (§3.12) |
| Manifest `Resource@src` | "absolute URI … relative URI shall not be used" | 12 manifests use relative script names ([05](05_manifest_hdi.md) §5.1) |

## 3.22 On disc

`e26` (every playlist): 247 files, all valid against the v1.1 schema; every
rule above that can be checked from the files holds (title numbering, `onEnd`
targets, scheduled-control ordering, chapter ordering, stream numbers against the
VTI, seamless abutting, `PlaylistApplication` languages unique), with only the
two `mediaAttr` authoring errors listed in §3.12. Element counts:

| Element | N | Element | N |
|---|---|---|---|
| `Playlist` | 247 | `Title` | 3196 |
| `FirstPlayTitle` | 119 | `PrimaryAudioVideoClip` | 4847 |
| `ApplicationSegment` | 2529 | `ApplicationResource` | 2506 |
| `TitleResource` | 80 | `PlaylistApplication` | 203 |
| `PlaylistApplicationResource` | 455 | `MediaAttributeList` | 244 |
| `Video` / `Audio` / `Subtitle` | 4869 / 6399 / 19992 | `SubVideo` / `SubAudio` | 84 / 38 |
| `ChapterList` / `Chapter` | 1014 / 7665 | `TrackNavigationList` | 2478 |
| `ScheduledControlList` | 435 | `PauseAt` / `Event` | 92 / 2696 |
| `NetworkTimeout` | 14 | `SecondaryAudioVideoClip`, `SubstituteAudioVideoClip`, `SubstituteAudioClip`, `AdvancedSubtitleSegment`, `NetworkSource` | 0 |

`[1, 5, 7, 11, 12]`
