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
semantics", those standards give the meaning; the book's chapter 7 [23 §7.5–7.9]
restates them and adds the HDi rules.

Sources: the DVD Forum book v1.01 [23 §7] (element syntax, every style
property's domain, initial value, inheritance and animation mode, the timing and
focus models), the DVD Forum schemas [5] (v1.0 and v1.1), the HDi Jumpstart
posts [14], and the corpus, checked by `e27` (every markup document) with the
earlier `e15` / `e17`. The book matches the v1.0 schema where the two schemas
differ (§14.11).

**How to read this sheet.** Start with the tree (§14.2), which shows every
element and where it can go. §14.3 defines each value type once; every table
after it uses those type names. §14.4 lists the attributes many elements share,
and every element section (§14.5–14.7) has a table of what it contains and a
table of all its attributes. §14.9 is the full list of style attributes, and
§14.12 lists what a reader has to keep while reading a page.

## 14.1 Files, namespaces, versions

| File | Root element | What it holds |
|---|---|---|
| `.xmu` | `root` | A markup page: `head` (styles, timing) and `body` (content) |
| `.xts` | `timing` | A timing section on its own, pulled into a page's `head` by `include` |
| `.xss` | `styling` | A styling section on its own, pulled into `head` by `include`. An included file holds only a `div`, a `styling` or a `timing` [23 §7.4.1] |
| `.xas` | `root` | Advanced Subtitle markup; same document model with the restrictions of §14.13a |

| Namespace | Prefix used here | Contains |
|---|---|---|
| `http://www.dvdforum.org/2005/ihd` | (none) | elements and their plain attributes |
| `http://www.dvdforum.org/2005/ihd#style` | `style:` | the style attributes (§14.9) |
| `http://www.dvdforum.org/2005/ihd#state` | `state:` | the state attributes (§14.10) |
| `http://www.w3.org/XML/1998/namespace` | `xml:` | `xml:lang`, `xml:base`, `xml:space` |

Schemas: `spec/raw/adv_obj/v1.1/iHD.xsd` (imports `iHDstyle.xsd` and
`iHDstate.xsd`); v1.0 for reference. Differences in §14.11. The corpus
validates against both except for one document (§14.13).

**Reading rules.**

