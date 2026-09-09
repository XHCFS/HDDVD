# 3. Playlist: VPLST$$$.XPL

*Counts written "N/120", "N/119", "on N discs", "listings", or as named discs are over the reference corpus of 120 archived retail HD DVD images [11]. `eNN` are the reproducible verification experiments [12].*


Path: `ADV_OBJ/VPLST$$$.XPL` with `$$$` = `000`…`999`.  
247 files, 0 parse failures, all `majorVersion="1"` `minorVersion="0"`.
`[11, 12]` **VERIFIED**

Namespace (required):

```
http://www.dvdforum.org/2005/HDDVDVideo/Playlist
```

Schema: `spec/raw/adv_obj/v1.0/Playlist.xsd` (DVD Forum, 16 Jul 2006, HD DVD 1.0).
`xsi:schemaLocation` URLs on discs are authoring debris and are often dead; parse
against the local XSD.

Boot file: **highest `$$$` present** (patent FIG.50, Scenarist: “The highest-numbered
Playlist is loaded first”). `.BAK` playlists are not searched.

This XML **is** the title/clip/chapter/stream model. There is no PGC.

## 3.1 Time

Type `TimeExpressionType`: `HH:MM:SS:FF`.

`TitleSet@timeBase` is `60fps` or `50fps` (**247/247 are `60fps`**, `e12`/`e14`).
XSD still allows `50fps`. FF≥50 appears **3590** times on `60fps` titles (`e14`). Do
not clamp 00–49.
`TitleSet@tickBase` is `24fps` / `50fps` / `60fps` (application clock).
Convert a title time to a frame count with `timeBase`, not wall-clock seconds.

`00:00:01:00` at `60fps` = 60 frames. At 29.97 video this is **not** 1.000 s of
pictures; it is 60 ticks of the title timeline.

## 3.2 Tree

```
Playlist
  @majorVersion @minorVersion  required
  @displayName @type           optional, type default "Advanced"
  Configuration                required
    StreamingBuffer @size      even integer, **pack/sector units** (2048 B); "0"×246, "1024"×1
    Aperture @size             "1920x1080" | "1280x720" (247/247 are 1920x1080)
    MainVideoDefaultColor @color  6 hex YCbCr; outer frame around scaled main video
    NetworkTimeout @timeout    optional, **milliseconds** (14 playlists, all "0")
  MediaAttributeList           optional
    VideoAttributeItem @index @codec
    AudioAttributeItem @index @codec [@channels …]
    SubpictureAttributeItem @index @codec
  TitleSet
    @timeBase required   @tickBase @defaultLanguage optional
    FirstPlayTitle?      logo / FBI; no titleNumber
    Title+               @titleNumber required, max 999 titles
    PlaylistApplication* @src = Manifest (.xmf or .aca/….xmf)
```

## 3.3 Title

| Attribute | Required | Notes |
|---|---|---|
| `titleNumber` | yes | positive integer |
| `titleDuration` | yes | `HH:MM:SS:FF` |
| `id` | no | XML ID; `onEnd` targets this |
| `onEnd` | no | IDREF of next Title (3192/3196 titles have it). **Omitted → stop** after the title (script may still `IPlaylist.load` / `jump`). Not a loop and not a hidden menu. |
| `selectable` | no | default true |
| `displayName` | no | UI string |
| `alternativeSDDisplayMode` | no | default `panscanOrLetterbox` |
| `tickBaseDivisor` | no | default 1 |
| `parentalLevel` | no | default `*:1` |

`titleDuration` vs last clip `titleTimeEnd` (`e14`, titles+FPT with clips):
**3237** equal, **70** duration longer (unmapped tail: aperture colour), **1**
shorter: `THE_SEARCHERS` FirstPlayTitle `00:00:23:00` vs last clip end
`00:00:23:55`. Timeline length is `titleDuration`; do not extend the title past
it. That extra 55 ticks is authoring error.

Child sequence (0–299 mapping objects, then optional lists):

| Element | `src` points at | Corpus |
|---|---|---|
| `PrimaryAudioVideoClip` | **`.MAP` only** | 4847 |
| `ApplicationSegment` | **`.XMF` only** (often inside ACA) | 2529 |
| `SecondaryAudioVideoClip` | | 0 |
| `SubstituteAudioVideoClip` | | 0 |
| `SubstituteAudioClip` | | 0 |
| `AdvancedSubtitleSegment` | | 0 |
| `TitleResource` | | rare |
| `ScheduledControlList` / `Event` | no src; `@titleTime` cue | used |
| `ChapterList` / `Chapter` | `@titleTimeBegin` | 7665 |
| `TrackNavigationList` | language / selectable tracks | used |

`FirstPlayTitle` is the same clip mapping as a Title but **without** `titleNumber`.
Present on 119 of 247 playlists. It is **not** the boot playlist.
Patent (c)(d): play **start→end of the title timeline at normal speed
only**, video track 1 + audio track 1. Ignore user title-nav (Next / Prev /
FF / FR / time-search / `jump`) until FPT ends, then Title 1. Next is **not**
“skip to Title 1.”
`[1]` **INFERRED**
(fail-closed; skip key not demonstrated).
Missing File Cache resource during FPT: **keep playing FPT video**, skip that
resource (same as 64 MB overflow skip). Do not abort the playlist.

