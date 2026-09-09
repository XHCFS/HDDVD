# HD DVD-Video Advanced Content Format Specification

A complete, implementable specification of the **HD DVD-Video Advanced Content**
disc format (the "Category 2" / HDi format used by nearly all retail HD DVDs):
its filesystem, on-disc structures, navigation model, interactive engine,
stream layout, and copy-protection layout. It is written so an engineer can build
a player, for example a VLC input module backed by a new library, from these
sheets alone, without access to the unpublished DVD Forum books.

There is no program-chain (PGC), cell, or navigation-command VM here. Advanced
Content replaces all of that with an XML playlist and an interactive application
engine (HDi). Standard Content (the older, DVD-Video-like "Category 1" mode) is
out of scope.

## About this specification

Most of the format was never published. This document was reconstructed from three
kinds of source and states each fact with its evidence:

- **Primary specifications.** Toshiba patents, the AACS HD DVD Pre-recorded Book,
  the DVD Forum v1.0 XML schemas, and the HDi scripting type library. Cited `[n]`.
- **A reference corpus.** 120 retail HD DVD disc images preserved on the Internet
  Archive, read structurally to confirm what discs actually contain. Figures written
  as **"N/120"** (or "N/119" for the Advanced-Content subset) are this survey. For
  example, "247/247 playlists" means the claim held for all 247 playlist files across
  the corpus. Reference [11].
- **Reproducible checks.** Every quantitative claim is re-derived by a numbered
  verification experiment, written **`e01` through `e20`**, that a reader can re-run.
  Reference [12].

**How to read a claim.** Normative rules are stated in imperative English. Each
carries a citation `[n]` to [13_references.md](13_references.md) (every reference is a
live URL or a bundled artifact) and an evidence grade: **VERIFIED** (confirmed on
disc or by two agreeing sources), **INFERRED** (a fail-closed rule reasoned from a
source), **OPEN** (a runtime guess would still be required), **UNCLOSEABLE** (needs
material not publicly available), or **OUT** (out of scope). OPEN/UNCLOSEABLE items
are collected in [11_gaps.md](11_gaps.md). None is on the critical path to playback.

**Reading / printing.** Read online via the rendered site (`docs/_build/html/`), or
as a single printable document via the single-page build (`docs/_build/singlehtml/`,
`make singlehtml` in `docs/`). That build is one HTML page containing every sheet,
suitable for print-to-PDF.


| Sheet | What it specifies |
|---|---|
| [01_volume.md](01_volume.md) | UDF, roots, how to recognise the disc |
| [02_discid.md](02_discid.md) | `ADV_OBJ/DISCID.DAT` |
| [03_playlist.md](03_playlist.md) | `VPLST$$$.XPL`: titles, clips, chapters, tracks |
| [04_aca.md](04_aca.md) | `.ACA` archive |
| [05_manifest_hdi.md](05_manifest_hdi.md) | Manifest, iHD, script. **Library gate.** |
| [06_vti.md](06_vti.md) | `HVA00001.VTI`: Advanced VTSI, ATRI, EVOBI |
| [07_map.md](07_map.md) | `.MAP` time map (seek) |
| [08_evo.md](08_evo.md) | `.EVO` MPEG-2 PS, NV_PCK |
| [09_aacs.md](09_aacs.md) | `ANY!` / `AAC!` overlay (format only; not a decryptor) |
| [10_playback.md](10_playback.md) | Insert to designed menus to title to pack. §10.0 flow and §10.8 Q&A |
| [11_gaps.md](11_gaps.md) | **What a C author still cannot build.** Gap register. |
| [12_hdi_scripting_abi.md](12_hdi_scripting_abi.md) | HDi scripting host ABI: 106 typeinfos, 200 constants, full iHD XSD surface |
| [13_references.md](13_references.md) | Numbered reference list. Every citation, live links. |

Authoritative XML schemas (DVD Forum 16 Jul 2006, v1.0; every retail playlist):

- `spec/raw/adv_obj/v1.0/Playlist.xsd`
- `spec/raw/adv_obj/v1.0/Manifest.xsd`
- `spec/raw/adv_obj/v1.0/iHD.xsd`
- `spec/raw/adv_obj/v1.0/iHDstyle.xsd`
- `spec/raw/adv_obj/v1.0/iHDstate.xsd`
- `spec/raw/adv_obj/iHD_Scripting_API.txt` (106 typeinfos; names only)

## Prior art and status

