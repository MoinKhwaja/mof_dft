# R2-3 — Generated CP2K vibrational-analysis inputs

This folder contains 46 ready-to-submit CP2K inputs for the R2-3 frequency
campaign: 42 PHVA jobs (7 candidates × 6 steps) plus 4 full-Hessian gas-phase
runs. Mg-MOF-74 (qmof-9f8e842) is intentionally **not** here — its s0–s5
GEO_OPT outputs aren't on disk yet; once those land, regenerate just that
candidate with `python ../../../generate_r2-3_inputs.py 9f8e842` (script is
under `outputs/` in the session scratch — copy it into the repo if needed).

## Generator + manifest

- `manifest.tsv` — one row per generated PHVA input with `qid, step, n_total,
  n_active, active_metal_index, n_adsorbate, n_first_shell, input_file`. Use
  this to track submission state and to verify the active subsystem chosen
  for each (material, step).
- The active-subsystem heuristic: adsorbate atoms (everything past index
  `n_bare = atoms in s0`) ∪ the metal closest to the adsorbate centroid ∪
  every atom within 2.6 Å of that metal. For s0 (no adsorbate) the metal
  list expands to ALL metals + their 1st coordination shells, giving a
  larger active set so the bare-MOF entropy isn't undersampled.

## Layout

```
runs/
├── manifest.tsv               46-row inventory
├── 04c1119/   (428 atoms, 24h wall)
│   ├── s0_freq.inp s0_freq.subsys s0_final.xyz s0.cif
│   ├── s1_freq.inp ...  through s5
│   └── job.sh                (SGE / TSUBAME4 format)
├── 0e64acd/   (200 atoms, 12h)
├── 07c07d3/   (192 atoms, 12h)
├── 52ef7e9/   (86  atoms, 8h)
├── 74ace65/   (98  atoms, 8h)
├── 91692c9/   (156 atoms, 12h)
├── ea9f3ea/   (54  atoms, 6h)   ← Ni-MOF-74 (waits for R1-3 UKS results)
└── molecules/ (CO2, H2, H2O, CH4, 4h)
```

## How to submit on TSUBAME4.0

For each candidate folder, copy the converged parent wavefunctions next to
the freq inputs so `SCF_GUESS RESTART` finds them:

```bash
cd Review_one/new_calc/R2-3_zpe_entropy/runs/<qid>/
for s in s0 s1 s2 s3 s4 s5; do
  ln -sf ../../../../../DFT/complete_dft_input/<qid>/${s}-RESTART.wfn \
         ${s}_freq-RESTART.wfn
done
qsub job.sh
```

For 0e64acd the parent wfn lives in `DFT/complete_dft_input/0e64acd/input/`
rather than directly in `0e64acd/`; adjust the symlink path accordingly.

For molecules:

```bash
cd Review_one/new_calc/R2-3_zpe_entropy/runs/molecules/
for m in co2 h2 h2o ch4; do
  ln -sf ../../../../../DFT/complete_dft_input/molecules/${m}-RESTART.wfn \
         ${m}_freq-RESTART.wfn
done
qsub job.sh
```

## Important constraints / things to verify before submission

1. **ea9f3ea (Ni-MOF-74) needs the R1-3 UKS wavefunctions, not the original
   closed-shell ones.** As soon as the spin-polarized R1-3 GEO_OPT finishes,
   point the symlinks at those wfn files and rerun the generator with
   `--multiplicity 7` (or whatever spin state R1-3 settled on) so the freq
   input has the matching `&DFT MULTIPLICITY` and `&DFT UKS .TRUE.` blocks.
   The current ea9f3ea/*_freq.inp files are spin-restricted placeholders.

2. **Active-subsystem indices were chosen automatically.** Spot-check the
   first generated input per material against the corresponding `_final.xyz`
   to make sure the active metal is really the one bound to the adsorbate
   (not a different metal that happens to be near the centroid). A quick
   awk check:
   ```bash
   awk 'NR==FNR && /INVOLVED_ATOMS/{flag=1;next} flag && /&END/{exit} flag' \
       <(grep -A 30 INVOLVED_ATOMS s1_freq.inp) > /dev/null  # smoke test
   ```

3. **DX = 0.005 Bohr displacement** is the CP2K default. If frequencies look
   noisy in the printout, drop to 0.002 — costs 2.5× more SCFs.

4. **No imaginary frequencies above 30i cm⁻¹.** Imaginary modes localized
   on the adsorbate mean the GEO_OPT didn't converge to a true minimum;
   imaginary modes on the framework are usually OK to ignore (frozen
   sub-cluster artifact). The quasi-RRHO post-processor warns on any
   imaginary frequency.

5. **Mg-MOF-74 (9f8e842) is NOT in this batch.** When its s0–s5 GEO_OPT
   outputs are available in `DFT/complete_dft_input/9f8e842/`, run
   `python generate_r2-3_inputs.py 9f8e842` to add its bundle.

## After the runs finish

Post-process every `*_freq.out` with the quasi-RRHO script:

```bash
for f in runs/*/s*_freq.out runs/molecules/*_freq.out; do
  python analysis/quasi_rrho.py "$f" --ads --T 298.15 > "${f%.out}.qrrho"
done
for m in co2 h2 h2o ch4; do
  python analysis/quasi_rrho.py runs/molecules/${m}_freq.out --gas --T 298.15 \
    --mol-mass <amu> --I <Ia> <Ib> <Ic> --sigma <sigma> \
    > runs/molecules/${m}_freq.qrrho
done
```

(Molecular mass + principal moments of inertia for each gas-phase molecule
are pre-tabulated in `analysis/thermochem.xlsx` Notes sheet.)

Paste the values from each `.qrrho` file into `analysis/thermochem.xlsx`
on the Adsorbed / GasMolecules sheets; the DeltaG sheet auto-computes the
common-reference ΔG_n at 298 K and 623 K via cross-sheet INDEX/MATCH.

## Sensitivity check — 623 K (operating temperature)

To regenerate every input at T = 623.15 K instead of 298.15 K, run the
generator with `TC_TEMPERATURE` patched. Alternatively, post-process each
`.out` a second time with `--T 623.15`; the harmonic frequencies don't
change with temperature, only the partition-function evaluations, so a
second post-processing pass is much cheaper than redoing the SCFs.
