# Adversarial review — what we claim, and why you should not believe it yet


> **Provenance.** Audits every other file. Sources are named inline per claim.
> See `EVIDENCE_STANDARD.md` for the tag format.

Every claim in `spec/clean/` interrogated. For each: **what is the evidence**, **how
many specimens**, **what would falsify it**, **what we never checked**.

Status codes: **SOLID** (patent + multi-disc agreement) · **THIN** (one specimen or
one source) · **INFERRED** (no direct evidence) · **OPEN** (unknown).

---

## 1. UDF / filesystem layer

| Claim | Status | Attack |
|---|---|---|
| HD DVD uses UDF 2.50 metadata partition | SOLID | 120 listings; LVD domain `*OSTA UDF Compliant` + revision `0x0250` on MYSTERY_MEN, DOWNFALL, RESERVOIR_DOGS |
| Metadata files are single-extent | **THIN→corpus-SOLID** | 120/120 walks succeeded with first-extent-only mapping. Fragmented still unseen. |
| Sector size is 2048 | **VERIFIED** | 120/120 listings; LVD `LogicalBlockSize` = 2048 on 3/3 parsed volumes |
| UDF revision is exactly 2.50 | **VERIFIED** (3 LVD) | Domain identifier suffix `0x0250`. Not 2.01 or 2.60 on those discs. |
| `part_start` is always 288 | **VERIFIED in-corpus** | 120/120. Spec vs Sonic artifact still open. |

**Never checked:** ISO9660 bridge presence; whether any disc has multiple/relocated
AVDPs; behaviour on the 8 cm and hybrid (combo) discs; whether HD DVD-R/RW media
differ; what happens with a Category 3 disc's dual zones at the UDF level.

## 2. Namespace and file naming

| Claim | Status | Attack |
|---|---|---|
| `HV%03dI01.IFO` naming | THIN | One Standard Content disc. `I02` never appears on that disc (HV000–HV011 all `I01`). |
| Max 511 VTS | **INFERRED** | Patent only. Highest observed is **11**. Never seen >99, so the u16 widening is *explained* but not *demonstrated*. |
| Title parts go to 99 | THIN | Highest observed `T19`. |
| Menu EVOB is `M%02d` | **OPEN** | VMG is `HV000M02.EVO` (no `M01`). VTS menus on the same disc **are** `M01`. |

**Never seen:** `HVSO@@@@.MAP` — 0 hits in 120 listings.
`DISCID.DAT` — **RESOLVED**, `HDDVD-V_CONF` 128-byte Config File; see `03` §8.
`ANY!_BAK` vs `ANY!` — **RESOLVED**: 104/104 AACS discs have BAK. 99 omit only
`MKBRECORDABLE.AACS` (§3.11). 5 copy `MKBRECORDABLE` into BAK (the 12,628-byte
MKBROM titles). `AAC!/` is an alternate AACS directory on 8 discs.

## 3. Standard Content — **everything here rests on ONE disc**

`RESERVOIR_DOGS` is the sole specimen in 120. Every byte-level claim below could be a
Sonic Scenarist SCA 4.2 artifact rather than a format property.

| Claim | Status | Attack |
|---|---|---|
| `VMGI_MAT` layout | SOLID | Patent RBP + disc agree. *(Note: earlier "identical to DVD" claim was WRONG — corrected.)* |
| `VTSI_MAT` layout | SOLID | Patent RBP + disc agree field-for-field |
| `TT_SRPT` 16-byte entries | **THIN** | Arithmetic-derived, one disc. No patent table exists for it. |
| `VTS_PGCIT` 12-byte SRP | **THIN** | Same. |
| PGC offsets at 0xA8 | **THIN** | Same. |
| **Two palettes** at 0xB0/0xF0 | **OPEN** | Byte-identical on the one specimen. Purpose unknown. If they never differ, is the second one real or is my field boundary wrong? |
| `cell_playback` 28 bytes | THIN | Chain-validated across 204 cells — strong *internally*, but one disc. |
| 4 trailing `cell_playback` bytes | **OPEN** | Always zero. Could be reserved, or could mean my stride is 24+4 padding rather than a 28-byte struct. |
| 2 extra bits in seconds byte | **OPEN** | Not frame rate. Not cell category. **Unexplained.** |
| Commands = DVD rotated 16 bits | THIN | Type histogram is compelling, but 57 commands from one disc. |
| Set-command operand layout | **WRONG** | Decodes `g0` for all 36 Set commands. Known incorrect. |

