#!/usr/bin/env python3
"""Build paired NEB endpoint xyz files for R2-2.

Reads converged s_n / s_{n+1} geometries from DFT/complete_dft_input/<id>/,
augments each endpoint with the participating gas-phase molecule(s) needed
to make atom counts match, and writes endpoint_A.xyz / endpoint_B.xyz with
matching element-by-index ordering ready for CP2K CI-NEB.

Usage:
    python build_neb_endpoints.py <material_id> <transition>

    material_id: 0e64acd | 52ef7e9 | 91692c9 | 07c07d3 | 74ace65
    transition : s0_to_s1 | s1_to_s2 | s2_to_s3 | s3_to_s4 | s4_to_s5
"""

import math
import sys
from pathlib import Path

REPO = Path("/gs/fs/tga-harada/Moin/HTP_MOF/HTS_MOF_Hydrogenation")

MATERIAL_PATH = {
    "0e64acd": REPO / "DFT/complete_dft_input/0e64acd/input",
    "52ef7e9": REPO / "DFT/complete_dft_input/52ef7e9",
    "91692c9": REPO / "DFT/complete_dft_input/91692c9",
    "07c07d3": REPO / "DFT/complete_dft_input/07c07d3",
    "74ace65": REPO / "DFT/complete_dft_input/74ace65",
}

FRAMEWORK_SIZE = {
    "0e64acd": 200,
    "52ef7e9": 86,
    "91692c9": 156,
    "07c07d3": 192,
    "74ace65": 98,
}

ACTIVE_METALS = {"Al", "Zn", "Mg", "Cu", "Fe", "Ni", "Cd", "In", "Nd", "Tb"}

GAS_PHASE_OFFSET = 3.5  # Å beyond the bonded active C
CO2_CO_BOND = 1.16
H2_HH_BOND = 0.74
H2O_OH_BOND = 0.96
H2O_HOH_ANGLE = math.radians(104.5)

OUTPUT_BASE = REPO / "Review_one/new_calc/R2-2_cineb_kinetics/inputs"


def read_xyz(path):
    """Read xyz; if multi-frame trajectory, return the LAST frame (converged geometry)."""
    with open(path) as f:
        lines = f.readlines()
    n = int(lines[0].strip())
    frame_len = n + 2
    n_frames = len(lines) // frame_len
    last_start = (n_frames - 1) * frame_len
    comment = lines[last_start + 1].rstrip("\n")
    atoms = []
    for line in lines[last_start + 2:last_start + 2 + n]:
        parts = line.split()
        atoms.append((parts[0], float(parts[1]), float(parts[2]), float(parts[3])))
    return n, comment, atoms


def write_xyz(path, atoms, comment):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(f"{len(atoms)}\n")
        f.write(f"{comment}\n")
        for el, x, y, z in atoms:
            f.write(f"  {el:2s}  {x:18.10f}  {y:18.10f}  {z:18.10f}\n")


def vsub(a, b): return tuple(x - y for x, y in zip(a, b))
def vadd(a, b): return tuple(x + y for x, y in zip(a, b))
def vscale(a, s): return tuple(x * s for x in a)
def vdist(a, b): return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def read_cell_from_cif(path):
    """Parse _cell_length_{a,b,c} and _cell_angle_{alpha,beta,gamma} from CIF.
    Returns (a_vec, b_vec, c_vec) as Cartesian lattice vectors."""
    a = b = c = alpha = beta = gamma = None
    with open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 2:
                continue
            key, val = parts[0], parts[1]
            if key == "_cell_length_a": a = float(val)
            elif key == "_cell_length_b": b = float(val)
            elif key == "_cell_length_c": c = float(val)
            elif key == "_cell_angle_alpha": alpha = math.radians(float(val))
            elif key == "_cell_angle_beta": beta = math.radians(float(val))
            elif key == "_cell_angle_gamma": gamma = math.radians(float(val))
    a_vec = (a, 0.0, 0.0)
    b_vec = (b * math.cos(gamma), b * math.sin(gamma), 0.0)
    cx = c * math.cos(beta)
    cy = c * (math.cos(alpha) - math.cos(beta) * math.cos(gamma)) / math.sin(gamma)
    cz = math.sqrt(max(c * c - cx * cx - cy * cy, 0.0))
    c_vec = (cx, cy, cz)
    return a_vec, b_vec, c_vec


def pbc_min_dist(p1, p2, cell):
    """Min distance between p1 and p2 considering 27 nearest periodic images."""
    a_v, b_v, c_v = cell
    md = float("inf")
    for ia in (-1, 0, 1):
        for ib in (-1, 0, 1):
            for ic in (-1, 0, 1):
                sx = ia * a_v[0] + ib * b_v[0] + ic * c_v[0]
                sy = ia * a_v[1] + ib * b_v[1] + ic * c_v[1]
                sz = ia * a_v[2] + ib * b_v[2] + ic * c_v[2]
                d = math.sqrt((p1[0] - p2[0] - sx) ** 2
                              + (p1[1] - p2[1] - sy) ** 2
                              + (p1[2] - p2[2] - sz) ** 2)
                if d < md:
                    md = d
    return md


