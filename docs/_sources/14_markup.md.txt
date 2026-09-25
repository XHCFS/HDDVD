# 14. iHD markup: `.xmu`, `.xts`, `.xss`

*Counts written "N/120", "N/119", "on N discs", "listings", or as named discs are over the reference corpus of 120 archived retail HD DVD images [11]. `eNN` are the reproducible verification experiments [12].*

iHD markup is the page language of HDi applications: the menus, pop-up menus,
bonus screens and in-movie overlays. A markup page does three things:

- **Content** (`body`): the boxes, images, text, buttons and text fields on the
  graphics plane, nested inside each other like HTML.
- **Styling** (`style:` attributes and `styling`): where each box is, how big,
  which image it shows, what colour its text is.
- **Timing** (`timing`): what changes over time and in response to the remote,
  for example "when this button gets focus, show its highlighted image".

Script ([05](05_manifest_hdi.md) §5.3) reads and changes the same page through
the DOM. A manifest names the application's first markup page
([05](05_manifest_hdi.md) §5.1).

HDi is built from Web standards [15]: the elements are XHTML-like, the style
attributes take their names and meanings from XSL-FO / CSS, and the timing model
is SMIL 2.0 [18] over a DOM Level 2 tree [17]
([12](12_hdi_scripting_abi.md) §12.4). Where this sheet says "XSL-FO
semantics", those standards give the meaning; the iHD book chapters that restate
them (Spec. 7.5–7.8) are not among the available sources.

Sources: the DVD Forum schemas [5] (v1.0 and v1.1), the HDi Jumpstart posts
[14], the patent [1] for page switching and clocks, and the corpus, checked by
`e27` (every markup document) with the earlier `e15` / `e17`.

**How to read this sheet.** Start with the tree (§14.2), which shows every
element and where it can go. §14.3 defines each value type once; every table
after it uses those type names. §14.4 lists the attributes many elements share,
and every element section (§14.5–14.7) has a table of what it contains and a
table of all its attributes. §14.9 is the full list of style attributes.

## 14.1 Files, namespaces, versions

| File | Root element | What it holds |
|---|---|---|
| `.xmu` | `root` | A markup page: `head` (styles, timing) and `body` (content) |
| `.xts` | `timing` | A timing section on its own, pulled into a page's `head` by `include` |
| `.xss` | `styling` (inferred) | A styling section on its own, pulled into `head` by `include` |
| `.xas` | `root` | Advanced Subtitle markup ([11](11_gaps.md) B3); same document model |

| Namespace | Prefix used here | Contains |
|---|---|---|
| `http://www.dvdforum.org/2005/ihd` | (none) | elements and their plain attributes |
| `http://www.dvdforum.org/2005/ihd#style` | `style:` | the style attributes (§14.9) |
| `http://www.dvdforum.org/2005/ihd#state` | `state:` | the state attributes (§14.10) |
| `http://www.w3.org/XML/1998/namespace` | `xml:` | `xml:lang`, `xml:base`, `xml:space` |

Schemas: `spec/raw/adv_obj/v1.1/iHD.xsd` (imports `iHDstyle.xsd` and
`iHDstate.xsd`); v1.0 for reference. Differences in §14.11. The corpus
validates against both except for one document (§14.12).

**Reading rules.**

- UTF-8 XML. Match by namespace and local name, never by prefix.
- Ignore comments and `xsi:schemaLocation` (24 roots carry one).
- **Attributes in other namespaces**: keep them on the DOM node (script can read
  them) and ignore them for rendering. `SHREK_THE_THIRD_EU` puts 305 such
  attributes (`onaction`, `onup`, … in `http://sampleext`) on buttons for its own
  script; the schema only allows foreign attributes on `meta`.
- Apply the defaults in the tables when an attribute is absent.
- An `id` is unique in the document. `nav*`, `style`, `use`, `id()` paths and
  script refer to elements by it.
- `include` is resolved before anything else (§14.5).

## 14.2 Document tree

**How many** says how often a child may appear. A bracket `┐ ┘` groups children
that may appear **in any order** among themselves; otherwise children come in
the order shown. Every element has its own section with a **Contains** table
(its children) and an **Attributes** table.

The page:

```
Element             How many                            What it is                        Section
root                1                                   the page                          §14.5
├── head            0 or 1                              everything that is not drawn      §14.5
│   ├── meta        any number, first                   author notes                      §14.5
│   ├── include     any number  ┐                       pulls in a .xss or .xts file      §14.5
│   ├── styling     any number  │ in any order          a block of styles                 §14.6
│   └── timing      any number  ┘                       a timing section                  §14.7
└── body            0 or 1                              what is drawn                     §14.5
    ├── meta        any number, first                   author notes                      §14.5
    ├── div         any number  ┐                       a box                             §14.5
    ├── object      any number  │ in any order          an image, sound or clear area     §14.5
    └── include     any number  ┘                       pulls in a .xmu fragment          §14.5
```

Inside `body`, content nests to any depth:

```
div                                                     a box                             §14.5
├── meta            any number, first
├── div             any number  ┐                       (boxes nest)
├── button          any number  │                       something to focus and press
├── input           any number  │ in any order          a text field
├── object          any number  │                       an image, sound or clear area
└── p               any number  ┘                       a paragraph of text

button, input                                                                             §14.5
├── meta            any number, first
└── p               0 or 1                              the label

object                                                                                    §14.5
├── meta            any number, first
├── param           any number                          a named value for the object
├── area            any number                          a clickable part of the image
└── p               0 or 1

p, span             text, mixed in any order with:                                        §14.5
                    meta, object, button, input, br, span
```

Inside `styling`:

```
styling                                                                                   §14.6
├── meta            any number, first
└── style           any number                          one named or selected style       §14.6
    └── meta        any number
```

Inside `timing`:

```
timing                                                                                    §14.7
├── defs            any number, first                   reusable effects                  §14.7
│   ├── g           any number  ┐                       a named group of effects
│   ├── animate     any number  │
│   ├── set         any number  │ in any order
│   ├── event       any number  │
│   └── link        any number  ┘
├── par             any number  ┐ in any order          run children at the same time     §14.7
└── seq             any number  ┘                       run children one after another
    ├── cue         any number  ┐                       one timed action                  §14.7
    ├── par         any number  │ in any order          (par and seq nest)
    └── seq         any number  ┘

cue                                                                                       §14.7
├── animate         any number  ┐                       change values over time
├── set             any number  │ in any order          set values
├── event           any number  ┘                       notify script
│   └── param       any number                          the event's data
└── link            exactly 1, instead of all the above switch to another page

g                   g, animate, set, event: any number, in any order
```

