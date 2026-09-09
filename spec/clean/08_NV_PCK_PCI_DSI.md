# NV_PCK / PCI / DSI — the gap is closed

This structure was previously marked **OPEN** in `03_libdvdread_requirements.md` and
`07_ADVERSARIAL_REVIEW.md`: 87 mentions across 4.86 M chars of patent text, zero
layout, absent from 161 OCR'd figure sheets. It was the largest unknown in the project.

**It was never a documentation problem.** The structure is in the stream, and the
stream is readable without decryption. Nobody had looked.

---

## 1. The EVO container

`[SRC: DISC | RESERVOIR_DOGS /HVDVD_TS/HV001T01.EVO @0 | first 4 KB via HTTP range]`
`[SRC: DISC | MYSTERY_MEN /HVDVD_TS/FEATURE_1.EVO @0 | same]`
**Confidence: VERIFIED** (2 discs, one encrypted one not)

EVO is an **MPEG-2 program stream**. Pack start code `00 00 01 BA` occurs at every
2048-byte boundary; the two bits after it are `01`, the MPEG-2 marker.

```
00 00 01 ba 44 00 04 00 04 01 04 9d 43 f8 00 00 01 bb 00 15 82 4e a1 ...
^^^^^^^^^^^ pack header (14 bytes)          ^^^^^^^^^^^ system header (0xBB)
```

**Consequence:** any MPEG-2 program-stream demuxer that accepts 2048-byte packs can
demux EVO. Navigation and pack headers are in the clear. The AACS overlay is payload
only.

## 2. AACS encrypts payload, not the container

`[SRC: DISC | RESERVOIR_DOGS (no ANY! dir) vs MYSTERY_MEN (ANY! present) | first 32 B of each EVO]`
**Confidence: VERIFIED** (2 discs)

The first 32 bytes are byte-identical on both discs except for one field:
```
RESERVOIR_DOGS: 00 00 01 ba 44 00 04 00 04 01 04 9d 43 f8 00 00 01 bb 00 15 82 4e a1 18 ...
MYSTERY_MEN   : 00 00 01 ba 44 00 04 00 04 01 04 9d 43 f8 00 00 01 bb 00 15 82 4e a1 0c ...
                                                                                     ^^ rate bound
```
Pack headers and system headers are in the clear on an AACS-protected disc.
**Navigation and structure are fully parseable without keys on every disc.** AACS
covers elementary-stream payload inside packs.

## 3. NV_PCK layout

`[SRC: DISC | RESERVOIR_DOGS HV001T01.EVO first pack | PES scan]`
`[SRC: DISC | MYSTERY_MEN FEATURE_1.EVO; DOWNFALL EVOB002.EVO | first NV_PCK + DSI vs MAP]`
**Confidence: VERIFIED** (packet set on 3 discs), **SINGLE** (PCI/DSI GI offsets first proven on Standard, then GI + `vobu_ea` on Advanced)

The first pack of each EVOBU is the NV_PCK. It contains **three**
`private_stream_2` (`0x000001BF`) PES packets, distinguished by a substream ID byte:

| Substream | PES length | Identity |
|---|---|---|
| `0x00` | 977 | **PCI** — Presentation Control Information |
| `0x01` | 755 | **DSI** — Data Search Information |
| `0x04` | 257 | **GCI_PKT** — General Control Information |

DVD-Video uses the same `private_stream_2` mechanism and the same substream IDs
(`0x00` PCI, `0x01` DSI) but different lengths (980 / 1018).

**`0x04` is GCI.** Patent Table 50: `sub_stream_id = 0000 0100b`,
`PES_packet_length = 0101h` = 257. Table 51: 1 byte substream id + 256 bytes GCI
(`GCI_GI` 16 + `RECI` 189 + reserved 51). Observed PES length is 257 on Standard
**and** Advanced.

`[SRC: PATENT | WO2006098395A1 / US20080298219A1 Table 50–52]`
`[SRC: DISC | RESERVOIR_DOGS HV001T01.EVO; MYSTERY_MEN FEATURE_1.EVO; DOWNFALL EVOB002.EVO | first NV_PCK]`
**VERIFIED** (3 discs, both categories)

It is **not** ADV_PCK (`sub_stream_id = 0x80`). TABLE 85 names NV_PCK as GCI+DSI;
the disc still carries a PCI packet as well. Advanced PCI GI may be filled
(DOWNFALL VOBU0 `vobu_e_ptm - vobu_s_ptm` = 45045 ticks = 500.5 ms) or zeroed
(MYSTERY_MEN VOBU0). Patent “simplified” ≠ packet omitted.

AACS CPI is **16 bytes inside GCI_PKT** (Final 0.953 Table 4-1: KMI 4 + CHMI 4 +
URMI 2 + CCI_SS 2 + CCI 2 + reserved 2). The book defers the byte offset to the
video spec. The first 16 data bytes look like patent `GCI_GI` (`GCI_CAT=0x40` on
Advanced including unencrypted `STALINGRAD`; `0x00` on Standard
`RESERVOIR_DOGS`). Reading byte 0 as AACS `KEY_VF` yields `01b` (segment key)
with no SKF — `GCI_CAT` is not `KEY_VF`. The 51-byte reserved tail after RECI is
zeros on dumped Advanced clips. `CPI_lsb_96` still needs the video-spec offset.
`[SRC: SPEC | AACS HD DVD Pre-recorded Final 0.953 §4.2 Tables 4-1/4-2]`

