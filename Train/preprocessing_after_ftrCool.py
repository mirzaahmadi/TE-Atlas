"""
SCRIPT 4

- This is the fourth script which will preprocess the training dataset AFTER it has undergone feature extraction. It will:
    1. Remove all rows that contain invalid information in any variable (infinite values, NaN values)
    2. Scales the numerical data so that all features fall between a specified range
    3. Choose a subset of the most relevant features from a dataset to use in the ML model using 'selectkbest'
    4. Saved the final preprocessed dataset to be used for model training.    
"""



import os
import pandas as pd
import numpy as np
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.preprocessing import MinMaxScaler
from joblib import dump


def main___preprocessing_after_ftr_cool(dataset, original_dataset_name, number_kbest):
    print("\n")
    print("\n")
    print("-----------------------------------------------------------------------------------------------")
    print("STEP 4: Preprocess the training dataset after feature extraction.")
    print("-----------------------------------------------------------------------------------------------")
    
    # create folder for model artifacts
    PKL_DIR = "Model_Artifacts"
    os.makedirs(PKL_DIR, exist_ok=True)

    dataset = pd.read_csv(dataset)
    
    # Inspect the dataset
    print("\nDataset head (5 rows):")
    print(dataset.head(5)) # Print the first five rows
    print("\nDataset info:")
    dataset.info() # Give further info about this dataset

    # Separate features and labels
    features_df = dataset.iloc[:, 1:-1].copy()   # Features (columns 1 up to the last column - doesn't include the last TE_Order column)
    labels_df = dataset.iloc[:, -1].copy()    # Final_Class

    # Ensure all features are numeric
    features_df = features_df.apply(pd.to_numeric, errors='coerce')

    # Check for bad values before filtering
    print("\nBefore filtering:")
    # These two print statements will print, respectively, the number of infinite values and the NaN values in the dataset
    print("Number of inf values:", np.isinf(features_df.select_dtypes(include=[np.number])).sum().sum()) # from feature_df, we are selecting all the 'inf' datatype values, and summing them up - returning the total number of them in the dataset.
    print("Number of NaN values:", np.isnan(features_df.select_dtypes(include=[np.number])).sum().sum()) # from feature_df, we are selecting all the 'NaN' datatype values, and summing them up - returning the total number of them in the dataset.

    # Replace infs with NaN, then drop any row that contains a NaN value
    features_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    features_df.dropna(inplace=True)

    # Align labels and sequence_content column
    labels_df = labels_df.loc[features_df.index].reset_index(drop=True) # Aligns labels_df rows to match the row indices of features_df, ensuring both dataframes are perfectly synchronized. The reset_index(drop=True) removes the old indices and reassigns a clean, sequential index (0,1,2,...).
    sequence_content_col = dataset.loc[features_df.index, 'sequence_content'].reset_index(drop=True) # Selects the 'sequence_content' column for rows matching features_df’s index, and resets the row index
    features_df = features_df.reset_index(drop=True)

    # Check again after filtering
    print("\nAfter filtering:")
    print("Number of inf values:", np.isinf(features_df).sum().sum())
    print("Number of NaN values:", np.isnan(features_df).sum().sum())
    print()

    # See the properties of the filtered dataset
    print("\nFiltered dataset info:")
    features_df.info() # Give further info about this dataset

    # Scale the features
    scaler = MinMaxScaler() # used to scale numerical data so that all feature values fall within a specific range, usually between 0 and 1.
    features_scaled = scaler.fit_transform(features_df)

    original_dataset_name_no_extension = original_dataset_name.replace(".CSV", "").replace(".csv", "")
    
    # save the scaler - this will be the same one used downstream if you are to test the model
    scaler_path = os.path.join(PKL_DIR, f"SCALER_{original_dataset_name_no_extension}.pkl")
    dump(scaler, scaler_path)
    print(f"\nScaler saved to {scaler_path}")

    # Select top x features using mutual_info_classif
    selector = SelectKBest(score_func=mutual_info_classif, k=number_kbest) # Selects the 'best' no. of features
    transformed_best_features = selector.fit_transform(features_scaled, labels_df)
    
    # Keep the selector as a pickle model for future use (eg. when testing the model)
    selector_path = os.path.join(PKL_DIR, f"FEATURE_SELECTOR_{original_dataset_name_no_extension}.pkl")
    dump(selector, selector_path)
    print(f"\nSelector saved to {selector_path}")

    # Get selected feature names 
    mask = selector.get_support() # mask is a boolean array with True for the selected features and False for the rest.
    selected_feature_names = features_df.columns[mask] 
    """ 
    eg.
    features_df.columns = ['A', 'B', 'C', 'D']
    mask = [True, False, True, False]
    features_df.columns[mask]  # returns ['A', 'C']
    """
    
    # Convert the subset of selected 'best' features back into a DataFrame - creates a DataFrame from the transformed_best_features NumPy array and assigns the correct column names (selected_feature_names).
    best_features_df = pd.DataFrame(transformed_best_features, columns=selected_feature_names)

    print("\n'Head' of best_features_df: ")
    print(best_features_df.head())

    print("\nSelected features:")
    print(selected_feature_names)

    # Create the final DataFrame - concatenating the sequence_content columns, dataframe, the selected columns of the features_df df, and the labels_df column
    final_df = pd.concat([
        sequence_content_col,
        best_features_df[selected_feature_names],
        labels_df.rename('Final_Class')
    ], axis=1)

    # Save to CSV
    final_training_dataset_name = f"FINAL_{original_dataset_name}"
    final_df.to_csv(final_training_dataset_name, index=False)
    print(f"\nFinal dataset produced: {final_training_dataset_name}. Model training will now begin.")