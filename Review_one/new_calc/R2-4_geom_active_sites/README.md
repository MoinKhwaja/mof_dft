# R2-4 — Ground-state geometry confirmation + active-site reporting (consolidation only)

## Verbatim comment (Referee 2)

> Additionally, how are the ground state geometries confirmed after SCF
> analysis? How are the active sites and stable geometries of adsorbents
> identified? Data on the screening of these should also be provided (at
> least in the SI file) on adsorption energies for different active sites
> and orientations.

## What this folder is (and isn't)

**No independent calculations live here.** R2-4 is a *consolidation /
reporting* folder. The reviewer's three sub-questions are addressed by
work happening in other folders:

| Sub-question                                  | Where the calculation lives                                  |
|-----------------------------------------------|--------------------------------------------------------------|
| "How are ground-state geometries confirmed?"  | `../R2-3_zpe_entropy/` (frequency analysis = no imag. modes) |
| "How are active sites identified?"            | OMS algorithm in `../../Screening_Scripts/` + `R1-6` redox-alignment |
| "Adsorption energies for different sites and orientations" | `../R1-9_config_sampling/` (all sampled configurations) |

This folder exists only so that:

1. There is one canonical place to assemble the **SI table** Referee 2
   explicitly asked for ("Data on the screening of these should also be
   provided ... at least in the SI file").
2. The Methodology paragraph documenting geometry-convergence criteria
   has a home.
3. R2-4 in the punch list and response letter has a folder pointer that
   matches every other reviewer comment.

## Deliverables

1. **`analysis/site_orientation_table.xlsx`** — copy of the consolidated
   table that `R1-9_config_sampling/analysis/` produces, formatted for SI.
   One row per (material, active site, orientation) with columns:
   - qmof ID
   - Site index (from Chung 2019 OMS algorithm)
   - Orientation (C-down / O-down / O,O-side-on)
   - E_ads (eV, common reference per R1-5)
   - ΔG_ads (eV, with thermo corrections from R2-3 if available)
   - Lowest-energy at this site? (Y/N)
   - Reported in main-text Figure 4? (Y/N)
   - Geometry file path

2. **§2.2 Methodology paragraph (drafted here, pasted into main.tex)** —
   document explicitly:
   - BFGS optimizer with `MAX_DR / MAX_FORCE / RMS_DR / RMS_FORCE = 3e-3`
     a.u. (from the existing `s*.inp` files in
     `../../DFT/complete_dft_input/`).
   - SCF threshold `EPS_SCF = 1.0e-5` a.u., OT/DIIS minimizer, outer SCF.
   - Confirmation of minima via R2-3 frequencies (no imaginary modes
     above a stated cutoff, e.g. 30i cm-1, with explicit note for any
     remaining low-frequency hindered rotors).
   - Active-site identification via the Chung et al. 2019 OMS algorithm
     (cite their work and `../../Screening_Scripts/`).
   - Reference to the consolidated SI table above and to the
     configuration-sampling protocol in `R1-9_config_sampling/`.

## Inputs needed

Outputs of:
- `../R1-9_config_sampling/analysis/config_sampling.xlsx` (all sampled
  configurations + E_ads).
- `../R2-3_zpe_entropy/analysis/thermochem.xlsx` (Gibbs corrections, if
  ready in time; otherwise report ΔE_ads only and add ΔG_ads at proof
  stage).
- `../R1-6_excited_state_photomech/analysis/redox_alignment.xlsx` (so the
  SI table can optionally include a "thermodynamically accessible to
  photoexcited electron?" Y/N column tying back to R1-6).

## Cross-links

- Heavy dependency: **R1-9** (configuration sampling) and **R1-6**
  (active-site/photomechanism context) drive the table contents.
- Lighter dependency: **R2-3** (Gibbs corrections) and **R1-3** (spin
  treatment) feed energy values used in the table.

## Owner / status

Owner: MK · Status: open (blocked on R1-9 + R2-3 first)
