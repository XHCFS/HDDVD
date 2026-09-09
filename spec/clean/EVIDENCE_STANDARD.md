# Evidence standard

Every factual claim in `spec/clean/` carries a provenance tag so any future reader can
re-derive or falsify it without trusting the author.

## Tag format

`[SRC: <source> | <locator> | <how>]`

**Source classes**

| Class | Meaning | Example locator |
|---|---|---|
| `PATENT` | text or table in a downloaded patent | `US20080298219A1 TABLE 80` |
| `SPEC` | published specification book (AACS LA, etc.) | `AACS HD DVD Pre-recorded Book Final 0.953 Table 3-8` |
| `DISC` | bytes read from a real disc image | `RESERVOIR_DOGS /HVDVD_TS/HV000I01.IFO @0x3E` |
| `CORPUS` | aggregate over many local files | `N=119 corpus/*/HVDVD_TS__HVA00001.VTI` |
| `SRCCODE` | third-party source we read | `libudfread src/udf_volume.c:56` |
| `TOOL` | output of an external tool | `udfclient -b 2048 <img>` |
| `DERIVED` | inference from other tagged facts | must name the inputs |

**Confidence**, always stated: `VERIFIED` (multi-specimen or patent+disc agreement) ·
`SINGLE` (one specimen) · `INFERRED` (reasoned, not observed) · `OPEN`.

## Rules

1. **No bare assertions.** A sentence stating a format fact without a tag is a bug.
2. **`DERIVED` must name its inputs** so the chain can be walked back.
3. **Patent vs disc must be distinguished.** Patents are draft-era and drift from
   shipped discs (see below). A patent table is evidence of intent; a disc is evidence
   of fact. When they disagree, the disc wins and the disagreement gets recorded.
4. **Record refuted hypotheses**, with the test that killed them. They are the
   expensive part to rediscover.
5. **State N.** "Verified" over 1 specimen and over 119 are different claims.
6. **Quote patents verbatim** when the wording carries the meaning. Paraphrase loses
   the qualifiers that matter ("shall", "may", "if no X exists ... padded with FFh").

## Known drift between patents and shipped discs

| Patent says | Discs have | Where seen |
|---|---|---|
| `HDDVD_TS` | `HVDVD_TS` | every disc, N=120 |
| `VPLIST%%%.XML` | `VPLST%%%.XPL` | every Advanced disc |
| `"HDDVD-V_TMAP"` | `HDDVD_TMAP00` | every `.MAP`, N=2421 |
| `HVAO00001.VTI` (OCR artifact) | `HVA00001.VTI` | N=119 |
| `TMAPI_SA` / `ILVUI_SA` as relative LBN | **byte offset** from start of the `.MAP` | N=2421 / 4 interleaved |
| AACS directory `AACS/` (Blu-ray) or always `ANY!/` | `ANY!/` on 96 discs, **`AAC!/` on 8** | N=120 listings |
| AACS HD DVD book: directory `"AACS"` / `"AACS_BAK"` | `ANY!/`+`ANY!_BAK/` or `AAC!/`+`AAC!_BAK/` | N=120 listings vs Final 0.953 §3.1 / §3.11 |

Google Patents' OCR also corrupts identifiers and **drops table rows** (TMAP_GI's
listed rows sum to 114 bytes against a stated 128). Where a table's numbers are in a
figure image rather than text, the values are simply absent — check the figure.

## Errors this standard has already caught

- **`VMGI_MAT` "byte-identical to DVD-Video"** — WRONG. HD DVD inserts
  `FP_PGCM_C_ADT_SA` / `FP_PGCM_EVOBU_ADMAP_SA` at RBP 216/220, shifting
  `VMGM_C_ADT` to 0xE0. Cause: checked against DVD instead of against the patent
  table that covers that region.
  `[SRC: PATENT | US20080298219A1 VMGI_MAT table | RBP 216-231]`
  `[SRC: DISC | RESERVOIR_DOGS HV000I01.IFO @0xE0,0xE4 = 8,9 | non-zero]`
- **`TMAPI_SRP` at offset 128** — WRONG, reads zeros. True location is **byte 384**
  (32-byte slots; `TMAPI_SA` is a byte offset). See `06_TMAP_solved.md`.
  `[SRC: CORPUS | N=2421]`
- **`VTS_CAT` app type in the high nibble** — WRONG, it is the low bits
  (`VTS_CAT`=2=`0010b`=Advanced VTS). `[SRC: PATENT | US20080298219A1 TABLE 79]`


## Published-spec citation form

In `spec/advanced/` (the built docs) the `[SRC: class | locator | how]` tags are rendered as **numbered citations `[n]`** resolving to `spec/advanced/13_references.md`, where every entry is a live/accessible link. The evidence **grades** (VERIFIED / INFERRED / OPEN / UNCLOSEABLE / OUT) stay inline as evidence-strength markers, separate from the citation number. `spec/clean/` keeps the long-form `[SRC:]` tags as the working trail.
