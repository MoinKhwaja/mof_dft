import os
import pandas as pd
import shutil


csv_path = "/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Database/qmof_database/CSVs/2_bandgap_mofs.csv"
source_folder = "/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Database/qmof_database/Misc/relaxed_structures"
destination_folder = "/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Screening_Scripts/Water_Stability/Fingerprinting/cifs_to_read"


os.makedirs(destination_folder, exist_ok=True)


df = pd.read_csv(csv_path)
qmof_ids = df['qmof_id']


for qmof_id in qmof_ids:
    source_file = os.path.join(source_folder, f"{qmof_id}.cif")
    destination_file = os.path.join(destination_folder, f"{qmof_id}.cif")
    
    if os.path.exists(source_file):
        shutil.copy(source_file, destination_file)
        print(f"Copied: {source_file} -> {destination_file}")
    else:
        print(f"File not found: {source_file}")

print("All available CIF files have been copied.")
