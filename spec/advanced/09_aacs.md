# 9. AACS overlay (format only)

*Counts written "N/120", "N/119", "on N discs", "listings", or as named discs are over the reference corpus of 120 archived retail HD DVD images [11]. `eNN` are the reproducible verification experiments [12].*


This section defines the on-disc AACS layout so a licensed player knows what to read. It is **not** a decryptor and contains no keys. Volume ID is **not** in the ISO.

Navigation XML / MAP / VTI / NV_PCK headers are always readable.

## 9.1 Directories

Book name: `AACS/`.  
Discs: `ANY!/` (96) or `AAC!/` (8). Mirror: `ANY!_BAK/` / `AAC!_BAK/`.  
Probe `ANY!`, then `AAC!`, then `AACS`.

BAK: 104/104 AACS discs have a backup. **99** omit only `MKBRECORDABLE.AACS`
(Final 0.953 §3.11). **5** also copy that file (the 12,628-byte `MKBROM` titles).

16/120 discs have no AACS directory (unencrypted).

## 9.2 Files

| File | Typical size | Role |
|---|---|---|
| `MKBROM.AACS` | 1e6 (88), 1 MiB (10), 12628 (5), 20480 (Pan’s) | Media Key Block. Stop at End-of-MKB; listed size may include padding |
| `MKBRECORDABLE.AACS` | ~1e6 | recorder MKB |
| `DKF.AACS` | 64 | Directory Key File: names the provider's persistent-storage directory (§9.4) |
| `VTKF$$$.AACS` | 2480 (`HD_VTKF_SIZE`); two Pan’s files add 36 zero bytes (§9.3) | Title Key File for `VPLST$$$.XPL` |
| `VTUF$$$.AACS` | 144 (all `URS_NUM` 0); format allows ≤ 64 KB | Title Usage File (§9.8). Same `$$$` as VTKF |
| `CONTENT_CERT.AACS` | 120 | Content Certificate (§9.5) |
| `CONTENT_HASH_TABLE1.AACS` | 8 + 8 × NHV | CHT #1: low 64 bits of SHA-1 of every EVOBU / TU, indexed by CPI `CH_PTR` |
| `CONTENT_HASH_TABLE2.AACS` | 40 060 + 8 × NHA | CHT #2: hashes of `DISCID.DAT`, `DKF`, `MNGCPY_MANIFEST`, every VTUF / ATUF, every XML and script file |
| `CONTENT_REVOCATION_LIST.AACS` | usually 1e6; 61440 on Pan’s | revocation |
| `MNGCPY_MANIFEST.XML` | ~200–304 | Managed Copy; not playback |

`ATKF` / `SKF` / `APLST`: **0/120**.

**Trailing residue** is permitted only after `MKBROM`, `MKBRECORDABLE`, `SKBF` and
`CONTENT_REVOCATION_LIST` [4 p. 21]; that is why their listed sizes vary. Every other
AACS file ends at its declared size.

### Content Hash Tables (Tables 3-18, 3-19)

CHT #1: `NHV` (u32, ≤ 500 000), 4 reserved bytes, then `NHV` 8-byte hashes, one per
EVOBU / TU, each the **least-significant 64 bits (last 8 bytes) of SHA-1** over the
EVOBU as stored (encrypted or not). An EVOBU's CPI `CH_PTR` (§9.6) is its 1-based
index here.

CHT #2 (fixed offsets): 0 `DISCID.DAT` (8), 8 `DKF.AACS` (8), 16 `MNGCPY_MANIFEST.XML`
(full 20-byte SHA-1), 36 `VTUF.AACS` (20), 56 `VTUF000`–`VTUF999` (20 each), 20 056
`ATUF000`–`ATUF999` (20 each), 40 056 `NHA` (u32), 40 060 `NHA` 8-byte hashes of XML
and ECMAScript files. A TUF hash covers its first `HASH_SIZE` bytes. Absent files are
`FF`-filled. The player checks these before using the file [4 §3.8].

Keyless verification on **104/104** AACS discs (`e22`): both CHT sizes match their
counts; Content Certificate digest #1 = SHA-1(CHT #1) and #2 = SHA-1(CHT #2); the DKF,
manifest and all 217 VTUF slots match; absent-TUF slots are `FF`. "Least-significant
64 bits" is the **last** 8 bytes of the digest (DKF: 104 match last-8, 0 first-8).
Two VTUFs with `HASH_SIZE` = 8 are hashed over **8** bytes, not 128: the stored field,
not the book's definition, is what the authoring tool hashed.
`Total_Number_of_HashUnits` (§9.5) = `NHV` + `NHA` + 3 + (VTUF files present) on
104/104. Every EVOBU sampled in `e23` has `CH_PTR` within 1 … `NHV`. `[11]` **VERIFIED**

### `-SLY`: DISCID rewritten after authoring

CHT #2 fixes the hash of `DISCID.DAT` at authoring time. It matches the shipped DISCID
on **71** discs. On the other **33** the DISCID was changed afterwards, and all 33 are
exactly the discs whose `PROVIDER_ID` ends in ASCII **`SLY`** ([02](02_discid.md) §2.2):

- 28 ASCII tags (`UNIVERSAL_HD-SLY`, `PARAMOUNT_HD-SLY`, `WHV***V1**HD-SLY`,
  `DW_ANIM___HD-SLY`): the committed hash matches the same file with **`DVD`**
  restored in place of `SLY`. They were authored as `…HD-DVD`.
