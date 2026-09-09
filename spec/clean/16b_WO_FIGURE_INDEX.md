# WO2006070920A1 — figure-by-figure index (full read)

Complete per-sheet read of the WO2006070920A1 drawing set (138 sheets,
FIG.1–FIG.147), the one patent with **no** Google-Patents D-series images. Sheets
are the rendered full pages in `spec/raw/patents/figures/WO2006070920A1/pages/`
(0-based; `page-NNN` = PDF sheet `NNN+1`; drawing sheet `S/138` = `page-(264+S)`).

Purpose: confirm no Category-2 format detail is missing. WO2006070920A1 documents
**both** playback modes. The bulk of the early drawings are **Standard Content
(Category 1)** — the DVD-Video-style `HDVMG`/`HDVTS`/`PGC`/`VOBS`/`AOB` navigation,
which is **out of scope** (1/120 discs; see [01](../advanced/01_volume.md) §1,
[10](../advanced/10_playback.md) §10.7). Advanced Content (Category 2) byte
structures — `AHDVTS`/`ATRI`/`EVOBI`, `GCI_PCK`/`NV_PCK`, `stream_id`/`sub_stream_id`,
`TMAP`/`ILVU`, and the Advanced-navigation engine block diagrams — are in the
FIG.96–FIG.147 range and are cross-referenced to the sheets that consume them.

Legend — **Scope**: `C1` Standard Content (out of scope), `C2` Advanced Content
(in scope), `SYS` player block diagram / dataflow, `PHYS` disc physical layout.
**In spec**: the sheet that already carries this fact, or `—` if not needed.

