# spec/clean — research log and evidence trail (NOT the spec)

The **authoritative specification is `spec/advanced/`** (sheets 01–10 + INDEX),
built to HTML under `docs/`. This directory is the working history: how each fact
was derived, the adversarial questions, and the patent-figure transcriptions.
When a note here disagrees with `spec/advanced/`, **`spec/advanced/` wins** — the
note is older thinking, kept for provenance.

## Current, still-cited

| File | Role |
|---|---|
| `EVIDENCE_STANDARD.md` | provenance tag format used across all sheets |
| `14_IMPLEMENTER_QUESTIONS.md` / `14_IMPLEMENTER_ANSWERS.md` | the implementer Q&A the sheets distill |
| `15_ADVERSARIAL_QUESTIONS.md` | adversarial pass; ASK/CLOSED tracker |
| `16_PATENT_FIGURES.md` | what each patent drawing specifies vs this corpus |
| `17_HDI_MENU_RESEARCH.md` | HDi menu census method behind sheet 05 |

## Early-session research (Standard Content + first framing)

`00_PRIMER`, `01_VMGI_MAT…`, `02_VTSI_MAT…`, `03_libdvdread_requirements`,
`04_ADV_OBJ`, `06_TMAP_solved`, `07_ADVERSARIAL_REVIEW`, `08_NV_PCK_PCI_DSI`,
`09_AACS`, `11_survey_results`, `12_DISC_STRUCTURE`, `13_PLAYBACK` are earlier
notes (several about Standard Content / Category 1, which is **out of scope** for
the product). Retained as the evidence trail. Do not implement from them; the
Category 2 facts they contain have been carried into `spec/advanced/` and
re-verified there by `experiments/e01`–`e19`.
