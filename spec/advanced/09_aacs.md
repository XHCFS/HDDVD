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
| `DKF.AACS` | 64 | Directory Key File. Persistent-storage name, not title key |
| `VTKF$$$.AACS` | 2480; 2516 on two Pan’s files | Title Key File for `VPLST$$$.XPL` |
| `VTUF$$$.AACS` | 144 | Title Usage File (CCI). Same `$$$` as VTKF |
| `CONTENT_CERT.AACS` | 120 | Content certificate |
| `CONTENT_HASH_TABLE1.AACS` / `2` | varies | 208 listed (104+104); sizes not a closed stride (44 676 …). **Bodies not saved; uncloseable** |
| `CONTENT_REVOCATION_LIST.AACS` | usually 1e6; 61440 on Pan’s | revocation |
| `MNGCPY_MANIFEST.XML` | ~200–304 | Managed Copy; not playback |

`ATKF` / `SKF` / `APLST`: **0/120**.

## 9.3 VTKF: Table 3-8 (Final 0.953)

Size the table from `HD_VTKF_SIZE`, do not assume 2480.

| Offset | Size | Field |
|---|---|---|
| 0 | 12 | `TKF_ID` = `"DVD_HD_V_TKF"` |
| 12 | 4 | `HD_VTKF_SIZE` |
| 16 | 12 | `PLAYLIST_NAME` = `VPLST%%%.XPL` |
| 28 | 4 | reserved |
| 32 | 4 | `VERN` shall be 0 |
| 36 | 92 | reserved |
| 128 | n×36 | Title Key Entry |
| size−48 | 32 | reserved |
| size−16 | 16 | TKF MAC = CMAC(`Kvu`, bytes 0 .. size−17) |

Nominal: 128 + 64×36 + 32 + 16 = **2480**.  
Pan’s VTKF001/003 = 2516 = 65 slots. Book/Scenarist cap is 64.

### Title Key Entry (36 bytes)

| Off | Size | Field |
|---|---|---|
| 0 | 1 | `BIFO`. Bit 7 `AV_FLG` = slot occupied |
| 1 | 3 | reserved |
| 4 | 16 | `Kte` (encrypted title key) |
| 20 | 16 | Binding MAC. `BIND_TYPE=000b` → `0xFF`×16 (Volume ID only) |

Match `PLAYLIST_NAME` to the **active** `VPLST$$$.XPL` (including after
`IPlaylist.load`). Do not use a foreign VTKF.
Empty slots are skipped, not terminators. `TITLE_KEY_PTR` is **1-based** (1…64).

A 32-byte stride is a known misparse. Do not use it.

Three titles have extra VTKF files without a matching VPLST (`BALLS_OF_FURY`,
`CHUCK_AND_LARRY`, `SHREK_THE_THIRD_EU`).

## 9.4 DKF (64 bytes): Table 6-2

Magic `DVD_HD_V_DKF`. Encrypted directory key at offset 48:
`KDIRe = AES-128E(Kvu, KDIR)`. Not used to decrypt EVO.

## 9.5 CONTENT_CERT (120 bytes): Table 3-17

| Off | Size | Field |
|---|---|---|
| 0 | 1 | type `00h` |
| 1 | 1 | bit 7 = bus encryption enabled (`BEE`) |
| 40 | 20 | CHT #1 digest |
| 60 | 20 | CHT #2 digest |
| 80 | 40 | signature |

Integrity / bus-encryption advertisement, not a title key.
`MATRIX_REVOLUTIONS` `CONTENT_CERT.AACS`: type `00h`, BEE bit 7 = **0**.
Archive.org ISOs are not bus-encrypted; a software ISO player ignores BEE.
`[11]` **SINGLE**

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
**pack byte 0x3C (60)**, inside the GCI packet (`0x000001BF` at 0x2A, substream at
0x2C). Confirmed byte-for-byte against a real disc: the nav-pack signature
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

Table 4-1 / 4-2 (once located):

| CPI bytes | Field |
|---|---|
| 0 | `KEY_VF` in bits 7–6: `00` neither, `01` segment key, `10` title key, `11` reserved |
| 1–2 | `TITLE_KEY_PTR` (1…64) when `KEY_VF=10b`; else 0 |
| 3 | `SEG_KEY_PTR` when `KEY_VF=01b`; else 0 |
| 4–7 | `CH_PTR` (CHT #1 entry, 1…500000) |
| 8–9 | URMI |
| 10–11 | CCI_SS |
| 12–13 | CCI |
| 14–15 | reserved `00` |

`KEY_VF=00b` → do not decrypt that EVOBU.

Blu-ray `aacs_decrypt_unit` (6144-byte TS aligned unit) **does not apply**.
Reusable: MKB walk, AES-G, `Kvu = AES-G(Km, VolumeID)`, `Kt = AES-128D(Kvu, Kte)`.

## 9.7 Volume ID

BCA + Lead-in. MMC `READ DISC STRUCTURE` format **`80h`**, after AACS drive
authentication. Not `DISCID.DAT@12`. This ISO corpus cannot yield `Kvu`.

## 9.8 VTUF (144 bytes)

Sample: `MYSTERY_MEN` `ANY!/VTUF000.AACS` (only VTUF saved). Magic
`DVD_HD_V_TUF`. Usage rules / CCI, not `Kc`. Book Table 3-10 (URS_NUM at **16**,
HASH_SIZE **17–20**, VERN **21–22**, PLAYLIST_NAME **23–34**). When `URS_NUM=0`
there is **no** usage-rule body; TUF MAC starts at **128**.

Do not use `spec/clean/09_AACS.md` “name at 0x18”. That dump folded `'V'` into
the preceding field. Disc + book agree on **23**.

| Offset | Size | Field |
|---|---|---|
| 0 | 12 | `URF_ID` = `"DVD_HD_V_TUF"` |
| 12 | 4 | `HD_VURF_SIZE` = 144 |
| 16 | 1 | `URS_NUM` | `0` on the sample |
| 17 | 4 | `HASH_SIZE` | `128`; hash covers bytes 0–127 |
| 21 | 2 | `VERN` / reserved | `0` |
| 23 | 12 | `PLAYLIST_NAME` | `"VPLST000.XPL"` |
| 35 | 93 | reserved | 0 |
| 128 | 16 | TUF MAC | CMAC(`Kvu`, bytes 0..127) |

Book Table 3-12 URS / BURS layout applies only when `URS_NUM>0`. **No such
body in this corpus:** 217/217 listed `VTUF$$$.AACS` (primary tree, not BAK)
are **144 bytes**. A non-zero URS list would grow the file. Layout of
`URS_NUM>0` is therefore **uncloseable** here (book-only).
`[11, 12]` **VERIFIED** (absence).

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