## 4. PCI — DVD-Video's `pci_gi_t` layout holds

`[SRC: DISC | RESERVOIR_DOGS HV001T01.EVO VOBU 0 and 1]`
`[SRC: DERIVED | field names/offsets from libdvdread nav_types.h pci_gi_t]`
**Confidence: SINGLE disc, 40 VOBUs chain-validated** — needs multi-disc confirmation

Offsets are relative to the substream ID byte:

| Off | Size | Field | VOBU 0 | VOBU 1 |
|---|---|---|---|---|
| 0 | 1 | substream id | 0x00 | 0x00 |
| 1 | 4 | `nv_pck_lbn` | 0 | 28 |
| 5 | 2 | `vobu_cat` | 0 | 0 |
| 9 | 4 | `vobu_uop_ctl` | 0 | 0 |
| 13 | 4 | `vobu_s_ptm` | 93003 | 138048 |
| 17 | 4 | `vobu_e_ptm` | 138048 | 183093 |

**Cross-checks that make this convincing:**
- `vobu_e_ptm - vobu_s_ptm` = 45045 ticks. At DVD's 90 kHz clock that is **500.5 ms**
  — and 45045 / 3003 = exactly **15 frames at 29.97 fps**. A half-second VOBU.
- VOBU 1's `vobu_s_ptm` equals VOBU 0's `vobu_e_ptm` exactly (138048). Continuous.
- VOBU 1's `nv_pck_lbn` (28) equals VOBU 0's `vobu_ea + 1` (27+1).

## 5. DSI — DVD-Video's `dsi_gi_t` layout holds

`[SRC: DISC | RESERVOIR_DOGS HV001T01.EVO VOBU 0 and 1]`
`[SRC: DERIVED | field names/offsets from libdvdread nav_types.h dsi_gi_t]`
**Confidence: SINGLE disc, 40 VOBUs chain-validated**

| Off | Size | Field | VOBU 0 | VOBU 1 |
|---|---|---|---|---|
| 0 | 1 | substream id | 0x01 | 0x01 |
| 1 | 4 | `nv_pck_scr` | 0 | 0 |
| 5 | 4 | `nv_pck_lbn` | 0 | 28 |
| 9 | 4 | `vobu_ea` | 27 | 48 |
| 13 | 4 | `vobu_1stref_ea` | 16 | 16 |
| 17 | 4 | `vobu_2ndref_ea` | 17 | 19 |
| 21 | 4 | `vobu_3rdref_ea` | 20 | 22 |
| 25 | 2 | `vobu_vob_idn` | 1 | 1 |
| 28 | 1 | `vobu_c_idn` | 1 | 1 |

**`vobu_ea` is RELATIVE to the VOBU start, not absolute.** Walking with
`next = lbn + vobu_ea + 1` chains correctly; `next = vobu_ea + 1` breaks at VOBU 2.
`[SRC: DERIVED | empirical - the absolute reading failed on VOBU 2]`

### Chain validation over 40 VOBUs
`[SRC: DISC | RESERVOIR_DOGS HV001T01.EVO | walked 40 VOBUs following DSI.vobu_ea]`
**Both invariants held 40/40:**
- `DSI.nv_pck_lbn` == the walk position
- `PCI.vobu_s_ptm` == the previous VOBU's `vobu_e_ptm`

Mean VOBU 479 sectors = 959 KB per 0.5 s = **15.7 Mbps**, a plausible HD DVD rate.
VOBU sizes ramp from 28 sectors (leader) to ~380 (feature), consistent with content.

## 6. What this changes

- **Seeking** no longer depends only on TMAP. DSI gives VOBU-accurate addressing and
  `vobu_1stref_ea` gives the decodable-I-frame offset in-stream.
- **Menus and buttons** become reachable: PCI carries the highlight information
  (`hli_t` in DVD) beyond the general-information block decoded above. The HLI region
  was not examined here — **OPEN**.
- `03_libdvdread_requirements.md` §4 ("Still completely unknown: NV_PCK") is
  **superseded** by this file.

## 7. Still open

| Item | Status |
|---|---|
| PCI beyond `pci_gi_t` — `nsml_agli`, `hli` (buttons/highlights) | OPEN — not examined |
| DSI beyond `dsi_gi_t` — `sml_pbi`, `sml_agli`, `vobu_sri`, `synci` | OPEN — not examined |
| GCI after the 16-byte `GCI_GI` (`RECI` 189 + reserved 51) | named by Table 51; ISRC bytes seen on MYSTERY_MEN; not a field table |
| CPI byte offset inside GCI_PKT | **CLOSED** — pack offset `0x3C`. See spec/advanced/09_aacs.md §9.6 |
| ADV_PCK (`sub_stream_id=0x80`) | INFERRED from patents; no pack dumped |
| Advanced NV_PCK packet set and `DSI.vobu_ea` vs MAP | **VERIFIED** — 3 discs; DOWNFALL 5/5 VOBU chain |
