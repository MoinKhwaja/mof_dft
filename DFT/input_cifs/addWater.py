from ase.io import read, write
from ase.build import molecule
from ase.geometry import distance
import numpy as np

structure = read("your_structure.cif")

h2o = molecule("H2O")

existing_positions = structure.get_positions()

box_buffer = 30  # Å
center = np.mean(existing_positions, axis=0)
trial_center = center + np.array([box_buffer, 0, 0])  

for i, atom in enumerate(h2o):
    atom.position += trial_center

too_close = True
while too_close:
    too_close = False
    for pos in h2o.get_positions():
        distances = np.linalg.norm(existing_positions - pos, axis=1)
        if np.any(distances < 15.0):
            trial_center += np.array([5.0, 0.0, 0.0])  
            for i, atom in enumerate(h2o):
                atom.position += np.array([5.0, 0.0, 0.0])
            too_close = True
            break

structure += h2o

write("structure_with_water.cif", structure)
print("Water molecule added at least 15 Å from all atoms.")
