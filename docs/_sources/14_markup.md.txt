# 14. iHD markup: `.xmu`, `.xts`, `.xss`

*Counts written "N/120", "N/119", "on N discs", "listings", or as named discs are over the reference corpus of 120 archived retail HD DVD images [11]. `eNN` are the reproducible verification experiments [12].*

iHD markup is the page language of HDi applications: the menus, pop-up menus,
bonus screens and in-movie overlays. A markup document lays out elements on the
graphics plane (boxes with images and text, buttons, text inputs), gives them
styles and states, and describes in a timing section how those styles and states
change over time and in response to focus and remote-control keys. Script
([05](05_manifest_hdi.md) §5.3) reads and changes the same document through the
DOM. A manifest names the application's first markup page
([05](05_manifest_hdi.md) §5.1).

This sheet documents every element and attribute of the iHD schemas, grouped as
the schemas group them: content (§14.4), styling (§14.5), timing (§14.6), then
the path expressions used by timing (§14.7), every style attribute (§14.8) and
every state attribute (§14.9). HDi is built from Web standards [15]: the element
set is XHTML-like, the style attributes take their names and meanings from
XSL-FO / CSS, and the timing model is SMIL 2.0 [18] over a DOM Level 2 tree
[17] ([12](12_hdi_scripting_abi.md) §12.4). Where this sheet says "XSL-FO
semantics", those standards give the meaning; the iHD book chapters that restate
them (Spec. 7.5–7.8) are not among the available sources.

Sources: the DVD Forum schemas [5] (v1.0 and v1.1), the HDi Jumpstart posts
[14], the patent [1] for page switching and clocks, and the corpus, checked by
`e27` (every markup document) with the earlier `e15` / `e17`.

## 14.1 Files, namespaces, versions

| File | Root element | What it holds |
|---|---|---|
| `.xmu` | `root` | A markup page: head (styles, timing) and body (content) |
| `.xts` | `timing` | A timing section on its own, pulled into a page's `head` by `include` |
| `.xss` | `styling` (inferred) | A styling section on its own, pulled into `head` by `include` |
| `.xas` | `root` | Advanced Subtitle markup ([11](11_gaps.md) B3); same document model |

| Namespace | Prefix used here | Contains |
|---|---|---|
| `http://www.dvdforum.org/2005/ihd` | (none) | elements and their plain attributes |
| `http://www.dvdforum.org/2005/ihd#style` | `style:` | the style attributes (§14.8) |
| `http://www.dvdforum.org/2005/ihd#state` | `state:` | the state attributes (§14.9) |
| `http://www.w3.org/XML/1998/namespace` | `xml:` | `xml:lang`, `xml:base`, `xml:space` |

Schemas: `spec/raw/adv_obj/v1.1/iHD.xsd` (imports `iHDstyle.xsd` and
`iHDstate.xsd`); v1.0 for reference. Differences in §14.10. The corpus
validates against both except for one document (§14.11).

**Reading rules.**

- UTF-8 XML. Match by namespace and local name, never by prefix.
- Ignore comments and `xsi:schemaLocation` (24 roots carry one).
- **Attributes in other namespaces**: keep them on the DOM node (script can read
  them) and ignore them for rendering. `SHREK_THE_THIRD_EU` puts 305 such
  attributes (`onaction`, `onup`, … in `http://sampleext`) on buttons for its own
  script; the schema only allows foreign attributes on `meta`.
- Apply the defaults below when an attribute is absent.
- An `id` is an XML ID: unique in the document, used by `nav*`, `style`,
  `id()` paths and script.
- `include` is resolved before anything else (§14.4).

## 14.2 Document structure

```
root                     xml:lang (required)
├── head?
│   ├── meta*
│   └── (include | styling | timing)*
│       styling  → style*                              §14.5
│       timing   → defs*, then (par | seq)*            §14.6
│                  defs → (g | animate | set | event | link)*
│                  par / seq → (cue | par | seq)*
│                  cue → (animate | set | event)* or one link
└── body?
    ├── meta*
    └── (div | object | include)*                      §14.4
        div   → meta*, (button | object | input | div | p)*
        p     → text and (object | button | input | br | span)*
        span  → text and (object | button | input | br | span)*
        button, input → meta*, p?
        object → meta*, param*, area*, p?
```

Every content element gets common attributes from its **base type**:

