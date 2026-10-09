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

Sources: the DVD Forum book v1.01 [23 §6.2.3] (the normative syntax and rules;
its attribute definitions are the "Describes …" text that US 2007/0091495 [1]
quotes); the DVD Forum schemas [5] (v1.0, 16 Jul 2006, and v1.1, 5 Nov 2007);
the Scenarist AC 4.5 User Guide [7]; and the corpus, checked by `e26` (all 247
playlists) together with the earlier `e12` / `e14`.

## 3.1 File, versions, schema

| | |
|---|---|
| Path | `ADV_OBJ/VPLST$$$.XPL`, `$$$` = `000`…`999` (see §3.20 for which one plays) |
| Namespace | `http://www.dvdforum.org/2005/HDDVDVideo/Playlist` |
| Root element | `Playlist` (one per file) |
| Encoding | XML 1.0, `UTF-8` or `UTF-16` (UTF-16 needs a byte-order mark). `standalone`, if present, is `yes`. The discs use UTF-8 [23 §6.2.1] |
| Schema | `spec/raw/adv_obj/v1.1/Playlist.xsd` (use this one); `v1.0/Playlist.xsd` for reference |

**Two schema versions.** Every playlist in the corpus declares
`majorVersion="1" minorVersion="0"`, but all 247 validate against the **v1.1**
schema and 33 of them fail v1.0 (`e26`). The failures are exactly the v1.1
additions, so discs were authored with the 1.1 tools. Read against v1.1. The book
v1.01 matches the v1.0 schema on every row below. The differences:

| v1.1 change | Effect |
|---|---|
| `Title@outputFrameRate`, `FirstPlayTitle@outputFrameRate` added | 182 Titles and 3 FirstPlayTitles carry it (§3.8) |
| `VideoAttributeItem@sourcePictureProgressiveMode` added | 0 on disc (§3.6) |
| `AudioAttributeItem@codec` gains `HEAACV2`, `MP3`, `WMAPRO`, `HEAAC` | 0 on disc |
| A `Title` may have no presentation clip (`choice minOccurs="0"`) | `MATRIX_REVOLUTIONS` `VPLST099` has a clip-less title |
| `FirstPlayTitle` needs at least one clip; clips need at least one `Video` | (v1.0 allowed none) |
| Language type renamed `ISO639-2` → `ISO639-1` | same two-letter values |

**Reading rules.**

- The document must be well formed; a player does not have to validate it, and an
  invalid one has no guaranteed behaviour. No DTD or schema declaration is needed;
  a schema location is ignored [23 §6.2.1].
- Match elements and attributes by namespace and local name, never by prefix.
- Ignore XML comments (discs put them inside lists) and `xsi:schemaLocation`
  (170 roots carry one; the URLs are dead authoring debris).
- Apply the defaults in the tables below when an optional attribute is absent;
  the defaults are part of the meaning.
- Keep URIs exactly as written (§3.2, §3.19).

## 3.2 Data types

