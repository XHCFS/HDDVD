# 12. HDi scripting host ABI (type library)

*Counts written "N/120", "N/119", "on N discs", "listings", or as named discs are over the reference corpus of 120 archived retail HD DVD images [11]. `eNN` are the reproducible verification experiments [12].*


The complete ECMAScript host surface the player exposes to disc scripts, extracted from the **type library binary** `spec/raw/adv_obj/typelib/iHDScripting.tlb` (MSFT OLE type library, `iHDScriptingTypeLib`, carried in `SCENACA.msi` inside `Scenarist_AC_4.5.iso`). This is the authoritative object model behind the used-subset call signatures in [05](05_manifest_hdi.md) §5.3.

`[6]`

**VERIFIED** at name + constant level (`experiments/e20_typelib.py`). Full parameter/return IDL is recoverable by loading the saved `.tlb` in a Windows type-library viewer (`oleview.exe` / `tlbimp` / `comtypes`); the binary is in the repo. That last step is the remaining part of gap B2 ([11](11_gaps.md)).

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

## 12.2 Constant catalog (200 constants)

Grouped by the interface that declares them. These are the literal values disc ECMAScript passes and compares. Names verified present in the `.tlb`; values (small sequential integers, DVD/AACS convention) need the IDL viewer step.

**IApplication:** `TIMER_APPLICATION`, `TIMER_TITLE`

**IAdvApplication:** `APPLICATION_PLAYLIST`, `APPLICATION_TITLE`, `STATE_ACTIVE`, `STATE_INACTIVE`, `STATE_INVALID`

**IFileIO:** `FILE_IOMODE_READ`, `FILE_IOMODE_WRITE`, `FILE_IOMODE_READWRITE`, `SUCCEEDED`, `FAILED`, `FILE_NOT_FOUND`, `NOT_PERMITTED`, `DIRECTORY_NOT_FOUND`, `ARGUMENT`, `NOT_ENOUGH_SPACE`

**IDiagnostics:** `TRACE_LEVEL_ERROR`, `TRACE_LEVEL_WARNING`, `TRACE_LEVEL_INFO`

**ITraceListenerCollection:** `LISTENER_TYPE_FILE`, `LISTENER_TYPE_NETWORK`, `LISTENER_TYPE_DEBUGGER`

**IController:** `OTHER`, `REMOTE_CONTROLLER`, `KEYBORAD`, `MOUSE`, `FRONT_PANEL`, `GAME_PAD`

**IHTTPClient:** `STATE_UNINITIALIZED`, `STATE_LOADING`, `STATE_REQUESTPROGRESS`, `STATE_REQUESTSENT`, `STATE_HEADERRECEIVED`, `STATE_RESPONSEPROGRESS`, `STATE_COMPLETED`, `STATE_ERROR`, `STATE_ABORT`, `AUTHENTICATION_NONE`, `AUTHENTICATION_BASIC`, `AUTHENTICATION_DIGEST`

**INetwork:** `HTTP_GET`, `HTTP_HEAD`, `HTTP_POST`, `HTTP_PUT`, `HTTP_TRACE`, `HTTP_OPTIONS`, `HTTP_DELETE`

**IPersistentStorageMgr:** `STORAGE_ALL`, `STORAGE_REQUIRED`, `STORAGE_ADDITIONAL`, `STORAGE_NETWORK`, `STATE_SLOT`, `STATE_MEDIA_SLOT`, `STATE_NON_SLOT`, `SUCCEEDED`, `FILE_NOT_FOUND`, `ARGUMENT`, `NOT_ENOUGH_SPACE`

**IPlayer:** `DISPLAY_ASPECT_RATIO_4_3`, `DISPLAY_ASPECT_RATIO_16_9`, `DISPLAY_ASPECT_RATIO_NOT_SPECIFIED`, `DISPLAY_NONE`, `DISPLAY_NORMAL_WIDE`, `DISPLAY_PANSCAN`, `DISPLAY_LETTERBOX`, `DISPLAY_HD`, `REGION_1`, `REGION_2`, `REGION_3`, `REGION_4`, `REGION_5`, `REGION_6`, `REGION_7`, `REGION_8`, `PARENTAL_NONE`, `PARENTAL_1`, `PARENTAL_2`, `PARENTAL_3`, `PARENTAL_4`, `PARENTAL_5`, `PARENTAL_6`, `PARENTAL_7`, `PARENTAL_8`, `ACCESSIBILITY_CLOSED_CAPTION`, `ACCESSIBILITY_SIMPLIFIED_CAPTION`, `ACCESSIBILITY_LARGE_FONT`, `ACCESSIBILITY_CONTRAST_DISPLAY`, `ACCESSIBILITY_DESCRIPTIVE_AUDIO`, `ACCESSIBILITY_EXTENDED_INTERACTION_TIMES`, `SUCCEEDED`, `FINISHED`, `FAILED`, `FILE_NOT_FOUND`, `NOT_ENOUGH_SPACE`, `WRONG_FORMAT`, `ARGUMENT`, `NETWORK_PROBLEM`, `INVALID_CALL`

