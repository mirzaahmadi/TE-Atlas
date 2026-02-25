"""
SCRIPT 2

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



def main___preprocessing_before_ftrCool(dataset):
    
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
    
    # This gives info about the TE Orders in the dataframe
    check_orders(df_no_Ns_above_threshold) 
    
    # This creates visualizations of seq length per order
    view_sequence_length_distributions(df_no_Ns_above_threshold) 
    
    # This creates a dataset where all Ns are imputed randomly with [ACTG]
    df_random = create_alternate_training_set(df_no_Ns_above_threshold)
    
    
    output_name = f"PREPROCESSED_{os.path.basename(dataset)}"
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


# This will give information regarding the different TE orders of the dataframe
def check_orders(df):
    all_orders = set()
    
    order_dict = {'Crypton': 0, 'SINE': 0, 'Helitron': 0, 'Non-LTR/LINE': 0, "TIR": 0, "DIRS": 0, "Maverick": 0, "LTR": 0, "Penelope-like Element/PLE": 0}
    
    try:
        for item, value in df["TE_Order"].items():
            all_orders.add(value)
            order_dict[value] += 1
    except:
        print("\n")
        print("ERROR: The input training dataset must not include any TE order that is outside of the following:Crytpon, SINE, Helitron, Non-LTR/LINE, DIRS, Maverick, LTR, Penelope-like Element/PLE. Please ensure all order names are spelled correctly.")
    
    print("\n")
    print("All the TE Orders within the dataset: ", all_orders)
    print("Initial counts for each TE Order:", order_dict)


# This will give us the length distributions of the sequences within each order + give us visualization plots
def view_sequence_length_distributions(df):
    order_dict_seq_lengths = {'Crypton': [], 'SINE': [], 'Helitron': [], 'Non-LTR/LINE': [], "TIR": [], "DIRS": [], "Maverick": [], "LTR": [], "Penelope-like Element/PLE": []}

    for index, value in df["sequence_content"].items():
        seq_len = len(value)
        order_dict_seq_lengths[df.loc[index, "TE_Order"]].append(seq_len)
        
    # Create output directory if it doesn't exist
    output_dir = "./Visualizations/Seq_Len_Plots_After_Preprocessing"
    os.makedirs(output_dir, exist_ok=True)
    
    # Loop through each TE order and plot a boxplot instead of a violin plot
    for k, v in order_dict_seq_lengths.items():
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.boxplot(v, showfliers=True)  # showfliers=True shows the outliers
        ax.set_title(f"{k} Sequence Length Boxplot")
        ax.set_ylabel("Sequence Length")

        # Build safe filename and save
        filename = f"{k}_Seq_Length_Boxplot.png".replace("/", "_")
        save_path = os.path.join(output_dir, filename)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
    print("\n")
    print("Sequence length visualizations generated. Review them to ensure they look appropriate. If any sequences appear unusually long or short, consider trimming them and retraining the model.")

            
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