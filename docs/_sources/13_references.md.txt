# 13. References

Numbered sources for the citations throughout sheets 01–12. Every entry is a live,
accessible source: a public URL, or a primary artifact bundled with this
specification at the path given. Inline `[n]` marks the source. The grades **VERIFIED / INFERRED /
OPEN / UNCLOSEABLE / OUT** are evidence-strength, not citations
(`spec/clean/EVIDENCE_STANDARD.md`).

## Patents

- **[1]** Toshiba, *Information playback system using information storage medium*, US 2007/0091495 A1: HD DVD-Video Advanced Content architecture: disc Categories & FIG.7, startup FIG.50, soft-reset FIG.51, FirstPlayTitle rules, `sync` hard/soft, page/title/application clocks. <https://patents.google.com/patent/US20070091495A1/en>
- **[2]** Toshiba, *Information storage medium, information reproducing apparatus and method*, US 2008/0298219 A1: byte tables: VMGI/VTSI_MAT, TT_SRPT; TMAP TABLE 80–84; stream IDs TABLE 45–47; sub-picture §5.5.4 / FIG.69; graphics FIG.29. <https://patents.google.com/patent/US20080298219A1/en>
- **[3]** Toshiba, WO 2006/070920 A1: GCI_PCK pack layout FIG.108–109, ATRIT/EVOBIT trees FIG.111–112, `stream_id` FIG.119/122, private_stream1 / private_stream2 `sub_stream_id` FIG.120–121, graphics superposing. This publication has no Google-Patents figure PNGs; its 138 drawing sheets (FIG.1–FIG.147) are bundled as full-page rasters in `spec/raw/patents/figures/WO2006070920A1/pages/` (see `spec/clean/16_PATENT_FIGURES.md` for the FIG→page map). <https://patents.google.com/patent/WO2006070920A1/en>

## Standards & specifications

- **[4]** AACS LA, *Advanced Access Content System (AACS): HD DVD and DVD Pre-recorded Book*, Final Revision 0.953 (154 pages). Tables cited: 3-8 Title Key File, 3-9 Binding Information (BIFO), 3-10 Title Usage File, 3-11 BURS, 3-12 Usage Rule Set, 3-17 Content Certificate, 3-18 / 3-19 Content Hash Tables #1 / #2, 4-1 to 4-6 CPI (KMI, CHMI, URMI, CCI_SS, CCI), 4-7 Encrypted Pack, 6-2 Directory Key File; §4.3 (one Title Key per EVOB), §6.3 (persistent-storage provider directory), p. 21 (trailing residue allowed only after MKB, SKBF and CRL). Withdrawn from the AACS LA site; archived copy captured 2013-01-28: <https://web.archive.org/web/20130128114208/http://www.aacsla.com/specifications/AACS_Spec_HD_DVD_and_DVD_Prerecorded_Final_0.953.pdf> (SHA-256 `bd772c0b2d233412d0a644ab89d3489acf82f3b2907ce13b7f94830bfb38d5f5`). Specifications index: <https://aacsla.com/aacs-specifications/>
- **[5]** DVD Forum, *HD DVD-Video Advanced Content* XML Schemas v1.0 (16 Jul 2006): `Playlist.xsd`, `Manifest.xsd`, `iHD.xsd`, `iHDstyle.xsd`, `iHDstate.xsd`. Bundled: `spec/raw/adv_obj/v1.0/`. Origin (Scenarist install): <https://archive.org/details/scenarist-hd-dvd-45>
- **[17]** W3C, *Document Object Model (DOM) Level 2 Core* <https://www.w3.org/TR/DOM-Level-2-Core/> and *DOM Level 2 Events* <https://www.w3.org/TR/DOM-Level-2-Events/>.
- **[18]** W3C, *Synchronized Multimedia Integration Language (SMIL 2.0)*. <https://www.w3.org/TR/2005/REC-SMIL2-20050107/>
- **[19]** Ecma International, *ECMA-327, Compact Profile of ECMAScript*. <https://ecma-international.org/publications-and-standards/standards/ecma-327/>

