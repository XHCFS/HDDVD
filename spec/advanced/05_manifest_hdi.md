# 5. Manifest, markup, script (HDi)

*Counts written "N/120", "N/119", "on N discs", "listings", or as named discs are over the reference corpus of 120 archived retail HD DVD images [11]. `eNN` are the reproducible verification experiments [12].*


HDi markup, script, and File Cache are part of Category 2. Linear video without
them is not Advanced Content. The surface below is specified end to end.

## 5.0 Scope (CLOSED)

On-disc menus are specified: this sheet plus [03](03_playlist.md),
[04](04_aca.md), [08](08_evo.md), the v1.0 XSDs, and `iHD_Scripting_API.txt`.
That holds for PNG-button Category 2 menus. Glyph/`anchor`/plane-alpha are
fail-closed in §5.9 (OpenType + XSL-FO names + patent overlay). They are not a
separate gap.

**In scope.** A designed retail menu works offline:

1. FIG.50 File Cache load of Manifest, markup, script, fonts, images, TMAPs.
2. ACA extract, including `0xff` members by offset/length.
3. `PlaylistApplication` (whole playlist except FirstPlayTitle) and
   `ApplicationSegment` (mapped on one title): `zOrder`, `autorun`, `sync`,
   `language` / `appBlock`.
4. iHD document: layout, `ihd#style`, `ihd#state`, timing (`cue` / `par` /
   `seq` / clocks).
5. Focus and remote navigation (`navIndex`, `navUp`…, `button`, `input`,
   `accessKey`).
6. ECMAScript host: language edition plus **typed** typelib members discs call
   (`IPlaylist.load` / `play` / `pause`, `ITitle.jump`, `Player.menuLanguage`,
   events).
7. Graphics plane composited over scaled main video in the Aperture.
8. ADV_PCK `0x80` → File Cache when packs exist; always load `src` (slot may
   be absent from that EVO; see [08](08_evo.md) §8.6).
9. Persistent-storage URI grammar for apps that `IPlaylist.load` a P-storage
   `VPLST` (PREMONITION).

**Out of scope:** network TLS / `.CER` / `IHTTPClient`, Category 1 PCI
buttons, firmware RE, AACS video decrypt (Archive.org packs are clear; licensed
players still need [09](09_aacs.md) later).

**Status:** File formats, `IPlaylist.load`, P-storage **script** URI
`file:///required/{contentId}/`, FIG.50 search as that same URI, JS encoding,
`jump`/`elapsedTime` types, PNG-button + `<p>`-in-`div` raster (§5.9), File
Cache `@size` / 64 MB fail-closed / wipe-on-`load`, and ADV_PCK concat
([08](08_evo.md) §8.6, `e16`) are specified (`e15`/`e17`, §5.7–5.8).
`jump`’s boolean, cue XPath, glyph/`anchor`, and plane alpha
are fail-closed in §5.3 / §5.9. Change those rules only if a disc contradicts
them.

`[5, 6, 11, 12]`

## 5.1 Manifest: `.xmf`

A manifest is the **initialization information of one HDi application**:
where on screen it draws, which markup page it opens with, which scripts run at
start-up, and which files it uses. The player launches the application from
it [1]. The playlist starts an application by pointing at its manifest
(`ApplicationSegment@src` or `PlaylistApplication@src`, [03](03_playlist.md)).
Manifests are usually members of an ACA ([04](04_aca.md)).

| | |
|---|---|
| Namespace | `http://www.dvdforum.org/2005/HDDVDVideo/Manifest` |
| Schema | `spec/raw/adv_obj/v1.0/Manifest.xsd` (Spec. 6.2.4.2); v1.1 is identical |
| Root element | `Application` |
| Encoding | UTF-8, optionally with a byte-order mark |

### Document tree

`?` = optional, `*` = any number, `+` = at least one. Children appear in exactly
this order (the XSD is a `sequence`). None of them has child elements;
everything is in attributes.

```
Application     @id?  @xml:base?                 the application
├── Region      @x  @y  @width  @height          where it draws
├── Script*     @src  @id?                       scripts run at start-up
├── Markup?     @src  @id?                       first page shown
└── Resource+   @src  @id?                       files it uses
```

### Elements

**`Application`** (root, one per file). The application itself.

| Child | How many | What it is |
|---|---|---|
| `Region` | exactly 1, first | Where the application draws |
| `Script` | any number | Scripts run at start-up |
| `Markup` | 0 or 1 | The first page shown |
| `Resource` | 1 or more, last | Files the application uses |

| Attribute | Type | Req. | What it is for |
|---|---|---|---|
| `id` | ID | no | Name of the application; script can refer to it |
| `xml:base` | URI | no | Base for resolving relative `src` values |