A typical menu page:

```
root
├── head
│   ├── styling → style id="defaultStyles"
│   └── timing clock="page"
│       └── par
│           ├── cue  begin="id('BT_play')[state:focused()=true()]"  → set backgroundFrame=1
│           └── cue  begin="id('BT_play')[state:actioned()=true()]" → event name="play"
└── body
    └── div  (full-screen background image)
        ├── button id="BT_play"   (x, y, width, height, backgroundImage, navDown="BT_scenes")
        │   └── p → "Play"
        └── button id="BT_scenes" (…, navUp="BT_play")
```

## 14.3 Data types

Every attribute in this sheet has one of these types. **Parsed value** says what
the text becomes once it is read.

| Type | Written as | Parsed value | Notes |
|---|---|---|---|
| boolean | `true` \| `false` | true / false | |
| integer | `-?[0-9]+` | signed integer | |
| non-negative integer | `[0-9]+` | unsigned integer | |
| number | decimal, `0.5` | fraction | only `opacity`, 0 to 1 |
| string | any text | text | |
| enum | one of the listed words | one of a fixed set | the tables list every allowed word |
| ID | an XML name (`BT_play`) | text | unique in the document |
| IDREF | an ID | text | names another element |
| IDREFS | IDs separated by spaces | list of texts | |
| names | names separated by spaces (`xs:NMTOKENS`) | list of texts | `class` |
| URI | `file:///dvddisc/…`, `…/x.aca/member`, or relative | text, kept as written | relative URIs resolve against `xml:base`, then the document's own location |
| URL list | `url('a.png') url('b.png')` or `none` | list of URIs, or none | `backgroundImage` |
| time | `HH:MM:SS`, `HH:MM:SS:FF` (hours may have more than two digits), or a decimal with a unit: `h`, `m`, `s`, `ms`, `f` (`0.5s`, `500ms`, `9f`) | either a clock value (hours, minutes, seconds, frames) or an amount with a unit | `f` counts frames of the element's clock (§14.7): the title timeline's frame rate on the title clock, the tick rate on page and application clocks (**INFERRED**). Keep the unit: the frame length is known only once the clock is |
| path | an XPath 1.0 expression (§14.8) | text, kept as written | evaluated while the page runs, not when it is read |
| time or path | a time, or a path | tagged: a time or a path | a value that matches the time syntax is a time; anything else is a path |
| length | integer + `px`, `em` or `%` (`-12px` where negatives are allowed) | number + unit | `px` are graphics-plane pixels (the playlist `Aperture`, normally 1920×1080) |
| percentage | integer + `%` | number | |
| colour | `#rgb`, `#rrggbb`, `rgb(r,g,b)`, `rgba(r,g,b,a)` (each 0–255 or a %), one of 16 names, or `transparent` | red, green, blue, alpha | names: `aqua black blue fuchsia gray green lime maroon navy olive purple red silver teal white yellow`. `transparent` = alpha 0 |
| access keys | space-separated keys: `U+XXXX` (4–6 hex digits, a Unicode character) or a virtual key `VK_…` | list of keys, each a character code or a virtual key | virtual keys listed below |
| border | text without `;` (CSS-like width, style, colour) | text | the grammar is not in the sources |
| font | a URI, optionally followed by a family name in quotes: `file:///dvddisc/ADV_OBJ/font.ttf 'Arial'` | URI + optional family name | an OpenType file in the File Cache; players have no built-in fonts |

Two forms apply on top of the style and state types:

| Form | Written as | Parsed value | Where |
|---|---|---|---|
| keyframe list | values separated by `;` (`1;0.8;0.5`) | list of values of the attribute's own type; a single value is a list of one | every **animatable** style attribute (§14.9), `state:enabled`, `state:focused`, `state:value`. Used by `animate` (§14.7) |
| `inherit` | the word `inherit` | "take the parent's value" | every style attribute except `anchor`, `crop`, `flip` and `navIndex` |

So a style attribute on an element is in one of three conditions: **not
written** (named and selected styles, then the default, apply), **`inherit`**,
or **a value** (one value or a keyframe list).

Virtual keys (`VirtualKeyType`): `VK_PLAY VK_PAUSE VK_FF VK_FR VK_SF VK_SR
VK_STEP_PREV VK_STEP_NEXT VK_SKIP_PREV VK_SKIP_NEXT VK_SUBTITLE_SWITCH
VK_SUBTITLE VK_CC VK_ANGLE VK_AUDIO VK_MENU VK_TOP_MENU VK_BACK VK_RESUME
VK_LEFT VK_UP VK_RIGHT VK_DOWN VK_LEFTUP VK_RIGHTUP VK_LEFTDOWN VK_RIGHTDOWN
VK_TAB VK_A_BUTTON`…`VK_L_BUTTON VK_ENTER VK_ESC VK_0`…`VK_9
VK_MOUSE_1`…`VK_MOUSE_5 VK_VECTOR_1`…`VK_VECTOR_4`.

## 14.4 Shared attributes

The schema builds the content elements from a chain of base types, each adding
attributes to the one before. This table spells the chain out: the **On**
column says exactly which elements have each attribute, so the element tables
below do not repeat them.

| Attribute | Type | Default | On | What it is for |
|---|---|---|---|---|
| `id` | ID | | every element | Name that paths, `nav*`, `style`, `use` and script refer to |
| `xml:lang` | language (`en`, `en-us`) | | every element except `link`; **required** on `root` | Language of the element's text |
| `xml:base` | URI | | every element | Base for relative URIs inside the element |
| `xml:space` | enum `default` \| `preserve` | | every element except `link` | XML white-space handling |
| `class` | names | | `body`, `br`, `object`, `div`, `p`, `span`, `button`, `input`, `area` | Group names, matched by `class()` in paths (§14.8) and by script |
| `state:enabled` | boolean, keyframe list | `true` | same as `class` | `false`: the element cannot be focused or activated (§14.10) |
| `style` | IDREFS | | `body`, `object`, `div`, `p`, `span`, `button`, `input`, `area` | Named styles to apply (§14.6) |
| `state:pointer` | boolean | `false` | `div`, `p`, `span`, `button`, `input`, `area` | A pointer is over the element (§14.10) |
| `state:focused` | boolean, keyframe list | `false` | `button`, `input`, `area` | The element has the focus (§14.10) |
| `state:actioned` | boolean | `false` | `button`, `input`, `area` | The element is being activated (§14.10) |
| `state:value` | boolean or string, keyframe list | | `button`, `input`, `area` | The element's value (§14.10) |

