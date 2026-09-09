# S9. References

The Standard Content set shares its numbered sources with the Advanced set, so the
citation numbers match across both. The full reference list with live links is
[Advanced sheet 13](../advanced/13_references.md). The entries this set relies on are
repeated here for convenience, followed by the specific Standard-Content patent figures.

## Sources cited in this set

- **[1]** Toshiba, *Information playback system using information storage medium*,
  US 2007/0091495 A1. Disc categories and the Standard-versus-Advanced split (FIG.2,
  FIG.4, FIG.5, FIG.7), Standard Content data structure, boot (FIG.50, FIG.147),
  maximum 511 VTS. <https://patents.google.com/patent/US20070091495A1/en>
- **[2]** Toshiba, *Information storage medium, information reproducing apparatus and
  method*, US 2008/0298219 A1. Byte-level RBP tables for VMGI_MAT and VTSI_MAT; stream
  ID tables 45 through 47; NV_PCK tables 50 through 52.
  <https://patents.google.com/patent/US20080298219A1/en>
- **[3]** Toshiba, WO 2006/070920 A1. The Standard-Content drawing set: HDVMGI (FIG.3
  through FIG.19), HDVTSI (FIG.20, FIG.21), menu PGC category (FIG.8, FIG.27), PGCI and
  the command VM (FIG.33), the graphics decoder (FIG.39), the Graphics Unit and button
  HLI (FIG.45), VTSI/PGC/PTT/Cell/EVOB/ILVU mapping (FIG.69, FIG.93, FIG.94), plane
  composition (FIG.102, FIG.144). Page-by-page reading in
  [`spec/clean/16b_WO_FIGURE_INDEX.md`](../clean/16b_WO_FIGURE_INDEX.md).
  <https://patents.google.com/patent/WO2006070920A1/en>
- **[4]** AACS LA, *Advanced Access Content System, HD DVD and DVD Pre-recorded Book*,
  Final Revision 0.953. Pack encryption and CPI tables.
  <https://aacsla.com/aacs-specifications/>
- **[11]** *HD-DVD Archive* series 1 through 12, 120 retail HD DVD images read over HTTP
  range with `tools/udfgrab.py`. The single Category 1 disc is `RESERVOIR_DOGS`
  (series 3). <https://archive.org/details/hd-dvd_archive_01>
- **[12]** Verification experiments `e01` through `e20` accompanying this repository
  (`experiments/run.py`).

## Reference implementations (delta sources)

- libdvdread, `ifo_types.h` and `ifo_read.c`: the DVD-Video structures this format
  extends. <https://code.videolan.org/videolan/libdvdread>
- libdvdnav, `src/vm/vm.c` and `src/vm/vmcmd.c`: the navigation-command VM that becomes
  reusable after the 16-bit command rotation ([§4.3](04_pgc_vm.md)).
  <https://code.videolan.org/videolan/libdvdnav>
- libudfread (libbluray): the UDF 2.50 metadata-partition reader.
  <https://code.videolan.org/videolan/libudfread>

`[SRC:]` tags in the sheets use the format defined in
`spec/clean/EVIDENCE_STANDARD.md`. Evidence grades (VERIFIED, SINGLE, INFERRED, OPEN)
are strength markers, not citations.