- `HOT_FUZZ`, `PREMONITION_GER` (binary IDs ending `534c59`): the original last three
  bytes were recovered by exhaustive search against the committed hash: `66 49 2d` and
  `4d 01 cf`. `HOT_FUZZ`'s restored ID equals the provider ID of `RAMBO_1/2/3_FRA`,
  `TOTAL_RECALL_FRA` and `ARMY_OF_SHADOWS` byte for byte, which confirms the search.
- `BROTHERS_GRIMM`, `PHANTOM_OF_THE_OPERA`, `THE_JACKAL` (identical DISCIDs, all-`FF`
  ID ending `SLY`): original differs in more than the last three bytes; not recovered.

A conforming AACS player verifies this hash at boot, so these images do not carry the
DISCID that was pressed. `[11]` **VERIFIED** (`e22`, 33/33 rewrites, 0 other
mismatches). That the suffix marks images processed with SlySoft AnyDVD HD is
**INFERRED** from the name only.

## 9.3 VTKF: Table 3-8 (Final 0.953)

One Title Key File per playlist: `VTKF$$$.AACS` accompanies `VPLST$$$.XPL`, and two
playlists may not share one. `VTKF.AACS` (no number) is the Category 1 name
[4 §3.5]. Each entry holds one encrypted Title Key; which entry decrypts an EVOB
is chosen by `TITLE_KEY_PTR` in that EVOB's CPI (§9.6).

| Offset | Size | Field | Rule |
|---|---|---|---|
| 0 | 12 | `TKF_ID` | `"DVD_HD_V_TKF"` |
| 12 | 4 | `HD_VTKF_SIZE` | end address of the TKF; **shall be 2480** |
| 16 | 12 | `PLAYLIST_NAME` | `VPLST%%%.XPL` / `APLST%%%.XPL`; `FF`×12 for Standard Content |
| 28 | 4 | reserved | `00` |
| 32 | 2 | `VERN` | 0 (see note) |
| 34 | 94 | reserved | `00` |
| 128 | 64 × 36 | Title Key Entry #1 … #64 | below |
| 2432 | 32 | reserved | `00` |
| 2464 | 16 | TKF MAC | CMAC(`Kvu`, bytes 0 … 2463) |

**The TKF is a fixed 2480-byte structure with exactly 64 entries** [4 Table 3-8].
`HD_VTKF_SIZE` = 2480 on **434/434** files (primary + BAK, 104 discs) (`e21`).
The player compares `PLAYLIST_NAME` with the **active** playlist (including after
`IPlaylist.load`) and must not use the keys unless they match [4 §3.5].

**Correction: `PANS_LABYRINTH` has no 65th slot.** `VTKF001` / `VTKF003` are 2516-byte
files: a normal 2480-byte TKF (`HD_VTKF_SIZE` = 2480, 64 entries, reserved zero, TKF MAC
at 2464) followed by **36 zero bytes**. The padding is exactly one entry wide, which is
why reading to the file length produced a phantom 65th entry. The book allows trailing
residue only after `MKBROM`, `MKBRECORDABLE`, `SKBF` and `CONTENT_REVOCATION_LIST`
[4 p. 21], so this is an authoring deviation. **Parse to `HD_VTKF_SIZE`, never to the
file length.** `[11]` **VERIFIED** (`e21`, 4/4 files)

`VERN` width: the book's table gives bytes 32–33, its prose "4 bytes". Bytes 32–35
are zero on 434/434, so both readings hold on disc.

### Title Key Entry (36 bytes)

| Off | Size | Field | Rule |
|---|---|---|---|
| 0 | 1 | `BIFO` | **Binding Information**, Table 3-9 below |
| 1 | 3 | reserved | `00` |
| 4 | 16 | `Kte` | encrypted Title Key: `Kte = AES-128E(Kvu, Kt)`, ECB |
| 20 | 16 | Binding MAC | per `BIND_TYPE` |

`TITLE_KEY_PTR` is **1-based** (1…64). Empty slots are skipped, not terminators.
A 32-byte stride is a known misparse.

### BIFO: Binding Information (Table 3-9)

| Bits | Field | Meaning |
|---|---|---|
| 7 | `AV_FLG` | 1 = Title Key available, 0 = not available |
| 6–4 | `BIND_TYPE` | what the key is bound to (below) |
| 3–0 | reserved | 0 |

| `BIND_TYPE` | Bound to | Binding MAC |
|---|---|---|
| `000` | Volume ID only | `FF`×16 |
| `001` | Pre-recorded Media Serial Number (PMSN) | CMAC(`Kt`, PMSN) |
| `010` | Device Unique Nonce (DUN) | CMAC(`Kt`, DUN) |
| `011` | PMSN and DUN | CMAC(`Kt`, AES-G(DUN, PMSN)) |
| `100` | Temporary Nonce (TN) | CMAC(`Kt`, TN) |
| others | reserved | |

`Kt = AES-128D(Kvu, Kte)`. Title Keys for content on a pre-recorded disc are
`BIND_TYPE 000`; the other types protect content copied to persistent storage.
A player verifies the Binding MAC before using a Title Key [4 §3.5].

Corpus (`e21`), 217 primary TKFs: **25 662 used slots, every one `BIFO` = `0x80`**
(`AV_FLG` 1, `BIND_TYPE` 000, Binding MAC `FF`×16); 2 114 unused slots, `BIFO` = `0x00`.
The book does not say how an unused slot is filled: its MAC is `FF`×16 on all 2 114,
its `Kte` `FF`×16 on 1 844 and `00`×16 on 270. 195 TKFs fill all 64 slots; 22 use
between 1 and 59. `[11]` **VERIFIED**

Three titles have extra VTKF files without a matching VPLST (`BALLS_OF_FURY`
`VTKF001`, `CHUCK_AND_LARRY` `VTKF016`, `SHREK_THE_THIRD_EU` `VTKF004`). The book
forbids two playlists sharing a TKF; it does not address a TKF with no playlist.