| Type | Syntax | Meaning |
|---|---|---|
| time expression | `HH:MM:SS:FF`; HH `00`–`23`, MM and SS `00`–`59`, FF `00`–`49` at 50 fps or `00`–`59` at 60 fps | A **non-drop frame count** on a title timeline: `(3600·HH + 60·MM + SS) · rate + FF`, where `rate` is `TitleSet@timeBase`. `00:00:01:00` at 60 fps is 60 counts, not one second of 29.97 video. One count is one video field (VSTU): 1.001/60 s, **1501.5** ticks of 90 kHz, at 60 fps; 1/50 s, 1800 ticks, at 50 fps. A clip's length in counts times 1501.5 equals its EVOB's 90 kHz length on 3538/3538 whole-EVOB clips and times 1500 on none (`e28`). Times shown to a viewer or handed to a demuxer in 90 kHz must use 1501.5, or a 2-hour title drifts about 7 s. FF ≥ 50 appears 3590 times on 60 fps titles (`e14`): do not clamp to 49. |
| frame rate | `50fps` \| `60fps` | Rate of the title timeline (the media clock) |
| tick rate | `24fps` \| `50fps` \| `60fps` | Rate of the application tick clock (page and application clocks). Must be `50fps` or `24fps` when the frame rate is 50, `60fps` or `24fps` when it is 60 |
| language | two lowercase letters, ISO 639-1 (`en`, `fr`, `ja`, …) | A menu / application language. The v1.0 type is *named* `ISO639-2` but its values are two-letter codes; match two letters |
| langCode | `xx:NN` or `*:NN`; `xx` ISO 639-1, `NN` two upper-case hex digits `[0-9A-F]{2}` | Track language plus **code extension** (what kind of track in that language). `*` = language not specified. Table below |
| parentalList | space-separated `CC:n` or `*:n`; `CC` ISO 3166 alpha-2 country in upper case, `n` `1`–`8` | Minimum parental level needed to play, per country. `*` = every country not listed. Each country (and `*`) at most once |
| multiplexed | `false` or a non-negative integer | How a resource reaches the File Cache (§3.14) |
| URI | `anyURI`, shorter than 1024 bytes in total | `file:///dvddisc/…` (the disc), `file:///filecache/…` (the File Cache's script area), `file:///required/…`, `file:///additional/<BasePath>/…`, `file:///common/required/…`, `file:///common/additional/<BasePath>/…` (persistent storage), `http://…` / `https://…` (network). An ACA member is addressed as `…/name.aca/member`. Relative URIs resolve per RFC 3986 §5 against the file's own location or `xml:base`; a path segment `..` is not allowed [23 §6.2.2] |
| boolean | `true` \| `false` | |
| ID / IDREF | XML name | `id` values are unique in the document; `onEnd` refers to one |

**Language code extension** (`NN` in langCode), from the book's Annex B
[23 Annex B]. The language half is two lower-case ISO 639 letters; `FF` as the
first byte of a binary language code means an additional code (`FFFF` = not
specified).

| NN | Audio | Subtitle (sub-picture) | On disc (audio / subtitle tracks) |
|---|---|---|---|
| `00` | not specified | not specified | 866 / 606 |
| `01` | normal | caption, normal size | 2336 / 9305 |
| `02` | for the visually impaired | caption, bigger size | 23 / 23 |
| `03` | director's comments 1 | caption for children | 210 / 271 |
| `04` | director's comments 2 | reserved | 14 / 0 |
| `05` | reserved | closed caption, normal size | 1 / 601 |
| `06` | reserved | closed caption, bigger size | 0 / 0 |
| `07` | reserved | closed caption for children | 0 / 0 |
| `09` | reserved | **forced** caption | 0 / 97 |
| `0D` | reserved | director's comments, normal size | 0 / 356 |
| `0E` | reserved | director's comments, bigger size | 0 / 0 |
| `0F` | reserved | director's comments for children | 0 / 0 |
| `80`–`FF` | provider defined | provider defined | 0 / 0 |

Every other value is reserved. A title holds at most one forced-caption (`09`)
sub-picture stream per language [23 Annex B.2]. The one audio track on `05` is
outside the table.

`[23 Annex B]` **SPEC**; `[11, 12]` counts.

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
| `majorVersion` | non-negative integer | yes | | Integer part of the Advanced Content version. Must be `1` [23 §6.2.3.14] |
| `minorVersion` | non-negative integer | yes | | Fractional part. Must be `0` in v1.01 (see §3.1) |
| `type` | `Advanced` \| `Interoperable` | no | `Advanced` | `Interoperable` marks content recorded in the user-recordable HD DVD video format rather than authored Advanced Content |
| `displayName` | string | no | | Human-readable name |
| `description` | string | no | | Free text |

On disc: `1`/`0` on 247/247; `type="Advanced"` on 79, absent on the rest;
`displayName` on 96 (often `Dummy`).

## 3.5 Configuration

System settings the player applies before any title starts. Children, in order:

| Element | Occurs | Attribute | Type | Req. | What it is for |
|---|---|---|---|---|---|
| `StreamingBuffer` | 1 | `size` | even integer | yes | Size of the Streaming Buffer carved out of the Data Cache, **in kB of 1024 bytes**, so the size is a multiple of 2048 bytes (`1024` = 1 MB) [23 §4.3.9.1, §6.2.3.8]. It holds network-streamed secondary video. `0` = none. The File Cache gets what remains |
| `Aperture` | 1 | `size` | `1920x1080` \| `1280x720` | yes | Full visible image size: the size of the graphics plane that applications draw on |
| `MainVideoDefaultColor` | 1 | `color` | six upper-case hex digits `YYCrCb` | yes | Colour of the main-video plane outside the (scaled) main video, the "Outer Frame Color". Y 16–235, Cr and Cb 16–240. Kept across title changes; script may change it |
| `NetworkTimeout` | 0–1 | `timeout` | non-negative integer | yes | How long the title timeline may wait for a hard-synchronised network download before the Network Timeout event, in milliseconds [23 §9.6.2] |

The Data Cache is at least 64 MB; the Streaming Buffer comes out of it, and
applications' resources must fit in the rest (§3.14). The player applies this
section at "Change System Configuration" in the startup sequence and on every
`Playlist.load`; doing so empties the File Cache and the Streaming Buffer
[23 §4.3.22.2]. In Restricted Mode (no trusted signature) `StreamingBuffer` must be
`0` and `NetworkTimeout` must be absent, or the playlist does not load
[23 Annex X.4.6.1].

On disc: `StreamingBuffer` `0` on 246, `1024` on 1; `Aperture` `1920x1080` on
247/247; `MainVideoDefaultColor` `108080` (112) or `107F7F` (135), both black;
`NetworkTimeout` on 14 playlists, all `0` (the meaning of 0 is not defined in
the sources).

## 3.6 MediaAttributeList

Codec and format of the elementary streams the clips use, indexed so that track
elements can point at them (`@mediaAttr`, §3.12). Children, in order: any number
of `VideoAttributeItem`, then `AudioAttributeItem`, then
`SubpictureAttributeItem`. `index` is unique per item type (a video item and an
audio item can both be `1`). `codec` is required; any other attribute that is
present must equal the matching field of the stream's `VTS_EVOB_ATR` in the VTI
([06](06_vti.md)) [23 §6.2.3.7].

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

**Codec source: the VTI.** The video compression mode in `EVOB_VM_ATR` bits 31–29
([06](06_vti.md)) equals the codec of the clip's `Video@mediaAttr` item on 4744 of
4869 clip videos. The 125 disagreements are on 17 discs (most on `THE_ANT_BULLY`,
`THE_MUMMY`, `MANCHURIAN_CANDIDIATE`, `CASABLANCA`). Ten of their EVOs on five discs
were read over HTTP: every one carries the codec the VTI names (`0xE0` MPEG-2 where
the playlist says VC-1 or AVC; `0xFD` VC-1 where it says MPEG-2). The playlist item
is the authoring error. Take the codec from the VTI; use `MediaAttributeList` only
as a hint.
`[11]` **VERIFIED** (2026-10 range reads)

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
| `titleNumber` | positive integer | yes | | The title's number. Starts at 1 and, in document order, either goes up by 1 or repeats the previous number. Titles that share a number form a **Parental Block**: each has `parentalLevel`, and the last one of the block is `*:1` [23 §6.2.3.1]. Fewer than 1000 titles |
| `id` | ID | no | | Name used by `onEnd` and by script |
| `type` | `Advanced` \| `Original` \| `UserDefined` | no | `Advanced` | `Original` / `UserDefined`: original or user-edited title of Interoperable (recorded) content |
| `selectable` | boolean | no | `true` | `false`: the user cannot navigate to this title (title menu, title search, next/previous title); script still can |
| `titleDuration` | time expression | yes | | Length of the title timeline. Every mapped object ends at or before it |
| `onEnd` | IDREF | no | | `id` of the title to play when this one ends. **Absent, or no such title: stop** after the title (script may still continue). Evaluated only when forward play (normal or fast forward) crosses the end; reverse play that reaches the start of the title resumes normal play in the same title [23 §4.3.19.5.1] |
| `tickBaseDivisor` | positive integer | no | `1` | Reduces the application tick rate for this title: with `3`, the Advanced Application Manager processes one tick in three and ignores the rest |
| `parentalLevel` | parentalList | no | `*:1` | Minimum parental level to play the title, per country. In a Parental Block the player plays the first title, in document order, whose level for the player's country (SPRM 12) is at most the player's level (SPRM 13) [23 §4.3.19.5.2] |
| `alternativeSDDisplayMode` | `panscanOrLetterbox` \| `panscan` \| `letterbox` | no | `panscanOrLetterbox` | Display modes allowed when outputting to a 4:3 monitor; the player must use an allowed one |
| `displayName` | string | no | | Title name a player may show |
| `description` | string | no | | Free text |
| `xml:base` | URI | no | | Base URI for relative URIs inside this title (XML Base) |
| `outputFrameRate` (v1.1) | `24p` \| `Other` \| `Unspecified` | no | `Unspecified` | Declares whether the title is 24-frame content, so a player can choose 24 Hz output. Not in the book v1.01; meaning beyond the value names is not in the sources |

**Rules.**

- Presentation objects on one title timeline must not overlap within a kind:
  no two `PrimaryAudioVideoClip`, no two `SecondaryAudioVideoClip`, no two
  `SubstituteAudioClip`, no two `SubstituteAudioVideoClip`. A
  `PrimaryAudioVideoClip` must not overlap a `SubstituteAudioVideoClip`.
  `SubstituteAudioVideoClip`, `SecondaryAudioVideoClip` and `SubstituteAudioClip`
  never overlap one another (they share the Secondary Video Player). No two clips
  with `dataSource="Disc"` overlap [23 §6.2.3.2].
  There is one main-video decoder and one sub-video decoder.
- `titleDuration` is greater than `00:00:00:00`; every `titleTimeEnd` is at most
  `titleDuration`.
- Where no clip is mapped, the timeline still runs and the main-video plane shows
  `MainVideoDefaultColor`.
- `titleDuration` is authoritative. On disc (`e14`, titles with clips): last
  clip end equals `titleDuration` 3237 times, is shorter 70 times (the tail
  shows the default colour), and longer once (`THE_SEARCHERS` FirstPlayTitle,
  `00:00:23:55` vs `00:00:23:00`: authoring error; stop at `titleDuration`).
- `onEnd` omitted means stop; it is not a loop and not a hidden menu.
- Starting a title resets the sub video's scale, position and alpha and the main
  video's layout; the outer-frame colour is kept [23 §4.3.13.3, Annex W].

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
no subtitle, sub-video or sub-audio. A `SubstituteAudioVideoClip` here must come
from the File Cache or persistent storage. It has no `titleNumber`,
`parentalLevel`, `type`, `tickBaseDivisor`, `selectable`, `displayName`, `onEnd` or
`description` [23 §6.2.3.1].

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `titleDuration` | time expression | yes | | Length of its timeline; every object ends before it |
| `alternativeSDDisplayMode` | as `Title` | no | `panscanOrLetterbox` | As `Title` |
| `xml:base` | URI | no | | As `Title` |
| `outputFrameRate` (v1.1) | as `Title` | no | `Unspecified` | As `Title` |

Playback rules [23 §4.3.19.6.1] (matching [1]): play it start to end at normal
speed, video track 1 and audio track 1, subtitles off whatever the system
parameters say. The title number is `0` meanwhile. Every user operation except
STOP and EJECT is refused. No Advanced Application runs (not even the
`PlaylistApplication`) and no event is raised. Then play Title 1; it never comes
back to the FirstPlayTitle. Its purpose is to cover the loading of
`PlaylistApplicationResource`s, which may be multiplexed into its video (§3.14).
If an error happens during it, the player may stop.
`[23]` **SPEC**

On disc: 119 of 247 playlists; `alternativeSDDisplayMode` `letterbox` 90.

## 3.10 Presentation clips

A clip maps a stretch of a video object onto the title timeline. All four clip
elements share `ClipMappingType`:

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `src` | URI | yes | | The object's **index file**, the time map (`.MAP`, [07](07_map.md)), not the `.EVO` (§3.19) |
| `titleTimeBegin` | time expression | yes | | Where the clip starts on the title timeline |
| `titleTimeEnd` | time expression | yes | | Where it ends; **exclusive** (`[begin, end)`): a frame mapped at `10` shows during `[10, 11)` [23 §4.3.19.2.1] |
| `clipTimeBegin` | time expression | no | `00:00:00:00` | Where playback starts **inside** the object, on the object's own clock. Must be the PTS of a coded frame ([23 Annex R.1.3]: a frame picture or a pair of field pictures) |
| `id` | ID | no | | Name for script |
| `description` | string | no | | Free text |

**Time model.** At title time `t` in `[titleTimeBegin, titleTimeEnd)` the clip
shows object time `clipTimeBegin + (t − titleTimeBegin)`. The span must fit in
the object: `clipTimeBegin + titleTimeEnd − titleTimeBegin` ≤ the object's
length. The object time converts to a disc address through the time map.
Object time counts from the EVOB's first video frame, not from PTS 0: the PTS is
`EVOB_V_S_PTM + object_time × 1501.5` ([06](06_vti.md) §6.3). Every EVOB start
PTM under a clip is above zero, and 4839/4839 clips fit inside their EVOB when
counted this way (`e28`). If the
object's video ends before `titleTimeEnd`, the main-video plane shows the outer
frame colour (a sub-video plane goes invisible) until `titleTimeEnd`; if it runs
longer, it is cut at `titleTimeEnd` [23 §4.3.19.2.1]. Audio that ends between two
title-timeline frames is rounded up to the next frame boundary [23 §4.3.19.7].

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
| `seamless` | `PrimaryAudioVideoClip` | boolean | no | `false` | `true`: this clip and the one mapped directly before it meet the seamless-connection conditions, so the decoder must not break between them (conditions below) |
| `sync` | the three secondary / substitute clips | `hard` \| `soft` \| `none` | no | see table | What happens if the object is not ready at `titleTimeBegin`. **hard**: the title timeline stops until it is. **soft**: the timeline keeps running and the object starts late. **none**: the object runs on its own time base, not the timeline's [23 §4.3.19.1] |
| `preload` | the three | time expression | no | | Title time at which the player should start prefetching the object |
| `noCache` | the three | boolean | no | `false` | Only with `dataSource="Network"` (otherwise absent): `true` adds `no-cache` to both `Cache-Control` and `Pragma` in the HTTP request; `false` adds it to neither |

Streaming (`Network`) objects go through the Streaming Buffer (§3.5);
`P-Storage`, `FileCache` and some `Disc` objects are read from the Data Cache so
the disc head is not shared with the primary clip. A network clip downloads its
time map first, completely, then streams the `.EVO` named by `EVOB_FNAME` in that
map, at the same location [23 §9.2.2.2].

**Which streams a secondary clip replaces** [23 §4.3.3, §4.3.19.2.2]. A
`SubstituteAudioVideoClip` replaces the primary main video and main audio; the two
never play together. A `SubstituteAudioClip` adds main-audio tracks; while one of
them plays, the primary main audio does not. A `SecondaryAudioVideoClip` replaces
the primary sub video and sub audio for its whole valid period; when its S-EVOB
carries both sub video and sub audio, its sub audio cannot be played without its
sub video.

**Seamless join** (`seamless="true"`) is allowed only when all of these hold
[23 §4.3.21.6, Annex K.1.4]; otherwise the attribute counts as `false` and the
timeline may break at the join:

- the two EVOBs are contiguous on the disc, or meet the jump conditions of
  [23 Annex K.7];
- `titleTimeEnd` of the earlier clip = `titleTimeBegin` of the later one;
- the earlier clip runs to the end of its EVOB:
  `clipTimeBegin + titleTimeEnd − titleTimeBegin = EVOB_V_E_PTM − EVOB_V_S_PTM`;
- the later clip starts at the start of its EVOB (`clipTimeBegin` = 0);
- the two EVOBs have identical `VTS_EVOB_ATR` (DD+ and AC-3 count as different);
- for interlaced video, the first field of the later EVOB is the opposite parity of
  the last field of the earlier one.

The begin and end of a primary clip are non-seamless points unless `seamless` is
`true`. A synchronised `SecondaryAudioVideoClip` must not span a non-seamless point
[23 §6.2.3.2].

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
| `networkThroughput` | non-negative integer | yes | Minimum network throughput needed to use this source, in **kbit/s** (1000 bit/s). Unique within the parent |

Allowed in a clip only when its `dataSource="Network"` and its `src` is
`http`/`https`; in `ApplicationResource` / `TitleResource` only when their `src`
is `http`/`https`.

Selection, done once while the title timeline is being set up: take the
`NetworkSource` entries whose `networkThroughput` ≤ the player's Network
Throughput parameter. If exactly one qualifies, use it; if several, use the one
with the largest `networkThroughput`; if none, use the parent's own `src`. For
resources, the file is still **referred to** by the parent's `src` URI whichever
source it was fetched from. Not allowed in Restricted Mode [23 Annex X.4.6.1].

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
| `Video` | 1–9 | `angleNumber` 1–9, default `1` | Main video (VM_PCK). `angleNumber` is used only when the clip's `src` is an **interleaved block**: it is the number *n* of the *n*-th TMAPI in that map, which picks the P-EVOB of the block (the angle) this track is. Otherwise omit it; main video is track 1. Must be `1` in a `SubstituteAudioVideoClip` |
| `Audio` | 1–8 | `streamNumber` 1–8, default `1` | Main audio (AM_PCK). `streamNumber` = audio stream number **+ 1**: the low 3 bits of `sub_stream_id` for LPCM / DD+ / DTS-HD / MLP, of `stream_id` for MPEG audio |
| `Subtitle` | 1–32 | `streamNumber` 1–32, default `1` | Sub-picture (SP_PCK). `streamNumber` = sub-picture stream number **+ 1**. The player looks that stream up in the EVOB's `EVOB_SPST_ATRT` ([06](06_vti.md)) and takes the decoding stream number for the current display (HD, SD wide, SD letterbox or SD pan-scan); that number is the low 5 bits of the `sub_stream_id` [23 §4.3.19.4.1, §6.3.1.2.3]. In `AdvancedSubtitleSegment`: `streamNumber` omitted, `mediaAttr` ignored |
| `SubVideo` | fixed `1` | | Sub video (VS_PCK) of the P-EVOB, or of the S-EVOB in a secondary clip. Present = enabled. A `SubVideo` and the `SubAudio` assigned at the same time come from the same clip |
| `SubAudio` | 1–8 | `streamNumber` 1–8, default `1` | Sub audio (AS_PCK); `streamNumber` = audio stream number + 1 |

Only streams listed here are available in that clip; an unassigned stream is
disabled. The assignment can change from clip to clip, so a track number means
"whatever stream the current clip maps to it". The number of streams and their
attributes do not change inside one EVOB [23 §4.3.19.4.1]. Track numbers of one
kind are unique at any one time [23 §6.2.3.3].

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
| `sync` | `hard` \| `soft` | no | `hard` | Start-up mode [23 §4.3.19.9]. **hard**: the title timeline holds while the resources load and the scripts' global code runs. **soft**: the timeline never holds; the application starts once its resources are in the File Cache, late, or not at all if the timeline jumped into its valid period or came back from trick play there. A resource that cannot be read without stopping the timeline must not belong to a soft application |
| `zOrder` | non-negative integer | yes | | Initial stacking order of this application on the graphics plane. Unique within the title and contiguous from 0; higher is drawn later (on top). Script can change it [23 §6.2.3.2, §7.3.1.2] |
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
- **Decision** (per segment, when the timeline enters its valid period;
  [23 §6.2.3.9], patent FIG.58 [1]):
  1. `autorun="false"` → inactive. Script may activate it later.
  2. Else, if `group` is present → active only while that group is the selected
     (valid) group. Script can change which group is selected.
  3. Else, if `appBlock` and `language` are present → active if `language`
     equals the player's menu language; if no segment of the block matches the
     menu language, the one whose `language` equals `TitleSet@defaultLanguage`
     is active; the others are inactive.
  4. Else (no activation information) → **active**. The book says so
     [23 §6.2.3.9]. The patent's prose for this branch says "invalid", which
     contradicts its own resource rule and every disc: 2275 segments with no
     activation information (or only `autorun="true"`) are the discs' working
     menus.
- Resources are loaded only for segments that will run: no activation
  information, or selected and `autorun="true"`.

Timing: the title timeline keeps counting while a soft application's resources
load; the application's execution period starts at or after `titleTimeBegin`.
No top-level script runs before the valid period starts, even if the files are
already loaded [23 §7.2.4.1].
Page and application clocks are independent of the media clock, so a markup
page with `timing@clock="page"` keeps ticking while the user pauses video.
Unmap at the exclusive `titleTimeEnd`.

On disc: 2529 `ApplicationSegment`; `sync` `hard` 2120, `soft` 304, absent 105
(= hard); `autorun` `true` 2168, `false` 136; `zOrder` `0` on 2227, unique and
contiguous within the title on 2225 of 2226 titles; `group` on
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
| `priority` | non-negative integer | yes | | Removal priority when the File Cache needs space and the resource is no longer in use. `0` is kept longest; a higher number goes first. `ApplicationResource` 1 to 2³¹−1, `TitleResource` 0 to 2³¹−1. Every title resource outranks every application resource, so application resources are removed first [23 §4.3.20.2.2, §4.3.20.3.3] |
| `multiplexed` | `false` \| non-negative integer | yes | | `false`: the File Cache Manager fetches `src`. An integer: the resource is also multiplexed into the video as ADV_PCK packs whose `advanced_identifier` equals it ([08](08_evo.md) §8.6); `loadingBegin` is then required, the packs come before `titleTimeBegin`, and the same file is also stored at `src` [23 §4.3.20.2.2, §6.5.4] |
| `loadingBegin` | time expression | no | application: its `titleTimeBegin`; title resource: `00:00:00:00` | When loading starts on the title timeline. The File Cache reserves the space then. `loadingBegin` ≤ `titleTimeBegin` < `titleTimeEnd` ≤ `titleDuration` |
| `noCache` | boolean | no | `false` | Only when `src` is `http`/`https`: `true` adds `no-cache` to `Cache-Control` and `Pragma` |
| `description` | string | no | | Free text |

`TitleResource` adds `titleTimeBegin` and `titleTimeEnd` (required): the
resource's valid period.

`PlaylistApplicationResource`:

| Attribute | Type | Req. | What it is for |
|---|---|---|---|
| `src` | URI | yes | File to load; must be on the disc or in persistent storage (not the network, not the script-managed File Cache area). Loaded before Title 1's other resources, during the FirstPlayTitle if there is one, else at `00:00:00:00` of Title 1; if not loaded by then, Title 1's timeline waits [23 §4.3.19.6.2.2] |
| `size` | positive integer | yes | Bytes to reserve (as above) |
| `multiplexed` | `false` \| non-negative integer | yes | As above |
| `description` | string | no | Free text |

**`multiplexed` is not a boolean.** An integer is an ADV_PCK `advanced_identifier`,
and the packs may be absent from the clip that plays (OLIVER_TWIST_JPN
`LoopMenu.EVO`), so **always load `src`**. The book requires the file at `src` for
this reason: a jump can cut the pack stream, and the File Cache Manager then reads
the file from the disc [23 §4.3.6, §6.5.4]. `"0"` is the integer 0, not `false`;
no ADV_PCK uses identifier 0, and the 12 rows with `"0"` are ordinary ACA files.
Load them from `src` like `false`. A numeric `multiplexed` on a
`PlaylistApplicationResource` needs a FirstPlayTitle to carry the packs
[23 §6.2.3.6].

**File Cache state machine** [23 §4.3.20.3]. Each resource is in one of five states:
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
If loading the playlist's resources overflows the File Cache anyway, the player
goes to the Stop state [23 §4.3.20.4]. Resources are loaded only for segments with
no activation information, or that are selected with `autorun="true"`, or that
are scheduled to be active [23 §4.3.20.3.2].

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

Rules [23 §4.3.19.6.2, §6.2.3.10] (matching [1]): all `PlaylistApplication`
elements form one Application Block; only the one matching the player's menu
language (SPRM 0) is activated, else the one matching `TitleSet@defaultLanguage`.
The choice is made once and kept even if the menu language changes. It is always
hard-synchronised; its resources come from the disc or persistent storage and
nothing loaded by `TitleResource` or `ApplicationResource` is visible to it; its
markup must not use the title clock. It starts before Title 1's other
applications and stops after them at the end of the playlist. It keeps running
through title jumps; during the jump the title number and time are the old
title's until playback of the new one starts. At each title start it is the
topmost application. Match `language` as two letters (script compares
`Player.menuLanguage`, sometimes after `.slice(0,2)`).

On disc: 203 playlists; `language` `en` 186, `de` 11, `ja` 3, `fr` 3, unique in
every playlist.

## 3.16 ChapterList

The title's chapters. Children: `Chapter` (1–1999). Chapters are **numbered by
document order from 1**. Fewer than 2000 per title and 100 000 per playlist.
Chapter 1 starts at `00:00:00:00`; start times increase in document order and
are at most `titleDuration`; a chapter ends where the next starts or at the end
of the title. A title without `ChapterList` is one chapter from
`00:00:00:00` [23 §6.2.3.5].

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
| `selectable` | boolean | no | `true` | `false`: the remote's angle / audio / subtitle keys skip this track (the Default Input Handler, [23 Annex V]); script still can select it |
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

**Choosing the current audio and subtitle track** [23 §4.3.19.4.2]. The player
keeps a *selected* track number, language code and code extension for audio and
for subtitles (system parameters set by the user or script; at start the
languages come from SPRM 16–19 and the numbers are unset). Whenever the clip
changes, it picks the *current* track:

1. Subtitles only: if a `SubtitleTrack` has `forced="true"`, take the lowest such
   track.
2. Else, if the selected track number is available, take it.
3. Else, among the available tracks (languages from this list), take the lowest
   track whose language and extension both match the selected ones; else whose
   language matches; else whose extension matches.
4. Else take the lowest available track. None available: no track.

The selected values stay as they were, so the choice is re-made at the next clip.
A track is available when the current clip assigns a stream to it (§3.12). Video
(the angle): the selected video track if available, else the lowest available.
Sub audio: the current `SubAudio` track if available, else track 1, else none.
Sub video is invisible and sub audio muted until script shows them
[23 §4.3.19.4.3–4].

When a title has no usable list (718 omit it, 15 have an empty one), step 4
applies: the lowest mapped `Audio` track and video track 1. On disc these are
always track 1 (all 493 list-less titles with an `Audio` child start with
track 1). `[23]` **SPEC**; `[11, 12]` **VERIFIED**.

On disc: 2478 lists; `AudioTrack` 3450 (`selectable="false"` 59), `SubtitleTrack`
11259 (`selectable="false"` 260; `forced` only ever `false`), `VideoTrack` 956.

## 3.18 ScheduledControlList

Frame-accurate pauses and script events on the title timeline. Children:
`PauseAt` and `Event`, any mix, at least one, in **strictly increasing**
`titleTime` order (no two at the same time).

| Element | Attribute | Type | Req. | What it is for |
|---|---|---|---|---|
| `PauseAt` | `titleTime` | time expression | yes | When the timeline reaches it in forward play (normal, fast or slow forward), **pause** the title timeline (video freezes on that frame) until script resumes (`Player.playlist.play()`, or a `jump`). Ignored in reverse play and when a jump lands on it. Fires a `play_state` event. Inside a clip's valid period the time must fall on a coded frame's PTS |
| | `id` | ID | no | Name for script |
| `Event` | `titleTime` | time expression | yes | When the timeline reaches it **at normal speed**, the Playlist Manager fires a `ScheduledEvent` (type `"scheduled_event"`, property `id`) [23 §4.3.19.2.5, Annex Z.6]. Not fired in trick play or by a jump. No effect on video. Script may handle it late |
| | `id` | ID | no | Event name, read by script as `evt.id` |

How discs listen: 14 listeners use `addEventListener("scheduled_event", …)` and
test `evt.id`, as the book says. `1408_DC` instead listens with the id as the event
type (`addEventListener("endFeature", …)`, `"endMenu"`) and nothing else fires that
type. A player that also dispatches an event whose type is the `id` runs both
patterns; no disc listens to both, so nothing runs twice. `[23]` **SPEC**;
`[11]` **VERIFIED** (122 scripts); the second dispatch **INFERRED**.

Fire each entry once, when the timeline clock crosses `titleTime`; after a
backward `jump` a later normal-speed crossing fires it again. This is how a
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

Boot file: **the highest `$$$` present** among `ADV_OBJ/VPLST$$$.XPL`, and in
persistent storage when `SEARCH_FLG` is 0 ([02](02_discid.md) §2.3)
[23 §4.3.22.2] (Scenarist: "The highest-numbered Playlist is loaded first").
`.BAK` playlists are not searched. Players without a display search
`APLST$$$.XPL` instead (0 on disc).

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

Where the sources disagree, the book v1.01 [23] and the schema win over the patent
text, and the discs show what players accept.

| Point | Patent text [1] | Book [23] / schema / discs |
|---|---|---|
| `Title@onEnd` | an early passage calls it a title **number**, `0` = pause | Book and XSD: IDREF to a Title `id`; absent = stop. Discs: 3192/3192 resolve to an `id` |
| Titles per playlist | "512 or less" | Book: fewer than 1000; XSD: 999 |
| Chapters per list | "512 or less" | Book: fewer than 2000 per title; XSD: 1999 |
| `ApplicationResource@size` | "can be omitted" | Book (§4.3.20.2.2) and XSD: required; present on every row |
| `PlaylistApplication` z-order | "Describes the Application z-order" | no `zOrder` attribute; the book puts it on top at each title start (§3.15) |
| `noCache` on resources | "if the URI scheme **is** http, the attribute shall be absent" | a typo for "is not": the attribute only has meaning for http/https |
| Version | `minorVersion` `0` | book: `0`; discs declare `0` but use v1.1 attributes (§3.1) |
| `mediaAttr` | must name an existing item | 2 discs point at missing sub-picture items (§3.12); 125 clip videos name the wrong codec (§3.6) |
| Manifest `Resource@src` | "absolute URI … relative URI shall not be used" | book says the same; 12 manifests use relative script names ([05](05_manifest_hdi.md) §5.1) |
| Playlist `Event` | "Playlist Manager Event" | book: `scheduled_event` with `id`; one disc listens on the id (§3.18) |

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
