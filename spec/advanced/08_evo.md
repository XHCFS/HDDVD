# 8. EVO: MPEG-2 program stream

*Counts written "N/120", "N/119", "on N discs", "listings", or as named discs are over the reference corpus of 120 archived retail HD DVD images [11]. `eNN` are the reproducible verification experiments [12].*


Path: `HVDVD_TS/<clip>.EVO`  
Container: MPEG-2 program stream, **2048-byte packs**.  
Pack start: `00 00 01 BA` at every 2048-byte boundary; MPEG-2 marker bits `01`.

Any MPEG-2 PS demuxer that accepts 2048-byte packs can demux this. Navigation
headers are in the clear even on AACS discs.

## 8.1 Pack types [23 §6.3.5]

| Pack | Contents |
|---|---|
| NV_PCK | Navigation: GCI + DSI (first pack of each EVOBU) |
| VM_PCK | Main video (MPEG-2 / AVC / VC-1) |
| AM_PCK | Main audio (DD+, MPEG, LPCM, DTS-HD, MLP) |
| VS_PCK | Sub video |
| AS_PCK | Sub audio (DD+, DTS-HD; optional mp3, HE-AAC v2, WMA Pro) |
| SP_PCK | Sub-picture |
| ADV_PCK | Advanced stream (archive files for the File Cache); `sub_stream_id = 0x80` |
| HLI_PCK | Highlight (Standard menus); `sub_stream_id = 0x08`; **ignore on Advanced** |

The book: a PCI or HLI in a Primary Video Set EVOB **shall be ignored** [23 §6.3.5.1].
Seek uses MAP + DSI, not PCI buttons.

An EVOBU starts with exactly one NV_PCK and runs to the next one or the end of the
EVOB. It plays 0.4 to 1.001 s (the last of an EVOB up to 1.2012 s), a whole number
of VSTUs, and starts where the previous one ended. The first EVOBU of an EVOB has
main video. Every stream is complete inside its EVOB. Rates: the EVOB at most
30.24 Mbit/s, main video 29.40 (HD) or 15.00 (SD), main audio 19.60 in total and
18.43 per stream, sub audio 4.00 in total and 512 kbit/s per stream [23 §6.3.5].

## 8.2 NV_PCK: first pack of each EVOBU

Three `private_stream_2` (`stream_id = 0xBF`) PES packets:

| `sub_stream_id` | PES length | Identity |
|---|---|---|
| `0x04` | 257 (`0x0101`) | GCI |
| `0x00` | 977 | PCI (Standard VTS only; inside the reserved area) |
| `0x01` | 755 (`0x02F3`) | DSI |

The book's NV_PCK [23 §6.3.5.2.2]: pack header (14), system header, GCI packet
(6-byte header, `sub_stream_id`, 256 bytes), a **reserved area** of one 983-byte PES
packet, then the DSI packet (`sub_stream_id`, 754 bytes). The reserved area may
hold a PCI packet (when a Standard VTS EVOB is reused) or an RDI packet
(Interoperable); a player ignores it. `private_stream_2` sub stream ids
[23 Table 6.3.5.1.1-3]: `0x00` PCI (reserved), `0x01` DSI, `0x04` GCI, `0x08` HLI
(reserved), `0x50` RDI (reserved), `0x80` Advanced stream, `0xFF` provider defined.

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

Order is GCI, reserved area, DSI; parse by substream id, not by order. Some
Advanced clips omit PCI: `STALINGRAD` `black.EVO` is GCI `0x04` + DSI `0x01` only
(35/35 VOBUs). On `RAMBO_1_FRA` the reserved area is **zero-filled, start code
included**: exactly the book's 983 bytes. The DSI follows at pack offset 1287. A
parser that walks PES packets back to back stops at the gap, so **scan for the next
`00 00 01 BF`** instead (`e23`). `[23]` **SPEC**; `[11]` **VERIFIED**

