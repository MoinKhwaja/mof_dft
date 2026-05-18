import pandas as pd
import numpy as np
from keras.models import load_model
from sklearn.preprocessing import StandardScaler

# Hardcoded model path
MODEL_PATH = "/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Screening_Scripts/Solvent_Stability/model/final_model_flag_few_epochs.h5"

# Full RAC and geo feature lists
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
geo = ['Df', 'Di', 'Dif', 'GPOAV', 'GPONAV',  'GSA', 'POAV', 
       'PONAV', 'VSA', 'cell_v']

def normalize_data_solvent(df_train, df_newMOF, fnames, lname, debug=False):
    """
    Normalizes training and test data, dropping NaN rows and applying scaling.
    """
    _df_train = df_train.copy().dropna(subset=fnames + lname)
    _df_newMOF = df_newMOF.copy().dropna(subset=fnames)
    X_train, X_newMOF = _df_train[fnames].values, _df_newMOF[fnames].values
    y_train = _df_train[lname].values

    if debug:
        print(f"Training data reduced from {len(df_train)} -> {len(y_train)} due to NaN.")

    x_scaler = StandardScaler()
    x_scaler.fit(X_train)
    X_train = x_scaler.transform(X_train)
    X_newMOF = x_scaler.transform(X_newMOF)
    y_train = np.array([1 if x == 1 else 0 for x in y_train.reshape(-1, )])
    return X_train, X_newMOF, y_train, x_scaler

def predict_solvent_stability(descriptor_csv, output_csv):
    """
    Predicts solvent stability for MOFs in the descriptors CSV.
    """
    # Load the trained model
    model = load_model(MODEL_PATH)

    # Load the training data for scaling
    train_df = pd.read_csv("/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Screening_Scripts/Solvent_Stability/model/train.csv")  # Replace with actual training data path
    train_df = train_df.loc[:, (train_df != train_df.iloc[0]).any()]  # Remove constant columns

    # Load the descriptors CSV
    descriptor_df = pd.read_csv(descriptor_csv)

    # Combine feature lists
    features = [val for val in train_df.columns.values if val in RACs + geo]

    # Normalize data
    X_train, X_test, y_train, _ = normalize_data_solvent(train_df, descriptor_df, features, ["flag"], debug=True)

    # Make predictions
    predictions = model.predict(X_test)
    predictions = np.round(predictions, 2)

    # Save predictions to CSV
    descriptor_df['Predictions'] = predictions
    descriptor_df.to_csv(output_csv, index=False)
    print(f"Predictions saved to {output_csv}")

