# 12. HDi scripting host ABI (type library)

*Counts written "N/120", "N/119", "on N discs", "listings", or as named discs are over the reference corpus of 120 archived retail HD DVD images [11]. `eNN` are the reproducible verification experiments [12].*


The complete ECMAScript host surface the player exposes to disc scripts, extracted from the **type library binary** `spec/raw/adv_obj/typelib/iHDScripting.tlb` (MSFT OLE type library, `iHDScriptingTypeLib`, carried in `SCENACA.msi` inside `Scenarist_AC_4.5.iso`). This is the authoritative object model behind the used-subset call signatures in [05](05_manifest_hdi.md) §5.3.

`[6]`

**VERIFIED** at name + constant level (`experiments/e20_typelib.py`). The book's
Annex Z [23] defines the same API for version 1.01: every object, member, parameter
and return type, the constant values (§12.2) and the processing steps of each call.
Read Annex Z for behaviour; the type library adds only the members of later
versions (§12.2, last paragraph).

## 12.1 Object model (106 typeinfos)

103 `dispinterface`, 2 `interface`, 1 `coclass`. The host objects a script reaches (`Player`, `Player.playlist`, `application`, `PersistentStorageManager`, `document`, …) are instances of these. Interface list:

`IJSObject` `IJSObjectEx` `IDispatchEx` `IServiceProvider`  
`IDOM2EventTarget` `IJSArray` `IJSFunction` `IJSError`  
`IApplication` `IDynamicAttributes` `IAdvApplication` `IStringArray`  
`ITimer` `IFileIO` `IDirectory` `IFile`  
`ITextStream` `IDiagnostics` `ITrace` `ITraceListener`  
`ITraceListenerCollection` `IController` `IControllerManager` `IDrawing`  
`IColor` `IRectangle` `IPen` `IDrawingArea`  
`IPoint` `IBrush` `IHTTPHeader` `IHTTPClient`  
`INetwork` `IDataCache` `IPersistentStorageMgr` `IPSDevice`  
`ICursorManager` `IPlayer` `IAACS` `ITrackSelection`  
`IBookmark` `ICapabilities` `IAudioCapabilities` `IDecodeCapabilities`  
`IDigitalInterfaceCapabilities` `IVideoCapabilities` `INetworkCapabilities` `IFontCapabilities`  
`IPlaybackCapabilities` `IPlaylist` `ITitle` `IChapter`  
`IAudioTrack` `IVideoTrack` `ISubtitleTrack` `IVideo`  
`IVideoScale` `IMainVideo` `ISubVideo` `ISubtitle`  
`IAudio` `IOutputChannels` `IAudioOutput` `IChannels`  
`IMainAudio` `ISubAudio` `IEffectAudio` `IStandardContentPlayer`  
`ISecondaryVideoPlayer` `IGeneralParameters` `IXML` `IDOM2Implementation`  
`IXMLParser` `IDOM2EventListener` `IDOM2Event` `IDOM2DocumentEvent`  
`IHDCustomizedEvent` `IHDEventProperties` `IDOM2ExceptionFunction` `IDOM2Exception`  
`IEventExceptionFunction` `IEventException` `INodeConstructor` `IEventConstructor`  
`IDocumentEventConstructor` `IMutationEventConstructor` `IDOM2Node` `IDOM2DocumentFragment`  
`IDOM2Document` `IDOM2NodeList` `IDOM2NamedNodeMap` `IDOM2CharacterData`  
`IDOM2Attr` `IDOM2Element` `IDOM2Text` `IDOM2Comment`  
`IDOM2CDATASection` `IDOM2DocumentType` `IDOM2Notation` `IDOM2Entity`  
`IDOM2EntityReference` `IDOM2ProcessingInstruction` `IAnimatableDocument` `IAnimatableProperty`  
`IAnimatableElement` `WinScriptInterpreter`  

## 12.2 Constant catalog

The values are the book's [23 Annex Z]; the names also appear in the type library
[6]. Grouped by the object that declares them. An integer constant is
`unsigned int`; a few are strings. Names the type library has but 1.01 does not
define are listed at the end.