System header values [23 Table 6.3.5.2.2-1]: `rate_bound` `0x824EA1` (30.24 Mbit/s),
`audio_bound` 0–8, `video_bound` 1 or 2, buffer bounds `0xB9` (all video) 1808 kB,
`0xB8` (all audio) 8192 B, `0xBD` 1568 kB, `0xBF` 2 kB, `0xFD` 1808 kB.

## 8.3 PCI GI (offsets from the substream id byte)

The book's Standard-content PCI [23 Vol 2 §5.2.6] is `PCI_GI` 60 bytes,
`NSML_AGLI` 36, reserved. A player ignores it on Advanced Content.

| Off | Size | Field |
|---|---|---|
| 0 | 1 | `0x00` |
| 1 | 4 | `NV_PCK_LBN` |
| 5 | 4 | reserved (DVD has `vobu_cat` at 5; the HD DVD book reserves it) |
| 9 | 4 | `EVOBU_UOP_CTL` (Standard Content user-operation bits) |
| 13 | 4 | `EVOBU_S_PTM` 90 kHz |
| 17 | 4 | `EVOBU_E_PTM` 90 kHz |
| 21 | 4 | `EVOBU_SE_E_PTM` (end at a sequence end code; 0 if none) |
| 25 | 4 | `C_ELTM` (BCD time) |
| 29 | 32 | reserved |

`vobu_e_ptm − vobu_s_ptm` = 45045 ticks = 500.5 ms = 15 frames at 29.97 on the
checked VOBUs. Next VOBU `vobu_s_ptm` equals previous `vobu_e_ptm`.

Advanced PCI GI may be filled (DOWNFALL) or zeroed (MYSTERY_MEN VOBU0).
Highlight buttons are **not** in this packet on HD DVD; they are HLI_PCK `0x08`.

## 8.4 DSI (offsets from the substream id byte)

754 bytes after the `0x01`: `DSI_GI` 32 at offset 1, `SML_PBI` 276 at 33,
`SML_AGLI` 54 at 309, `EVOBU_SRI` 168 at 363, `SYNCI` 168 at 531, reserved 56
[23 Vol 2 §5.2.7, §6.3.4].

**DSI_GI**

| Off | Size | Field |
|---|---|---|
| 0 | 1 | `0x01` |
| 1 | 4 | `NV_PCK_SCR`, low 32 bits of this pack's `SCR_base` |
| 5 | 4 | `NV_PCK_LBN`, on Advanced Content the RLBN from the first sector of the EVOB |
| 9 | 4 | `EVOBU_EA`, last pack of the EVOBU as RLBN from its first: pack count minus one |
| 13 | 4 | `EVOBU_1STREF_EA`, end of the first reference picture (RLBN; 0 without video) |
| 17 | 4 | `EVOBU_2NDREF_EA` |
| 21 | 4 | `EVOBU_3RDREF_EA` (0 if absent) |
| 25 | 2 | `EVOBU_EVOB_IDN`, EVOB ID number |
| 27 | 1 | `EVOBU_ADP_ID` / upper cell id bits (reserved on Advanced) |
| 28 | 1 | `EVOBU_C_IDN`, 0 on Advanced |
| 29 | 4 | `C_ELTM`, 0 on Advanced |

Walk: `next_lbn = this_lbn + EVOBU_EA + 1`.  
`EVOBU_EA + 1` equals MAP `EVOBU_SZ` on Advanced content checked.

**SML_PBI** (seamless playback, 276 bytes): `EVOBU_SML_CAT` (2; b15 PREU, b14 ILVU,
b13 unit start, b12 unit end), `ILVU_EA` (4), `NXT_ILVU_SA` (4), `NXT_ILVU_SZ` (2),
`EVOB_V_S_PTM` (4), `EVOB_V_E_PTM` (4; the same in every EVOBU of the EVOB), then
for each of the 8 decoding audio numbers the main-audio stop times and gap lengths
(`EVOB_AM_STP_PTM`, `EVOB_AM_GAP_LEN`, two 4-byte values per stream each) and the
same for sub audio (`AS`). **SML_AGLI** (54): 9 × 6-byte seamless-angle
destinations (b46–b16 destination ILVU start RLBN, b15–b0 its size), all 0 unless
the block is a seamless angle block. **SYNCI** (168): the nearest AM_PCK per main
audio stream (8 × 2), SP_PCK per sub-picture stream (32 × 4), reserved, sub video
(2) and sub audio (8 × 2), each indexed by decoding stream number.
**EVOBU_SRI** is recorded but a player need not use it [23 Annex N.2].