## 3.4 PrimaryAudioVideoClip

Extends `ClipMappingType`:

| Attribute | Required | Default | Meaning |
|---|---|---|---|
| `src` | yes | | URI of the **`.MAP`** |
| `titleTimeBegin` | yes | | when this clip occupies the title timeline |
| `titleTimeEnd` | yes | | exclusive end (`[begin,end)`). 1527 abutting pairs, **0** overlaps |
| `clipTimeBegin` | no | `00:00:00:00` | offset into the MAP/EVO |
| `dataSource` | no | `Disc` | `Disc` only for this element |
| `seamless` | no | `false` | decoder connection; not a second MAP format |
| `id` | no | | |

Children:

| Element | Attributes |
|---|---|
| `Video` | `@track` 1–9, `@mediaAttr` → `VideoAttributeItem@index`, `@angleNumber` 1–9 default 1 |
| `Audio` | `@track` 1–8, `@streamNumber` 1–8 default 1, `@mediaAttr` |
| `Subtitle` | `@track` 1–32, `@streamNumber` 1–32, `@mediaAttr` |
| `SubVideo` | `@track` fixed 1 |
| `SubAudio` | `@track` 1–8, `@streamNumber` |

**Decoder codec comes from `MediaAttributeList`, not from VTI `V_ATR`.**
`VideoAttributeItem@codec`: `MPEG-2` | `VC-1` | `AVC` | `MPEG-1`.
`AudioAttributeItem@codec`: `LPCM` | `DD+` | `DTS-HD` | `MLP` | `MPEG` | `AC-3`.
`SubpictureAttributeItem@codec`: `2bitRLC` | `8bitRLC`.

`@mediaAttr` default 1 (1-based index into that list).

## 3.5 ApplicationSegment

Extends `ObjectMappingType` (`titleTimeBegin`, `titleTimeEnd`, `src`).

| Attribute | Required | Default |
|---|---|---|
| `src` | yes | Manifest URI |
| `zOrder` | yes | |
| `autorun` | no | `true` |
| `sync` | no | `hard` |
| `language` `group` `appBlock` | no | |

Children: `ApplicationResource` (`src`, `size`, `priority`, `multiplexed` required).

`loadingBegin` is present on **110** `ApplicationResource` rows (7 discs). Every
value is `00:00:00:00` (`e14`). Treat as “pull at title start”, not a delayed
clock. `noCache="true"` is **0/247**. `ApplicationSegment@sync`: `hard` 2120,
`omit` 105 (= default hard), `soft` 304, **`none` 0**.
**Hard** holds the Title Timeline until File Cache load + startup finish.
**Soft** lets the timeline run; the app may appear after `titleTimeBegin` or
miss the window (jump-in / trick-play). Page / application clocks are
independent of the media clock: a mapped `timing@clock="page"` menu **keeps
ticking** when the user pauses video. Unmap at exclusive `titleTimeEnd`
anyway.
`[1]`
**VERIFIED** (load). Pause **INFERRED** (independent clocks).

`multiplexed` is XSD type `false | nonNegativeInteger`, **not** a boolean `true`.
`false` = File Cache loads the resource from `ADV_OBJ` (ACA or loose file).
A positive integer is a multiplex slot (ADV_PCK in **some** EVO,
[08](08_evo.md) §8.6). Always load `src`; packs may be missing from that
title’s clip (OLIVER `LoopMenu.EVO`).
Saved playlists: `ApplicationResource@multiplexed` is `false` on **2495** rows
and a positive integer on **11** (`"1"` ×8, `"2"` ×3).
`PlaylistApplicationResource@multiplexed` is mixed: `false` (126), `"0"` (12),
and slot indices `"1"`…`"19"` (the rest of 455). `"0"` is the XSD integer 0,
not the token `false`. No ADV_PCK uses slot 0 (`e16` slots start at 1). The
12 rows are URI ACA files (`menu.aca`, `ime.aca`, `Black.aca`, …). **Always
load `src`**, same as `false`. Do not skip the file because the attribute is
numeric.

Corpus `ApplicationResource@src`: ACA 2354, PNG 114, XMF 17, JS 17, …

## 3.6 PlaylistApplication

Lives under `TitleSet`, not inside a Title. Language-specific app for the whole playlist.

| Attribute | Required |
|---|---|
| `src` | Manifest URI (`.xmf` or `something.aca/manifest.xmf`) |
| `language` | ISO 639-1 **two-letter** (`en`, `fr`, …). XSD type is *named* `ISO639-2` but the enumeration is two letters. A 3-letter lookup will miss `Player.menuLanguage`. |

Children: `PlaylistApplicationResource` (`src`, `size`, `multiplexed`).

203 playlists have this. 455 resources: ACA 409, PNG 46.

