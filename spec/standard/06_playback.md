# S6. Playback sequence (Category 1)

*The structure is from patent [1] (FIG.7, FIG.147, FIG.99); disc behaviour is from
`RESERVOIR_DOGS` [11]. The VM execution model is DVD-Video's, per libdvdnav.*

## 6.1 Boot

```
mount UDF 2.50 volume
      |
      +- ADV_OBJ/VPLST$$$.XPL present?  -- yes --> Advanced startup (Category 2 or 3)
      |                                             (Advanced sheet 10)
      +- no --> read HV000I01.IFO
                    ID == "HVDVD-VMG100" ?  -- yes --> Category 1, continue below
                                            -- no  --> player-defined failure
```
`[SRC: PATENT | US20070091495A1 FIG.7, FIG.147]` `[11]` **VERIFIED** as a classifier (1
Category 1 disc, 119 Advanced, 0 mixed).

Patent FIG.147 [3]: on a type-1 disc the player runs "Playback disc of content type 1",
which is the DVD-Video state machine below. There is no startup file, no player-system
configuration step, and no advanced-navigation load; those belong to the type-2 and
type-3 branch.

## 6.2 First-play, title, and menu (the VM state machine)

1. First-play PGC. `VMGI_MAT.FP_PGCI_SA` ([§2.3](02_vmgi.md)) points at the FP_PGC,
   whose command runs immediately. On the specimen it is `JumpTT 15`, a jump to title
   15 (a warning or logo clip in VTS 11). `[11]` **SINGLE**.
2. Title resolution. `JumpTT n` (or `JumpVTS_TT`) indexes `TT_SRPT`
   ([§2.2](02_vmgi.md)) to `(VTSN, VTS_TTN, start sector)`, and the target VTS IFO is
   opened.
3. PGC playback. The title's PGC ([§4.1](04_pgc_vm.md)) plays its programs and cells in
   order. Pre-commands run before the PGC, post-commands after, and each cell may carry
   a cell command. On the specimen the feature PGC's post-command is `CallSS VTSM`,
   which calls the VTS menu on end. `[11]` **SINGLE**.
4. Menus. The VMG menu (`VMGM_PGCI_UT`, object `HV000M02.EVO`) and VTS menus
   (`HDVTSM_PGCI_UT`, object `HVnnnM01.EVO`) are themselves PGCs, selected by language
   unit and menu type. Buttons come from the NV_PCK PCI HLI and the GU graphics
   ([§5.5](05_evob_nv.md)); pressing a button runs its VM button command.
5. Navigation. `Link*`, `Jump*`, `Call*`, `Resume`, `SetSystem` (audio, subp, angle,
   SPRM), and `Set` and `Compare` (GPRM) drive transitions, exactly as in DVD-Video with
   the 16-bit command rotation ([§4.3](04_pgc_vm.md)).

`[SRC: PATENT | US20070091495A1 FIG.99]` `[11]` `[SRCCODE: libdvdnav src/vm/vm.c]`
**SINGLE** for the specimen's specific chain.

## 6.3 Seek

Time-based seek within a title uses `VTS_TMAPT` and then the in-stream DSI, per
[§5.6](05_evob_nv.md). Chapter (PTT) jumps use `VTS_PTT_SRPT` to get `(pgcn, pgn)`, then
`program_map` to reach the first cell of that program. All of this is DVD-Video.
**VERIFIED** (TMAPT durations match; PTT counts match program counts).

## 6.4 Relationship to a player implementation

A DVD-Video player built on libdvdread and libdvdnav ports to Standard Content with a
bounded set of changes, all documented in this set:

- UDF 2.50 metadata-partition mount, via libudfread ([§1.1](01_volume.md)).
- New ID strings; VMGI_MAT with 2 inserted fields; TT_SRPT 12 to 16 bytes; VTS_PGCIT SRP
  8 to 12 bytes; the PGC with two palettes and a reordered header; cell_playback 24 to
  28 bytes ([§2](02_vmgi.md) through [§4](04_pgc_vm.md)).
- The VM command word rotated right 16 bits at load ([§4.3](04_pgc_vm.md)).
- EVO as 2048-byte MPEG-2 PS with HD codecs (VC-1, AVC, DD+, TrueHD, DTS-HD) handed to
  the codec layer ([§5](05_evob_nv.md)).
- AACS overlay instead of CSS ([§7](07_aacs.md)).

This is a smaller delta than Advanced Content, which replaces the entire navigation
model. It is documented here for completeness. It is not on the product path, because
the retail corpus contains one such disc.
