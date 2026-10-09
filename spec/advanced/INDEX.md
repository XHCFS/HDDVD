# HD DVD-Video Advanced Content Format Specification

A specification of the **HD DVD-Video Advanced Content** disc format (Category 2 /
HDi, used by nearly all retail HD DVDs): filesystem, on-disc structures,
navigation model, interactive engine, stream layout, and copy-protection layout.
The sheets are checked against the DVD Forum book, version 1.01 (June 2006), now
public as a scan [23]. The discs were authored to the later schema v1.1, so where
the book and the discs differ the sheets give both.

There is no program-chain (PGC), cell, or navigation-command VM here. Advanced
Content replaces all of that with an XML playlist and an interactive application
engine (HDi). Standard Content (the older, DVD-Video-like "Category 1" mode) is
out of scope.

## About this specification

The format book was confidential until its version 1.01 scan was released [23].
This document was first reconstructed without it, then checked line by line against
it. Each fact is stated with its evidence:

- **Primary specifications.** The DVD Forum book v1.01 [23], Toshiba patents, the
  AACS HD DVD Pre-recorded Book, the DVD Forum v1.0 and v1.1 XML schemas, and the
  HDi scripting type library. Cited `[n]`.
- **A reference corpus.** 120 retail HD DVD disc images preserved on the Internet
  Archive, read structurally to confirm what discs actually contain. Figures written
  as **"N/120"** (or "N/119" for the Advanced-Content subset) are this survey. For
  example, "247/247 playlists" means the claim held for all 247 playlist files across
  the corpus. Reference [11].
- **Reproducible checks.** Every quantitative claim is re-derived by a numbered
  verification experiment, written **`e01` through `e20`**.
  Reference [12].

**How to read a claim.** Normative rules are stated in imperative English. Each
carries a citation `[n]` to [13_references.md](13_references.md) (every reference is a
live URL or a bundled artifact) and an evidence grade: **VERIFIED** (confirmed on
disc or by two agreeing sources), **SPEC** (stated by the book [23] or another
primary specification, and not something the discs can show), **INFERRED** (a
fail-closed rule reasoned from a source), **OPEN** (a runtime guess would still be
required), **UNCLOSEABLE** (needs material not publicly available), or **OUT**
(out of scope). OPEN/UNCLOSEABLE items
are collected in [11_gaps.md](11_gaps.md). None is on the critical path to playback.

**Reading / printing.** The HTML site is one sheet per page. The whole specification
is also a single printable page (`make singlehtml` in `docs/`, served as `docs/print/`)
and an EPUB (`make epub`, `docs/HD-DVD-Advanced-Content.epub`).


| Sheet | What it specifies |
|---|---|
| [01_volume.md](01_volume.md) | UDF, roots, how to recognise the disc |
| [02_discid.md](02_discid.md) | `ADV_OBJ/DISCID.DAT` |
| [03_playlist.md](03_playlist.md) | `VPLST$$$.XPL`: titles, clips, chapters, tracks |
| [04_aca.md](04_aca.md) | `.ACA` archive |
| [05_manifest_hdi.md](05_manifest_hdi.md) | Manifest, iHD, script |
| [14_markup.md](14_markup.md) | iHD markup (`.xmu`, `.xts`, `.xss`): document tree, value types, every element, style and state attribute, timing, path expressions |
| [06_vti.md](06_vti.md) | `HVA00001.VTI`: Advanced VTSI, ATRI, EVOBI |
| [07_map.md](07_map.md) | `.MAP` time map (seek) |
| [08_evo.md](08_evo.md) | `.EVO` MPEG-2 PS, NV_PCK |
| [09_aacs.md](09_aacs.md) | `ANY!` / `AAC!` overlay (format only; not a decryptor) |
| [10_playback.md](10_playback.md) | Insert to designed menus to title to pack. §10.0 flow and §10.8 Q&A |
| [11_gaps.md](11_gaps.md) | Gap register |
| [12_hdi_scripting_abi.md](12_hdi_scripting_abi.md) | HDi scripting host ABI: objects, constant values, system events, XPath variables, virtual keys (Annex Z, V, W), full iHD XSD surface |
| [13_references.md](13_references.md) | Numbered reference list. Every citation, live links. |

Authoritative XML schemas (DVD Forum): v1.0 (16 Jul 2006) and v1.1 (5 Nov 2007),
both bundled. Retail playlists declare version 1.0 but all 247 validate only
against **v1.1** (`e26`, [03](03_playlist.md) §3.1), so read against v1.1:

- `spec/raw/adv_obj/v1.1/Playlist.xsd` (v1.0 for reference)
- `spec/raw/adv_obj/v1.1/Manifest.xsd` (identical to v1.0)
- `spec/raw/adv_obj/v1.1/iHD.xsd`, `iHDstyle.xsd`, `iHDstate.xsd` (v1.0 for reference)
- `spec/raw/adv_obj/iHD_Scripting_API.txt` (106 typeinfos; names only)

## Status of public sources

No published open implementation of Advanced Content / HDi is known. VLC, Kodi and
xine have never implemented it. The proprietary players that once did (WinDVD 9,
PowerDVD 7 Ultra, ArcSoft TotalMedia Theatre) are discontinued, fail on modern
Windows, and **cannot open menus from an ISO or folder**. They required a physical
disc in a licensed drive.
`[20]`

