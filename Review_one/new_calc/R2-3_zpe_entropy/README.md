# R2-3 — ZPE, thermal, and entropy corrections (move Eq. 1 from ΔE to ΔG)

## Verbatim comment (Referee 2)

> There are major concerns about the calculation of the total energy (in eq 1).
> Which energy is used from the DFT results? Do they consist of only DFT
> energy, or is there an inclusion of ZPE and entropy contribution? If they
> are included, it should also be mentioned in the computation section. If
> they are not included, they should also be added to the energy values for
> more accurate results.

## What this folder produces

A Gibbs-free-energy version of Equation 1 and Figure 4. Everything we
currently report (Figure 4, Table S5) is the electronic energy difference
ΔE. We have to switch to

    ΔG_n = ΔE_elec,n + ΔZPE_n + ΔH_T,n − T·ΔS_n

with a common reference state (this simultaneously closes R1-5):

    ΔG_n = G[MOF+ads_n]
           − G[MOF_bare]
           − n_CO2·G[CO2(g)]
           − n_H2·G[H2(g)]
           + n_H2O·G[H2O(g)]
           + n_CH4·G[CH4(g)]

The job of this folder is to produce every G(...) term in that
equation. We need vibrational frequencies at every stationary point —
six per candidate (s0 through s5) for the adsorbed states, plus one
each for the four gas-phase reference molecules already optimized in
`DFT/complete_dft_input/molecules/`.

## Protocol decisions (and the reason behind each)

### 1. Partial-Hessian Vibrational Analysis (PHVA) for the adsorbed states

A full Hessian on a 400-atom cluster is ~2,400 SCF gradient evaluations
per stationary point. With ~24 stationary points across the 8 candidates'
larger clusters that is order ~60,000 SCFs — prohibitive even on
TSUBAME4.0. PHVA, where only the chemically active subsystem contributes
to the Hessian, brings this down by roughly 30× without changing the
modes that matter for the reaction thermochemistry. PHVA is standard in
catalysis (see Sauer & Sierka, *J. Comput. Chem.* 2000, **21**, 1470 and
the more recent review in Ye et al., *Chem. Rev.* 2024). The
contribution of the rest of the cluster to ΔG cancels between the
adsorbed and reference states because the same atoms are present in
both — the cancellation is exact in the limit that the frozen
sub-cluster is identical.

**Active subsystem** at each step = (adsorbate atoms) ∪ (the open
metal site) ∪ (the first coordination shell of donor atoms around the
OMS). Typical sizes 10–14 atoms regardless of total cluster size.
The exact atom indices for each candidate go in
`inputs/active_subsystems.tsv` (one row per material, columns =
qmof ID, step, atom index list).

### 2. Grimme (2012) quasi-RRHO for low-frequency modes

Pure harmonic S(T) diverges as ν → 0, which makes the entropy of soft
adsorbate modes (hindered translations, hindered rotations) wildly
overestimated. Grimme's quasi-RRHO interpolates the harmonic entropy
of each mode toward a free-rotor entropy below a cutoff ν_c, with a
smooth Lorentzian damping w(ν) = 1/(1 + (ν_c/ν)^4). We use ν_c = 100
cm⁻¹ as Grimme recommended and as is standard in heterogeneous
catalysis. The script in `analysis/quasi_rrho.py` applies this
correction.

Reference: Grimme, S. *Chem. Eur. J.* 2012, **18**, 9955–9964
(DOI 10.1002/chem.201200497).

### 3. Tighter SCF + tighter geometry before frequencies

CP2K force errors propagate to frequencies as δω ≈ δF / sqrt(m).
The geometry-optimization SCF threshold (1.0e-5) is too loose for
accurate vibrational frequencies. We re-converge each stationary
point with `EPS_SCF = 1.0e-7` and `MAX_FORCE / RMS_FORCE = 1.0e-4`
before the vibrational step. Reuses the existing `*-RESTART.wfn`,
so this is a few SCFs, not a full geometry re-relax.

### 4. Two temperatures

- T = 298.15 K: the standard-state temperature; values reported in
  Figure 4 and Table S5 of the revised paper.
- T = 623.15 K (350 °C): the operating temperature used by
  Yasumura et al. (2025, our ref 60) for the experimentally relevant
  Mg/Ni-MOF-74 system. Reported in the SI as a sensitivity check;
  required to defend the claim that any small endothermic step
  (e.g. qmof-52ef7e9) is thermally accessible (also closes R1-7).

### 5. Gas-phase reference molecules: full ideal-gas RRHO

Small, cheap, do them with the full Hessian and add translational +
rotational entropy via Sackur-Tetrode and the symmetric-top rotational
partition function in post-processing. Symmetry numbers: CO₂ σ=2 (D∞h),
H₂ σ=2 (D∞h), H₂O σ=2 (C₂v), CH₄ σ=12 (Td). The CP2K input template
takes σ via the `SYMMETRY_NUMBER` keyword.

## Step-by-step workflow

1. **(prep)** Define the active subsystem for every (material, step)
   combination. Write atom-index lists into `inputs/active_subsystems.tsv`.
2. **(tighten)** For each (material, step), run a 20-step BFGS
   geometry refinement at `EPS_SCF=1e-7`, `MAX_FORCE=1e-4` using the
   existing `*-RESTART.wfn`. Outputs go in `runs/<id>/s<n>_tight/`.
3. **(PHVA)** Run `inputs/template_adsorbate_phva.inp` adapted per
   stationary point. Outputs go in `runs/<id>/s<n>_freq/`. Confirm
   that no imaginary frequency above 30i cm⁻¹ appears in the active
   subsystem; document any soft low-frequency modes ≤ 30i.
