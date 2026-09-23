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

PES length 257 = 1 byte substream id + 256 bytes GCI. The patent's split of those
256 bytes (Tables 50–51) does not match the disc; the observed layout is §8.5.

Typical pack prefix:

```
00 00 01 BA <14-byte pack header>
00 00 01 BB <system header>
00 00 01 BF <PCI or GCI or DSI PES> …
```

Order of the three PES packets is GCI/PCI/DSI as listed in the patent; parse by
substream id, not by order. Some Advanced clips omit PCI: `STALINGRAD`
`black.EVO` is GCI `0x04` + DSI `0x01` only (35/35 VOBUs). On `RAMBO_1_FRA` the PCI
slot is still present but **zero-filled, start code included** (983 zero bytes =
6-byte PES header + 977): the DSI follows at pack offset 1287. A parser that walks PES
packets back to back stops at the gap, so **scan for the next `00 00 01 BF`** instead
(`e23`). `[11]` **VERIFIED**

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

257-byte PES payload. The patent's TABLE 52 field list (`GCI_GI` 16 bytes of
`GCI_CAT`, reserved, `DCI_CCI_SS`, `DCI`, `CCI`, then `RECI` 189 + reserved 51) **does
not match the disc**. Observed layout (offsets in the PES payload, `0x04` = byte 0;
`e23`, 24 EVOBUs on each of 12 discs):

| Off | Size | Field | Observed |
|---|---|---|---|
| 0 | 1 | `sub_stream_id` | `0x04` |
| 1 | 1 | `GCI_CAT` | `0x40` on Advanced (AACS and unencrypted); `0x00` on Standard Content (`RESERVOIR_DOGS`) |
| 2 | 5 | **EVOBU start PTM**, 90 kHz | equals `EVOBI` start PTM ([06](06_vti.md)) at the EVOB's first EVOBU on 12/12 discs, then advances by each EVOBU's duration (45 045, or 87 087 for a longer EVOBU). Top byte 0 on every sample; width 32 vs 40 bits undetermined |
| 7 | 6 | reserved | zero on every sample |
| 13 | 16 | **AACS CPI** | Table 4-1 layout, [09](09_aacs.md) §9.6. All zero on the unencrypted `1408_DC` |
| 29 | 228 | `RECI` and reserved | zero on 10 of 12 discs. `AEON_FLUX` and `TRANSFORMERS` (both Paramount) carry an identical repeating 10-byte record from byte 33, `80 25 23 25 1e 19 20 01 23 40`; undecoded (TABLE 53 names ISRC blocks) |

The CPI sits at pack **`0x3C`** on the observed framing (pack header 14 bytes, system
header, GCI start code at `0x29`, `sub_stream_id` at `0x2F`). Locate the GCI by
`sub_stream_id` rather than hard-coding the pack offset, since stuffing or a missing
system header moves it. **Do not** read `GCI_CAT` (`0x40`) as the AACS `KEY_VF`: it
would decode as "segment key". `[11]` **VERIFIED**

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
([03](03_playlist.md) §3.17). Audio decoding number is 3 bits → 8 per codec, matching
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

## 8.8 Sub-picture (SP_PCK): Sub-picture Unit

Bitmap subtitles. Routing is §8.7 (`0xBD`, `sub_stream_id` `0x20 | (n-1)`, up to 32
streams). Each **Sub-picture Unit (SPU)** is one image plus the commands that
show, colour and hide it: header `SPUH`, run-length pixel data `PXD` (top field,
then bottom field), then the display-control sequence table `SP_DCSQT`. An SPU
spans one or more SP_PCKs; reassemble the payload bytes after the
`sub_stream_id` until `SPU_SZ` bytes are collected. The first SP_PCK of an SPU
carries the PES PTS, which is the SPU's time origin.

Every Advanced title in the corpus uses the **8-bit** SPU of patent §5.5.4. All
1258 `SP_ATR` words say so ([06](06_vti.md)), and all SPUs sampled carry the
10-byte header below. `e25` checks three SPUs saved in `spec/raw/evo_samples/`
(12_MONKEYS, 1408_DC, STALINGRAD) and, with `E25_LIVE=1`, every SPU in 12 EVOBUs
from the middle of 12 features: 54 SPUs on 11 discs (1408_DC, 16_BLOCKS,
40YR_OLD_VIRGIN, DOOM, GOODFELLAS, HOT_FUZZ, MYSTERY_MEN, PANS_LABYRINTH,
STALINGRAD, TRANSFORMERS, U2_RATTLE_AND_HUM; the 12_MONKEYS window is silent,
and 18 more SPUs from a window at 40% of it agree). `[2, 11, 12]` **VERIFIED**

The 2-bit, DVD-shaped SPU (patent §5.5.3) starts with a non-zero 2-byte
`PRE_HEAD` (DVD size field). A `0000h` start selects the long header. No
Advanced title here uses the 2-bit form.