**IAACS:** `INVALIDKEY`

**IAudioCapabilities:** `CHANNEL_2`, `CHANNEL_5_1`, `CHANNEL_7_1`

**IDecodeCapabilities:** `NOT_SUPPORT`, `CHANNEL_2`, `CHANNEL_5_1`, `CHANNEL_7_1`

**IDigitalInterfaceCapabilities:** `CODEC_DD`, `CODEC_DTS`

**IFontCapabilities:** `CLASS_1`, `CLASS_2`

**IPlaylist:** `PLAYSTATE_PLAY`, `PLAYSTATE_PAUSE`, `PLAYSTATE_FAST_FWD`, `PLAYSTATE_FAST_REV`, `PLAYSTATE_SLOW_FWD`, `PLAYSTATE_SLOW_REV`

**IStandardContentPlayer:** `DOMAIN_TITLE`, `DOMAIN_MENU`

**ISecondaryVideoPlayer:** `PLAYSTATE_INIT`, `PLAYSTATE_PLAY`, `PLAYSTATE_PAUSE`, `PLAYSTATE_STOP`, `PLAYSTATE_SYNC`, `PLAYSTATE_STREAMING_PRELOAD`, `PLAYSTATE_STREAMING_PLAY`, `PLAYSTATE_STREAMING_PAUSE`

**IXMLParser:** `UTF8`, `UTF16_BE`, `UTF16_LE`, `UTF16`, `READY`, `PARSING`, `WRITING`, `PARSE_ERR`, `FILE_NOT_FOUND`, `FILE_OVERWRITE_ERR`, `FILECACHE_ERR`, `SERIALIZE_ERR`, `FILE_WRITE_ERR`

**IDOM2Event:** `CAPTURING_PHASE`, `AT_TARGET`, `BUBBLING_PHASE`

**IHDEventProperties:** `BEGIN`, `END`, `CHANGE`, `DISCONNECTED`, `NOT_FOUND`, `EMPTY`, `RESTART`, `CONNECTION`, `DOWN`, `CURSOR_MOVE`, `VECTOR`

**IDOM2ExceptionFunction:** `INDEX_SIZE_ERR`, `DOMSTRING_SIZE_ERR`, `HIERARCHY_REQUEST_ERR`, `WRONG_DOCUMENT_ERR`, `INVALID_CHARACTER_ERR`, `NO_DATA_ALLOWED_ERR`, `NO_MODIFICATION_ALLOWED_ERR`, `NOT_FOUND_ERR`, `NOT_SUPPORTED_ERR`, `INUSE_ATTRIBUTE_ERR`, `INVALID_STATE_ERR`, `SYNTAX_ERR`, `INVALID_MODIFICATION_ERR`, `NAMESPACE_ERR`, `INVALID_ACCESS_ERR`

**IEventExceptionFunction:** `UNSPECIFIED_EVENT_TYPE_ERR`

**INodeConstructor:** `ELEMENT_NODE`, `ATTRIBUTE_NODE`, `TEXT_NODE`, `CDATA_SECTION_NODE`, `ENTITY_REFERENCE_NODE`, `ENTITY_NODE`, `PROCESSING_INSTRUCTION_NODE`, `COMMENT_NODE`, `DOCUMENT_NODE`, `DOCUMENT_TYPE_NODE`, `DOCUMENT_FRAGMENT_NODE`, `NOTATION_NODE`

**IEventConstructor:** `CAPTURING_PHASE`, `AT_TARGET`, `BUBBLING_PHASE`

**IMutationEventConstructor:** `MODIFICATION`, `ADDITION`, `REMOVAL`

**IDOM2Node:** `ELEMENT_NODE`, `ATTRIBUTE_NODE`, `TEXT_NODE`, `CDATA_SECTION_NODE`, `ENTITY_REFERENCE_NODE`, `ENTITY_NODE`, `PROCESSING_INSTRUCTION_NODE`, `COMMENT_NODE`, `DOCUMENT_NODE`, `DOCUMENT_TYPE_NODE`, `DOCUMENT_FRAGMENT_NODE`, `NOTATION_NODE`

## 12.3 Complete iHD markup surface (XSD)

So a general parser accepts every conforming construct, not only the corpus-used subset ([05](05_manifest_hdi.md) §5.9 covers the *used* attrs; this is the *full* set). Authoritative source: the v1.0 schemas.

`[5]` **VERIFIED**

