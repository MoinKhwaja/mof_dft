import pandas as pd

input_file = '/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Database/qmof_database/CSVs/1_porosity_mofs.csv'
output_file = '2_bandgap_mofs.csv'

df = pd.read_csv(input_file)

if 'outputs.pbe.bandgap' in df.columns:
    filtered_df = df[df['outputs.pbe.bandgap'] > 1.2]
    filtered_df.to_csv(output_file, index=False)
    print(f"Filtered rows saved to {output_file}.")
else:
    print("The column 'outputs.pbe.bandgap' does not exist in the input file.")
