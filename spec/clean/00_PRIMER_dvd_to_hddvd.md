# HD DVD for people who already know DVD-Video


> **Provenance.** Synthesis document. Individual claims carry [V]/[P]/[?] markers; full provenance in the per-structure files.
> See `EVIDENCE_STANDARD.md` for the tag format.

Read this first. It assumes you know VMG/VTS/PGC/Cell, IFO layout, NV_PCK, and CSS.
Everything is framed as a **delta from DVD-Video**, with the source for each claim and
how to verify it yourself.

Markers: **[V]** verified against real disc bytes · **[P]** from patents only ·
**[?]** unknown or unresolved.

---

## 0. The one idea that reorganises everything

**HD DVD is two formats sharing a disc.**

DVD-Video has exactly one navigation model. HD DVD has two, and they have almost
nothing in common:

| | Standard Content | Advanced Content |
|---|---|---|
| model | DVD-Video, evolved | declarative XML + sandboxed app |
| lives in | `HVDVD_TS/HV*.IFO` | `ADV_OBJ/*.XPL` + `.ACA` |
| has PGC/Cell/PTT? | yes | **no** |
| has VM commands? | yes | **no** |
| interactivity | VM + NV_PCK buttons | HDi (markup + ECMAScript) |
| analogous to | DVD-Video | libbluray's MPLS + BD-J |

Discs declare a **Category**: 1 = Standard only, 2 = Advanced only, 3 = both. **[P]**

The patents are blunt about what Advanced VTS drops:

> "Elimination of a layered structure. No Title, no PGC, no PTT and no Cell.
> No supports of Navigation Command and UOP control."

**Why this matters more than anything else:** we surveyed 120 retail discs and found
**1 Standard Content, 119 Advanced, 0 Category 3**. **[V]** Your DVD knowledge maps
onto the format that almost no retail disc uses. Plan accordingly.

---

## 1. Layer by layer, DVD → HD DVD

### 1.1 Filesystem — the first wall

| | DVD-Video | HD DVD |
|---|---|---|
| filesystem | UDF 1.02 (+ISO9660 bridge) | **UDF 2.50** **[V]** |
| partitions | one physical | **physical + Metadata Partition** **[V]** |

UDF 2.50's Metadata Partition is a *virtual* partition whose contents live inside a
regular file (the "metadata file") in the physical partition. File Entries and
directory data go there; **file payload stays in the physical partition**.

libdvdread's bundled UDF reader (`dvd_udf.c`) knows nothing about this and will fail
to mount any HD DVD. This is the single hardest blocker, and it is *not* a
navigation problem at all.

**Verify it yourself** — this is the fastest way to see it:
```
udfclient -b 2048 some_hddvd.iso
```
Look for:
```
mapping 0 on 0 as direct recording data
mapping 1 on 0 as metadata only recording metadata
*** marked read-only due to read-only support for Metadata partition ***
```

### 1.2 Namespace and file naming

| | DVD-Video | HD DVD |
|---|---|---|
| content dir | `VIDEO_TS` | `HVDVD_TS` **[V]** |
| VMG | `VIDEO_TS.IFO`/`.BUP` | `HV000I01.IFO`/`.BUP` **[V]** |
| VTS info | `VTS_%02d_0.IFO` | `HV%03dI01.IFO` **[V]** |
| menu object | `VTS_%02d_0.VOB` | `HV%03dM%02d.EVO` **[V]** |
| title object | `VTS_%02d_%d.VOB` | `HV%03dT%02d.EVO` **[V]** |
| max VTS | 99 | **511** **[P]** |
| max parts | 9 | 99 **[V]** (T19 seen) |
| also present | — | `ADV_OBJ/`, `ANY!/`, `ANY!_BAK/` **[V]** |

VOB → **EVO** = "Enhanced Video Object". Same idea, new codecs (VC-1, H.264 alongside
MPEG-2; DD+, TrueHD, DTS-HD alongside AC-3).

### 1.3 Standard Content navigation — mostly DVD with targeted widenings

12-byte ASCII identifiers, same convention as DVD's `DVDVIDEO-VMG`: **[V]**
`HVDVD-VMG100`, `STANDARD-VTS`, `ADVANCED-VTS`.

**Unchanged — reuse your DVD readers as-is** **[V]**: `VTS_PTT_SRPT`, `VTS_C_ADT`,
`VTS_EVOBU_ADMAP`, `VTS_TMAPT` (including bit-31 discontinuity), PGC `audio_control` /
`subp_control`, `cell_position`.

