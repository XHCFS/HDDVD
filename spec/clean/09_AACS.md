# AACS on HD DVD

Provenance per `EVIDENCE_STANDARD.md`.

## What is and is not encrypted

Navigation files are not encrypted on any disc examined.
`[SRC: CORPUS | MYSTERY_MEN, BATMAN_BEGINS, PANS_LABYRINTH | HVA00001.VTI begins with ASCII "ADVANCED-VTS" while ANY! is present]`
**VERIFIED** (3 discs)

The EVO container is not encrypted either. Pack headers and system headers are in the
clear.
`[SRC: DISC | MYSTERY_MEN FEATURE_1.EVO @0 vs RESERVOIR_DOGS HV001T01.EVO @0 | first 32 bytes identical except the rate-bound field]`
**VERIFIED** (2 discs, one AACS one not)

Consequence: the navigation layer, TMAP, NV_PCK, PCI and DSI are all readable with no
keys. AACS covers elementary-stream payload inside packs only.

Unencrypted discs exist: **16/120** have neither `ANY!` nor `AAC!`.
`[SRC: CORPUS | N=120 listings]`

## File set

Primary tree is **`ANY!/`** (96 discs) or **`AAC!/`** (8 discs:
`ETERNAL_SUNSHINE`, `FAST_AND_FURIOUS`, `FIREWALL`, `KISS_KISS_BANG_BANG`,
`MATRIX_REVOLUTIONS`, `SPARTACUS`, `SUPERMAN_II_RDC`, `U2_RATTLE_AND_HUM`).
Mirrored in `ANY!_BAK/` or `AAC!_BAK/`. No disc uses a Blu-ray-style `AACS/` directory.
`[SRC: CORPUS | N=120 listings]` **VERIFIED**

| File | Size | Purpose |
|---|---|---|
| `MKBROM.AACS` | **not one size:** 1,000,000 (88), 1,048,576 (10), 12,628 (5), 20,480 (`PANS_LABYRINTH`) | Media Key Block (ROM) |
| `MKBRECORDABLE.AACS` | usually 1,000,000 | Media Key Block (recordable) |
| `DKF.AACS` | 64 | Disc Key File |
| `VTKF000.AACS` | usually 2,480; **2,516** on `PANS_LABYRINTH` VTKF001/003 | Title Key File |
| `VTUF000.AACS` | 144 | Title Usage File |
| `CONTENT_CERT.AACS` | 120 | Content certificate |
| `CONTENT_HASH_TABLE1/2.AACS` | vary by title | Content hash tables |
| `CONTENT_REVOCATION_LIST.AACS` | usually 1,000,000; **61,440** on `PANS_LABYRINTH` | Revocation list |
| `MNGCPY_MANIFEST.XML` | 304 | Managed Copy manifest |

## Key-file headers follow the HD DVD 12-byte ID convention

`[SRC: DISC | MYSTERY_MEN ANY!/DKF.AACS, VTUF000.AACS, VTKF000.AACS @0]`
**VERIFIED** (3 files, 1 disc)

Each begins with a 12-byte ASCII identifier followed by a u32 total length:

```
DKF.AACS      "DVD_HD_V_DKF" 00 00 00 40   (64 = file size)
VTUF000.AACS  "DVD_HD_V_TUF" 00 00 00 90   (144 = file size)
VTKF000.AACS  "DVD_HD_V_TKF" 00 00 09 b0   (2480 = file size)
```

This is the same grammar as `HVDVD-VMG100`, `STANDARD-VTS`, `ADVANCED-VTS` and
`HDDVD_TMAP00`: **12-byte ASCII ID, then a u32 size/end-address**. Useful as a
sanity check when identifying an unknown HD DVD file.
`[SRC: DERIVED | inputs: this file, 03_libdvdread_requirements.md §3, 06_TMAP_solved.md]`

### DKF.AACS (64 bytes)
Header, reserved/VERN, then 16 bytes at offset 48 — Encrypted Directory Key (`KDIRe`).
Not a title key. Full Table 6-2 in the addendum.
`[SRC: DISC | MYSTERY_MEN ANY!/DKF.AACS]`
`[SRC: SPEC | HD DVD Pre-recorded Final 0.953 Table 6-2]`

