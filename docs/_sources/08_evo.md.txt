# 8. EVO: MPEG-2 program stream

*Counts written "N/120", "N/119", "on N discs", "listings", or as named discs are over the reference corpus of 120 archived retail HD DVD images [11]. `eNN` are the reproducible verification experiments [12].*


Path: `HVDVD_TS/<clip>.EVO`  
Container: MPEG-2 program stream, **2048-byte packs**.  
Pack start: `00 00 01 BA` at every 2048-byte boundary; MPEG-2 marker bits `01`.

Any MPEG-2 PS demuxer that accepts 2048-byte packs can demux this. Navigation
headers are in the clear even on AACS discs.

## 8.1 Pack types (TABLE 85)

| Pack | Contents |
|---|---|
| NV_PCK | Navigation: GCI + PCI + DSI (first pack of each EVOBU) |
| VM_PCK | Main video (MPEG-2 / AVC / VC-1) |
| AM_PCK | Main audio |
| VS_PCK | Sub video |
| AS_PCK | Sub audio |
| SP_PCK | Sub-picture |
| ADV_PCK | Advanced stream (File Cache); `sub_stream_id = 0x80` |
| HLI_PCK | Highlight (Standard menus); `sub_stream_id = 0x08`; **ignore on Advanced** |

Patents: HLI and PCI “shall be ignored in Advanced Content.” Seek uses MAP + DSI,
not PCI buttons.

## 8.2 NV_PCK: first pack of each EVOBU

Three `private_stream_2` (`stream_id = 0xBF`) PES packets:

| `sub_stream_id` | PES length | Identity |
|---|---|---|
| `0x00` | 977 | PCI |
| `0x01` | 755 | DSI |
| `0x04` | 257 | GCI |

Verified on Standard and Advanced (RESERVOIR_DOGS, MYSTERY_MEN, DOWNFALL).

DVD-Video uses `0x00`/`0x01` at lengths 980/1018. HD DVD lengths differ.
`0x04` is **not** ADV_PCK (`0x80`).
WO FIG.121 (`pages/page-378.png`) only names PCI `0x00` / DSI `0x01` / provider `0xFF`
for `private_stream2`. GCI is “others.” 98219 Tables 50–51 and every Advanced NV_PCK
here use `0x04`. **Disc + 98219 win.**

PES length 257 = 1 byte substream id + 256 bytes GCI
(`GCI_GI` 16 + `RECI` 189 + reserved 51). Patent Tables 50–51.

Typical pack prefix:

```
00 00 01 BA <14-byte pack header>
00 00 01 BB <system header>
00 00 01 BF <PCI or GCI or DSI PES> …
```

Order of the three PES packets is GCI/PCI/DSI as listed in the patent; parse by
substream id, not by order. Some Advanced clips omit PCI: `STALINGRAD`
`black.EVO` is GCI `0x04` + DSI `0x01` only (35/35 VOBUs).

## 8.3 PCI GI (offsets from the substream id byte)

DVD `pci_gi_t` layout holds for the GI.

| Off | Size | Field |
|---|---|---|
| 0 | 1 | `0x00` |
| 1 | 4 | `nv_pck_lbn` |
| 5 | 2 | `vobu_cat` |
| 7 | 2 | reserved (DVD hole: a packed C struct must include this, not jump 5→9) |
| 9 | 4 | `vobu_uop_ctl` |
| 13 | 4 | `vobu_s_ptm` 90 kHz |
| 17 | 4 | `vobu_e_ptm` 90 kHz |

`vobu_e_ptm − vobu_s_ptm` = 45045 ticks = 500.5 ms = 15 frames at 29.97 on the
checked VOBUs. Next VOBU `vobu_s_ptm` equals previous `vobu_e_ptm`.

Advanced PCI GI may be filled (DOWNFALL) or zeroed (MYSTERY_MEN VOBU0).
Highlight buttons are **not** in this packet on HD DVD; they are HLI_PCK `0x08`.

## 8.4 DSI GI (offsets from the substream id byte)

DVD `dsi_gi_t` layout holds for the GI.

| Off | Size | Field |
|---|---|---|
| 0 | 1 | `0x01` |
| 1 | 4 | `nv_pck_scr` |
| 5 | 4 | `nv_pck_lbn` |
| 9 | 4 | `vobu_ea` **relative** pack count minus one |
| 13 | 4 | `vobu_1stref_ea` |
| 17 | 4 | `vobu_2ndref_ea` |
| 21 | 4 | `vobu_3rdref_ea` |
| 25 | 2 | `vobu_vob_idn` |
| 27 | 1 | reserved (DVD hole) |
| 28 | 1 | `vobu_c_idn` |