**Never decoded:** `VMGM_PGCI_UT` and `VTSM_PGCI_UT` bodies (menu PGCs — required for
menus), `VTS_ATRT` entry bodies, `PTL_MAIT` (never observed), `TXTDT_MGI` (patent has
`TXTDT_MG_SA` at RBP 212 but never describes the body).

**Unasked question:** does HD DVD add commands DVD lacks? We only saw types 1/2/3.
Types 0/4/5/6 never appeared. Absence of evidence only.

## 4. Advanced Content

| Claim | Status | Attack |
|---|---|---|
| XPL element/attribute model | SOLID | 247 files, 0 parse failures, **official `Playlist.xsd` v1.0/v1.1** in `spec/raw/adv_obj/` |
| `.MAP` = TMAP_GI + TMAPI_SRP + TMAPI | SOLID | Patent tables 80/82/83/84 + disc; **SRP at byte 384** |
| `EVOBU_ENT` bit widths | **SOLID** | Patent TABLE 83 figure (`C00040.png`): `1STREF_SZ` 11 + `EVOBU_PB_TM` 8 + `EVOBU_SZ` 13. Corpus 108 entries have `SZ > 2047`. DOWNFALL pack-count exact. `e08`. |
| `TMAPI_SRP` at offset 128 | **WRONG** (resolved) | Padding. True location **384**. `TMAPI_SA` is a byte offset, not LBN. |
| TMAP_GI is 128 bytes | **RESOLVED** | Missing 14 OCR bytes = VTI filename at RBP 114-125 + 2 NULs |
| `.ACA` container format | **THIN** | **One 2008-byte sample, 2 entries.** 409 listed, 0 saved by default. |
| `ADVANCED-VTS` VTSI_MAT (TABLE 77) | **RESOLVED** | 119/119. |
| `VTS_EVOB_ATRT` / `VTS_EVOBIT` | **RESOLVED** (headers+stride+`V_ATR`) | 1024-byte ATRI, 320-byte EVOBI; EVO filename at EVOBI+2; `V_ATR` at ATRI+2 (`e08`). Audio/SP/palettes **OPEN**. |

**Examined, not a full runtime spec:** 1408 markup/script/font samples (`1408`); MATRIX `selector.aca`. HDi execution, `ScheduledControlList`/`Event` runtime, and the rest of the ACA archive stay **OPEN**.

**Still unread as field tables:** ATRI beyond `V_ATR`; EVOBI 274–285.

## 5. EVO container — RESOLVED (was: "we have never opened one")

| Claim | Status |
|---|---|
| EVO is MPEG-2 program stream, 2048-byte packs | **VERIFIED** — `00 00 01 BA` at every 2048 boundary, MPEG-2 marker bits, 2 discs |
| Any MPEG-2 PS demuxer can take EVO packs | **well-founded** — standard 2048-byte PS |
| Pack taxonomy VM/AM/VS/AS/SP/NV/ADV_PCK | still INFERRED (FIG.25 only) |

**Still never dumped:** ADV_PCK (`0x80`); full stream-ID census for VC-1/H.264/audio/SP.
See `08_NV_PCK_PCI_DSI.md`.

## 6. NV_PCK (PCI/DSI) — RESOLVED (was: "nothing at all")

It was never a documentation problem — the structure is in the stream and nobody had
looked. PCI and DSI follow DVD-Video's `pci_gi_t`/`dsi_gi_t`. Advanced EVO carries
the same three packets. MAP `EVOBU_SZ` = `DSI.vobu_ea+1` on DOWNFALL (5/5) and
MYSTERY_MEN VOBU0. Packet `0x04` is GCI (patent Tables 50–51). AACS CPI is 16 bytes
*inside* GCI_PKT; the **byte offset** of those 16 bytes is **OPEN** (`GCI_GI[0]` is
not `KEY_VF`). Highlight/button regions (`hli_t`) and the DSI tail (`vobu_sri`,
`synci`) are **still OPEN**. See `08_NV_PCK_PCI_DSI.md`.

## 7. AACS — format-specific book now in hand

Traceable answers: `09_AACS.md` addendum. Sources: AACS LA Common + Pre-recorded
Video (live), HD DVD Pre-recorded **Final 0.953** (Wayback; removed from aacsla.com),
BD Pre-recorded 0.921 (contrast), libaacs `aacs.c`, Scenarist AC 4.5, N=120 listings.

