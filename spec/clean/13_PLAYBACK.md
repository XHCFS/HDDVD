# Playback sequence

What a player does after insert. Theorized from patents and AACS books, then checked
against discs. Firmware binaries have **not** been reverse-engineered. The catalog
http://hd-dvd.org/firmware.html is the live index of player/drive update images
(`http://hd-dvd.org/files/firmware/`). It is **intermittent** (HTTP 200 with
matching zip/iso sizes, then 503, both on 2026-09-08). Wayback copy:
https://web.archive.org/web/20231210144123/http://hd-dvd.org/firmware.html
OEM notes on that page do not confirm FIG.50 (no `VPLST` / `DISCID` / `ADV_OBJ`).

Confidence: **VERIFIED** where a disc or experiment agrees · **PATENT** where only
the book/figure exists · **OPEN** where we have not looked.

---

## A. Insert → category (all discs)

```
mount medium
    │
    ├─ HD DVD?          PATENT FIG.7 S11   OPEN how (UDF 2.50 + HVDVD_TS works in practice)
    │
    ├─ ADV_OBJ/VPLST*.XPL present?
    │      yes → Category 2 or 3 → section B
    │      no  → read VMGI (HVDVD-VMG100) → Category 1 → section D
    │
    └─ neither → player-defined failure
```

`[SRC: PATENT | US20070091495A1 FIG.7]`
`[SRC: CORPUS | 119 yes / 1 no / 0 Category 3]`

Audio-only players search `APLST###.XPL` instead of `VPLST`. **0** `APLST` in this
corpus. `[SRC: PATENT | FIG.8]` `[SRC: CORPUS | e07]`

---

## B. Advanced Content startup (Category 2) — patent FIG.50

Verbatim structure from US20070091495A1 “Startup Sequence of Advanced Content”.
Disc filenames use `VPLST$$$.XPL` / `ADV_OBJ`, not the patent’s `VPLIST.XML`.

```
1. Read ADV_OBJ/DISCID.DAT
      PROVIDER_ID, CONTENT_ID, SEARCH_FLG
      → locate persistent-storage directory for this disc

2. Display Mode (system parameter)
      display connected → VPLST search
      audio-only        → APLST search

3. VPLST search
   3-1. if SEARCH_FLG == 0: search persistent storage for VPLST$$$.XPL (000–999)
        if SEARCH_FLG == 1: skip
   3-2. search ADV_OBJ/ (not subdirs) for VPLST$$$.XPL
   3-3. if none → APLST search / failure
   3-4. **open the file with the highest $$$**

4. Change system configuration
      StreamingBuffer size from Playlist/Configuration
      wipe File Cache + streaming buffer

5. Initialize Title Timeline + chapters for the first title
      object mapping (clips on the timeline)
      playback sequence (Chapter titleTimeBegin)

6. Prepare first title
      File Cache Manager loads Manifest, markup, script, fonts, images,
      and any TMAP needed before start
      init Primary Video Player / Secondary Video Player / Advanced Application engine
      Primary Video Player is told IFO/VTI + TMAP(s) for Primary Audio Video

7. Start Title Timeline
      objects mapped onto the timeline present according to schedule

8. Failure: no VPLST and no APLST → player-defined
```

`[SRC: PATENT | US20070091495A1 FIG.50 numbered steps 1–9]`
`[SRC: TOOL | Scenarist “The highest-numbered Playlist is loaded first when a player starts up.”]`
`[SRC: CORPUS | e07 | 119/119 Advanced discs have numbered VPLST]`

### B.1 What “first title” means

Inside the **loaded** playlist (XSD `TitleSet`):

1. If `FirstPlayTitle` exists, that clip plays first (often a logo). No `titleNumber`.
   119 of 247 playlists have one. `[SRC: CORPUS | e07]` `[SRC: XSD | FirstPlayTitle]`
2. Then `Title` elements in document order, `titleNumber` 1…n.
   `onEnd` is an IDREF to another title (3192/3196 titles set it).
3. `PlaylistApplication` runs in parallel (HDi). 203 playlists have one.

