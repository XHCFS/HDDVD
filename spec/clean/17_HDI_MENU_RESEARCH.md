# 17. HDi menu research — method and results

Offline census of saved Advanced Content against the v1.0 XSDs, the
name-only typelib, Jumpstart, Scenarist AC 4.5, and patents. Disc wins.
Library work: `spec/advanced/05` §5.0 is **met**. C is a separate step.

`[SRC: CORPUS | e15 e17 | 2026-09-08]`

## Method (do not skip a layer)

1. **Inventory.** List every `ADV_OBJ` file on 120 discs (`_listing.txt`).
   Save ACA ≤ 320 KiB (`tools/pull_hdi_sample.py`). Compare saved size to
   listing size; skip 0-byte pulls.
2. **Allowlist.** Parse `iHD.xsd` / `iHDstyle.xsd` / `iHDstate.xsd` for
   element and attribute local-names. A used name not in the XSD is a
   spec bug, not a new dialect.
3. **Extract.** ACA directory `14+(flags&0xFF)+32` (`e11`). Member payload
   by offset/length even when `flags` high byte is `0xff`.
4. **Markup census.** Every saved `.xmu` (loose + ACA): elements, style,
   state, `timing@clock`, `cue` begin/end kinds, `position`,
   `backgroundImage` `url()` arity, `include@href`.
5. **Script census.** Every saved `.js`: encoding, `file:///` roots,
   `Player.*` paths, typelib name hits, `jump`/`load` call shape.
6. **Playlist cross-check.** `ApplicationResource@size` vs listing;
   `@priority`; `@multiplexed`.
7. **Public prose.** Jumpstart (Hello World, Chapters, Persistent Storage,
   Xbox `0xC667000A`) and Scenarist AC 4.5 File Cache graph. Disc XML/JS
   wins when they disagree.
8. **Patents.** FIG.50 / FIG.51 / FIG.20 / TABLE 91. Record drawing vs
   body. Do not close a gate item on patent-only text.
9. **Pack dump.** `e16` HTTP-ranges a small muxed EVO for ADV_PCK `0x80`.
   The ACA that would be muxed can be read as a file (`OLIVER_TWIST_JPN`
   `archive2.aca`) but that does not prove pack layout.

Falsifiers are in `experiments/e15_hdi_menu_census.py` and
`experiments/e17_hdi_deep_census.py`.

## Sample (this run)

| Item | N |
|---|---|
| Listed `.ACA` | 409 |
| Saved complete ACA (size = listing) | 97 (every listed ACA ≤ 320 KiB) |
| ACA members | 885 |
| Saved `.js` | 122, all UTF-16BE BOM `FE FF` |
| Saved `.xmu` | 84 |
| Saved `.xmf` | 89 |

Member extensions: `png` 585, `js` 119, `xmf` 86, `xmu` 82, `ttf` 7,
`xas` 2, `xts` 2, `xul` 2 (`e17`).

**ACA directory.** namelen 0 / `>64` / `/` = **0/885**. Formula holds.
`flags` high byte `0xff` on 868/885 (AACS-wrapped CRC); `2`–`7` on the
rest (STALINGRAD-style, raw CRC).
`[SRC: DISC | e17]` **VERIFIED**

## Markup (used subset)

Elements (`e15`): `p` **1390**, `div` 1339, `cue` 1015, `event` 499,
`button` 492, `param` 365, `meta` 329, `set` 263, `par` 176, `input` 113,
`object` 7. Unknown elements: 0.

`<p>` is always a child of `div` and carries **no** style attributes. The
parent supplies `font` / `fontSize` / `lineHeight` / `color`. The first
50-ACA cut had `p=0` because those text archives were not pulled yet —
do not repeat that claim.

`timing@clock`: `page` 66, `application` 9, `title` 3, omitted 6.

`style:position`: **1462/1462 `absolute`**.

Cue `begin`/`end` kinds (`e17`): XPath `state:focused` 681,
`state:actioned` 268, duration 173, timecode 69, other 35.
Other includes `setXPathVariable` names (`$sw01`, `$selectedSubtitleTrackNumber`)
and `style:opacity()=1` (CRANK `main_menu.xmu`).

`backgroundImage` `url()` arity: 1 (901), 2 (316), 3 (57), 17 (72), plus
4/5/16/20/41. `backgroundFrame` 114.

`object@type` used: `application/x-clearrect` (full-aperture wipe,
MATRIX/BONNIE `cards.xmu`), `audio/x-wav` (OLIVER menus, `display="none"`,
`src="chimes.wav"`). Both are enumerations in iHD.xsd. JPEG/PNG/MNG
`object` unused — those assets are `div`/`button` `backgroundImage`.

