# 11. What a C author still cannot build (gap register)

*Counts written "N/120", "N/119", "on N discs", "listings", or as named discs are over the reference corpus of 120 archived retail HD DVD images [11]. `eNN` are the reproducible verification experiments [12].*


This sheet is the boundary of the spec. Sheets 01–10 let a competent C author build
**Category 2 linear playback + PNG-button HDi menus** for the retail corpus
(the §5.0 gate). Everything a *complete, general* `libhddvd` still needs is listed
here, graded by how much it blocks, with the best source and whether it is
closeable from open material.

**There is no open-source HD DVD player.** VLC, Kodi, and xine do not implement
Advanced Content. The proprietary players (WinDVD 9, PowerDVD 7 Ultra, ArcSoft
TMT) are discontinued, fail on modern Windows, and **cannot open menus from an
ISO/folder**. They drove a physical disc. `libhddvd` would be the first program
that can. `[20]`

Grades: **BLOCKING** (a conforming disc feature will not work), **DEGRADED**
(plays, but a real title looks or behaves wrong), **EXTERNAL** (needs a component
outside libhddvd: a codec, a key, a drive), **RESEARCH** (closeable with more
corpus/patent work), **UNCLOSEABLE** (needs firmware reverse-engineering or NDA books).

The DVD Forum book v1.01 is now public [23]. It closes B1 and B3 below and most of
§C; what it settles is marked **CLOSED [23]**. The discs were authored to the
later schema v1.1, so a few disc behaviours newer than 1.01 remain RESEARCH.

---

## A. Fully specified (a C author CAN build these now)

UDF 2.50 mount (01), DISCID probe (02), playlist parse + title/clip/chapter/track
model (03), ACA extract (04), Manifest + used iHD markup + used script host +
File Cache + raster/focus/cues (05), VTI/ATRI/EVOBI (06), MAP seek (07), EVO
demux + NV_PCK/DSI + **stream routing §8.7** + **sub-picture RLC §8.8** (08),
AACS on-disc layout + decrypt math (09), full control flow (10). These are
VERIFIED or fail-closed INFERRED with a rule that cannot desync a conforming
title.

---

## B. BLOCKING (missing for a *general* engine; not for the corpus menus)

### B1. Full HDi runtime semantics (event/timing execution model): CLOSED [23]

The book's chapter 7 (markup: page lifecycle, tick processing, focus and implicit
navigation, gestures, the timing algebra, the style property tables), chapter 8
(script restrictions, system events and their order, event delivery across
applications, application lifetime states, the work-item scheduler) and Annex Z
(every API object, member and constant value) are the complete contract. Sheets
[05](05_manifest_hdi.md), [12](12_hdi_scripting_abi.md) and [14](14_markup.md)
summarise them. The text below is the history of the gap.
Sheets 05/10 specify the **used subset** the retail corpus exercises: the ~18
script calls with signatures, the used markup attributes, the used cue-path
allowlist, the page/title/application clock rule. A *general* HDi engine (one
that runs an arbitrary conforming disc, not just these 120) needs the complete
event-dispatch order, the full `par`/`seq`/`cue` timing resolution, and the
error/exception model. That behavioural contract is in the DVD Forum **iHD /
Annex Z** book, which is unpublished.
For the corpus, the used subset is complete (0 unknown used attrs/calls across
e15/e17). For an unknown disc, fail-closed (unknown cue path = does not fire;
unknown call = no-op) keeps sync but may drop an effect.
**Best source:** Microsoft HDi "Jumpstart" prose (used-subset semantics only);
the XSDs (structure); the typelib (names). The runtime half is specified from
published standards in [12](12_hdi_scripting_abi.md) §12.4: the event model is W3C
DOM Level 2 Events [17], node/exception model DOM 2 Core [17], timing SMIL 2.0 [18],
script ECMA-327 [19]. The typelib proves iHD implements exactly these. The
HDi-specific glue is also specified from public sources: the three clocks from
Jumpstart [14] + patent [1] (§5.2), the cue-predicate grammar as XPath 1.0 +
enumerated `state:`/`style:` functions ([12](12_hdi_scripting_abi.md) §12.6), the
player object model from the type library (§12.5). What remains is numeric/edge
quirks (cue coercion, A102 tick instant), fail-closed in the sheets,
**DEGRADED-safe**, not blocking.
`[5, 6, 14]`

### B2. HDi type-library signatures (ABI): CLOSED for 1.01 [23 Annex Z]