Walk: `next_lbn = this_lbn + vobu_ea + 1`.  
`vobu_ea + 1` equals MAP `EVOBU_SZ` on Advanced content checked.

DSI tail (`sml_pbi`, `vobu_sri`, `synci`) is not a closed table. Not required for
MAP-based seek.

## 8.5 GCI (substream `0x04`)

| Off | Size | Field |
|---|---|---|
| 0 | 1 | `0x04` |
| 1 | 16 | `GCI_GI` (TABLE 52) |
| 17 | 189 | `RECI` (ISRC blocks, TABLE 53) |
| 206 | 51 | reserved |

`GCI_GI`:

| Off | Size | Field |
|---|---|---|
| 0 | 1 | `GCI_CAT` | `0x40` on Advanced (AACS **and** unencrypted `STALINGRAD`). `0x00` is Standard Content (`RESERVOIR_DOGS`), not “no AACS” |
| 1 | 3 | reserved / VOBU-related | increments across VOBUs on `STALINGRAD` `black.EVO` |
| 4 | 2 | `DCI_CCI_SS` | changes every VOBU on the dumps |
| 6 | 4 | `DCI` |
| 10 | 4 | `CCI` |
| 14 | 2 | reserved | `0000` on `STALINGRAD`; `0600` on `SHREK` `BLACK_IDTAG` |

AACS CPI is **16 bytes inside this GCI_PKT** (Final 0.953 Table 4-1). The book
defers the byte offset to the video spec. **Do not** treat `GCI_GI[0]` as `KEY_VF`
(`0x40` is Advanced category, and would also decode as segment-key with no SKF).
The 16-byte CPI field is at **pack offset 0x3C** on the observed NV_PCK framing
(pack `00 00 01 BA`, system header at `0x11=0xBB`, GCI PES at `0x29` → GCI-payload
offset 12). Recovered from BackupHDDVD's `EVOBPack.java` and confirmed on a real
NV_PCK. It reads all-zero (`KEY_VF=0`) on unencrypted clips. **Do not hard-code
pack `0x3C` if stuffing or a missing `0xBB` system header moves the GCI PES**.
Locate `sub_stream_id 0x04`, then apply the GCI-relative offset. See [09](09_aacs.md) §9.6.

## 8.6 ADV_PCK (`sub_stream_id = 0x80`)

`private_stream_2`, pack not encryptable. FIG.81A: pack header then one Advanced
PES (no NV_PCK system header). File Cache, never the AV decoder.

Playlist `ApplicationResource@multiplexed` / `PlaylistApplicationResource@multiplexed`
as a positive integer is the **slot** carried in every ADV_PCK. `false` means
load only from the `src` URI. A positive slot does **not** guarantee packs in
that title’s EVO: `OLIVER_TWIST_JPN` `LoopMenu.EVO` (46 MB, `multiplexed="1"`)
and `JpnTokuhou.EVO` (64 MB, `multiplexed="2"`) have **0** `0x80` packs; the
ACA still exists under `ADV_OBJ`. Always load `src`. If ADV_PCK for that slot
appears in the playing EVOB, concat it. On `STALINGRAD` `logo.EVO` the bytes
**equal** the `ADV_OBJ` file (`e16`).

### Pack grammar (`e16`, `STALINGRAD` `logo.EVO`, N=2383)

Stuffing length 0. PES at pack offset 14: `00 00 01 BF`, `PES_packet_length`
2028 on full packs (14+6+2028=2048). Payload:

| Off | Size | Field |
|---|---|---|
| 0 | 1 | `sub_stream_id` = `0x80` |
| 1 | 1 | packed: `PES_scrambling_control` 2b + `adv_pkt_status` 2b + reserved 4b |
| 2 | 1 | slot = XPL `@multiplexed` (`1`…`6` here) |

`adv_pkt_status`: `01b` first (6 packs), `00b` middle (2371), `10b` last (6).
Reserved nibble 0. Scramble 0 (clear packs).

**First packet only** (`01b`): bytes 2–33 are slot + ASCII ACA filename + NUL
(`\x01mainApp.aca` … `\x06ineditsMenu.aca`). After that 32-byte name field,
ADDTHD is **padding until** `HDDVDACA` (or until the first nonzero, then
require the magic). STALINGRAD is 225 zero bytes then `HDDVDACA` at payload
offset 259. **Do not hard-code 259.** A second disc is not required; the
locator is the decoder. The ACA header `total size` at +14 equals the
`ADV_OBJ` file length (`mainApp.aca` 260447).