Not required for MAP-based seek; required for seamless joins ([03](03_playlist.md)
§3.10) and angle changes.

## 8.5 GCI (substream `0x04`)

257-byte PES payload: `GCI_GI` 32 bytes, `RECI` 189, reserved 35
[23 Vol 2 §5.2.5, §6.3.3]. The patent's TABLE 52 (16-byte GI, `RECI` + 51) does
not match the disc; the book does. Offsets in the PES payload, `0x04` = byte 0
(`e23`, 24 EVOBUs on each of 12 discs):

| Off | Size | Field | Observed |
|---|---|---|---|
| 0 | 1 | `sub_stream_id` | `0x04` |
| 1 | 1 | `GCI_CAT` | b7–b6 EVOBU category: `00` Standard, `01` Advanced, `10` Interoperable; the rest reserved. `0x40` on Advanced (AACS and unencrypted); `0x00` on Standard Content (`RESERVOIR_DOGS`) |
| 2 | 1 | reserved | 0 |
| 3 | 4 | `EVOBU_S_PTM`, 90 kHz | start of the first picture of the EVOBU in display order. Equals `EVOB_V_S_PTM` ([06](06_vti.md)) at the EVOB's first EVOBU on 12/12 discs, then advances by each EVOBU's duration (45 045, or 87 087 for a longer EVOBU) |
| 7 | 2 | reserved | 0 |
| 9 | 4 | `DCI` | reserved for Interoperable Content; 0 on Standard and Advanced |
| 13 | 16 | `CPI`, copy protection information | AACS Table 4-1 layout, [09](09_aacs.md) §9.6. All zero on the unencrypted `1408_DC` |
| 29 | 4 | reserved | 0 |
| 33 | 189 | `RECI`, recording information | zero on 10 of 12 discs |
| 222 | 35 | reserved | 0 |

**RECI** [23 Vol 2 §5.2.5.2, Annex T]: ISRC of the video (10 bytes), of decoding
audio streams 0–7 (8 × 10), of 8 sub-picture streams (8 × 10), then three select
bytes (`ISRC_V_SEL`, `ISRC_A_SEL`, `ISRC_SP_SEL`: b7 main/sub, and for sub-pictures
which group of 8 streams) and 16 reserved. Each ISRC: b79 valid flag, two 6-bit
country characters, three 6-bit owner characters, year and recording number in
BCD; characters `0`–`9` = 0–9, `A`–`Z` = `0x11`–`0x2A`. `AEON_FLUX` and
`TRANSFORMERS` (both Paramount) repeat `80 25 23 25 1e 19 20 01 23 40` from byte
33: valid, country `US`, owner `UNI`, year `20`, number `01234`, a placeholder
ISRC.

The CPI sits at pack **`0x3C`** on the observed framing (pack header 14 bytes, system
header, GCI start code at `0x29`, `sub_stream_id` at `0x2F`). Locate the GCI by
`sub_stream_id` rather than hard-coding the pack offset, since stuffing or a missing
system header moves it. **Do not** read `GCI_CAT` (`0x40`) as the AACS `KEY_VF`: it
would decode as "segment key". `[11]` **VERIFIED**

## 8.6 ADV_PCK (`sub_stream_id = 0x80`)

`private_stream_2`. The book allows `PES_scrambling_control` `01b` (a
copy-protection structure) [23 Table 6.3.5.2.8-1]; every observed pack has 0.
FIG.81A: pack header then one Advanced
PES (no NV_PCK system header). File Cache, never the AV decoder. The Advanced
Stream carries only archive files ([04](04_aca.md)); each starts on a pack
boundary, and only the last pack of a file may hold stuffing (1–7 bytes) or a
padding packet (8 or more) [23 §6.3.5.2.8, §6.3.5.3.5].