### VTKF000.AACS (2480 bytes typical) — Title Key File
Header at 0, then the ASCII string **`VPLST000.XPL`** at offset 0x10.
64 title-key slots of 36 bytes start at byte 128 (Table 3-8). Two files on
`PANS_LABYRINTH` are 2516 bytes (= 128 + 65×36 + 32 + 16): one extra slot versus
the book's 64. Disc wins. Full Table 3-8 in the addendum.
`[SRC: DISC | MYSTERY_MEN ANY!/VTKF000.AACS @0x10]`
`[SRC: CORPUS | PANS_LABYRINTH VTKF001/003 listed 2516; ISO line 1 of that listing]`
`[SRC: SPEC | HD DVD Pre-recorded Final 0.953 Table 3-8]`

### VTUF000.AACS (144 bytes) — Title Usage File
Header at 0, URS_NUM at 16, HASH_SIZE u32 at **17–20** (value 128), VERN at 21–22,
then ASCII **`VPLST000.XPL` at offset 23** (book Table 3-10). Do not parse the name
at 0x18 — that dump folded `'V'` into the preceding field. TUF MAC at 0x80 when
`URS_NUM=0`.
`[SRC: DISC | MYSTERY_MEN ANY!/VTUF000.AACS]`

**Structural difference from Blu-ray.** Both key files bind by **playlist filename**
(`VPLST000.XPL`), not by numbered CPS unit as Blu-ray's `Unit_Key_RO.inf` does.
A port cannot assume Blu-ray's unit-indexed model.
`[SRC: DERIVED | inputs: the two files above; libaacs src/libaacs/unit_key.c:256 "AACS/Unit_Key_RO"]`

### MNGCPY_MANIFEST.XML — Managed Copy
Verbatim `[SRC: DISC | MYSTERY_MEN ANY!/MNGCPY_MANIFEST.XML]`:
```xml
<mcManifest xmlns="http://www.aacsla.com/2006/02/hdmcManifest" ...>
	<Cid>gAAAAAAAAAAsWwAAAAAAAQ==</Cid>
	<serverList>
		<serverUri>http://smc.universalhomentertainment.com/</serverUri>
	</serverList>
</mcManifest>
```
Namespace is AACS-LA's, not DVD Forum's. `Cid` is a base64 content identifier.
Not needed for playback.

## libaacs cannot read these

`[SRC: SRCCODE | libaacs src/libaacs/aacs.c:315,886, unit_key.c:256 | hardcodes "MKB_RO.inf", "Unit_Key_RO.inf", "AACS/" paths]`
`[SRC: SRCCODE | grep -riE "hd.?dvd|HVDVD|ANY!|VTKF|MKBROM|DKF" libaacs/src -> no matches]`
**VERIFIED**

The AACS cryptography itself is a common standard. **MKB record parsing, AES-G, and
AES-128 ECB unwrap of title keys are reusable. `aacs_decrypt_unit` is not** — HD DVD
encrypts 2048-byte packs with a 128-byte clear prefix and a per-pack Content Key, not
BD's 6144-byte Aligned Unit. Full argument in the addendum below.

## Open

- Byte-for-byte decode of `CONTENT_HASH_TABLE1/2.AACS` **bodies** (hash-unit stride).
  Filenames and roles are in the HD DVD AACS book; CMF schema agrees on CHT1=EVOB /
  CHT2=Advanced Resources. `[SRC: SPEC | HD DVD Pre-recorded Final 0.953 §3.7]`
  `[SRC: SRCCODE | spec/raw/adv_obj/CmfDiscInformation.xsd CHT1/CHT2 documentation]`
- `VTUF###.AACS` usage-rule body beyond the 12-byte ID, size, and playlist name.
- Why the on-disc directory is `ANY!` / `AAC!` instead of the reserved name `AACS`.
- Extra `VTKF` files with no matching `VPLST` (`BALLS_OF_FURY`, `CHUCK_AND_LARRY`,
  `SHREK_THE_THIRD_EU`). Spec forbids two playlists sharing one TKF; it does not
  explain a TKF with no playlist.

## Addendum: BAK, numbering, `AAC!`