Sheets 01–10 specify Category 2 linear playback and on-disc HDi menus. The
behaviour of a complete HDi runtime (markup chapter 7, script chapter 8, the API in
Annex Z) is now public in the v1.01 book [23]; the sheets summarise what a reader
needs and point to the book's sections. The type-library IDL (B2) is still the
source for members added after 1.01. Player firmware is not a usable source. The Toshiba update images are fully
encrypted (entropy 7.997), verified in `11_gaps.md` §11.F. Remaining gaps are in
[11_gaps.md](11_gaps.md).

## Conventions

| Item | Rule |
|---|---|
| Endian | All `HVDVD_TS` / `ADV_OBJ` / AACS **video** structs are **big-endian**. UDF on-disc descriptors are little-endian. |
| Sector / pack | 2048 bytes. |
| Integer sizes | `u8` `u16` `u32`. Unused / absent start addresses are `0xFFFFFFFF`. |
| Time | `HH:MM:SS:FF` = `(([0-1][0-9])\|(2[0-3])):[0-5][0-9]:[0-5][0-9]:[0-5][0-9]`. `FF` is frames on `TitleSet@timeBase` (`60fps` on 247/247 playlists, `e12`/`e14`). |
| Disc URI | `file:///dvddisc/` + absolute path from volume root. Example: `file:///dvddisc/HVDVD_TS/FEATURE_1.MAP`. |
| Path through ACA | `file:///dvddisc/ADV_OBJ/<archive>.aca/<member>` |
| Version word | `VERN` `0x0010` = specification 1.0 (high byte major, low nibble-style as on DVD). |
| Drift | When a patent identifier disagrees with the disc, **the disc wins**. When the book v1.01 disagrees with the disc, the disc shows what players accepted and the book what 1.01 required; both are recorded in place. |
| Citations | Inline `[n]` → numbered source in [13_references.md](13_references.md) (every entry a live/accessible link); `[23 §x.y]` is a section of the DVD Forum book v1.01. Grades **VERIFIED/SPEC/INFERRED/OPEN/UNCLOSEABLE/OUT** are evidence strength, not citations. |
| Patent figures | What the drawings specify vs this corpus: `spec/clean/16_PATENT_FIGURES.md`. |

## Scope

Category 2 discs are HDi titles (203/247 playlists ship a `PlaylistApplication`,
2529 `ApplicationSegment`s, 3/119 boot a selector with no video until
`IPlaylist.load`). Pack demux without the Advanced Application engine is not
Category 2.

Sheets 01–10 specify linear playback and on-disc menus for the retail corpus.
The HDi runtime contract is the v1.01 book [23 §7, §8, Annex Z], summarised in
[12](12_hdi_scripting_abi.md) and [14](14_markup.md). See [11_gaps.md](11_gaps.md).

On-disc menus are File Cache + ACA + Manifest + iHD markup (layout / style /
state / timing) + ECMAScript typelib + graphics plane over scaled main video +
the playback API discs actually call. Network TLS / `.CER` and firmware
reverse-engineering are **out of scope**. ADV_PCK concat, persistent-storage URI
grammar, `jump` pause-at-destination, used cue paths, glyph/`anchor` fail-closed
raster, src-over plane blend, `changeLayout` 8-tuple, `createTimer` / `ITimer`,
`animate` keyframes, and `sync` hard/soft are specified
([05](05_manifest_hdi.md) §5.3 / §5.9, [08](08_evo.md) §8.6,
[03](03_playlist.md) §3.13). Change those rules only if a disc contradicts them.
Flow: [10](10_playback.md) §10.0 / §10.8.

Still uncloseable: firmware vs FIG.50 (catalog
http://hd-dvd.org/firmware.html is intermittent; no reverse-engineering), CHT
bodies, VTUF `URS_NUM>0`. The book closes the ATRI palettes ([06](06_vti.md)),
EVOBI+282 (`FIRST_SCR`), and the Category 3 / `HVS0@@@@.MAP` / `APLST` rules
[23 §3.3.2, §4.3.22]; the corpus has 0/120 of the last three. See
[10](10_playback.md) §10.7.

Open questions that are not C structs: `spec/clean/15_ADVERSARIAL_QUESTIONS.md`.

## Verification status (final)

Every quantitative claim in these sheets is machine-checked against the 120-disc corpus
by `experiments/e01`–`e20` (`python3 experiments/run.py`, all pass) and re-verified in a
line-by-line pass: XPL 247 / versions / `timeBase` / Aperture / StreamingBuffer /
NetworkTimeout; DISCID 119×128 B / magic / `SEARCH_FLG` 106·13 / Disc-ID 0xFF×16 ×109;
VTI 119 / `ADVANCED-VTS` / VERN 0x0010 / `VTS_CAT`=2 / `VTSI_EA`; MAP 2421 / magic /
`TMAP_EA`; ACA 97 files·885 members·magic; typelib 106 typeinfos·954 names; ATRI 1131;
EVOBI 2431; `sync` 2120·304·105; ApplicationSegment 2529; PlaylistApplication 203;
AACS BAK 104 (5 with `MKBRECORDABLE`); EVO pack framing + §8.7 stream routing on disc.
All matched. Remaining OPEN items ([11_gaps.md](11_gaps.md)) are off the playback path.
Every factual line carries a numbered citation to a live source ([13_references.md](13_references.md)).
