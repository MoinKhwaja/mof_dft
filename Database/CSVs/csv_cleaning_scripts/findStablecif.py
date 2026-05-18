import os
import shutil
import pandas as pd

# Define the paths
csv_path = '/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation /Database/CSVs/3_solvent_water_mofs.csv'         # Replace with your CSV file path
source_folder = '/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation /Screening_Scripts/Water_Stability/Fingerprinting/cifs_to_read'   # Replace with your folder containing CIF files
destination_folder = '/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation /Screening_Scripts/Solvent_Stability/passing_cifs'  # Replace with your desired output folder

# Read the CSV file
data = pd.read_csv(csv_path)

# Ensure the destination folder exists
os.makedirs(destination_folder, exist_ok=True)

# Check if 'qmof_id' exists in the CSV
if 'qmof_id' in data.columns:
    # Loop through each qmof_id
    for qmof_id in data['qmof_id']:
        cif_filename = f"{qmof_id}.cif"
        source_file_path = os.path.join(source_folder, cif_filename)
        destination_file_path = os.path.join(destination_folder, cif_filename)
        
        # Check if the CIF file exists in the source folder
        if os.path.exists(source_file_path):
            # Move the file to the destination folder
            shutil.move(source_file_path, destination_file_path)
            print(f"Moved: {cif_filename}")
        else:
            print(f"File not found: {cif_filename}")
else:
    print("The column 'qmof_id' does not exist in the provided CSV file.")