`include@href` (36): other `.xmu` fragments, `.xts` (timing-only iHD
documents, STALINGRAD/HOT_FUZZ `mainApp.xts`), `.xss` (style fragments
on discs whose archives were larger than the 320 KiB pull). Same
namespaces.

`.xas` (HOT_FUZZ / ARMY_OF_SHADOWS `advsubs.xas`): empty iHD
root/head/body — Advanced Subtitle stub. `.xul` (PANS_LABYRINTH
`Menubar.xul`): Mozilla XUL (`chrome://global/skin/`), **not** iHD.
Out of the HDi markup engine.

## Script

URI roots in JS: `dvddisc` 218, `required` 8, `filecache` 4. Never
`fixed` / `removable`. PREMONITION:

```
var psUrl = "file:///required/" + PersistentStorageManager.contentId + "/";
Player.playlist.load(psUrl + playlist);
```

`jump(..., false)` 258/258 call sites (`e15`). `IPlaylist.load` 27 sites.

`Player.*` (top): `playlist.currentChapter.number`,
`generalParameters.setValue`, `playlist.titles` / `.play` / `.load`,
`video.main.changeLayout`, `createVideoScale`, `subtitle.visible`,
`track.select*`, `elapsedTime`.

Typelib names actually appearing: `addEventListener`, `createTimer`,
`jump`, `load`, `setXPathVariable`, `getElementById`, `setProperty`,
`setMarkupLoadedHandler`, … Names without types remain a host-binding
problem; the **call shape** of the menu-critical ones is in sheet 05.

## File Cache

`ApplicationResource` / `PlaylistApplicationResource` `@size` vs listing
(`e15`, `file:///dvddisc/`): 532 equal, 2428 larger, **1 smaller**
(PANS_LABYRINTH `multi_angle.aca` 5500 vs 6436), 0 unlisted.

Jumpstart: size may be larger, must not be smaller. Xbox `0xC667000A`
`XPLAYER_E_CANT_LOAD_RESOURCE` if missing or too small.

`@priority`: 1 on 2440, omitted 455, 2 on 32, 3 on 34. Scenarist: higher
Buffer Flush Priority is removed first when the 64 MB buffer is full;
0 is last. That is an **authoring** rule mapped to `@priority`. Player
behaviour if a title’s live set exceeds 64 MB is fail-closed skip (A41,
sheet 05 §5.7).

FIG.50 step 5: Change System Configuration **withdraws** File Cache and
Streaming Buffer (boot after highest `VPLST`). FIG.51 **body**: wipe then
reload on `IPlaylist.load` (A37 closed fail-closed). Drawing vs body recorded
in `16_PATENT_FIGURES.md`.

## Persistent storage (two layers)

| Layer | Evidence | Status |
|---|---|---|
| Script URI | PREMONITION + Jumpstart “Very Simple Network”; FIG.20 **drawing** `file:///required/` | specified |
| Management UI folders | Jumpstart: content-ID folder **nested under** provider-ID folder; `[language]-explanation` labels | specified as nesting, not bytes |
| FIG.50 VPLST search | `file:///required/{contentId}/VPLST$$$.XPL` then disc `ADV_OBJ` | specified INFERRED (sheet 05 §5.8) |

## ADV_PCK

Specimen: `STALINGRAD` `/HVDVD_TS/logo.EVO` (`e16`, 2383 packs, slots 1–6).
First packet: slot + ACA filename + 225 zero ADDTHD + `HDDVDACA`. Middle/last:
4-byte prefix then ACA. Concat equals `/ADV_OBJ/<name>.aca`. OLIVER
`JpnTokuhou.EVO` / `LoopMenu.EVO` have **0** packs; load the ACA file anyway.
`archive2.aca` members remain as in the file census.

## What still blocks §5.0

Nothing in this census. §5.0 is **met**. Fail-closed leftovers that are now
**in the sheets** (do not reopen without a disc contradiction): `jump`
pause-at-destination, used cue-path allowlist, OpenType em scale, `anchor`
FO names, src-over, ADV_PCK `HDDVDACA` locator, `changeLayout` 8-tuple,
`createTimer` type+`ITimer`, `animate` keyframes, `input` mode, `accessKey`
VK_*, `sync` hard/soft, `multiplexed="0"` as URI. Unused XSD attrs and
firmware vs FIG.50 stay out / uncloseable.
