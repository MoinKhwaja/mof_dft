# Review_one / new_calc

All new DFT/CP2K calculations spun up to address the first round of reviewer
comments live here. Each subfolder corresponds to one reviewer comment with
`Classification = new-compute` in `../response/punch_list.xlsx`.

## Map: folder ↔ comment

| Folder                              | Comment | Effort | Short title                                                       |
|-------------------------------------|---------|--------|-------------------------------------------------------------------|
| `R1-3_spin_polarization/`           | R1-3    | medium | Spin-polarized rerun of Ni-MOF-74 reaction profile                |
| `R1-6_excited_state_photomech/`     | R1-6    | high   | sTDA excited states + HOMO/LUMO vs CO2RR redox potentials         |
| `R1-9_config_sampling/`             | R1-9    | high   | Alternative CO2 orientations / protonation sites (8 candidates)   |
| `R1-10_hybrid_bandgap/`             | R1-10   | medium | HSE06 / ωB97X-D + Rosen 1.09 fit on the 8 candidates              |
| `R2-2_cineb_kinetics/`              | R2-2    | high   | CI-NEB activation energies on the 5 novel materials               |
| `R2-3_zpe_entropy/`                 | R2-3    | high   | Vibrational frequencies → ZPE / H_T / S / G                       |
| `R2-4_geom_active_sites/`           | R2-4    | medium | **Consolidation only** — pulls outputs from R1-9, R1-6, R2-3      |

R2-4 has no independent calculations; it exists as the canonical assembly
point for the SI table the reviewer explicitly asked for, and for the
geometry-convergence methodology paragraph. Its `inputs/` and `runs/` are
intentionally empty.

## Subfolder layout

Each compute-producing folder has:

- `README.md` — verbatim comment, what to compute, suggested CP2K block,
  expected outputs, cross-links to other folders.
- `inputs/` — starting structures, prepared CP2K input files, restart wfn
  files copied from `../../DFT/complete_dft_input/<id>/`.
- `runs/` — actual CP2K run directories (one per material / band /
  configuration as appropriate).
- `analysis/` — post-processing scripts and result spreadsheets that feed
  back into the revised manuscript and SI.

## Dependency order (when to run what)

```
                ┌──────────────────────────────┐
                │ R1-3  spin polarization      │
                │ (Ni-MOF-74 UKS / DFT+U)      │
                └──────────────┬───────────────┘
                               │ locks spin treatment
                               ▼
   ┌─────────────────┐   ┌───────────────────────┐   ┌─────────────────────────┐
   │ R1-10  hybrid   │   │ R1-9  config sampling │   │ R1-6  sTDA + redox-     │
   │ band gap        │   │ (CO2 orientations,    │   │ potential alignment     │
   │ (HSE06, ωB97X-D │   │  proton sites)        │   │ (excited-state proof)   │
   │  + Rosen 1.09)  │   └──────────┬────────────┘   └──────────┬──────────────┘
   └────────┬────────┘              │                           │
            │                       ▼                           ▼
            │            ┌────────────────────────────────────────────────────┐
            │            │ R2-3  ZPE / entropy / G                            │
            │            │ (frequencies at every stationary point)            │
            │            └──────────┬─────────────────────────────────────────┘
            │                       │ supplies ΔG endpoints
            │                       ▼
            │            ┌────────────────────────────────────────────────────┐
            │            │ R2-2  CI-NEB kinetics                              │
            │            │ (5 novel materials × 5 transitions)                │
            │            └────────────────────────────────────────────────────┘
            │
            └──► R1-6 (HSE06 inputs into the redox-alignment plot)
            └──► R2-4 (consolidation: takes outputs from R1-9, R1-6, R2-3)
```

In practice:

1. **Lock spin treatment (R1-3) first.** It changes the energies and
   wavefunctions everything else builds on.
2. **R1-10 (hybrid gaps)** and **R1-6 (sTDA + redox alignment)** can run
   largely in parallel once spin is decided; R1-6 benefits from R1-10's
   HSE06 single-point gaps, so ideally start R1-10 a day or two earlier.
3. **R1-9 (config sampling)** in parallel with R1-10/R1-6. The lowest-
   energy configurations from R1-9 are the geometries everything
   downstream uses.
4. **R2-3 (frequencies / G)** after R1-9 geometries are final.
5. **R2-2 (CI-NEB)** last — largest compute, uses R1-9 endpoints and
   ideally R2-3 Gibbs corrections for ΔG‡.
6. **R2-4** is the SI-table consolidation; populate at the end.

## Status tracking

Mark progress in `../response/punch_list.xlsx` (`Status` column) rather
than in this README — that keeps a single source of truth.

## Methodology references that drive these calculations

These are the primary sources behind the protocols in the subfolder
READMEs (full bibliographic detail in each subfolder + in `references.bib`
once added):

- **Rosen et al.**, *npj Comput. Mater.* 2022 — QMOF database + the
  `1.09·E_g,PBE + 1.04 eV` linear fit (used in R1-10).
- **Hehn et al.**, *J. Chem. Theory Comput.* 2022, **18**, 4186 — sTDA
  implementation in CP2K GPW (used in R1-6).
- **Aziz et al.**, *J. Mater. Chem. A* 2017, **5**, 11894 — HOMO/LUMO vs
  CO2RR/HER/water-splitting redox alignment in a porphyrinic MOF (used
  in R1-6).
- **Chen et al.**, *Coord. Chem. Rev.* 2022, **469**, 214664 — 4-pathway
  taxonomy and 5-step photo-CO2RR mechanism (used in R1-1 / R1-6
  framing).
- **Liu, Wu, Gong**, *J. Phys.: Energy* 2021, **3**, 034016 — TD-PBE/MOLOPT-
  SR-GTH cluster calculations on a Ni-porphyrin MOF for CO2-to-CH4 (closest
  published method twin to ours).
- **Taddei et al.**, *J. Mater. Chem. A* 2019, **7**, 23781 — PBE/DZVP-
  MOLOPT-SR-GTH/GTH-PBE on UiO-66 (same basis + pseudopotentials as us).
- **Ingham, Aziz, Di Tommaso, Crespo-Otero**, *Mater. Adv.* 2023, **4**,
  5388 — perspective from which most of the above were identified.