Playlist `ApplicationResource@multiplexed` / `PlaylistApplicationResource@multiplexed`
as an integer is the **`advanced_identifier`** carried in every ADV_PCK of that
archive. Different archives never share an identifier; one archive may be
multiplexed into several EVOBs under the same one. `false` means load only from
the `src` URI. A numeric identifier does **not** guarantee packs in that title’s
EVO: `OLIVER_TWIST_JPN` `LoopMenu.EVO` (46 MB, `multiplexed="1"`)
and `JpnTokuhou.EVO` (64 MB, `multiplexed="2"`) have **0** `0x80` packs; the
ACA still exists under `ADV_OBJ`, as the book requires. Always load `src`. If
ADV_PCK for that identifier appears in the playing EVOB, concat it. On
`STALINGRAD` `logo.EVO` the bytes **equal** the `ADV_OBJ` file (`e16`).

### Pack grammar (`e16`, `STALINGRAD` `logo.EVO`, N=2383)

Stuffing length 0. PES at pack offset 14: `00 00 01 BF`, `PES_packet_length`
2028 on full packs (14+6+2028=2048). Payload:

The book's ADV_PKT [23 §6.3.5.2.8]:

| Off | Size | Field |
|---|---|---|
| 0 | 1 | `sub_stream_id` = `0x80` |
| 1 | 2 | b15–b14 `PES_scrambling_control` (`00` none, `01` copy-protection structure present); b13–b12 `advanced_pkt_status`; b11–b0 `advanced_identifier` = XPL `@multiplexed` (`1`…`6` here) |
| 3 | 255 | `advanced_file_name`, the archive's name, ISO 8859-1, zero-filled. **Only when the status is `01b` or `11b`** |
| next | 1 | `number_of_stuffing_bytes`, 0–7 |
| next | n | `0xFF` stuffing |
| next | … | archive bytes |

`advanced_pkt_status`: `01b` first pack of the archive, `00b` middle, `10b` last,
`11b` the whole archive in one pack. On disc `01b` 6 packs, `00b` 2371, `10b` 6.
Scramble 0 (clear packs).

So the archive bytes start at `3 + 255 + 1 + n` = **259** (no stuffing) in a first
pack and at `3 + 1 + n` = **4** in the others. `STALINGRAD` agrees: the name
(`mainApp.aca` … `ineditsMenu.aca`) is zero-filled to 255 bytes, byte 258 is 0,
and `HDDVDACA` starts at 259; middle and last packs have byte 3 = 0 and data at 4.
The ACA header `FILE_SZ` at +14 equals the `ADV_OBJ` file length (`mainApp.aca`
260447).

Concat per identifier, pack order:

```
off = 3
if status in (01b, 11b): off += 255
n = payload[off]; off += 1 + n
out += payload[off:]
```

`E16_FULL=1` reconstituted all six identifiers; each blob matched
`/ADV_OBJ/<name>.aca`. An earlier version of this sheet located the data by
searching for `HDDVDACA` and read byte 2 alone as the identifier; the book's rule
replaces both. TABLE 91's "32-byte name then data on every packet" is **wrong**.
`[23]` **SPEC**; `[11, 12]` **VERIFIED**
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
| DD+ / DTS-HD / LPCM / MLP | `0xBD` + `sub_stream_id` (§8.7; `nnn` = decoding stream number, 0-based vs XPL `streamNumber` 1-based) |
| Sub-picture | `0xBD`, `sub_stream_id = 001nnnnnb` |
| Sub video (PiP) | `stream_id` `0xE1` MPEG-2, `0xE3` AVC, `0xFD` with extension `0x56` VC-1 [23 Table 6.3.5.1.1-1] |
| Sub audio | `0xBD` + `sub_stream_id` `0xC8`+ DD+, `0x98`+ DTS-HD, `0xB8`+ WMA Pro; `stream_id` `0xC8`–`0xCF` mp3, `0xD8`–`0xDF` HE-AAC v2 |
| ADV_PCK | `0xBF`, `sub_stream_id = 0x80` → **File Cache, never the AV decoder** |

