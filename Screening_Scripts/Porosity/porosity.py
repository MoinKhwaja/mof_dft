import pandas as pd

input_file = '/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Database/qmof_database/CSVs/qmof_adjusted_bandgap.csv'
output_file = 'porosity_mofs.csv'

df = pd.read_csv(input_file)

if 'info.pld' in df.columns:
    filtered_df = df[df['info.pld'] >= 4.5]
    filtered_df.to_csv(output_file, index=False)
    print(f"Filtered rows saved to {output_file}.")
else:
    print("The column 'info.pld' does not exist in the input file.")
