# S6. Playback sequence (Category 1)

*Structure from patent [1] FIG.7/FIG.147/FIG.99; disc behaviour from `RESERVOIR_DOGS`
[11]. The VM execution model is DVD-Video's [SRCCODE: libdvdnav].*

## 6.1 Boot

```
mount UDF 2.50 volume
      │
      ├─ ADV_OBJ/VPLST$$$.XPL present? ── yes ─→ Advanced startup (Category 2/3)
      │                                          (Advanced §10)
      └─ no ─→ read HV000I01.IFO
                    ID == "HVDVD-VMG100" ?  ── yes ─→ Category 1, continue below
                                            ── no  ─→ player-defined failure
```
`[SRC: PATENT | US20070091495A1 FIG.7, FIG.147 "Content type 1?"]` `[11]` **VERIFIED**
as a classifier (1 Category-1 disc, 119 Advanced, 0 mixed).

Patent FIG.147 [3]: on a type-1 disc the player runs "Playback disc of content type 1"
— i.e. the DVD-Video state machine below. There is no startup file, no player-system
configuration step, and no advanced-navigation load (those are the type-2/3 branch).

## 6.2 First-play → title → menu (the VM state machine)

1. **First-play PGC** — `VMGI_MAT.FP_PGCI_SA` ([§2.3](02_vmgi.md)) points at the FP_PGC.
   Its command runs immediately. On the specimen it is **`JumpTT 15`** — jump to title
   15 (a warning/logo clip in VTS 11). `[11]` **SINGLE**.
2. **Title resolution** — `JumpTT n` (or `JumpVTS_TT`) indexes `TT_SRPT`
   ([§2.2](02_vmgi.md)) → `(VTSN, VTS_TTN, start sector)`. The target VTS IFO is opened.
3. **PGC playback** — the title's PGC ([§4.1](04_pgc_vm.md)) plays its programs/cells in
   order. Pre-commands run before the PGC, post-commands after; each cell may carry a
   cell command. Example: the feature PGC's post-command is **`CallSS VTSM`** — call the
   VTS menu on end. `[11]` **SINGLE**.
4. **Menus** — VMG menu (`VMGM_PGCI_UT`, object `HV000M02.EVO`) and VTS menus
   (`HDVTSM_PGCI_UT`, object `HVnnnM01.EVO`) are themselves PGCs, selected by language
   unit and menu type. Buttons come from NV_PCK PCI HLI + GU graphics
   ([§5.5](05_evob_nv.md)); pressing a button runs its VM button command.
5. **Navigation** — `Link*`/`Jump*`/`Call*`/`Resume`, `SetSystem` (audio/subp/angle,
   SPRM), `Set`/`Compare` (GPRM) drive transitions, exactly as DVD-Video with the
   16-bit command rotation ([§4.3](04_pgc_vm.md)).

`[SRC: PATENT | US20070091495A1 FIG.99 "Advanced VTS playback init" (analogue) ]`
`[11]` `[SRCCODE: libdvdnav src/vm/vm.c]` **SINGLE** for the specimen's specific chain.

## 6.3 Seek

Time-based seek within a title uses `VTS_TMAPT` then in-stream DSI, per
[§5.6](05_evob_nv.md). Chapter (PTT) jumps use `VTS_PTT_SRPT` → `(pgcn, pgn)` →
`program_map` → first cell of that program. All DVD-Video. **VERIFIED** (TMAPT
durations match; PTT counts match program counts).

## 6.4 Relationship to a player implementation

A DVD-Video player (libdvdread + libdvdnav) ports to Standard Content with a bounded
set of changes, all documented in this set:

- UDF 2.50 metadata-partition mount (libudfread) — [§1.1](01_volume.md).
- New ID strings; VMGI_MAT +2 inserted fields; TT_SRPT 12→16; VTS_PGCIT SRP 8→12;
  PGC palette ×2 and reordered header; cell_playback 24→28 — [§2](02_vmgi.md)–[§4](04_pgc_vm.md).
- VM command word rotated right 16 bits at load — [§4.3](04_pgc_vm.md).
- EVO = 2048-byte MPEG-2 PS with HD codecs (VC-1/AVC + DD+/TrueHD/DTS-HD) handed to the
  codec layer — [§5](05_evob_nv.md).
- AACS overlay instead of CSS — [§7](07_aacs.md).

This is a genuinely smaller delta than Advanced Content (which replaces the entire
navigation model). It is documented here for completeness; it is **not** on the product
path, because the retail corpus contains one such disc.