**Middle and last** (`00b` / `10b`): byte 3 is `0x00`. ACA bytes start at
offset **4**. No filename field.

Concat per slot, pack order:

```
if status == 01b:  out += payload[payload.find(b"HDDVDACA", 34):]
else:              out += payload[4:]
```

`E16_FULL=1` reconstituted all six slots; each blob matched `/ADV_OBJ/<name>.aca`.
TABLE 91’s “32-byte name then data on every packet” is **wrong** for middle/last
(that would drop or insert 32 bytes). Disc wins.
`[11, 12]` **VERIFIED**
`[2]` **VERIFIED** (`0xBF`/`0x80` / status bits); **superseded** (per-packet 32-byte name)
`[10]`

Eight packs: `spec/raw/adv_obj/samples/advpck_stalingrad_logo.bin`.

OLIVER `archive2.aca` members (file, not packs): `special.xmu` `tokuten.xmu`
`top.xmu` `top_in.xmu` `top_special.xmu`, four `.xmf`, `main.js`.
`[11, 12]` **VERIFIED** (ACA)

Earlier scans with 0 `0x80`: `SHREK` `BLACK_IDTAG`, `STALINGRAD` `black.EVO`,
`GRINCH` `INTRO` head, `ARMY_OF_SHADOWS` `advanced.EVO` (21 MB, video-only
despite the name).

The demux rule: an EVOBU's first pack is NV_PCK; thereafter route by
`stream_id` / `sub_stream_id` (TABLE 45–47):

| Kind | Identification |
|---|---|
| MPEG-2 video | `stream_id = 0xE0` |
| MPEG-4 AVC | `stream_id = 0xE2` |
| VC-1 | `stream_id = 0xFD`, `stream_id_extension = 0x55` |
| AC-3 / DD+ / DTS-HD / LPCM / MLP | `0xBD` + TABLE 46 `sub_stream_id` (`***` = stream number, 0-based vs XPL `streamNumber` 1-based) |
| Sub-picture | `0xBD`, `sub_stream_id = 001*****b` |
| Secondary video (PiP) | `0xBD` + `sub_stream_id` `0x91` MPEG-2 / `0x92` AVC / `0x93` VC-1 (WO FIG.120). **Not** how primary AVC/VC-1 is muxed here |
| ADV_PCK | `0xBF`, `sub_stream_id = 0x80` → **File Cache, never the AV decoder** |

`[2]`
`[11]`

## 8.7 AACS vs container

Encrypted packs (not NV_PCK, not ADV_PCK):

| Bytes | Content |
|---|---|
| 0–127 | clear (pack/PES headers, `Dtk` at 84–87) |
| 128–2047 | AES-CBC payload |

`PES_scrambling_control` at pack byte 20: `01b` = Encrypted Portion present.
See [09](09_aacs.md).

## 8.7 Elementary-stream routing (TABLE 45 / 46): how `@streamNumber` finds its PES

This is what a player uses to demux the track the playlist selected. A clip's
`<Video>/<Audio>/<Subtitle>` child carries `@streamNumber` (1-based decoding
number) and `@mediaAttr` (codec via `MediaAttributeList`, [03](03_playlist.md)).
`@streamNumber` maps to the PES stream as follows.

### stream_id / stream_id_extension (TABLE 45)

| `stream_id` | ext | Stream |
|---|---|---|
| `110x 0nnn` (`0xC0..0xC7`,`0xD0..0xD7`) | | MPEG audio, decoding audio number = `nnn` |
| `1110 0000` (`0xE0`) | | Main video MPEG-2 |
| `1110 0010` (`0xE2`) | | Main video MPEG-4 AVC (H.264) |
| `1011 1101` (`0xBD`) | | private_stream_1 (audio + sub-picture, TABLE 46) |
| `1011 1111` (`0xBF`) | | private_stream_2 (NV_PCK / ADV_PCK, §8.2 / §8.6) |
| `1111 1101` (`0xFD`) | `101 0101` (`0x55`) | Main video **VC-1** (extended_stream_id; ext byte in the PES extension) |

`[2]`
`[11]`
**VERIFIED**

VC-1 is the AMD2:2004 extended-stream-id mechanism: `stream_id=0xFD`, real type in
`stream_id_extension` (`0x55`). Parse the PES extension flags to reach it; do not
treat `0xFD` as generic private data.

### sub_stream_id for private_stream_1 = `0xBD` (TABLE 46)