**`Region`** (exactly 1, first child). Where the application draws when it
starts: the values are the region's **initial** position and size. The canvas
is the graphics plane; its size comes from the playlist's `Aperture`
([03](03_playlist.md) §3.5). No children.

| Attribute | Type | Req. | What it is for |
|---|---|---|---|
| `x` | non-negative integer | yes | Left edge of the region (its top-left corner) on the canvas, in pixels |
| `y` | non-negative integer | yes | Top edge of the region (its top-left corner) on the canvas, in pixels |
| `width` | non-negative integer | yes | Width of the region, in pixels |
| `height` | non-negative integer | yes | Height of the region, in pixels |

**`Script`** (0 or more). A script that runs when the application starts. No children.

| Attribute | Type | Req. | What it is for |
|---|---|---|---|
| `src` | URI | yes | An ECMAScript (`.js`) file, evaluated as global code during start-up |
| `id` | ID | no | Name of this entry |

**`Markup`** (0 or 1). The first page the application shows. Absent for
script-only applications. No children.

| Attribute | Type | Req. | What it is for |
|---|---|---|---|
| `src` | URI | yes | The **initial** markup page (`.xmu`, §5.2). Later pages are loaded by script |
| `id` | ID | no | Name of this entry |

**`Resource`** (1 or more, last). A file the application uses. No children.

| Attribute | Type | Req. | What it is for |
|---|---|---|---|
| `src` | URI | yes | Markup, script, image, font, or a whole `.aca` archive |
| `id` | ID | no | Name of this entry |

**Every** file the application uses must be listed, except files in the
script-managed (API Managed) area of the File Cache. Each `src` must be the
absolute URI of one of the playlist's resources (`ApplicationResource`,
`TitleResource` or `PlaylistApplicationResource` `src`,
[03](03_playlist.md) §3.14): the playlist decides when files are loaded, the
manifest says which of them this application uses.

`Script` and `Markup` say **what to run**; `Resource` says **what to load**. The
file a `Script` or `Markup` names is always loadable through the `Resource` list:
listed directly, inside a listed archive (`…/menus.aca/script.js` when
`…/menus.aca` is a Resource), or a relative name inside the manifest's own archive.

### Reading rules

- Match elements by namespace and local name, never by prefix.
- Reject the document if the root is not `Application` in the Manifest
  namespace, the children are out of order, `Region` or every `Resource` is
  missing, or a required attribute is missing.
- Accept and ignore attributes that describe the file rather than the
  application: `xsi:schemaLocation` on the root, and a leading byte-order mark.
- Keep `src` exactly as written. The specification requires absolute URIs for
  `Resource`; discs also use relative names on `Script` (a bare `UniLoad.js`),
  which resolve against the manifest's own location, for a manifest inside an
  ACA that archive (RFC 3986, `xml:base` if present). Accept both.

### Example (`1408_DC` `popupMenu.xmf`)

```xml
<Application xmlns="http://www.dvdforum.org/2005/HDDVDVideo/Manifest">
  <Region x="0" y="0" width="1920" height="1080" />
  <Script src="file:///dvddisc/ADV_OBJ/script.js" />
  <Markup src="file:///dvddisc/ADV_OBJ/menu.xmu" />
  <Resource src="file:///dvddisc/ADV_OBJ/menu.xmu" />
  <Resource src="file:///dvddisc/ADV_OBJ/script.js" />
  <Resource src="file:///dvddisc/ADV_OBJ/popupMenu.aca" />
  <Resource src="file:///dvddisc/ADV_OBJ/font.ttf" />
</Application>
```

### On disc

`e24` checks every `.xmf` in the corpus against the rules above: 89 manifests
on 28 discs, 86 of them ACA members (extracted by offset/length).

- All 89 follow the XSD order with no undeclared attributes. 26 roots also
  carry `xsi:schemaLocation`.
- `Region` is `0,0,1920,1080` on all 89: applications cover the whole graphics plane.
- 72 have `Markup`; 17 are script-only (loader or logo applications). `Script`
  count runs 0–17 per manifest (71 have exactly one).
- `id` appears on `Application` (6), `Script` (14) and `Markup` (5), never on
  `Resource`. `xml:base` never appears.
- `src` is `file:///dvddisc/…` on 440 references. The other 12 are bare
  relative names, always on a `Script`, always in a manifest inside an ACA, and
  always naming a member of that ACA.
- All 229 `Script` / `Markup` files are loadable through `Resource`: 7 listed
  directly, 210 inside a listed `.aca`, 12 relative inside the manifest's own ACA.
- 215 of 223 `Resource` URIs are exactly one of the same disc's playlist
  resource URIs. The 8 others: the selector manifests of `BLADE_RUNNER` and
  `TRAINING_DAY` list `…/selector/script.js`, and `SHREK_THE_THIRD_EU`
  `iHD_Manifest.xmf` lists 6 archives that no saved playlist schedules.
