"""
Generate concrete CP2K vibrational-analysis (PHVA) input files for R2-3,
one bundle per (material, step), from the converged GEO_OPT outputs that
already live in mof_dft/DFT/complete_dft_input/<id>/.

Active subsystem heuristic per stationary point:
  - Adsorbate atoms = indices > n_bare (n_bare = atom count in s0-pos-1.xyz).
  - Active metal = the metal nearest the adsorbate centroid (for s0, every metal).
  - First coordination shell = atoms within R_FIRST_SHELL of the active metal.

Outputs are written to
  mof_dft/Review_one/new_calc/R2-3_zpe_entropy/runs/<id>/sN_freq.{inp,subsys}
plus a per-material job.sh and a single-frame sN_final.xyz extracted from the
last frame of the GEO_OPT trajectory.

Run with no arguments to process every candidate that has converged outputs;
pass IDs as positional args to restrict.
"""
from __future__ import annotations
import math
import re
import shutil
import sys
from pathlib import Path

# ------------------------------------------------------------------
ROOT          = Path("/sessions/serene-compassionate-mayer/mnt/mof_dft")
SRC_BASE      = ROOT / "DFT" / "complete_dft_input"
DST_BASE      = ROOT / "Review_one" / "new_calc" / "R2-3_zpe_entropy" / "runs"

METALS        = {"Ni", "Mg", "Zn", "Cu", "Co", "Fe", "Mn", "Al", "Ca", "Cr", "V", "Ti", "Cd", "In", "Nd", "Tb"}
R_FIRST_SHELL = 2.6        # Angstrom, M-O cutoff for first-shell donors
STEPS         = ["s0", "s1", "s2", "s3", "s4", "s5"]

# Pre-tuned wall-time per candidate based on cluster size (hours).
# Conservative; PHVA is independent across displacements so NPROC_REP can absorb it.
WALL_HOURS = {
    "ea9f3ea":  6,   #  54 atoms
    "9f8e842":  6,   #  72-80 atoms (when outputs land)
    "52ef7e9":  8,   #  86 atoms
    "74ace65":  8,   #  98 atoms
    "91692c9": 12,   # 156 atoms
    "07c07d3": 12,   # 192 atoms
    "0e64acd": 12,   # ~100 atoms
    "04c1119": 24,   # 428 atoms
}

# Source of the existing CP2K data files for each candidate. Most live directly
# under complete_dft_input/<id>/ ; 0e64acd lives in complete_dft_input/0e64acd/input/.
def src_dir(qid: str) -> Path:
    direct = SRC_BASE / qid
    nested = direct / "input"
    if (direct / f"s0-pos-1.xyz").exists():
        return direct
    if (nested / f"s0-pos-1.xyz").exists():
        return nested
    return direct   # default; caller will detect missing files


# ------------------------------------------------------------------
def parse_last_frame(xyz_path: Path) -> tuple[int, list[tuple[str, float, float, float]]]:
    """Return (n_atoms, [(element, x, y, z), ...]) for the LAST frame of a CP2K
    -pos-1.xyz trajectory."""
    with xyz_path.open() as f:
        lines = f.readlines()
    # find every header line (an integer alone)
    headers = [i for i, ln in enumerate(lines) if ln.strip().isdigit()]
    if not headers:
        raise RuntimeError(f"no frame header in {xyz_path}")
    n = int(lines[headers[-1]].strip())
    atoms_start = headers[-1] + 2     # skip header + comment
    atoms = []
    for ln in lines[atoms_start : atoms_start + n]:
        parts = ln.split()
        if len(parts) < 4:
            continue
        el = parts[0]
        x, y, z = (float(parts[1]), float(parts[2]), float(parts[3]))
        atoms.append((el, x, y, z))
    if len(atoms) != n:
        raise RuntimeError(f"frame parse mismatch in {xyz_path}: expected {n}, got {len(atoms)}")
    return n, atoms