Schema names for reference: `root`, `head`, `meta`, `include` are
*NonDisplay*; `body`, `br`, `object` are *Display* (+ `class`,
`state:enabled`); `div`, `p`, `span` are *Navigable* (+ `style`,
`state:pointer`); `button`, `input`, `area` are *Stateful* (+ `state:focused`,
`state:actioned`, `state:value`). `body` and `object` add `style` themselves.

**Timing attributes.** `begin`, `dur` and `end` appear on content elements and
on timing elements, with different types:

| On | `begin`, `end` | `dur` |
|---|---|---|
| `body`, `div`, `p`, `span` | time | time |
| `timing`, `par`, `seq`, `cue` | time or path | time |

## 14.5 Content elements

Each element below has three tables: **Contains** (its children),
**Attributes** (every attribute it has, shared ones included) and, for elements
that are drawn, **Style attributes** (the style attributes it accepts, detailed
in §14.9).

### `root`

The document element of a `.xmu` or `.xas` (Spec. 7.5.3.1.13).

**Contains**

| Child | How many | What it is |
|---|---|---|
| `head` | 0 or 1 | Everything that is not drawn |
| `body` | 0 or 1 | What is drawn |

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `xml:lang` | language | **yes** |  | Language of the page's text (`en`, `en-us` on disc) |
| `id`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

### `head`

Everything on the page that is not drawn: its styles and its timing
(7.5.3.1.6).

**Contains**

| Child | How many | What it is |
|---|---|---|
| `meta` | any number, first | Author notes (`meta` below) |
| `include` | any number, in any order with `styling` and `timing` | A `.xss` (styling) or `.xts` (timing) file pulled in here |
| `styling` | any number | A block of styles (§14.6) |
| `timing` | any number | A timing section (§14.7) |

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

### `body`

What is drawn (7.5.3.1.2). Its box is the application's region (the manifest
`Region`).

**Contains**

| Child | How many | What it is |
|---|---|---|
| `meta` | any number, first | Author notes (`meta` below) |
| `div` | any number, in any order with `object` and `include` | A box |
| `object` | any number | An image, sound or clear area |
| `include` | any number | A `.xmu` fragment pulled in here |

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `timeContainer` | enum `par` \| `seq` | no | `seq` | How its timed children are scheduled (§14.7) |
| `begin`, `dur`, `end` | time | no |  | When it is active on its clock |
| `state:foreground` | boolean | no | `false` | Whether this page's application is the foreground application, the one that receives the remote keys (**INFERRED** from the name) |
| `class` | names | no |  | Group names, matched by `class()` in paths and by script |
| `state:enabled` | boolean | no | `true` | `false`: it cannot be focused or activated (§14.10) |
| `style` | IDREFS | no |  | Named styles to apply (§14.6) |
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

**Style attributes** (§14.9)

| Group | Attributes |
|---|---|
| Position and size | `width`, `height`, `inlineProgressionDimension`, `blockProgressionDimension` |
| Showing and hiding | `display`, `visibility`, `opacity` |
| Background and image | `backgroundColor`, `backgroundImage`, `backgroundFrame`, `backgroundPositionHorizontal`, `backgroundPositionVertical`, `backgroundRepeat`, `contentWidth`, `contentHeight`, `scaling`, `crop`, `flip` |
| Border and padding | `border`, `borderStart`, `borderEnd`, `borderBefore`, `borderAfter`, `padding`, `paddingStart`, `paddingEnd`, `paddingBefore`, `paddingAfter` |
| Text | `font`, `fontSize`, `fontStyle`, `color`, `lineHeight`, `textAlign`, `textIndent`, `displayAlign`, `wrapOption`, `direction`, `writingMode`, `linefeedTreatment`, `whiteSpaceCollapse`, `whiteSpaceTreatment` |

### `div`

A box, the building block of every menu (7.5.3.1.5).

**Contains**

| Child | How many | What it is |
|---|---|---|
| `meta` | any number, first | Author notes (`meta` below) |
| `div` | any number, in any order with the rows below | A box inside this one |
| `button` | any number | Something to focus and press |
| `input` | any number | A text field |
| `object` | any number | An image, sound or clear area |
| `p` | any number | A paragraph of text |

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `timeContainer` | enum `par` \| `seq` | no | `par` | How its timed children are scheduled (§14.7) |
| `begin`, `dur`, `end` | time | no |  | When it is active on its clock |
| `class` | names | no |  | Group names, matched by `class()` in paths and by script |
| `state:enabled` | boolean | no | `true` | `false`: it cannot be focused or activated (§14.10) |
| `style` | IDREFS | no |  | Named styles to apply (§14.6) |
| `state:pointer` | boolean | no | `false` | A pointer is over it (§14.10) |
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

**Style attributes** (§14.9)

| Group | Attributes |
|---|---|
| Position and size | `position`, `x`, `y`, `anchor`, `width`, `height`, `inlineProgressionDimension`, `blockProgressionDimension`, `zIndex` |
| Showing and hiding | `display`, `visibility`, `opacity` |
| Background and image | `backgroundColor`, `backgroundImage`, `backgroundFrame`, `backgroundPositionHorizontal`, `backgroundPositionVertical`, `backgroundRepeat`, `contentWidth`, `contentHeight`, `scaling`, `crop`, `flip` |
| Border and padding | `border`, `borderStart`, `borderEnd`, `borderBefore`, `borderAfter`, `padding`, `paddingStart`, `paddingEnd`, `paddingBefore`, `paddingAfter` |
| Text | `font`, `fontSize`, `fontStyle`, `color`, `lineHeight`, `textAlign`, `textIndent`, `displayAlign`, `wrapOption`, `direction`, `writingMode`, `linefeedTreatment`, `whiteSpaceCollapse`, `whiteSpaceTreatment` |

### `p` and `span`

A paragraph and an inline run of text inside it (7.5.3.1.11, 7.5.3.1.14). On
disc every `p` is inside a `div`, and the text styling (`font`, `fontSize`,
`color`, `lineHeight`) is on that `div` ([05](05_manifest_hdi.md) §5.9).

**Contains**

| Child | How many | What it is |
|---|---|---|
| text | any amount, in any order with the rows below | The words |
| `meta` | any number | Author notes |
| `object` | any number | An image or sound inside the text |
| `button` | any number | A button inside the text |
| `input` | any number | A text field inside the text |
| `br` | any number | A line break |
| `span` | any number | A run of text with its own style |

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `timeContainer` | enum `par` \| `seq` | no | `par` | How its timed children are scheduled (§14.7) |
| `begin`, `dur`, `end` | time | no |  | When it is active on its clock |
| `class` | names | no |  | Group names, matched by `class()` in paths and by script |
| `state:enabled` | boolean | no | `true` | `false`: it cannot be focused or activated (§14.10) |
| `style` | IDREFS | no |  | Named styles to apply (§14.6) |
| `state:pointer` | boolean | no | `false` | A pointer is over it (§14.10) |
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

