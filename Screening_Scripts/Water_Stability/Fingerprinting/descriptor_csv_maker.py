import os
from generate_descriptors import descriptor_generator
import pandas as pd


input_folder = "/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Screening_Scripts/Water_Stability/Fingerprinting/cifs_to_read"
output_folder = "/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Screening_Scripts/Water_Stability/Fingerprinting/outputs"
output_csv_path = os.path.join(output_folder, "all_descriptors.csv")


os.makedirs(output_folder, exist_ok=True)


all_descriptors = pd.DataFrame()


for cif_file in os.listdir(input_folder):
    if cif_file.endswith(".cif"):  
       
        name = os.path.splitext(cif_file)[0]  
        cif_path = os.path.join(input_folder, cif_file)
        print(f"Processing {cif_path}...")
        
    
        try:
            descriptor_generator(name, cif_path=cif_path, output_folder=output_folder)
            
            
            descriptor_file = os.path.join(output_folder, f"{name}_descriptors.csv")
            if os.path.exists(descriptor_file):
                mof_descriptors = pd.read_csv(descriptor_file)
                all_descriptors = pd.concat([all_descriptors, mof_descriptors], ignore_index=True)
            else:
                print(f"Descriptor file not found for {name}. Skipping.")
        except Exception as e:
            print(f"Error processing {cif_file}: {e}")


all_descriptors.to_csv(output_csv_path, index=False)
print(f"All descriptors saved to {output_csv_path}")

