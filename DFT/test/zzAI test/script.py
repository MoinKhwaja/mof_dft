from ase.io import read, write
from ase.build import molecule
import numpy as np

# Load MOF structure
mof = read("/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation /DFT/input_cifs/zzAI test/s0.cif")

# Identify aluminum atoms
al_indices = [i for i, atom in enumerate(mof) if atom.symbol == "Al"]

# Choose the first Al atom
al_index = al_indices[0]
al_position = mof[al_index].position

# Create CO2 molecule (linear geometry)
co2 = molecule("CO2")

# Typical Al–O bond distance for adsorption
al_o_distance = 1  # Angstrom

# Vector from CO2 O to C (assuming O-C-O linear)
o_vector = co2[0].position - co2[1].position
o_vector /= np.linalg.norm(o_vector)

# Place O at desired distance from Al
co2_translation = al_position + o_vector * al_o_distance - co2[0].position
co2.translate(co2_translation)

# Combine MOF and CO2
combined = mof + co2
print("working")
# Save the result
write("s0_with_CO2.cif", combined)
