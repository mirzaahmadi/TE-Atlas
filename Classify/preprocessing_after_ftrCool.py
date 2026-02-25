"""
SCRIPT 4 - NOTE: This script is only preprocessing an UNLABELLED dataset after feature extraction

- This is the fourth script which will preprocess the dataset AFTER it has undergone feature extraction. It will:
    1. Remove all rows that contain invalid information in any variable (infinite values, NaN values)
    2. Scale the numerical data using the previously saved scaler
    3. Reduce to the previously selected top features using the saved selector
    4. Save the final preprocessed dataset to be used for model inference
"""

import pandas as pd
import numpy as np
from joblib import load

def main___preprocessing_after_ftr_cool(dataset, original_dataset_name, scaler_pkl, selector_pkl):
    print("\n")
    print("\n")
    print("-----------------------------------------------------------------------------------------------")
    print("STEP 4: Preprocess the dataset after feature extraction.")
    print("-----------------------------------------------------------------------------------------------")

    dataset = pd.read_csv(dataset)
    
    print("\nDataset head (5 rows):")
    print(dataset.head(5))
    print("\nDataset info:")
    dataset.info()

    features_df = dataset.iloc[:, 2:].copy()

    features_df = features_df.apply(pd.to_numeric, errors='coerce')

    print("\nBefore filtering:")
    print("Number of inf values:", np.isinf(features_df.select_dtypes(include=[np.number])).sum().sum())
    print("Number of NaN values:", np.isnan(features_df.select_dtypes(include=[np.number])).sum().sum())

    features_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    features_df.dropna(inplace=True)

    sequence_id_col = dataset.loc[features_df.index, 'Sequence_ID'].reset_index(drop=True)
    sequence_content_col = dataset.loc[features_df.index, 'sequence_content'].reset_index(drop=True)
    features_df = features_df.reset_index(drop=True)

    print("\nAfter filtering:")
    print("Number of inf values:", np.isinf(features_df).sum().sum())
    print("Number of NaN values:", np.isnan(features_df).sum().sum())
    print()

    print("\nFiltered dataset info:")
    features_df.info()

    original_dataset_name_no_extension = original_dataset_name.replace(".CSV", "").replace(".csv", "")

    print(f"\nLoading scaler from {scaler_pkl}")
    scaler = load(scaler_pkl)

    print(f"Loading feature selector from {selector_pkl}")
    selector = load(selector_pkl)

    features_scaled = scaler.transform(features_df)
    transformed_best_features = selector.transform(features_scaled)

    mask = selector.get_support()
    selected_feature_names = features_df.columns[mask]

    best_features_df = pd.DataFrame(transformed_best_features, columns=selected_feature_names)

    print("\n'Head' of best_features_df: ")
    print(best_features_df.head())

    print("\nSelected features:")
    print(selected_feature_names)

    final_df = pd.concat([
        sequence_id_col,
        sequence_content_col,
        best_features_df[selected_feature_names]
    ], axis=1)

    final_classification_dataset_name = f"FINAL_{original_dataset_name}.csv"
    final_df.to_csv(final_classification_dataset_name, index=False)
    print(f"\nFinal dataset produced: {final_classification_dataset_name}.")

    print("\nThe unlabelled dataset has been preprocessed and is now ready to be classified.")
