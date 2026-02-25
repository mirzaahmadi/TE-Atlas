"""
SCRIPT 1

- This is the first script - this serves as a way to keep track of and visualize the ambiguous nucletodies within each and across all sequences within the training dataset.
"""


import pandas as pd
import statistics
import matplotlib.pyplot as plt
import sys
import os
from Bio.Seq import Seq



def main___summarize_ambig_seqs(dataset): 
    
    print("-----------------------------------------------------------------------------------------------")
    print("STEP 1: First, Summarize all ambiguous sequences present in the training dataset.")
    print("-----------------------------------------------------------------------------------------------")
      
    df = pd.read_csv(dataset) # pass in the specified training dataset as a dataframe
    print("\n")
    print(f"Raw training dataset: {dataset}")
    print('length of dataframe is: ', len(df))

    percentages = []
    
    # Go through each sequence, take account of all the seqs that have ambiguous nucleotides
    for index, value in df["sequence_content"].items():
        seq = Seq(value)
        ambig_count = sum(1 for base in seq if base not in "ACTG") # This counts all the ambig nucleotides in each seq
        percentages.append((ambig_count / len(seq)) * 100)

    print("\n")
    print("Showing percentage of ambiguous bases for the first ten sequences: ", percentages[:10])


    mean = statistics.mean(percentages)
    print("Average percentage of ambiguous nucleotides in each sequence (across ALL sequences in the dataset): ", f"{mean:.3f}%")


    # PLOT FIGURE
    # Create folder if it doesn't exist
    os.makedirs("Visualizations", exist_ok=True)

    plt.figure(figsize=(10, 5))
    plt.hist(percentages, bins=30, color='skyblue', edgecolor='black')

    plt.title("Distribution of Ambiguous Nucleotide Content (%) Across Sequences")
    plt.xlabel("Percentage of Ambiguous Nucleotides in Sequence")
    plt.ylabel("Number of Sequences")
    plt.grid(True)

    # Save plot
    plt.savefig("Visualizations/Ambiguous_nucleotides_plot.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("\n")
    print("Ambiguous_sequences_plot.png saved")

if __name__ == "__main__":
    main___summarize_ambig_seqs()