`[23]` `[2]` `[11]`

## 8.7 Elementary-stream routing (TABLE 45 / 46): how `@streamNumber` finds its PES

This is what a player uses to demux the track the playlist selected. A clip's
`<Video>/<Audio>/<Subtitle>` child carries `@streamNumber` (1-based decoding
number) and `@mediaAttr` (codec via `MediaAttributeList`, [03](03_playlist.md)).
`@streamNumber` maps to the PES stream as follows.

### stream_id / stream_id_extension (TABLE 45)

| `stream_id` | ext | Stream |
|---|---|---|
| `110x 0nnn` (`0xC0..0xC7`,`0xD0..0xD7`) | | MPEG audio, main; decoding audio number = `nnn` |
| `1100 1nnn` (`0xC8..0xCF`) | | mp3, sub audio (optional) |
| `1101 1nnn` (`0xD8..0xDF`) | | MPEG-4 HE-AAC v2, sub audio (optional) |
| `1110 0000` (`0xE0`) | | Main video MPEG-2 |
| `1110 0001` (`0xE1`) | | Sub video MPEG-2 |
| `1110 0010` (`0xE2`) | | Main video MPEG-4 AVC (H.264) |
| `1110 0011` (`0xE3`) | | Sub video MPEG-4 AVC |
| `1011 1101` (`0xBD`) | | private_stream_1 (audio + sub-picture, below) |
| `1011 1111` (`0xBF`) | | private_stream_2 (NV_PCK / ADV_PCK, §8.2 / §8.6) |
| `1111 1101` (`0xFD`) | `101 0101` (`0x55`) | Main video **VC-1** (extended_stream_id; ext byte in the PES extension) |
| `1111 1101` (`0xFD`) | `101 0110` (`0x56`) | Sub video VC-1 |

A Secondary Video Set uses decoding number 0 for its optional-codec sub audio
(`0xC8` mp3, `0xD8` HE-AAC v2, `0xB8` WMA Pro) [23 Annex Q].
`[23 Table 6.3.5.1.1-1]` **SPEC**; `[2]`; `[11]` **VERIFIED** (main video ids)

VC-1 is the AMD2:2004 extended-stream-id mechanism: `stream_id=0xFD`, real type in
`stream_id_extension` (`0x55`). Parse the PES extension flags to reach it; do not
treat `0xFD` as generic private data.

### sub_stream_id for private_stream_1 = `0xBD` (TABLE 46)

The first byte of the PES payload (after the PES header) is `sub_stream_id`:

| `sub_stream_id` | Stream | decoding number |
|---|---|---|
| `001x xxxx` (`0x20..0x3F`) | **Sub-picture** (subtitle) | `x xxxx` = decoding sub-picture number |
| `1000 0nnn` (`0x80..0x87`) | reserved (AC-3, Interoperable Content) | `nnn` |
| `1000 1nnn` (`0x88..0x8F`) | DTS-HD main audio | `nnn` |
| `1001 1nnn` (`0x98..0x9F`) | DTS-HD sub audio | `nnn` |
| `1010 0nnn` (`0xA0..0xA7`) | Linear PCM main audio (1/1200 s frames) | `nnn` |
| `1010 1nnn` (`0xA8..0xAF`) | reserved (LPCM 1/600 s, Interoperable) | |
| `1011 0nnn` (`0xB0..0xB7`) | MLP (Dolby TrueHD) main audio | `nnn` |
| `1011 1nnn` (`0xB8..0xBF`) | WMA Pro sub audio (optional) | `nnn` |
| `1100 0nnn` (`0xC0..0xC7`) | **DD+ (E-AC-3)** main audio | `nnn` |
| `1100 1nnn` (`0xC8..0xCF`) | DD+ sub audio | `nnn` |
| `1111 1111` (`0xFF`) | provider-defined | |

Every other value is reserved and must not appear [23 Table 6.3.5.1.1-2].
`[23]` **SPEC**; `[2]`; `[11]` **VERIFIED** (DD+ range on disc)

### The rule a demuxer applies

