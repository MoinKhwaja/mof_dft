"""Generate gas-phase RRHO frequency inputs for CO2 / H2 / H2O / CH4.

Reuses the converged geometries and wavefunctions already at
mof_dft/DFT/complete_dft_input/molecules/<mol>-pos-1.xyz (+ .wfn). Each input
restarts the SCF from the existing wfn, then does a full Hessian vibrational
analysis and writes thermochemistry.
"""
from __future__ import annotations
import re
import shutil
from pathlib import Path

ROOT = Path("/sessions/serene-compassionate-mayer/mnt/mof_dft")
SRC  = ROOT / "DFT" / "complete_dft_input" / "molecules"
DST  = ROOT / "Review_one" / "new_calc" / "R2-3_zpe_entropy" / "runs" / "molecules"
DST.mkdir(parents=True, exist_ok=True)

# (name, symmetry_number, multiplicity, linear_yn)
MOLS = [
    ("co2", 2, 1, True),
    ("h2",  2, 1, True),
    ("h2o", 2, 1, False),
    ("ch4", 12, 1, False),
]

INP_TEMPLATE = """!! R2-3 gas-phase RRHO frequency input — generated automatically.
!! Molecule: {mol}  symmetry_number={sigma}  linear={linear}

&GLOBAL
  PROJECT_NAME      {mol}_freq
  PRINT_LEVEL       MEDIUM
  RUN_TYPE          VIBRATIONAL_ANALYSIS
&END GLOBAL

&VIBRATIONAL_ANALYSIS
  DX               0.005
  NPROC_REP        4
  FULLY_PERIODIC   .FALSE.

  TC_PRESSURE      101325.0
  TC_TEMPERATURE   298.15

  THERMOCHEMISTRY  .TRUE.
  SYMMETRY_NUMBER  {sigma}

  &PRINT
    &MOLDEN_VIB
      ON
    &END MOLDEN_VIB
  &END PRINT
&END VIBRATIONAL_ANALYSIS

&FORCE_EVAL
  METHOD Quickstep

  &DFT
    BASIS_SET_FILE_NAME  /home/3/uh03203/Documents/cp2k/data/BASIS_MOLOPT_UCL
    BASIS_SET_FILE_NAME  /home/3/uh03203/Documents/cp2k/data/BASIS_MOLOPT
    POTENTIAL_FILE_NAME  /home/3/uh03203/Documents/cp2k/data/GTH_POTENTIALS
    BASIS_SET_FILE_NAME  /home/3/uh03203/Documents/cp2k/data/BASIS_SET

    MULTIPLICITY  {multiplicity}

    &MGRID
      CUTOFF       450
      REL_CUTOFF   60
      NGRIDS       4
    &END MGRID

    &QS
      METHOD GPW
    &END QS

    &SCF
      SCF_GUESS  RESTART
      EPS_SCF    1.0E-7
      MAX_SCF    200
      &OT
        MINIMIZER       DIIS
        PRECONDITIONER  FULL_SINGLE_INVERSE
      &END OT
    &END SCF

    &XC
      &XC_FUNCTIONAL PBE
      &END XC_FUNCTIONAL
      &vdW_POTENTIAL
        DISPERSION_FUNCTIONAL  PAIR_POTENTIAL
        &PAIR_POTENTIAL
          TYPE                  DFTD3
          REFERENCE_FUNCTIONAL  PBE
          PARAMETER_FILE_NAME   /home/3/uh03203/Documents/cp2k/data/dftd3.dat
          R_CUTOFF              10
        &END PAIR_POTENTIAL
      &END vdW_POTENTIAL
    &END XC
  &END DFT

  @INCLUDE '{mol}_freq.subsys'
&END FORCE_EVAL
"""

SUBSYS_TEMPLATE = """ &SUBSYS
     &CELL
        ABC 15.0 15.0 15.0
        PERIODIC NONE
     &END CELL

     &TOPOLOGY
       COORD_FILE_FORMAT XYZ
       COORD_FILE_NAME   {mol}_final.xyz
       CONN_FILE_FORMAT  OFF
     &END TOPOLOGY

    &KIND H
      ELEMENT      H
      BASIS_SET    DZVP-MOLOPT-GTH
      POTENTIAL    GTH-PBE-q1
    &END KIND

    &KIND C
      ELEMENT      C
      BASIS_SET    DZVP-MOLOPT-GTH
      POTENTIAL    GTH-PBE-q4
    &END KIND

    &KIND O
      ELEMENT      O
      BASIS_SET    DZVP-MOLOPT-GTH
      POTENTIAL    GTH-PBE-q6
    &END KIND
  &END SUBSYS
"""

JOB_TEMPLATE = """#!/bin/sh
#$ -cwd
#$ -l node_f=1
#$ -l h_rt=04:00:00
#$ -N r23_molecules
#$ -m be
#$ -M khwaja.m.aa@m.titech.ac.jp

# R2-3 gas-phase RRHO frequencies for CO2 / H2 / H2O / CH4.
# Copy each parent wavefunction next to its freq input before submitting:
#   for m in co2 h2 h2o ch4; do
#     ln -sf ../../../../DFT/complete_dft_input/molecules/${m}-RESTART.wfn ${m}_freq-RESTART.wfn
#   done

module load cp2k

for MOL in co2 h2 h2o ch4; do
  echo "=== $MOL_freq @ $(date) ==="
  mpirun -np 4 cp2k.psmp -i ${MOL}_freq.inp -o ${MOL}_freq.out
done
"""


def parse_last_frame(xyz_path: Path):
    lines = xyz_path.read_text().splitlines()
    headers = [i for i, ln in enumerate(lines) if ln.strip().isdigit()]
    n = int(lines[headers[-1]].strip())
    start = headers[-1] + 2
    out = []
    for ln in lines[start: start + n]:
        parts = ln.split()
        out.append((parts[0], float(parts[1]), float(parts[2]), float(parts[3])))
    return out


def write_xyz(path, atoms, comment=""):
    with path.open("w") as f:
        f.write(f"{len(atoms)}\n{comment}\n")
        for el, x, y, z in atoms:
            f.write(f"{el:<4s} {x:18.10f} {y:18.10f} {z:18.10f}\n")


for mol, sigma, mult, linear in MOLS:
    src_xyz = SRC / f"{mol}-pos-1.xyz"
    if not src_xyz.exists():
        print(f"  SKIP {mol}: {src_xyz} not found")
        continue
    atoms = parse_last_frame(src_xyz)
    write_xyz(DST / f"{mol}_final.xyz", atoms, comment=f"{mol} final converged geometry")
    (DST / f"{mol}_freq.inp").write_text(INP_TEMPLATE.format(
        mol=mol, sigma=sigma, multiplicity=mult, linear=linear,
    ))
    (DST / f"{mol}_freq.subsys").write_text(SUBSYS_TEMPLATE.format(mol=mol))
    print(f"  wrote {mol}: {len(atoms)} atoms, sigma={sigma}, linear={linear}")

(DST / "job.sh").write_text(JOB_TEMPLATE)
print(f"\nWrote job.sh to {DST/'job.sh'}")