**Style attributes of `p`** (§14.9)

| Group | Attributes |
|---|---|
| Position and size | `width`, `height`, `inlineProgressionDimension`, `blockProgressionDimension` |
| Showing and hiding | `display`, `visibility`, `opacity` |
| Background and image | `backgroundColor` |
| Border and padding | `border`, `borderStart`, `borderEnd`, `borderBefore`, `borderAfter`, `padding`, `paddingStart`, `paddingEnd`, `paddingBefore`, `paddingAfter` |
| Text | `font`, `fontSize`, `fontStyle`, `color`, `lineHeight`, `textAlign`, `textIndent`, `displayAlign`, `textAltitude`, `textDepth`, `wrapOption`, `direction`, `linefeedTreatment`, `whiteSpaceCollapse`, `whiteSpaceTreatment` |

**Style attributes of `span`** (§14.9)

| Group | Attributes |
|---|---|
| Showing and hiding | `display`, `visibility`, `opacity` |
| Background and image | `backgroundColor` |
| Text | `font`, `fontSize`, `fontStyle`, `color`, `textAltitude`, `textDepth`, `wrapOption`, `direction`, `linefeedTreatment`, `suppressAtLineBreak`, `breakBefore`, `breakAfter` |

### `br`

A line break inside `p` or `span` (7.5.3.1.3).

**Contains:** nothing.

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `class` | names | no |  | Group names, matched by `class()` in paths and by script |
| `state:enabled` | boolean | no | `true` | `false`: it cannot be focused or activated (§14.10) |
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

**Style attributes** (§14.9)

| Group | Attributes |
|---|---|
| Showing and hiding | `display`, `visibility`, `opacity` |
| Background and image | `backgroundColor` |
| Text | `breakBefore`, `breakAfter` |

### `button`

Something the user can focus and press (7.5.3.1.4).

**Contains**

| Child | How many | What it is |
|---|---|---|
| `meta` | any number, first | Author notes (`meta` below) |
| `p` | 0 or 1 | The label |

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `accessKey` | access keys | no |  | Remote keys that press the button directly, wherever the focus is (`VK_MENU`, `VK_TOP_MENU`, `VK_A_BUTTON` on disc). Pressing one sets `state:actioned` on it |
| `class` | names | no |  | Group names, matched by `class()` in paths and by script |
| `state:enabled` | boolean | no | `true` | `false`: it cannot be focused or activated (§14.10) |
| `style` | IDREFS | no |  | Named styles to apply (§14.6) |
| `state:pointer` | boolean | no | `false` | A pointer is over it (§14.10) |
| `state:focused` | boolean | no | `false` | It has the focus (§14.10) |
| `state:actioned` | boolean | no | `false` | It is being pressed (§14.10) |
| `state:value` | boolean or string | no |  | Its value (§14.10) |
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

**Style attributes** (§14.9)

| Group | Attributes |
|---|---|
| Position and size | `position`, `x`, `y`, `anchor`, `width`, `height`, `inlineProgressionDimension`, `blockProgressionDimension`, `zIndex` |
| Showing and hiding | `display`, `visibility`, `opacity` |
| Background and image | `backgroundColor`, `backgroundImage`, `backgroundFrame`, `backgroundPositionHorizontal`, `backgroundPositionVertical`, `backgroundRepeat`, `contentWidth`, `contentHeight`, `scaling`, `crop`, `flip` |
| Border and padding | `border`, `borderStart`, `borderEnd`, `borderBefore`, `borderAfter`, `padding`, `paddingStart`, `paddingEnd`, `paddingBefore`, `paddingAfter` |
| Text | `displayAlign`, `breakBefore`, `breakAfter` |
| Focus navigation | `navUp`, `navDown`, `navLeft`, `navRight`, `navLeftUp`, `navLeftDown`, `navRightUp`, `navRightDown`, `navIndex` |

### `input`

A text field (7.5.3.1.8). Its text is its `state:value`.

**Contains**

| Child | How many | What it is |
|---|---|---|
| `meta` | any number, first | Author notes (`meta` below) |
| `p` | 0 or 1 | The label |

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `mode` | enum `password` \| `singleline` \| `multiline` \| `display` | no | `singleline` | Kind of field; `display` shows text without editing |
| `accessKey` | access keys | no |  | As `button` |
| `class` | names | no |  | Group names, matched by `class()` in paths and by script |
| `state:enabled` | boolean | no | `true` | `false`: it cannot be focused or activated (§14.10) |
| `style` | IDREFS | no |  | Named styles to apply (§14.6) |
| `state:pointer` | boolean | no | `false` | A pointer is over it (§14.10) |
| `state:focused` | boolean | no | `false` | It has the focus (§14.10) |
| `state:actioned` | boolean | no | `false` | It is being pressed (§14.10) |
| `state:value` | boolean or string | no |  | Its value (§14.10) |
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

**Style attributes** (§14.9)

| Group | Attributes |
|---|---|
| Position and size | `width`, `height`, `inlineProgressionDimension`, `blockProgressionDimension` |
| Showing and hiding | `display`, `visibility`, `opacity` |
| Background and image | `backgroundColor`, `backgroundImage`, `backgroundFrame`, `backgroundPositionHorizontal`, `backgroundPositionVertical`, `backgroundRepeat`, `contentWidth`, `contentHeight`, `scaling`, `crop`, `flip` |
| Border and padding | `border`, `borderStart`, `borderEnd`, `borderBefore`, `borderAfter`, `padding`, `paddingStart`, `paddingEnd`, `paddingBefore`, `paddingAfter` |
| Text | `font`, `fontSize`, `fontStyle`, `color`, `lineHeight`, `textAlign`, `textIndent`, `displayAlign`, `textAltitude`, `textDepth`, `wrapOption`, `direction`, `writingMode`, `linefeedTreatment`, `whiteSpaceCollapse`, `whiteSpaceTreatment`, `suppressAtLineBreak`, `breakBefore`, `breakAfter` |
| Focus navigation | `navUp`, `navDown`, `navLeft`, `navRight`, `navLeftUp`, `navLeftDown`, `navRightUp`, `navRightDown`, `navIndex` |

### `object`