The first byte of the PES payload (after the PES header) is `sub_stream_id`:

| `sub_stream_id` | Stream | decoding number |
|---|---|---|
| `001x xxxx` (`0x20..0x3F`) | **Sub-picture** (subtitle) | `x xxxx` = sub-picture number |
| `011x xxxx` (`0x60..0x7F`) | reserved (extended sub-picture) | |
| `1000 0nnn` (`0x80..0x87`) | Dolby AC-3 audio | `nnn` |
| `1000 1nnn` (`0x88..0x8F`) | DTS-HD audio | `nnn` |
| `1010 0nnn` (`0xA0..0xA7`) | Linear PCM audio | `nnn` |
| `1011 0nnn` (`0xB0..0xB7`) | MLP (Dolby TrueHD) audio | `nnn` |
| `1100 0nnn` (`0xC0..0xC7`) | **DD+ (E-AC-3)** audio | `nnn` |
| `1111 1111` (`0xFF`) | provider-defined | |

`[2]`
`[11]`
**VERIFIED** (DD+ range on disc; other ranges patent-only, marked below)

### The rule a demuxer applies

```
decoding_number = @streamNumber - 1          # 1-based -> 0-based nnn
codec           = MediaAttributeList[@mediaAttr].codec
Audio:  find 0xBD packs whose sub_stream_id = CODEC_BASE | decoding_number
        CODEC_BASE: DD+ 0xC0, AC-3 0x80, DTS-HD 0x88, LPCM 0xA0, MLP 0xB0
        (MPEG audio instead uses stream_id 0xC0|nnn, no 0xBD wrapper)
Video (main): 0xE0 (MPEG-2) | 0xE2 (AVC) | 0xFD ext 0x55 (VC-1) per @mediaAttr codec
Subtitle: 0xBD packs whose sub_stream_id = 0x20 | decoding_number  (0x20..0x3F)
```

**Feeding the decoder.** In a `0xBD` pack, after the PES header the payload starts with
the DVD-style 4-byte `private_stream_1` sub-header: `sub_stream_id`(1), frame-header
count(1), first-access-unit pointer(2, BE). Observed on DOWNFALL DD+ as `c0 01 03 84 …`.
**Strip those 4 bytes** and hand the elementary stream (E-AC3/AC-3/MLP/DTS-HD/LPCM) to the
codec; this is the DVD convention ffmpeg's PS path already handles. VC-1 (`0xFD`/ext `0x55`)
and MPEG-2/AVC carry sequence headers **in-band** (`00 00 01 0F` for VC-1, confirmed on
DOWNFALL). No reconstructed extradata. `[2]` **VERIFIED** (framing on disc).

Sub-picture range `0x20..0x3F` gives 32 streams, exactly `SubtitleTrack` max 32
([03](03_playlist.md) §3.8). Audio decoding number is 3 bits → 8 per codec, matching
`AudioTrack` max 8.

**Grades.** Video VC-1 `0xFD`/`0x55` and DD+ audio `0xC0+` VERIFIED on disc. AC-3 /
DTS-HD / LPCM / MLP audio bases and the `0x20` sub-picture base are **INFERRED**
from TABLE 46 (patent). Not all codecs appear in the sampled clips, but the bit
patterns are a closed table and the demuxer applies them uniformly. Sub / secondary video (VS_PCK, picture-in-picture) is carried **inside**
`private_stream_1` (`0xBD`), sub_stream_id `0x91` MPEG-2 / `0x92` AVC / `0x93`
VC-1 (WO2006070920A1 FIG.119–120), not the `0xE0`/`0xE2`/`0xFD` main-video ids.
Sub audio (AS_PCK) uses the TABLE 46 audio ranges. PiP is selected by the clip's
`SubVideo`/`SubAudio` mapping, is not on the linear-playback path, and no sampled
clip carries it, so those ids are patent-only here. `[3]` **INFERRED**.

## 8.8 Sub-picture (SP_PCK): `2bitRLC` / `8bitRLC` decode

Needed to render subtitles / SP-based menus. Routing is §8.7 (`0xBD` sub
`0x20|(n-1)`). Payload is a **Sub-picture Unit (SPU)**: header `SPUH`, run-length
pixel data `PXD`, then a display-control sequence table `SP_DCSQT`. An SPU spans
one or more SP_PCKs; the last SP_PCK may pad.
`[2]`

### Pixel values (TABLE 67/68)

