# R1-3 — Spin polarization

## Verbatim comment (Referee 1)

> It should be specified whether DFT calculations are performed with spin polarisation.

## Status

Original CP2K inputs used `MULTIPLICITY 1` and no `&UKS`, i.e. spin-restricted
closed-shell. This is defensible for the Zn(II) (d10), Mg(II), and Al(III)
candidates, but is *not* defensible for Ni-MOF-74 (qmof-ea9f3ea), where Ni(II)
in an octahedral O-environment carries unpaired d-electrons (typically high
spin, S = 1 per Ni; antiferromagnetic ordering between adjacent Ni centers).

## What to compute

1. **Closed-shell justification (text only, all candidates except Ni-MOF-74).**
   Add one paragraph to §2.2 citing the d0/d10/closed-shell argument; no new
   compute.
2. **Spin-polarized rerun of Ni-MOF-74 reaction profile (s0 -> s5).** Switch on
   `&UKS`, set `MULTIPLICITY` consistent with the chosen spin state, and provide
   `&BS` initial magnetization on each Ni atom (try high-spin ferromagnetic
   first, then antiferromagnetic if the FM solution looks suspicious).
3. **Compare energies and re-plot Figure 4 / re-fill Table S5 for that
   material** with the spin-polarized numbers.

## Inputs needed

- `DFT/complete_dft_input/ea9f3ea/s0.inp` … `s5.inp` (existing closed-shell
  inputs; clone and modify).
- `DFT/complete_dft_input/ea9f3ea/s*-RESTART.wfn` — do **not** restart from
  these; the wavefunction shape is wrong for UKS. Start with `SCF_GUESS ATOMIC`
  or `RESTART` after a fresh atomic SCF.
- BASIS_MOLOPT / GTH potentials already on TSUBAME.

## Suggested CP2K block (paste into &DFT)

```text
UKS .TRUE.
MULTIPLICITY  7        ! 6 Ni atoms x 2 unpaired e- each, ferromagnetic guess
&SCF
  SCF_GUESS ATOMIC
  &OT
    MINIMIZER DIIS
    PRECONDITIONER FULL_SINGLE_INVERSE
  &END OT
&END SCF
```

For an antiferromagnetic guess use `MULTIPLICITY 1` and `&BS` broken-symmetry
section with `+2, +2, +2, -2, -2, -2` on the six Ni centers.

## Expected outputs

- 6 new geometry-optimized structures (s0–s5) for Ni-MOF-74 with spin
  polarization on.
- Single-number comparison: ΔE(unpolarized) vs ΔE(polarized) per step.
- Decision: does the qualitative thermodynamic profile change? Update §3.2 and
  Table S5 accordingly.

## Cross-links

- Folder R2-3 (ZPE/entropy) must be run on the *final* geometries that come out
  of this folder for Ni-MOF-74.
- Folder R1-10 (hybrid band gap) can be done independently but should use the
  spin-polarized DFT setting once decided.

## Owner / status

Owner: MK · Status: open