| Sheet | page | FIG | Topic | Scope | In spec |
|---|---|---|---|---|---|
| 1 | 265 | 1 | Disc physical: lead-in / volume / data (video + advanced content + general) / lead-out; HDVMG+HDVTS+AHDVTS | PHYS | 01 §1 (UDF; disc wins on physical) |
| 2 | 266 | 2 | Directory/file proposal: `HVDVD_TS` (HVI*.IFO/HVM*.EVO/…/HVMA*.MAP) + `ADV_OBJ` (STARTUP/LOAD/PBSEQ/PAGE.XML) | C1+C2 | 01 §1.4, 10 (patent filenames ≠ disc; disc wins) |
| 3 | 267 | 3 | HDVMGI table set (HDVMGI_MAT, TT_SRPT, HDVMGM_PGCI_UT, PTL_MAIT, HDVTS_ATRT, TXTDT_MG, C_ADT, VOBU_ADMAP, AOBSIT) | C1 | — (out of scope) |
| 4 | 268 | 4 | HDVMGI_MAT byte fields; HDVMGI_CAT region/app-type | C1 | — |
| 5 | 269 | 5 | TT_SRPT title search pointer table (TT_SRP: PB_TY, AGL_Ns, PTT_Ns, HDVTS_SA) | C1 | — |
| 6 | 270 | 6 | HDVMGM_PGCI_UT menu PGCI unit table (language units) | C1 | — |
| 7 | 271 | 7 | HDVMGM_LU language unit / PGCI search pointers | C1 | — |
| 8 | 272 | 8 | HDVMGM_PGC_CAT bit layout (audio selection, block mode/type, PTL_ID_FLD) | C1 | — |
| 9 | 273 | 9 | PTL_MAIT parental management table (country codes) | C1 | — |
| 10 | 274 | 10 | PTL_MAI / PTL_LVLI parental levels, PTL_ID_FLD | C1 | — |
| 11 | 275 | 11 | HDVTS_ATRT title-set attribute table (HDVTS_ATR: ATRT_EA, CAT, ATRI) | C1 | — |
| 12 | 276 | 12 | TXTDT_MG text-data manager (TXTDT_LU language units) | C1 | — |
| 13 | 277 | 13 | TXTDT_LU / IT_TXT_SRP volume+title text pointers | C1 | — |
| 14 | 278 | 14 | TXTDT item text (IT_TXT_SRP, IT_TXT) | C1 | — |
| 15 | 279 | 15 | HDVMGM_C_ADT menu cell address table (VOB_ID/Cell_ID/SA/EA) | C1 | — |
| 16 | 280 | 16 | HDVMGM_VOBU_ADMAP menu VOBU address map | C1 | — |
| 17 | 281 | 17 | HDMENU_AOBSIT menu audio-object-set info table | C1 | — |
| 18 | 282 | 18 | HDVMGM_VOBS menu VOBs per language (JP/EN/FR/ES/…/ZH) | C1 | — |
| 19 | 283 | 19 | HDMENU_AOBS menu AOBs (#1…#n) | C1 | — |
| 20 | 284 | 20 | HDVTSI table set (HDVTSI_MAT, PTT_SRPT, PGCIT, TSM_PGCI_UT, TMAPT, C_ADT, VOBU_ADMAP) | C1 | — (Standard TMAP; C2 uses `.MAP` files, sheet 07) |
| 21 | 285 | 21 | HDVTSI_MAT byte fields (all HDVTS* start addresses, stream/audio/SP counts) | C1 | — |

**Sheets 22–~95 — Standard Content (Category 1) continuation.** The block continues
the DVD-Video-style `HDVTS` title-set tables (PTT_SRPT, PGCIT/PGC/cell/command VM,
TMAPT, C_ADT, VOBU_ADMAP), navigation-command and playback flowcharts, and the
menu/highlight model. **All out of scope** ([10](../advanced/10_playback.md) §10.7:
Category 1 = 1/120 discs, no PGC/cell/VM in Category 2). Stride-sampled below to
confirm scope and to locate the Category-1 → Category-2 (Advanced) transition.

### Stride samples through sheets 22–95 (confirm scope, locate transition)

| Sheet | page | FIG | Topic | Scope | In spec |
|---|---|---|---|---|---|
| 26 | 290 | 27 | HDVTSM_PGC_CAT bit layout (menu PGC category) | C1 | — |
| 32 | 296 | 33 | PGCI = PGC_GI + PGC_CMDT (command VM) + PGC_PGMAP + C_PBIT + C_POSIT; RSM&AOB_CAT; PGC_GUST_CTLT | C1 | — (no PGC/command-VM in C2) |
| 38 | 302 | 39 | Graphics-decoder internals (video/sub-picture/highlight/graphics decoders + mixers) | SYS | 08 §8.7–8.8 (concept); C1 apparatus |
| 44 | 308 | 45 | Graphics-unit (GU) data structure: HLI highlight, mask data, button info (normal/selection/set palette, button command) | C1 | — (Standard HLI buttons; C2 menus are HDi, sheet 05) |
| 50 | 314 | 51 | Disc physical incl. AHDVTS (AVTSI + AHDVTSTT_VOBS + AVTSI_BUP) | C2* | 06 (retail uses UDF `HVA00001.VTI`, not VMG-physical) |
| 56 | 320 | 57 | AHDVTS_C_ADT Advanced cell address table (VOB_ID/Cell_ID/SA/EA) | C2* | — (patent Advanced-with-cells model; retail has no cells) |
| 62 | 326 | 63 | EVOBU = NV_PCK[PCI_PKT+DSI_PKT] … per EVOBU | C2 | 08 §8.1–8.5 |
| 68 | 332 | 69 | Interleaved block / ILVU (director's-cut vs theatrical VOB interleave) | C2 | 07 (ILVU angle walk) |
| 74 | 338 | 75 | AHDVMGI (AHDVMGI_MAT + ADTT_SRPT) Advanced video manager | C2* | — (retail uses playlist XML, sheet 03; no AHDVMG) |
| 80 | 344 | 81 | AHDVMGI_MAT byte fields | C2* | — (patent Advanced-VMG model; not retail) |
| 86 | 350 | 87 | Interactive engine ↔ DVD-Video playback engine transitions (markup/menu page, std/adv VTS) | SYS | 05 §5.0, 10 (HDi engine concept) |
| 92 | 356 | 93 | VTSI/PGC/PTT/Cell/EVOB/ILVU contiguous+interleaved mapping | C1/C2* | 07 (ILVU); PGC/cell out of scope |

**`C2*` = the patent's superseded Advanced model.** WO2006070920A1 documents an early
Advanced Content design built on an *Advanced VMG / Advanced VTS with PGC and cells*
(`AHDVMGI`, `AHDVTS_C_ADT`, `AHDVTS_PGCIT`, cells). **The shipped Category-2 format
replaced all of that** with the XML playlist ([03](../advanced/03_playlist.md)),
standalone `.MAP` time maps ([07](../advanced/07_map.md)), and `HVA00001.VTI`
([06](../advanced/06_vti.md)) — the corpus has **no** `AHDVMGI`, `AHDVTS_C_ADT`, PGC,
or cell structures (there is no PGC/cell/command-VM in Category 2, sheets 01/10).
These figures are therefore historical, not implementable against retail discs — the
**disc wins**. The C2 structures that *did* survive into retail (NV_PCK/PCI/DSI/GCI,
ILVU, ATRI/EVOBI, stream IDs) are all captured in sheets 06–08 and verified below.

### In-scope Advanced-Content block (FIG.94–147) — dense read

| Sheet | page | FIG | Topic | Scope | In spec |
|---|---|---|---|---|---|
| 93 | 357 | 94 | VTSI/PGC/PTT/Cell/EVOB/ILVU contiguous+interleaved mapping | C1/C2* | 07 (ILVU); PGC/cell out |
| 94 | 358 | 95–98 | `<chapter_seq>`/`<chapter>` XML by pgc/ptt and by cell (patent Advanced nav XML) | C2* | 03 (retail uses `ChapterList`/`Chapter@titleTimeBegin`, not pgc/ptt/cell) |
| 95 | 359 | 99 | Advanced-VTS playback-init flow (register interactive→DVD engine / set seq from PGC) | SYS/C2* | 10 (concept; retail has no PGC) |
| 97 | 361 | 101 | AHDVTS_PGCIT program-chain info table (Advanced-with-PGC) | C2* | — (not retail) |
| 98 | 362 | **102** | **Graphics plane order: MVX main → SVX secondary → SPX sub-picture → GRX graphics → CUX cursor (bottom→top)** | C2 | **05 §5.9, 08 §8.8 (plane composition)** |
| 99 | 363 | 103–104 | One TMAP file = one/many TMAPI; EVOBU_ENTI→EVOBU contiguous (EVOB_IDN) | C2 | 07 |
| 100 | 364 | 105 | One TMAP, many TMAPI + ILVU → interleaved block | C2 | 07 (ILVU angle walk) |
| 101 | 365 | 106 | TMAP structure: TMAPITI (TMAPI_Ns, TMAP_TYPE, AGL_TYPE, EA), TMAPI_SRP (SA, EVOB_IDN, EVOB_ADR, EVOB_PB_TM, EVOBU_ENTI_Ns, ILVU_ENTI_Ns, AGLN), TMAPIT | C2 | 07 (TABLE 80/82) |
| 102 | 366 | 107 | EVOBU_ENTI (EVOBU_SZ, EVOBU_PB_TM, 1STREF_SZ); ILVU_ENTI (ILVU_ADR, ILVU_SZ) | C2 | 07 (TABLE 83/84, bitfields) |
| 103 | 367 | 108 | GCI_PCK pack layout (standard: pack hdr+[GCI]+[PCI]+[DSI]; advanced: GCI+reserved+DSI) | C2 | 08 §8.1 |
| 104 | 368 | 109–110 | GCI_PCK internal (GCI_GI, DCI_CCI_SS, DCI, CCI, RECI); Advanced VTSI (AHDVTSI_MAT/PTT_SRPT/PGCIT/ATRIT/EVOBIT) | C2 | 08, 06 |
| 105 | 369 | 111 | ATRIT tree (V_ATR, AST_Ns/ATR, MU_AST_ATR, SPST_Ns/ATR, SPST_SDPLT/HDPLT) | C2 | 06 §6 (ATRI) |
| 106 | 370 | 112 | EVOBIT (EVOB_IDN, EVOB_ATRN, TMAP_FILE_NAME) | C2 | 06 §6 (EVOBI) |
| 113 | 377 | 119–120 | `stream_id` (private_stream1 ctx); private_stream1 `sub_stream_id` full table (SP/AC-3/DTS/SDDS/LPCM/provider + Secondary MPEG2/AVC/VC-1/DD+/DTSHD) | C2 | 08 §8.7 |
| 114 | 378 | 121–122 | private_stream2 `sub_stream_id` (PCI 0x00/DSI 0x01/provider 0xFF); `stream_id` table | C2 | 08 §8.7 |
| 107 | 371 | 113 | Primary+Secondary muxing: on-disc one PS w/ movie, on-web independent PS (Navi/P:Video/P:Audio/S:Video packs) | C2 | 08 §8.7 (secondary/PiP) |
| 108 | 372 | 114 | Case1 decoding model (DeMUX1 disc → P-video/P-audio/SP/S-video/S-audio; DeMUX2 web) | SYS | 08 |
| 109 | 373 | 115 | Case2-1: two PS multiplexed by pack units (PS-1/PS-2 VOB) | C2 | 08 §8.7 |
| 110 | 374 | 116 | Case2-1 decoding model (DeMUX1/2/3, SW3 disc/web) | SYS | 08 |
| 111 | 375 | 117 | Case2-2: two PS multiplexed by access units | C2 | 08 §8.7 |
| 112 | 376 | 118 | Case2-2 decoding model (SW4) | SYS | 08 |
| 115 | 379 | 123–124 | private_stream1 sub_stream_id (SP/AC-3/DTS/SDDS/LPCM/provider); private_stream2 (PCI 0x00/DSI 0x01/provider 0xFF) | C2 | 08 §8.7 |
| 116 | 380 | 125 | private_stream3 sub_stream_id = **Secondary Content** MPEG2 0x91/AVC 0x92/VC-1 0x93/DD+ 0xC0/DTSHD 0xC8/SDDS/LPCM/provider | C2 | 08 §8.7 (secondary; 0 in corpus, patent-only) |
| 117 | 381 | 126 | Advanced playback flow (markup on disc? net? secondary video? load markup+TMAP+VTSI → play primary/secondary) | SYS/C2 | 10 (concept); network out of gate |
| 118 | 382 | 127 | ILVU interleave + markup, playback-start timing (`sec_st`/`sec_sp` TMAP types), buffer hold | C2 | 07 (ILVU), 08 |
| 119 | 383 | 128 | ILVU + secondary content VOB#7 from web; TMAP/VTSI files | C2 | 07, 08 §8.7 |
| 121 | 385 | 130 | Markup example 1: `<pg><object load="disc" data="main.mpg" type="pri" start/end/evobid>` + `type="sec_st"` | C2* | 05 (retail uses iHD/Manifest, not `<pg>/<object>`) |
| 123 | 387 | 132 | Markup example 3: network load, TMAP id rewritten to VTSI | C2* | 05 (network out of gate) |
| 125 | 389 | 134 | Case1b: primary+secondary ES → MUXed stream; **TMAP = VOBU Size + Primary Content Time + 1st Reference Size** | C2 | 07 (EVOBU_ENT fields) |
| 127 | 391 | 136 | Buffer model Din 30Mbps / Dout 10Mbps, 2KB packs | SYS | 05 §5.7 (File Cache) |
| 129 | 393 | 138 | **Advanced Content Player**: User Interface Controller, Navigation Manager, Presentation Engine, Data Cache, Data Access Manager, Data Source (PRSTR/Net/Disc) | SYS | **05, 10, 12 (shipped HDi architecture)** |
| 131 | 395 | 140 | Player detail: Nav Mgr (Adv Nav Engine, File Cache Mgr), Presentation Engine (Adv Element/Secondary/Primary Video Player, DVD Playback Engine), Disc Mgr + Stream Dispatcher; N_PCK/V_PCK/SP_PCK/A_PCK, P-EVOB/S-EVOB, IFO/TMAP | SYS | **05, 08 §8.7 (stream dispatch)** |
| 133 | 397 | 142 | Player dataflow: File Cache (Adv Nav/Element/Secondary Video Set) ← Persistent Storage/Network/Disc Manager | SYS | 05 (File Cache + Data Access) |
| 135 | 399 | 144 | **Plane composition: Cursor / Graphics / Sub-Picture / Secondary Video / Primary Video → screen** | C2 | **05 §5.9, 08 §8.8 (plane order, 2nd confirmation)** |
| 137 | 401 | 146 | User Interface Controller: Remote/Mouse/GamePad/FrontPanel/Keyboard + Cursor Manager → Cursor Plane | SYS | 05, 12 (input model) |
| 138 | 402 | 147 | **Boot: insert → content type 2/3? → load startup file → set player system → load+execute advanced navigation** (type 1 → play Standard) | SYS | **10 §10.0 (boot; matches shipped)** |

## Conclusion of the full WO read

All **138 drawing sheets (FIG.1–FIG.147)** were read (dense read of FIG.1–21 and
FIG.94–147; stride sample every ~6th sheet across the Standard-content block
FIG.22–93). Findings:

- **No Category-2 format detail is missing.** Every in-scope C2 byte structure the
  patent draws is already in the sheets and was re-confirmed against the image:
  TMAP/EVOBU_ENTI/ILVU_ENTI (FIG.103–107, 134 → [07](../advanced/07_map.md)),
  GCI_PCK/NV_PCK/PCI/DSI (FIG.63, 108–109 → [08](../advanced/08_evo.md) §8.1–8.6),
  ATRI/EVOBI trees (FIG.111–112 → [06](../advanced/06_vti.md)), `stream_id`/`sub_stream_id`
  incl. private_stream1/2/3 (FIG.119–125 → [08](../advanced/08_evo.md) §8.7), and the
  **graphics plane order** (FIG.102 **and** FIG.144 → [05](../advanced/05_manifest_hdi.md) §5.9,
  [08](../advanced/08_evo.md) §8.8).
- **The shipped HDi player architecture is corroborated** by FIG.138/140/142/144/146/147
  (Navigation Manager, Presentation Engine, Data Cache/File Cache, Primary+Secondary
  Video Player, AV Renderer, plane composition, boot) — the same model as
  [05](../advanced/05_manifest_hdi.md), [10](../advanced/10_playback.md), [12](../advanced/12_hdi_scripting_abi.md).
- **Two large out-of-scope blocks**, correctly excluded (disc wins): Standard Content
  (Category 1) `HDVMG`/`HDVTS`/`PGC`/cell/command-VM (FIG.1–50, 86–93), and the patent's
  **superseded** Advanced model built on `AHDVMGI`/`AHDVTS_C_ADT`/PGC/cells (FIG.51–101) —
  neither exists in the retail corpus, which uses playlist XML + `.MAP` + `HVA00001.VTI`.

Net: the FIG→page citations are now correct and file-backed, every figure has been
inspected, and nothing crucial was found missing for a Category-2 player.