Embedded media (7.5.3.1.10).

**Contains**

| Child | How many | What it is |
|---|---|---|
| `meta` | any number, first | Author notes (`meta` below) |
| `param` | any number | A named value for the object |
| `area` | any number | A clickable part of the image |
| `p` | 0 or 1 | Text shown with it |

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `type` | enum `image/jpeg` \| `image/png` \| `image/cvi` \| `image/cdw` \| `image/mng` \| `audio/x-wav` \| `application/x-clearrect` \| `application/x-graphic` | **yes** |  | What the object is. `application/x-clearrect` clears its box on the graphics plane so video shows through; `audio/x-wav` is an effect sound |
| `src` | URI | no |  | The media file |
| `content` | IDREF | no |  | Element whose content the object presents |
| `class` | names | no |  | Group names, matched by `class()` in paths and by script |
| `state:enabled` | boolean | no | `true` | `false`: it cannot be focused or activated (§14.10) |
| `style` | IDREFS | no |  | Named styles to apply (§14.6) |
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

**Style attributes** (§14.9)

| Group | Attributes |
|---|---|
| Position and size | `position`, `x`, `y`, `anchor`, `width`, `height`, `inlineProgressionDimension`, `blockProgressionDimension`, `zIndex` |
| Showing and hiding | `display`, `visibility`, `opacity` |
| Background and image | `backgroundColor`, `backgroundImage`, `backgroundFrame`, `backgroundPositionHorizontal`, `backgroundPositionVertical`, `backgroundRepeat`, `contentWidth`, `contentHeight`, `scaling`, `crop`, `flip` |
| Border and padding | `border`, `borderStart`, `borderEnd`, `borderBefore`, `borderAfter`, `padding`, `paddingStart`, `paddingEnd`, `paddingBefore`, `paddingAfter` |
| Text | `displayAlign`, `breakBefore`, `breakAfter` |

### `param`

A named value for its parent `object` or `event` (7.5.3.1.12).

**Contains**

| Child | How many | What it is |
|---|---|---|
| text | any amount | May carry the value instead of the `value` attribute |

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `name` | string | **yes** |  | Name of the value |
| `value` | string | no |  | The value |
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

### `area`

A clickable part of an `object`, as in an HTML image map (7.5.3.1.1).

**Contains:** nothing.

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `shape` | enum `circle` \| `poly` \| `rect` \| `default` | no | `default` | Shape of the part; `default` is the whole object |
| `coords` | non-negative integers, space-separated | no |  | Shape coordinates, HTML image-map convention |
| `accessKey` | access keys | no |  | As `button` |
| `class` | names | no |  | Group names, matched by `class()` in paths and by script |
| `state:enabled` | boolean | no | `true` | `false`: it cannot be focused or activated (§14.10) |
| `style` | IDREFS | no |  | Named styles to apply (§14.6) |
| `state:pointer` | boolean | no | `false` | A pointer is over it (§14.10) |
| `state:focused` | boolean | no | `false` | It has the focus (§14.10) |
| `state:actioned` | boolean | no | `false` | It is being pressed (§14.10) |
| `state:value` | boolean or string | no |  | Its value (§14.10) |
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

**Style attributes** (§14.9)

| Group | Attributes |
|---|---|
| Position and size | `width`, `height`, `inlineProgressionDimension`, `blockProgressionDimension` |
| Showing and hiding | `display`, `visibility`, `opacity` |
| Background and image | `backgroundColor`, `backgroundImage`, `backgroundFrame`, `backgroundPositionHorizontal`, `backgroundPositionVertical`, `backgroundRepeat`, `contentWidth`, `contentHeight`, `scaling`, `crop`, `flip` |
| Border and padding | `border`, `borderStart`, `borderEnd`, `borderBefore`, `borderAfter`, `padding`, `paddingStart`, `paddingEnd`, `paddingBefore`, `paddingAfter` |
| Text | `color`, `displayAlign` |
| Focus navigation | `navUp`, `navDown`, `navLeft`, `navRight`, `navLeftUp`, `navLeftDown`, `navRightUp`, `navRightDown`, `navIndex` |

### `meta`

Author notes (7.5.3.1.9). Ignored by rendering. On disc always empty (329).

**Contains**

| Child | How many | What it is |
|---|---|---|
| any element from another namespace | any number | Whatever the author put there |

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| any attribute from another namespace | string | no |  | Whatever the author put there |
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

### `include`

Pulls another document in at this point (7.5.3.1.7). On disc: `body` includes
`.xmu` 23 times, `head` includes `.xss` 11 and `.xts` 2.

**Contains:** nothing.

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `href` | URI | **yes** |  | The document: a `.xmu` fragment inside `body`; a `.xts` (a `timing`) or `.xss` (a `styling`) inside `head` |
| `condition` | string | no |  | Condition for including it (unused on disc) |
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

## 14.6 Styling

Styles can be given three ways, all with the same `style:` attributes (§14.9):

1. **Inline**: `style:` attributes on the element itself.
2. **Named**: a `style` element with an `id` in `head/styling`. An element lists
   the ids it uses in its `style` attribute; a `style` can build on others the
   same way.
3. **Selected**: a `style` element with `select` applies to every element the
   path matches.

Precedence between the three is not in the available sources. Apply them in the
CSS order that HDi's model follows [15]: named or selected styles first, in
document order, then inline attributes, which win. **INFERRED**.

### `styling`

A block of styles (7.6.3.1.1).

**Contains**

| Child | How many | What it is |
|---|---|---|
| `meta` | any number, first | Author notes (`meta` below) |
| `style` | any number | One style |

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

### `style`

One style (7.6.3.1.2). On disc: 88 `style` elements; named styles referenced
387 times (`defaultStyles`, `defaultStyles keyStyle`, …); `select` is unused.

**Contains**