Annex Z gives every member's parameter and return types and every constant's
value for the 1.01 API ([12](12_hdi_scripting_abi.md)). The type library is
still the only source for members added after 1.01 (for example `aacs`,
`regionCode`, `captureWithMAC`); those stay RESEARCH.
`iHD_Scripting_API.txt` is **106 typeinfos / 954 names only**, with no argument types
or return types. Sheets 03/05/10 give *inferred* signatures for the members discs
actually call (from call-sites). For any member a future disc calls that the
corpus does not, the C author has a name but no signature.
The called surface is specified; the rest is names.
**Best source:** the `.tlb` inside `SCENACA.msi` carries a full IDL (types). This
repo originally had only the extracted name list. Re-extracting the typelib with an
IDL dumper (e.g. `oleview`/`tlbimp` on the `.tlb`) would close signatures.
**MOSTLY CLOSED.** The `.tlb` was extracted from `SCENACA.msi` and saved to
`spec/raw/adv_obj/typelib/iHDScripting.tlb`. Sheet [12](12_hdi_scripting_abi.md)
gives all 106 interfaces and 200 named constants (proving e.g. `TIMER_TITLE` real,
not inferred). Parameter/return **types** still need a Windows type-library viewer
on the saved binary. That is a mechanical step; the artifact is in the repo.
**RESEARCH** (artifact in hand).

### B3. Advanced Subtitle: CLOSED [23 §7.9]
An Advanced Subtitle is ordinary iHD markup (`.xas`) drawn on the sub-picture
plane, without `area`/`button`/`input`/`object`, focus, inline styles, script or
`event`, and usually with inline timing ([14](14_markup.md) §14.13a). Its
playlist side is `AdvancedSubtitleSegment` ([03](03_playlist.md) §3.13). 0/120
discs use it, so it has no corpus test.

---

## C. DEGRADED (plays, but not pixel/behaviour exact)

| Item | Effect if only the fail-closed rule is used | Sheet |
|---|---|---|
| Glyph rasterisation / `anchor` pixel | text menus render, sub-pixel placement not screenshot-exact | 05 §5.9 |
| Graphics-plane blend constants | src-over is correct; exact YCbCr matrix / rounding not measured | 05 §5.9 |
| `jump(time, true)` (was: pause-at-destination) | CLOSED [23 Annex Z.10.13]: the boolean is `bookmark`, not pause | 05 §5.3 |
| File Cache 64 MB overflow order | CLOSED [23 §4.3.20]: priority order, application resources before title resources, Stop on overflow | 05 §5.7 |
| Playlist `Event` delivered under its own id as event type | 1.01 delivers `scheduled_event` only; `1408_DC` listens on the id | 03 §3.18 |
| ILVU angle interleave beyond Pan's 4 maps | linear play unaffected; multi-angle walk INFERRED | 07 |

None desync a conforming linear title; all are cosmetic or unused-path.

---

## D. EXTERNAL (outside libhddvd by design)

| Item | Who provides it | Note |
|---|---|---|
| VC-1 / H.264 / MPEG-2 video decode | ffmpeg / codec lib | §8.7 routes the ES; decoding is not libhddvd |
| DD+ / TrueHD / DTS-HD / LPCM audio decode | codec lib | same |
| OpenType glyph rendering | freetype | §5.9 gives em-scale rule |
| AACS keys (VUK / title key) on a real disc | see §E | corpus ISOs are already clear |
| Volume ID (BCA) | the drive (MMC `80h`), after AACS auth | not in any ISO (09 §9.7) |
| Network / Managed Copy / `.CER` TLS | out of the gate entirely | 05 §5.0 |

---

## E. Encryption: what is and is not needed  (detail: 09 §9.9–9.11)

For **this corpus**: nothing. Packs are AACS-stripped (`PES_scrambling_control=00`
on 704/704, e09); a player reads them clear.

For a **real encrypted disc**: the *format* is fully specified: pack layout
(128 clear + 1920 CBC), `Kc = AES-G(Kt, Dtk || CPI_lsb_96)`, CPI at pack `0x3C`,
fixed CBC IV `0BA0F8DDFEA61FB3D8DF9F566A050F78`, VTKF title-key indexing (09 §9.6,
§9.11). What is **not** in libhddvd and must be added: the MKB→Km→Kvu→Kt key
ladder (needs the Volume ID from the drive) and the AACS device/host keys. Those
are the licensed/derived-secret parts. Open toolchains (`aacskeys`, `dumphd`,
BackupHDDVD) already do them. See §F for the libaacs port.

---

## F. Firmware is not a usable source  (checked, not assumed)

The path "read the player firmware to recover the HDi runtime" does not work.
Toshiba HD-A20 update ISO `HD-A20 Ver 3003.iso` (42 MB): **no ISO 9660 directory,
entropy 7.997 bits/byte throughout**. The payload is fully encrypted/packed, not
inspectable code. `[13]` **UNCLOSEABLE** (encrypted firmware; would
need the player's own update-decrypt key and then full ARM/MIPS reverse-engineering
of a player OS, which is out of scope and low-yield next to the patents/XSDs already
in hand).

---

## Reader-test verdict

Build order for a C author: **(1)** UDF→playlist→MAP→EVO demux→video/audio via
§8.7 = linear playback of every corpus disc; **(2)** ACA→Manifest→used iHD→script
subset→File Cache→graphics plane = PNG-button menus (the §5.0 gate). Both are
closed. B1 and B3 are now closed by the book, and B2 for the 1.01 API. What
remains is the post-1.01 API surface and the exact rendering of features no disc
uses. No open-source player has ever crossed even the linear bar.