| Object | Constants |
|---|---|
| `Application` (Timer type) | `TIMER_APPLICATION` 1 (application clock), `TIMER_TITLE` 2 (title clock) |
| `AdvancedApplication` | `APPLICATION_PLAYLIST` 1, `APPLICATION_TITLE` 2; state `STATE_ACTIVE` 1, `STATE_INACTIVE` 2, `STATE_INVALID` 3 |
| `FileIO` | mode `FILE_IOMODE_READ` 1, `FILE_IOMODE_WRITE` 2, `FILE_IOMODE_READWRITE` 3; result `SUCCEEDED` 1, `ARGUMENT` 2, `FILE_NOT_FOUND` 3, `NOT_ENOUGH_SPACE` 4, `IO` 5, `NOT_PERMITTED` 6, `FAILED` 7, `DIRECTORY_NOT_FOUND` 8 |
| `Diagnostics` | `TRACE_LEVEL_ERROR` 1, `TRACE_LEVEL_WARNING` 2, `TRACE_LEVEL_INFO` 3 |
| `TraceListenerCollection` | strings: `LISTENER_TYPE_FILE` `"file"`, `LISTENER_TYPE_NETWORK` `"network"`, `LISTENER_TYPE_DEBUGGER` `"debugger"` |
| `Controller` | `OTHER` 0, `REMOTE_CONTROLLER` 1, `KEYBOARD` 2, `MOUSE` 3, `FRONT_PANEL` 4, `GAME_PAD` 5 (the type library spells `KEYBORAD`) |
| `ControllerEvent` | strings: `CONNECT` `"controller_connect"`, `DISCONNECT` `"controller_disconnect"` (Z.5.1; Z.6.2 writes `CONNECTED` `"controller_connected"` / `DISCONNECTED` `"controller_disconnected"`, the book is inconsistent) |
| `ControllerKeyEvent` | strings: `DOWN` `"controller_key_down"`, `UP` `"controller_key_up"`, `CURSOR_MOVE` `"cursor_move"`, `VECTOR` `"controller_key_vector"` |
| `HTTPClient` | state `STATE_UNINITIALIZED` 1, `STATE_LOADING` 2, `STATE_REQUESTPROGRESS` 3, `STATE_REQUESTSENT` 4, `STATE_HEADERRECEIVED` 5, `STATE_RESPONSEPROGRESS` 6, `STATE_COMPLETED` 7, `STATE_ERROR` 8, `STATE_ABORT` 9; `AUTHENTICATION_NONE` 1, `AUTHENTICATION_BASIC` 2, `AUTHENTICATION_DIGEST` 3 |
| `Network` | `HTTP_GET` 1, `HTTP_HEAD` 2, `HTTP_POST` 3, `HTTP_PUT` 4, `HTTP_TRACE` 5, `HTTP_OPTIONS` 6, `HTTP_DELETE` 7 |
| `PersistentStorageManager` | device `STORAGE_ALL` 0, `STORAGE_REQUIRED` 1, `STORAGE_ADDITIONAL` 2, `STORAGE_NETWORK` 3; slot `STATE_SLOT` 1, `STATE_MEDIA_SLOT` 2, `STATE_NON_SLOT` 3; result `SUCCEEDED` 1, `ARGUMENT` 2, `FILE_NOT_FOUND` 3, `NOT_ENOUGH_SPACE` 4 |
| `PersistentStorageEvent` | string: `CHANGE` `"storage_change"` |
| `Player` | aspect `DISPLAY_ASPECT_RATIO_4_3` 1, `DISPLAY_ASPECT_RATIO_16_9` 2, `DISPLAY_ASPECT_RATIO_NOT_SPECIFIED` 3; display `DISPLAY_NONE` 1, `DISPLAY_NORMAL_WIDE` 2, `DISPLAY_PANSCAN` 3, `DISPLAY_LETTERBOX` 4, `DISPLAY_HD` 5; `PARENTAL_NONE` 0, `PARENTAL_1`…`PARENTAL_8` 1…8 (US: 1 G, 3 PG, 4 PG-13, 6 R, 7 NC-17); accessibility bits `ACCESSIBILITY_CLOSED_CAPTION` 1, `…_SIMPLIFIED_CAPTION` 2, `…_LARGE_FONT` 4, `…_CONTRAST_DISPLAY` 8, `…_DESCRIPTIVE_AUDIO` 16, `…_EXTENDED_INTERACTION_TIMES` 32; async result `SUCCEEDED` 1, `ARGUMENT` 2, `FILE_NOT_FOUND` 3, `NOT_ENOUGH_SPACE` 4, `WRONG_FORMAT` 5, `NETWORK_PROBLEM` 6, `FAILED` 7, `FINISHED` 8, `INVALID_CALL` 9 |
| `AudioCapabilities` | `CHANNEL_2` 1, `CHANNEL_5_1` 2, `CHANNEL_7_1` 3 |
| `DecodeCapabilities` | `NOT_SUPPORT` 0, `CHANNEL_2` 1, `CHANNEL_5_1` 2, `CHANNEL_7_1` 3 |
| `DigitalInterfaceCapabilities` | `CODEC_DD` 1, `CODEC_DTS` 2 |
| `VideoCapabilities` | `SD` 1, `HD` 2 |
| `FontCapabilities` | `CLASS_1` 1, `CLASS_2` 2 (optional OpenType tables supported) |
| `Playlist` | `PLAYSTATE_PLAY` 1, `PLAYSTATE_PAUSE` 2, `PLAYSTATE_FAST_FWD` 3, `PLAYSTATE_FAST_REV` 4, `PLAYSTATE_SLOW_FWD` 5, `PLAYSTATE_SLOW_REV` 6 |
| `StandardContentPlayer` | `DOMAIN_TITLE` 1, `DOMAIN_MENU` 2 |
| `SecondaryVideoPlayer` | `PLAYSTATE_PLAY` 1, `PLAYSTATE_PAUSE` 2, `PLAYSTATE_STOP` 3, `PLAYSTATE_SYNC` 4, `PLAYSTATE_INIT` 5, `PLAYSTATE_STREAMING_PRELOAD` 6, `PLAYSTATE_STREAMING_PLAY` 7, `PLAYSTATE_STREAMING_PAUSE` 8 |
| `XMLParser` | encoding `UTF8` 1, `UTF16_BE` 2, `UTF16_LE` 3, `UTF16` 2; status `READY` 1, `PARSING` 2, `WRITING` 4; errors `FILE_NOT_FOUND` 3, `OK` 5, `PARSE_ERR` 6, `FILE_OVERWRITE_ERR` 7, `FILECACHE_ERR` 8, `SERIALIZE_ERR` 9, `FILE_WRITE_ERR` 10 |
| `Event` (DOM 2) | `CAPTURING_PHASE` 1, `AT_TARGET` 2, `BUBBLING_PHASE` 3 |
| `MutationEvent` (DOM 2) | `MODIFICATION` 1, `ADDITION` 2, `REMOVAL` 3 |
| `Node` (DOM 2) | `ELEMENT_NODE` 1 … `NOTATION_NODE` 12 (W3C order) |
| `DOMException` (DOM 2) | `INDEX_SIZE_ERR` 1 … `INVALID_ACCESS_ERR` 15 (W3C order); `EventException.UNSPECIFIED_EVENT_TYPE_ERR` 0 |

