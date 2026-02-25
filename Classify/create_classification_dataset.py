"""
SCRIPT 1

- This is the first script - this script will create a raw testing dataset from a past run of earlgrey's output CSV and the corresponding cd-hit file used within that run.
"""

import pandas as pd
from Bio import SeqIO
import sys
import csv
import os


# Read in the dataset file (unknown sequences) and the cd-hit output file from first half of pipeline
def main___create_classification_dataset(df, final_cd_hit, name_prefix):
    
    print("-----------------------------------------------------------------------------------------------")
    print("STEP 1: Create a raw dataset from the complete.csv and cd-hit results.")
    print("-----------------------------------------------------------------------------------------------")
    
    data_frame = pd.read_csv(df) 
    filtered_df = filter_for_single_classifications(data_frame)
    sequences = representative_seq_puller(filtered_df)
    discovered_sequences_fasta = create_fasta_rep_seqs(sequences, final_cd_hit)
    create_feature_extraction_dataset(discovered_sequences_fasta, name_prefix)
    
# For any cluster that has only "unknown" elements, there is no string instance within the classification column for that cluster. Therefore, for each of these clusters we output the classification within that column as "unknown"

# Extract sequences and classifications where there is only a single classification present in the family_count column
def filter_for_single_classifications(data_fr):
    for index, row in data_fr.iterrows():
        family_info = row["family_count"]
        
        # we only need everything before the ":" in the classification column, so take out everything after
        if pd.notna(family_info) and "," not in str(family_info):
            data_fr.at[index, "family_count"] = str(family_info).split(':')[0]
    
    return data_fr
    

# This function retrieves the seq_IDs and the family-level classifications for each viable representative sequence from the CSV
def representative_seq_puller(df):
    current_cluster = "Cluster 0"
    rep_seq = None
    rep_seq_found = False
    rep_seqs = []
    family_level_classifications = []

    for index, row in df.iterrows():
        cluster = row['cluster']
        sequence_info = row['Sequence Information']
        rep_seq_info = row["Representative Sequence?"]
        pipeline_info = row["Pipeline_Count"]
        family_info = row["family_count"]
        unknown_count = row["Unknown_Count"]

        # Detect cluster change
        if cluster != current_cluster:
            current_cluster = cluster
            rep_seq = None
            rep_seq_found = False

        # Store representative sequence when found
        if rep_seq_info == "YES":
            rep_seq = sequence_info
            rep_seq_found = True

        # Final row in the cluster
        if pd.notna(pipeline_info): # This will only be true on the last row of the cluster, as pipeline_info is only present on the last row
            if "," in str(family_info):
                # Invalidate representative sequence if family_info is multi-labeled
                rep_seq = None
                rep_seq_found = False

            if rep_seq_found and unknown_count == "UNKNOWN PRESENT: Undiscovered": # Both a representative seq that has "UNKNOWN PRESENT: Undiscovered" in its cluster must be present for the seq and the classification to be added
                rep_seqs.append(rep_seq)

            # Reset for next cluster
            rep_seq = None
            rep_seq_found = False
               
           
    # Create a dictionary where rep_seqs entries are 'keys' and family_level_classifications entries are 'values'
    seqs_classifications_dict = dict(zip(rep_seqs, family_level_classifications))
    
    print("\n")
    print("Representative sequence ID list - these will be the input for the classification model (first 10 entries shown):")
    print(rep_seqs[:10]) # This will show the first 10 representative sequences within our list
    print("Length of the \"rep_seq_IDs\" list: ", len(rep_seqs))
    

    # Return the list of unlabelled 'rep_seqs'
    return rep_seqs

    
# This function creates a fasta file of only the representative sequences - again, these only include representative sequences from clusters that are not classified
def create_fasta_rep_seqs(seqs, cd_hit):

    final_output_file = "Representative_Sequences.fasta"
    with open(final_output_file, "w") as output_handle:
        for record in SeqIO.parse(cd_hit, "fasta"): #Even though cd-hit does not have a fasta extension, it is still a fasta
            
            # loop through each entry in the cd_hit file, if entry (minus header) is also within our 'rep_seqs', add to fasta
            record.id = record.id.split("_", 1)[-1]  # Remove the cd-hit specific prefix from the sequence ID
            
            # Only write the sequence if it is shared between my 'rep_seqs' list and my cd_hit fasta, AND if "N" nucleotides takes up less than threshold_for_N_nucleotides % of the sequence
            if record.id in seqs:
                SeqIO.write(record, output_handle, "fasta")


    return final_output_file
                
# This function creates the final CSV dataset with 2 columns: Sequence ID, Sequence Content
def create_feature_extraction_dataset(final_output_file_fasta, name_prefix):
    output_csv = f"classification_dataset_{name_prefix}.csv"
    input_fasta = final_output_file_fasta
        
    with open(output_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Sequence_ID", "sequence_content"])  # Column headers

        for record in SeqIO.parse(input_fasta, "fasta"):
            writer.writerow([record.id, str(record.seq)])
            
    print("\n")
    print("Raw unlabelled classification dataset created: ", output_csv)
            
    os.remove(final_output_file_fasta)   
            