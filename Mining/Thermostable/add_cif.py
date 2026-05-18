import os
import shutil
import pandas as pd

def filter_and_copy_cifs(csv_file, source_directory, destination_directory):
    # Load the CSV file
    data = pd.read_csv(csv_file)

    # Get the list of qmof_id values from the CSV
    qmof_ids = data['qmof_id'].astype(str).tolist()

    # Ensure the destination directory exists
    os.makedirs(destination_directory, exist_ok=True)

    # Iterate through the files in the source directory
    for file_name in os.listdir(source_directory):
        # Check if the file name (without extension) is in the qmof_id list
        if file_name.endswith('.cif') and file_name[:-4] in qmof_ids:
            source_path = os.path.join(source_directory, file_name)
            destination_path = os.path.join(destination_directory, file_name)
            # Copy the .cif file to the destination directory
            shutil.copy(source_path, destination_path)

# Example usage
csv_file = '/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Database/CSVs/Misc_CSVs/water_stable_ge_0.75.csv'  # Replace with the actual path to the CSV file
source_directory = '/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Screening_Scripts/Water_Stability/Fingerprinting/cifs_to_read'  # Replace with the actual source directory path
destination_directory = '/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Mining/Thermostable/mof_cifs'  # Replace with the actual destination directory path

filter_and_copy_cifs(csv_file, source_directory, destination_directory)