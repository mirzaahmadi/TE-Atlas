"""
SCRIPT 0

- This is script 0 - for training a model with a new dataset. This will connect all the other scripts together.
"""

import shutil
import sys
import argparse
from summarize_ambig_seqs import main___summarize_ambig_seqs
from preprocessing_before_ftrCool import main___preprocessing_before_ftrCool
from preprocessing_after_ftrCool import main___preprocessing_after_ftr_cool
from train_model import main___train_model
import subprocess
import os
from pathlib import Path

def main():

    # Print an evident message to the terminal so the user knows that the training process will begin
    print("\n" + "="*80)
    print(" TRAINING MODE ")
    print("="*80)
    print("You have chosen to train a NEW MODEL using the specified dataset.")
    print("---------------------------------------------------------------")
    print("• Training of a new model will now take place.")
    print("• Once training is complete, the model will be saved as a .pkl file.")
    print("• This trained model can later be used to classify UNKNOWN sequences.")
    print("---------------------------------------------------------------")
    print("Starting training process...\n")

    print("\n")
    print("\n")
    print("\n")


    # To start this file, pass in the training dataset and optionally, any parameters

    # This function will restrict the range of values for kbest and n_estimators
    def restricted_kbest(v):
        v = int(v)
        if not 5 <= v <= 1000:
            raise argparse.ArgumentTypeError("kbest must be between 5 and 1000")
        return v

    # This function will restrict the range of values for n_estimators
    def restricted_estimators(v):
        v = int(v)
        if not 50 <= v <= 1000:
            raise argparse.ArgumentTypeError("n_estimators must be between 50 and 1000")
        return v

    # This sets up the argument parser
    parser = argparse.ArgumentParser(
        prog="_START_TRAINING.py",
        description="Start pipeline: preprocess, extract features, and train model.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # 1) required positional argument
    parser.add_argument("dataset", help="Path to the dataset CSV")

    # 2) optional flags
    parser.add_argument("--kbest", type=restricted_kbest, default=20,
                        help="Top-K features to select (integer in [5, 1000])")
    parser.add_argument("--n-estimators", type=restricted_estimators, default=100,
                        help="Number of trees for Random Forest (integer in [50, 1000])")

    # If user supplied no args, show a short usage + tip and exit (like your sys.exit example)
    if len(sys.argv) == 1:
        parser.print_usage()  # prints: usage: _START_TRAINING.py [-h] [--kbest KBEST] [--n-estimators N_ESTIMATORS] dataset
        print("\nTip: use -h/--help to see all options.")
        sys.exit(1)

    args = parser.parse_args() # This will capture the arguments for use later on



    # Get the input file name from the dataset path
    input_file = os.path.basename(args.dataset)

    # Directory where THIS script lives (e.g., FULL_PIPELINE/Train)
    SCRIPT_DIR = Path(__file__).resolve().parent

    # STEP 1: Summarize all ambiguous sequences in the training dataset to give the user an overview of data quality
    main___summarize_ambig_seqs(args.dataset)

    # STEP 2: Preprocess the dataset before ftrCool
    main___preprocessing_before_ftrCool(args.dataset)

    # STEP 3: Perform feature extraction using R package ftrCool
    preprocessed_dataset = Path.cwd() / f"PREPROCESSED_{input_file}"
    r_script = SCRIPT_DIR / "ftrCool_feature_extraction.R"
    subprocess.run(
        ["Rscript", str(r_script), str(preprocessed_dataset)],
        cwd=str(SCRIPT_DIR),
        check=True
    )

    # STEP 4: Preprocess the dataset after ftrCool
    # Prefer the constant name the R script wrote, but fall back to the derived name if present
    extracted_constant = SCRIPT_DIR / "ftrCool_extracted_training_dataset.csv"
    extracted_derived  = Path.cwd() / f"ftrCool_extracted_{os.path.splitext(input_file)[0]}.csv"
    if extracted_constant.exists():
        ftrCool_extracted_dataset = str(extracted_constant)
    elif extracted_derived.exists():
        ftrCool_extracted_dataset = str(extracted_derived)
    else:
        # Default to the constant path (keeps behavior predictable if creation happens slightly later)
        ftrCool_extracted_dataset = str(extracted_constant)

    main___preprocessing_after_ftr_cool(ftrCool_extracted_dataset, input_file, args.kbest)

    # STEP 5: Train the model
    final_training_data = f"FINAL_{input_file}"
    main___train_model(final_training_data, input_file, args.n_estimators)

    # STEP 6: Clean up directory - move all intermediate CSV files to subfolder
    INTERMEDIATE_DATA_DIR = "Intermediate_dataset_files"
    os.makedirs(INTERMEDIATE_DATA_DIR, exist_ok=True)

    # Move all intermediate CSV files to the new directory
    for filename in os.listdir("."):
        if filename.lower().endswith(".csv") and filename != os.path.basename(args.dataset):
            shutil.move(filename, os.path.join(INTERMEDIATE_DATA_DIR, filename))


if __name__ == "__main__":
    main()
