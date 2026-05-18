# R1-6 — Excited-state photo-mechanism (connect band gap → reaction profile)

## Verbatim comment (Referee 1)

> Ground state energies were calculated at the DFT-D3 level. However, in the
> introduction the authors claim that the photo-hydrogenation mechanism relies
> on charge excitation and separation. The photocatalytic mechanism for CO2
> hydrogenation involves the interaction of CO2 with an excited electron to
> give the CO2- intermediate. The authors have modelled the photocatalytic
> mechanism as a thermocatalytic mechanism. The authors have not accounted
> for or discussed any excitation in the calculation of the reaction profile.
> How is their ground state reaction profile linked to a process involving an
> excited state?

## Why this needs calculation (and not just text)

We initially classified this as text-only (re-frame the photo-hydrogenation as
"band-gap screen + ground-state PCET thermodynamics"). On reading the Ingham
et al. perspective (Mater. Adv. 2023, 4, 5388), it became clear that the
strongest possible defence is to *include* an explicit excited-state result
on representative candidates so the paper actually contains photo-excitation
physics, not just a band-gap criterion as a stand-in for it. This folder
holds those calculations.

## What to compute (three sub-tasks)

### (a) sTDA excited states on representative candidates

Use **simplified Tamm-Dancoff TDDFT (sTDA)** as implemented in CP2K GPW
(Hehn et al., *J. Chem. Theory Comput.* 2022, **18**, 4186) on a subset of
the 8 final candidates. sTDA restarts cheaply from our converged PBE
wavefunctions and gives the first ~30-50 excited states. Report:

- Optical gap (first bright excitation with f > 0.05).
- Character of the lowest bright excitation (LC / LMCT / MLCT / LLCT) from
  natural transition orbital analysis.
- Comparison of optical gap to the fundamental (HOMO/LUMO) gap from R1-10.

Suggested representative subset (4 of the 8 to keep compute bounded):

| qmof ID         | Why representative                                 |
|-----------------|----------------------------------------------------|
| qmof-9f8e842    | Mg-MOF-74 — closed-shell, simple ligand, well studied (sanity check) |
| qmof-ea9f3ea    | Ni-MOF-74 — open-shell, depends on R1-3 spin treatment            |
| qmof-52ef7e9    | Al / azobenzene linker — photoswitchable linker, most photo-active candidate |
| qmof-74ace65    | Zn / pyrazole linker — different topology, halogenated linker      |

### (b) HOMO/LUMO vs CO2RR / HER / water-splitting redox potentials

Following Aziz et al. (*J. Mater. Chem. A* 2017, **5**, 11894), align the
band edges of every final candidate to the vacuum level (scissor-correct
where needed) and plot against:

- CO2 + e- → CO2- (E1 = -1.85 V vs SHE)
- CO2 + 2H+ + 2e- → HCOOH (-0.61 V)
- CO2 + 2H+ + 2e- → CO + H2O (-0.53 V)
- CO2 + 4H+ + 4e- → CH2O + H2O (-0.48 V)
- CO2 + 6H+ + 6e- → CH3OH + H2O (-0.38 V)
- CO2 + 8H+ + 8e- → CH4 + 2H2O (-0.24 V)  ← our target
- HER: 2H+ + 2e- → H2 (-0.41 V)
- Water oxidation: O2 + 4H+ + 4e- → 2H2O (+0.82 V)