def fibonacci_sphere(n):
    """Return n unit vectors approximately evenly distributed on a sphere."""
    pts = []
    phi = math.pi * (3.0 - math.sqrt(5.0))  # golden angle
    for i in range(n):
        y = 1.0 - (i / float(n - 1)) * 2.0
        radius = math.sqrt(max(1.0 - y * y, 0.0))
        theta = phi * i
        pts.append((math.cos(theta) * radius, y, math.sin(theta) * radius))
    return pts


def find_best_gas_placement(active_c_pos, all_atoms, cell, n_dirs=400,
                             offsets=(3.5, 3.75, 4.0, 4.25, 4.5)):
    """Scan directions and offsets; pick the (direction, offset) maximizing min PBC distance.

    Goal: gas-phase center is ≥3 Å from any atom and 3.5–4.5 Å from the active C."""
    best = None
    best_d = -1.0
    best_off = None
    for direction in fibonacci_sphere(n_dirs):
        for off in offsets:
            cand = vadd(active_c_pos, vscale(direction, off))
            md = min(pbc_min_dist(cand, pos(a), cell) for a in all_atoms)
            if md > best_d:
                best_d = md
                best = direction
                best_off = off
    return best, best_off, best_d


def vnorm(a):
    n = math.sqrt(sum(x * x for x in a))
    return tuple(x / n for x in a) if n else (0.0, 0.0, 0.0)


def vcross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def pos(atom):
    return (atom[1], atom[2], atom[3])


def find_active_metal(framework, active_c_pos):
    cands = [a for a in framework if a[0] in ACTIVE_METALS]
    if not cands:
        raise RuntimeError("No active metal found in framework")
    best = min(cands, key=lambda a: vdist(pos(a), active_c_pos))
    return best


def get_active_c(active_atoms):
    cs = [a for a in active_atoms if a[0] == "C"]
    if len(cs) != 1:
        raise RuntimeError(f"Expected exactly 1 C in active region, got {len(cs)}")
    return pos(cs[0])


def extract_h2o_from_s5(s5_active):
    os_ = [a for a in s5_active if a[0] == "O"]
    if len(os_) != 1:
        raise RuntimeError(f"Expected 1 O in s5 active (the H2O O), got {len(os_)}")
    o = os_[0]
    hs = [a for a in s5_active if a[0] == "H"]
    hs.sort(key=lambda h: vdist(pos(h), pos(o)))
    return [o, hs[0], hs[1]]


ELEMENT_ORDER = {"O": 0, "C": 1, "H": 2}


def sort_active(atoms):
    return sorted(atoms, key=lambda a: (ELEMENT_ORDER.get(a[0], 99), a[1], a[2], a[3]))


def split_fw_act(atoms, fw_size):
    return atoms[:fw_size], atoms[fw_size:]


def build_co2(center, axis):
    """C at center, O atoms along axis (perpendicular to approach)."""
    o1 = vadd(center, vscale(axis, CO2_CO_BOND))
    o2 = vadd(center, vscale(axis, -CO2_CO_BOND))
    return [("C",) + center, ("O",) + o1, ("O",) + o2]


def build_h2(center, axis):
    """H2 midpoint at center, oriented along axis."""
    h1 = vadd(center, vscale(axis, H2_HH_BOND / 2))
    h2 = vadd(center, vscale(axis, -H2_HH_BOND / 2))
    return [("H",) + h1, ("H",) + h2]


def build_h2o(o_center, axis1, axis2):
    """H2O with O at o_center; H atoms in the (axis1, axis2) plane at 104.5° opening."""
    half = H2O_HOH_ANGLE / 2
    dir1 = vadd(vscale(axis1, math.cos(half)), vscale(axis2, math.sin(half)))
    dir2 = vadd(vscale(axis1, math.cos(half)), vscale(axis2, -math.sin(half)))
    h1 = vadd(o_center, vscale(vnorm(dir1), H2O_OH_BOND))
    h2 = vadd(o_center, vscale(vnorm(dir2), H2O_OH_BOND))
    return [("O",) + o_center, ("H",) + h1, ("H",) + h2]


