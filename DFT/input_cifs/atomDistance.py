import os
from ase.io import read, write
from ase.neighborlist import NeighborList
import numpy as np

input_folder = "/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation /DFT/input_cifs/3fcf6ee/init"
output_folder = "/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation /DFT/input_cifs/3fcf6ee/init/fixed"
min_dist = 0.51

os.makedirs(output_folder, exist_ok=True)

def fix_close_contacts(atoms, min_dist):
    cutoffs = [min_dist] * len(atoms)
    nl = NeighborList(cutoffs, self_interaction=False, bothways=True)
    nl.update(atoms)

    moved = True
    while moved:
        moved = False
        for i in range(len(atoms)):
            indices, offsets = nl.get_neighbors(i)
            for j, offset in zip(indices, offsets):
                vec = atoms.positions[j] + np.dot(offset, atoms.get_cell()) - atoms.positions[i]
                dist = np.linalg.norm(vec)
                if dist < 0.5:
                    moved = True
                    direction = vec / dist
                    new_vec = direction * min_dist
                    atoms.positions[j] = atoms.positions[i] + new_vec - np.dot(offset, atoms.get_cell())
        nl.update(atoms)
    return atoms

for file in os.listdir(input_folder):
    if file.endswith(".cif"):
        filepath = os.path.join(input_folder, file)
        atoms = read(filepath)
        atoms = fix_close_contacts(atoms, min_dist)
        output_path = os.path.join(output_folder, file)
        write(output_path, atoms)
        print(f"Fixed and saved: {output_path}")
