"""
SCRIPT 0

- This is script 0 - for testing a model with a dataset of 'unknown' sequences (which were still NOT FOUND with clustering). This will connect all the other scripts together.
"""

import shutil
import sys
import os
import argparse
import subprocess
from create_classification_dataset import main___create_classification_dataset
from preprocessing_before_ftrCool import main___preprocessing_before_ftrCool
from preprocessing_after_ftrCool import main___preprocessing_after_ftr_cool
from classify import main___classify
from pathlib import Path

def main():
    # Print an evident message to the terminal so the user knows that the testing process will begin
    print("\n" + "="*80)
    print(" AI CLASSIFICATION MODE ")
    print("="*80)
    print("You have chosen to classify the UNKNOWN sequences using the trained AI model.")
    print("---------------------------------------------------------------")
    print("• The pipeline will now extract all sequences labeled as 'UNKNOWN' from the complete.csv file.")
    print("• These sequences will be formatted and processed into model-compatible features.")
    print("• The trained model will then predict the most likely class for each unknown sequence.")
    print("• Results will be saved as a new output file containing predicted classifications.")
    print("---------------------------------------------------------------")
    print("Starting classification process...\n")

    print("\n")
    print("\n")
    print("\n")
    
    # ----- argparse setup -----
    parser = argparse.ArgumentParser(
        prog="_START_CLASSIFYING.py",
        description="Classify UNKNOWN sequences using a trained model (builds classification dataset, preprocesses, extracts features).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # 6 mandatory arguments
    parser.add_argument("complete_csv", help="Path to COMPLETE_TE_RESULTS_*.csv file") # COMPLETE_TE_RESULTS_*.csv
    parser.add_argument("cdhit_output", help="Path to CD-HIT output file used in the first half of the pipeline") # CD-HIT file
    parser.add_argument("model_pkl", help="Path to trained model .pkl file") # trained model .pkl
    parser.add_argument("scaler_pkl", help="Path to scaler .pkl file used during training") # scaler .pkl
    parser.add_argument("label_encoder_pkl", help="Path to label encoder .pkl file used during training") # label encoder .pkl
    parser.add_argument("selector_pkl", help="Path to feature selector .pkl file used during training") # feature selector .pkl

    # 1 optional argument
    parser.add_argument(
        "--classifier-threshold",
        type=float,
        default=0.7,
        help="Confidence threshold (0–1) for assigning class labels during classification (default: 0.7)"
    )

     # if no args → show usage
    if len(sys.argv) == 1:
        parser.print_usage()
        print("\nTip: use -h/--help to see all options.")
        sys.exit(1)

    args = parser.parse_args()
    
    # Derive the base name
    input_data_file_name = os.path.splitext(os.path.basename(args.complete_csv.split("COMPLETE_TE_RESULTS_")[1]))[0]



    # STEP 1: Generate the unlabelled classification dataset from the complete.csv and cd-hit results
    main___create_classification_dataset(args.complete_csv, args.cdhit_output, input_data_file_name)

    # STEP 2: Preprocess the raw classification dataset before feature extraction
    classification_dataset = f"classification_dataset_{input_data_file_name}.csv"
    main___preprocessing_before_ftrCool(classification_dataset, input_data_file_name)
    
    # STEP 3: Perform feature extraction using R package ftrCool
    preprocessed_dataset = f"preprocessed_classification_dataset_{input_data_file_name}.csv"

    # Build absolute paths
    SCRIPT_DIR = Path(__file__).resolve().parent
    r_script = SCRIPT_DIR / "ftrCool_feature_extraction.R"
    preprocessed_abs = Path.cwd() / preprocessed_dataset  # file produced in current working dir

    # Use absolute path to the R script and the CSV
    subprocess.run(
        ["Rscript", str(r_script), str(preprocessed_abs), input_data_file_name],
        check=True
    )
    
    # STEP 4: Preprocess the classification dataset after feature extraction
    ftr_cool_extracted_dataset = f"ftrCool_extracted_{input_data_file_name}.csv"
    main___preprocessing_after_ftr_cool(ftr_cool_extracted_dataset, input_data_file_name, args.scaler_pkl, args.selector_pkl)
    
    # STEP 5: Classify the unseen dataset using the trained model
    Final_dataset = f"FINAL_{input_data_file_name}.csv"
    main___classify(Final_dataset, args.model_pkl, args.label_encoder_pkl, args.classifier_threshold)
    
    # STEP 6: Clean up intermediate data files
    INTERMEDIATE_DATA_dir = "Intermediate_dataset_files"
    os.makedirs(INTERMEDIATE_DATA_dir, exist_ok=True)

    # Move all intermediate CSV files to the new directory
    for filename in os.listdir("."):
        if filename.lower().endswith(".csv") and filename != args.complete_csv:
            shutil.move(filename, os.path.join(INTERMEDIATE_DATA_dir, filename))
    


if __name__ == "__main__":
    main()