| Child | How many | What it is |
|---|---|---|
| `meta` | any number | Author notes |

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `id` | ID | no |  | Name other elements use in their `style` attribute |
| `style` | IDREFS | no |  | Other named styles this one builds on |
| `select` | path | no |  | Elements this style applies to |
| every `style:` attribute | §14.9 | no |  | The style values; all 61 are allowed here |
| `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common |

## 14.7 Timing

Timing makes the page change over time and react to input. It lives in
`head/timing` (or an included `.xts`), apart from the content it acts on: each
`cue` selects the elements it changes.

**Clocks.** Every timing section runs on one clock, chosen by `timing@clock`:

| Clock | Runs | Used for |
|---|---|---|
| `title` (default) | locked to the title timeline (media time): pauses and seeks with the video | cues at specific movie times (in-movie overlays) |
| `page` | from when the page is loaded, independent of the video | menus: effects keep playing while the video is paused |
| `application` | for the application's whole active life | timers shared across pages |

Page and application clocks tick at `TitleSet@tickBase`, reduced by
`Title@tickBaseDivisor` ([03](03_playlist.md) §3.7, §3.8). On disc: `page` 68,
`application` 9, `title` 3, omitted 8. ([05](05_manifest_hdi.md) §5.2.)

### `timing`

A timing section (7.7.2.9.10).

**Contains**

| Child | How many | What it is |
|---|---|---|
| `defs` | any number, first | Reusable effects |
| `par` | any number, in any order with `seq` | Children run at the same time |
| `seq` | any number | Children run one after another |

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `clock` | enum `title` \| `application` \| `page` | no | `title` | The clock (above) |
| `timeContainer` | enum `par` \| `seq` | no | `par` | How the top-level containers run |
| `begin`, `end` | time or path | no |  | Active interval of the whole section |
| `dur` | time | no |  | Its length |
| `clockDivisor` | positive integer | no | `1` | **v1.0 only**, removed in v1.1 |
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

### `par` and `seq`

Time containers, as in SMIL (7.7.2.9.7–8): the children of `par` run at the
same time; the children of `seq` run one after another.

**Contains**

| Child | How many | What it is |
|---|---|---|
| `cue` | any number, in any order with `par` and `seq` | One timed action |
| `par` | any number | A nested container |
| `seq` | any number | A nested container |

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `begin`, `end` | time or path | no |  | When the container starts and stops |
| `dur` | time | no |  | Its length |
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

### `cue`

The unit of action (7.7.2.9.2): while it is active, it applies its effects to
the elements it selects.

**Contains**

| Child | How many | What it is |
|---|---|---|
| `animate` | any number, in any order with `set` and `event` | Change values over time |
| `set` | any number | Set values |
| `event` | any number | Notify script |
| `link` | exactly 1, **instead of** all the above | Switch to another page |

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `select` | path | no |  | The elements the cue acts on. Absent: the element its `begin` path matched (`defaultNode()`, §14.8) |
| `begin` | time or path | no |  | When it starts: a time, or the moment a condition becomes true (`id('BT_play')[state:focused()=true()]`) |
| `end` | time or path | no |  | When it stops |
| `dur` | time | no |  | Its length, instead of `end` |
| `use` | IDREFS | no |  | `g` elements in `defs` whose effects apply as if written inside the cue |
| `fill` | enum `remove` \| `hold` | no | `remove` | After the cue ends: `remove` undoes its effects, `hold` keeps the final values |
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

### `defs`

Reusable effects (7.7.2.9.3), used by a `cue` through `use`.

**Contains**

| Child | How many | What it is |
|---|---|---|
| `g` | any number, in any order with the rows below | A named group of effects |
| `animate` | any number |  |
| `set` | any number |  |
| `event` | any number |  |
| `link` | any number |  |

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

### `g`

A named group of effects (7.7.2.9.5); a `cue` applies it by listing its `id` in
`use`.

**Contains**

| Child | How many | What it is |
|---|---|---|
| `g` | any number, in any order with the rows below | A nested group |
| `animate` | any number |  |
| `set` | any number |  |
| `event` | any number |  |

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

### `set`

While active, sets style and state attributes of the selected elements
(7.7.2.9.9). Example: `<set style:backgroundFrame="1"/>` shows the focused
image.

**Contains:** nothing.

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| any animatable style attribute (§14.9) | its own type | no |  | The value to set |
| `state:enabled`, `state:focused`, `state:value` | §14.10 | no |  | The state to set |
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

### `animate`

Changes attributes over the cue's duration through keyframes spread evenly
across it (7.7.2.9.1): `<animate style:opacity="0;0.5;1"/>`.

**Contains:** nothing.

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `calcMode` | enum `linear` \| `discrete` | no | `linear` | Interpolate between keyframes, or jump |
| `additive` | enum `replace` \| `sum` | no | `replace` | Replace the attribute's value, or add to it |
| any animatable style attribute (§14.9) | keyframe list | no |  | The keyframes |
| `state:enabled`, `state:focused`, `state:value` | keyframe list | no |  | The keyframes |
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

### `event`

Fires a DOM event when the cue starts (7.7.2.9.4), aimed at the cue's selected
elements (**INFERRED**). Script receives it with `addEventListener(name, …)`.

**Contains**

| Child | How many | What it is |
|---|---|---|
| `param` | any number | The event's data |

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `name` | name (`xs:NMTOKEN`) | **yes** |  | The event's name |
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

### `link`

Switches the application to another markup page (7.7.2.9.6). The current page is
replaced; the application and its File Cache stay [1]. On disc: 12, all in
`OLIVER_TWIST_JPN` menus.

**Contains:** nothing.

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `href` | URI | **yes** |  | The `.xmu` to switch to |
| `xml:base` | URI | no |  | Base for `href` |
| `id` | ID | no |  | v1.1 only |

### Rules

From SMIL 2.0 [18] and [12](12_hdi_scripting_abi.md) §12.4:

- A cue whose `begin` is a path starts when the path becomes true and ends when
  its `end` becomes true (or after `dur`). It can start again the next time
  `begin` is true.
- Evaluate path conditions on every clock tick and on every focus, action or
  state change.
- A cue's timing never outlives its application: the application's valid period
  on the title timeline ([03](03_playlist.md) §3.13) gates everything.

On disc: `cue` 1239, `set` 579, `event` 510, `animate` 483, `par` 204, `seq` 33,
`defs` 54, `g` 8, `link` 12; `fill` only `hold` (176); `calcMode` only `linear`
(24); `additive` only `sum` (12).

## 14.8 Path expressions

`begin`, `end` and `select` on timing elements, and `select` on `style`, take a
path expression (`PathExpressionType`, Spec. 7.5.2.4). It is **XPath 1.0**
evaluated over the markup document, with the `state:` and `style:` namespaces
bound, the page's variables, and these functions:

| Function | Returns | Meaning |
|---|---|---|
| `id('x')`, `id($v)` | node-set | The element with that `id` (XPath standard) |
| `class('c')`, `class($v)` | node-set | Every element whose `class` contains `c` (iHD extension) |
| `defaultNode()` | node-set | The cue's default node: the element its `begin` matched. On disc it appears only in the `end` of timing elements (192 `cue`, 1 `par`) that have no `select` and whose `begin` names one element, as `defaultNode()[state:focused()=false()]`: "end when that element loses focus". **INFERRED** |
| `state:focused()`, `state:actioned()`, `state:enabled()`, `state:pointer()`, `state:value()`, `state:foreground()` | boolean or string | The state attribute (§14.10) of the context node |
| `style:x()`, `style:opacity()`, … (one per style attribute) | string | The current value of that style attribute of the context node; with a node argument (`style:x(id('focusToggle'))`), of that node |
| `true()`, `false()`, `not()`, `boolean()` | boolean | XPath standard |

Also: location paths (`//button`, `//body`), predicates `[…]`, attribute tests
(`@state:focused='true'`, `@id=$focus`), unions `|`, comparisons `=` `!=`,
`and`, number and string literals, and `$name` variables that script sets with
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