**`ANY!_BAK` is not a byte-for-byte copy of `ANY!`.** Every AACS disc (104/104) has a
backup tree. On **99** of them, BAK contains every primary file **except**
`MKBRECORDABLE.AACS` (book §3.11). On **5** (`RAMBO_*_FRA`, `OLIVER_TWIST_JPN`,
`TOTAL_RECALL_FRA`) BAK **also copies** `MKBRECORDABLE.AACS` — those are the
12,628-byte `MKBROM` titles. Disc drift: §3.11 is not followed there.
`[SRC: CORPUS | N=104 AACS listings | set difference; experiments/e05]`
**VERIFIED**

**`VTKF###.AACS` / `VTUF###.AACS` numbers track playlist numbers.** `VTUF` set equals
`VTKF` set on 119/119 discs that have either. `VTKF` numbers equal `VPLST` numbers on
101/119; the 18 mismatches are 16 unencrypted discs (no VTKF) plus three extras:
`BALLS_OF_FURY` VTKF `{0,1}` vs VPLST `{0}`; `CHUCK_AND_LARRY` VTKF 0–16 vs VPLST 0–15;
`SHREK_THE_THIRD_EU` VTKF 0–4 vs VPLST 0–3.
`[SRC: CORPUS | N=120 listings]`
**VERIFIED** as a naming rule, not as a key-layout decode.

SHREK also shows multiple 2480-byte `VTKF` files of identical listed size — one per
playlist index, not one concatenated table.

## Addendum: adversarial AACS / libaacs reference

This section is the traceable answer to the questions in `07_ADVERSARIAL_REVIEW.md` §7–8.
It documents **on-disc layout and how HD DVD AACS differs from libaacs**. It does not
specify a decryptor, device keys, or a processing sequence to run.

### Sources (what exists, what does not)

AACS LA still hosts the **format-independent** books and the **Blu-ray** books.
The **HD DVD and DVD** books are removed from the live index (“due to inactivity”)
and offered only via `Admin@AACSLA.com`.
`[SRC: SPEC | https://aacsla.com/aacs-specifications/ | HD DVD and DVD Books note]`
**VERIFIED** (page fetched 2026-09-08)

The withdrawn HD DVD Pre-recorded Book is still in the Internet Archive. Two
revisions used here:

| Rev | Wayback |
|---|---|
| 0.912 (166 pp.) | `web.archive.org/web/20061026081219id_/http://www.aacsla.com/specifications/AACS_Spec_HD_DVD_and_DVD_Prerecorded_0_912.pdf` |
| **Final 0.953** (154 pp.) | `web.archive.org/web/20130128114208id_/http://www.aacsla.com/specifications/AACS_Spec_HD_DVD_and_DVD_Prerecorded_Final_0.953.pdf` |

Table numbers **moved** between those revisions: Title Key File is Table 3-5 in 0.912
and **Table 3-8** in Final 0.953. Cite the revision with the table.

Still on the live AACS LA site (used below):

- Common Cryptographic Elements Final 0.953 —
  `https://aacsla.com/wp-content/uploads/2019/02/AACS_Spec_Common_Final_0953.pdf`
- Pre-recorded Video Book (format-independent) Final 0.953
- Blu-ray Disc Pre-recorded Book Rev 0.921 —
  `https://aacsla.com/wp-content/uploads/2019/02/AACS_Spec_BD_Prerecorded.921.pdf`

Precedence: *“When there is a discrepancy between a format-independent book and a
format-specific book then the format specific book takes precedence.”*
`[SRC: SPEC | Common 0.953 §1.1]`
**VERIFIED**

libaacs (VideoLAN; Toysoft github mirror read 2026-09-08): `ALIGNED_UNIT_LEN 6144`,
hardcoded `AACS/MKB_RO.inf` and `AACS/Unit_Key_RO.inf`, `aacs_decrypt_unit` verifies
MPEG-TS `0x47` every 192 bytes. No `VTKF`, `MKBROM`, `ANY!`, or HD DVD strings.
`[SRC: SRCCODE | Toysoft/libaacs src/libaacs/aacs.c ALIGNED_UNIT_LEN, _verify_ts, aacs_decrypt_unit]`
**VERIFIED**

### Q1. Is HD DVD crypto “the same AACS” as Blu-ray?

**Shared (format-independent):** AES-128 ECB/CBC, AES-G, CMAC, MKB record types,
`Kvu = AES-G(Km, IDv)`, title-key wrap `Kte = AES-128E(Kvu, Kt)`.
Default CBC IV `iv0 = 0BA0F8DDFEA61FB3D8DF9F566A050F7816` unless a format book says
otherwise. CBC **frame size** is explicitly left to the format-specific book.
`[SRC: SPEC | Common 0.953 §2.1.2–2.1.3; Pre-recorded Video 0.953 §3.3–3.5]`