**No open-source HD DVD player exists.** VLC, Kodi and xine have never implemented
Advanced Content / HDi. The proprietary players that once did (WinDVD 9,
PowerDVD 7 Ultra, ArcSoft TotalMedia Theatre) are discontinued, fail on modern
Windows, and **cannot open menus from an ISO or folder**. They drove a physical
disc through a licensed drive. A player built from this spec would be the first
able to play HD DVD Advanced Content from an image.
`[20]`

**What is and is not buildable** is enumerated in `11_gaps.md`. Sheets 01–10 fully
specify Category 2 linear playback and PNG-button HDi menus (the gate). A *general*
HDi engine additionally needs the unpublished iHD/Annex Z behavioural book (B1) and
the full type-library IDL (B2, recoverable from the Scenarist MSI). Player firmware
is not a usable source for those. The Toshiba update images are fully encrypted
(entropy 7.997), verified in `11_gaps.md` §11.F.

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
| Drift | When a patent identifier disagrees with the disc, **the disc wins**. Recorded in-place. |
| Citations | Inline `[n]` → numbered source in [13_references.md](13_references.md) (every entry a live/accessible link). Grades **VERIFIED/INFERRED/OPEN/UNCLOSEABLE/OUT** are evidence strength, not citations. |
| Patent figures | What the drawings specify vs this corpus: `spec/clean/16_PATENT_FIGURES.md`. |

## Library gate (CLOSED)

The gate ([05](05_manifest_hdi.md) §5.0) exists to stop a *pack-demuxer-only*
implementation being mistaken for an HD DVD player. Category 2 discs are HDi
products (203/247 playlists ship a `PlaylistApplication`, 2529
`ApplicationSegment`s, 3/119 boot a selector with no video until
`IPlaylist.load`), so a demuxer without the Advanced Application engine is not
this player.

**The gate is met. A reader can build PNG-button on-disc menus from these
sheets, so `libhddvd` may proceed.** Build within the boundary of
[11_gaps.md](11_gaps.md): the corpus (linear playback and menus) is fully
specified. Remaining work for a *general* engine is B1 runtime glue (now specified
from published DOM2/SMIL/ECMA-327 in [12](12_hdi_scripting_abi.md) §12.4) and B2
parameter IDL (the type-library binary is bundled). This is a specification, not an
implementation.

On-disc menus (the gate) are: File Cache + ACA + Manifest + iHD markup
(layout / style / state / timing) + ECMAScript typelib + graphics plane over
scaled main video + the playback API discs actually call. Network TLS / `.CER`
and firmware reverse-engineering are **out** of the gate. ADV_PCK concat,
persistent-storage URI grammar, `jump` pause-at-destination, used cue paths,
glyph/`anchor` fail-closed raster, src-over plane blend, `changeLayout` 8-tuple,
`createTimer` / `ITimer`, `animate` keyframes, and `sync` hard/soft are
specified ([05](05_manifest_hdi.md) §5.3 / §5.9, [08](08_evo.md) §8.6,
[03](03_playlist.md) §3.5). Change those rules only if a disc contradicts them.
Flow: [10](10_playback.md) §10.0 / §10.8.

Uncloseable even after the gate: firmware vs FIG.50 (catalog
http://hd-dvd.org/firmware.html is intermittent; no reverse-engineering), CHT bodies, VTUF
`URS_NUM>0`, ATRI palettes, EVOBI+282 units, Category 3 / `HVSO` / `APLST`
(0/120). See [10](10_playback.md) §10.7.

Adversarial implementer pass (what is not a C struct, remaining holes):
`spec/clean/15_ADVERSARIAL_QUESTIONS.md`.

## Verification status (final)

Every quantitative claim in these sheets is machine-checked against the 120-disc corpus
by `experiments/e01`–`e20` (`python3 experiments/run.py`, all pass) and re-verified in a
line-by-line pass: XPL 247 / versions / `timeBase` / Aperture / StreamingBuffer /
NetworkTimeout; DISCID 119×128 B / magic / `SEARCH_FLG` 106·13 / Disc-ID 0xFF×16 ×109;
VTI 119 / `ADVANCED-VTS` / VERN 0x0010 / `VTS_CAT`=2 / `VTSI_EA`; MAP 2421 / magic /
`TMAP_EA`; ACA 97 files·885 members·magic; typelib 106 typeinfos·954 names; ATRI 1131;
EVOBI 2431; `sync` 2120·304·105; ApplicationSegment 2529; PlaylistApplication 203;
AACS BAK 104 (5 with `MKBRECORDABLE`); EVO pack framing + §8.7 stream routing on disc.
All matched. Remaining OPEN items ([11_gaps.md](11_gaps.md)) are off the build path.
Every factual line carries a numbered citation to a live source ([13_references.md](13_references.md)).