## 9.4 DKF (64 bytes): Table 6-2

**Directory Key File.** It carries the key that names the content provider's directory
in persistent storage [4 §6.3]. It is not used to decrypt video. Required on an AACS
disc; ignored for Category 1.

| Offset | Size | Field | Rule |
|---|---|---|---|
| 0 | 12 | `DKF_ID` | `"DVD_HD_V_DKF"` |
| 12 | 4 | `HD_VDKF_SIZE` | shall be 64 |
| 16 | 16 | reserved | `00` |
| 32 | 2 | `VERN` | 0 |
| 34 | 14 | reserved | `00` |
| 48 | 16 | `KDIRe` | encrypted Directory Key: `KDIRe = AES-128E(Kvu, KDIR)`, ECB |

**What the Directory Key does** [4 §6.3]. At boot, with `SEARCH_FLG` = 0 ([02](02_discid.md) §2.3), the
AACS module checks the DKF's hash against CHT #2 (§9.2), decrypts `KDIR` with `Kvu`,
and derives the **name of the provider's directory** from DISCID `PROVIDER_ID`:

```
PROVIDER_DIR = AES-G(KDIR, PROVIDER_ID)      16 bytes, written as a GUID
```

Persistent storage is laid out as:

```
/HD_DVD/INFO.TXT                              medium information (player)
/HD_DVD/<PROVIDER_DIR>/INFO.TXT               provider information (applications)
/HD_DVD/<PROVIDER_DIR>/<icon images>          not encapsulated; shown by the management screen
/HD_DVD/<PROVIDER_DIR>/<CONTENT_ID>/INFO.TXT  content information (applications)
/HD_DVD/<PROVIDER_DIR>/<CONTENT_ID>/…         the disc's files, e.g. VPLST003.XPL
```

So `PROVIDER_ID` never appears on the storage device as written in DISCID; the folder
name is a keyed transform of it, reproducible only with `KDIR`. The `<CONTENT_ID>`
folder is the GUID string of DISCID `CONTENT_ID`. `[4]` **SPEC**; 0 on-device
directory specimens.

Corpus (`e21`): all fields above hold on **208/208** files (104 discs, primary + BAK);
`KDIRe` is real data on every disc (never `00`×16 or `FF`×16) and distinct on every
disc (104 values). Distinct ciphertext is expected even if a provider reused one
`KDIR`, because `Kvu` differs per disc. `[11]` **VERIFIED**

## 9.5 CONTENT_CERT (120 bytes): Table 3-17

One per disc [4 §3.7]. It signs the two Content Hash Tables, so it authenticates
every hashed file on the disc.

| Off | Size | Field | Rule |
|---|---|---|---|
| 0 | 1 | Certificate Type | `00h` |
| 1 | 1 | bit 7 `BEE`, bits 6–0 reserved | Bus Encryption Enabled: 1 = PC hosts must bus-encrypt EVOB reads |
| 2 | 4 | `Total_Number_of_HashUnits` | hashes in CHT #1 + CHT #2 (§9.2) |
| 6 | 1 | `Total_Number_of_Layers` | `01h` |
| 7 | 1 | `Layer_Number` | `00h` |
| 8 | 4 | reserved | `00` |
| 12 | 2 | `Number_of_Digests` | `0002h` |
| 14 | 2 | Applicant ID | with the next field, forms the Content Certificate ID |
| 16 | 4 | Content Sequence Number | |
| 20 | 2 | Minimum CRL Version | |
| 22 | 2 | reserved | `00` |
| 24 | 2 | `Length_Format_Specific_Section` | `000Eh` |
| 26 | 14 | reserved | `00` |
| 40 | 20 | CHT Digest #1 | SHA-1 of `CONTENT_HASH_TABLE1.AACS` |
| 60 | 20 | CHT Digest #2 | SHA-1 of `CONTENT_HASH_TABLE2.AACS` |
| 80 | 40 | Signature Data | AACS LA signature (Pre-recorded Video Book) |

Corpus (`e21`, `e22`), **208/208** files (104 discs): every fixed value above holds;
`BEE` = 0 and Minimum CRL Version = 0 on all; both digests equal SHA-1 of the saved
hash tables. `[11]` **VERIFIED**

**Applicant ID does not identify the studio.** Values: `111` (53 discs), `109` (22),
`134` (12), `140` (9), `104` (6), `177`, `226` (1 each). `111` spans Universal,
Paramount and DreamWorks titles; `134` spans Universal, Paramount, Warner, New Line and
DreamWorks Animation, all 2007 releases; `140` is German releases; `104` is French and
Japanese releases. The grouping follows region and release period, consistent with the
replicator or authoring facility that applied to AACS LA. **INFERRED**

## 9.6 Pack encryption: Table 4-7

Per encrypted 2048-byte pack:

| Bytes | |
|---|---|
| 0–127 | Unencrypted Portion. `PES_scrambling_control` at byte 20. `Dtk` u32 at **84–87** |
| 128–2047 | Encrypted Portion, AES-CBC, 1920 bytes |

NV_PCK and ADV_PCK shall not be encrypted.

Content key (HD DVD book **overrides** the generic Pre-recorded Video book):

```
Kc = AES-G(Kt, Dtk || CPI_lsb_96)
```

`Kt` from VTKF slot `TITLE_KEY_PTR`.  
`CPI` = 16 bytes in GCI_PKT of that EVOBU's NV_PCK (Table 4-1).