- Encoding is UTF-8 on all 89; 6 start with a byte-order mark.

`[1, 5, 11, 12]` **VERIFIED**

## 5.2 Markup: `.xmu`

**The complete markup reference is [14](14_markup.md)**: the document tree
(§14.2), the value types and what each parses to (§14.3), every element with its
attributes (§14.4–14.7), the path expressions (§14.8), and every style and state
attribute (§14.9–14.10), checked against every markup document on disc (`e27`).
Read that sheet to implement markup. This section keeps the research notes
behind it; where a count here differs from sheet 14, the earlier `e15` sample is
the reason and sheet 14 is current.

Namespace: `http://www.dvdforum.org/2005/ihd`  
Also: `ihd#style`, `ihd#state`  
Schema: `spec/raw/adv_obj/v1.0/iHD.xsd`  
Root: `root` with required `xml:lang`

Saved sample (`e15` after the ≤320 KiB ACA pull): **97 ACA**, **84 XMU**,
**122 JS**. Counts move as more archives land. Method:
`spec/clean/17_HDI_MENU_RESEARCH.md`.

| Element | Count (`e15`) | Notes |
|---|---|---|
| `p` | 1390 | always a child of `div`; text runs, no style attrs on `p` itself |
| `div` `button` `input` | 1339 / 492 / 113 | body |
| `object` | 7 | `application/x-clearrect` or `audio/x-wav`, not JPEG/PNG `object` |
| `cue` `par` `seq` `defs` `g` `set` `animate` `event` | timing | `include` 36 → `.xmu` / `.xts` / `.xss` |
| `style` `styling` `meta` `link` | head / chrome | |

Used `ihd#style` local-names ⊆ iHDstyle.xsd (no unknown attrs). Top: `x y
width height position display backgroundImage opacity nav*` then
`contentWidth contentHeight backgroundFrame fontSize color font lineHeight
anchor zIndex visibility …`. New vs the first 50-ACA cut: `lineHeight`
(37) once `<p>` archives landed.

Used `ihd#state` (`e27`): `value` 113, `focused` 33, `enabled` 1. Markup rarely sets
`actioned`; Jumpstart Chapters and `1408` fire it from the remote (Enter).

**Clocks.** `timing@clock` (`e27`): `page` 68, `application` 9, `title` 3, omitted 8.

The three clock types (Microsoft HDi Jumpstart [14], *Dissecting Chapters*):

- **title clock**: locked to media time, *"when cues should occur at specific timecodes
  during the movie"* (in-movie experiences such as Warner IME and Universal U-Control).
- **page clock**: independent of media time, *"for cues that are time independent [and]
  have times relative to other cues (like menus)"*. A page-clock menu keeps ticking
  while the user pauses video.
- **application clock** (XSD enum [5]): runs for the application's active lifetime,
  independent of both, for app-global timers.

A markup document may carry more than one timing block. An omitted `<timing>` is legal
(STALINGRAD `startUp.xmu`); the Hello World sample's "empty timing tag is required" is a
sample convention, not a rule. Because the page and application clocks are independent of
the media clock (patent), `sync="soft"` does not freeze a page-clock menu's cues. Unmap
at exclusive `titleTimeEnd`.

`ApplicationSegment@sync` [1]: `hard` holds the Title Timeline until File Cache load and
startup finish; `soft` lets the timeline run, so the app may miss its window.

`[11, 12]` **VERIFIED** (title and page clocks from Jumpstart; independence from patent).
`[5]` application-clock lifetime and `[1]` pause behaviour are **INFERRED**.

**Cue.** `begin`/`end` are `TimeOrPathExpressionType` (iHD.xsd): either
`HH:MM:SS:FF` / `NNh|m|s|ms|f`, or a path. Retail menus use XPath:

```
<cue select="id('BT_scenes')"
     begin="id('BT_scenes')[state:focused()=1]"
     end="id('BT_scenes')[state:focused()=0]"
     use="ButtonFocused" />
```

`use` points at `defs/g` which may `set` style (e.g. `backgroundFrame`) and
dispatch `event@name`. Script `addEventListener` that name.

Also used (`e17`): `state:actioned()=true()` (Enter, Jumpstart Chapters;
`1408` uses a `seq` on `//button[state:actioned()=true()]`); durations
(`400ms`); `style:opacity()=1`; `$name` variables bound by
`document.setXPathVariable`. Timecode `HH:MM:SS:FF` on `begin`/`end` is rare
(69). An unknown path is false (the cue does not fire). This is the used
subset, not a general XPath 1.0 engine.

**Mapping vs cues (A40).** `ApplicationSegment@titleTimeBegin` / `@titleTimeEnd`
decide whether the app is on the Title Timeline. Cues run only while that
app is active. If a cue time and the mapping disagree, **mapping wins**:
there is no app to tick. Soft-sync apps may miss their window (Q52).
`[11, 12]` The mapping fields are **VERIFIED**; the rule that mapping (not cue time) gates whether an app ticks is **INFERRED** (Annex Z unpublished).