**Not shared:** directory, key-file names, Volume ID storage, encryption unit, which
bytes stay clear, how the Content Key is derived, bus-encryption geometry.
HD DVD book wins those.

### Q2. Can `aacs_decrypt_unit` decrypt an EVO?

**No.** That API assumes a 6144-byte BD Aligned Unit (32×192-byte source packets),
leaves the first 16 bytes as a seed, derives a Block Key, CBC-decrypts bytes 16–6143,
and checks TS sync. HD DVD is MPEG-2 **program stream**, 2048-byte packs, and a
different Content Key (Q4–Q6). Calling it on an EVO is the wrong container, unit
size, seed, and verify.
`[SRC: SRCCODE | libaacs aacs.c _verify_ts / aacs_decrypt_unit]`
`[SRC: SPEC | HD DVD Pre-recorded Final 0.953 §4.3.2 Table 4-7]`
`[SRC: DISC | MYSTERY_MEN FEATURE_1.EVO | pack_start 00 00 01 BA every 2048]`
**VERIFIED** as a non-fit. (This is not a claim that some other unit size “almost”
works.)

A third-party HD DVD port (`libfreemkv`) even documents a 6144-byte PS check as
**unvalidated against real HD DVD media**. The format-specific book falsifies that
assumption: encryption is **per pack**, not per 6144-byte Aligned Unit.
`[SRC: SRCCODE | libfreemkv aacs/decrypt.rs unit_is_clean_ps comment]`
`[SRC: SPEC | HD DVD Pre-recorded Final 0.953 §4.3 “Encryption of an EVOB is performed on a Pack basis”]`

### Q3. Where is the Volume ID? Is it in the ISO / `DISCID.DAT`?

**Not in the UDF image.** Volume ID is split between **BCA** and **Lead-in**. A PC
host obtains the 128-bit value via `READ DISC STRUCTURE` Format `80h` after AACS
drive authentication; the drive MAC-protects it with the Bus Key.
`[SRC: SPEC | HD DVD Pre-recorded Final 0.953 §2.1 / Table 2-4; Common 0.953 §4.4, §4.14.3.1]`

`DISCID.DAT` offset 12 is a **network Disc ID** (often `FFh`×16), not Volume ID.
`[SRC: DISC | 03 §8]`
HTTP-range ISO dumps therefore **cannot** yield `Kvu`. That is a hard limit of this
corpus, not a missing file.

PMSN (optional) is also BCA (`READ DISC STRUCTURE` `81h`). KCD is Lead-in, not a
root file. No `SKB.AACS` / `SKF.AACS` in 120 listings — Sequence/Segment Key path
is unused on this corpus.
`[SRC: CORPUS | N=120 listings | grep SKB/SKF/ATKF/APLST → 0]`

### Q4. Which bytes of a pack are encrypted?

Per encrypted pack (2048 bytes):

- bytes **0–127**: Unencrypted Portion (pack/PES headers, `PES_scrambling_control`
  at byte 20, 32-bit Title Key Data `Dtk` at bytes **84–87**)
- bytes **128–2047**: Encrypted Portion (1920 bytes), AES-CBC under a **Content Key**
  `Kc`, not under the Title Key directly

`NV_PCK` and `ADV_PCK` **shall not** be encrypted. On Standard Content, `NV_PCK` is
not allowed to be encrypted. On Advanced Content the same. That is why
`FEATURE_1.EVO` starts with a clear pack header *and* a clear system header that
crosses byte 16 — the BD “first 16 bytes of the unit” model never applied here.
`[SRC: SPEC | HD DVD Pre-recorded Final 0.953 §4.3.1–4.3.2 Table 4-7]`
`[SRC: DISC | 08_NV_PCK_PCI_DSI.md | first 32 bytes of MYSTERY_MEN FEATURE_1.EVO]`
**VERIFIED** (spec + the already-observed clear NV_PCK)

`PES_scrambling_control` is the **on-pack flag** (01b encrypted / 00b not), not a
second cryptosystem. Patents say the same for ADV_PCK's private-data copy of the
field (`00b`/`01b` = whether the pack has a CPS-specific structure).
`[SRC: PATENT | US20060182418A1 Note 1 on PES_scrambling_control]`