(Reduction potentials from Ejsmont, Jankowska & Goscianska, *Catalysts*
2022, **12**, 110, which is Ingham's ref 216.)

This produces a Figure (likely Figure 3 or a new Figure) showing which
candidates are thermodynamically capable of (i) photoexcited-electron
reduction of CO2 to a CO2- intermediate, (ii) HER as competing pathway,
and (iii) — if relevant — water oxidation as the hole-acceptor.

### (c) Canonical 5-step photo-CO2RR mechanism diagram

Reproduce the 5-step semiconductor CO2RR mechanism from Ingham §7 / Chen
et al. (*Coord. Chem. Rev.* 2022, **469**, 214664) — light absorption →
charge separation → CO2 → CO2- at the CB edge → proton-coupled steps →
product desorption — and explicitly map our calculations onto it:

- Step 1 (light absorption): band gap (PBE+0.85 eV / Rosen 1.09 fit / HSE06
  from R1-10) + sTDA optical gap (this folder, task a).
- Step 2 (CO2- formation): redox-potential alignment (this folder, task b).
- Steps 3-5 (proton-coupled hydrogenation steps): the existing s0-s5 PCET
  profile (revised per R1-5 common-reference equation and R2-3 Gibbs
  corrections).

The figure is the single most important deliverable from this folder: it
visually answers Referee 1's "how is the ground-state profile linked to an
excited-state process?" in one panel.

## Inputs needed

- Converged PBE wavefunctions: `DFT/complete_dft_input/<id>/s0-RESTART.wfn`
  (for sTDA restart and HSE06 single-points).
- Optimized s0 geometries: `DFT/complete_dft_input/<id>/s0-pos-1.xyz`.
- ADMM auxiliary basis already in `BASIS_ADMM_MOLOPT` / `BASIS_ADMM`.

## Suggested CP2K block — sTDA

```text
&PROPERTIES
  &TDDFPT
    NSTATES 40
    MAX_ITER 100
    CONVERGENCE [eV] 1.0E-5
    KERNEL sTDA
    &sTDA
      DO_EXCHANGE TRUE
      FRACTION 0.25      ! HF-like exchange fraction in the sTDA kernel
    &END sTDA
    &PRINT
      &NTO_ANALYSIS
      &END
    &END PRINT
  &END TDDFPT
&END PROPERTIES
```

(Run as `RUN_TYPE ENERGY` with `&PROPERTIES/&TDDFPT` requesting sTDA; restart
the underlying KS-DFT from the converged PBE wfn.)

## Suggested CP2K block — HOMO/LUMO vacuum alignment

For each candidate, after the s0 PBE (or HSE06 from R1-10) single point,
print:

```text
&DFT
  &PRINT
    &MO_CUBES
      NHOMO 1
      NLUMO 1
      WRITE_CUBE F
    &END MO_CUBES
    &V_HARTREE_CUBE
    &END V_HARTREE_CUBE
    &E_DENSITY_CUBE
    &END E_DENSITY_CUBE
  &END PRINT
&END DFT
```

Then post-process the Hartree-potential cube to extract the vacuum level
along the longest pore axis, align HOMO/LUMO eigenvalues to that vacuum
level, and convert to vs. SHE (E_SHE = -4.44 V vs vacuum at 298 K).

## Expected outputs

- `analysis/sTDA_results.xlsx`:
  rows = (candidate × excited state index), cols = E (eV), oscillator
  strength, character (LC/LMCT/MLCT/LLCT), dominant orbital pair.
- `analysis/redox_alignment.xlsx`:
  rows = candidates, cols = HOMO_vs_vac, LUMO_vs_vac, HOMO_vs_SHE,
  LUMO_vs_SHE, ΔG_CO2_to_CO2- accessible? (Y/N), competing HER below LUMO?
- New main-text Figure mapping our calculations onto the canonical 5-step
  photo-CO2RR mechanism.
- New methodology paragraph in §2.2 documenting sTDA and the redox-potential
  alignment procedure.
- New §4 Discussion paragraph closing the loop: band gap + sTDA = photo-step;
  ground-state PCET = hydrogenation half.

## Cross-links

- Inputs come from R1-3 (final spin treatment for Ni-MOF-74) and R1-10
  (HSE06 single-points; sTDA can be run on top of either PBE or hybrid).
- Output feeds R2-4 (the consolidated active-site / mechanism reporting
  layer).
- The HOMO/LUMO-vs-redox figure can largely replace a portion of Figure 3
  in the manuscript.

## Methodology references to cite

- Hehn, Sertcan, Belleflamme, Chulkov, Watkins, Hutter, *J. Chem. Theory
  Comput.* 2022, **18**, 4186 — sTDA implementation in CP2K GPW.
- Grimme & Bannwarth, *J. Chem. Phys.* 2016, **145**, 054103 — original
  sTDA / sTDDFT method.
- Aziz, Ruiz-Salvador, Hernández, Calero, Hamad, Grau-Crespo,
  *J. Mater. Chem. A* 2017, **5**, 11894 — HOMO/LUMO vs CO2RR redox
  alignment for porphyrinic MOF (PMOF).
- Chen, Abazari, Adegoke, … Zhou, *Coord. Chem. Rev.* 2022, **469**, 214664
  — 4-pathway taxonomy (photo / electro / hydrogenation-with-H2 /
  cycloaddition) and 5-step CO2RR mechanism.
- Ejsmont, Jankowska, Goscianska, *Catalysts* 2022, **12**, 110 — reduction
  potentials used in the redox-alignment plot.
- Ingham, Aziz, Di Tommaso, Crespo-Otero, *Mater. Adv.* 2023, **4**, 5388 —
  perspective tying the whole protocol together.

## Owner / status

Owner: MK / ALCM · Status: open
