import pandas as pd

# Define the RACs and geo features required
RACs = [
    'D_func-I-0-all', 'D_func-I-1-all', 'D_func-I-2-all', 'D_func-I-3-all',
    'D_func-S-0-all', 'D_func-S-1-all', 'D_func-S-2-all', 'D_func-S-3-all',
    'D_func-T-0-all', 'D_func-T-1-all', 'D_func-T-2-all', 'D_func-T-3-all',
    'D_func-Z-0-all', 'D_func-Z-1-all', 'D_func-Z-2-all', 'D_func-Z-3-all',
    'D_func-chi-0-all', 'D_func-chi-1-all', 'D_func-chi-2-all',
    'D_func-chi-3-all', 'D_lc-I-0-all', 'D_lc-I-1-all', 'D_lc-I-2-all',
    'D_lc-I-3-all', 'D_lc-S-0-all', 'D_lc-S-1-all', 'D_lc-S-2-all',
    'D_lc-S-3-all', 'D_lc-T-0-all', 'D_lc-T-1-all', 'D_lc-T-2-all',
    'D_lc-T-3-all', 'D_lc-Z-0-all', 'D_lc-Z-1-all', 'D_lc-Z-2-all',
    'D_lc-Z-3-all', 'D_lc-chi-0-all', 'D_lc-chi-1-all', 'D_lc-chi-2-all',
    'D_lc-chi-3-all', 'D_mc-I-0-all', 'D_mc-I-1-all', 'D_mc-I-2-all',
    'D_mc-I-3-all', 'D_mc-S-0-all', 'D_mc-S-1-all', 'D_mc-S-2-all',
    'D_mc-S-3-all', 'D_mc-T-0-all', 'D_mc-T-1-all', 'D_mc-T-2-all',
    'D_mc-T-3-all', 'D_mc-Z-0-all', 'D_mc-Z-1-all', 'D_mc-Z-2-all',
    'D_mc-Z-3-all', 'D_mc-chi-0-all', 'D_mc-chi-1-all', 'D_mc-chi-2-all',
    'D_mc-chi-3-all', 'f-I-0-all', 'f-I-1-all', 'f-I-2-all', 'f-I-3-all',
    'f-S-0-all', 'f-S-1-all', 'f-S-2-all', 'f-S-3-all', 'f-T-0-all', 'f-T-1-all',
    'f-T-2-all', 'f-T-3-all', 'f-Z-0-all', 'f-Z-1-all', 'f-Z-2-all', 'f-Z-3-all',
    'f-chi-0-all', 'f-chi-1-all', 'f-chi-2-all', 'f-chi-3-all', 'f-lig-I-0',
    'f-lig-I-1', 'f-lig-I-2', 'f-lig-I-3', 'f-lig-S-0', 'f-lig-S-1', 'f-lig-S-2',
    'f-lig-S-3', 'f-lig-T-0', 'f-lig-T-1', 'f-lig-T-2', 'f-lig-T-3', 'f-lig-Z-0',
    'f-lig-Z-1', 'f-lig-Z-2', 'f-lig-Z-3', 'f-lig-chi-0', 'f-lig-chi-1',
    'f-lig-chi-2', 'f-lig-chi-3', 'func-I-0-all', 'func-I-1-all',
    'func-I-2-all', 'func-I-3-all', 'func-S-0-all', 'func-S-1-all',
    'func-S-2-all', 'func-S-3-all', 'func-T-0-all', 'func-T-1-all',
    'func-T-2-all', 'func-T-3-all', 'func-Z-0-all', 'func-Z-1-all',
    'func-Z-2-all', 'func-Z-3-all', 'func-chi-0-all', 'func-chi-1-all',
    'func-chi-2-all', 'func-chi-3-all', 'lc-I-0-all', 'lc-I-1-all', 'lc-I-2-all',
    'lc-I-3-all', 'lc-S-0-all', 'lc-S-1-all', 'lc-S-2-all', 'lc-S-3-all',
    'lc-T-0-all', 'lc-T-1-all', 'lc-T-2-all', 'lc-T-3-all', 'lc-Z-0-all',
    'lc-Z-1-all', 'lc-Z-2-all', 'lc-Z-3-all', 'lc-chi-0-all', 'lc-chi-1-all',
    'lc-chi-2-all', 'lc-chi-3-all', 'mc-I-0-all', 'mc-I-1-all', 'mc-I-2-all',
    'mc-I-3-all', 'mc-S-0-all', 'mc-S-1-all', 'mc-S-2-all', 'mc-S-3-all',
    'mc-T-0-all', 'mc-T-1-all', 'mc-T-2-all', 'mc-T-3-all', 'mc-Z-0-all',
    'mc-Z-1-all', 'mc-Z-2-all', 'mc-Z-3-all', 'mc-chi-0-all', 'mc-chi-1-all',
    'mc-chi-2-all', 'mc-chi-3-all'
]
geo = [
    'Df', 'Di', 'Dif', 'GPOAV', 'GPONAV', 'GPOV', 'GSA', 'POAV', 'POAV_vol_frac',
    'PONAV', 'PONAV_vol_frac', 'VPOV', 'VSA', 'cell_v'
]
required_features = RACs + geo

# Function to debug the descriptors CSV
def debug_descriptors(descriptor_csv):
    try:
        df = pd.read_csv(descriptor_csv)
        print(f"Number of columns in descriptors CSV: {len(df.columns)}")
        print(f"Column names in descriptors CSV: {list(df.columns)}")

        missing_features = [feature for feature in required_features if feature not in df.columns]
        extra_features = [feature for feature in df.columns if feature not in required_features]

        if missing_features:
            print(f"Missing features: {missing_features}")
        else:
            print("No missing features.")

        if extra_features:
            print(f"Extra features: {extra_features}")
        else:
            print("No extra features.")

        # Check for NaN percentages
        nan_percentages = df[required_features].isna().mean() * 100
        high_nan_features = nan_percentages[nan_percentages > 0].sort_values(ascending=False)

        if not high_nan_features.empty:
            print("\nFeatures with NaN values (percentage):")
            print(high_nan_features)
        else:
            print("No NaN values found in required features.")

        df_filtered = df.dropna(subset=required_features)
        print(f"Number of rows after dropping NaNs for required features: {df_filtered.shape[0]}")
        return df_filtered

    except Exception as e:
        print(f"Error while debugging descriptors CSV: {e}")


# Example usage
if __name__ == "__main__":
    descriptor_csv_path = "/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Screening_Scripts/Solvent_Stability/filtered_descriptors.csv"  # Update with your CSV path
    debug_descriptors(descriptor_csv_path)