### Q5. How is the Content Key related to the Title Key? (why BD Block Key is wrong)

The format-independent Pre-recorded Video book writes `Ce = AES-128CBCE(Kt, C)`.
The HD DVD book **overrides** that with a per-pack Content Key:

`Kc = AES-G(Kt, Dtk || CPI_lsb_96)`

`Dtk` is pack bytes 84–87. `CPI_lsb_96` is the least significant 96 bits of the
16-byte CPI field in the **GCI packet inside that EVOBU's NV_PCK**.
`TITLE_KEY_PTR` in CPI/KMI is a **1-based** index into the 64 VTKF slots
(1…64). `KEY_VF=00b` means the EVOBU is not title-key encrypted.
`[SRC: SPEC | HD DVD Pre-recorded Final 0.953 §4.2 Tables 4-1/4-2, §4.3.2, §4.3.4]`

BD instead derives a Block Key from the CPS Unit Key and the first 16 bytes of a
6144-byte Aligned Unit (libaacs `crypto_aes128e` then XOR). That construction is
**BD-book-specific**. Using it on HD DVD packs would be applying the wrong format
book.
`[SRC: SPEC | BD Pre-recorded 0.921 Figure 3-6/3-7, “Aligned Unit” = 32 source packets]`
`[SRC: SRCCODE | libaacs aacs.c _decrypt_unit]`

libaacs **AES-G / AES-128-ECB primitives** still match `Kvu` and `Kt = AES-128D(Kvu, Kte)`.
The reusable seam stops after title-key unwrap.

### Q6. VTKF layout — 32-byte stride or 36? 64 keys?

Final 0.953 **Table 3-8** (0.912 Table 3-5). Nominal file length **2480**.

| Offset | Size | Field |
|---|---|---|
| 0 | 12 | `TKF_ID` = `DVD_HD_V_TKF` |
| 12 | 4 | `HD_VTKF_SIZE` = 2480 |
| 16 | 12 | `PLAYLIST_NAME` (`VPLST%%%.XPL` or `FF`×12 on Standard Content) |
| 28 | 4 | reserved |
| 32 | 4 | `VERN` (shall be 0) |
| 36–127 | | reserved |
| 128 | 64×36 | Title Key Entry: 1-byte `BIFO` + 3 reserved + 16-byte `Kte` + 16-byte Binding MAC |
| 2432–2463 | 32 | reserved |
| 2464 | 16 | TKF MAC = CMAC(`Kvu`, bytes 0–2463) |

Arithmetic: 128 + 64×36 + 32 + 16 = **2480**. That is the listed size of every
primary `VTKF###.AACS` **except** `PANS_LABYRINTH` VTKF001 and VTKF003 (2516 =
128 + 65×36 + 32 + 16).
`[SRC: SPEC | HD DVD Pre-recorded Final 0.953 Table 3-8]`
`[SRC: CORPUS | VTKF sizes {2480, 2516}; ISO https://archive.org/download/hd-dvd_archive_01/PANS_LABYRINTH.iso]`
`[SRC: DISC | MYSTERY_MEN VTKF000 @0 `DVD_HD_V_TKF`, size `09 B0`, @0x10 `VPLST000.XPL`]`
**VERIFIED** as a layout (headers + size). Encrypted key bytes are not published here.
The 2516-byte files are **disc drift** past the book's 64-slot cap / Scenarist “64
Title Keys” note. Reader should size the table from `HD_VTKF_SIZE`, not assume 2480.

`AV_FLG` is BIFO bit 7 (set = slot occupied). `BIND_TYPE=000b` (typical on disc) fills
the Binding MAC with `FFh` (Volume ID only). Slot index is the CPS/title-key number
used by `TITLE_KEY_PTR`; empty slots are skipped, not terminators.
`[SRC: SPEC | Table 3-6 BIFO]`

Scenarist AC 4.5: “Up to 64 Title Keys can be created per project” — same 64-slot
cap. `[SRC: TOOL | Scenarist_AC_4.5_UserGuide.txt “Adding Title Keys”]`

A 32-byte stride is a known misparse: entry #1 still lands at offset 132, then
drifts +4 per slot. Recorded here so it is not rediscovered.
`[SRC: SRCCODE | libfreemkv commit 2274423 | names the 32-vs-36 failure mode]`

