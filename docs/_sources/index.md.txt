# HD DVD-Video Advanced Content Format Specification

A complete, implementable specification of the **HD DVD-Video Advanced Content**
disc format (the "Category 2" / HDi format used by nearly all retail HD DVDs):
its filesystem, on-disc structures, navigation model, interactive engine,
stream layout, and copy-protection layout. An engineer can build a player (for
example a VLC input module backed by a new `libhddvd`) from these sheets alone,
without the unpublished DVD Forum books. There is no program-chain, cell, or
navigation-command VM. Advanced Content replaces all of that with an XML playlist
and an interactive application engine (HDi). Standard Content (the older,
DVD-Video-like Category 1 mode) is out of scope.

**How this was reconstructed, and how to read a claim.** Most of the format was
never published, so it was recovered from three kinds of source, each fact stated
with its evidence: **primary specifications** (Toshiba patents, the AACS HD DVD
Pre-recorded Book, the DVD Forum v1.0 XML schemas, the HDi scripting type library),
a **reference corpus** of 120 retail HD DVD disc images preserved on the Internet
Archive and read structurally, and **reproducible checks** (`e01` through `e20`) that
re-derive every quantitative claim. Figures written **"N/120"** (or **"N/119"** for
the Advanced-Content subset) are counts over that corpus. For example, "247/247
playlists" means the rule held for all 247 playlist files. Every normative statement
carries a citation `[n]` to the reference list (each entry a live URL or a bundled
artifact) and an evidence grade: **VERIFIED / INFERRED / OPEN / UNCLOSEABLE / OUT**.
See the [reference list](13_references.md). OPEN/UNCLOSEABLE items are collected in
[the gap register](11_gaps.md). None is on the critical path to playback.

**Printing.** This site is also built as a single printable page (Sphinx
`singlehtml`, `docs/_build/singlehtml/index.html`) containing every sheet in order,
suitable for print-to-PDF.
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

```{toctree}
:maxdepth: 2
:caption: Specification

01_volume
02_discid
03_playlist
04_aca
05_manifest_hdi
06_vti
07_map
08_evo
09_aacs
10_playback
11_gaps
12_hdi_scripting_abi
13_references
```

Authoritative XML schemas (DVD Forum 16 Jul 2006, v1.0; every retail playlist):

- `spec/raw/adv_obj/v1.0/Playlist.xsd`
- `spec/raw/adv_obj/v1.0/Manifest.xsd`
- `spec/raw/adv_obj/v1.0/iHD.xsd`
- `spec/raw/adv_obj/v1.0/iHDstyle.xsd`
- `spec/raw/adv_obj/v1.0/iHDstate.xsd`
- `spec/raw/adv_obj/iHD_Scripting_API.txt` (106 typeinfos; names only)

## Conventions

| Item | Rule |
|---|---|
| Endian | All `HVDVD_TS` / `ADV_OBJ` / AACS **video** structs are **big-endian**. UDF on-disc descriptors are little-endian. |
| Sector / pack | 2048 bytes. |
| Integer sizes | `u8` `u16` `u32`. Unused / absent start addresses are `0xFFFFFFFF`. |
| Time | `HH:MM:SS:FF` = `(([0-1][0-9])\|(2[0-3])):[0-5][0-9]:[0-5][0-9]:[0-5][0-9]`. `FF` is frames on `TitleSet@timeBase` (`60fps` on 247/247 playlists). |
| Disc URI | `file:///dvddisc/` + absolute path from volume root. Example: `file:///dvddisc/HVDVD_TS/FEATURE_1.MAP`. |
| Path through ACA | `file:///dvddisc/ADV_OBJ/<archive>.aca/<member>` |
| Version word | `VERN` `0x0010` = specification 1.0. |
| Drift | When a patent identifier disagrees with the disc, **the disc wins**. Recorded in-place. |

## Library gate (full menus, not first picture)

**The library gate (`05_manifest_hdi.md` §5.0) is CLOSED.** It existed to stop a
pack-demuxer-only build being mistaken for a player. Category 2 discs are HDi
products, so the Advanced Application engine is required, not optional. A reader
can now build PNG-button on-disc menus from these sheets, so `libhddvd` may
proceed, within the boundary of `11_gaps.md` (corpus fully specified; remaining
work is B1 runtime glue, now specified from DOM2/SMIL/ECMA-327 in
`12_hdi_scripting_abi.md`, and B2 parameter IDL with the type-library binary saved
in the repo).

On-disc menus (the gate): File Cache + ACA + Manifest + iHD markup + ECMAScript
typelib + graphics plane over scaled main video + the playback API discs call.
Network TLS / `.CER` and firmware reverse-engineering are out of the gate. ADV_PCK and
persistent-storage URI grammar are in.