### B.2 Highest playlist ≠ feature (disc vs patent)

Patent: always load max `$$$`. Three discs use that file as a **language selector**:

| Disc | Highest | What it contains | Then |
|---|---|---|---|
| `MATRIX_REVOLUTIONS` | 099 | `PlaylistApplication` → `selector.aca/manifest.xmf`; **no** MAP clips | script `Player.playlist.load(VPLST000 or VPLST001)` by `Player.menuLanguage` |
| `BLADE_RUNNER` | 002 | app-only, 989 B | same pattern (`selector.aca` listed) |
| `TRAINING_DAY` | 003 | app-only, 822 B | same |

`[SRC: DISC | MATRIX VPLST099.XPL + selector.aca/script.js UTF-16BE]`
**VERIFIED** (1 disc body + 2 listings).

116/119 highest playlists **do** contain `PrimaryAudioVideoClip`.

**Library contract (you decide, document it):**

- `hddvd_boot_playlist()` — spec: highest `VPLST$$$` (FIG.50).
- `hddvd_feature_playlists()` — every XPL that has a MAP clip (usable without HDi).
- Optional later: execute selector script / `IPlaylist.load`.

A VLC module that only wants “play the movie” uses the feature playlist, not 099.

### B.3 Seek

Time is `HH:MM:SS:FF` on a `TitleSet@timeBase` of `60fps` (247/247).
`[SRC: CORPUS | 04 addendum]`

```
title time T
    → Chapter titleTimeBegin (optional UI)
    → find PrimaryAudioVideoClip where titleTimeBegin ≤ T < titleTimeEnd
    → local time = T − titleTimeBegin + clipTimeBegin
    → walk EVOBU_ENT in the MAP (byte offset TMAPI_SA, usually 416)
    → sum EVOBU_SZ packs until playback time covers local time
    → file offset = that pack count × 2048 in the sibling .EVO
```

`EVOBU_SZ` sum equals EVO pack count on DOWNFALL. TABLE 83 figure is 13-bit `EVOBU_SZ`.
First five DOWNFALL EVOBUs: MAP size = `DSI.vobu_ea+1` and `DSI.nv_pck_lbn` = walk
position **5/5**. MYSTERY_MEN VOBU0: 81 = `vobu_ea+1`.
`[SRC: DISC | 06_TMAP_solved.md + 08_NV_PCK_PCI_DSI.md]`
**VERIFIED** on Advanced content.

`seamless="true"` on a following clip (Matrix `PEVOB` → `PEVOB_Divide`) is a
connection condition for the decoder, not a second MAP format.

### B.4 HDi runtime (later)

After File Cache load:

- Manifest points at Script + Markup + Resource.
- Markup is a small document engine (`iHD.xsd`): `root`, `cue`, focus, `event`.
- Script talks to `Player.playlist` (`load/play/pause/stop/fastForward/…`),
  `Player.track.selectSubtitleTrackNumber`, `Player.generalParameters`,
  `Player.menuLanguage`. `[SRC: SRCCODE | iHD_Scripting_API.txt IPlaylist]`
  `[SRC: DISC | 1408 script.js; MATRIX selector.aca/script.js]`

Firmware should match this API. **Not compared yet.**

Soft reset / playlist update: patent FIG.51 (`IPlaylist.load` / Soft Reset API).
Used when a selector replaces 099 with 000.

---

## C. AACS relative to playback

Navigation XML/MAP/VTI/NV_PCK headers are readable without keys.
Encrypted **packs** (not NV_PCK/ADV_PCK): bytes 0–127 clear, 128–2047 CBC.
`Kc = AES-G(Kt, Dtk || CPI_lsb_96)`. `Dtk` pack 84–87. CPI in GCI (`NV_PCK` `0x04`).
Title key from VTKF matching the **active playlist filename**.
Volume ID: BCA + Lead-in, not the ISO.

Compliant boot also walks MKBROM, CERT, CHT (`09` Q7–Q8). A research demuxer
can skip integrity and still locate packs. A licensed player shall not.

`[SRC: SPEC | Final 0.953 Tables 3-8, 4-7, §3.9]`
**Do not put a decryptor in this repository.**

