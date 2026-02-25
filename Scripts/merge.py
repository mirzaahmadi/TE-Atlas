# FUNCTIONALITY: This script, which is called by the 'main.sh' file, will take as input the complete CSV file and the filtered_output_PFAM table. This script will then merge the PFAM table into the complete CSV file,
               # resulting in a 'proteins' column added to the complete CSV output file.

import sys
import pandas as pd
from Bio import SeqIO
from collections import defaultdict



# passes in the complete csv file and the filtered pfam output csv file
def main(c_df, p_df):
    complete_df = pd.read_csv(c_df)
    pfam_df = pd.read_csv(p_df)

    filtered_pfam_df = clean_pfam(pfam_df)
    merged_df, merged_rows = merge_dataframes(complete_df, filtered_pfam_df)
    final_merged_df = optimize_row_placement(merged_df, merged_rows)

    final_merged_df.to_csv(c_df, index=False)


def clean_pfam(pfam_df): # Cleans pfam dataframe, making it ready for merging with complete dataframe
    pfam_df = pfam_df[['seq_id', 'hmm_name']].copy()  # Explicitly create a copy of the pfam_dataframe
    pfam_df = pfam_df.rename(columns={'seq_id': 'Sequence Information'})  # Rename seq_id column so that column names match

    # Initialize the dictionary to store protein names as sets
    # Default dicts automatically create a default value (empty list for eg) when you access a key that doesn't exist
    pfam_dict = defaultdict(set) # To avoid duplicate values, make the value a set

    # Iterate through the DataFrame and add protein names to the set for each sequence ID
    for seq_id, protein_name in zip(pfam_df['Sequence Information'], pfam_df['hmm_name']):
        pfam_dict[seq_id].add(protein_name)

    # Join multiple protein names for the same seq_id into a comma-separated string
    for seq_id in pfam_dict:
        pfam_dict[seq_id] = ', '.join(pfam_dict[seq_id])

    # Convert the dict back into dataframe for merging
    filtered_pfam_df = pd.DataFrame.from_dict(pfam_dict, orient='index', columns=['Proteins'])

    # Reset the index to treat sequence information as a regular column and name it 'Sequence Information'
    filtered_pfam_df.reset_index(inplace=True)
    filtered_pfam_df.rename(columns={'index': 'Sequence Information'}, inplace=True)

    return filtered_pfam_df



def merge_dataframes(complete_df, filtered_pfam_df): # This function will merge the complete CSV output file with the filtered PFAM table
    merged_df = pd.merge(complete_df, filtered_pfam_df[['Sequence Information', 'Proteins']], on='Sequence Information', how='left')
    merged_rows = merged_df[merged_df["Proteins"].notnull()] # Extract the merged rows for later use

    return merged_df, merged_rows



def optimize_row_placement(merged_df, merged_rows):
    # Get the list of clusters you need to check
    clusters = merged_rows['cluster'].unique()  # Get unique clusters from merged_rows

    # Create a dictionary to store matching rows (that are in the main complete csv) by cluster
    matching_rows_dict = {cluster: merged_df[merged_df['cluster'] == cluster] for cluster in clusters}

    # Iterate through each cluster's rows and update as needed
    for cluster, cluster_df in matching_rows_dict.items(): # cluster is the key, cluseter_df is the value
        # Find the row where the 'Unknown_Count' column has "UNKNOWN PRESENT: Undiscovered"
        undiscovered_row = cluster_df[cluster_df['Unknown_Count'] == "UNKNOWN PRESENT: Undiscovered"]

        if not undiscovered_row.empty:
            # Find the first row with a protein name in the cluster
            protein_row = cluster_df[cluster_df['Proteins'].notna() & (cluster_df['Proteins'] != '')].iloc[0]

            # Update the 'undiscovered_row' row with the protein name from protein_row
            merged_df.loc[undiscovered_row.index, 'Proteins'] = protein_row['Proteins']

            # Clear protein names from all other rows in the same cluster that do not have 'UNKNOWN PRESENT: Undiscovered'
            merged_df.loc[cluster_df[cluster_df['Unknown_Count'] != "UNKNOWN PRESENT: Undiscovered"].index, 'Proteins'] = None

    return merged_df



main(sys.argv[1], sys.argv[2])
