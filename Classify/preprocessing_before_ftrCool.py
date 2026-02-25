"""
SCRIPT 2 - NOTE: This script is only preprocessing an UNLABELLED dataset before feature extraction

- This is the second script which will preprocess the raw training dataset by:
    1. Removing all sequences with ambiguous nucleotides that exceed 1% of the sequence's content
    2. For the remaining sequences, randomly impute all N nucleotides with [ACTG]
"""


import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import random
from Bio.Seq import Seq



def main___preprocessing_before_ftrCool(dataset, name_prefix):
    
    print("\n")
    print("\n")
    print("-----------------------------------------------------------------------------------------------")
    print("STEP 2: Preprocess the training dataset before feature extraction.")
    print("-----------------------------------------------------------------------------------------------")
    
    df = pd.read_csv(dataset)
    
    # Converts sequence content to all uppercase
    uppercase_df = convert_nucs_to_uppercase(df) 
    
    # Explore sequence data that is not [ACTGN]
    check_non_ACTGN_nucleotides(uppercase_df) 
    
    # Explore sequences with nucleotides that are "N"
    sequence_IDs_above_threshold = check_N_sequences(uppercase_df) 
    
    # This will return IDs of those sequences that have ambiguous nucleotide proportions above threshold
    sequence_IDs_above_threshold_list_TO_REMOVE, df_only_ACTGN = check_N_sequences_AFTER_conversion(uppercase_df) 
    
    # This will return a cleaned up dataset, removing all IDs with Ns above the threshold
    df_no_Ns_above_threshold = remove_Ns_above_threshold(df_only_ACTGN, sequence_IDs_above_threshold_list_TO_REMOVE) 
    
    # This creates a dataset where all Ns are imputed randomly with [ACTG]
    df_random = create_alternate_training_set(df_no_Ns_above_threshold)


    output_name = f"preprocessed_classification_dataset_{name_prefix}.csv"
    df_random.to_csv(output_name, index=False)

    print("\n")
    print("Preprocessed dataset produced. This will now go through feature extraction via the R package ftrCool.")

# First, convert all nucleotides to uppercase (ftrCool will do this anyway, but we did this in preprocessing here as well)
def convert_nucs_to_uppercase(df):
    df["sequence_content"] = df["sequence_content"].str.upper()
    
    return df


# There are some nucleotides that are not in [A, C, T, G, N] - explore this data
def check_non_ACTGN_nucleotides(uppercase_df):
    sequences_w_non_ACTGN = set() 
    non_ACTGN_chars = set()
    
    # Loop through the 'sequence_content' column, collecting the number of sequences that contain letters other than [ACTGN] and a set of all the weird characters
    for index, value in uppercase_df["sequence_content"].items():
        seq = Seq(value)
        for c in seq:
            if c not in "ACTGN":
                sequences_w_non_ACTGN.add(uppercase_df.loc[index, "Sequence_ID"])
                non_ACTGN_chars.add(c)
    
    print("\n")
    print("Number of sequences that contain non [ACTGN] letters: ", len(sequences_w_non_ACTGN))
    print("All the letters found within the dataset that are not [ACTGN]: ", non_ACTGN_chars)
    print("\n")


# This will see how many sequences have Ns, and then after converting non [ACTGN] to "N", how many sequences with Ns there are after this step
def check_N_sequences(df):
    All_percentages = {}
    number_of_seqs_over_threshold = []
    sequence_IDs_above_threshold = [] # These contain the ID of all sequences that are above threshold - to remove
    
    # Loop through sequence content, gathering percentage of each sequence that is ambiguous nucleotide
    for index, value in df["sequence_content"].items():
        if "N" in value:
            n_count = value.count("N")
            percent = (n_count / len(value) * 100)
            All_percentages[df.loc[index, "Sequence_ID"]] = percent         

    for k, v in All_percentages.items():
        if v > 1:
            number_of_seqs_over_threshold.append(v)
            sequence_IDs_above_threshold.append(k)
    
    print("Number of sequences with at least one N:", len(All_percentages)) 
    print("Number of sequences above threshold:", len(number_of_seqs_over_threshold))
    
    return sequence_IDs_above_threshold
    

# Now, let's convert all nucleotides that are not [ACTGN] to N, recheck the variables, and then return both the ID list of all sequences (above threshold) to remove, and an updated dataframe with only [ACTGN]
def check_N_sequences_AFTER_conversion(uppercase_df):
    
    uppercase_df_copy = uppercase_df.copy()
    # Replace any letter that's not A/C/G/T/N with N
    uppercase_df_copy["sequence_content"] = uppercase_df_copy["sequence_content"].str.replace(r"[^ACGTN]", "N", regex=True)

    print("\n")
    print("AFTER CONVERTING NON [ACTGN] characters to N:")
    Ids_above_threshold = check_N_sequences(uppercase_df_copy)
    
    return Ids_above_threshold, uppercase_df_copy

    
# This will remove all the sequence IDs that have a percent threshold above 1% of Ns
def remove_Ns_above_threshold(df_only_ACTGN, sequence_IDs_above_threshold_list):
    df_no_Ns_above_threshold = df_only_ACTGN[~df_only_ACTGN["Sequence_ID"].isin(sequence_IDs_above_threshold_list)]
    df_no_Ns_above_threshold = df_no_Ns_above_threshold.reset_index(drop=True)
    
    print("\n")
    print("This dataframe contains sequences with only ACTGN values (Also Only contains sequences with Ns below the 1% threshold)")
    print(df_no_Ns_above_threshold)
    
    return df_no_Ns_above_threshold

            
# This will create a dataset where all Ns are imputed randomly with [ACTG]. This dataset will then be fed into ftrCool for feature extraction.
def create_alternate_training_set(df):

    df_random = df.copy()
    df_random["sequence_content"] = df_random["sequence_content"].apply(replace_N_with_random)
    
    return df_random


# This is a helper function which will randomly choose a base for 'N' in a sequence from ATCG
def replace_N_with_random(seq):
    return ''.join(random.choice("ACTG") if c == "N" else c for c in seq)    


if __name__ == "__main__":
    main___preprocessing_before_ftrCool()