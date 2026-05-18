# Review_one / response — Phase A scaffold

This folder is the working space for our response to the first round of reviewer
comments on **NR-ART-04-2026-001578** ("In Silico Screening of Metal-Organic
Frameworks for CO2 Photo-Hydrogenation", Nanoscale).

## Files

- **punch_list.xlsx** — Master tracker. One row per reviewer comment (23 total:
  13 from Referee 1, 10 from Referee 2). Columns: `ID`, `Reviewer`,
  `Verbatim comment`, `Category`, `Classification`, `Effort`,
  `Target section(s)`, `Owner`, `Status`, `Notes / approach`.
  The **Summary** sheet auto-counts by reviewer / category / classification /
  effort / status. The **Legend** sheet defines the controlled vocabularies.

- **response_to_reviewers.docx** — Working draft of the point-by-point response
  letter that will be submitted to RSC. One section per reviewer, one heading
  per comment, with the reviewer's verbatim text quoted, classification
  metadata, a draft response (gray "Response (DRAFT)" stub), and an empty red
  `[TODO]` slot where the final author reply goes once the underlying
  calculation / analysis / text change is complete.

## Controlled vocabularies

- **Category**: framing · methodology · validation · discussion · cosmetic ·
  bibliography
- **Classification**: text-only · re-analysis · new-compute
- **Effort**: low (<= 1 day) · medium (days to ~1 week) · high (weeks,
  compute-bound)
- **Status**: open · in-progress · done

## How to work with these files

1. Pick the next item from `punch_list.xlsx` — sort/filter by `Effort` or
   `Classification` to plan a session (e.g. clear all `low`/`text-only`
   items first to retire Phase B quickly).
2. Update status to `in-progress` in `punch_list.xlsx` when you start.
3. Do the underlying work in the main project (new CP2K runs in `DFT/`,
   manuscript edits in `Review_one/Latex_format/main.tex`, etc.).
4. Replace the `[TODO]` block in `response_to_reviewers.docx` with the final
   author reply, citing revised manuscript section / line / figure / SI item.
5. Update status to `done` in `punch_list.xlsx`.

Every comment in `response_to_reviewers.docx` has an ID (e.g. `R1-5`,
`R2-3`) that matches the `ID` column of `punch_list.xlsx`. Keep them in sync.

## Phase A definition (what this folder represents)

Phase A is the triage + scaffold pass — no calculations, no manuscript edits.
It exists so that nothing falls through the cracks in the heavier phases that
follow (cosmetic edits, re-analysis on existing DFT data, new CP2K compute,
manuscript rewrite, response-letter finalization).