### SPUH (patent Table 66)

| Off | Size | Field | On disc |
|---|---|---|---|
| 0 | 2 | `SPU_ID` | `0000h` |
| 2 | 4 | `SPU_SZ` | SPU size in bytes; always even (odd sizes get one `FFh`) |
| 6 | 4 | `SP_DCSQT_SA` | offset of `SP_DCSQT` from the first SPU byte |

`PXD` starts right after the header: the top-field address is **10** on every SPU.

### SP_DCSQT: display-control sequences

A chain of `SP_DCSQ` entries, starting at `SP_DCSQT_SA`:

| Off | Size | Field |
|---|---|---|
| 0 | 2 | `SP_DCSQ_STM`: start time relative to the SPU PTS, in units of 1024 / 90 000 s (≈11.4 ms, DVD parity) |
| 2 | 4 | `SP_NXT_DCSQ_SA`: offset of the next `SP_DCSQ` from the first SPU byte. **The last one points at itself** |
| 6 | … | commands, ended by `FFh` |

DVD uses 2-byte addresses here. HD DVD widens them to 4. The last DCSQ ends the
SPU (at most `FFh` padding follows). The `STM` unit is checked on disc: every
`STP_DSP` time × 1024 lands before the next SPU of the same stream, typically
70–100 ms early (the gap between two subtitles).

### Display-control commands

| Opcode | Name | Operand | Meaning |
|---|---|---|---|
| `01h` | `STA_DSP` | none | start display |
| `02h` | `STP_DSP` | none | stop display |
| `83h` | colour table | 768 bytes | 256 × (`Y`, `Cr`, `Cb`), one per pixel value: 0–3 the specified pixels (background, pattern, emphasis-1, emphasis-2), 4–255 the 8-bit pixels (patent Table 61) |
| `84h` | contrast table | 256 bytes | one contrast per pixel value (Table 62). **`FFh` = fully transparent, lower = more opaque** |
| `85h` | `SET_DAREA2` | 6 bytes | display area, two 24-bit words of 12-bit start + 12-bit end: x (`x0 << 12 \| x1`), then y. Width = `x1 − x0 + 1` |
| `86h` | PXD addresses | 8 bytes | top-field and bottom-field `PXD` offsets from the first SPU byte, 4 bytes each |
| `FFh` | `CMD_END` | none | end of this `SP_DCSQ` |

No other opcode appears on disc. Typical first DCSQ: `01 83 84 85 86 FF`, and the
last DCSQ: `02 FF` at the stop time. The high bit separates these HD commands from
the DVD ones they replace (`03h` SET_COLOR, `04h` SET_CONTR, `05h` SET_DAREA,
`06h` SET_DSPXA with 16-colour, 4-bit fields and 2-byte addresses).

Contrast direction, from the discs: the clear area around the text is the most-used
pixel value on every SPU and has contrast `FFh`, and the text itself `00h`.
STALINGRAD fades a subtitle in and out with contrast-only DCSQs (`84` alone) that
step every contrast `FF → F6 → F2 → EE … 88`, hold, then back to `FF` before
`STP_DSP`. Most discs use pixel value 0 (background) for the clear area; 1408_DC
uses 8-bit value 227. **Decide transparency by contrast, not by pixel value.**

### Pixel data (8bitRLC, patent §5.5.4.2, TABLE 67–76)

MSB-first bit units; each **line** starts on a byte boundary; a line holds exactly
the display-area width in pixels.

| Unit | Bits | Layout |
|---|---|---|
| 1 pixel, specified | 4 | `Comp=0` `flag=0` `PIX1 PIX0` (value 0–3) |
| 1 pixel, 8-bit | 10 | `Comp=0` `flag=1` `PIX7…PIX0` (value 4–255; 0–3 prohibited here) |
| run of 2–9 | +4 | `Comp=1` + pixel as above + `LEXT=0` `RUN2…0`; run = `RUN + 2` |
| run of 10–136 | +8 | `Comp=1` + pixel + `LEXT=1` `RUN6…0`; run = `RUN + 9` |
| to end of line | +8 | `Comp=1` + pixel + `LEXT=1` `RUN = 0` |

The 8-bit value is a full byte after the flag (a 10-bit unit), not 7 bits: with 7,
every line overruns its width. Top field holds lines 0, 2, 4…, bottom field
1, 3, 5…; each field is followed by 0–2 zero bytes of padding. An encoder may
write one extra empty line per field (1408_DC full-frame SPUs: 540 lines per field
for a 1078-line area); decode the area's lines and ignore the rest.

## 8.9 AACS vs container

Encrypted packs (not NV_PCK, not ADV_PCK):

| Bytes | Content |
|---|---|
| 0–127 | clear (pack/PES headers, `Dtk` at 84–87) |
| 128–2047 | AES-CBC payload |

`PES_scrambling_control` at pack byte 20: `01b` = Encrypted Portion present.
See [09](09_aacs.md).
