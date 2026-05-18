import pandas as pd


input_csv_path = "/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Database/qmof_database/CSVs/Misc_CSVs/bandgap_mofs_addedWaterStable.csv" 
output_filtered_csv_path = "/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Database/qmof_database/CSVs/output.csv" 

df = pd.read_csv(input_csv_path)

filtered_df = df[df['water_stable'] >= 0.70]
filtered_df.to_csv(output_filtered_csv_path, index=False)

print(f"Filtered rows saved to {output_filtered_csv_path}")