def main():
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    material, transition = sys.argv[1], sys.argv[2]

    if material not in MATERIAL_PATH:
        sys.exit(f"Unknown material: {material}")
    valid_tr = ["s0_to_s1", "s1_to_s2", "s2_to_s3", "s3_to_s4", "s4_to_s5"]
    if transition not in valid_tr:
        sys.exit(f"Unknown transition: {transition}")

    n_from = int(transition.split("_to_")[0][1:])
    n_to = int(transition.split("_to_")[1][1:])

    path = MATERIAL_PATH[material]
    fw_size = FRAMEWORK_SIZE[material]

    _, _, atoms_a = read_xyz(path / f"s{n_from}-pos-1.xyz")
    _, _, atoms_b = read_xyz(path / f"s{n_to}-pos-1.xyz")

    fw_a, act_a = split_fw_act(atoms_a, fw_size)
    fw_b, act_b = split_fw_act(atoms_b, fw_size)

    # Framework element-order sanity check
    fw_a_els = [a[0] for a in fw_a]
    fw_b_els = [a[0] for a in fw_b]
    if fw_a_els != fw_b_els:
        sys.exit(f"Framework element order differs between s{n_from} and s{n_to}")

    # Reference C: prefer whichever endpoint has the C still bonded near the metal.
    # s0 has no C → use s1's C; s5 has CH4 desorbed into the pore → use s4's C.
    # For other transitions both A and B work; pick A by default.
    if n_from == 0:
        active_c_pos = get_active_c(act_b)
    else:
        active_c_pos = get_active_c(act_a)
    metal = find_active_metal(fw_b, active_c_pos)
    metal_pos = pos(metal)

    # Read cell vectors for PBC-aware placement
    cif_path = path / f"s{n_to}.cif"
    cell = read_cell_from_cif(cif_path)

    # Scan directions and offsets; pick combo maximizing PBC clearance.
    direction, offset, clearance = find_best_gas_placement(active_c_pos, atoms_b, cell)
    gas_center = vadd(active_c_pos, vscale(direction, offset))

    # Perpendicular axis for molecule orientation
    ref = (0.0, 0.0, 1.0) if abs(direction[2]) < 0.9 else (1.0, 0.0, 0.0)
    perp = vnorm(vcross(direction, ref))

    extra_a, extra_b = [], []

    if transition == "s0_to_s1":
        extra_a = build_co2(gas_center, perp)
    elif transition == "s1_to_s2":
        extra_a = build_h2(gas_center, perp)
    elif transition == "s2_to_s3":
        extra_a = build_h2(gas_center, perp)
    elif transition == "s3_to_s4":
        extra_a = build_h2(gas_center, perp)
        # H2O on B side: place at the same scanned gas_center, with OH bonds in the
        # plane defined by `perp` and a second axis orthogonal to (direction, perp).
        perp2 = vnorm(vcross(direction, perp))
        extra_b = build_h2o(gas_center, perp, perp2)
    elif transition == "s4_to_s5":
        extra_a = build_h2(gas_center, perp)

    combined_a = list(fw_a) + sort_active(list(act_a) + extra_a)
    combined_b = list(fw_b) + sort_active(list(act_b) + extra_b)

    # Sanity: same count and same element at each index
    if len(combined_a) != len(combined_b):
        sys.exit(f"Total atom mismatch: A={len(combined_a)}, B={len(combined_b)}")
    bad = [(i, a[0], b[0]) for i, (a, b) in enumerate(zip(combined_a, combined_b)) if a[0] != b[0]]
    if bad:
        print(f"FATAL: {len(bad)} index/element mismatches:", file=sys.stderr)
        for i, ea, eb in bad[:10]:
            print(f"  idx {i}: A={ea}, B={eb}", file=sys.stderr)
        sys.exit(2)

    out_dir = OUTPUT_BASE / material / transition
    write_xyz(out_dir / "endpoint_A.xyz", combined_a,
              f"{material} {transition} A (s{n_from} augmented)")
    write_xyz(out_dir / "endpoint_B.xyz", combined_b,
              f"{material} {transition} B (s{n_to} augmented)")

    # Report (PBC-aware min distances)
    min_dist_a = min(
        (pbc_min_dist(pos(g), pos(f), cell) for g in extra_a for f in fw_a + act_a),
        default=float("inf"))
    min_dist_b = min(
        (pbc_min_dist(pos(g), pos(f), cell) for g in extra_b for f in fw_b + act_b),
        default=float("inf"))

    print(f"Material:        {material}  ({len(fw_a)}-atom framework)")
    print(f"Transition:      {transition}")
    print(f"Active metal:    {metal[0]} at {metal_pos[0]:.3f}, {metal_pos[1]:.3f}, {metal_pos[2]:.3f}")
    print(f"Active C ref:    {active_c_pos[0]:.3f}, {active_c_pos[1]:.3f}, {active_c_pos[2]:.3f}")
    print(f"|M-C| = {vdist(metal_pos, active_c_pos):.3f} Å")
    print(f"Chosen gas-phase offset: {offset:.2f} Å  (clearance: {clearance:.3f} Å)")
    print(f"Gas-phase center: {gas_center[0]:.3f}, {gas_center[1]:.3f}, {gas_center[2]:.3f}")
    if extra_a:
        print(f"Added to A ({len(extra_a)} atoms): {[a[0] for a in extra_a]}")
        print(f"  min dist from any added atom to existing atom: {min_dist_a:.3f} Å")
    if extra_b:
        print(f"Added to B ({len(extra_b)} atoms): {[a[0] for a in extra_b]}")
        print(f"  min dist from any added atom to existing atom: {min_dist_b:.3f} Å")
    print(f"Wrote {out_dir}/endpoint_A.xyz ({len(combined_a)} atoms)")
    print(f"Wrote {out_dir}/endpoint_B.xyz ({len(combined_b)} atoms)")


if __name__ == "__main__":
    main()