`VMGI_MAT` is *nearly* unchanged: RBP 0-215 matches DVD, but HD DVD inserts
`FP_PGCM_C_ADT_SA`/`FP_PGCM_EVOBU_ADMAP_SA` at 216/220, pushing `VMGM_C_ADT` and
`VMGM_EVOBU_ADMAP` to 224/228. **[V]** An earlier draft of this primer called it
"identical" — that was wrong, and it is exactly the kind of error that comes from
checking against DVD instead of against the patent table covering that region.

**Changed** — full table in `03_libdvdread_requirements.md`. The pattern behind the
changes is worth internalising: **fields widened wherever DVD's limits were raised.**
`TT_SRPT` grew 12→16 bytes because `VTSN`/`VTS_TTN` went u8→u16, because the spec
allows 511 title sets and 99 doesn't fit in a byte. Once you see that, most of the
deltas become predictable rather than arbitrary.

**Navigation commands:** still 8 bytes, still DVD's instruction set — but the word is
**rotated right 16 bits**. `DVD[0..5] = HD[2..7]`, `DVD[6..7] = HD[0..1]`. **[V]**
libdvdnav's `vmcmd.c` works after that one transform.

**NV_PCK (PCI/DSI): no public source describes it — but it is readable in the stream.**
The first pack of every EVOBU is the NV_PCK, carrying three `private_stream_2` packets
(substream `0x00` = PCI, `0x01` = DSI, `0x04` = HD DVD-specific, undecoded). PCI and DSI
follow DVD-Video's `pci_gi_t`/`dsi_gi_t`. **[V]** — chain-validated over 40 VOBUs.
One gotcha: `vobu_ea` is **relative** to the VOBU start, not absolute.
Highlight/button regions remain **[?]**. See `08_NV_PCK_PCI_DSI.md`.

### 1.4 Advanced Content — genuinely new, but declarative

| Ext | What | Format |
|---|---|---|
| `.XPL` | playlist — the whole title/chapter/stream model | **XML**, namespace `http://www.dvdforum.org/2005/HDDVDVideo/Playlist`; official XSD in `spec/raw/adv_obj/` **[V]** |
| `.ACA` | application package archive | magic `HDDVDACA`, cracked **[V]** (N=1) |
| `.MAP` | per-clip time map | `HDDVD_TMAP00`; TMAP_GI / TMAPI_SRP@384 / EVOBU_ENT **[V]** |
| `.VTI` | advanced VTS info | `ADVANCED-VTS`; ATRT 1024 B, EVOBIT 320 B **[V]** |
| `DISCID.DAT` | playlist-manager config | `HDDVD-V_CONF`, 128 B **[V]** |
| `.XMF` | HDi markup (also inside ACA) | XML; schema `iHD.xsd` |
| `.JS` | ECMAScript | **UTF-16BE** **[V]** |

Key structural point: `PrimaryAudioVideoClip@src` in the playlist points at a
**`.MAP`**, not at the EVO. The time map is the addressing layer. **[V]**

### 1.5 Encryption

| | DVD-Video | HD DVD |
|---|---|---|
| scheme | CSS | **AACS** **[V]** |
| library | libdvdcss | libaacs — **has zero HD DVD support** **[V]** (read the source) |
| location | — | `ANY!/` or `AAC!/`, plus `*_BAK/` **[V]** |

AACS does not encrypt the EVO container either: pack headers are byte-identical on an
encrypted and an unencrypted disc. **[V]** Encrypted packs keep a **128-byte**
clear prefix; `NV_PCK`/`ADV_PCK` are not encryptable at all. libaacs's
`aacs_decrypt_unit` (BD 6144-byte TS Aligned Unit) does not apply. **[V]** Key files
use the same 12-byte-ASCII-ID convention as the IFOs and bind by **playlist
filename**, not by numbered CPS unit as Blu-ray does. **[V]** See `09_AACS.md`.

**libdvdcss is irrelevant here** — CSS and AACS share nothing.

**The fact that changes your plan:** navigation files are *never* encrypted. On
AACS-protected discs the IFO/VTI magic reads as plaintext ASCII. **[V]** AACS covers
bytes 128–2047 of encryptable packs only. So the entire navigation layer is parseable
with no crypto at all. Unencrypted discs also exist (no `ANY!` directory at all). **[V]**
Volume ID is in BCA/Lead-in, not in the ISO — this corpus cannot yield `Kvu`. **[V]**

---

## 2. Sources — what to trust, and why