**CPI byte offset inside GCI_PKT: CLOSED for typical NV_PCK framing. Pack offset 0x3C.**
If the pack has stuffing or omits the system header, parse GCI by `sub_stream_id 0x04`
and take CPI from that PES (GCI-payload offset 12 on the observed layout). Corpus
`e09`: 704/704 packs `PES_scrambling_control=00`; no encrypted pack to re-test.

`[9]`
`[11]`
**VERIFIED**

The first reverse-engineering tool encodes the offset the AACS book and the patents
both deferred. In the NV_PCK (first pack of an EVOBU), the 16-byte CPI field is at
**pack byte 0x3C (60)**, inside the GCI packet (start code `00 00 01 BF` at 0x29–0x2C,
`sub_stream_id` `0x04` at 0x2F; CPI = GCI payload byte 13 counting that `0x04`). Confirmed byte-for-byte against a real disc: the nav-pack signature
(`[0x2A]=00 [0x2B]=01 [0x11]=0xBB [0x2C]=0xBF`) matches and CPI@0x3C reads all-zero
on unencrypted `RESERVOIR_DOGS` (`KEY_VF=0`, correct for clear content).

Content-key math, from the same source (`decryptPACK`):
```
Dtk         = pack bytes 84..87            (keySeed[0..3])
CPI_lsb_96  = CPIField[4..15]              (keySeed[4..15])
Kc          = AES-G(Kt, Dtk || CPI_lsb_96)
plain[128..2047] = AES-128-CBC-decrypt(Kc, cipher[128..2047])
KEY_VF      = CPIField[0] & 0x80           TITLE_KEY_PTR = u16be(CPIField[1..2])
```

AACS Table 4-2: `TITLE_KEY_PTR` is **two bytes** (example `0009h`). BackupHDDVD
used `CPIField[2]` alone, which is correct when byte 1 is `00`. `KEY_VF=00b` →
do not decrypt. Cannot test `10b` on stripped ISOs.

Two facts about *this corpus* remain, and they are why no encrypted pack is present
to exercise the above:

1. **The book defers it by design.** §4.2 verbatim: *"A CPI field is located in a
   GCI packet (GCI_PKT)... See the HD DVD-Video Specifications for the detailed
   location of CPI field in a GCI_PKT."* That book never leaked.
   `WO2006070920A1` FIG.109 gives GCI's field **order** (`GCI_GI`, `DCI_CCI_SS`,
   `DCI`, `CCI`, `RECI`) but no byte counts - the sizes live in the figure image.

2. **This corpus has no encrypted pack to solve against.** Table 4-7 [4]: *"When a Pack
   is encrypted, the 2-bit PES_scrambling_control shall be 01_2. Otherwise, the
   PES_scrambling_control shall be 00_2."* (pack byte 20, bits 5-4). Measured at 50%
   file depth, 64 packs each, by `experiments/e09_pack_encryption.py`
   (8 AACS-directory titles + 3 without):
   **scrambling = 00₂ on 704/704 packs.** Every 16-byte window in the dumped GCI
   reads `KEY_VF = 00_2` ("do not decrypt") - the correct value for clear content.
   `[11]` **VERIFIED**

   Entropy does not separate them either: AACS `MYSTERY_MEN` tail 7.818 vs
   known-unencrypted `DOWNFALL` 7.727 / `INSIDE_MAN` 7.865. Compressed video sits
   at 7.7-7.9 whether or not AES ran.

**Conclusion: the Archive.org ISOs are AACS-stripped.** The `ANY!`/`AAC!` trees are
copied verbatim; the packs are in the clear. Everything here about *file layout*
holds. Nothing about *encrypted content* can be derived or tested from this corpus.
The corpus cannot exhibit an encrypted pack, but CPI's location is no longer OPEN. It was recovered from BackupHDDVD's source (above), not from these ISOs.

### CPI layout (Tables 4-1 to 4-6)

| CPI bytes | Block | Field |
|---|---|---|
| 0–3 | **KMI** Key Management Information | byte 0 bits 7–6 `KEY_VF` (bits 5–0 reserved); bytes 1–2 `TITLE_KEY_PTR` (u16); byte 3 `SEG_KEY_PTR` |
| 4–7 | **CHMI** Content Hash Management Information | `CH_PTR` (u32): this EVOBU's entry in CHT #1, 1 … 500 000 |
| 8–9 | **URMI** Usage Rule Management Information | bit 15 `UR_VF`; bits 14–0 `UR_PTR` (Usage Rule Set number in the TUF, 1 … 255); all ones when `UR_VF` = 0 |
| 10–11 | **CCI_SS** (status of CCI) | byte 10: bit 7 `PCCI_VF`, 6 `APS_VF`, 5 `ICT_VF`, 4 `DOT_VF`, 3–0 reserved; byte 11 reserved |
| 12–13 | **CCI** Copy Control Information | byte 12: bits 7–5 `PCCI`, 4–2 `APSTB`, 1 `ICT`, 0 `DOT`; byte 13 reserved |
| 14–15 | reserved | `00` |

`KEY_VF`: `00` no key pointer valid (EVOBU not encrypted), `01` `SEG_KEY_PTR` valid,
`10` `TITLE_KEY_PTR` valid, `11` reserved. When `KEY_VF` ≠ `10`, `TITLE_KEY_PTR`
**shall be 0**; when ≠ `01`, `SEG_KEY_PTR` shall be 0.

`PCCI` (primitive copy control): `000` Copy Freely, `100` Copy One Generation, `010`
No More Copies, `110` Copy Never, `011` Encryption Plus Non-Assertion. `APSTB`
(analog protection): `000` off, `001`–`011` APS1 types 1–3, `110`/`111` APS2. `ICT`: 1 =
high-definition analog output only as a constrained image. `DOT`: 1 = no analog output
of the decoded video. A validity flag of 0 in CCI_SS means its field is read as its
permissive value. If main and sub video are both shown, the main video's CCI applies.

