# R1-10 — Hybrid-functional band-gap sanity check

## Verbatim comment (Referee 1)

> The authors have screened 20,000 MOF structures using a correction to account
> for the well-known failing of GGA methods to reproduce the bandgap. While
> appropriate for such a large number of structures, the authors should
> validate the bandgaps of their successful candidate materials using a more
> accurate hybrid functional. This is a necessary sanity check for their
> workflow.

## What to compute

Single-point hybrid-functional band gap on each of the **8 final candidate
MOFs**:

| qmof ID         | Synthesized? | Metal |
|-----------------|--------------|-------|
| qmof-04c1119    | YES          | Zn    |
| qmof-ea9f3ea    | YES          | Ni    |
| qmof-9f8e842    | YES          | Mg    |
| qmof-0e64acd    | NO           | Al    |
| qmof-52ef7e9    | NO           | Al    |
| qmof-91692c9    | NO           | Al    |
| qmof-07c07d3    | NO           | Zn    |
| qmof-74ace65    | NO           | Zn    |

Recommended functional: **HSE06** (or PBE0 if HSE06 is too expensive).
Single-point on the s0 (bare relaxed MOF) geometry; no reoptimization needed.

## Inputs needed

- `DFT/complete_dft_input/<id>/s0-pos-1.xyz` (s0 converged geometry).
- `DFT/complete_dft_input/<id>/s0-RESTART.wfn` — use as `SCF_GUESS RESTART`
  for the PBE pre-iteration to accelerate convergence; the hybrid SCF itself
  will then start from the converged PBE density.

## Suggested CP2K block (replace &XC_FUNCTIONAL)

```text
&XC_FUNCTIONAL
  &PBE
    SCALE_X 0.75
    SCALE_C 1.0
  &END PBE
&END XC_FUNCTIONAL
&HF
  FRACTION 0.25
  &SCREENING
    EPS_SCHWARZ 1.0E-6
    SCREEN_ON_INITIAL_P TRUE
  &END SCREENING
  &INTERACTION_POTENTIAL
    POTENTIAL_TYPE SHORTRANGE
    OMEGA 0.11
  &END INTERACTION_POTENTIAL
  &MEMORY
    MAX_MEMORY 8000
  &END MEMORY
&END HF
```

Use ADMM (auxiliary basis already loaded in the original inputs:
`BASIS_ADMM_MOLOPT`, `BASIS_ADMM`) to make HSE06 tractable on the cluster
sizes used.

## Expected outputs

- `analysis/bandgap_comparison.xlsx`:
  - column A: qmof ID
  - column B: PBE gap (Materials Project value)
  - column C: PBE + 0.85 eV (empirical Fumanal shift used in screening)
  - column D: HSE06 (or PBE0) gap (this work)
  - column E: |D − C| (MAE of empirical shift)
  - column F: still inside 1.7–3.5 eV window? (Y/N)
- New SI Table S[N] reproducing the above.
- One-paragraph result in §3.1 of the main text discussing agreement.

## Cross-links

- Independent of R1-3 / R1-9; can be run in parallel.
- If hybrid gap pushes a candidate outside the 1.7–3.5 eV window, flag in
  Discussion — does not necessarily disqualify the candidate but warrants
  comment.

## Owner / status

Owner: MK · Status: open