## Software, tools & primary artifacts

- **[6]** iHD Scripting Type Library `iHDScripting.tlb` and extracted name list `iHD_Scripting_API.txt`, from Sonic Scenarist AC 4.5 `SCENACA.msi`. Bundled: `spec/raw/adv_obj/typelib/`, `spec/raw/adv_obj/iHD_Scripting_API.txt`. Origin: <https://archive.org/details/scenarist-hd-dvd-45>
- **[7]** Sonic, *Scenarist Advanced Content 4.5 User Guide*. Bundled: `spec/raw/adv_obj/Scenarist_AC_4.5_UserGuide.txt`. Origin: <https://archive.org/details/scenarist-hd-dvd-45>
- **[8]** libaacs, VideoLAN: source. <https://code.videolan.org/videolan/libaacs>
- **[9]** muslix64, *BackupHDDVD* (2006): source `src/aacs/{decoder/EVOBPack.java, decoder/DecryptEVOB.java, math/AESFunc.java}`. <https://archive.org/details/backup-hddvd>
- **[10]** Reference-decoder (`HDDVDPLAYDLL`) File Cache / ACA strings, as surfaced by the DumpHD tooling discussed in [16]. <http://forum.doom9.org/archive/index.php/t-123282.html>
- **[12]** Verification experiments `e01`–`e26` accompanying this specification (`experiments/run.py`).

## Disc & firmware corpus (Internet Archive)

- **[11]** *HD-DVD Archive* #1–#12: 120 retail HD DVD images, read over HTTP range with `tools/udfgrab.py`; per-disc names appear inline. <https://archive.org/details/hd-dvd_archive_01> (series #1–#12).
- **[13]** *HD-DVD Firmware Update Archive*: Toshiba player update images (`HD-A20 Ver 3003.iso`, fully encrypted; §11.F). <https://archive.org/details/hd-dvd-firmware-updates>

## Developer documentation & community

- **[14]** Microsoft HDi "Jumpstart" developer blog (Amit Dekate): Dissecting Hello World / Chapters, Persistent Storage, Xbox error codes. <https://learn.microsoft.com/en-us/archive/blogs/amyd/>
- **[15]** *HD DVD format capabilities, interactivity, and disc authoring*, EDN <https://www.edn.com/hd-dvd-format-capabilities-interactivity-and-disc-authoring/>; Wikipedia, *HDi (interactivity)* <https://en.wikipedia.org/wiki/HDi_(interactivity)> and *Advanced Content* <https://en.wikipedia.org/wiki/Advanced_Content>.
- **[16]** Wikipedia, *AACS encryption key controversy* <https://en.wikipedia.org/wiki/AACS_encryption_key_controversy>; Doom9 forum, *HD-DVD (and Blu-Ray) decrypting tools* <http://forum.doom9.org/archive/index.php/t-123282.html>.
- **[20]** HD DVD playback discussions (2024): VideoHelp <https://forum.videohelp.com/threads/300688>, AVS Forum, AVForums.

## Optical-drive command set

- **[21]** T10, *SCSI Multimedia Commands (MMC-5 / MMC-6)*: `GET CONFIGURATION`; optical-media profile list incl. `0x0050` HD DVD-ROM, `0x0051` HD DVD-R, `0x0052` HD DVD-RAM. Wikipedia, *SCSI Multimedia Commands* <https://en.wikipedia.org/wiki/SCSI_Multimedia_Commands>; profile constants e.g. QEMU `MMC_PROFILE_HDDVD_ROM` <https://en.wikipedia.org/wiki/SCSI_Multimedia_Commands>.
- **[22]** Redump preservation project, *HD DVD-Video Key Extraction*: per-disc AACS metadata preserved with a dump (MKB, Media Key, **Volume ID**, Volume Unique Key, Unit Key File Hash); confirms Volume ID is a drive/BCA value, not in the image. <http://wiki.redump.org/index.php?title=HD_DVD-Video_Key_Extraction>