- XML in UTF-8, or UTF-16 with a byte-order mark [23 §6.2.1]. Match by
  namespace and local name, never by prefix.
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
| positive integer | `[1-9][0-9]*` | unsigned integer, at least 1 | only `timing@clockDivisor` (v1.0) |
| number | decimal, `0.5` | fraction | only `opacity`, 0 to 1 |
| string | any text | text | |
| enum | one of the listed words | one of a fixed set | the tables list every allowed word |
| ID | an XML name (`BT_play`) | text | unique in the document |
| IDREF | an ID | text | names another element |
| IDREFS | IDs separated by spaces | list of texts | |
| name | one XML name token (`xs:NMTOKEN`) | text | only `event@name` |
| names | names separated by spaces (`xs:NMTOKENS`) | list of texts | `class` |
| language | a language tag (`en`, `en-us`) | text | `xml:lang` |
| URI | `file:///dvddisc/…`, `…/x.aca/member`, or relative | text, kept as written | relative URIs resolve against `xml:base`, then the document's own location |
| URL list | `url('a.png') url('b.png')` or `none` | list of URIs, or none | `backgroundImage` |
| time | `HH:MM:SS`, `HH:MM:SS:FF` (hours may have more than two digits), or a decimal with a unit: `h`, `m`, `s`, `ms`, `f` (`0.5s`, `500ms`, `9f`) | either a clock value (hours, minutes, seconds, frames) or an amount with a unit | `f` counts frames of the element's clock (§14.7): the title timeline's frame rate on the title clock, the tick rate on page and application clocks (**INFERRED**). Keep the unit: the frame length is known only once the clock is |
| path | an XPath 1.0 expression (§14.8) | text, kept as written | evaluated while the page runs, not when it is read |
| time or path | a time, or a path | tagged: a time or a path | a value that matches the time syntax is a time; anything else is a path |
| length | a whole number followed by its unit, no space: `100px`, `2em`, `50%`, `-12px` | one signed whole number + one unit (`px`, `em` or `%`) | Never a fraction (`12.5px` is invalid). Negative values are allowed everywhere except `padding*` and `fontSize`. `px` are graphics-plane pixels (the playlist `Aperture`, normally 1920×1080). `1em` is the block-direction font size (with `fontSize="32px 48px"`, `1em` = `48px`) [23 §7.6.2]. The book calls `%` values *percentage*, a separate type. Words such as `auto` are not lengths; the attribute's own type lists them |
| percentage | a whole number followed by `%`: `50%` | one whole number | A length whose unit is `%` |
| colour | `#rgb`, `#rrggbb`, `rgb(r,g,b)`, `rgba(r,g,b,a)` (each 0–255 or a %), one of 16 names, or `transparent` | red, green, blue, alpha | CSS2 §4.3.6 in sRGB, plus `rgba()` whose fourth value is opacity (0 or 0% transparent, 255 or 100% opaque); CSS system colours are not allowed [23 §7.6.2]. Names: `aqua black blue fuchsia gray green lime maroon navy olive purple red silver teal white yellow`. `transparent` = `rgba(0,0,0,0)` |
| access keys | space-separated keys: `U+XXXX` (4–6 hex digits, a Unicode character) or a virtual key `VK_…` | list of keys, each a character code or a virtual key | virtual keys listed below |
| border | `width? style? colour?`, space-separated | width (a length), style, colour | style `none` \| `hidden` \| `solid`; a missing part takes its initial value: width `3px`, style `none`, colour = the element's computed `color` [23 §7.6.2, §7.6.3.3.2.9–13] |
| font | a URI, optionally followed by a full font name in single quotes: `file:///dvddisc/ADV_OBJ/font.ttc 'Helvetica-Italic'` | URI + optional full font name | an OpenType file (`.ttf`, `.otf`, `.ttc`) in the File Cache; players have no built-in fonts. The name must equal a full font name in the file's `name` table; absent, any font of the file. A missing font file makes the page invalid [23 §7.3.2.2, §7.6.3.3.2.25] |

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
column says exactly which elements have each attribute. The element tables in
§14.5–14.7 repeat these rows, so each element's table is complete on its own.

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
| `state:value` | boolean or string, keyframe list | | `button`, `input`, `area` | The element's value (§14.10). The schema cannot tell `true` the boolean from `true` the text, so keep it as written |

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
| `state:foreground` | boolean | no | `false` | `true` while this page's application is the topmost one in z-order. Set by the player only; markup, `set` and script cannot change it [23 §7.6.3.4.2.1] |
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
| `type` | enum `image/jpeg` \| `image/png` \| `image/cvi` \| `image/cdw` \| `image/mng` \| `audio/x-wav` \| `application/x-clearrect` \| `application/x-graphic` | **yes** |  | What the object is; the referenced file must be of this type or the page is invalid. Behaviour per type in §14.5a |
| `src` | URI | no |  | The media file. Required for the image types and `audio/x-wav`; not used with the two `application/…` types |
| `content` | IDREF | no |  | Another `object` this one shows again (for example one drawing canvas drawn at two places or sizes) [23 §7.5.3.1.10] |
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
| `name` | string | **yes** |  | Name of the value; unique among one object's `param`s |
| `value` | string | no |  | The value. If the element has text, the text is the value and this attribute is ignored |
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

### `area`

A clickable part of an `object`, as in an HTML image map (7.5.3.1.1).

**Contains:** nothing.

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `shape` | enum `circle` \| `poly` \| `rect` \| `default` | no | `default` | Shape of the part; `default` is the whole object |
| `coords` | non-negative integers, space-separated | no |  | Pixel offsets from the top-left of the parent's drawn area: `circle` cx cy r; `poly` x0 y0 x1 y1 …, closed automatically; `rect` left top right bottom; ignored for `default`; extra numbers ignored. Of overlapping sibling areas the later one gets the event [23 §7.5.3.1.1] |
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
`.xmu` 23 times, `head` includes `.xss` 11 and `.xts` 2. It restricts XInclude to
`href` with `parse="xml"`. A file that cannot be found is skipped as if the
`include` were absent; a file that is not a valid document makes the page not
well formed [23 §7.5.3.1.7].