4. **(gas refs)** Run `inputs/template_gasphase_rrho.inp` once each
   for CO₂, H₂, H₂O, CH₄. Outputs in `runs/molecules/<mol>_freq/`.
5. **(post-process)** For every output, run
   `python analysis/quasi_rrho.py <out>` with `--ads` for the MOF
   stationary points and `--gas --mol-mass ... --I ... --sigma ...`
   for the molecules. The script returns ZPE, U_vib, T·S, and G_corr
   in eV.
6. **(sum)** Collect everything in `analysis/thermochem.xlsx` and
   compute ΔG_n per material per step at T = 298.15 K and T = 623.15 K.
7. **(figures)** Regenerate Figure 4 with the y-axis labelled
   "ΔG (eV)" instead of "ΔE (eV)" using the 298.15 K column.
   Regenerate Table S5 with the per-step breakdown
   (E_elec, ZPE, H_T, T·S, G).

## Compute budget (rough)

| Cluster size | SCF time per evaluation | Active atoms (typical) | PHVA SCFs per step | Wall time per step |
|---:|---:|---:|---:|---:|
| 54 atoms (ea9f3ea Ni-MOF-74) | 5 min   | 8  | ~50  | ~4 h   |
| 86 atoms (52ef7e9 Al-aza) | 10 min  | 10 | ~60  | ~10 h  |
| 100 atoms (74ace65 Zn-pyrazole) | 15 min  | 12 | ~72  | ~18 h  |
| 156 atoms (91692c9 Al) | 30 min  | 12 | ~72  | ~36 h  |
| 192 atoms (07c07d3 Zn paddle-wheel) | 45 min  | 14 | ~84  | ~60 h  |
| 428 atoms (04c1119 Zn-IRMOF-10) | 2 h     | 14 | ~84  | ~170 h |

Sum across the 8 final candidates × 6 steps + 4 gas-phase molecules:
roughly **2,500 node-hours** at single-node throughput. With
`NPROC_REP=16` and 6–8 simultaneous jobs on TSUBAME4.0, **wall-clock
~1–2 weeks**. Each (material, step) is independent; queue them all
in parallel.

## Open issue to flag before starting

**qmof-9f8e842 (Mg-MOF-74) is missing from `DFT/complete_dft_input/`.**
The folder is in `DFT/passing_cifs/` and the CIF is in
`DFT/input_cifs/9f8e842 -Finished/`, but the s0–s5 geometry-optimization
outputs are not where the other candidates' are. Either they live in
a separate location that needs locating, or they need re-running.
Mg-MOF-74 is the top-recommended material in the paper, so addressing
R2-3 without it leaves a hole. Sort this out **before** starting the
PHVA campaign.

## Inputs you'll need

- `s<n>-pos-1.xyz` for each (material, step) — already on disk.
- `s<n>-RESTART.wfn` — already on disk; used for both the tight
  re-optimization and the vibrational SCF restart.
- `inputs/active_subsystems.tsv` — to be created (see Step 1).
- `inputs/template_adsorbate_phva.inp` — provided.
- `inputs/template_gasphase_rrho.inp` — provided.

## Files in this folder

- `README.md` — this document.
- `inputs/template_adsorbate_phva.inp` — CP2K PHVA template for the
  adsorbed reaction-pathway states.
- `inputs/template_gasphase_rrho.inp` — CP2K full-Hessian template
  for the gas-phase reference molecules.
- `inputs/active_subsystems.tsv` — (to be populated) per-material
  per-step atom index lists for the active subsystem.
- `analysis/quasi_rrho.py` — Python post-processor that applies the
  Grimme quasi-RRHO correction and prints ZPE, U_vib, T·S, G_corr.
- `analysis/thermochem.xlsx` — (to be populated) per-(material, step)
  thermochemistry breakdown that feeds Figure 4 and Table S5.

## Cross-links

- **R1-5** (common-reference Eq. 1) is closed by this folder. The
  reformulation lives in the new ΔG_n equation above; we do not
  separately tabulate ΔE_n.
- **R1-3** (spin polarization) must be locked first for Ni-MOF-74,
  because the frequencies depend on the wavefunction.
- **R1-9** (configuration sampling) must be locked first for every
  candidate — we only do frequencies on the lowest-energy
  configuration at each step.
- **R2-2** (CI-NEB) downstream of this: Gibbs activation energies
  ΔG‡ = ΔE‡ + ΔZPE‡ + ΔH_T‡ − T·ΔS‡ require the transition-state
  frequencies. Once R2-2 has the transition states, run PHVA on them
  using the same active-subsystem definition.

## Methodology references

- Grimme, S. *Chem. Eur. J.* 2012, **18**, 9955–9964 — quasi-RRHO.
- Sauer, J.; Sierka, M. *J. Comput. Chem.* 2000, **21**, 1470 — PHVA
  in heterogeneous catalysis.
- Ye, R.; Hurlock, M. J.; Day, B. A.; Stanley, C. B.;
  Goldsmith, B. R. *Chem. Rev.* 2024 — recent PHVA review for MOF
  catalysis (verify exact citation).
- McQuarrie, *Statistical Mechanics*, 2000 — ideal-gas RRHO.
- VandeVondele et al., *Comput. Phys. Commun.* 2005, **167**, 103 —
  CP2K/Quickstep (already cited in main text).

## Owner / status

Owner: MK · Status: open · Blocked on R1-3 (spin treatment) +
R1-9 (final lowest-energy configurations) for the adsorbed states;
the gas-phase reference runs can start immediately.