**Layout (used attrs only).** Implement §5.9. `x`,`y`,`width`,`height` are
aperture pixels (Configuration Aperture 1920×1080 on 247/247). `position` is
**always `absolute`** in this sample (1462/1462). `backgroundImage` is a list of
`url(...)` frames; `backgroundFrame` selects the index. `navUp`/`navDown`/
`navLeft`/`navRight` are the remote graph; `navIndex="none"` skips a node
(`1408` debug `input`). Full box-model
of unused XSD attrs (`writingMode`, padding, borders, …) is **not** required
until a census hits them.

**Encoding.** Saved XMU is UTF-8 (`<?xml … encoding="utf-8"`). JS is not.

Full element/attribute list remains the XSD. Do not invent a second schema.

## 5.3 Script

Compact-profile ECMAScript (no `with`, no `eval`; no optional methods such as
`substr`) talking to the HDi type library
(`spec/raw/adv_obj/iHD_Scripting_API.txt`, 106 typeinfos).
`[14]`

**Encoding:** UTF-16BE with BOM `FE FF` on **every** saved `.js` (`e15` N=122),
including the three loose `1408` files. Do not sniff UTF-8 for script.

Playback surface actually **called** on saved discs (`e15`):

| Call | Signature (disc + Jumpstart) |
|---|---|
| `Player.playlist.load(uri)` | string, full URI (`file:///dvddisc/ADV_OBJ/VPLST$$$.XPL` or `psUrl+name`) |
| `ITitle.jump(time, pause)` | `time` = `HH:MM:SS:FF`; `pause` boolean. Saved sources: **always `false`** |
| `IChapter.jump(time, pause)` | same. Index: `Player.playlist.titles["id"]` or `.chapters[n]` |
| `Player.playlist.play()` / `.pause` | distinct from `jump`. `1408` chapter handler: `jump(..., false)` then `play()` after hiding the menubar |
| `Player.playlist.currentTitle.elapsedTime` | `HH:MM:SS:FF` string |
| `application.createTimer(time, type, cb)` | `time` = `HH:MM:SS:FF` interval. `type` is `1` (150/151 sites) or `TIMER_APPLICATION` (1). `1` = title-timeline clock (fail-closed `TIMER_TITLE`; that name is unused in JS). Owner is `application.` (127 sites; 24 bare are continuation lines of the same). Returns `ITimer`: set `.enabled` (true 155 / false 74) and `.autoReset`. **`.autoReset` is `false` (one-shot) on 142 sites but `true` on 7**, all `resumeStoreTimer`, a `00:00:15:00` periodic resume-position saver. **Honor `autoReset` as written; do not assume one-shot.** `[11, 12]` VERIFIED |
| `Player.video.main.changeLayout(x, y, scale, cropX, cropY, cropW, cropH, time)` | **always 8 args** (101/101). `scale` = `Player.createVideoScale(num, den)` or `null`. Used: `(96,166,createVideoScale(1,1),0,0,720,480,"00:00:00:00")` ×67 (SD window); `(0,0,null,0,0,1920,1080,"00:00:00:00")` ×30 (full aperture). `createVideoScale` is **only** `(1,1)` (71/71) |
| `addEventListener(name, fn, bool)` | markup `event@name`, plus `controller_key_down`, `application_end` |
| `Player.menuLanguage` | two-letter (`en`/`fr`/`ja`/`de`). Selectors `switch` on that. Some JS `slice(0,2)` first |
| `Player.track.selectAudioTrackNumber` / `selectSubtitleTrackNumber` | 1-based |
| `Player.generalParameters.getValue` / `setValue` | string keys |
| `PersistentStorageManager.contentId` | GUID string in URI |
| `FileIO.getFileInfo` / `remove` / `createDirectory` / `getDirectoryInfo` | P-storage paths |
| `document.setXPathVariable(name, value)` | binds `$name` for cue path expressions (ARMY_OF_SHADOWS `$sw01`) |
| `document.getElementById` / `setProperty` | markup nodes from script |

`ITitle.jump` / `IChapter.jump` second argument is **pause-at-destination**
(fail-closed). `true` → seek then `PLAYSTATE_PAUSE`. `false` → seek and do
not force pause: a jump that selects another Title starts that title playing
(`1408` extras/trailers call `jump(..., false)` with no `play()`). If the
current title was already paused, it stays paused unless script calls
`Player.playlist.play()` (`1408` chapter buttons: `jump` then `play()` after
`menubarHide()`). Saved JS never passes `true` (`e15` 258/258 `false`).
Typelib: `play` / `pause` / `playState` live on `IPlaylist`, not on `jump`.
`[11]` **INFERRED**
(Annex Z unpublished; disc call shapes).