**Contains:** nothing.

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `href` | URI | **yes** |  | The document: a `.xmu` fragment inside `body`; a `.xts` (a `timing`) or `.xss` (a `styling`) inside `head` |
| `condition` | path | no |  | An XPath boolean (§14.8) evaluated with the including page's `body` as context, before any include is merged and without the `style:`/`state:` functions; false: skip this include. Unused on disc [23 §7.5.3.1.7] |
| `id`, `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common to every element |

### 14.5a What each `object` type does

From [23 §7.8]:

| `type` | `param`s | Behaviour |
|---|---|---|
| `image/png`, `image/jpeg`, `image/cvi`, `image/cdw` | none | Drawn like a `button` whose `backgroundImage` is `src`; any other `backgroundImage` is ignored |
| `image/mng` | none | Plays the MNG from its start each time `display` becomes `auto`, unsynchronised; background properties then apply to `backgroundImage`, not the MNG; `crop` does not apply |
| `audio/x-wav` | `AttenuateL`, `AttenuateR`: `0%`–`100%`, default `100%`, linear; `Loop`: integer ≥ 1, default `1`, discrete | Effect sound. No marks, size 0×0. Plays from the start each time `display` becomes `auto`; stops on `display="none"`, at the end of its loops, or when another effect sound starts (one effect sound at a time). Its level is the attenuation (perceptually linear) times the volume script sets |
| `application/x-graphic` | `width`, `height` (like `style:width`/`height`): the initial drawing-area size | A drawing area for the script Drawing API, initially transparent, kept between frames, scaled to the box, drawn src-over the background |
| `application/x-clearrect` | `TargetPlane`: `sub` \| `main`, default `main`, not animatable | Cuts a hole: `sub` through the graphics and sub-picture planes to the sub video; `main` also through the sub-video plane to the main video. Elements drawn after it draw over the hole |

## 14.6 Styling

Styles can be given three ways, all with the same `style:` attributes (§14.9):

1. **Inline**: `style:` attributes on the element itself.
2. **Named**: a `style` element with an `id` in `head/styling`. An element lists
   the ids it uses in its `style` attribute; a `style` can build on others the
   same way.
3. **Selected**: a `style` element with `select` applies to every element the
   path matches.

Precedence [23 §7.6.1]: first every **selected** style, in document order (each
setting its attributes on every node its path matches); then every **named**
style an element lists, left to right, each one's own `style` list expanded
depth-first before its own attributes; then **inline** attributes, which win.
Example: `c` = (`a b`, y 3px), `f` = (`d e`, y 6px), `<p style="c f">` gets the
x of `e` and y 6px. A `style` may only name styles that come earlier in the
document (after includes). Animation (`set`, `animate`, script) applies on top
of all three. An attribute set by none of them is inherited if it is an
inheritable property (§14.9) or `inherit`, else takes its initial value.
`[23]` **SPEC**.

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
| `select` | path | no |  | Elements this style applies to; evaluated from the `body` of the document holding the `styling`, so it cannot reach `head` |
| every `style:` attribute | §14.9 | no |  | The style values; all 61 are allowed here |
| `xml:lang`, `xml:base`, `xml:space` | §14.4 | no |  | Common |

## 14.7 Timing

Timing makes the page change over time and react to input. It lives in
`head/timing` (or an included `.xts`), apart from the content it acts on: each
`cue` selects the elements it changes.

**Clocks.** Every timing section runs on one clock, chosen by `timing@clock`:

| Clock | Runs | Used for |
|---|---|---|
| `title` (default) | locked to the title timeline (media time): pauses and seeks with the video; counted from the start of the application's valid period | cues at specific movie times (in-movie overlays) |
| `page` | from when the current page started presenting, independent of the video | menus: effects keep playing while the video is paused |
| `application` | from when the application's first page started presenting, for its whole active life | timers shared across pages |

A path in `begin` or `end` is allowed only under the page or application clock
and only on a child of a `par`; under the title clock it is a well-formedness
error [23 §7.7.2.10.2]. `fill="hold"` works only under the page and application
clocks [23 §7.7.2.10.6].

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
| `clockDivisor` | positive integer | no | `1` | The section's clock advances only every n-th tick; the frames between repeat. Book and v1.0; removed in v1.1 [23 §7.7.2.10.9] |
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
| `select` | path | no |  | The elements the cue acts on, evaluated when it becomes active. Absent: the nodes matched by the nearest begin path (its own or an ancestor's) that started it (`defaultNode()`, §14.8); none: the cue still occupies time but applies nothing |
| `begin` | time or path | no |  | When it starts: a time, or the moment a condition becomes true (`id('BT_play')[state:focused()=true()]`) |
| `end` | time or path | no |  | When it stops |
| `dur` | time | no |  | Its length. A cue with neither `dur` nor `end` has length zero and does nothing |
| `use` | IDREFS | no |  | Effects in `defs` that apply as if written inside the cue: a `g`, or a single `set`, `animate` or `event`. On disc 256 name a `set`, 141 a `g`, 13 an `animate` |
| `fill` | enum `remove` \| `hold` | no | `remove` | After the cue ends before its parent: `remove` undoes its effects, `hold` keeps the final values until the parent ends. Under the title clock `hold` acts as `remove` |
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

Fires a DOM event when the cue starts (7.7.2.9.4), once per interval of the cue,
aimed at each element the cue selects. Script receives it with
`addEventListener(name, …)`. The event's `type` is `name`, it bubbles and is
cancelable, and each child `param` adds a string property named by its `name`.
It reaches script as a queued work item, after the work already queued, and is
offered to every application in priority order [23 §7.7.2.9.4, §8.3.7].

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

Switches the application to another markup page (7.7.2.9.6) when its interval
first becomes active. The current page is replaced; the application, its script
context and its File Cache stay [1]. If `href` is not a markup page, the
application ends. Several links at once: the first `link` of the first `cue` in
document order wins; nothing else in that interval runs [23 §7.7.2.9.6]. On
disc: 12, all in `OLIVER_TWIST_JPN` menus.

**Contains:** nothing.

**Attributes**

| Attribute | Type | Req. | Default | What it is for |
|---|---|---|---|---|
| `href` | URI | **yes** |  | The `.xmu` to switch to |
| `xml:base` | URI | no |  | Base for `href` |
| `id` | ID | no |  | v1.1 only |

### Rules

The book's subset of SMIL 2.0 [23 §7.7], [18]:

- Not supported: `animateMotion`, `animateColor`, `targetElement`,
  `attributeType`, `href`/`actuate`/`show`/`type` on animations, `calcMode="paced"`,
  `accumulate`, `from`/`by`/`to`, `endsync`, explicit `media` and `indefinite`.
- **Simple duration.** `dur` alone: `dur`. `end` alone: `end` minus the start
  (an `end` time counts from the previous sibling's finish in a `seq`, else from
  the parent's start), at least zero; an unresolved path: indefinite. Both: the
  shorter. Neither: for a container, up to the last child's end (`par`: the
  latest child end; `seq`: the last child's end), indefinite if a child has an
  unresolved path; otherwise zero.
- **In a `par`** a child starts at the parent's start plus a `begin` time, or at
  the first tick its `begin` path is true; it finishes at the earliest of its
  start plus simple duration, its last active child's finish, the parent's
  finish, and (for a path `end`) the first tick that path is true after it
  started. **In a `seq`** the first child starts at the parent's start plus
  `begin`, each next one at the previous one's finish plus `begin`.
- A path time, once resolved, stays until its interval has finished **and** the
  path has gone false again; then it can start a new, separate interval. Time
  resolution is rounded up to the next tick.
- Evaluate path conditions on every clock tick; property functions read the
  values from the start of the tick, before this tick's animation.
- When several cues on one clock animate the same property of a node, the one
  that started latest wins, ties going to the later in document order; across
  clocks, title beats application beats page.
- `animate` interpolates over the simple duration (first value at the start,
  last at the scheduled end); it is ignored if that duration is zero or
  indefinite. `calcMode="discrete"` holds each value until the next one;
  properties whose values cannot be interpolated are discrete.
- Animation changes the property layer only, never the DOM attribute.
- A cue's timing never outlives its application: the application's valid period
  on the title timeline ([03](03_playlist.md) §3.13) gates everything.
- **Inline timing** (`begin`, `dur`, `end`, `timeContainer` on `body`, `div`, `p`,
  `span`) and a `timing` section cannot be mixed in one document. Inline timing is
  for pages with no `area`, `button` or `input`. With it, `body` is a `seq` and
  the others `par`; an element is shown (`display` auto) only while active; a
  child of a `par` needs `dur` or `end` [23 §7.7.2.7].

On disc: `cue` 1239, `set` 579, `event` 510, `animate` 483, `par` 204, `seq` 33,
`defs` 54, `g` 8, `link` 12; `fill` only `hold` (176); `calcMode` only `linear`
(24); `additive` only `sum` (12).

## 14.8 Path expressions

`begin`, `end` and `select` on timing elements, `select` on `style`, and
`condition` on `include` take a path expression (`PathExpressionType`,
[23 §7.5.2.4]). It is an **XPath 1.0** subset evaluated over the markup document
with `body` as the context node, the namespace prefixes in force on the element
holding it, the variables below, and these functions. The grammar keeps
location paths starting with `/` or `@`, name tests (`*`, `prefix:*`, a QName,
and the extension `*:name` = that local name in any namespace), predicates,
`or`, `and`, `=`, `!=`, `<`, `>`, `<=`, `>=`, `+`, `-`, `*`, `div`, `mod`, unary
`-`, `|`, `$variables`, literals, numbers and function calls.

| Function | Returns | Meaning |
|---|---|---|
| `id('x')`, `id($v)` | node-set | The element with that `id` (XPath standard) |
| `class('c')`, `class($v)` | node-set | Every element whose `class` contains `c` (iHD extension) |
| `defaultNode()` | node-set | The cue's default node: the element its `begin` matched. On disc it appears only in the `end` of timing elements (192 `cue`, 1 `par`) that have no `select` and whose `begin` names one element, as `defaultNode()[state:focused()=false()]`: "end when that element loses focus". **INFERRED** |
| `state:focused()`, `state:actioned()`, `state:enabled()`, `state:pointer()`, `state:value()`, `state:foreground()` | boolean or string | The state attribute (§14.10) of the context node |
| `style:x()`, `style:opacity()`, … (one per style attribute) | string | The current value of that style attribute of the context node; with a node argument (`style:x(id('focusToggle'))`), of that node |
| `true()`, `false()`, `not()`, `boolean()` and the rest of the XPath 1.0 library | as XPath | XPath standard. `id()` works only in documents named `.xpl`, `.xmf`, `.xmu`, `.xas`, `.xss`, `.xts` |
| `GPRM(n)` | number | General parameter register `n` (0–63); out of range: −1 |
| `SPRM(n)` | number | System parameter register `n` (0–31); out of range: −1 |

The property functions return the **computed** value as a string in a fixed
form: colours `rgba(R,G,B,A)` with 0–255 integers, lengths `Npx`, URIs
`url('…')`, booleans and numbers as XPath values; `inherit` and relative values
are resolved first; an attribute the element does not support gives `""`
[23 §7.5.2.4.3.2].

**Variables** [23 §7.5.2.4.1, Annex W.2]: one per system parameter, set by the
player (player and capability parameters when the page loads; presentation,
audio, layout and cursor parameters when the path is evaluated), for example
`$playState`, `$titleId`, `$currentAudioTrackNumber`, `$subtitleVisibility`,
`$cursorX`, `$networkConnection`; plus those script sets with
`document.setXPathVariable(name, value)`. The full list is in
[12](12_hdi_scripting_abi.md) §12.7.

Also: location paths (`//button`, `//body`), predicates `[…]`, attribute tests
(`@state:focused='true'`, `@id=$focus`), unions `|`, comparisons `=` `!=`,
`and`, number and string literals, and `$name` variables that script sets with
`document.setXPathVariable(name, value)` ([05](05_manifest_hdi.md) §5.3).

