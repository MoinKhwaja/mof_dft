import pandas as pd

# Load the CSV files
csv1_path = '/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation /Screening_Scripts/Solvent_Stability/stable_percent_0_75_or_greater.csv'  
csv2_path = '/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation /Database/CSVs/2_bandgap_mofs.csv'               
output_path = '/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation /Database/CSVs/3_solvent_water_mofs.csv'         

# Read the data
csv1 = pd.read_csv(csv1_path)
csv2 = pd.read_csv(csv2_path)

# Check if the required columns exist
if 'File' in csv1.columns and 'qmof_id' in csv2.columns:
    # Find matching rows
    matching_rows = csv2[csv2['qmof_id'].isin(csv1['File'])]
    
    # Save to a new CSV file
    matching_rows.to_csv(output_path, index=False)
    print(f"Matching rows saved to: {output_path}")
else:
    print("Required columns ('file', 'qmof_id') are missing in the datasets.")
