"""
SCRIPT 5

- This is the fifth script which will classify an UNSEEN (UNLABELLED) dataset using a trained model.
"""

import joblib
import sys
import pandas as pd
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
import os

def main___classify(final_dataset, model_pkl, label_encoder_pkl, classifier_threshold):
    print("\n")
    print("\n")
    print("-----------------------------------------------------------------------------------------------")
    print("STEP 5: Classify the dataset using the trained model.")
    print("-----------------------------------------------------------------------------------------------")

    seq_ids, features = load_data(final_dataset)
    classify(seq_ids, features, model_pkl, label_encoder_pkl, classifier_threshold)


def load_data(filename):
    """
    Load data from CSV - The input is an UNLABELLED dataset with SCALED + SELECTED features.
    Expects first two columns to be: Sequence_ID, sequence_content
    """
    df = pd.read_csv(filename)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Keep IDs to report results
    seq_ids = df["Sequence_ID"].astype(str).tolist()

    # Features start at column index 2 (exclude Sequence_ID, sequence_content)
    features = df.iloc[:, 2:].values.tolist()
    features = [[float(x) for x in row] for row in features]
    return seq_ids, features


def classify(seq_ids, features, model_pkl, label_encoder_pkl, classifier_threshold):
    trained_model = joblib.load(model_pkl)
    label_encoder = joblib.load(label_encoder_pkl)

    # Predict probabilities and apply threshold
    probs = trained_model.predict_proba(features)
    max_idx = np.argmax(probs, axis=1)
    max_val = probs[np.arange(len(probs)), max_idx]

    # Map predicted integer classes back to original labels
    # Assumes the model was trained on label-encoded integers 0..K-1
    pred_int = trained_model.classes_[max_idx]
    pred_labels = label_encoder.inverse_transform(pred_int)

    # Thresholding: below threshold → UNKNOWN
    assigned = np.where(max_val >= float(classifier_threshold), pred_labels, "UNKNOWN")

    # Summaries
    total = len(seq_ids)
    unknown_count = int(np.sum(assigned == "UNKNOWN"))
    classified_mask = (assigned != "UNKNOWN")
    classified_labels = assigned[classified_mask]
    per_class_counts = Counter(classified_labels.tolist())

    # Print summary
    print("\nCLASSIFICATION SUMMARY")
    print(f"Total sequences: {total}")
    print(f"Threshold: {float(classifier_threshold):.2f}")
    print(f"Classified: {total - unknown_count}")
    for cls, cnt in sorted(per_class_counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"  • {cls}: {cnt}")
    print(f"Unknown (below threshold): {unknown_count}")

    # --- Outputs directory ---
    outputs_dir = "AI_Classification_Results"
    os.makedirs(outputs_dir, exist_ok=True)

    # Save CSV (two columns only, including UNKNOWN)
    results_path = os.path.join(outputs_dir, f"classification_results_threshold_{float(classifier_threshold):.2f}.csv")
    out = pd.DataFrame({
        "Sequence_ID": seq_ids,
        "Predicted_Class": assigned
    })
    out.to_csv(results_path, index=False)
    print("\nPredictions saved to:", results_path)

    # Visualization: bar plot of counts per class including UNKNOWN
    plot_counts = dict(per_class_counts)
    plot_counts["UNKNOWN"] = unknown_count
    classes = list(plot_counts.keys())
    counts = [plot_counts[c] for c in classes]

    plt.figure(figsize=(10, 6))
    plt.bar(classes, counts)
    plt.title(f"Classification Summary (threshold={float(classifier_threshold):.2f})")
    plt.xlabel("Predicted Class")
    plt.ylabel("Number of Sequences")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plot_path = os.path.join(outputs_dir, f"classification_summary_threshold_{float(classifier_threshold):.2f}.png")
    plt.savefig(plot_path, dpi=200)
    plt.close()
    print("Visualization saved to:", plot_path)