**Elements** (`iHD.xsd`, 26): `animate`, `area`, `body`, `br`, `button`, `cue`, `defs`, `div`, `event`, `g`, `head`, `include`, `input`, `link`, `meta`, `object`, `p`, `par`, `param`, `root`, `seq`, `set`, `span`, `style`, `styling`, `timing`

**Structural attributes** (`iHD.xsd`, timing/id/nav core): `ExtendableElement`, `InlineTimingAttributes`, `OutOfLineTimingAttributes`, `accessKey`, `additive`, `begin`, `calcMode`, `class`, `clock`, `clockDivisor`, `condition`, `content`, `coords`, `dur`, `end`, `fill`, `href`, `id`, `mode`, `name`, `select`, `shape`, `src`, `style`, `timeContainer`, `type`, `use`, `value`, `xmlNamespace`

**`ihd#style` attributes** (63): `anchor`, `backgroundColor`, `backgroundFrame`, `backgroundImage`, `backgroundPositionHorizontal`, `backgroundPositionVertical`, `backgroundRepeat`, `blockProgressionDimension`, `border`, `borderAfter`, `borderBefore`, `borderEnd`, `borderStart`, `breakAfter`, `breakBefore`, `color`, `contentHeight`, `contentWidth`, `crop`, `direction`, `display`, `displayAlign`, `endIndent`, `flip`, `font`, `fontSize`, `fontStyle`, `height`, `inlineProgressionDimension`, `lineHeight`, `linefeedTreatment`, `navDown`, `navIndex`, `navLeft`, `navLeftDown`, `navLeftUp`, `navRight`, `navRightDown`, `navRightUp`, `navUp`, `opacity`, `padding`, `paddingAfter`, `paddingBefore`, `paddingEnd`, `paddingStart`, `position`, `scaling`, `startIndent`, `suppressAtLineBreak`, `textAlign`, `textAltitude`, `textDepth`, `textIndent`, `visibility`, `whiteSpaceCollapse`, `whiteSpaceTreatment`, `width`, `wrapOption`, `writingMode`, `x`, `y`, `zIndex`

**`ihd#state` attributes** (6): `actioned`, `enabled`, `focused`, `foreground`, `pointer`, `value`

A parser must accept all of the above; [05](05_manifest_hdi.md) §5.9 marks which are corpus-exercised vs which stay structurally-accepted-but-unused (`writingMode`, `padding*`, `border*`, `direction`, `displayAlign`, `whiteSpace*`, `pointer`, …). Unknown names outside these sets are a non-conforming disc. Fail-closed: ignore the node.


## 12.4 HDi runtime semantics (published standards)

The HDi *behavioural* contract (event dispatch, timing resolution, DOM/exception
model) is not unpublished proprietary behaviour. HDi is, in Microsoft/Disco's
description, *"a combination of Web-based standards: an HTML-based element grammar,
a CSS/XSL-based attribute grammar, and a SMIL-based element/attribute grammar for
timing, animation, eventing and synchronization, parsed into a DOM that ECMAScript
controls."* The recovered type library proves iHD implements exactly those W3C/ECMA
models. Their **published** semantics are therefore the runtime contract. That
covers the runtime half of gap B1 from open standards. Only HDi-specific glue (the
disc clock model, §5.2/§5.9) rests on the unpublished book.
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
`accessKey`/Enter synthesise `state:actioned` on the focused target (§5.9).

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

Resolve `begin`/`end`/`dur` and interpolate exactly as SMIL 2.0 [18]:
`calcMode` (`linear` default | `discrete` | `paced`), `additive` (`replace`
default | `sum`), `fill` (`remove` default | `hold`), and container type
(`par` = children share a timebase, `seq` = children run in order). §5.9 gives the
corpus-used cue-path predicates over this model; the *timing algebra itself* is
SMIL 2.0. A conforming keyframe list a future disc uses that the corpus does not is
still resolved by the SMIL rules, not by a guess.

## 12.5 Player object model (from the type library)

Member **names** of the script host graph and its control surface are the type library [6]. Semantics of the members discs call are [14] plus disc call-sites ([05](05_manifest_hdi.md) §5.3). The whole surface is enumerable, not just corpus-used calls.

