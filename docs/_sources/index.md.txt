# HD DVD-Video Advanced Content Format Specification

A specification of the **HD DVD-Video Advanced Content** disc format (Category 2 /
HDi, used by nearly all retail HD DVDs): filesystem, on-disc structures,
navigation model, interactive engine, stream layout, and copy-protection layout.
The unpublished DVD Forum books are not required to read these sheets. There is
no program-chain, cell, or navigation-command VM. Advanced Content replaces all
of that with an XML playlist and an interactive application engine (HDi).
Standard Content (the older, DVD-Video-like Category 1 mode) is out of scope.

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

**Print and EPUB.** The whole specification is one document:
<a href="print/index.html">print this site</a>
(browser print-to-PDF) or download
<a href="HD-DVD-Advanced-Content.epub">HD-DVD-Advanced-Content.epub</a>.
## Status of public sources

No published open implementation of Advanced Content / HDi is known. VLC, Kodi and
xine have never implemented it. The proprietary players that once did (WinDVD 9,
PowerDVD 7 Ultra, ArcSoft TotalMedia Theatre) are discontinued, fail on modern
Windows, and **cannot open menus from an ISO or folder**. They required a physical
disc in a licensed drive.
`[20]`

Sheets 01–10 specify Category 2 linear playback and on-disc HDi menus. A complete
HDi runtime additionally needs the unpublished iHD/Annex Z behavioural book (B1)
and the full type-library IDL (B2, recoverable from the Scenarist MSI). Player
firmware is not a usable source for those. The Toshiba update images are fully
encrypted (entropy 7.997), verified in `11_gaps.md` §11.F. Remaining gaps are in
`11_gaps.md`.

```{toctree}
:maxdepth: 2
:caption: Specification

01_volume
02_discid
03_playlist
04_aca
05_manifest_hdi
14_markup
06_vti
07_map
08_evo
09_aacs
10_playback
11_gaps
12_hdi_scripting_abi
13_references
```

The **Standard Content (Category 1)** mode, the DVD-Video-like navigation used by one
disc in the corpus, is documented for the record in the archival appendix below. It is
out of scope for the player.

```{toctree}
:maxdepth: 2
:caption: Appendix: Standard Content (archival)

std_INDEX
std_01_volume
std_02_vmgi
std_03_vtsi
std_04_pgc_vm
std_05_evob_nv
std_06_playback
std_07_aacs
std_08_gaps
std_09_references
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

## Scope

Category 2 discs are HDi titles, so the Advanced Application engine is part of
the format, not an optional extra. Sheets 01–10 specify linear playback and
on-disc menus for the retail corpus. Remaining items are in `11_gaps.md`: B1
runtime glue (DOM2/SMIL/ECMA-327 in `12_hdi_scripting_abi.md`) and B2 parameter
IDL (type-library binary in the repository).

On-disc menus: File Cache + ACA + Manifest + iHD markup + ECMAScript typelib +
graphics plane over scaled main video + the playback API discs call. Network TLS
/ `.CER` and firmware reverse-engineering are out of scope. ADV_PCK and
persistent-storage URI grammar are in.