A path in `begin` / `end` is true when XPath `boolean()` of its value is true.
A `select` must give a node-set; anything else selects nothing. A path that
cannot be evaluated is false (the cue does not fire).
`[23 §7.5.2.4]` **SPEC**; the evaluation-failure rule **INFERRED**.

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
  can be used in `set` and `animate`. The book gives each one a mode
  [23 §7.6.3.3.2]: **discrete** (only `set` or `animate calcMode="discrete"`) for
  `anchor`, `backgroundImage`, `border*`, `display`, `displayAlign`, `flip`,
  `font`, `fontStyle`, `nav*`, `navIndex`, `textAlign`, `visibility`, `wrapOption`;
  **linear** (interpolated; the only ones `additive="sum"` works on) for the
  others marked animatable. Properties with animation mode none (no mark in the
  tables) cannot be animated at all.
- **Inherited** when not set [23 §7.6.3.3.2]: `color`, `crop`, `direction`,
  `displayAlign`, `endIndent`, `font`, `fontSize` (its computed value),
  `fontStyle`, `lineHeight`, `linefeedTreatment`, `startIndent`, `textAlign`,
  `textIndent`, `visibility`, `whiteSpaceCollapse`, `whiteSpaceTreatment`,
  `wrapOption`, `writingMode`. Every other property takes its default unless the
  value is `inherit`.
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
| `position` | enum `static` \| `relative` \| `absolute` | `static` | | button, div, object | 1462 | `absolute`: the box is placed with `anchor` at `x`, `y` in the nearest reference area. `relative`: offset from its flow position like XSL `left`/`top`. `static`: flow layout, `x`/`y`/`anchor` ignored. Applies to `div`, `button`, `object` in a block context |
| `x` | length or `auto` | `0px` | yes | button, div, object | 1763 | Horizontal position of the anchor point (absolute) or offset (relative); `%` of the containing block's width |
| `y` | length or `auto` | `0px` | yes | button, div, object | 1913 | Vertical position, as `x`; `%` of the containing block's height |
| `anchor` | enum `startBefore` \| `centerBefore` \| `endBefore` \| `startCenter` \| `center` \| `endCenter` \| `startAfter` \| `centerAfter` \| `endAfter` | `startBefore` | yes | button, div, object | 31 | Which point of the box is placed at (`x`, `y`): start / center / end across, Before / Center / After down; `center` is the middle. Start and end use the outer (border) edges, center the content centre; formulas in [05](05_manifest_hdi.md) §5.9 and [23 Table 7.6.3.3.2.1-1]. Absolute positioning only |
| `width` | length or `auto` | `auto` | yes | area, body, button, div, input, object, p | 1668 | Box width |
| `height` | length or `auto` | `auto` | yes | area, body, button, div, input, object, p | 1665 | Box height |
| `inlineProgressionDimension` | length or `auto` | `auto` | yes | area, body, button, div, input, object, p | 0 | XSL-FO name for the size along a line (the width in `lr-tb`) |
| `blockProgressionDimension` | length or `auto` | `auto` | yes | area, body, button, div, input, object, p | 0 | XSL-FO name for the size across lines (the height in `lr-tb`) |
| `zIndex` | integer or `auto` | `auto` | yes | button, div, object | 19 | Drawing order of absolutely positioned elements within the application; higher is drawn later (on top); equal values keep document order |