### 2.1 The DVD Forum books — do not chase these
*DVD Specifications for High Definition Video*. NDA-only, never leaked. From the one
serious community RE attempt (Doom9, 2008):
> "someone who wanted to have one had to pay a large amount to the DVDforum, and sign
> NDA's, so chances are rather low that a spec will be leaked to the community."

There is also **no free physical spec** — I checked ECMA on the theory that HD DVD had
a published standard like DVD's ECMA-267/268. It does not. ECMA-372 is C++/CLI;
ECMA-382/384 are DVD-R/RW DL. Don't repeat that search.

### 2.2 Toshiba patent applications — the de facto specification
Large sections are transcribed near-verbatim from the books, **including byte-level
tables**. This is the single most valuable public source.

- `US20080298219A1` — **has `RBP` (Relative Byte Position) tables.** Start here.
- `WO2006098395A1`, `EP1866921A1` — same family, more RBP tables
- `US20070091495A1` — 1.5 M chars of architecture: categories, zones, allocation rules
- also `US20070077037`, `US20070091494`, `US20070079001`, `EP1763034A2`

Search pattern that finds them: Google Patents for
`"information storage medium" "standard content" "advanced content" EVOB TMAP playlist`.

**How much to trust them:** I derived the `VTSI_MAT` attribute-block layout
independently from disc bytes, *then* compared to the patent's RBP table. They agreed
field-for-field. **[V]** So the offsets are reliable.

**Where they drift:** identifiers, not offsets. Patents say `HDDVD_TS` (discs use
`HVDVD_TS`) and `VPLIST%%%.XML` (discs use `VPLST%%%.XPL`). Google's OCR also corrupts
names — it renders `HVA00001.VTI` as `HVAO00001.VTI`, which is impossible under 8.3.
**Always confirm an identifier against a real disc.**

**The figures matter and the text does not replace them.** 86 drawing sheets in
`US20080298219A1` alone. FIG.25 gives the pack taxonomy (`VM_PCK`, `AM_PCK`, `VS_PCK`,
`AS_PCK`, `SP_PCK`, `NV_PCK`, `AVD_PCK`) and the `IFO/TMAP → DVD Playback Engine`
path; FIG.10 gives the Extended System Target Decoder buffer/timing model including a
PCI decoder and STC with Main/Sub ADPI. None of that is in the prose. Local copies: `spec/raw/patents/` (extracted tables). Figures: Google Patents PDF for the same numbers.

Two traps: `pdftotext` returns *nothing* for 57 of 155 description pages (font
encoding, not scans — the HTML text layer covers them). And Arch ships `tesseract`
without `eng.traineddata`; fetch it into a local dir and set `TESSDATA_PREFIX` rather
than writing to `/usr/share`.

### 2.3 Community reverse engineering
Doom9 thread 137428, "Attempt to document HD-DVD IFO file structures" (tteich, 2008) —
the only serious public attempt. He got field *order* for `HVDVD-VMG100` and
STANDARD-VTS but not field *sizes*, and fully described ADVANCED-VTS. His method was
reading these same patents.

His companion doc `hddvd.txt` and 11 reference IFOs are **lost** — host dead, and
Wayback has no successful capture (I checked every timestamp). Local copy of the
thread: `spec/raw/community/`.

### 2.4 Real discs — the ground truth
Internet Archive: `hd-dvd_archive_01`…`_12` (~120 ISOs, 2.77 TB), plus
`star-trek-tos-hddvd`, `mjolnirmayhem-hd-dvd`, `king-kong_202603`,
`freedom-vol-1-3-hddvd-iso`, `300-hd-dvd`, `hd-dvd-games`.

Also `scenarist-hd-dvd-45` — **Sonic Scenarist**, the authoring tool. The one Standard
Content disc we found was authored with Scenarist SCA 4.2 (visible in the UDF
implementation ID). Authoring tools ship sample projects; this is the most promising
lead for a second Standard Content specimen.

### 2.5 Reference implementations to read
- **libudfread** (libbluray) — already handles metadata partitions; your UDF answer
- **libdvdnav** `src/vm/vmcmd.c` — the command decoder that works after the rotation
- **libdvdread** `ifo_types.h` / `ifo_read.c` — the structures you're extending
- **ffmpeg** — already demuxes EVO; read what it assumes
- **libaacs** — MKB/AES-G primitives only; `aacs_decrypt_unit` is BD-specific

### 2.6 AACS LA books — HD DVD book was public, then pulled

