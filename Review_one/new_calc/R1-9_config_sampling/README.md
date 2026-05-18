# R1-9 — Configuration sampling at each reaction step

## Verbatim comment (Referee 1)

> It is unclear if the authors have sampled different configurations for each
> step. i.e., Have they tried to coordinate CO2 to the metal centre via the C
> atom, or have they attempted to hydrogenate the oxygen atom that is
> coordinated to the metal centre?

## What to compute

For each of the **8 final candidates** (priority on the 5 novel materials:
qmof-0e64acd, -52ef7e9, -91692c9, -07c07d3, -74ace65), optimize at least the
following alternative initial configurations and keep the lowest-energy one for
the main-text Figure 4:

1. **CO2 binding orientation on the OMS** (step s1):
   - C-down (carbon coordinates to the metal)
   - O-down end-on
   - O,O-side-on (bidentate through both oxygens)
2. **First hydrogenation step** (step s2):
   - Proton onto the metal-bound oxygen (formate-like *OCHO)
   - Proton onto the distal oxygen (carboxyl-like *COOH)
3. **Optional sanity check for one or two candidates**: alternative protonation
   site at the *CHO -> *CH2O step (carbon vs oxygen).

## Inputs needed

- 8 optimized MOF clusters from `DFT/complete_dft_input/<id>/s0-pos-1.xyz` (use
  the converged geometry as starting point).
- CO2 reference molecule from `DFT/complete_dft_input/molecules/co2.xyz`.
- Existing `s1.inp` per material as a template; clone and modify only the
  initial atomic positions.

## Practical scaffolding

- Within each material folder, organize sub-runs as:
  - `runs/<id>/s1_c-down/`
  - `runs/<id>/s1_o-down/`
  - `runs/<id>/s1_side-on/`
  - `runs/<id>/s2_proximal_OH/`
  - `runs/<id>/s2_distal_OH/`
- Use `SCF_GUESS ATOMIC` on the first config of each material, then
  `SCF_GUESS RESTART` from the lowest-energy converged neighbor for the others.

## Expected outputs

- `analysis/config_sampling.xlsx` — one sheet per material, rows = sampled
  configurations, columns = E_total, ΔE_ads, lowest? (Y/N), final structure
  file path.
- Update main-text Figure 4 with the lowest-energy configuration's energy per
  step.
- New SI Table S[N] listing all sampled configurations and their relative
  energies.

## Cross-links

- Heavily overlaps with **R2-4** (active-site / orientation screening) — those
  outputs can be reused for both responses.
- Spin treatment per material should follow the decision made in **R1-3**.

## Owner / status

Owner: MK · Status: open