## 3.7 Chapter

| Attribute | Required |
|---|---|
| `titleTimeBegin` | yes |
| `id` `displayName` `description` | no |

UI chapter list. Pack-accurate seek still uses the MAP ([07](07_map.md)).

## 3.8 TrackNavigationList

| Child | Max | Extra |
|---|---|---|
| `VideoTrack` | 9 | `@track`, `@selectable` default true |
| `AudioTrack` | 8 | `@track`, `@langcode` ISO 639-1 `xx` + hex extension `NN` (`LangCodeType`) |
| `SubtitleTrack` | 32 | `@track`, `@langcode`, `@forced` |

Of 3196 Title elements: 2463 carry a non-empty `TrackNavigationList`, **718 omit
it entirely, and 15 more carry an empty one** (733 with no usable track list).
For those 733: use the first mapped `Audio` child, else track 1. In the corpus
these never diverge. All 493 TNL-less titles that have an `Audio` child give
first `Audio@track="1"`, and the remaining 240 have no `Audio` element, so the
rule resolves to **track 1** in every case. Video track 1. Do not invent a
`defaultLanguage` match until a disc needs it.
`[11, 12]` **VERIFIED** (fail-closed; rule and lowest-track never differ).

## 3.9 URI of a clip MAP

Example from `MYSTERY_MEN` `VPLST000.XPL`:

```
src="file:///dvddisc/HVDVD_TS/UNILOGO.MAP"
```

Resolve: volume root + `HVDVD_TS/UNILOGO.MAP`.
Sibling EVO: `HVDVD_TS/UNILOGO.EVO`.
Confirm with EVOBI filename in [06](06_vti.md).

## 3.9a ScheduledControlList: timeline pauses and events

Child of `Title` (435 lists across the corpus). Two element types. `@titleTime` (`HH:MM:SS:FF` on the Title Timeline) is required
(2788/2788); `@id` is optional (56 entries omit it; an anonymous `PauseAt` still
pauses; an `Event` with no `id` has no script listener and is a no-op):

| Element | N | Rule |
|---|---|---|
| `PauseAt` | 92 | When the Title Timeline reaches `@titleTime`, **pause the timeline** (freeze video on that frame). It resumes only when script calls `Player.playlist.play()` (or a `jump`). This is how a menu-loop clip holds its last frame. |
| `Event` | 2696 | When the timeline reaches `@titleTime`, **dispatch a named event** (`@id`) to the HDi engine. Script catches it with `addEventListener("<id>", …)` ([05](05_manifest_hdi.md) §5.3). No video effect by itself. |

Canonical pattern (`BATMAN_BEGINS`): a loader clip has `PauseAt id=end-loader
titleTime=00:00:04:59` and `Event id=enable-mainmenu titleTime=00:00:05:01`.
The timeline plays the loader, pauses on its last frame, and the enable-mainmenu
event hands control to the menu script. Fire each entry once, when the monotonic
Title-Timeline clock crosses `@titleTime`; on a backward `jump` a re-crossing may
re-fire (fail-closed: treat as edge-triggered at crossing).
`[11, 12]`
**VERIFIED** (structure) / **INFERRED** (pause + dispatch semantics; Annex Z unpublished).

## 3.10 Which playlist to open

| Rule | N |
|---|---|
| Highest `VPLST$$$` contains `PrimaryAudioVideoClip` (video from XPL alone) | 116/119 |
| Highest is a **selector** (app only; loads another XPL at runtime) | 3 |

Selector discs: `MATRIX_REVOLUTIONS` (`VPLST099`), `BLADE_RUNNER` (`VPLST002`),
`TRAINING_DAY` (`VPLST003`). Each `selector.aca/script.js` (UTF-16BE) does:

```
Player.playlist.load("file:///dvddisc/ADV_OBJ/VPLST000.XPL");
```

by `Player.menuLanguage`. All three `switch` on **two-letter** tokens
(`en` / `fr` / `ja` / `de`); `en` is `default`. Full URI, not a
playlist number. Some other scripts do `Player.menuLanguage.slice(0,2)`
before matching. Expose a two-letter ISO 639-1 string (or at least treat
the first two characters as the language).
`[11]` **VERIFIED** (`e12`)

A player that implements FIG.50 strictly must run HDi on those three.
Opening a lower `VPLST` without HDi is a research-only fallback (`e14` A97:
3/3 have a clip-bearing lower `$$$`). It is **not** an implementation path:
library work waits on the menu gate in [05](05_manifest_hdi.md) §5.0.

If `FirstPlayTitle` is present it plays **before Title 1**, then Title 1.
`PlaylistApplication` is not scheduled on FirstPlayTitle. Hold user
title-nav until FPT ends (§3.3).

## 3.11 Elements in the XSD, unused in this corpus

`SecondaryAudioVideoClip`, `SubstituteAudioVideoClip`, `SubstituteAudioClip`,
`AdvancedSubtitleSegment`, `NetworkSource`. Still legal; implement if you need
network / persistent-storage clips.