| Object (interface) | Role | Members |
|---|---|---|
| `Player (IPlayer)` | top-level singleton | `majorVersion`, `minorVersion`, `performanceLevel`, `countryCode`, `displayAspectRatio`, `currentDisplayMode`, `regionCode`, `accessibility`, `parentalLevel`, `track`, `bookmark`, `capabilities`, `playlist`, `video`, `audio`, `subtitle`, `secondaryVideoPlayer`, `standardContentPlayer`, `generalParameters`, `aacs`, `menuLanguage`, `applicationGroup`, `createVideoScale` |
| `Player.playlist (IPlaylist)` | playback control | `location`, `titles`, `currentTitle`, `currentChapter`, `playState`, `playSpeed`, `fastForwardSpeed`, `fastReverseSpeed`, `slowForwardSpeed`, `slowReverseSpeed`, `load`, `play`, `pause`, `stop`, `fastForward`, `fastReverse`, `slowForward`, `slowReverse`, `stepForward`, `stepBackward` |
| `...currentTitle (ITitle)` | current title | `elapsedTime`, `chapters`, `videoTracks`, `audioTracks`, `subtitleTracks`, `attributes`, `jump` |
| `...chapters[n] (IChapter)` | chapter | `number`, `elapsedTime`, `attributes`, `jump`, `top` |
| `Player.video.main (IMainVideo)` | main video plane | `capturing`, `changing`, `outerFrameColorY`, `outerFrameColorCr`, `outerFrameColorCb`, `x`, `y`, `scale`, `cropX`, `cropY`, `cropHeight`, `cropWidth`, `capture`, `captureWithMAC`, `changeImageSize`, `changeImageSizeWithMAC`, `setOuterFrameColor`, `changeLayout` |
| `application (IApplication)` | app host | `FileIO`, `Diagnostics`, `ControllerManager`, `Drawing`, `Network`, `attributes`, `zOrder`, `location`, `advancedApplications`, `thisAdvancedApplication`, `document`, `application`, `coordX`, `coordY`, `moveToTop`, `moveToBottom`, `link`, `setMarkupLoadedHandler`, `createStringArray`, `createTimer`, `createEvent`, `computeImplicitNav` |
| `PersistentStorageManager (IPersistentStorageMgr)` | P-storage | `contentId`, `getPersistentStorageDevices`, `callManagementMenu`, `saveBasePath` |

**Playback control (`IPlaylist`):** `load` (replace playlist, FIG.51 soft reset [1]), `play`/`pause`/`stop`, `fastForward`/`fastReverse`/`slowForward`/`slowReverse` (+ `*Speed`), `stepForward`/`stepBackward`, `playState` (`PLAYSTATE_*`, §12.2); `currentTitle`/`currentChapter` are live position; `titles[...]`/`.chapters[n]` index by id/number [14]. Trick-play verbs are the published surface even where no corpus disc scripts them.

## 12.6 Cue-predicate grammar (`PathExpressionType`)

iHD.xsd annotates `PathExpressionType` only as "Spec 7.5.2.4" (unpublished book), but the grammar is closeable: **XPath 1.0** boolean/node-set over the markup DOM, extended with two function namespaces whose functions are exactly the `ihd#state` / `ihd#style` attribute local-names [5], plus `$name` vars (`document.setXPathVariable`, §5.3) and time/duration literals.

Namespaces: `state="http://www.dvdforum.org/2005/ihd#state"`, `style="http://www.dvdforum.org/2005/ihd#style"`.

**`state:` functions** (one per `ihd#state` attribute [5]): `state:actioned()`, `state:enabled()`, `state:focused()`, `state:foreground()`, `state:pointer()`, `state:value()`.

**`style:` functions** (one per `ihd#style` attribute [5]; used `style:opacity()`): `style:` + any §12.3 style attribute.

With `id('X')`, comparisons (`=0`/`=1`/`=true()`), `$var`, and time literals (`HH:MM:SS:FF`, `NNms`) this covers every observed predicate (§5.9) and any conforming one a future disc forms. The function set is enumerated, not sampled. Unknown/ill-typed path evaluates to boolean false (the cue does not fire). **INFERRED** (XPath 1.0 + enumerated extension functions).

### Remaining items after §12.5 / §12.6 / §5.2

The three items once attributed to the unpublished book are specified from public
sources:

- **The three clocks** (page / title / application) and their media-clock and
  `sync` relation, from Microsoft HDi Jumpstart [14] and the patent [1]
  ([05](05_manifest_hdi.md) §5.2).
- **The cue-path predicate grammar**, as XPath 1.0 plus the enumerated
  `state:` / `style:` extension functions and `$vars` (§12.6), from the XSDs [5].
- **Player object semantics.** The full object graph and control surface is the
  type library [6] (§12.5); used-method behaviour is [14] plus disc call-sites.

What remains is **numeric/edge quirks** no public artifact fixes:
exact node-set→boolean coercion in a cue predicate, the precise still-frame vs
tick instant at `titleTimeEnd` (A102), and any per-method corner behaviour beyond
what a disc exercises. All are fail-closed in the sheets. None blocks a
conforming title. The DVD Forum iHD/Annex Z book would make them exhaustive. That book is the
remaining unpublished source. What it would add is a short list of numeric and
edge cases, not the whole runtime.