**One Title Key per EVOB** [4 §4.3]: *"A Title Key shall not be changed within one
P/S-EVOB. A Title Key may be shared by plural EVOBs."* CCI and `UR_PTR` also stay
constant within an EVOB. `TITLE_KEY_PTR` is repeated in every EVOBU's CPI, but the
key only changes at an EVOB boundary. Because `CPI_lsb_96` contains `CH_PTR`, each
EVOBU still gets its own content key `Kc`.

**Observed on disc** (`e23`, 24 consecutive EVOBUs on each of 11 AACS discs and the
unencrypted `1408_DC`; the GCI `sub_stream_id` is at pack offset 47 on all, so CPI is at
pack `0x3C`):

- `CH_PTR` rises by exactly 1 per EVOBU and stays within 1 … `NHV` of that disc's
  CHT #1: **this locates the CPI on the disc itself**, independently of BackupHDDVD.
- URMI = `7FFF` (`UR_VF` 0, `UR_PTR` all ones, as the book requires); CCI_SS = `F000`
  (all four validity flags set) on 10 of 11, `0000` on `HOT_FUZZ`.
- `KEY_VF` = `00` and CCI = `0000` on all, yet `TITLE_KEY_PTR` = 1, 3, 7 or 9 remains,
  and every such pointer lands on an occupied slot of that disc's VTKF. The book forbids a
  non-zero pointer with `KEY_VF` = `00`: CPI bytes 0 and 12 were cleared by the tool
  that decrypted the image (BackupHDDVD documents exactly this, §9.11), and the leftover
  pointers show which Title Key each EVOB was originally encrypted with.
- `1408_DC` (no AACS directory): all 16 CPI bytes are zero.
`[11]` **VERIFIED**

Blu-ray `aacs_decrypt_unit` (6144-byte TS aligned unit) **does not apply**.
Reusable: MKB walk, AES-G, `Kvu = AES-G(Km, VolumeID)`, `Kt = AES-128D(Kvu, Kte)`.

## 9.7 Volume ID

BCA + Lead-in. MMC `READ DISC STRUCTURE` format **`80h`**, after AACS drive
authentication. Not `DISCID.DAT@12`. This ISO corpus cannot yield `Kvu`.

## 9.8 VTUF: Table 3-10 (Final 0.953)

**Title Usage File.** Holds the Usage Rules (copy and output permissions) that an
EVOB's CPI can point to through `UR_PTR` (§9.6). Optional on a disc; one per
playlist (`VTUF$$$.AACS` with `VPLST$$$.XPL`), never shared; `VTUF.AACS` is the
Category 1 name; at most 64 KB [4 §3.6].

| Offset | Size | Field | Rule |
|---|---|---|---|
| 0 | 12 | `URF_ID` | `"DVD_HD_V_TUF"` |
| 12 | 4 | `HD_VURF_SIZE` | file size in bytes, ≤ 65 536 |
| 16 | 1 | `URS_NUM` | number of Usage Rule Sets, 0…255 |
| 17 | 4 | `HASH_SIZE` | bytes covered by the CHT #2 hash: the TUF minus the BURS fields and TUF MAC |
| 21 | 2 | `VERN` | 0 |
| 23 | 12 | `PLAYLIST_NAME` | `VPLST%%%.XPL`; `FF`×12 for Standard Content |
| 35 | 93 | reserved | `00` |
| 128 | X₁ … Xₙ | Usage Rule Set #1 … #N | Table 3-12, variable |
| 128 + ΣX | 17 × N | BURS #1 … #N | 1-byte `BIFO` + 16-byte Binding MAC each (Table 3-11) |
| end − 16 | 16 | TUF MAC | CMAC(`Kvu`, whole TUF except this field) |

With `URS_NUM` = 0 there are no URS or BURS and the file is exactly **144 bytes**: header
to 127, TUF MAC at 128. `VERN` is 2 bytes here although the book's prose says 4; the
table places `PLAYLIST_NAME` at 23, which only fits a 2-byte `VERN`.

**BURS** (Table 3-11) binds one Usage Rule Set with the same `BIND_TYPE` values as
§9.3, but its `AV_FLG` is always 0 and its Binding MAC is keyed differently: `00`×16
for Volume-ID binding, otherwise CMAC(PMSN / DUN / AES-G(DUN, PMSN) / TN, {URS}).
A mismatched `PLAYLIST_NAME`, TUF MAC or Binding MAC sends the player to Stop State
before the associated EVOB plays [4 §3.6].

**Usage Rule Set** (Table 3-12): a 10-byte header, `URS_VERSION` (2), `URS_SIZE` (4,
the whole set including this header), `UR_NUM` (4), then `UR_NUM` Usage Rules. Each rule
is `UR_ID` (3), `UR_TYPE` (1), `UR_SIZE` (4, the whole rule including these 8 bytes) and
a `UR_BODY` of `UR_SIZE` − 8 bytes. `URS_VERSION` tells apart two sets with identical
rules but different bindings. A player processes rules whose `UR_ID` it recognises; for
an unknown one, `UR_TYPE` decides: `00h` ignore it and play, `10h` go to Stop State.
Rule bodies are Tables 3-13 to 3-16 (CCI for update, time-based conditions, REL rules,
output control bits).