9-bit code. Bit 8 = 0 selects one of the four *specified* pixels; bit 8 = 1 is an
8-bit gray/gradation index (`8bitRLC`). `2bitRLC` uses only the specified four.

| Code | Pixel |
|---|---|
| `0 0000 0000` | Background |
| `0 0000 0001` | Pattern |
| `0 0000 0010` | Emphasis-1 |
| `0 0000 0011` | Emphasis-2 |
| `1 xxxx xxxx` | Pixel-4 … Pixel-255 (`1 0000 0000`..`1 0000 0011` **prohibited**) |

Actual RGB/contrast for each index comes from the display-control commands
(color + contrast), not from the code itself.

### Run-length rule (eight patterns, MSB-first bitstream)

Specified-4 pixels (2-bit color `PIX1 PIX0`):

| Run | Unit bits | Layout | Run value |
|---|---|---|---|
| 1 | 4 | `Comp=0 PIX2=0 PIX1 PIX0` | 1 |
| 2–9 | 8 | `Comp=1 PIX2=0 PIX1 PIX0 LEXT=0 RUN2..0` | RUN+2 |
| 10–136 | 12 | `Comp=1 PIX2=0 PIX1 PIX0 LEXT=1 RUN6..0` | RUN+9 |
| to EOL | 12 | `Comp=1 PIX2=0 PIX1 PIX0 LEXT=1 RUN=0` | to end of line |

8-bit pixels (`8bitRLC`, color `PIX7..PIX0`):

| Run | Unit bits | Layout | Run value |
|---|---|---|---|
| 1 | 9 | `Comp=0 PIX7=1 PIX6..0` | 1 |
| 2–9 | 13 | `Comp=1 PIX7=1 PIX6..0 LEXT=0 RUN2..0` | RUN+2 |
| 10–136 | 17 | `Comp=1 PIX7=1 PIX6..0 LEXT=1 RUN6..0` | RUN+9 |
| to EOL | 17 | same, `RUN=0` | to end of line |

Line width = `SET_DAREA2` display area. PXD is stored per field (top field PXD
first, then bottom, after `SPUH`); byte-align at each field/line boundary per the
figure tables (69–76, image-only; the prose above is the authoritative encoding).
**INFERRED** bit order from prose; TABLE 69–76 pixel layouts are figure images.

### Display-control sequence (`SP_DCSQT`)

`SP_DCSQ` entries carry a presentation time (`SP_DCSQ_STM`, relative to SPU PTS)
and an offset to the next `SP_DCSQ`, then commands. The command set (bit layout in
a figure table, names per §5.5.4.4):

| Command | Effect |
|---|---|
| `STA_DSP` / `FSTA_DSP` | start (or forced-start) sub-picture display at this time |
| `STP_DSP` | stop display (also used to clear at a Cell boundary) |
| `SET_COLOR` | 4 palette indices for Background/Pattern/Emphasis-1/-2 |
| `SET_CONTR` | 4 contrast (alpha) values, one per specified pixel |
| `SET_DAREA2` | display rectangle (line width + top/bottom) |
| `SET_DSPXA` | PXD start addresses (top / bottom field) |
| `CHG_COLCON` | change color/contrast mid-display (karaoke wipes) |
| `END` | end of this `SP_DCSQ` |

**Command opcodes close by DVD parity.** HD DVD sub-picture reuses the DVD-Video
display-control command set; the opcode bytes are the DVD ones (public: DVD-Video
spec / ffmpeg `dvdsubdec`): `0x00` FSTA_DSP, `0x01` STA_DSP, `0x02` STP_DSP, `0x03`
SET_COLOR, `0x04` SET_CONTR, `0x05` SET_DAREA, `0x06` SET_DSPXA, `0x07` CHG_COLCON,
`0xFF` CMD_END, with HD DVD adding **`SET_DAREA2`** for the larger HD display area
(book §5.5.4.4 names it). A DVD sub-picture decoder extended for 8-bit RLC (§8.8
run-length) and the HD display rectangle handles HD DVD SP. **INFERRED** (opcode
bytes by DVD parity; `SET_DAREA2` from the book).

For plain subtitles a decoder needs `SET_DAREA2`, `SET_COLOR`, `SET_CONTR`,
`STA_DSP`/`STP_DSP`. `8bitRLC` gray indices use a 256-entry CLUT the same commands
extend. **INFERRED** (command bit layouts are figure-only; names and roles are
§5.5.4.4 prose). No SP_PCK subtitle appeared in the sampled feature windows.
Advanced titles usually caption via HDi Advanced Subtitle markup instead, so this
path is **specified but not corpus-exercised**.