| Claim | Status | Attack |
|---|---|---|
| Navigation / IFO / MAP / XPL unencrypted | SOLID | 3+ discs; book: NV_PCK not encryptable |
| Pack *headers* in the clear | SOLID | first 32 B of FEATURE_1.EVO; book: 128-byte Unencrypted Portion |
| “AACS = encrypt ES payload, libaacs will decrypt it” | **WRONG** | `aacs_decrypt_unit` is BD 6144-byte TS. HD DVD is 2048-byte PS packs, 128/1920 split, Content Key `AES-G(Kt, Dtk\|\|CPI)` |
| libaacs has no HD DVD support | SOLID | source; Toysoft README historically said patches welcome |
| AES-G / MKB / `Kt=AES-128D(Kvu,Kte)` reusable | SOLID | Common + HD DVD books; **unit decrypt not reusable** |
| Volume ID in the ISO | **WRONG** | BCA + Lead-in; MMC Format `80h`. `DISCID.DAT@12` is not Volume ID |
| VTKF is unit-indexed like `Unit_Key_RO.inf` | **WRONG** | playlist name @16; 64×36-byte slots from byte 128; `TITLE_KEY_PTR` 1…64 |
| `ANY!_BAK` dropping `MKBRECORDABLE` is a bug | **WRONG** | Final 0.953 §3.11 specifies exactly that |
| Directory is `AACS/` | **WRONG on disc** | book reserves `AACS`; corpus is `ANY!` (96) / `AAC!` (8) |
| 6144-byte “PS aligned unit” (libfreemkv) | **WRONG** | book: pack basis; libfreemkv itself marked that check unvalidated |

**Still OPEN:** CHT1/CHT2 *body* stride; VTUF usage-rule body; why `ANY!`/`AAC!`
instead of `AACS`; extra VTKF without VPLST on 3 titles; CPI **byte offset** inside
GCI_PKT (identity of packet `0x04` is closed).

### 7.1 The questions (asked, then answered)

Falsifiers in parentheses.

1. **Does the format-specific book override Common/Pre-recorded Video?** Yes.
   Common §1.1. (Falsify: quote a later AACS LA erratum reversing precedence.)
2. **Is HD DVD's encrypted unit 6144 bytes?** No — 2048-byte pack, 1920 encrypted.
   Final 0.953 Table 4-7. (Falsify: a disc whose encrypted media is 6144-aligned
   with only 16 bytes clear *including* NV_PCK.)
3. **Does `aacs_decrypt_unit` apply?** No. libaacs `_verify_ts` / 6144 Block Key.
4. **Are the first 16 bytes the AACS seed, as on BD?** No. 128-byte clear prefix;
   `Dtk` at 84–87. NV_PCK fully clear, so MYSTERY_MEN's system header at byte 14
   is expected, not a mystery.
5. **Is the Title Key the CBC key?** Not on HD DVD. `Kc = AES-G(Kt, Dtk \|\| CPI_lsb_96)`.
   Format-independent §3.4 is overridden.
6. **Where is Volume ID?** BCA+Lead-in, not UDF, not `DISCID.DAT`. ISO corpus cannot
   compute `Kvu`.
7. **VTKF stride 32 or 36? How many keys?** 36-byte entries, 64 slots, file 2480
   in Table 3-8 (0.953) / 3-5 (0.912). Almost every listed VTKF is 2480.
   `PANS_LABYRINTH` VTKF001/003 are 2516 (65 slots). Size the table from the
   file’s `HD_VTKF_SIZE`. Scenarist cap = 64.
8. **How does a pack choose a title key?** CPI `TITLE_KEY_PTR` (1-based) + `KEY_VF`.
   Not BD CPS unit in `Unit_Key_RO.inf`.
9. **Is `MKBROM.AACS` a different MKB format than libaacs parses?** Same Common
   records; different *filename*. Residual padding is optional. Listed sizes here:
   1,000,000 (88), 1,048,576 (10), 12,628 (5), 20,480 (`PANS_LABYRINTH`).
   Lead-in P-MKB is the 1 MiB object.
10. **Why is `MKBRECORDABLE.AACS` on ROM?** Read/Write MKB for recorders. BAK omits
    it on 99 discs (§3.11); 5 copy it into BAK anyway.
11. **`ANY!` vs `AAC!` vs `AACS`?** Filenames match the book; directory name does not.
12. **Are CHT/CERT required to *decrypt* packs?** Required for a compliant player's
    integrity boot path. Not inputs to `Kc`. Cert is 120 bytes (Table 3-17).