## 14.9 Style attributes

All in the `ihd#style` namespace (Spec. 7.6.3.3.2.*), grouped by what they do.

- **Type** uses the names from §14.3. Every attribute also accepts `inherit`
  except `anchor`, `crop`, `flip` and `navIndex`.
- **Anim.** = animatable: the value may be a keyframe list, and the attribute
  can be used in `set` and `animate`.
- **Allowed on** is the element's style group in the v1.1 schema. Every
  attribute is also allowed on `style` (§14.6).
- **On disc** counts the attribute on any element in the corpus.

Meanings marked "XSL-FO semantics" follow that standard; the rest are verified
on disc or follow directly from the name and values
([05](05_manifest_hdi.md) §5.9 for the used rendering rules). Directions: in the
default writing mode `lr-tb`, *start* = left, *end* = right, *before* = top,
*after* = bottom.

### Position and size

| Attribute | Type | Default | Anim. | Allowed on | On disc | What it is for |
|---|---|---|---|---|---|---|
| `position` | enum `static` \| `relative` \| `absolute` | `static` | | button, div, object | 1462 | `absolute`: the box is placed at `x`, `y` in its parent. `static` and `relative` follow flow layout |
| `x` | length or `auto` | `0px` | yes | button, div, object | 1763 | Horizontal position of the anchor point, relative to the parent |
| `y` | length or `auto` | `0px` | yes | button, div, object | 1913 | Vertical position of the anchor point, relative to the parent |
| `anchor` | enum `startBefore` \| `centerBefore` \| `endBefore` \| `startCenter` \| `center` \| `endCenter` \| `startAfter` \| `centerAfter` \| `endAfter` | `startBefore` | yes | button, div, object | 31 | Which point of the box is placed at (`x`, `y`): start / center / end across, Before / Center / After down; `center` is the middle |
| `width` | length or `auto` | `auto` | yes | area, body, button, div, input, object, p | 1668 | Box width |
| `height` | length or `auto` | `auto` | yes | area, body, button, div, input, object, p | 1665 | Box height |
| `inlineProgressionDimension` | length or `auto` | `auto` | yes | area, body, button, div, input, object, p | 0 | XSL-FO name for the size along a line (the width in `lr-tb`) |
| `blockProgressionDimension` | length or `auto` | `auto` | yes | area, body, button, div, input, object, p | 0 | XSL-FO name for the size across lines (the height in `lr-tb`) |
| `zIndex` | integer or `auto` | `auto` | yes | button, div, object | 19 | Stacking order among siblings; higher is drawn on top |

### Showing and hiding

| Attribute | Type | Default | Anim. | Allowed on | On disc | What it is for |
|---|---|---|---|---|---|---|
| `display` | enum `auto` \| `none` | `auto` | yes | area, body, br, button, div, input, object, p, span | 1641 | `none` removes the element and its children from rendering (it stays in the navigation graph); `auto` shows it |
| `visibility` | enum `visible` \| `hidden` | `visible` | yes | area, body, br, button, div, input, object, p, span | 11 | `hidden` hides the element but keeps its space and navigation |
| `opacity` | number 0–1 | `1.0` | yes | area, body, br, button, div, input, object, p, span | 1526 | Alpha multiplied into the element and its children: 0 invisible, 1 opaque |

### Background and image

| Attribute | Type | Default | Anim. | Allowed on | On disc | What it is for |
|---|---|---|---|---|---|---|
| `backgroundColor` | colour | `transparent` | yes | area, body, br, button, div, input, object, p, span | 4 | Colour filling the box behind its content |
| `backgroundImage` | URL list | `none` | yes | area, body, button, div, input, object | 1357 | The box's images; one is shown at a time, chosen by `backgroundFrame`. Long lists are animation strips |
| `backgroundFrame` | integer | `0` | yes | area, body, button, div, input, object | 114 | Which image of `backgroundImage` is shown, counting from 0. Menus use 0 normal, 1 focused, 2 pressed |
| `backgroundPositionHorizontal` | length, or enum `left` \| `center` \| `right` | `0%` | yes | area, body, button, div, input, object | 6 | Horizontal position of the background image in the box |
| `backgroundPositionVertical` | length, or enum `top` \| `center` \| `bottom` | `0%` | yes | area, body, button, div, input, object | 3 | Vertical position of the background image in the box |
| `backgroundRepeat` | enum `repeat` \| `no-repeat` | `no-repeat` | | area, body, button, div, input, object | 0 | Whether the background image is tiled |
| `contentWidth` | length, `auto` or `scale-to-fit` | `auto` | yes | area, body, button, div, input, object | 116 | Width of the image drawn inside the box, as `contentHeight` |
| `contentHeight` | length, `auto` or `scale-to-fit` | `auto` | yes | area, body, button, div, input, object | 115 | Height of the image drawn inside the box: `auto` = its own size, `scale-to-fit` = fit the box |
| `scaling` | enum `uniform` \| `non-uniform` | `non-uniform` | | area, body, button, div, input, object | 1 | `uniform` keeps the image's aspect ratio when fitting; `non-uniform` stretches |
| `crop` | four non-negative integers, or `auto` | `auto` | yes | area, body, button, div, input, object | 0 | Part of the source image to use; `auto` = all of it. Order of the four numbers not in the sources |
| `flip` | enum `none` \| `inlineProgression` \| `blockProgression` \| `both` | `none` | yes | area, body, button, div, input, object | 0 | Mirror the content across the inline axis, the block axis, or both |

### Border and padding

| Attribute | Type | Default | Anim. | Allowed on | On disc | What it is for |
|---|---|---|---|---|---|---|
| `border` | border | `None` | yes | area, body, button, div, input, object, p | 0 | Border on all four sides |
| `borderStart`, `borderEnd`, `borderBefore`, `borderAfter` | border | `None` | yes | area, body, button, div, input, object, p | 0 | Border on one side |
| `padding` | 1–4 non-negative lengths, space-separated | `0px` | yes | area, body, button, div, input, object, p | 0 | Space between border and content on all sides (CSS order) |
| `paddingStart`, `paddingEnd`, `paddingBefore`, `paddingAfter` | non-negative length | `0px` | yes | area, body, button, div, input, object, p | 0 | Padding on one side |