| Base | Adds | Elements |
|---|---|---|
| NonDisplay | (nothing) | `root`, `head`, `meta`, `include` |
| Display | `class`, `state:enabled` | `body`, `br`, `object` |
| Navigable | + `style` (IDREFS), `state:pointer` | `div`, `p`, `span` |
| Activateable | + `state:focused`, `state:actioned` | (base only) |
| Stateful | + `state:value` | `area`, `button`, `input` |

All elements also accept `xml:base`, `xml:lang`, `xml:space` and `id`.

## 14.3 Data types

| Type | Syntax | Meaning |
|---|---|---|
| time | `HH:MM:SS` or `HH:MM:SS:FF` (clock value, hours may exceed two digits), or a number with a unit: `h`, `m`, `s`, `ms`, `f` (`0.5s`, `500ms`, `9f`) | A time or duration on the element's clock (§14.6). `f` counts frames: the title timeline's frame rate on the title clock, the tick rate on page and application clocks (**INFERRED**) |
| time or path | a time, or a path expression (§14.7) | `begin` / `end` on timing elements: a time, or a condition that becomes true |
| length | integer + `px`, `em` or `%` (`-12px` allowed where the type allows negatives) | Pixels are graphics-plane pixels (the playlist `Aperture`, normally 1920×1080) |
| colour | `#rgb`, `#rrggbb`, `rgb(r,g,b)`, `rgba(r,g,b,a)` (0–255 or %), one of 16 names (`aqua black blue fuchsia gray green lime maroon navy olive purple red silver teal white yellow`), `transparent` | |
| animated value | several values separated by `;` (`1;0.8;0.5`) | Keyframes for `animate` (§14.6); a style attribute that allows it lists "animatable" in §14.8 |
| `inherit` | the token | Take the parent's value |
| access key list | space-separated: `U+XXXX` (a Unicode character) or a virtual key `VK_…` | Remote keys that activate the element directly |
| URI | `anyURI` | `file:///dvddisc/…`, an ACA member `…/x.aca/member`, or a relative URI (against `xml:base` then the document's location) |

Virtual keys (`VirtualKeyType`): `VK_PLAY VK_PAUSE VK_FF VK_FR VK_SF VK_SR
VK_STEP_PREV VK_STEP_NEXT VK_SKIP_PREV VK_SKIP_NEXT VK_SUBTITLE_SWITCH
VK_SUBTITLE VK_CC VK_ANGLE VK_AUDIO VK_MENU VK_TOP_MENU VK_BACK VK_RESUME
VK_LEFT VK_UP VK_RIGHT VK_DOWN VK_LEFTUP VK_RIGHTUP VK_LEFTDOWN VK_RIGHTDOWN
VK_TAB VK_A_BUTTON`…`VK_L_BUTTON VK_ENTER VK_ESC VK_0`…`VK_9
VK_MOUSE_1`…`VK_MOUSE_5 VK_VECTOR_1`…`VK_VECTOR_4`.

## 14.4 Content elements

**`root`** (Spec. 7.5.3.1.13). The document element. Children: `head?`, `body?`.

| Attribute | Type | Req. | What it is for |
|---|---|---|---|
| `xml:lang` | language | **yes** | Language of the page's text (`en`, `en-us` on disc) |
| `xml:base` | URI | no | Base for relative URIs in the page |
| `xml:space`, `id` | | no | XML standard |

**`head`** (7.5.3.1.6). Non-visual part: `meta*`, then any number of `include`,
`styling`, `timing`.

**`body`** (7.5.3.1.2). The visible page; its box is the application's region
(the manifest `Region`). Children: `meta*`, then `div`, `object`, `include`.

| Attribute | Type | Default | What it is for |
|---|---|---|---|
| `timeContainer` | `par` \| `seq` | `seq` | How the body's timed children are scheduled (§14.6) |
| `begin`, `dur`, `end` | time | | When the body is active on its clock |
| `style` | IDREFS | | Named styles to apply (§14.5) |
| `state:foreground` | boolean | `false` | Whether this page's application is the foreground application, the one that receives the remote keys (**INFERRED** from the name) |
| `class`, `state:enabled` | | | From Display base |
| body style attributes | | | §14.8 |

**`div`** (7.5.3.1.5). A box: the building block of every menu. Children:
`meta*`, then `button`, `object`, `input`, `div`, `p`.

| Attribute | Type | Default | What it is for |
|---|---|---|---|
| `timeContainer` | `par` \| `seq` | `par` | Scheduling of timed children |
| `begin`, `dur`, `end` | time | | Active interval |
| `class`, `style`, `state:enabled`, `state:pointer` | | | From Navigable base |
| div style attributes | | | §14.8 |

**`p`** (7.5.3.1.11) and **`span`** (7.5.3.1.14). A paragraph and an inline run
of text (mixed content). Children: text, `meta`, `object`, `button`, `input`,
`br`, `span`. Attributes: `timeContainer` (default `par`), `begin` / `dur` / `end`,
the Navigable base, and their style attributes. On disc every `p` is inside a
`div`, and the text styling (`font`, `fontSize`, `color`, `lineHeight`) is on
that `div` ([05](05_manifest_hdi.md) §5.9).

**`br`** (7.5.3.1.3). A line break inside `p` / `span`. Display base, `br` style
attributes.

**`button`** (7.5.3.1.4). A focusable, activatable element. Children: `meta*`,
`p?` (its label).

| Attribute | Type | What it is for |
|---|---|---|
| `accessKey` | access key list | Remote keys that activate the button directly, wherever focus is (`VK_MENU`, `VK_TOP_MENU`, `VK_A_BUTTON` on disc). Pressing one sets `state:actioned` on it |
| Stateful base | | `class`, `style`, `state:enabled`, `state:pointer`, `state:focused`, `state:actioned`, `state:value` |
| button style attributes | | §14.8, including the `nav*` focus graph |

**`input`** (7.5.3.1.8). A text field. Children: `meta*`, `p?`.

| Attribute | Type | Default | What it is for |
|---|---|---|---|
| `mode` | `password` \| `singleline` \| `multiline` \| `display` | `singleline` | Kind of field; `display` shows text without editing |
| `state:value` | string | | The text |
| `accessKey` | access key list | | As `button` |

**`object`** (7.5.3.1.10). Embedded media. Children: `meta*`, `param*`,
`area*`, `p?`.

| Attribute | Type | Req. | What it is for |
|---|---|---|---|
| `type` | `image/jpeg` \| `image/png` \| `image/cvi` \| `image/cdw` \| `image/mng` \| `audio/x-wav` \| `application/x-clearrect` \| `application/x-graphic` | yes | What the object is. `application/x-clearrect` clears its box on the graphics plane so video shows through; `audio/x-wav` is an effect sound |
| `src` | URI | no | The media file |
| `content` | IDREF | no | Element whose content the object presents |
| `style` | IDREFS | no | Named styles |
| object style attributes | | | §14.8 |

**`param`** (7.5.3.1.12). A named value for its parent `object` or `event`:
`name` (required), `value`; the element may also have text content.

**`area`** (7.5.3.1.1). A clickable region of an `object` (image map):

| Attribute | Type | Default | What it is for |
|---|---|---|---|
| `shape` | `circle` \| `poly` \| `rect` \| `default` | `default` | Region shape; `default` = the whole object |
| `coords` | list of non-negative integers | | Shape coordinates (HTML image-map convention) |
| `accessKey` | access key list | | As `button` |
| Stateful base, area style attributes | | | |

**`meta`** (7.5.3.1.9). Author metadata: any elements and attributes from other
namespaces; ignored by rendering. On disc always empty (329).

**`include`** (7.5.3.1.7). Pulls another document into this one at this point.

| Attribute | Type | Req. | What it is for |
|---|---|---|---|
| `href` | URI | yes | The document: `.xmu` fragment in `body`, `.xts` (a `timing`) or `.xss` (a `styling`) in `head` |
| `condition` | string | no | Condition for including it (unused on disc) |

On disc: `body` includes `.xmu` 23, `head` includes `.xss` 11 and `.xts` 2.

## 14.5 Styling

Styles can be written three ways, all with the same `style:` attributes (§14.8):

1. **Inline**: `style:` attributes on the element itself.
2. **Named styles**: a `style` element with an `id` in `head/styling`; an element
   lists the ids it uses in its `style` attribute (space-separated IDREFS; `style`
   elements can also reference others the same way).
3. **Selected styles**: a `style` element with `select` (a path expression,
   §14.7) applies to every element the path matches.

**`styling`** (7.6.3.1.1): `meta*`, `style*`.

**`style`** (7.6.3.1.2): children `meta*`.

| Attribute | Type | What it is for |
|---|---|---|
| `id` | ID | Name other elements use in their `style` attribute |
| `style` | IDREFS | Other named styles this one builds on |
| `select` | path | Elements this style applies to |
| any `style:` attribute | | The style values (all 61 allowed) |

Precedence between the three is not in the available sources. Apply them in the
CSS order that HDi's model follows [15]: named or selected styles first, in
document order, then inline attributes, which win. **INFERRED**. On disc: 88
`style` elements, named styles referenced 387 times (`defaultStyles`,
`defaultStyles keyStyle`, …); `select` on `style` is unused.

## 14.6 Timing

Timing makes the page change over time and react to input. It lives in
`head/timing` (or an included `.xts`), separately from the content it acts on.

**Clocks.** Every timing section runs on one clock (`timing@clock`):

| Clock | Runs | Used for |
|---|---|---|
| `title` (default) | locked to the title timeline (media time): pauses and seeks with the video | cues at specific movie times (in-movie overlays) |
| `page` | from when the page is loaded, independent of the video | menus: effects keep playing while the video is paused |
| `application` | for the application's whole active life | timers shared across pages |

Page and application clocks tick at `TitleSet@tickBase`, reduced by
`Title@tickBaseDivisor` ([03](03_playlist.md) §3.7, §3.8). On disc: `page` 68,
`application` 9, `title` 3, omitted 8. ([05](05_manifest_hdi.md) §5.2.)

**`timing`** (7.7.2.9.10). Children: `defs*`, then `par` / `seq`.

| Attribute | Type | Default | What it is for |
|---|---|---|---|
| `clock` | `title` \| `application` \| `page` | `title` | The clock (above) |
| `timeContainer` | `par` \| `seq` | `par` | How the top-level containers run |
| `begin`, `dur`, `end` | time or path | | Active interval of the whole section |
| `clockDivisor` (v1.0 only) | positive integer | `1` | Removed in v1.1 |

**`par`** and **`seq`** (7.7.2.9.7–8). Time containers, as SMIL: the children of
`par` run in parallel; the children of `seq` one after another. Children: `cue`,
`par`, `seq`. Attributes: `begin`, `dur`, `end` (time or path).

**`cue`** (7.7.2.9.2). The unit of action: while its interval is active, it applies
its effects to the elements it selects.

| Attribute | Type | Default | What it is for |
|---|---|---|---|
| `select` | path | | The elements the cue acts on. Absent: the element its `begin` path matched (see `defaultNode()`, §14.7) |
| `begin` | time or path | | When the cue starts: a time, or the moment a condition becomes true (`id('BT_play')[state:focused()=true()]`) |
| `end` | time or path | | When it stops |
| `dur` | time | | Its length (instead of `end`) |
| `use` | IDREFS | | `g` elements from `defs` whose effects to apply, as if they were written inside the cue |
| `fill` | `remove` \| `hold` | `remove` | After the cue ends: `remove` undoes its effects, `hold` keeps the final values |

Children: any number of `animate`, `set`, `event`; **or** a single `link`.

**`defs`** (7.7.2.9.3) holds reusable effects: `g`, `animate`, `set`, `event`,
`link`. **`g`** (7.7.2.9.5) groups them under an `id` for `cue@use`; children
`g`, `animate`, `set`, `event`.

**`set`** (7.7.2.9.9). While active, sets style and state attributes of the
selected elements to the given values. Allowed: every animatable style attribute
and `state:enabled`, `state:focused`, `state:value` (v1.1). Example:
`<set style:backgroundFrame="1"/>` shows the focused image.

**`animate`** (7.7.2.9.1). Changes attributes over the cue's duration through a
list of keyframes (`style:opacity="0;0.5;1"`), spread evenly across the duration.

| Attribute | Type | Default | What it is for |
|---|---|---|---|
| `calcMode` | `linear` \| `discrete` | `linear` | Interpolate between keyframes, or jump |
| `additive` | `replace` \| `sum` | `replace` | Replace the attribute's value, or add to it |
| animatable style / state attributes | animated value | | The keyframes |

**`event`** (7.7.2.9.4). Fires a DOM event named `name` (required) when the cue
starts, targeted at the cue's selected elements (**INFERRED**); script receives it through
`addEventListener(name, …)`. Children: `param*`, the event's data.

**`link`** (7.7.2.9.6). Switches the application to another markup page:
`href` (required, the `.xmu`), `xml:base`, `id` (v1.1). The current page is
replaced; the application and its File Cache stay [1]. On disc: 12, all in
`OLIVER_TWIST_JPN` menus.

**Rules** (SMIL 2.0 [18], [12](12_hdi_scripting_abi.md) §12.4):

- A cue whose `begin` is a path starts when the path becomes true and ends when
  its `end` becomes true (or after `dur`); it can start again when `begin` is
  next true.
- Evaluate path conditions on every clock tick and on every focus, action or
  state change.
- A cue's timing never outlives its application: the application's valid period
  on the title timeline ([03](03_playlist.md) §3.13) gates everything.

On disc: `cue` 1239, `set` 579, `event` 510, `animate` 483, `par` 204, `seq` 33,
`defs` 54, `g` 8, `link` 12; `fill` only `hold` (176); `calcMode` only `linear`
(24); `additive` only `sum` (12).

## 14.7 Path expressions

`begin`, `end` and `select` on timing elements, and `select` on `style`, take a
path expression (`PathExpressionType`, Spec. 7.5.2.4). It is **XPath 1.0**
evaluated over the markup document, with the `state:` and `style:` namespaces
bound, the page's variables, and these functions:

| Function | Returns | Meaning |
|---|---|---|
| `id('x')`, `id($v)` | node-set | The element with that `id` (XPath standard) |
| `class('c')`, `class($v)` | node-set | Every element whose `class` contains `c` (iHD extension) |
| `defaultNode()` | node-set | The cue's default node: the element its `begin` matched. On disc it appears only in the `end` of timing elements (192 `cue`, 1 `par`) that have no `select` and whose `begin` names one element, as `defaultNode()[state:focused()=false()]`: "end when that element loses focus". **INFERRED** |
| `state:focused()`, `state:actioned()`, `state:enabled()`, `state:pointer()`, `state:value()`, `state:foreground()` | boolean or string | The state attribute (§14.9) of the context node |
| `style:x()`, `style:opacity()`, … (one per style attribute) | string | The current value of that style attribute of the context node; with a node argument (`style:x(id('focusToggle'))`) of that node |
| `true()`, `false()`, `not()`, `boolean()` | boolean | XPath standard |

Plus: location paths (`//button`, `//body`), predicates `[…]`, attribute tests
(`@state:focused='true'`, `@id=$focus`), unions `|`, comparisons `=` `!=`, `and`,
number and string literals, and `$name` variables that script sets with
`document.setXPathVariable(name, value)` ([05](05_manifest_hdi.md) §5.3).

A path in `begin` / `end` is true when it yields a non-empty node-set or boolean
true. A path that cannot be evaluated is false (the cue does not fire).
**INFERRED** (XPath 1.0 plus enumerated extensions; Spec. 7.5.2.4 unpublished).

On disc (every `begin`, `end` and `select`): `id` 1664 uses,
`state:focused` 680, `true` 589, `state:actioned` 302, `false` 277,
`defaultNode` 193, `class` 31, `style:display` 25, `style:y` 21,
`style:opacity` 18, `not` 8, `boolean` 8, `state:pointer` 4, `style:x` 1;
88 distinct path shapes. The commonest:

```
select="id('BT_scenes')"
begin="id('BT_scenes')[state:focused()=true()]"
end="defaultNode()[state:focused()=false()]"
begin="//button[state:actioned()=true()]"
begin="(boolean($sw01) and boolean($set01))"
```

## 14.8 Style attributes

All in the `ihd#style` namespace (Spec. 7.6.3.3.2.*). **Animatable** attributes
may take a `;` keyframe list and may be used in `set` / `animate`. **Allowed on**
is from the element's style group in the v1.1 schema; every attribute is also
allowed on `style`. **Used** counts the attribute on any element in the corpus.
Meanings marked "XSL-FO semantics" follow that standard; the rest are verified
on disc or follow directly from the name and values
([05](05_manifest_hdi.md) §5.9 for the used rendering rules).

| Attribute | Values | Default | Animatable | Allowed on | Used | What it is for |
|---|---|---|---|---|---|---|
| `anchor` | `startBefore` \| `centerBefore` \| `endBefore` \| `startCenter` \| `center` \| `endCenter` \| `startAfter` \| `centerAfter` \| `endAfter` | `startBefore` | yes | button, div, object | 31 | Which point of the element's box is placed at (`x`, `y`): `start`/`center`/`end` across × `Before`/`Center`/`After` down (in `lr-tb`, start = left, before = top); `center` is the middle |
| `backgroundColor` | colour | `transparent` | yes | area, body, br, button, div, input, object, p, span | 4 | Colour filling the box behind its content |
| `backgroundFrame` | integer | `0` | yes | area, body, button, div, input, object | 114 | Which image of the `backgroundImage` list is shown, counting from 0. Menus use 0 normal, 1 focused, 2 actioned |
| `backgroundImage` | list of `url('…')` \| `none` | `none` | yes | area, body, button, div, input, object | 1357 | The box's image(s): a space-separated list of `url('…')`; one is shown at a time, chosen by `backgroundFrame`. Long lists are animation strips |
| `backgroundPositionHorizontal` | length \| % \| `left` \| `center` \| `right` | `0%` | yes | area, body, button, div, input, object | 6 | Horizontal position of the background image in the box |
| `backgroundPositionVertical` | length \| % \| `top` \| `center` \| `bottom` | `0%` | yes | area, body, button, div, input, object | 3 | Vertical position of the background image in the box |
| `backgroundRepeat` | `repeat` \| `no-repeat` | `no-repeat` |  | area, body, button, div, input, object | 0 | Whether the background image is tiled |
| `blockProgressionDimension` | length \| % \| `auto` | `auto` | yes | area, body, button, div, input, object, p | 0 | Size along the block direction (the height in `lr-tb`); XSL-FO name for `height` |
| `border` | border string | `None` | yes | area, body, button, div, input, object, p | 0 | Border on all four sides, as one string (CSS-like width, style, colour) |
| `borderAfter` | border string | `None` | yes | area, body, button, div, input, object, p | 0 | Border on the after side (bottom in `lr-tb`) |
| `borderBefore` | border string | `None` | yes | area, body, button, div, input, object, p | 0 | Border on the before side (top in `lr-tb`) |
| `borderEnd` | border string | `None` | yes | area, body, button, div, input, object, p | 0 | Border on the end side (right in `lr-tb`) |
| `borderStart` | border string | `None` | yes | area, body, button, div, input, object, p | 0 | Border on the start side (left in `lr-tb`) |
| `breakAfter` | `auto` \| `line` | `auto` |  | br, button, input, object, span | 0 | `line` forces a line break after this inline element |
| `breakBefore` | `auto` \| `line` | `auto` |  | br, button, input, object, span | 0 | `line` forces a line break before this inline element |
| `color` |  | `white` | yes | area, body, div, input, p, span | 50 | Text colour |
| `contentWidth` | length \| % \| `auto` \| `scale-to-fit` | `auto` | yes | area, body, button, div, input, object | 116 | Width of the image drawn inside the box (as `contentHeight`) |
| `contentHeight` | length \| % \| `auto` \| `scale-to-fit` | `auto` | yes | area, body, button, div, input, object | 115 | Height of the image drawn inside the box: `auto` = its own size, `scale-to-fit` = fit the box |
| `crop` | four integers \| `auto` | `auto` | yes | area, body, button, div, input, object | 0 | Part of the source image to use, four integers; `auto` = all of it. Order of the four numbers not in the sources |
| `direction` | `ltr` \| `rtl` | `ltr` |  | body, div, input, p, span | 0 | Text direction, left-to-right or right-to-left |
| `display` | `auto` \| `none` | `auto` | yes | area, body, br, button, div, input, object, p, span | 1641 | `none` removes the element and its children from rendering (it stays in the navigation graph); `auto` shows it |
| `displayAlign` | `auto` \| `before` \| `center` \| `after` | `auto` | yes | area, body, button, div, input, object, p | 0 | Alignment of the content along the block direction (top / middle / bottom in `lr-tb`) |
| `flip` | `none` \| `inlineProgression` \| `blockProgression` \| `both` | `none` | yes | area, body, button, div, input, object | 0 | Mirror the content across the inline axis, the block axis, or both |
| `font` | font URI | `None` | yes | body, div, input, p, span | 47 | The font: URI of an OpenType file in the File Cache (players have no built-in fonts), optionally followed by a quoted family name |
| `fontSize` | 1 or 2 lengths \| `xx-small` \| `x-small` \| `small` \| `medium` \| `large` \| `x-large` \| `xx-large` \| `smaller` \| `larger` | `medium` | yes | body, div, input, p, span | 55 | Text size; two lengths give horizontal and vertical size separately |
| `fontStyle` | `normal` \| `italic` \| `oblique` \| `backslant` \| `reverse-oblique` | `normal` | yes | body, div, input, p, span | 0 | Upright, italic or slanted text |
| `height` | length \| % \| `auto` | `auto` | yes | area, body, button, div, input, object, p | 1665 | Box height |
| `inlineProgressionDimension` | length \| % \| `auto` | `auto` | yes | area, body, button, div, input, object, p | 0 | Size along the inline direction (the width in `lr-tb`); XSL-FO name for `width` |
| `linefeedTreatment` | `ignore` \| `preserve` \| `treat-as-space` \| `treat-as-zero-width-space` | `treat-as-space` |  | body, div, input, p, span | 0 | What a line feed in the text does (XSL-FO semantics) |
| `lineHeight` | length \| % \| `auto` | `auto` | yes | body, div, input, p | 37 | Height of each line of text |
| `navDown` | element id \| `none` | `none` | yes | area, button, input | 405 | `id` of the element that gets focus when the user presses down; `none` = focus stays |
| `navIndex` | two integers \| `auto` \| `none` | `auto` | yes | area, button, input | 2 | Sequential navigation order; `none` removes the element from remote navigation, `auto` = document order |
| `navLeft` | element id \| `none` | `none` | yes | area, button, input | 405 | As `navDown`, for left |
| `navLeftDown` | element id \| `none` | `none` | yes | area, button, input | 5 | As `navDown`, for the diagonal key |
| `navLeftUp` | element id \| `none` | `none` | yes | area, button, input | 5 | As `navDown`, for the diagonal key |
| `navRight` | element id \| `none` | `none` | yes | area, button, input | 405 | As `navDown`, for right |
| `navRightDown` | element id \| `none` | `none` | yes | area, button, input | 5 | As `navDown`, for the diagonal key |
| `navRightUp` | element id \| `none` | `none` | yes | area, button, input | 5 | As `navDown`, for the diagonal key |
| `navUp` | element id \| `none` | `none` | yes | area, button, input | 405 | As `navDown`, for up |
| `opacity` | number 0–1 | `1.0` | yes | area, body, br, button, div, input, object, p, span | 1526 | Alpha multiplied into the element and its children: 0 invisible, 1 opaque |
| `padding` | 1–4 lengths | `0px` | yes | area, body, button, div, input, object, p | 0 | Space between border and content on all sides (1–4 values, CSS order) |
| `paddingAfter` | length \| % | `0px` | yes | area, body, button, div, input, object, p | 0 | Padding on the after side |
| `paddingBefore` | length \| % | `0px` | yes | area, body, button, div, input, object, p | 0 | Padding on the before side |
| `paddingEnd` | length \| % | `0px` | yes | area, body, button, div, input, object, p | 0 | Padding on the end side |
| `paddingStart` | length \| % | `0px` | yes | area, body, button, div, input, object, p | 0 | Padding on the start side |
| `position` | `static` \| `relative` \| `absolute` | `static` |  | button, div, object | 1462 | `absolute`: the box is placed at `x`, `y` in its parent. `static` / `relative` follow flow layout |
| `scaling` | `uniform` \| `non-uniform` | `non-uniform` |  | area, body, button, div, input, object | 1 | `uniform` keeps the image aspect ratio when fitting; `non-uniform` stretches |
| `suppressAtLineBreak` | `auto` \| `suppress` \| `retain` | `auto` |  | input, span | 0 | Whether this inline content is dropped at a line break (XSL-FO semantics) |
| `textAlign` | `start` \| `center` \| `end` | `start` | yes | body, div, input, p | 0 | Alignment of lines: start, centre or end |
| `textAltitude` | length \| % \| `auto` | `auto` | yes | input, p, span | 0 | Height of the text area above the baseline |
| `textDepth` | length \| % \| `auto` | `auto` | yes | input, p, span | 0 | Depth of the text area below the baseline |
| `textIndent` | length \| % | `0px` | yes | body, div, input, p | 0 | Indent of the first line |
| `visibility` | `visible` \| `hidden` | `visible` | yes | area, body, br, button, div, input, object, p, span | 11 | `hidden` hides the element but keeps its space and navigation |
| `whiteSpaceCollapse` | `true` \| `false` | `true` |  | body, div, input, p | 0 | Whether runs of spaces collapse to one (XSL-FO semantics) |
| `whiteSpaceTreatment` | `ignore` \| `preserve` \| `ignore-before` \| `ignore-after` \| `ignore-around` | `ignore-around` |  | body, div, input, p | 0 | Which spaces around line breaks are removed (XSL-FO semantics) |
| `width` | length \| % \| `auto` | `auto` | yes | area, body, button, div, input, object, p | 1668 | Box width |
| `wrapOption` | `wrap` \| `no-wrap` | `wrap` | yes | body, div, input, p, span | 0 | Whether long lines wrap |
| `writingMode` | `lr-tb` \| `rl-tb` \| `tb-rl` | `lr-tb` |  | body, div, input | 0 | Line and page direction: `lr-tb` left-to-right, top-to-bottom; `rl-tb`; `tb-rl` vertical (Japanese) |
| `x` | length \| % \| `auto` | `0px` | yes | button, div, object | 1763 | Horizontal position of the anchor point, relative to the parent |
| `y` | length \| % \| `auto` | `0px` | yes | button, div, object | 1913 | Vertical position of the anchor point, relative to the parent |
| `zIndex` | integer \| `auto` | `auto` | yes | button, div, object | 19 | Stacking order among siblings; higher is drawn on top |

On disc: `position` is always `absolute` (1462/1462); `display` `inherit` 1054,
`auto` 473, `none` 114; `opacity` `inherit` 1043 and keyframe lists on
`animate`; `contentWidth` / `contentHeight` `scale-to-fit` 41 / 40.
`writingMode`, `padding*`, `border*`, `direction`, `displayAlign`, `whiteSpace*`,
`textAlign` and the text-metric attributes are never used; implement them from
the schema and XSL-FO when a disc needs them.

`[5, 11, 12]` **VERIFIED** (names, values, defaults, placement); meanings of the
unused attributes **INFERRED** (XSL-FO / CSS).

## 14.9 State attributes

In the `ihd#state` namespace (Spec. 7.6.3.4.2.*). They describe what the user is
doing to an element. The player maintains them; markup can set initial values;
`set` / `animate` and script can change the animatable ones; path expressions
read them with `state:…()`.

| Attribute | Values | Default | Animatable | On | What it is for |
|---|---|---|---|---|---|
| `enabled` | boolean | `true` | yes | Display elements and up | `false`: the element cannot be focused or activated |
| `focused` | boolean | `false` | yes | `area`, `button`, `input` | The element has the focus. One element on a page is focused; moving focus sets the old one `false` and the new one `true`. May be set `true` in markup to choose the initial focus; otherwise the first focusable element in document order |
| `actioned` | boolean | `false` | no (v1.1) | `area`, `button`, `input` | The element is being activated: Enter on the focused element, one of its `accessKey` keys, or a pointer click. True while the activation lasts |
| `pointer` | boolean | `false` | no | `div`, `p`, `span` and up | A pointer (cursor) is over the element |
| `value` | boolean or string | | yes | `area`, `button`, `input` | The element's value: the text of an `input` |
| `foreground` | boolean | `false` | no | `body` | See `body` (§14.4) |

On disc: `state:value` 113 (all on `input`), `state:focused` 33 (initial focus),
`state:enabled` 1.

## 14.10 v1.0 and v1.1

Retail discs validate against both schema versions (§14.11); read against v1.1
and accept the v1.0-only forms below.

| Change in v1.1 | v1.0 had |
|---|---|
| `timing@clockDivisor` removed | `clockDivisor` (positive integer, default 1) |
| `set` takes only animatable style and state attributes | all style attributes and all state attributes, plus a `value` attribute |
| `animate` loses its `value` attribute | `value` (string) |
| `cue` no longer takes style attributes directly | all style attributes on `cue` |
| `link@id` added | no `id` |
| `state:actioned` is a plain boolean and not animatable | animated boolean, animatable |
| `style:startIndent`, `style:endIndent` removed | both, on block elements |
| `anchor`, `backgroundPositionHorizontal`, `backgroundPositionVertical` accept `;` keyframe lists | single values |
| `opacity` values restricted to 0–1 | values from −1 to 1 allowed by the pattern |
| Per-element style sets: `area` gains the size attributes and `flip`, loses `breakBefore` / `breakAfter`; `body` gains the size attributes and `flip`; `p` gains the size attributes; `input` gains `flip`; `suppressAtLineBreak` moves from all inline elements to `span` and `input`; `body` and `div` lose `textAltitude` / `textDepth` | the v1.0 sets |

## 14.11 On disc

`e27`: 88 markup documents on the saved discs: 84 `.xmu`, 2 `.xts`, 2 `.xas`
(both empty stubs), extracted from ACAs and loose files. 87 validate against
both v1.1 and v1.0. The one that does not, `SHREK_THE_THIRD_EU`
`iHD_Markup.xmu`, fails only because of its 305 foreign-namespace attributes
(§14.1). `.xss` files are referenced 11 times but none is among the saved
archives.

| Element | N | Element | N |
|---|---|---|---|
| `p` | 1390 | `div` | 1339 |
| `cue` | 1239 | `set` | 579 |
| `event` | 510 | `button` | 492 |
| `animate` | 483 | `param` | 366 |
| `meta` | 329 | `par` | 204 |
| `input` | 113 | `timing` / `style` | 88 / 88 |
| `root` / `head` / `body` | 86 each | `styling` | 67 |
| `defs` | 54 | `include` | 36 |
| `seq` | 33 | `link` | 12 |
| `g` | 8 | `object` | 7 |
| `span`, `br`, `area` | 0 | | |

`[5, 11, 12, 14]`