Corpus (`e21`), **434/434** files (217 primary + BAK): 144 bytes, `URS_NUM` = 0,
`HD_VURF_SIZE` = length, `VERN` 0, reserved zero, `PLAYLIST_NAME` at **23** matching
the file number. No disc carries a Usage Rule Set. `HASH_SIZE` is 128 (bytes 0–127)
on 430 files but **8** on both copies of `KING_OF_CALIFORNIA` and
`RESIDENT_EVIL3_GER`; see §9.2 for which value CHT #2 actually hashed. `[11]`
**VERIFIED**

Do not use `spec/clean/09_AACS.md` "name at 0x18". That dump folded `'V'` into the
preceding field. Disc and book agree on **23**.

## 9.9 Reusing libaacs: what ports and what does not

Source: `code.videolan.org/videolan/libaacs` (master), read directly.
`[8]` **VERIFIED**

Chain: `_read_mkb_file("AACS/MKB_RO.inf")` (aacs.c:315) -> `_calc_mk` (613) ->
`_read_vid` via MMC (689) -> `_calc_vuk = aes128d(mk,vid)` (738) ->
`_calc_uks` from `AACS/Unit_Key_RO.inf` (812/886) -> `aacs_decrypt_unit` (1186).

**Reusable unchanged** - `crypto.h` exposes exactly what HD DVD needs:
`crypto_aesg3` = AES-G for `Kc = AES-G(Kt, Dtk || CPI_lsb_96)`; `crypto_aes128d/e`
for `Kt`/`Kvu`/`KDIRe`; `crypto_aes_cmac_16` for VTKF/VTUF MACs. `mkb.c`, `mk.c`,
`ec.c` are format-independent.

**Needs modification:**

| Component | Blocker | Scale |
|---|---|---|
| `aacs.c` paths | hardcodes `AACS/MKB_RO.inf`, `AACS/Unit_Key_RO.inf`; HD DVD is `ANY!/`/`AAC!/` + `MKBROM.AACS`/`VTKF$$$.AACS` | trivial |
| `mmc.c:167` | `cmd[1] = MMC_MEDIA_TYPE_BLURAY & 0x0f` hardcoded; format `80h` (mmc.c:108) is shared | one line, mandatory |
| `unit_key.c:134` | parses BD title->CPS-unit map at `p+26+2+4*i`; HD DVD has no CPS-unit table (VTKF binds by playlist name, per-EVOBU by `TITLE_KEY_PTR` in CPI) | rewrite |
| `aacs_decrypt_unit:1191` | `if(!(buf[0]&0xc0))` over BD's 6144-byte aligned unit of 192-byte TS packets; HD DVD is a 2048-byte pack, 128 clear + 1920 AES-CBC | rewrite |

**The cryptography ports; the container and key-indexing layers do not.**

### Exact extension points (libaacs master, read 2026-09)

| libaacs location | BD behaviour | HD DVD change |
|---|---|---|
| `aacs.c:49` `ALIGNED_UNIT_LEN 6144` | 6144-byte unit = 32×192 TS packets | HD DVD unit is a **2048-byte pack**; add a parallel constant |
| `aacs.c:_decrypt_unit` (~966) | block key `AES128E(uk, buf[0:16]) XOR buf[0:16]`, then `crypto_aacs_decrypt` over bytes 16..6144 | HD DVD: `Kc = AES-G(Kt, Dtk‖CPI_lsb_96)` (Kt from VTKF by `TITLE_KEY_PTR`), CBC over bytes **128..2047** with **fixed IV** `0BA0…0F78`. New function, not a parameter tweak. |
| `aacs.c:_verify_ts` (~957) | checks `0x47` TS sync every 192 B, clears CPI bits | HD DVD verifies MPEG-2 PS `00 00 01 BA` at pack start; replace |
| `aacs.c:1186` `aacs_decrypt_unit` | reads BD TP_extra_header CPI (`buf[0]&0xc0`) | HD DVD keys off `PES_scrambling_control` (pack byte 20 bits 5-4) + CPI@0x3C |
| `aacs.c:315,886` paths `AACS/MKB_RO.inf`,`AACS/Unit_Key_RO.inf` | Blu-ray dir | HD DVD `ANY!/`or`AAC!/` + `MKBROM.AACS`/`VTKF$$$.AACS` |
| `unit_key.c` CPS-unit map (`p+26+2+4*i`) | title→CPS-unit table | HD DVD binds by playlist filename; per-EVOBU `TITLE_KEY_PTR` from CPI |
| `mmc.c:167` `cmd[1]=MMC_MEDIA_TYPE_BLURAY` | BD media type in CDB | set HD DVD media type; format `80h` (`mmc.c:108`) is shared |

**Reusable unchanged:** `crypto.h`: `crypto_aesg3` (= AES-G), `crypto_aes128e/d`,
`crypto_aes_cmac_16`, plus `mkb.c`, `mk.c`, `ec.c` (MKB walk, media key, EC-DSA).
The key ladder MKB→Km→Kvu→Kt is format-independent; only the container read and
the final pack-decrypt differ. And it is
moot for ISO-only work: `Kvu` needs the BCA Volume ID (§9.7), absent from any ISO.

## 9.10 Prior art: the corpus was decrypted by known 2007 tools

The stripped-corpus finding (§9.6) has a direct explanation: HD DVD AACS was broken
publicly in 2007 and the toolchain is open source. libhddvd does **not** need to
solve decryption; for an already-decrypted ISO it needs nothing, and for a pristine
disc the existing tools produce the keys.

**Timeline** `[16]`:
- 2006-12 / 2007-01: `muslix64` releases **BackupHDDVD**, extracting per-title keys
  from HD DVD by reading them out of a software player's memory.
- 2007-02-11: Doom9 user `arnezami` recovers the AACS **Processing Key**
  (device- and title-independent). The hex is in that controversy; **not
  reproduced here**.

**Tools, with source availability** `[16]`:

| Tool | Role | Source |
|---|---|---|
| **DumpHD** (Java) | decrypts EVO/ACA via `keydb.cfg` or on-disc key retrieval; bundles ACAPacker, PackScanner | binaries; the reference HD DVD ripper |
| **BackupHDDVD** (C# / GUI) | decrypt EVO **and ACA** | source included |
| **aacskeys** (C) | derive full key list incl. VUK from a player host certificate | source |
| **Zotty's ACA Decrypter**, **extract_aca** | `.ACA` element extraction/decrypt | C++ source |
| **dumpvid**, **VUKkeyfinder**, **validateVUK** | obtain/validate Volume ID / VUK from a drive or player memory | source |

`keydb.cfg` (the same format libaacs consumes) is still mirrored, e.g.
`fvonline-db.bplaced.net`, `vlc-aacs.whoknowsmy.name`.

**What this means for the spec and for libhddvd:**

1. The Archive.org ISOs match §9.6: DumpHD or BackupHDDVD was run, packs decrypted
   in place, `ANY!`/`AAC!` trees left on the image. A player reading these needs
   **no** AACS code.
2. For a real disc, the reusable path is: get the Volume ID (`dumpvid` / MMC `80h`),
   derive VUK (`aacskeys` or libaacs crypto core per §9.9), unwrap the VTKF title key
   (§9.3), then per-EVOBU `Kc = AES-G(Kt, Dtk || CPI_lsb_96)` (§9.6). Every step has
   an open-source reference implementation predating this project.
3. Only the **CPI byte offset** (§9.6) is undocumented in public *specs*, but DumpHD
   and BackupHDDVD's decrypt paths embody it in code. If that offset is ever needed
   as a spec fact, **their source is where it is recoverable**, not this ISO corpus.
   `[9, 12]`

## 9.11 Full decrypt flow: from BackupHDDVD source (verbatim facts for the C port)

`[9]`
**VERIFIED** against the AACS book §4.3.2 and a real NV_PCK.

These are the two constants and the loop the book does not spell out. libhddvd (or a
libaacs port) needs exactly these.

### AES-G (the AACS one-way function)
```
AES_G(k, x)  =  AES-128-ECB-DECRYPT(k, x)  XOR  x       # 16-byte block
```
i.e. ECB **decrypt** of x under key k, then XOR the plaintext-in with the result.
(`AESFunc.AESG`: `Cipher "AES/ECB/NoPadding"`, DECRYPT_MODE, then `xor(out, x2)`.)

### Pack CBC decryption
```
Kc  = AES_G(Kt, Dtk || CPI_lsb_96)                      # 16 bytes
plain[128..2047] = AES-128-CBC-DECRYPT(Kc, cipher[128..2047])
IV  = 0BA0F8DDFEA61FB3D8DF9F566A050F78                   # FIXED AACS constant, 16 bytes
```
The IV is **constant**, not per-pack (`AESFunc.AESCBCConstantIV`). The 128-byte
Unencrypted Portion is copied through untouched; only bytes 128..2047 (1920) are CBC.

### Field sources within a pack
```
Dtk        = pack[84..87]          (4 bytes)            EVOBPack: keySeed[0..3]
CPI        = pack[0x3C .. 0x3C+15] (16 bytes, in NV_PCK's GCI packet)
CPI_lsb_96 = CPI[4..15]            (12 bytes)            keySeed[4..15]
KEY_VF     = CPI[0] & 0x80                               (0 => EVOBU not encrypted)
TITLE_KEY_PTR = CPI[2]                                   selects Kt among title keys
```

### EVO decrypt driver (per EVOB file)
```
current_CPI = zero16 ; current_ptr = 0
for each 2048-byte pack in file order:
    if pack is NV_PCK (pack[0x2A]=00 pack[0x2B]=01 pack[0x11]=0xBB pack[0x2C]=0xBF):
        current_CPI = pack[0x3C .. 0x3C+15]
        current_ptr = current_CPI[2]                     # TITLE_KEY_PTR
        # NV_PCK is never encrypted; emit as-is (the tool also zeroes CPI@0x3C,0x48
        #   in its output so re-muxed streams look clear (cosmetic, optional)
    else if PES_scrambling_control (pack[20] bits 5-4) == 01b:
        Kt = title_keys[current_ptr]
        Kc = AES_G(Kt, pack[84..87] || current_CPI[4..15])
        pack[128..2047] = AES-128-CBC-DECRYPT(Kc, pack[128..2047], IV=const)
        clear pack[20] scrambling bits (& 0xCF)
    emit pack
```
The CPI that governs an EVOBU's encrypted packs comes from that EVOBU's **NV_PCK**
(first pack), latched and applied to following packs until the next NV_PCK.

### libaacs mapping (what an implementer changes)
- `AES_G` == libaacs `crypto_aesg` family (`crypto.h`); reuse.
- CBC step: libaacs' BD path uses a per-unit derived IV over a 6144-byte unit;
  HD DVD uses the **fixed IV above** over a **1920-byte** region of a 2048-byte pack.
  This is a new decrypt routine, not a parameter tweak to `aacs_decrypt_unit`.
- Key indexing: `title_keys[TITLE_KEY_PTR]` from VTKF (§9.3), not BD's CPS-unit map.
- Nothing here needs a disc: for an already-decrypted ISO (this corpus, §9.6) the
  scrambling bit is 0 and this whole branch is skipped.

## 9.12 How EVO "decryption" is actually done, and what applies here

Two different operations are both loosely called "extracting the EVO"; keep them apart.

### (a) Copy the EVO out of the disc: no keys, always possible
Reading `HVDVD_TS/*.EVO` off the UDF volume is a plain file copy (`tools/udfgrab.py`).
The **navigation** layer (UDF, IFO/VTI, MAP, NV_PCK/DSI, playlist) is never
encrypted, so title enumeration, seeking, and stream routing (§8.7) work on any disc
with no keys. This is all this project needs, and all it does.

### (b) Decrypt the AACS-scrambled payload inside the packs
Only the 1920-byte Encrypted Portion of packs marked `PES_scrambling_control=01`
is ciphertext. The ladder (AACS HD DVD Pre-recorded Book [4] + §9.6/§9.11):

```
device/processing key  --process-->  MKBROM.AACS        -> Media Key  Km
Km  XOR-AES-G  Volume ID (from the DRIVE, MMC 80h; not in any ISO)  -> Kvu
Kvu  --AES-128D-->  VTKF entry[TITLE_KEY_PTR]           -> Title Key  Kt
per encrypted pack:  Kc = AES-G(Kt, Dtk || CPI_lsb_96)  (Dtk=pack[84:88], CPI@0x3C)
                     plain[128:2048] = AES-128-CBC-D(Kc, cipher, IV=0BA0..0F78)
```

**How "people" did it (2007, all open):** `muslix64` (BackupHDDVD) and `arnezami`
recovered the AACS **device/processing keys** by reading a running software player's
memory, famously the processing key `09 F9 …`. With those keys plus the Volume ID
(captured from the drive via `dumpvid`, or shipped in a community `KEYDB.cfg`), the
ladder above runs end to end. Tools: `BackupHDDVD`, `dumphd`, `aacskeys`; keydb
mirrors (`fvonline-db.bplaced.net`, `vlc-aacs.whoknowsmy.name`) distribute the
recovered per-disc keys. `[16]`

### Can we do it here, with what we know?
- **For this corpus: nothing to do.** The ISOs are already stripped (packs clear,
  §9.6, e09). We already read the EVO payload directly; that is why §8.7's stream
  census and e10's seek worked with no keys.
- **For a real encrypted disc:** the *format and the pack math are fully specified
  and verified* (against BackupHDDVD's `EVOBPack.java` and the AACS book), so a
  player that already holds a Title Key can decrypt a pack with the code in §9.11.
  What this specification deliberately does **not** define, by design, is the
  **AACS device/processing keys** or a key-recovery routine. Those are the licensed
  secret, they come from a drive/player or a public keydb, not from us. The Volume ID
  likewise is not in an ISO; it needs the physical drive (§9.7).

**Bottom line:** the knowledge here is complete enough to *decrypt a pack given a
key*, and to drive `libaacs` (extended per §9.9) for the whole ladder, but obtaining
the keys is external, and for the archived corpus it is moot because the packs are
already clear.

## 9.13 Sequence Key (SKB / SKF): format closed, 0/120 discs

Previously "OPEN, player SK path". The AACS book [4] Chapter 3.4 / 7 fully defines it;
no disc in this corpus uses it (`SKB.AACS` / `SKF.AACS` are 0/120), so it is
format-documented but not corpus-exercised. Needed only for titles that carry a
Sequence Key Section (studio traitor-tracing variants), which this corpus does not.

**`SKBF` (`SKB.AACS`)** (Table 3-4 [4]): `SKBF_ID` = `"DVD_HD_VSKBF"` (12 B),
`VERN` u16 (=0), six `SKB_SIZE#1..6` (4 B each = L#n), 10 B reserved, then six
variable SKBs (record order: Verify-Media-Key, Nonce, Calculate-Variant-Data,
optional Conditional records, End-of-SKB). Processing one SKB yields a Volume
Variant Unique Key `Kvvu[j]` and a 10-bit Segment Key Unit Number `SKUN[j]`
(0–1023); six SKBs → `Kvvu[1..6]`, `SKUN[1..6]`.

**`SKF` (`SKF.AACS`)** (Table 3-5 [4]): `SKF_ID` = 12-byte ASCII, `HDV_SKF_SIZE`
u32, reserved, `VERN` u32, then **six Segment Key Groups (SKG)**, each **1024
Segment Key Units (SKU)**, each SKU = 32 encrypted (SEG_NO, 16-byte Segment Key)
pairs. For group `j`, `SKU #SKUN[j]` is decrypted with `Kvvu[j]` → a 32-entry
Segment Key Table (SKT) for that Segment Key Range (a set of P-EVOBs).

**Playback path** (Chapter 7 [4]): inside a Sequence Key Section, `SEG_KEY_PTR` in
the EVOBU's CPI (§9.6) selects the segment key; the content key becomes
`Kc = AES-G(SEG_KEY*, Dtk || CPI_lsb_96)` instead of the title-key form. If
`SEG_KEY_PTR` is valid but the SKB/SKF are absent, the pack is treated per the
title-key path. `[4]` **format VERIFIED (book)**; corpus N=0 (no SKB/SKF).

## 9.14 Empirical decrypt: the one step not reproducible here

The pack decrypt (§9.6/§9.11) is verified against BackupHDDVD source [9] and the AACS book [4], but **cannot be re-verified end-to-end from the reference corpus**. Those images are AACS-stripped (§9.6), so there is no ciphertext pack, and a real disc's `Kvu` needs the drive's Volume ID (§9.7). Redump [22] preserves encrypted HD DVD dumps together with their per-disc keys (MKB, Media Key, Volume ID, VUK, Unit-Key-File hash). That confirms both the key set required and that Volume ID is a drive/BCA value. Redump is a preservation database, not a public file host. The decrypt is **specified and externally validated**. An empirical run needs a pristine image plus its keys (Redump) or a licensed drive. This is a hard boundary of material availability, not a gap in the format.