### Showing and hiding

| Attribute | Type | Default | Anim. | Allowed on | On disc | What it is for |
|---|---|---|---|---|---|---|
| `display` | enum `auto` \| `none` | `auto` | yes | area, body, br, button, div, input, object, p, span | 1641 | `none` removes the element and its children from layout; such an element cannot take the focus, is skipped by arrow navigation and ignores its `accessKey`. `auto` shows it as block or inline according to the element (`div`, `p`, `body` block; `span`, `br` inline; `button`, `input`, `object` as their parent's context; `area` as its parent) [23 §7.6.3.3.2.21] |
| `visibility` | enum `visible` \| `hidden` | `visible` | yes | area, body, br, button, div, input, object, p, span | 11 | `hidden` hides the element's marks but keeps its space; it can still take the focus and its `accessKey`, but not the pointer. Inherited |
| `opacity` | number 0–1 | `1.0` | yes | area, body, br, button, div, input, object, p, span | 1526 | Alpha of the element's own background and marks, multiplied with each pixel's alpha: 0 invisible, 1 opaque. Not inherited: children are not faded unless they say `inherit`, which is why the discs write `opacity="inherit"` 1043 times |

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
| `crop` | four non-negative integers, or `auto` | `auto` | yes | area, body, button, div, input, object | 0 | Part of the source image to use, as a rectangle `left top right bottom` in image pixels, cut to the image; `auto` = all of it. Applies to the background image and to image objects other than MNG. Inherited [23 §7.6.3.3.2.19] |
| `flip` | enum `none` \| `inlineProgression` \| `blockProgression` \| `both` | `none` | yes | area, body, button, div, input, object | 0 | Mirror the content across the inline axis, the block axis, or both |

### Border and padding

| Attribute | Type | Default | Anim. | Allowed on | On disc | What it is for |
|---|---|---|---|---|---|---|
| `border` | border | width `3px`, style `none`, colour = `color` | yes | area, body, button, div, input, object, p | 0 | Border on all four sides (block elements) |
| `borderStart`, `borderEnd`, `borderBefore`, `borderAfter` | border | as `border` | yes | area, body, button, div, input, object, p | 0 | Border on one side |
| `padding` | 1, 2 or 4 non-negative lengths, space-separated | `0px` | yes | area, body, button, div, input, object, p | 0 | Space between border and content. One value: all sides; two: before/after then start/end; four: before, end, after, start |
| `paddingStart`, `paddingEnd`, `paddingBefore`, `paddingAfter` | non-negative length | `0px` | yes | area, body, button, div, input, object, p | 0 | Padding on one side |

### Text

| Attribute | Type | Default | Anim. | Allowed on | On disc | What it is for |
|---|---|---|---|---|---|---|
| `font` | font | empty | yes | body, div, input, p, span | 47 | The font file, optionally with a full font name. Inherited |
| `fontSize` | 1 or 2 non-negative lengths, or enum `xx-small` \| `x-small` \| `small` \| `medium` \| `large` \| `x-large` \| `xx-large` \| `smaller` \| `larger` | `medium` | yes | body, div, input, p, span | 55 | Text size; first length along the line, second across (one length = both). Words on a 1920×1080 / 1280×720 Aperture: `xx-small` 26/17 px, `x-small` 38/26, `small` 51/34, `medium` 64/43, `large` 77/51, `x-large` 90/60, `xx-large` 102/68; `smaller` 90%, `larger` 110% [23 §7.6.3.3.2.26] |
| `fontStyle` | enum `normal` \| `italic` \| `oblique` \| `backslant` \| `reverse-oblique` | `normal` | yes | body, div, input, p, span | 0 | Upright, or slanted by the player (it does not pick another face). `reverse-oblique` = `backslant` |
| `color` | colour | `white` | yes | area, body, div, input, p, span | 50 | Text colour |
| `lineHeight` | length or `auto` | `auto` | yes | body, div, input, p | 37 | Height of each line of text; `auto` = XSL `normal`, the font's line height |
| `textAlign` | enum `start` \| `center` \| `end` | `start` | yes | body, div, input, p | 0 | Alignment of lines |
| `textIndent` | length | `0px` | yes | body, div, input, p | 0 | Indent of the first line |
| `displayAlign` | enum `auto` \| `before` \| `center` \| `after` | `auto` | yes | area, body, button, div, input, object, p | 0 | Alignment of the content across lines (top / middle / bottom in `lr-tb`) |
| `textAltitude` | length or `auto` | `auto` | yes | input, p, span | 0 | Height of the text area above the baseline |
| `textDepth` | length or `auto` | `auto` | yes | input, p, span | 0 | Depth of the text area below the baseline |
| `wrapOption` | enum `wrap` \| `no-wrap` | `wrap` | yes | body, div, input, p, span | 0 | Whether long lines wrap |
| `direction` | enum `ltr` \| `rtl` | `ltr` | | body, div, input, p, span | 0 | Text direction |
| `writingMode` | enum `lr-tb` \| `rl-tb` \| `tb-rl` | `lr-tb` | | body, div, input | 0 | Line and page direction: left-to-right top-to-bottom, right-to-left, or vertical (Japanese). The book applies it to `div` only. Inherited |
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
| `navUp`, `navDown`, `navLeft`, `navRight` | `[app#]id` or `none` | `none` | yes | area, button, input | 405 each | `id` of the element that gets the focus when the user presses that arrow, in another application if `app` (an `ApplicationSegment`/`PlaylistApplication` `id`) is given; `none` or a target that cannot take the focus: the focus stays. Overrides `navIndex` |
| `navLeftUp`, `navLeftDown`, `navRightUp`, `navRightDown` | `[app#]id` or `none` | `none` | yes | area, button, input | 5 each | As above, for the diagonal keys |
| `navIndex` | two non-negative integers, `auto` or `none` | `auto` | yes | area, button, input | 2 | Arrow order when no `nav*` applies: the first number for Right/Left, the second for Down/Up, wrapping round. `none`: never reached by arrows. `auto`: numbered by the player at each page load, rows (top to bottom, then left to right) for the first number and columns for the second, skipping numbers authors set [23 §7.2.5.3] |

On disc: `position` is always `absolute` (1462/1462); `display` is `inherit`
1054 times, `auto` 473, `none` 114; `opacity` is `inherit` 1043 times, and
keyframe lists appear on `animate`; `contentWidth` / `contentHeight`
`scale-to-fit` 41 / 40. `writingMode`, `padding*`, `border*`, `direction`,
`displayAlign`, `whiteSpace*`, `textAlign` and the text-metric attributes are
never used; implement them from the schema and XSL-FO when a disc needs them.

`[5, 11, 12]` **VERIFIED** (names, types, values, defaults, placement);
`[23 §7.6.3.3]` **SPEC** (meanings, inheritance, animation modes).

## 14.10 State attributes

In the `ihd#state` namespace ([23 §7.6.3.4]). They describe what the user is
doing to an element. The player keeps them up to date; markup can set initial
values; paths read them with `state:…()`.

Who may change them: `foreground`, `pointer` and `actioned` belong to the player
(markup `set`/`animate` and script have no effect). `focused`, `enabled` and
`value` may also be set by `set`/`animate` or by script; such a value overrides
the player's, shows in the DOM attribute, and stays after the animation ends
until script calls `unsetProperty()`. While a `set`/`animate` holds one of them
the player cannot change it, but script can. Once script sets one with
`setProperty()`/`animateProperty()`, that state is under script control for every
element (per application for `enabled` and `value`, for all applications for
`focused`) until any `unsetProperty()` call.

| Attribute | Type | Default | Anim. | On | What it is for |
|---|---|---|---|---|---|
| `enabled` | boolean | `true` | yes | `body`, `br`, `object`, `div`, `p`, `span`, `button`, `input`, `area` | `false`: the element cannot be focused or activated |
| `focused` | boolean | `false` | yes | `button`, `input`, `area` | The element has the focus. At most one element in the whole player has it; moving the focus sets the old one `false` and the new one `true`. Set `true` in markup to choose the initial focus (several: the last in document order). Otherwise nothing is focused until the first arrow key (§14.9 `navIndex`). Needs `display` not `none`, `navIndex` not `none` and `enabled`. A Cancel (ESC) gesture clears it everywhere. When several applications set it in one tick, the lowest application in processing order (focused application, then top to bottom) wins |
| `actioned` | boolean | `false` | no (v1.1) | `button`, `input`, `area` | The element is being pressed: Enter on the focused element, one of its `accessKey` keys (one title tick), or a pointer click (from button down to button up). A pressed element then takes the focus |
| `pointer` | boolean | `false` | no | `div`, `p`, `span`, `button`, `input`, `area` | The cursor's hot spot is over the element as laid out; only while the cursor is enabled |
| `value` | boolean or string | | yes | `button`, `input`, `area` | `button`, `area`: starts `false` and toggles each time the element is pressed. `input`: its text, starting empty or as written; editing starts when it takes the focus, by a player-specific method. `set`/`animate` may set any string |
| `foreground` | boolean | `false` | no | `body` | `true` while the application is the topmost in z-order |

On disc: `state:value` 113 (all on `input`), `state:focused` 33 (initial focus),
`state:enabled` 1.

## 14.11 v1.0 and v1.1

Retail discs validate against both schema versions (§14.13); read against v1.1
and accept the v1.0-only forms below. The book v1.01 [23 §7] matches the v1.0
column: it still has `clockDivisor`, `startIndent`/`endIndent` and animatable
`state:actioned`.

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

## 14.12 Reading a page into memory

What a reader must keep so that layout, timing and script later get the right
answer. These follow from the rules above; they are collected here because each
one is easy to lose while parsing.

- **Three kinds of document.** A `.xmu` or `.xas` has `root` at the top, a `.xts`
  has `timing`, a `.xss` has `styling`. `include` pulls the last two into a
  page's `head` and `.xmu` fragments into `body`, so a reader needs to accept all
  three roots.
- **`include` needs a loader.** Its `href` can name a loose file or an archive
  member (`…/menus.aca/timing.xts`). The reader does not open files itself; it
  asks whoever loaded the page for the included document.
- **Keep children in document order.** Order carries meaning:
  - `seq` runs its children one after another, in order (§14.7).
  - Named and selected styles apply in document order (§14.6).
  - `navIndex="auto"` is numbered from the laid-out positions, with document
    order breaking ties of equal position and z-order (§14.9).

  A `div`'s children are one ordered list of mixed kinds, not one list per kind.
- **Keep text where it is.** In `p` and `span`, text and child elements
  alternate (`Press <span>here</span> to play`). Each run of text is a child in
  its own right, in order between the elements. Keep text as written: how spaces
  and line feeds are treated is a style (`whiteSpaceCollapse`,
  `linefeedTreatment`, §14.9), decided at layout.
- **Do not fill in style defaults.** A style attribute that is not written must
  stay "not written": named and selected styles apply to it first, and only
  then the default (§14.3, §14.6). Filling the default in while reading would
  make it win over the named styles. Plain attributes (`timeContainer`, `mode`,
  `shape`, `fill`, …) have no such rule; their defaults can be applied when read.
- **Keep `inherit` and keyframe lists** as they are (§14.3). `inherit` is
  resolved against the parent at layout; keyframe lists are used by `animate`
  and by animatable values.
- **Keep references as text.** `style`, `use`, `nav*`, `content` and `id()` in
  paths name elements by `id`. Resolve them after the whole page (with its
  includes) is read, because they can point forward.
- **Keep paths as text.** They are evaluated while the page runs (§14.8).
- **Keep attributes from other namespaces** with their namespace, name and
  value (§14.1): script can read them.
- **`meta` is ignored by rendering.** A reader may keep or drop its contents.

## 14.13a Advanced Subtitle documents (`.xas`)

An Advanced Subtitle is an application drawn on the sub-picture plane instead of
the graphics plane, with these limits [23 §7.9]: no `area`, `button`, `input` or
`object`; nothing can take the focus; no inline style attributes; no script and no
`event`. It may use inline timing. A title shows either a sub-picture stream or an
Advanced Subtitle, never both. Advanced Subtitles are processed before the
graphics-plane applications. On disc: 2 `.xas`, both empty stubs.

## 14.13 On disc

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