Selector: match `PLAYLIST_NAME` to the active playlist; do not use a foreign VTKF.
Two playlists must not share a TKF. `ATKF%%%.AACS` would pair with `APLST%%%.XPL`;
**0** `APLST`/`ATKF` in this corpus.
`[SRC: SPEC | §3.5 Title Key File]`
`[SRC: CORPUS | N=120]`

### Q7. DKF, VTUF, CONTENT_CERT — what are they for, and does playback need them?

**DKF** (64 bytes): Directory Key File. `DVD_HD_V_DKF`, size 64, encrypted directory
key at offset 48 = `AES-128E(Kvu, KDIR)`. Used to protect the **provider directory
name in persistent storage**, not EVOB payload. Ignored for Category 1.
`[SRC: SPEC | Final 0.953 Table 6-2]`
`[SRC: DISC | MYSTERY_MEN DKF | 16-byte block at offset 48]`

**VTUF** (144 bytes): Title Usage File / CCI. Playlist-bound like VTKF. Needed for
usage rules (copy control), not for recovering `Kc`.
`[SRC: SPEC | Final 0.953 Table 3-10 PLAYLIST_NAME bytes 23–34; DISC MYSTERY_MEN]`

**CONTENT_CERT.AACS** is **exactly 120 bytes** (Table 3-17, bytes 0–119): type `00h`,
`BEE` flag in bit 7 of byte 1 (bus encryption enabled), hash-unit counts, two 20-byte
CHT digests at 40 and 60, signature 80–119. No 12-byte ASCII ID — that absence was
correct. Integrity / bus-encryption advertisement, not a title key.
`[SRC: SPEC | Final 0.953 Table 3-17]`
`[SRC: CORPUS | CONTENT_CERT size 120 on every AACS disc in listings]`
**VERIFIED** (size + spec). Byte-level cert parse against a disc body still **SINGLE**
until a cert file is saved.

CHT1/CHT2 **sizes vary by title** (not a constant 145824/53860). They are hash tables
the player checks against the cert digests in the boot sequence. A research demuxer
that only wants elementary streams does not need them to *locate* packs; a licensed
player shall verify them.
`[SRC: SPEC | §3.7, §3.9 boot sequence]`
`[SRC: CORPUS | CHT1/CHT2 sizes differ across listings]`

### Q8. `MKBROM.AACS` size vs spec 1 MiB. Which MKB?

Two different objects:

- **Lead-in P-MKB** allocation is described as 1 MB = **1,048,576** bytes of MKB packs.
- **Data-area file** `MKBROM.AACS` is the MKB the player reads first in the boot
  sequence. Superfluous residual **may** follow MKBROM / MKBRECORDABLE / SKBF / CRL.
`[SRC: SPEC | Final 0.953 §1.2 residual note, §3.3, lead-in P-MKB size]`

Primary-tree listed sizes in this corpus (N=104 AACS discs):

| Bytes | N | Note |
|---|---|---|
| 1,000,000 | 88 | round-million residual |
| 1,048,576 | 10 | exact 1 MiB (`BEOWULF`, `MATRIX_REVOLUTIONS`, …) |
| 12,628 | 5 | no residual (`RAMBO_*_FRA`, `OLIVER_TWIST_JPN`, `TOTAL_RECALL_FRA`) |
| 20,480 | 1 | `PANS_LABYRINTH` (CRL on that disc is 61,440) |

A reader must stop at End-of-MKB, not trust 1e6 or a BD file length.
`[SRC: SPEC | Common 0.953 §3.2.5.1.1]`
`[SRC: CORPUS | MKBROM sizes {1000000, 1048576, 12628, 20480}]`
First record of a well-formed MKB is still Type and Version (`Record Type 10h`).
libaacs's MKB walker can consume that **if** it is pointed at `MKBROM.AACS`
instead of `MKB_RO.inf`.

`MKBRECORDABLE.AACS` is the Read/Write MKB for **update of recordable media**, allowed
on a ROM disc so a recorder can copy a newer MKB. It is **intentionally absent** from
the backup directory.
`[SRC: SPEC | §3.3, §3.11 “except the MKBRECORDABLE.AACS”]`
`[SRC: CORPUS | 99 BAK = primary minus MKBRECORDABLE; 5 copy MKBRECORDABLE into BAK]`
**VERIFIED** (spec + corpus; this was empirical first, now sourced)