13. **Bus encryption same as BD?** No. 128/1920, `Dbe` at bytes 14–17, EVOB sectors
    only. Irrelevant to HTTP ISOs.
14. **KCD / SKB / PMSN on these discs?** KCD/PMSN are not UDF files. SKB/SKF: 0/120.
15. **Segment keys? ATKF?** Authoring CMF lists them; 0 `SKF`/`ATKF`/`APLST` in corpus.
16. **`PES_scrambling_control` vs AACS?** Same pack: 01b means the Encrypted Portion
    is present. Not CSS, not a second algorithm.
17. **Unencrypted discs?** 16/120 have no AACS dir. `RESERVOIR_DOGS` plus 15 Advanced.
18. **DKF = disc/title key?** No. Persistent-storage directory name. 64-byte Table 6-2.
19. **Can libaacs MKB + AES-G be reused without BD paths?** Yes, with new I/O and
    **without** `aacs_decrypt_unit`. VLC's 6144 hook cannot be satisfied by EVO.
20. **Is `DISCID.DAT` Volume ID?** No. Config File; Disc ID @12 is network, often `FF`.
21. **libfreemkv Table 3-8 VTKF** — table citation is correct **for Final 0.953**.
    Its 6144 PS-unit decrypt path is not.
22. **CPI vs TMAP?** Unrelated. CPI lives in GCI in NV_PCK; TMAP is the `.MAP` file.

---

## The questions that would most change the plan

1. ~~Is the EVO really a demuxable MPEG-2 PS?~~ **ANSWERED: yes.**
2. ~~What is in `HVA00001.VTI`?~~ **ANSWERED**, 119/119 TABLE 77 + ATRT/EVOBIT strides.
3. ~~Does an official `Playlist.xsd` exist publicly?~~ **ANSWERED:** yes, local copies
   `spec/raw/adv_obj/v1.0/` and `v1.1/`. Retail discs are 1.0.
4. ~~Are patent Table 83's bit widths recoverable from the figure images?~~ **ANSWERED:**
   yes. `US20080298219A1-20081204-C00040.png` is 11+8+13. Earlier DOWNFALL-only 11-bit
   SZ reading was specimen-local. `e08`.
5. **Is there a second Standard Content disc anywhere?** Everything in section 3 is one-specimen.
6. ~~What do the AACS key files look like?~~ **Answered for VTKF/DKF/CERT
   structure** (Final 0.953 Tables 3-8, 6-2, 3-17 + disc sizes). CHT *bodies* OPEN.
   See `09_AACS.md`.
7. ~~Is `NV_PCK` documented in a patent we have not pulled?~~ TABLE 85 names GCI+DSI;
   ADV_PCK is substream `0x80`. Packet `0x04` **is** GCI (Tables 50–51). CPI offset
   inside that packet is still **OPEN**.
8. ~~Will libaacs decrypt HD DVD if we point it at `ANY!`?~~ **No.** Wrong unit,
   wrong seed, wrong key derivation, wrong verify. Reuse MKB/AES-G only.

---

## Round 2 — closed vs still OPEN

Asked against the previous edition of this file. Answers are in `03`, `06`, `08`,
`12`, `13`, `e08`.

| Previous attack | Result |
|---|---|
| LVD unread; UDF 2.50 inferred | **Closed.** 3 LVD: `LogicalBlockSize=2048`, revision `0x0250`. |
| TABLE 83 figure unread | **Closed.** Figure is 13-bit `EVOBU_SZ`. |
| ATRI payload entirely OPEN | **Partial.** `V_ATR` at bytes 2–5; rest OPEN. |
| XMF/JS never examined | **Partial.** 1408 samples + MATRIX selector saved; HDi runtime OPEN. |
| GCI `0x04` unknown | **Identity closed.** CPI at pack `0x3C` (spec/advanced/09). |
| Advanced EVO / MAP vs DSI untested | **Closed** on DOWNFALL + MYSTERY_MEN. |
| Firmware catalog as live oracle | Catalog URL is live **and** 503 on the same day. Blobs exist at `http://hd-dvd.org/files/firmware/` when origin is 200. **no RE**. OEM notes do not confirm FIG.50. |

What would still change a linear Advanced playback walk: a second Standard Content
disc, Volume ID from a drive, firmware vs FIG.50 (**uncloseable**), HDi execution,
ADV_PCK dump. ACA directory formula is closed on 4 files (spec/advanced/04).