The Common Cryptographic Elements book and the format-independent Pre-recorded Video
book are still on `aacsla.com`. The **HD DVD and DVD Pre-recorded Book** was removed
from the live index for “inactivity”; Wayback still has Final 0.953 (and 0.912).
Format-specific book takes precedence over Common. That book is what falsifies
“libaacs will decrypt EVO.” Locators and answers: `09_AACS.md`.

---

## 3. Method — how to derive this yourself

This is the transferable part. Five techniques did essentially all the work.

### 3.1 Survey cheaply before committing
**AACS does not encrypt filesystem metadata.** A ~6 MB HTTP range request against the
head of a 25 GB ISO yields its complete file listing. Surveying 120 discs costs under
a gigabyte, not 2.77 TB. `tools/udfgrab.py --list` does this.

Doing that survey *first* is what revealed the 1-in-120 ratio — which reframed the
entire project before any parser was written.

### 3.2 Arithmetic closure — the strongest validator
Structures declare their own sizes. Make them prove themselves.

- `TT_SRPT`: header says `last_byte=247` → 240 data bytes ÷ 15 titles = **16-byte
  stride**. That's how the 12→16 change was found, without guessing.
- `VTS_PGCIT`: 5 SRPs × 12 B + 8 B header = 68, and the first `PGC_SA` is exactly 68.
- PGC: `cell_playback` 386 + 58 cells × **28 B** = 2010 = `cell_position_offset`;
  + 58 × 4 = 2242 = next PGC start. Both unknowns solved by one equation.

If your stride guess doesn't make the arithmetic close, it's wrong. This is far more
reliable than eyeballing hex.

### 3.3 Chain validation
Sequential structures must link up. Every one of 204 cells satisfied
`cell[n+1].first_sector == cell[n].last_sector + 1`. A layout that produces a valid
chain across 204 samples is not a coincidence.

### 3.4 Semantic cross-check against the real world
Decoded values must mean something.
- `VTS_TMAPT` map 1: 1980 entries × `tmu`=3 s = 5940 s = **99 minutes** = Reservoir
  Dogs' runtime, and the PGC playback time independently says 99 minutes.
- `VMGI_MAT` says 11 title sets; the disc has exactly 11 VTS files.
- `VTS_AST_N`=6 and the PGC has exactly 6 non-zero `audio_control` entries.
- Frame-rate bits = `0b10` = 25 fps on a Benelux (PAL) release.

When several independent readings agree on a real-world fact, the layout is right.

### 3.5 Statistics over many samples to locate a field
When you can't see a field, count it.

Collecting all 57 commands on the disc and histogramming each byte position showed
`byte[0]` was `0x00` **every time** — so it could not be the opcode. Testing
`byte[2]>>5` gave `{1,2,3}` = exactly DVD's Link/Jump, SetSystem, Set. Raw bytes gave
`{0: 57}` — all invalid. That contrast *is* the proof, and it's what produced the
16-bit rotation. One sample would have told you nothing.

### 3.6 Corollary: check your classifier before trusting your survey
I classified discs as Standard via "has `HV*.IFO` and no `.VTI`". A **Category 3** disc
has *both* — so that rule would have silently filed exactly the specimens I wanted
under "Advanced". Re-running with co-occurrence detection found 0 Category 3 discs, so
nothing was hidden. But the earlier numbers were only correct by luck.

**Ask what your filter would hide, not just what it finds.**

---

## 4. Honest state of knowledge

Verified against real bytes but **from a single Standard Content specimen**:
everything in `01_` and `02_`. The "unchanged from DVD" claims are safer, because the
patent RBP tables corroborate them independently. The "changed" claims — two palettes,
4 trailing `cell_playback` bytes, the 2 unexplained bits in the seconds byte — are
exactly the sort of thing that varies between authoring tools and disc generations.

Genuinely unknown / still open: PCI highlight/button regions and DSI tail [?], CPI
**byte offset** inside GCI_PKT (packet identity is closed) [?], menu PGC unit tables
[?], Standard-Content `VTS_ATRT` entry bodies [?], ATRI beyond `V_ATR` [?],
Set-command operand encoding [?], CHT hash-unit bodies [?], HDi runtime, firmware vs
FIG.50, Volume ID (not in ISO). Closed since this paragraph was first written: NV_PCK
PCI/DSI/GCI identity, `.MAP` TABLE 83 figure, `.VTI` ATRT/EVOBIT + `V_ATR`,
`DISCID.DAT`, official `Playlist.xsd`, AACS pack 128/1920 split, VTKF Table 3-8,
MAP vs DSI on Advanced EVO, LVD UDF 2.50, BD unit-decrypt non-fit.