```
(optional, if ANY! or AAC! present)
    read MKBROM → Media Key
    Volume ID from drive → Kvu
    VTKF for this VPLST$$$ → Kt
    each encrypted pack → Kc → CBC payload
Primary Video Player still sees a 2048-byte MPEG-2 PS
```

libaacs `aacs_decrypt_unit` is the wrong unit. Reuse MKB walk + AES-G only.

---

## D. Standard Content (Category 1) — 1 disc

```
HV000I01.IFO  (VMGI)
    FP_PGCI → first play PGC (JumpTT 15 on RESERVOIR_DOGS)
    TT_SRPT → titles
    VMGM / VTSM PGC + nav commands (word rotated 16 bits vs DVD)
    cell_playback → EVOB sectors
    NV_PCK PCI/DSI for buttons/seek inside the PGC
```

`[SRC: DISC | RESERVOIR_DOGS | 01, 02, 08]`
**SINGLE.** Menu PGCI bodies unread. Set-command operands **known wrong**.

Category 3 would allow jumps between Advanced and Standard state. **Never seen.**

---

## E. Pack path into a demuxer

A player that already demuxes MPEG-2 program streams consumes HD DVD video like this:

```
open volume (ISO or drive)
classify category
select playlist / title
time → MAP EVOBU_ENT → sibling .EVO byte offset
read N × 2048-byte packs
    → MPEG-2 PS demuxer (pack start 00 00 01 BA every 2048)
optional: decrypt ES payload (Volume ID from drive)
optional: surface XPL, ACA, markup for the HDi engine
```

The playlist model is closer to Blu-ray MPLS than to DVD PGC. Do not wrap DVD nav.
Do not feed 6144-byte BD aligned units. AACS unit decrypt for BD TS does not apply.

---

## F. Adversarial checks on this flowchart

| Question | Answer |
|---|---|
| Does FIG.50 match retail filenames? | Yes after drift: `VPLST$$$.XPL`, `ADV_OBJ`, `DISCID.DAT`. |
| Must we run HDi to play video? | No on 116/119 discs if we skip the highest-if-app-only rule and open a clip-bearing XPL. Yes for the 3 selector discs if we insist on spec boot. |
| Is `DISCID.DAT` Volume ID? | No. |
| Is FirstPlayTitle the boot playlist? | No. Boot is highest XPL; FirstPlayTitle is the first clip *inside* that XPL (or the loaded one). |
| Can we seek from XPL chapters only? | Yes for UI; accurate pack seek still needs MAP `EVOBU_ENT`. |
| Does firmware confirm FIG.50? | **UNCLOSEABLE.** Catalog http://hd-dvd.org/firmware.html is live-but-flaky (200/503); blobs at `/files/firmware/` are not RE’d. OEM notes = HDMI/network/pause, not playlist boot. FIG.50 vs XPL: see spec/advanced/10_playback.md §10.7. |

---

## G. What this spec already specifies vs what it cannot

| Specified (enough to walk a disc) | Not specified (needs more evidence) |
|---|---|
| UDF 2.50, roots, category | Official “is this HD DVD?” probe |
| XPL titles/chapters/clips; highest-VPLST boot; 3 selector exceptions | HDi markup/script execution; firmware vs FIG.50 (**uncloseable**) |
| MAP `EVOBU_ENT` → EVO pack offset; matches DSI | ILVU angle walk beyond Pan’s four maps |
| NV_PCK = GCI+PCI+DSI; PCI/DSI GI; CPI at pack `0x3C` | PCI HLI, DSI tail, ADV_PCK dump |
| ATRI `V_ATR`/`AST_Ns`/`SP_Ns`; EVOBI name + pack count + serial | ATRI palettes; EVOBI+282 units |
| AACS pack split, VTKF, BAK; Volume ID is not in the ISO | Drive `READ DISC STRUCTURE` 80h; CHT bodies; VTUF `URS_NUM>0` |
| ACA header + variable directory (`14+namelen+32`) on 4 files | ACA AACS-sidecar internals; `.CER` bodies |