def write_xyz(path: Path, atoms: list[tuple[str, float, float, float]], comment: str = "") -> None:
    with path.open("w") as f:
        f.write(f"{len(atoms)}\n{comment}\n")
        for el, x, y, z in atoms:
            f.write(f"{el:<4s} {x:18.10f} {y:18.10f} {z:18.10f}\n")


def dist(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def centroid(positions: list[tuple[float, float, float]]) -> tuple[float, float, float]:
    n = len(positions)
    return (sum(p[0] for p in positions) / n,
            sum(p[1] for p in positions) / n,
            sum(p[2] for p in positions) / n)


def pick_active_subsystem(atoms: list[tuple[str, float, float, float]], n_bare: int
                          ) -> tuple[list[int], dict]:
    """Return (1-based active atom indices, debug info)."""
    n = len(atoms)
    elements = [a[0] for a in atoms]
    coords   = [(a[1], a[2], a[3]) for a in atoms]

    adsorbate_idx0 = list(range(n_bare, n))     # 0-based
    metal_idx0     = [i for i, el in enumerate(elements) if el in METALS]

    if not metal_idx0:
        raise RuntimeError("no metal atoms detected — expected one of " + ",".join(METALS))

    # active metal = metal closest to adsorbate centroid; if no adsorbate (s0),
    # take the first metal as a representative and document this in the readme.
    if adsorbate_idx0:
        cen = centroid([coords[i] for i in adsorbate_idx0])
        active_metal_i = min(metal_idx0, key=lambda i: dist(coords[i], cen))
    else:
        # bare MOF (s0): include ALL metals so the active site is captured in either dimer
        active_metal_i = None

    # first-shell donors within R_FIRST_SHELL of the active metal (or every metal if s0)
    metals_to_shell = [active_metal_i] if active_metal_i is not None else metal_idx0
    first_shell: set[int] = set()
    for m in metals_to_shell:
        for j in range(n):
            if j == m or j in first_shell:
                continue
            if dist(coords[m], coords[j]) < R_FIRST_SHELL and elements[j] not in METALS:
                first_shell.add(j)

    active = set()
    if active_metal_i is not None:
        active.add(active_metal_i)
    else:
        active.update(metal_idx0)
    active.update(first_shell)
    active.update(adsorbate_idx0)

    one_based = sorted(i + 1 for i in active)
    debug = {
        "n_total": n,
        "n_bare": n_bare,
        "n_adsorbate": len(adsorbate_idx0),
        "active_metal_index": (active_metal_i + 1) if active_metal_i is not None else "ALL",
        "n_first_shell": len(first_shell),
        "n_active": len(active),
    }
    return one_based, debug


# ------------------------------------------------------------------
PHVA_TEMPLATE = """!! R2-3 PHVA frequency input — generated automatically.
!! Material: {qid}   Step: {step}
!! Active subsystem: {n_active} atoms (1-based) {{adsorbate={n_ads}, metal={metal_label}, 1st shell={n_first}}}
!! n_total = {n_total} atoms.

&GLOBAL
  PROJECT_NAME       {step}_freq
  PRINT_LEVEL        MEDIUM
  RUN_TYPE           VIBRATIONAL_ANALYSIS
&END GLOBAL

&VIBRATIONAL_ANALYSIS
  DX               0.005
  NPROC_REP        4
  FULLY_PERIODIC   .FALSE.
  TC_PRESSURE      101325.0
  TC_TEMPERATURE   298.15
  THERMOCHEMISTRY  .TRUE.

  &MODE_SELECTIVE
    &INVOLVED_ATOMS
      INVOLVED_ATOMS  {atom_list_wrapped}
    &END INVOLVED_ATOMS
  &END MODE_SELECTIVE

  &PRINT
    &MOLDEN_VIB
      ON
    &END MOLDEN_VIB
    &PROGRAM_RUN_INFO
      &EACH
        REPLICA_EVAL  1
      &END EACH
    &END PROGRAM_RUN_INFO
  &END PRINT
&END VIBRATIONAL_ANALYSIS

&FORCE_EVAL
  METHOD Quickstep

  &DFT
    BASIS_SET_FILE_NAME  /home/3/uh03203/Documents/cp2k/data/BASIS_MOLOPT_UCL
    BASIS_SET_FILE_NAME  /home/3/uh03203/Documents/cp2k/data/BASIS_MOLOPT
    POTENTIAL_FILE_NAME  /home/3/uh03203/Documents/cp2k/data/GTH_POTENTIALS
    BASIS_SET_FILE_NAME  /home/3/uh03203/Documents/cp2k/data/BASIS_ADMM_MOLOPT
    BASIS_SET_FILE_NAME  /home/3/uh03203/Documents/cp2k/data/BASIS_ADMM
    BASIS_SET_FILE_NAME  /home/3/uh03203/Documents/cp2k/data/BASIS_SET

    MULTIPLICITY  {multiplicity}

    &MGRID
      CUTOFF      450
      REL_CUTOFF  60
      NGRIDS      4
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
      &OUTER_SCF
        OPTIMIZER  DIIS
        EPS_SCF    1.0E-6
        MAX_SCF    100
      &END OUTER_SCF
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

  @INCLUDE '{step}_freq.subsys'
&END FORCE_EVAL
"""


SUBSYS_TEMPLATE = """ &SUBSYS
     &CELL
        CELL_FILE_FORMAT CIF
        CELL_FILE_NAME {step}.cif
     &END CELL

     &TOPOLOGY
       COORD_FILE_FORMAT XYZ
       COORD_FILE_NAME {step}_final.xyz
       CONN_FILE_FORMAT OFF
     &END TOPOLOGY

{kinds}
  &END SUBSYS
"""


JOB_TEMPLATE = """#!/bin/sh
#$ -cwd
#$ -l node_f=1
#$ -l h_rt={wall_hours:02d}:00:00
#$ -N r23_{qid}
#$ -m be
#$ -M khwaja.m.aa@m.titech.ac.jp

# R2-3 PHVA frequency calculations for {qid}
# Sequential s0 -> s5. Each step restarts SCF from the parent geo_opt wavefunction.
# Copy/symlink the parent wfn files into this directory before submitting:
#   for s in s0 s1 s2 s3 s4 s5; do
#     ln -sf ../../../../DFT/complete_dft_input/{qid_link}/${{s}}-RESTART.wfn   ${{s}}_freq-RESTART.wfn
#   done

module load cp2k

for STEP in {steps_joined}; do
  echo "=== $STEP_freq @ $(date) ==="
  mpirun -np 4 cp2k.psmp -i ${{STEP}}_freq.inp -o ${{STEP}}_freq.out
done
"""


def kind_block_from_parent(parent_subsys: Path) -> str:
    """Pull the &KIND ... &END KIND blocks from the parent .subsys verbatim."""
    text = parent_subsys.read_text()
    kinds = []
    pat = re.compile(r"&KIND[\s\S]+?&END KIND")
    for m in pat.finditer(text):
        kinds.append(m.group(0))
    if not kinds:
        # fallback: copy whole &SUBSYS internals other than CELL/TOPOLOGY
        return "    !! WARNING: no &KIND blocks recovered from parent subsys."
    return "\n\n".join("    " + k.replace("\n", "\n    ").rstrip() for k in kinds)


def chunk(seq: list, width: int = 12) -> str:
    """Pretty-print a long INVOLVED_ATOMS list with line continuations."""
    out_lines = []
    line = []
    for v in seq:
        line.append(str(v))
        if len(line) == width:
            out_lines.append(" ".join(line))
            line = []
    if line:
        out_lines.append(" ".join(line))
    return ("\n" + " " * 22).join(out_lines)


# ------------------------------------------------------------------
def generate_one(qid: str, manifest_rows: list[dict]) -> None:
    src = src_dir(qid)
    dst = DST_BASE / qid
    dst.mkdir(parents=True, exist_ok=True)
    print(f"\n=== {qid}  (src: {src})")

    # n_bare from s0 last frame
    pos0 = src / "s0-pos-1.xyz"
    if not pos0.exists():
        print(f"  SKIP {qid}: missing s0-pos-1.xyz at {pos0}")
        return
    n_bare, atoms0 = parse_last_frame(pos0)
    print(f"  n_bare (s0) = {n_bare}")

    for step in STEPS:
        pos = src / f"{step}-pos-1.xyz"
        if not pos.exists():
            print(f"    {step}: NO -pos-1.xyz, skipping")
            continue
        n_total, atoms = parse_last_frame(pos)

        # write the final-frame xyz next to the new freq inputs
        final_xyz = dst / f"{step}_final.xyz"
        write_xyz(final_xyz, atoms, comment=f"{qid} {step} final converged frame")

        # active subsystem indices
        active, debug = pick_active_subsystem(atoms, n_bare)
        print(f"    {step}: n_total={n_total}, adsorbate={debug['n_adsorbate']}, "
              f"active_metal={debug['active_metal_index']}, first_shell={debug['n_first_shell']}, "
              f"active_total={debug['n_active']}")

        # copy the structure .cif over so &CELL can find it
        src_cif = src / f"{step}.cif"
        if src_cif.exists():
            shutil.copy(src_cif, dst / f"{step}.cif")
        else:
            # fall back to s0.cif which has the same cell parameters
            shutil.copy(src / "s0.cif", dst / f"{step}.cif")

        # write subsys
        kinds = kind_block_from_parent(src / f"{step}.subsys")
        (dst / f"{step}_freq.subsys").write_text(
            SUBSYS_TEMPLATE.format(step=step, kinds=kinds)
        )

        # write inp
        atom_list_str = chunk(active, width=12)
        metal_label = str(debug["active_metal_index"])
        (dst / f"{step}_freq.inp").write_text(PHVA_TEMPLATE.format(
            qid=qid, step=step,
            n_active=debug["n_active"], n_ads=debug["n_adsorbate"],
            metal_label=metal_label, n_first=debug["n_first_shell"],
            n_total=debug["n_total"],
            atom_list_wrapped=atom_list_str,
            multiplicity=1,
        ))

        manifest_rows.append({
            "qid": qid,
            "step": step,
            "n_total": n_total,
            "n_active": debug["n_active"],
            "active_metal_index": metal_label,
            "n_adsorbate": debug["n_adsorbate"],
            "n_first_shell": debug["n_first_shell"],
            "input_file": str(dst / f"{step}_freq.inp"),
        })

    # write job.sh
    wall = WALL_HOURS.get(qid, 12)
    (dst / "job.sh").write_text(JOB_TEMPLATE.format(
        wall_hours=wall, qid=qid, qid_link=qid,
        steps_joined=" ".join(STEPS),
    ))
    print(f"  wrote job.sh  (wall {wall}h)")


# ------------------------------------------------------------------
def main() -> int:
    requested = sys.argv[1:] or [
        "04c1119", "ea9f3ea", "0e64acd", "52ef7e9",
        "91692c9", "07c07d3", "74ace65",
        # 9f8e842 is omitted -- still awaiting GEO_OPT outputs
    ]
    manifest_rows: list[dict] = []
    for qid in requested:
        try:
            generate_one(qid, manifest_rows)
        except Exception as e:
            print(f"  ERROR {qid}: {e}")

    # write manifest
    manifest = DST_BASE / "manifest.tsv"
    with manifest.open("w") as f:
        cols = ["qid", "step", "n_total", "n_active", "active_metal_index",
                "n_adsorbate", "n_first_shell", "input_file"]
        f.write("\t".join(cols) + "\n")
        for row in manifest_rows:
            f.write("\t".join(str(row[c]) for c in cols) + "\n")
    print(f"\nManifest: {manifest}")
    print(f"Total inputs generated: {len(manifest_rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
