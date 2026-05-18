# R2-3 — ZPE and entropy corrections

## Verbatim comment (Referee 2)

> There are major concerns about the calculation of the total energy (in eq 1).
> Which energy is used from the DFT results? Do they consist of only DFT
> energy, or is there an inclusion of ZPE and entropy contribution? If they
> are included, it should also be mentioned in the computation section. If
> they are not included, they should also be added to the energy values for
> more accurate results.

## What to compute

Vibrational frequencies at every optimized stationary point in the reaction
profile (s0 through s5) for every candidate that survives the screening
(prioritise the 8 final candidates). From frequencies:

- Zero-point energy: ZPE = ½ Σ ℏω_i
- Thermal enthalpy correction: ΔH_T (harmonic, 298.15 K)
- Vibrational entropy: S_vib (harmonic, 298.15 K)
- For gas-phase reference molecules (CO2, H2, H2O, CH4): full
  translational + rotational + vibrational partition function with literature
  symmetry numbers; preferred to read these from NIST or compute via Shomate.

Then report Gibbs free-energy change per step:

    ΔG_n = ΔE_n + ΔZPE_n + ΔH_T,n − T·ΔS_n

For adsorbed intermediates use harmonic approximation only (no translational /
rotational degrees of freedom). Document this clearly in §2.2.

## Inputs needed

- All converged geometries `s<n>-pos-1.xyz` per material.
- Existing wavefunctions `s<n>-RESTART.wfn` to accelerate the frequency runs.

## Suggested CP2K block

```text
&GLOBAL
  RUN_TYPE VIBRATIONAL_ANALYSIS
&END GLOBAL
&VIBRATIONAL_ANALYSIS
  TEMPERATURE 298.15
  THERMOCHEMISTRY .TRUE.
  &PRINT
    &MOLDEN_VIB
    &END
    &THERMOCHEMISTRY
    &END
  &END PRINT
&END VIBRATIONAL_ANALYSIS
```

Tip: for the cluster sizes here, full Hessians can be expensive. If runtime is
prohibitive, restrict the Hessian to the chemically active subsystem (adsorbate
+ OMS metal + first-shell donors) using `&MODE_SELECTIVE` / partial Hessian
vibrational analysis (PHVA), and document that approximation in §2.2.

## Expected outputs

- `analysis/thermochem.xlsx`: rows = (material × step), columns = E (eV),
  ZPE (eV), H_T (eV), S (eV/K), G (eV), ΔG_n (eV).
- Regenerated Figure 4 with the y-axis labelled “ΔG (eV)” and main-text Table
  S5 updated likewise.
- Methodology paragraph in §2.2 documenting (i) harmonic approximation, (ii)
  T, P, (iii) treatment of low-frequency modes (e.g. cutoff at 50 cm⁻¹), (iv)
  PHVA if used.

## Cross-links

- Must be run **after** R1-3 (final spin treatment) and R1-9 (final
  configuration choice) are locked, otherwise the frequencies are recomputed.
- Outputs feed directly into R2-2 if Gibbs-corrected NEB barriers are wanted.

## Owner / status

Owner: MK · Status: open