### Q9. `ANY!` vs `AAC!` vs reserved `AACS`?

The book: root directory name **`AACS`** is reserved; backups in **`AACS_BAK`**.
Filenames inside (`MKBROM.AACS`, `VTKF%%%.AACS`, …) **match the discs**.
`[SRC: SPEC | §3.1, §3.3, §3.5, §3.11]`

The discs: **`ANY!/`** (96) or **`AAC!/`** (8), plus `*_BAK/`. Same file set.
`[SRC: CORPUS | N=120]`
**VERIFIED disagreement.** Disc wins for a reader; a libaacs port must probe
`ANY!`, `AAC!`, and `AACS`, not hardcode `AACS/`. Why authoring used `ANY!`/`AAC!`
is **OPEN**.

MMC `READ DISC STRUCTURE` Sub-command shall be `0000b` for DVD **or HD DVD**, `0001b`
for BD — another place libaacs's BD path would miss HD DVD even for Volume ID.
`[SRC: SPEC | Common 0.953 §4.14.3]`

### Q10. Bus encryption — same as BD's per-2048-in-6144 loop?

**No.** HD DVD bus encryption (PC host ↔ licensed drive) also uses a 128/1920 split,
but the BE Key is `Kbe = AES-G(Krd, Dbe || DEADBEEFDEADBEEFDEADBEEF16)` with `Dbe` at
pack bytes **14–17**, and it applies **only to EVOB/P-EVOB/S-EVOB sectors** (`B_flag`
in CPR_MAI). libaacs bus decrypt walks 6144 in 2048 steps leaving 16 bytes clear —
wrong prefix and wrong seed location.
`[SRC: SPEC | Final 0.953 §4.3.5 Table 4-9; Common 0.953 §4.14 bus extents]`
`[SRC: SRCCODE | libaacs aacs.c _decrypt_unit_bus]`

HTTP ISO dumps are not bus-encrypted (no drive). Bus encryption is a **drive/host**
problem for real-media playback, not for this corpus.

### Q11. What can a player reuse from libaacs without using the BD unit path?

| Piece | Reuse? |
|---|---|
| Device/processing-key file, MKB subset-difference walk | **Yes** (Common book). Feed `MKBROM.AACS`, not `MKB_RO.inf`. |
| `Kvu = AES-G(Km, VolumeID)` | **Yes**, once Volume ID comes from the drive (not the ISO). |
| `Kt = AES-128D(Kvu, Kte)` | **Yes**. VTKF entries are that `Kte`. |
| `aacs_decrypt_unit` / `_verify_ts` / 6144 Block Key | **No.** |
| `Unit_Key_RO.inf` parser | **No.** Parse VTKF Table 3-8; select by playlist name. |
| Path `AACS/` | **No.** Probe `ANY!` / `AAC!` / `AACS`. |
| `CONTENT_CERT` BEE bit | Layout is HD DVD Table 3-17, not BD `Content00.cer`. |

VLC's libaacs hook is built around `aacs_decrypt_unit(buf[6144])`. An HD DVD module
cannot satisfy that hook with EVOs. It needs its own access/demux path: 2048-byte
packs, CPI from NV_PCK/GCI, pack-local `Dtk`, and a Content Key distinct from BD's
Block Key. That is an integration fact, not a how-to.

### Refuted hypotheses (this round)

- “CBC frame is 6144 on HD DVD because that is the AACS Aligned Unit.” **Wrong.**
  HD DVD has no Aligned Unit in the format-specific book; the frame is the 1920-byte
  Encrypted Portion of a pack.
- “First 16 bytes of each unit stay plain, like BD / libaacs.” **Wrong.** 128 bytes
  stay plain; NV_PCK/ADV_PCK are entirely plain.
- “Title Key is the CBC key for content, per the format-independent book §3.4.”
  **Overridden** by `Kc = AES-G(Kt, Dtk \|\| CPI_lsb_96)`.
- “`ANY!_BAK` dropping `MKBRECORDABLE.AACS` is an authoring quirk.” **Specified.**
- “Table 3-8 is the MKB Subset-Difference Index” (Common book). **Different book.**
  HD DVD Final 0.953 Table 3-8 is the Title Key File. Always name the book.
