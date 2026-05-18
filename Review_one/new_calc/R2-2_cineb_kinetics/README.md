# R2-2 — Kinetic barriers via CI-NEB on the 5 novel materials

## Verbatim comment (Referee 2)

> For the DFT analysis, the authors performed thermodynamic screening and duly
> noted that the kinetic barriers were not calculated. Given the computations
> performed in this manuscript, it is necessary to include a kinetic analysis
> to strengthen the conclusions. If the aim is to reduce computational cost,
> the kinetic barriers (via Cl-NEB) can be performed on the last 5 novel
> materials they have identified for experimental research.

## What to compute

Climbing-image NEB activation energies for each PCET step in the s0 -> s5
pathway, on the **5 novel materials**:

- qmof-0e64acd (Al)
- qmof-52ef7e9 (Al)
- qmof-91692c9 (Al)
- qmof-07c07d3 (Zn)
- qmof-74ace65 (Zn)

That is 5 materials × 5 transitions = **25 NEB runs**. Use 5–8 images per band
including the climbing image.

## Inputs needed

Per material, the already-optimized endpoint structures sit at
`DFT/complete_dft_input/<id>/s<n>-pos-1.xyz` for n = 0..5. Build NEB inputs
that pair s_n → s_(n+1):

- s0 → s1 (CO2 adsorption)
- s1 → s2 (first H addition)
- s2 → s3 (second H addition, C–O cleavage, H2O formation)
- s3 → s4 (third H addition)
- s4 → s5 (final H + CH4 desorption)

## Suggested CP2K block

```text
&GLOBAL
  RUN_TYPE BAND
&END GLOBAL
&MOTION
  &BAND
    NPROC_REP <ncores_per_image>
    BAND_TYPE CI-NEB
    NUMBER_OF_REPLICA 7      ! 5 intermediate + 2 endpoints; tune as needed
    K_SPRING 0.05
    &CI_NEB
      NSTEPS_IT 5
    &END CI_NEB
    &OPTIMIZE_BAND
      OPT_TYPE DIIS
      &DIIS
        MAX_STEPS 200
      &END DIIS
    &END OPTIMIZE_BAND
    &REPLICA
      COORD_FILE_NAME s0-pos-1.xyz
    &END REPLICA
    &REPLICA
      COORD_FILE_NAME s1-pos-1.xyz
    &END REPLICA
  &END BAND
&END MOTION
```

## Expected outputs

- One `Ea_<id>_s<n>_to_s<n+1>.dat` per transition + climbing-image structure
  in `runs/<id>/`.
- `analysis/cineb_summary.xlsx`: rows = materials, columns = E_a per
  transition + max E_a + identification of rate-determining step.
- New main-text or SI figure: bar/heat-map of activation energies across the 5
  novel materials.
- Discussion text in §3.2 and §4 explaining how kinetics modulates the
  thermodynamic ranking (e.g. a thermodynamically favored material with a
  high E_a may be less attractive than a slightly less favored material with
  lower E_a).

## Cross-links

- Depends on R1-9 outputs (lowest-energy configurations should be the NEB
  endpoints) and on R2-3 if Gibbs barriers (not just electronic-energy
  barriers) are desired.
- Single biggest compute commitment of the revision.

## Owner / status

Owner: MK · Status: open