```
decoding_number = @streamNumber - 1          # 1-based -> 0-based nnn
codec           = MediaAttributeList[@mediaAttr].codec
Audio:  find 0xBD packs whose sub_stream_id = CODEC_BASE | decoding_number
        CODEC_BASE: DD+ 0xC0, AC-3 0x80, DTS-HD 0x88, LPCM 0xA0, MLP 0xB0
        (MPEG audio instead uses stream_id 0xC0|nnn, no 0xBD wrapper)
Video (main): 0xE0 (MPEG-2) | 0xE2 (AVC) | 0xFD ext 0x55 (VC-1) per @mediaAttr codec
Subtitle: n = SPST_ATR[@streamNumber - 1] decoding number for the output
        (HD, or SD wide / letterbox / pan-scan; sheet 06 §6.2)
        0xBD packs whose sub_stream_id = 0x20 | n  (0x20..0x3F)
```

On disc every `SPST_ATR` gives HD number `streamNumber − 1`, so the two readings
agree; the table lookup is still the rule.

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

**Grades.** Video VC-1 `0xFD`/`0x55`, MPEG-2 `0xE0` and DD+ audio `0xC0+` VERIFIED
on disc. Every id above is in the book's tables [23 §6.3.5.1.1], so the rest are
**SPEC**. Sub video (VS_PCK, picture-in-picture) has its own `stream_id`s
`0xE1` / `0xE3` / `0xFD`+`0x56`. An earlier version of this sheet took them from
WO2006070920A1 FIG.119–120 as `0xBD` sub-streams `0x91`–`0x93`; the book refutes
that. Sub audio (AS_PCK) is `0xBD` `0xC8`+ (DD+) or `0x98`+ (DTS-HD), or the
optional codecs above, with the same 4-byte private header as main audio. PiP is
selected by the clip's `SubVideo`/`SubAudio` mapping, is not on the linear-playback
path, and no sampled clip carries it.

## 8.8 Sub-picture (SP_PCK): Sub-picture Unit

Bitmap subtitles. Routing is §8.7 (`0xBD`, `sub_stream_id` `0x20 | (n-1)`, up to 32
streams). Each **Sub-picture Unit (SPU)** is one image plus the commands that
show, colour and hide it: header `SPUH`, run-length pixel data `PXD` (top field,
then bottom field), then the display-control sequence table `SP_DCSQT`. An SPU
spans one or more SP_PCKs; reassemble the payload bytes after the
`sub_stream_id` until `SPU_SZ` bytes are collected. The first SP_PCK of an SPU
carries the PES PTS, which is the SPU's time origin.

Every Advanced title in the corpus uses the **8-bit** SPU of [23 Vol 2 §5.5.4]
(patent §5.5.4). All
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
| 2 | 4 | `SPU_SZ` | SPU size in bytes, at most 1536 kB; always even (odd sizes get one `FFh`) |
| 6 | 4 | `SP_DCSQT_SA` | offset of `SP_DCSQT` from the first SPU byte; the table is at most half the SPU |

An SPU is valid from its PTS until the next SPU of the same stream; it fills whole
SP_PCKs and only its last pack may carry stuffing or padding. SPU PTSs strictly
increase per stream, the first is not before `EVOB_V_S_PTM` and the last
presentation ends by `EVOB_V_E_PTM`. In Advanced Content the display area is a
rectangle inside the Aperture for HD streams (x 0–1919, y 2–1079) or inside the SD
output for SD streams (x 0–719, y 2–479 at 60 Hz, 2–574 at 50 Hz), not inside the
video [23 §6.3.5.3.3, Vol 2 §5.5.4].

`PXD` starts right after the header: the top-field address is **10** on every SPU.

### SP_DCSQT: display-control sequences

A chain of `SP_DCSQ` entries, starting at `SP_DCSQT_SA`:

| Off | Size | Field |
|---|---|---|
| 0 | 2 | `SP_DCSQ_STM`: start time relative to the SPU PTS: bits 25–10 of a 90 kHz count, so units of 1024 / 90 000 s (≈11.4 ms). It lands on the VSTU grid: `STM = (3003·n)/2048` at 60 Hz, `(225·n)/128` at 50 Hz, `n` VSTUs after the PTS (even `n` for 29.97 / 25 fps video). The first DCSQ has `STM` 0; no two DCSQs share a time |
| 2 | 4 | `SP_NXT_DCSQ_SA`: offset of the next `SP_DCSQ` from the first SPU byte. **The last one points at itself** |
| 6 | … | commands, ended by `FFh` |

DVD uses 2-byte addresses here. HD DVD widens them to 4. The last DCSQ ends the
SPU (at most `FFh` padding follows). The `STM` unit is checked on disc: every
`STP_DSP` time × 1024 lands before the next SPU of the same stream, typically
70–100 ms early (the gap between two subtitles).

### Display-control commands

The book's commands [23 Vol 2 §5.5.4.4]; each appears at most once per DCSQ:

| Opcode | Name | Operand | Meaning |
|---|---|---|---|
| `00h` | `FSTA_DSP` | none | start display **even if** the user has sub-pictures off (forced captions) |
| `01h` | `STA_DSP` | none | start display; overruled when sub-pictures are off |
| `02h` | `STP_DSP` | none | stop display (a later `STA_DSP` may show it again) |
| `83h` | `SET_COLOR2` | 768 bytes | 256 × (`Y`, `Cr`, `Cb`), one per pixel value: 0–3 the specified pixels (background, pattern, emphasis-1, emphasis-2), 4–255 the 8-bit pixels. Kept until changed within the SPU |
| `84h` | `SET_CONTR2` | 256 bytes | one contrast per pixel value: video weight `k/256`, sub-picture weight `(256−k)/256`, `k` = value, or value + 1 when the value is not 0. **`00h` opaque, `FFh` fully transparent** |
| `85h` | `SET_DAREA2` | 6 bytes | display area, bits below |
| `86h` | `SET_DSPXA2` | 8 bytes | top-field and bottom-field `PXD` offsets from the first SPU byte, 4 bytes each; top-field data is lines `Ystart`, `Ystart+2`, …, bottom-field `Ystart+1`, … |
| `87h` | `CHG_COLCON2` | 2-byte size + `PXCD` | colour and contrast changes inside the area (below) |
| `FFh` | `CMD_END` | none | end of this `SP_DCSQ` |

`SET_DAREA2` operand (6 bytes): byte 1 b7 reserved, b6–b0 start X high 7 bits;
byte 2 b7–b4 start X low 4 bits, b3 reserved, b2–b0 end X high 3 bits; byte 3 end X
low 8 bits; bytes 4–6 the same for Y. Each coordinate is 11 bits; start Y is even.
Width = `endX − startX + 1` = the pixels per PXD line. On disc the reserved bits are
0, so a reader of 12-bit fields gets the same numbers; mask them anyway.

`CHG_COLCON2` (`PXCD`): a list of line groups, each a 4-byte `LN_CTLI` (change start
line, number of change points 1–8, change end line; lines in ascending,
non-overlapping order) followed by that many 1026-byte `PX_CTLI` (11-bit change
start pixel in the low bits of the first 2 bytes, then 768 colour bytes and 256
contrast bytes for the pixels from that point on). `0x0FFFFFFF` as an `LN_CTLI`
ends the list; a `PXCD` holding only it cancels an earlier `CHG_COLCON2`. Each line
starts with the `SET_COLOR2`/`SET_CONTR2` values. Not allowed while Highlight
Information is in use.

No other opcode appears on disc; `00h` and `87h` do not occur in the sampled SPUs.
Typical first DCSQ: `01 83 84 85 86 FF`, and the last DCSQ: `02 FF` at the stop
time. The high bit separates these HD commands from the DVD ones they replace
(`03h` SET_COLOR, `04h` SET_CONTR, `05h` SET_DAREA, `06h` SET_DSPXA with
16-colour, 4-bit fields and 2-byte addresses).
`[23]` **SPEC**; `[11, 12]` **VERIFIED** (`e25`)

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
