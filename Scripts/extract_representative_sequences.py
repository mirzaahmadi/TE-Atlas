# FUNCTIONALITY: This script (which is called directly from the main.sh file) takes as input the final cd_hit file produced by 'cd-hit' and the final CSV file (produced by format_data.py). This file will create a new
               # fasta file called "Representative_Sequences.py" which will hold the sequence headers and content for each of the representative sequences that are still tagged as 'unknown'. This fasta file will be
               # scanned my PFAM to see if there are any genes within any sequence.


import pandas as pd
from Bio import SeqIO
import sys

def main(df, fsta, base_name):
    data_frame = pd.read_csv(df)
    rep_seq_headers = representative_puller(data_frame)
    modify_final_fasta(rep_seq_headers, fsta, base_name)


# This file takes as input a final cd-hit file and a final CSV file as well
def representative_puller(df):
    current = "Cluster 0" # This is initialized as the first cluster in the file
    rep_seqs = [] # This holds the representative sequence IDs in clusters where there is undiscovered unknown
    temp_rep_seq_list = [] # This temporarily holds representative sequences to be potentially added to rep_seqs

    # Iterate through each row in dataframe
    for index, row in df.iterrows():
        cluster = row['cluster']
        sequence_info = row['Sequence Information']
        rep_seq_info = row["Representative Sequence?"]
        unknown_info = row['Unknown_Count']

        # Ensure unknown_info is treated as a string
        if pd.isna(unknown_info):  # Handle NaN values
            unknown_info = ""

        # Add representative sequence headers to rep_seqs list
        if cluster == current:
            if rep_seq_info == "YES" and "Undiscovered" in unknown_info:
                rep_seqs.append(sequence_info)
            elif rep_seq_info == "YES":
                temp_rep_seq_list.append(sequence_info)
            elif "Undiscovered" in unknown_info:
                rep_seqs.append(temp_rep_seq_list[-1])

        else:
            current = cluster
            temp_rep_seq_list = []
            if rep_seq_info == "YES" and "Undiscovered" in unknown_info:
                rep_seqs.append(sequence_info)
            elif rep_seq_info == "YES":
                temp_rep_seq_list.append(sequence_info)
            elif "Undiscovered" in unknown_info:
                rep_seqs.append(temp_rep_seq_list[-1])

    return rep_seqs

# The representative sequences for each cluster that still have the tag 'undiscovered' - write those to a new fasta file called "Representative_Sequences.fasta"
def modify_final_fasta(seq_headers, fasta, b_name):
    final_output_file = "Representative_Sequences_" + b_name + ".fasta"
    with open(final_output_file, "w") as output_handle:
        for record in SeqIO.parse(fasta, "fasta"):
            record.id = record.id.split("_", 1)[1]
            if record.id in seq_headers:
                SeqIO.write(record, output_handle, "fasta")


main(sys.argv[1], sys.argv[2], sys.argv[3])





