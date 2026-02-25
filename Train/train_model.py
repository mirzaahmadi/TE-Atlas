"""
SCRIPT 5

- This is the fifth script which will preprocess the training dataset AFTER it has undergone feature extraction. It will:


    1. Remove all rows that contain invalid information in any variable (infinite values, NaN values)
    2. Scales the numerical data so that all features fall between a specified range
    3. Choose a subset of the most relevant features from a dataset to use in the ML model using 'selectkbest'
    4. Saved the final preprocessed dataset to be used for model training.    
"""

import joblib # For saving the model
import pandas as pd
import numpy as np
import os

# For visualizations
import matplotlib.pyplot as plt
import seaborn as sns

# For Model training
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from sklearn.calibration import CalibratedClassifierCV 
from imblearn.over_sampling import SMOTE
from joblib import dump


def main___train_model(data, name, number_of_estimators):
    print("\n")
    print("\n")
    print("-----------------------------------------------------------------------------------------------")
    print("STEP 5: Train the model.")
    print("-----------------------------------------------------------------------------------------------")
    
    data = pd.read_csv(data)
        
    features, targets, class_labels  = load_data(data, name)

    # Initiate model - this is the non-calibrated one (calibration comes after)
    base_rf = RandomForestClassifier(n_estimators=number_of_estimators, random_state=42, class_weight="balanced")
    
    smote = SMOTE(random_state=42, k_neighbors=3)

    skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42) 

    all_preds = []
    all_true = []

    fold = 1
    for train_idx, test_idx in skf.split(features, targets):
        X_train, X_test = np.array(features)[train_idx], np.array(features)[test_idx]
        y_train, y_test = np.array(targets)[train_idx], np.array(targets)[test_idx]

        X_train, y_train = smote.fit_resample(X_train, y_train)

        # Wrap the RF with probability calibration (method = sigmoid) is used with smaller sized classes
        calibrated_rf = CalibratedClassifierCV(base_rf, method="sigmoid", cv=5)
        calibrated_rf.fit(X_train, y_train)

        y_pred = calibrated_rf.predict(X_test)

        all_preds.extend(y_pred)
        all_true.extend(y_test)

        print(f"\n--- Fold {fold} ---")
        print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
        fold += 1

    all_preds = np.array(all_preds)
    all_true = np.array(all_true)

    print("\n=== OVERALL METRICS ===")
    print("Accuracy:", accuracy_score(all_true, all_preds))
    print("Macro Precision:", precision_score(all_true, all_preds, average='macro'))
    print("Macro Recall:", recall_score(all_true, all_preds, average='macro'))
    print("Macro F1:", f1_score(all_true, all_preds, average='macro'))

    print("\n=== CLASSIFICATION REPORT (PER CLASS) ===")
    labels_idx = np.arange(len(class_labels))
    report_dict = classification_report(
        all_true, all_preds,
        labels=labels_idx,
        target_names=class_labels,
        output_dict=True
    )
    print(classification_report(all_true, all_preds, labels=labels_idx, target_names=class_labels))

    # Save the classification report as CSV under Visualizations/Training Metrics
    os.makedirs("Visualizations/Training Metrics", exist_ok=True)
    report_df = pd.DataFrame(report_dict).transpose()
    report_csv_path = "Visualizations/Training Metrics/classification_report.csv"
    report_df.to_csv(report_csv_path, index=True)
    print(f"\nClassification report saved to: {report_csv_path}")

    cm = confusion_matrix(all_true, all_preds, labels=labels_idx)
    plot_confusion_matrix(cm, class_labels)
    plot_class_metrics(report_dict, class_labels)

    # Refit model on full dataset (with SMOTE)
    X_resampled, y_resampled = smote.fit_resample(features, targets)
    
    # Fit and save calibrated model (not the raw RF)
    calibrated_rf_full = CalibratedClassifierCV(base_rf, method="sigmoid", cv=5)
    calibrated_rf_full.fit(X_resampled, y_resampled)
    
    PKL_DIR = "Model_Artifacts"
    
    original_dataset_name_no_extension = name.replace(".CSV", "").replace(".csv", "")
    trained_model_path = os.path.join(PKL_DIR, f"TRAINED_MODEL_{original_dataset_name_no_extension}.pkl")

    dump(calibrated_rf_full, trained_model_path)

    print("\n")
    print(f"Model training complete. Saved as '{trained_model_path}'. Ready for evaluation on a properly formatted testing dataset.")


def load_data(data, name):
    """
    Load and split data from CSV - One list for features and another for targets
    """
    df_randomized = data.sample(frac=1, random_state=42).reset_index(drop=True)

    # features are the (already SCALED) columns from training preprocessing
    features = df_randomized.iloc[:, 1:-1].values.tolist()
    targets = df_randomized.iloc[:, -1].tolist()

    target_encoder = LabelEncoder()
    target_encoder.fit(targets)

    # Create the shared folder for all model artifacts
    PKL_DIR = "Model_Artifacts"
    os.makedirs(PKL_DIR, exist_ok=True)

    original_dataset_name_no_extension = name.replace(".CSV", "").replace(".csv", "")

    # Save the label encoder in the same folder
    label_encoder_path = os.path.join(PKL_DIR, f"LABEL_ENCODER_{original_dataset_name_no_extension}.pkl")
    dump(target_encoder, label_encoder_path)

    print(f"Label encoder saved to: {label_encoder_path}")
    

    converted_target_list = target_encoder.transform(targets)
    class_labels = target_encoder.classes_.tolist()

    converted_feature_list = [[float(item) for item in feature] for feature in features]
    
    return converted_feature_list, converted_target_list, class_labels


def plot_confusion_matrix(cm, class_labels):
    os.makedirs("Visualizations/Training Metrics", exist_ok=True)

    # Row-normalize the confusion matrix so colors are relative per row
    cm_normalized = cm.astype(float) / cm.sum(axis=1, keepdims=True)
    cm_normalized = np.nan_to_num(cm_normalized)  # handle any div-by-zero rows

    plt.figure(figsize=(10, 8))
    sns.heatmap(cm_normalized, annot=cm, fmt="d", cmap="Blues",
                xticklabels=class_labels, yticklabels=class_labels)
    plt.title("Confusion Matrix (Row-normalized for color scaling)")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.tight_layout()
    plt.savefig("Visualizations/Training Metrics/confusion_matrix.png")
    plt.close()
    
    print("\n")
    print("Confusion matrix plot created.")
    

def plot_class_metrics(report_dict, class_labels):
    precision, recall, f1 = [], [], []

    for label in class_labels:
        precision.append(report_dict[label]['precision'])
        recall.append(report_dict[label]['recall'])
        f1.append(report_dict[label]['f1-score'])

    x = np.arange(len(class_labels))
    width = 0.25

    plt.figure(figsize=(12, 6))
    plt.bar(x - width, precision, width, label='Precision')
    plt.bar(x, recall, width, label='Recall')
    plt.bar(x + width, f1, width, label='F1 Score')

    plt.xticks(x, class_labels, rotation=45, ha="right")
    plt.title("Per-Class Metrics")
    plt.legend()
    plt.tight_layout()
    plt.savefig("Visualizations/Training Metrics/per_class_metrics.png")
    plt.close()

    print("\n")
    print("Grouped bar plot created.")
    
if __name__ == "__main__":
    d = pd.read_csv("FINAL_features_random_for_N_20_FEATURES.csv")
    name = "FINAL_features_random_for_N_20_FEATURES.csv"
    main___train_model(d, name)