`IPlaylist.load` / soft reset is how a selector playlist (`VPLST099`) replaces
itself with `VPLST000` (patent FIG.51). Argument is the **full URI**:

```
Player.playlist.load("file:///dvddisc/ADV_OBJ/VPLST000.XPL");
```

PREMONITION also loads from required storage:

```
var psUrl = "file:///required/" + PersistentStorageManager.contentId + "/";
Player.playlist.load(psUrl + playlist);
```

`[11, 12]` **VERIFIED**
Soft reset replaces the playlist document; it is not a disc re-insert (DISCID
category probe is not re-run).

## 5.4 Runtime (patent FIG.50 steps 6–7)

After the playlist is chosen:

1. File Cache Manager loads Manifest, markup, script, fonts, images, and any TMAP
   needed before start.
2. Init Primary Video Player with VTI + TMAP(s) for Primary Audio Video.
3. Init Advanced Application engine.
4. Start Title Timeline. Objects mapped onto the timeline present according to
   `titleTimeBegin` / `titleTimeEnd`.

Firmware vs this API is **uncloseable** (no RE of player binaries). Catalog:
[http://hd-dvd.org/firmware.html](http://hd-dvd.org/firmware.html) is live but
intermittent (200 then 503 on 2026-09-08). Wayback:
https://web.archive.org/web/20231210144123/http://hd-dvd.org/firmware.html
OEM notes cover HDMI/network extras, not the HDi API. Cross-check FIG.50 against
XPL/DISCID instead ([10](10_playback.md) §10.7).

## 5.5 What is specified vs out of scope

| Subsystem | Sheet / source | Status |
|---|---|---|
| PlaylistApplication / ApplicationSegment mapping, `zOrder`, `sync`, `autorun`, `language`/`appBlock` | [03](03_playlist.md); patents FIG.57/70 | specified |
| `IPlaylist.load` full `file:///dvddisc/ADV_OBJ/VPLST$$$.XPL`; FIG.51 soft reset | this sheet; three `selector.aca/script.js` | specified |
| Manifest tree (`Region`, `Script`, `Markup`, `Resource`) | Manifest.xsd | specified (schema) |
| ACA directory `14+(flags&0xFF)+32`; extract by offset/length | [04](04_aca.md); `e17` 97 ACA / 885 members | specified (namelen 0/`>`/`/` = 0) |
| iHD used subset + cue XPath + clocks | iHD.xsd; `e15`/`e17` | specified for used attrs; unused XSD attrs untranscribed |
| Compact ES + typed `load`/`jump`/`elapsedTime`/`createTimer`/`changeLayout`/`setXPathVariable` | Jumpstart; `e15` N=122 JS | specified (`jump` pause; layout 8-tuple; timer type) |
| PNG-button raster + `nav*` + `backgroundFrame` + `<p>` in styled `div` | this sheet §5.9 | specified; glyph/`anchor`/alpha fail-closed same section |
| File Cache `@size` vs file | Jumpstart; `e15` | 532 equal, 2428 larger, **1 smaller** |
| File Cache 64 MB flush | Scenarist; HDDVDPLAYDLL strings; `@priority` | specified fail-closed (§5.7) |
| ADV_PCK `0x80` payload | [08](08_evo.md) §8.6; `e16` | specified (`STALINGRAD` `logo.EVO` N=2383; concat = ADV_OBJ file) |
| P-storage **script** URI | PREMONITION; Jumpstart; FIG.20 drawing | specified `file:///required/{contentId}/` |
| FIG.50 VPLST search | same URI; empty P-storage still boots | specified INFERRED (§5.8) |
| File Cache wipe on `load` | FIG.51 body; A37 | specified fail-closed (wipe then reload) |
| Markup `cue` vs `titleTimeBegin` | A40; §5.2 | specified (mapping wins) |
| `.CER` / `IHTTPClient` | 10 listed, bodies unsaved | out of gate |

XSD annotations cite unpublished DVD Forum book sections (`Spec. 7.5…`). Those
numbers are **not** a substitute for writing the engine here. Jumpstart
(https://learn.microsoft.com/en-us/archive/blogs/amyd/) and Scenarist AC 4.5
User Guide are the public prose; disc `.xmu` / `.js` win when they disagree.

## 5.6 Remaining spec work (no firmware)

Closed by `e15`/`e17`/`e16` + Jumpstart + patents (do not re-open): JS
encoding, `jump` pause-at-destination, `elapsedTime` string, cue path
allowlist, `file:///required/{contentId}/`, File Cache `size ≥ file` except
one authoring error, used iHD attr allowlist, compact ES, PNG-button layout
+ `nav*` + `backgroundFrame` + `<p>`-in-`div` + glyph/`anchor`/src-over
(§5.9), `changeLayout` 8-tuple / `createVideoScale(1,1)`, `createTimer`
type+`ITimer`, `animate` keyframe lists, `input` mode, `accessKey` VK_*,
`sync` hard/soft, `multiplexed="0"` as URI, ADV_PCK concat ([08](08_evo.md)
§8.6).

Not a second gate:

1. Re-run `e15`/`e17` if more ACA land so unused-attr claims stay
   falsifiable.
2. Unused iHDstyle attrs (`writingMode`, padding, borders, MNG, `pointer`)
   stay on the XSD until a census hits them.
3. Screenshot calibration of a specific OpenType file (hinting) is not
   required; scale `fontSize` to the em square.

Xbox `0xC667000A`: playlist `size` smaller than the file (`e15` N=1
PANS_LABYRINTH). Conforming player: reject that resource. The file on disc is
still 6436 bytes.

## 5.7 File Cache `@size`

Jumpstart: declared `size` **may be larger** than the file, **must not be
smaller**. Xbox error `XPLAYER_E_CANT_LOAD_RESOURCE` (0xC667000A) if the
resource is missing or `size` is too small.
`[14]`
`[14]`

Corpus (`e15`, every `ApplicationResource` / `PlaylistApplicationResource`
with `file:///dvddisc/` and a listing path): **532** equal, **2428** larger,
**1** smaller (`PANS_LABYRINTH` `/ADV_OBJ/multi_angle.aca` size 5500 vs listing
6436), **0** unlisted.

64 MB cap: Scenarist AC 4.5 User Guide (“The File Cache Loading must not at
any time exceed 64 MB”). Clips are flushed **only when space is needed**.
Higher Buffer Flush Priority is removed first; priority 0 is last. That maps
to playlist `@priority` (corpus: `1` on 2440 resources, omitted 455, `2` on
32, `3` on 34). Accounting unit is the playlist `@size` (Jumpstart / Xbox),
not raw member bytes.
`[7]` **INFERRED**
(authoring tool, not a player dump).

If a conforming title stays ≤ 64 MB, a player does not need an overflow
policy. When the live reserved `@size` sum would exceed 64 MB: flush
resources with the **highest** `@priority` first (Scenarist Buffer Flush
Priority; omitted PlaylistApplicationResource stays; they outlive titles).
If the new resource still does not fit, **do not load it**. Reference
decoder strings: `Exceeded cache size! Used: %.3f mb, Available: %.3f mb`
and `Insufficient space in file cache`.
`[10]`
**INFERRED** as fail-closed (no player dump of an overflowing title).
Conforming authored titles never hit this.

**`IPlaylist.load` (A37).** Follow FIG.51 **body**, not the drawing: Soft
Reset runs Change System Configuration (wipe File Cache and Streaming
Buffer) then loads the **new** playlist’s resources. Shared filenames are
re-fetched from disc / P-storage, not kept. Re-fetch is always correct;
keep-on-overlap is an unproven optimisation.
`[1]`
**INFERRED** (drawing vs body; body wins for wipe).

## 5.8 Persistent storage URIs (script)

```
file:///required/{PersistentStorageManager.contentId}/{relative}
file:///filecache/{relative}
file:///dvddisc/ADV_OBJ/{relative}
```

`file:///fixed/` and `file:///removable/` do not occur in saved JS (`e15`).
`STORAGE_REQUIRED` is how PREMONITION opens the device
(`getPersistentStorageDevices(PersistentStorageManager.STORAGE_REQUIRED)` and
`getPersistentStorageDevices(1)`).

`file:///required/` is the **own-provider** area (FIG.20 drawing). Scripts
never put `PROVIDER_ID` in the URI. Jumpstart downloads to
`file:///required/` + `PersistentStorageManager.contentId` + filename
(https://learn.microsoft.com/en-us/archive/blogs/amyd/very-simple-network-example).
PREMONITION uses the same concatenation for `VPLST` and `update.txt`.

**Host binding for `contentId`:** DISCID `CONTENT_ID` (16 bytes @44).
PREMONITION names the value `GUID`. Scenarist “Auto-generate” for Content
ID. Expose it as lowercase UUID `8-4-4-4-12` hex (`aabbccdd-eeff-…`).
All-`FF` (10 discs, usually `SEARCH_FLG=1`) is not a usable content
directory. Skip P-storage search.
`[11, 12]` **INFERRED**
(string punctuation; 16 bytes VERIFIED).

**FIG.50 VPLST search (`SEARCH_FLG=0`).** Search
`file:///required/{contentId}/VPLST$$$.XPL` on every connected required
device, then `ADV_OBJ/VPLST$$$.XPL` on disc, then pick the highest `$$$`.
Empty P-storage still boots the disc playlist (106 discs).

**Persistent-storage directory layout (AACS book [4 §6.3]).** The player creates
`/HD_DVD/` on the storage medium with `INFO.TXT` (medium information). Each content
provider gets `/HD_DVD/<PROVIDER_DIR>/`, where `PROVIDER_DIR = AES-G(KDIR,
PROVIDER_ID)` is written as a GUID; `KDIR` is unwrapped from the disc's DKF
([09](09_aacs.md) §9.4). So the folder name is a keyed transform of DISCID
`PROVIDER_ID`, not the ID itself, and isolates one provider's data from another's.
Inside it: `INFO.TXT` (provider information, written by applications), unencapsulated
icon images for the management screen, and one `<CONTENT_ID>` directory per title (GUID
of DISCID `CONTENT_ID`) holding that title's `INFO.TXT` and files such as a downloaded
`VPLST$$$.XPL`. The `[language]-explanation` / `[language]-icon` keys set with
`setProviderInformation(…)` / `setContentInformation(contentId, …)` [14] are what the
applications write into those `INFO.TXT` files; unset → "Unknown Provider" / "Unknown
Content". None of this nesting appears in the script URI `file:///required/{contentId}/`.
`[4]` **SPEC** (AACS mode); 0 on-device directory specimens.

## 5.9 Raster, focus, cues (used path)

This is enough to paint `1408` `menu.xmu` and the OLIVER `archive2` menus.
It is **not** a full XSL-FO engine. Unused iHDstyle attributes stay on the
XSD until a census hits them.
`[11, 12]` **VERIFIED**
`[5]`
`[14]`

**Coordinate space.** Manifest `Region` and playlist Configuration Aperture
are 1920×1080 on 247/247 playlists. `style:x` / `y` / `width` / `height` are
`LengthType` (`-?[0-9]+(px|em|%)`, default `x`/`y` = `0px`, `width`/`height`
= `auto`). Retail buttons use `px`. A box may sit outside the aperture
(`1408` `BT_dummy` at `y="1100px"`). Clip at the aperture; it is still
focusable.

**Position.** XSD: `static` | `relative` | `absolute` | `inherit`, default
`static`. Saved markup: **every** `position` is `absolute` (406/406). For
this sample, place the box at `(x,y)` in the parent’s content box (the
root/`body` is the Region). `static`/`relative` remain untranscribed.

**Anchor.** Default `startBefore`. Used 31 times. XSD 3×3
(`start|center|end` × `Before|Center|After`, plus token `center`; Spec
7.6.3.3.2.1). Same names as XSL-FO area alignment: the named point of the
**border box** sits on `(x,y)`. `writingMode` is unused in the census.
`start` is left, `before` is top. Even `width`/`height` for a `center*`
token: integer-floor toward start/before (do not screenshot-measure).
`[5]` **VERIFIED** (names, default).
Pixel of even `center` **INFERRED** (fail-closed floor).

**Stacking.** `zIndex` default `auto` (used 19). `opacity` default `1.0`
(`AlphaValueType`, 0–1). `display` `auto`|`none` (default `auto`);
`visibility` `hidden` is used to hide whole menu layers (`1408` `menubar` /
`special`). `none` / `hidden` still occupy their nav graph.

**Background.** `backgroundImage` is `URIListType` (a string). Retail form:

```
url('popupMenu.aca/N1_scenes.PNG') url('popupMenu.aca/S1_scenes.PNG') url('popupMenu.aca/A1_scenes.PNG')
```

Split on `url(...)`. `backgroundFrame` (integer, default 0) selects that
index. Jumpstart Chapters + `1408`: frame 0 = normal, 1 = focused, 2 =
actioned. Lists with 17–41 URLs are animation strips; `animate` /
`set` advance the frame (or other style). Resolve each URL relative to the File Cache
(ACA member or `file:///dvddisc/...`). `backgroundColor` default
`transparent` (used 3). `contentWidth`/`contentHeight` (used ~40) size the
image inside the box; default `auto` = box size. `scaling` used once
(`uniform` | `non-uniform`, default `non-uniform`).

**`object`.** Required `@type`. Used values:

| type | Role |
|---|---|
| `application/x-clearrect` | fill the box (usually 1920×1080) with transparent / clear the graphics plane |
| `audio/x-wav` | effect audio; OLIVER sets `display="none"` and `src="chimes.wav"` |

JPEG/PNG as `object` is legal in the XSD and unused here; those assets are
`backgroundImage` on `div`/`button`.

**Composite (graphics over video).** Five presentation planes; main video
is the bottom plane inside the Aperture after `changeLayout` /
`createVideoScale`. Paint the graphics plane **src-over** that scaled
YCbCr: PNG per-pixel alpha × object `opacity` (default 1.0).
`application/x-clearrect` punches alpha 0 in that box (video shows
through). `zOrder` stacks apps on the graphics plane. Cursor sits above
graphics. Unmapped ticks: fill `MainVideoDefaultColor`.
`[2, 3]`
**INFERRED** (fail-closed overlay; not screenshot-measured).
`[11, 12]` **VERIFIED**
(API / object type). `changeLayout` 8-tuple **VERIFIED** (call sites).

**Focus graph.** `button` and `input` are navigable. `navUp` `navDown`
`navLeft` `navRight` (and the four diagonals, used 4 each) are
`NavigationType`: `none` | `inherit` | element `xml:id`. Arrow on the
remote follows that id; `none` does not move. `navIndex` is used twice, both
`1408` debug `<input mode="display" style:navIndex="none">`. `none` = skip
the node in the remote graph. XSD `auto` / `N N` unused.

**`accessKey`.** Used (OLIVER `VK_A_BUTTON`…`VK_D_BUTTON` / `VK_MENU`;
Resident Evil `VK_TOP_MENU` / `VK_MENU`). Token is `AccessKeyType` in iHD.xsd.
That remote key synthesizes `state:actioned` on the element (same path as
Enter on a focused button). It is not a second nav graph.

**`input`.** 113 elements. `@mode`: `multiline` 106 (AACS error text on
CRANK/DEATH_PROOF/PREMONITION `client.aca`; paint `state:value`),
`display` 7 (`1408` debug line, `navIndex="none"`). `password` unused.
Treat used `input` as a styled text run of `state:value`, not a PIN pad.

**Initial focus.** An element may set `state:focused="true"` at parse
(`1408` `BT_dummy`). Otherwise the first navigable in document order.
Exactly one focused node. Moving focus: old node `focused=false`, new
`focused=true`. Enter: `state:actioned=true` while the key is held /
until the action cue ends (Jumpstart: actioned begins the `g` that
dispatches the event). `state:enabled` default `true` (used 1).
`state:value` on `input` (80).

**Cues (page clock, menus).** On each focus/action/timer tick:

1. Evaluate every `cue@begin` / `@end` as either a clock time / duration
   or a path (`PathExpressionType` is an unrestricted `xs:string`; Spec
   7.5.2.4 is unpublished).
2. Implement the **used** path subset only (`e17`):
   `id('ID')[state:focused()=0|1]`,
   `//button[state:actioned()=true()]`, duration, timecode,
   `style:opacity()=1`, `$name` / `$name='…'` after `setXPathVariable`.
   An unknown path is false. The cue does **not** fire. This is not a
   general XPath 1.0 engine.
3. When begin is true and end is false, apply `use` (`defs/g`: `set`
   style/state, `event@name`) and/or child `set`/`event`/`animate`.
4. `1408` action path: `seq begin="//button[state:actioned()=true()]"
   dur="400ms"` then `backgroundFrame=2` for 180ms then
   `event name="runActivatedHandler"`.

**`set` / `animate`.** `set` snaps one style/state for the cue
(`backgroundFrame` 111, `display` 89, `opacity` 40). `animate` (57) puts a
**semicolon list** on a LengthType / AlphaValueType attr (XSD already allows
`;` keyframes) and spreads those N values across the parent `cue@dur`
(`0.25s` / `0.5s` / `800ms` on ARMY_OF_SHADOWS). `calcMode` default `linear`
(interpolates); `discrete` jumps. `additive` default `replace`; `sum` adds to
the current value (subtitle drift). `fill="hold"` (used) keeps the last
keyframe; XSD default `remove`.

**Include.** `include@href` loads another iHD document (`.xmu` fragment,
`.xts` timing-only, `.xss` style fragment) into the parent. Same
namespaces. Not Mozilla XUL (`.xul` on PANS_LABYRINTH is a different
language; ignore for the HDi engine).

**Not in this algorithm:** unused iHDstyle attrs (`writingMode`, padding,
borders, MNG, `pointer` state). Stay on the XSD until a census hits them.

**Text (`<p>`).** 1390/1390 `<p>` are children of a `div` (TERMINATOR_2_GER
`bonus_menu.xmu` and others). The `p` itself has **no** style attributes.
The parent `div` is `position="absolute"` with `x y width height`,
`color`, `fontSize`, `lineHeight`, `font` (File Cache URI, sometimes
without a `.ttf` suffix, e.g. `…/IMAGION_SA`), and often
`display="inherit"` `opacity="inherit"`. Jumpstart: players have **no**
built-in fonts; missing OpenType in File Cache → no glyphs.

Fail-closed raster: scale the OpenType em so `unitsPerEm` maps to
`fontSize` CSS px. Line box height is `lineHeight` (equals `fontSize` on
the checked pages). Successive `<p>` in one tall box (`height="2604px"`)
stack on that stride. Baseline from font `hhea` / `OS/2`. Do not
screenshot-calibrate hinting.
`[11, 12]` **VERIFIED**
(structure).
`[14]` **INFERRED**
(em scale; not screenshot-measured).