### Text

| Attribute | Type | Default | Anim. | Allowed on | On disc | What it is for |
|---|---|---|---|---|---|---|
| `font` | font | `None` | yes | body, div, input, p, span | 47 | The font file, optionally with a family name |
| `fontSize` | 1 or 2 non-negative lengths, or enum `xx-small` \| `x-small` \| `small` \| `medium` \| `large` \| `x-large` \| `xx-large` \| `smaller` \| `larger` | `medium` | yes | body, div, input, p, span | 55 | Text size; two lengths give horizontal and vertical size separately |
| `fontStyle` | enum `normal` \| `italic` \| `oblique` \| `backslant` \| `reverse-oblique` | `normal` | yes | body, div, input, p, span | 0 | Upright, italic or slanted text |
| `color` | colour | `white` | yes | area, body, div, input, p, span | 50 | Text colour |
| `lineHeight` | length or `auto` | `auto` | yes | body, div, input, p | 37 | Height of each line of text |
| `textAlign` | enum `start` \| `center` \| `end` | `start` | yes | body, div, input, p | 0 | Alignment of lines |
| `textIndent` | length | `0px` | yes | body, div, input, p | 0 | Indent of the first line |
| `displayAlign` | enum `auto` \| `before` \| `center` \| `after` | `auto` | yes | area, body, button, div, input, object, p | 0 | Alignment of the content across lines (top / middle / bottom in `lr-tb`) |
| `textAltitude` | length or `auto` | `auto` | yes | input, p, span | 0 | Height of the text area above the baseline |
| `textDepth` | length or `auto` | `auto` | yes | input, p, span | 0 | Depth of the text area below the baseline |
| `wrapOption` | enum `wrap` \| `no-wrap` | `wrap` | yes | body, div, input, p, span | 0 | Whether long lines wrap |
| `direction` | enum `ltr` \| `rtl` | `ltr` | | body, div, input, p, span | 0 | Text direction |
| `writingMode` | enum `lr-tb` \| `rl-tb` \| `tb-rl` | `lr-tb` | | body, div, input | 0 | Line and page direction: left-to-right top-to-bottom, right-to-left, or vertical (Japanese) |
| `linefeedTreatment` | enum `ignore` \| `preserve` \| `treat-as-space` \| `treat-as-zero-width-space` | `treat-as-space` | | body, div, input, p, span | 0 | What a line feed in the text does (XSL-FO semantics) |
| `whiteSpaceCollapse` | enum `true` \| `false` | `true` | | body, div, input, p | 0 | Whether runs of spaces collapse to one (XSL-FO semantics) |
| `whiteSpaceTreatment` | enum `ignore` \| `preserve` \| `ignore-before` \| `ignore-after` \| `ignore-around` | `ignore-around` | | body, div, input, p | 0 | Which spaces around line breaks are removed (XSL-FO semantics) |
| `suppressAtLineBreak` | enum `auto` \| `suppress` \| `retain` | `auto` | | input, span | 0 | Whether this inline content is dropped at a line break (XSL-FO semantics) |
| `breakBefore`, `breakAfter` | enum `auto` \| `line` | `auto` | | br, button, input, object, span | 0 | `line` forces a line break before / after this inline element |

### Focus navigation

These build the graph the focus moves along when the user presses the arrow
keys on the remote.

| Attribute | Type | Default | Anim. | Allowed on | On disc | What it is for |
|---|---|---|---|---|---|---|
| `navUp`, `navDown`, `navLeft`, `navRight` | IDREF or `none` | `none` | yes | area, button, input | 405 each | `id` of the element that gets the focus when the user presses that arrow; `none` = the focus stays |
| `navLeftUp`, `navLeftDown`, `navRightUp`, `navRightDown` | IDREF or `none` | `none` | yes | area, button, input | 5 each | As above, for the diagonal keys |
| `navIndex` | two non-negative integers, `auto` or `none` | `auto` | yes | area, button, input | 2 | Order for sequential navigation. `none` removes the element from remote navigation; `auto` = document order |

On disc: `position` is always `absolute` (1462/1462); `display` is `inherit`
1054 times, `auto` 473, `none` 114; `opacity` is `inherit` 1043 times, and
keyframe lists appear on `animate`; `contentWidth` / `contentHeight`
`scale-to-fit` 41 / 40. `writingMode`, `padding*`, `border*`, `direction`,
`displayAlign`, `whiteSpace*`, `textAlign` and the text-metric attributes are
never used; implement them from the schema and XSL-FO when a disc needs them.

`[5, 11, 12]` **VERIFIED** (names, types, values, defaults, placement);
meanings of the unused attributes **INFERRED** (XSL-FO / CSS).

## 14.10 State attributes

In the `ihd#state` namespace (Spec. 7.6.3.4.2.*). They describe what the user is
doing to an element. The player keeps them up to date; markup can set initial
values; `set`, `animate` and script can change the animatable ones; paths read
them with `state:…()`.

| Attribute | Type | Default | Anim. | On | What it is for |
|---|---|---|---|---|---|
| `enabled` | boolean | `true` | yes | `body`, `br`, `object`, `div`, `p`, `span`, `button`, `input`, `area` | `false`: the element cannot be focused or activated |
| `focused` | boolean | `false` | yes | `button`, `input`, `area` | The element has the focus. One element on a page has it; moving the focus sets the old one `false` and the new one `true`. Set `true` in markup to choose the initial focus; otherwise it is the first focusable element in document order |
| `actioned` | boolean | `false` | no (v1.1) | `button`, `input`, `area` | The element is being pressed: Enter on the focused element, one of its `accessKey` keys, or a pointer click. True while the press lasts |
| `pointer` | boolean | `false` | no | `div`, `p`, `span`, `button`, `input`, `area` | A pointer (cursor) is over the element |
| `value` | boolean or string | | yes | `button`, `input`, `area` | The element's value: the text of an `input` |
| `foreground` | boolean | `false` | no | `body` | See `body` (§14.5) |

On disc: `state:value` 113 (all on `input`), `state:focused` 33 (initial focus),
`state:enabled` 1.

## 14.11 v1.0 and v1.1

Retail discs validate against both schema versions (§14.12); read against v1.1
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

## 14.12 On disc

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
