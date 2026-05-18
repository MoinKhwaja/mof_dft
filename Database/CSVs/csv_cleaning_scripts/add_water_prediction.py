import pandas as pd

csv1_path = "/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Database/CSVs/2_bandgap_mofs.csv"  # Replace with the actual path to the first CSV
csv2_path = "/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Screening_Scripts/Water_Stability/Predictions/test.csv"  # Replace with the actual path to the second CSV
output_csv_path = "/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Database/CSVs/Misc_CSVs/output_csv.csv"  # Replace with the desired path for the output CSV

df1 = pd.read_csv(csv1_path)  
df2 = pd.read_csv(csv2_path)  
df1['water_stable'] = float('nan')

for _, row in df2.iterrows():
    name = row['name']
    prediction = row['Predictions']
    df1.loc[df1['qmof_id'] == name, 'water_stable'] = prediction

df1.to_csv(output_csv_path, index=False)

print(f"Updated CSV with 'water_stable' column saved to {output_csv_path}")