**System event types** are string constants on each event object; they are what
`addEventListener` takes [23 Annex Z.6.2]. Every system event bubbles, is
cancelable, cannot be made with `createEvent`, and has a read-only `time` (the
title-timeline time it happened at).

| Event object | Constant = type | Fired when | In trick play | Extra properties |
|---|---|---|---|---|
| `TitleEvent` | `BEGIN` = `"title_begin"`, `END` = `"title_end"` | a title starts (start-up, `onEnd`, API) / just before it ends | fired | `id` |
| `ScheduledEvent` | `EVENT` = `"scheduled_event"` | the timeline reaches a playlist `Event` | not fired | `id` |
| `ChapterEvent` | `CHANGE` = `"chapter"` | the chapter changes (not at the title's end) | fired | `oldValue`, `newValue` |
| `ClipEvent` | `BEGIN` = `"clip_begin"`, `END` = `"clip_end"` | a clip starts / just before it ends (unselected clips too, playlist order) | not fired | `id` |
| `VideoTrackEvent`, `AudioTrackEvent`, `SubtitleTrackEvent` | `CHANGE` = `"video_track"`, `"audio_track"`, `"subtitle_track"` | the track changes by clip change or API | not fired | `oldValue`, `newValue` (NaN when absent) |
| `ApplicationEvent` | `END` = `"application_end"` | just before the timeline leaves the application's valid period | fired | `id` |
| `PlayStateEvent` | `CHANGE` = `"play_state"` | play state changes (API, user, `PauseAt`, title change) | fired | `oldValue`, `newValue` |
| `PlaySpeedEvent` | `CHANGE` = `"play_speed"` | trick-play speed changes | fired | `oldValue`, `newValue` |
| `ControllerEvent` | `CONNECTED` = `"controller_connected"`, `DISCONNECTED` = `"controller_disconnected"` (§Z.5.1 writes `controller_connect` / `controller_disconnect`) | a controller is connected / removed | fired | |
| `PersistentStorageEvent` | `CHANGE` = `"storage_change"` | an additional device is connected / removed | fired | |
| `NetworkTimeoutEvent` | `TIMEOUT` = `"network_timeout"` | a hard-synchronised download passes `NetworkTimeout` | fired | `uri` |
| `ResourceNotFoundEvent` | `NOT_FOUND` = `"resource_not_found"` | a resource or secondary video set is missing or fails to download | | `uri` |
| `StreamingBufferEvent` | `EMPTY` = `"buffer_empty"`, `RESTART` = `"buffer_restart"` | streaming buffer underflow / playback resumes | | `uri`, `time` |
| `NetworkConnectionEvent` | `CONNECTION` = `"network_connection"` | the data-link state changes | | `connect` |
| `StopRequestEvent` | `STOP` = `"stop_request"` | the user or system asks to stop (STOP, EJECT) | fired | |

Events caused by the timeline fire at the start of a tick, in this table's order;
API-caused events fire in call order. A title start fires, in order:
`title_begin` (after Playlist applications load), `chapter` (1), `clip_begin`,
then the track events; a title end: `clip_end`, `application_end`, `title_end`,
`stop_request` [23 §8.3.1]. On disc ([05](05_manifest_hdi.md) §5.3) scripts
listen to `controller_key_down`, `chapter`, `scheduled_event`, `title_begin`,
`title_end`, `play_state`, `audio_track`, `controller_key_up`,
`subtitle_track`, `stop_request`.

**Exceptions** [23 Annex Z.1.3]: `HDDVD_E_ARGUMENT`, `HDDVD_E_ARGUMENTOUTOFRANGE`,
`HDDVD_E_ARGUMENTNULL`, `HDDVD_E_FORMAT`, `HDDVD_E_OVERFLOW`, `HDDVD_E_IO`,
`HDDVD_E_PATHTOOLONG`, `HDDVD_E_FILENOTFOUND`, `HDDVD_E_NOTSUPPORTED`,
`HDDVD_E_INVALIDOPERATION`, `HDDVD_E_UNSPECIFIEDEVENTTYPE`, `HDDVD_E_INVALIDCALL`
(also every restricted API in Restricted Mode), `HDDVD_E_NOTENOUGHSPACE`,
`HDDVD_E_TIMEOUT`, `HDDVD_E_PROTOCOLVIOLATION`, `HDDVD_E_WEB`.

**In the type library but not in 1.01**: `IAACS.INVALIDKEY`, `IPlayer.REGION_1`…
`REGION_8` (no `regionCode` member in 1.01), and the members `aacs`,
`captureWithMAC`, `changeImageSizeWithMAC`. They come from a later version of the
book; no disc in the corpus calls them. The type library's `IHDEventProperties`
names (`BEGIN`, `END`, `CHANGE`, …) are the event-type constants above.

`[23 Annex Z]` **SPEC**; `[6]` names **VERIFIED** (`e20`).

## 12.3 Complete iHD markup surface (XSD)

So a general parser accepts every conforming construct, not only the corpus-used subset ([05](05_manifest_hdi.md) §5.9 covers the *used* attrs; this is the *full* set). The full per-element and per-attribute reference, with types, defaults and meanings, is [14](14_markup.md); the lists below are the v1.0 name sets.

`[5]` **VERIFIED**

**Elements** (`iHD.xsd`, 26): `animate`, `area`, `body`, `br`, `button`, `cue`, `defs`, `div`, `event`, `g`, `head`, `include`, `input`, `link`, `meta`, `object`, `p`, `par`, `param`, `root`, `seq`, `set`, `span`, `style`, `styling`, `timing`

**Structural attributes** (`iHD.xsd`, timing/id/nav core): `ExtendableElement`, `InlineTimingAttributes`, `OutOfLineTimingAttributes`, `accessKey`, `additive`, `begin`, `calcMode`, `class`, `clock`, `clockDivisor`, `condition`, `content`, `coords`, `dur`, `end`, `fill`, `href`, `id`, `mode`, `name`, `select`, `shape`, `src`, `style`, `timeContainer`, `type`, `use`, `value`, `xmlNamespace`

**`ihd#style` attributes** (63): `anchor`, `backgroundColor`, `backgroundFrame`, `backgroundImage`, `backgroundPositionHorizontal`, `backgroundPositionVertical`, `backgroundRepeat`, `blockProgressionDimension`, `border`, `borderAfter`, `borderBefore`, `borderEnd`, `borderStart`, `breakAfter`, `breakBefore`, `color`, `contentHeight`, `contentWidth`, `crop`, `direction`, `display`, `displayAlign`, `endIndent`, `flip`, `font`, `fontSize`, `fontStyle`, `height`, `inlineProgressionDimension`, `lineHeight`, `linefeedTreatment`, `navDown`, `navIndex`, `navLeft`, `navLeftDown`, `navLeftUp`, `navRight`, `navRightDown`, `navRightUp`, `navUp`, `opacity`, `padding`, `paddingAfter`, `paddingBefore`, `paddingEnd`, `paddingStart`, `position`, `scaling`, `startIndent`, `suppressAtLineBreak`, `textAlign`, `textAltitude`, `textDepth`, `textIndent`, `visibility`, `whiteSpaceCollapse`, `whiteSpaceTreatment`, `width`, `wrapOption`, `writingMode`, `x`, `y`, `zIndex`

**`ihd#state` attributes** (6): `actioned`, `enabled`, `focused`, `foreground`, `pointer`, `value`

A parser must accept all of the above; [05](05_manifest_hdi.md) §5.9 marks which are corpus-exercised vs which stay structurally-accepted-but-unused (`writingMode`, `padding*`, `border*`, `direction`, `displayAlign`, `whiteSpace*`, `pointer`, …). Unknown names outside these sets are a non-conforming disc. Fail-closed: ignore the node.


## 12.4 HDi runtime semantics (published standards)

The HDi *behavioural* contract (event dispatch, timing resolution, DOM/exception
model) is in the book [23 §7, §8, Annex Z], which builds on these published
standards and restricts them. HDi is, in Microsoft/Disco's
description, *"a combination of Web-based standards: an HTML-based element grammar,
a CSS/XSL-based attribute grammar, and a SMIL-based element/attribute grammar for
timing, animation, eventing and synchronization, parsed into a DOM that ECMAScript
controls."* The recovered type library proves iHD implements exactly those W3C/ECMA
models. Their **published** semantics are therefore the runtime contract. That
covers the runtime half of gap B1 from open standards; the HDi-specific glue (the
clocks, the scheduler, focus, gestures) is in the book [23 §7.2, §8.3–8.5].
`[15]`
`[6]`

| HDi layer | Published standard the player must implement | Proof in the typelib / XSD |
|---|---|---|
| Markup elements | XHTML-like (`root/body/div/p/span/button/input/object/br/area`) | iHD.xsd, §12.3 |
| Style attributes | CSS + XSL-FO area model (`anchor`, `writingMode`, `padding*`, `border*`, `displayAlign`) | iHDstyle.xsd, §12.3 |
| Timing / animation | **SMIL 2.0** [18] (`begin end dur calcMode additive fill timeContainer`; `par`/`seq`/`cue`/`set`/`animate`) | iHD.xsd timing attrs |
| Eventing | **W3C DOM Level 2 Events** [17] | `IDOM2EventTarget`, `IDOM2Event`, `IDOM2EventListener`, `MutationEvent` |
| Node model | **W3C DOM Level 2 Core** [17] | `IDOM2Node`, `INodeConstructor` |
| Exceptions | **W3C DOM Level 2 exceptions** [17] | `IDOM2Exception`, `IDOM2ExceptionFunction` |
| Script language | **ECMA-327 Compact Profile** [19] (no `with`/`eval`/`substr`) | Jumpstart; §5.3 |

### Event dispatch order (DOM Level 2 Events, verbatim)

`Player`/markup nodes are `EventTarget`s. `addEventListener(type, listener, useCapture)`
registers; `dispatchEvent` runs the standard three-phase flow, and the typelib's
phase constants fix the values:

| Phase | `IDOM2Event` constant | Value | Meaning |
|---|---|---|---|
| capture | `CAPTURING_PHASE` | 1 | root → target, `useCapture=true` listeners |
| target | `AT_TARGET` | 2 | listeners on the target node |
| bubble | `BUBBLING_PHASE` | 3 | target → root, `useCapture=false` listeners |

`preventDefault()` cancels the default action; `stopPropagation()` halts further
phases (`initEvent` sets type/bubbles/cancelable). This is exactly W3C DOM2 Events.
Implement that algorithm. HDi input arrives as controller-key events
(`initControllerKeyEvent`, `IHDEventProperties`) delivered through the same flow;
`accessKey`/Enter synthesise `state:actioned` on the focused target ([05](05_manifest_hdi.md) §5.9).

### DOM Level 2 node types (standard integer values, typelib order matches W3C)

`ELEMENT_NODE`=1, `ATTRIBUTE_NODE`=2, `TEXT_NODE`=3, `CDATA_SECTION_NODE`=4,
`ENTITY_REFERENCE_NODE`=5, `ENTITY_NODE`=6, `PROCESSING_INSTRUCTION_NODE`=7,
`COMMENT_NODE`=8, `DOCUMENT_NODE`=9, `DOCUMENT_TYPE_NODE`=10,
`DOCUMENT_FRAGMENT_NODE`=11, `NOTATION_NODE`=12. **INFERRED** values (W3C DOM2
Core fixes them; typelib lists the names in this canonical order).

### DOM Level 2 exception codes (standard integer values)

`INDEX_SIZE_ERR`=1, `DOMSTRING_SIZE_ERR`=2, `HIERARCHY_REQUEST_ERR`=3,
`WRONG_DOCUMENT_ERR`=4, `INVALID_CHARACTER_ERR`=5, `NO_DATA_ALLOWED_ERR`=6,
`NO_MODIFICATION_ALLOWED_ERR`=7, `NOT_FOUND_ERR`=8, `NOT_SUPPORTED_ERR`=9,
`INUSE_ATTRIBUTE_ERR`=10, `INVALID_STATE_ERR`=11, `SYNTAX_ERR`=12,
`INVALID_MODIFICATION_ERR`=13, `NAMESPACE_ERR`=14, `INVALID_ACCESS_ERR`=15
(+ `UNSPECIFIED_EVENT_TYPE_ERR` for events). **INFERRED** values from W3C DOM2.

### SMIL 2.0 timing resolution (`cue` / `par` / `seq` / `set` / `animate`)

Resolve `begin`/`end`/`dur` and interpolate as the book's SMIL 2.0 subset
[23 §7.7], [18]: `calcMode` (`linear` default | `discrete`; **no** `paced`),
`additive` (`replace` default | `sum`), `fill` (`remove` default | `hold`, page and
application clocks only), and container type (`par` = children share a timebase,
`seq` = children run in order). No `from`/`by`/`to`, `accumulate`,
`animateMotion` or `animateColor`. The simple-duration and active-interval rules
are in [14](14_markup.md) §14.7.

## 12.5 Player object model

Member names from the type library [6]; the book's Annex Z [23] defines the 1.01
members and their behaviour (the table marks typelib-only members). Disc
call-sites are in [05](05_manifest_hdi.md) §5.3.

| Object (interface) | Role | Members |
|---|---|---|
| `Player (IPlayer)` | top-level singleton | `majorVersion`, `minorVersion`, `performanceLevel`, `countryCode`, `displayAspectRatio`, `currentDisplayMode`, `accessibility`, `parentalLevel`, `menuLanguage`, `applicationGroup`, `track`, `bookmark`, `capabilities`, `playlist`, `video`, `audio`, `subtitle`, `secondaryVideoPlayer`, `standardContentPlayer`, `generalParameters`, `createVideoScale(numerator, denominator)`; typelib only: `regionCode`, `aacs` |
| `Player.playlist (IPlaylist)` | playback control | `location`, `titles`, `currentTitle`, `currentChapter`, `playState`, `playSpeed`, `fastForwardSpeed`, `fastReverseSpeed`, `slowForwardSpeed`, `slowReverseSpeed`, `load`, `play`, `pause`, `stop`, `fastForward`, `fastReverse`, `slowForward`, `slowReverse`, `stepForward`, `stepBackward` |
| `...currentTitle (ITitle)` | current title | `elapsedTime`, `chapters`, `videoTracks`, `audioTracks`, `subtitleTracks`, `attributes` (every `Title` attribute as a string), `jump(time, bookmark)` |
| `...chapters[n] (IChapter)` | chapter | `number`, `elapsedTime`, `attributes`, `jump(time, bookmark)`, `top()` |
| `Player.video.main (IMainVideo)` | main video plane | `capturing`, `changing`, `outerFrameColorY`, `outerFrameColorCr`, `outerFrameColorCb`, `x`, `y`, `scale`, `cropX`, `cropY`, `cropHeight`, `cropWidth`, `capture`, `changeImageSize`, `setOuterFrameColor`, `changeLayout(x, y, scale, cropX, cropY, cropWidth, cropHeight, duration)`; typelib only: `captureWithMAC`, `changeImageSizeWithMAC` |
| `application (IApplication)` | app host; its members are also global properties | `FileIO`, `Diagnostics`, `ControllerManager`, `Drawing`, `Network`, `attributes`, `zOrder`, `location`, `advancedApplications`, `thisAdvancedApplication`, `document`, `application`, `coordX`, `coordY` (region position on the canvas), `moveToTop`, `moveToBottom`, `link(uri)`, `setMarkupLoadedHandler(callback)`, `createStringArray(size)`, `createTimer(ticks, type, callback)`, `computeImplicitNav()`, plus `EventTarget` and `DocumentEvent` (`addEventListener`, `createEvent`) |
| `AdvancedApplication` | another application of the title | `id`, `state`, `zOrder`, `type`, `activate()`, `inactivate()`, `moveBefore(app)`, `moveAfter(app)` |
| `PersistentStorageManager (IPersistentStorageMgr)` | P-storage | `contentId`, `getPersistentStorageDevices`, `callManagementMenu`, `saveBasePath` |

**Playback control (`IPlaylist`):** `load(uri)` (replace the playlist: Soft Reset, [10](10_playback.md) §10.2), `play`/`pause`/`stop`, `fastForward(i)`/`fastReverse(i)`/`slowForward(i)`/`slowReverse(i)` (an index into `fastForwardSpeed` etc.), `stepForward()`/`stepBackward()` (Annex V's default handler writes `stepReverse`), `playState` (`PLAYSTATE_*`, §12.2); `currentTitle`/`currentChapter` are live position; `titles[...]`/`.chapters[n]` index by id/number [23 Annex Z.10.12].

**Application states** [23 §8.4]: an application is *Valid* while the title time is
in `[titleTimeBegin, titleTimeEnd)`, *Selected* when its language and group match
the player, *Ready* when `autorun` is true on entering the valid period or
`activate()` was called during it (`inactivate()` clears it), and *Loaded* once its
manifest's resources are in the File Cache and its first script and page are
parsed. It is active (runs script, takes events, draws) only when all four hold.
All script runs on one application thread through a queue of work items ordered
by begin time, then insertion; items past their end time are dropped; long
scripts are never aborted [23 §8.5].

**Restricted Mode** [23 Annex X]: without a trusted signature, network,
persistent-storage and diagnostics APIs throw `HDDVD_E_INVALIDCALL`, URI
arguments are limited to `file:///dvddisc/` and `file:///filecache/`, and the XML
DOM is read-only; constants stay readable.

## 12.6 Cue-predicate grammar (`PathExpressionType`)

iHD.xsd annotates `PathExpressionType` as "Spec 7.5.2.4"; that section of the book
[23] defines it: an **XPath 1.0** subset over the markup DOM with `body` as the
context node, extended with two function namespaces whose functions are the
`ihd#state` / `ihd#style` property names, `GPRM()`, `SPRM()`, `class()`,
`defaultNode()`, the system-parameter variables (§12.7) and `$name` variables set
by `document.setXPathVariable` ([05](05_manifest_hdi.md) §5.3). Full rules in
[14](14_markup.md) §14.8.

Namespaces: `state="http://www.dvdforum.org/2005/ihd#state"`, `style="http://www.dvdforum.org/2005/ihd#style"`.

**Node functions** used on disc besides XPath's own `id()`: `class('c')` (elements whose `class` contains `c`) and `defaultNode()` (the cue's default node, the element its `begin` matched); see [14](14_markup.md) §14.8 for the full list with counts.

**`state:` functions** (one per `ihd#state` attribute [5]): `state:actioned()`, `state:enabled()`, `state:focused()`, `state:foreground()`, `state:pointer()`, `state:value()`.

**`style:` functions** (one per `ihd#style` attribute [5]; used `style:opacity()`): `style:` + any §12.3 style attribute.

With `id('X')`, comparisons (`=0`/`=1`/`=true()`) and `$var` this covers every
observed predicate ([05](05_manifest_hdi.md) §5.9). A path that cannot be evaluated is false (the cue does
not fire). `[23 §7.5.2.4]` **SPEC**; the failure rule **INFERRED**.

## 12.7 XPath variables (system parameters)

Markup paths can read every system parameter as a variable [23 §7.5.2.4.1,
Annex W.2]. Player and capability variables hold their value when the page loaded;
the others are read when the path is evaluated. In Restricted Mode
`networkThroughput` and `streamBufferSize` read 0 and `networkConnection` false.

| Group | Variables |
|---|---|
| Player | `majorVersion`, `minorVersion`, `currentDisplayMode` (1–5, §12.2 display type), `dataCacheSize`, `performanceLevel`, `closedCaption`, `simplifiedCaption`, `largeFont`, `contrastDisplay`, `descriptiveAudio`, `extendedInteractionTimes` |
| Capability | `mainAudioCapabilityLPCM` (1–2), `mainAudioCapabilityDDP`, `mainAudioCapabilityMPEG`, `mainAudioCapabilityDTSHD`, `mainAudioCapabilityMLP` (1–3), `subAudioCapabilityDDP`, `subAudioCapabilityDTSHD` (1), `subAudioCapabilityAACV2`, `subAudioCapabilityMP3`, `subAudioCapabilityWMAPro` (0–1), `enableHDMIOutput`, `audioCapabilityAnalogOutput`, `audioCapabilityHDMI` (1–3 or NaN), `audioCapabilitySPDIF` (1–2 or NaN), `spdifCapabilityEncoded`, `spdifCapabilityDirectOutputOfDD`, `spdifCapabilityDirectOutputOfDTS`, `subVideoResolution` (1–2), `networkConnection`, `networkThroughput` (kbit/s), `supportedOpenTypeFontTables`, `supportOfSlowForward`, `supportOfSlowReverse`, `supportOfStepForward`, `supportOfStepReverse` |
| Presentation | `playlistLocation`, `titleId`, `titleNumber`, `timeOnTitleTime`, `playState` (1–6), `playSpeed`, `playStateOfSecondaryVideoPlayer`, `elapsedTimeOfSecondaryVideoPlayer`, `currentVideoTrackNumber`, `currentAudioTrackNumber`, `currentSubtitleTrackNumber`, `selectedVideoTrackNumber`, `selectedAudioTrackNumber`, `selectedSubtitleTrackNumber`, `selectedAudioLanguageCode`, `selectedAudioLanguageCodeExtension`, `selectedSubtitleLanguageCode`, `selectedSubtitleLanguageCodeExtension`, `selectedApplicationGroup`, `effectAudioPlaying`, `streamBufferSize` |
| Audio (0–255) | `mainAudioVolumeTo{Left,Right,Center,LeftS,RightS,LeftB,RightB,Lfe}`; `subAudioLeftChannelGainTo…`, `subAudioRightChannelGainTo…`, `effectAudioLeftChannelGainTo…`, `effectAudioRightChannelGainTo…` with the same eight outputs |
| Layout | `mainVideoOuterFrameColorY` (16–235), `mainVideoOuterFrameColorCr`, `mainVideoOuterFrameColorCb` (16–240), `mainVideoChanging`, `mainVideoCapturing`, `mainVideoX`, `mainVideoY`, `mainVideoScaleNumerator`, `mainVideoScaleDenominator` (1–16), `mainVideoCropX`, `mainVideoCropY`, `mainVideoCropWidth`, `mainVideoCropHeight`, `subVideoX`, `subVideoY`, `subVideoScaleNumerator`, `subVideoScaleDenominator`, `subVideoCropX`, `subVideoCropY`, `subVideoCropWidth`, `subVideoCropHeight`, `subVideoChanging`, `subVideoAlpha` (0–255), `subtitleVisibility` |
| Cursor | `cursorX`, `cursorY`, `cursorImage`, `cursorHotSpotX`, `cursorHotSpotY`, `cursorRegionX`, `cursorRegionY`, `cursorRegionWidth`, `cursorRegionHeight`, `cursorEnable`, `cursorVisible` |

Initial values and what Soft Reset and a title change reset are in [23 Annex W]:
for example the current track numbers reset on Soft Reset but survive a title
change, the selected ones survive both, the selected languages start from SPRM
16–19, and the video layout resets at every title while the outer-frame colour
does not. Menu language, country and parental level are SPRM 0, 12 and 13.

## 12.8 Virtual keys and the default input handler

Key events reach script first; what script does not consume goes to markup
(`accessKey`, arrows, Enter, ESC); what markup does not consume runs the default
handler [23 §4.3.17, Annex V]. M = the player must have the key.

| Key | Value | M | Default action |
|---|---|---|---|
| `VK_PLAY` | `0xFA` | M | `Player.playlist.play()` |
| `VK_PAUSE` | `0xB3` | M | toggle play / pause |
| `VK_FF`, `VK_FR` | `0xC1`, `0xC2` | M | next fast forward / reverse speed |
| `VK_SF`, `VK_SR` | `0xC3`, `0xC4` | | next slow speed, if supported |
| `VK_STEP_NEXT`, `VK_STEP_PREV` | `0xC5`, `0xC6` | | step, if supported |
| `VK_SKIP_NEXT` | `0xC7` | M | next chapter; at the last chapter the `onEnd` title, else stop |
| `VK_SKIP_PREV` | `0xC8` | M | `currentChapter.top()` |
| `VK_SUBTITLE_SWITCH` | `0xC9` | M | toggle `Player.subtitle.visible` |
| `VK_SUBTITLE` | `0xCA` | M | next selectable subtitle track (skipping closed captions if `VK_CC` exists) |
| `VK_CC` | `0xCB` | | next closed-caption track (extension `05`–`07`) |
| `VK_ANGLE` | `0xCC` | M | next selectable video track |
| `VK_AUDIO` | `0xCD` | M | next selectable audio track |
| `VK_MENU`, `VK_TOP_MENU`, `VK_BACK`, `VK_RESUME` | `0xCE`, `0xCF`, `0xD0`, `0xD1` | M | none (for applications) |
| `VK_LEFT`, `VK_UP`, `VK_RIGHT`, `VK_DOWN` | `0x25`–`0x28` | M | markup navigation |
| `VK_LEFTUP`, `VK_RIGHTUP`, `VK_LEFTDOWN`, `VK_RIGHTDOWN` | `0x29`–`0x2C` | M | markup navigation |
| `VK_TAB` | `0x09` | | markup |
| `VK_A_BUTTON`…`VK_D_BUTTON` | `0x70`–`0x73` | M | none |
| `VK_E_BUTTON`…`VK_L_BUTTON` | `0x74`–`0x7B` | | none |
| `VK_ENTER` | `0x0D` | M | markup Activate |
| `VK_ESC` | `0x1B` | | markup Cancel |
| `VK_0`…`VK_9` | `0x30`–`0x39` | M | none |
| `VK_MOUSE_1` | `0x01` | M | markup Activate (on key up) |
| `VK_MOUSE_2`…`VK_MOUSE_5` | `0x02`, `0x04`, `0x05`, `0x06` | | none |
| `VK_VECTOR_1`…`VK_VECTOR_4` | `0x97`–`0x9A` | | analog input |

The track keys walk `Player.playlist.currentTitle.{video,audio,subtitle}Tracks`
from the current track, wrapping, and pick the next `selectable` one; a title
without a `TrackNavigationList` does not change track.

`[23 Annex V, Annex W]` **SPEC**

### Remaining items

Earlier versions of this sheet reconstructed the clocks, the cue grammar and the
object semantics from Jumpstart, the patents and the XSDs, and listed the DVD
Forum book as the missing source. The book [23] now confirms or replaces each
reconstruction (§12.2–12.8, [05](05_manifest_hdi.md), [14](14_markup.md)). What
the book does not fix is behaviour no disc exercises at pixel or tick precision,
and members added after version 1.01.
