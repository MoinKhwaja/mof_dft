import pandas as pd

input_file = '/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Database/qmof_database/CSVs/qmof.csv'
output_file = 'qmof_adjusted_bandgap.csv'

df = pd.read_csv(input_file)

if 'outputs.pbe.bandgap' in df.columns:
    df['outputs.pbe.bandgap'] = df['outputs.pbe.bandgap'] + 0.85
    df.to_csv(output_file, index=False)
    print(f"Adjusted bandgap values saved to {output_file}.")
else:
    print("The column 'outputs.pbe.bandgap' does not exist in the input file.")
