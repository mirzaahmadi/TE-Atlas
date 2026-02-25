# FUNCTIONALITY: This script is called by 'format_data.py'. After the formatted excel table is produced in the main directory (which is produced by the script '_optimize_csv.py'), this file will add on some additional
               # columns that add more information to the output. This includes the pipeline_count, Unknown_count, and family_count columns.



import pandas as pd
import re



def main(df):
    pipeline_metrics = pipeline_count(df) # this function creates the pipeline_count column which indicates which pipelines were present in each cluster and how many times they were used to find a TE
    pipeline_unknowns_metrics = unknown_column(pipeline_metrics) # This function creates the column Unknown_Count which specifies the number of 'unknowns' found in each cluster
    final_df = family_classification(pipeline_unknowns_metrics) # This function creates a column called Family_Count which keeps tracks of the families of the TE's found in each cluster
    return final_df



def pipeline_count(df):
    """
    This function facilitates the addition of a column which lists the pipelines used in each cluster and the number of times they are used
    """
    current = None
    pipeline_dict = {} # Initialize an empty dictionary to hold pipeline counts

    # Iterates through every row in the dataframe, retrieving the value in the column 'cluster' and the value in the column 'Pipeline Used' (for each row)
    for index, row in df.iterrows():
        cluster = row['cluster']
        pipeline = row["Pipeline Used"]

        # The following lines are added to ensure compatability between data types and content written within certain columns
        if "Pipeline_Count" not in df.columns:
            df["Pipeline_Count"] = None # On the first iteration, this column doesn't exist yet, so just assign it as none to avoid 'KeyError'
        else:
            df["Pipeline_Count"] = df["Pipeline_Count"].astype(object)

        # when the cluster changes, assign the current pipeline dict (the text within this dict) to the last row in that cluster, indicating the pipelines used in that cluster
        if current != cluster:
            if current is not None:
                # 'df.at[index-1,...' accesses the cell position just before the current row (which is the last row in the last cluster) and writes the pipeline_count
                df.at[index-1, "Pipeline_Count"] = str(pipeline_dict).replace("{", "").replace("}", "").replace("\'", "")
                pipeline_dict = {}

            current = cluster # since our current cluster does not equal current, let's update that

        if current == cluster: # However if the current cluster does equal current
            if pipeline in pipeline_dict: # If the cluster name is already in the the pipeline dict, add one
                pipeline_dict[pipeline] += 1
            else: # If the cluster name is not in the pipeline dict, add it in there and assign it as 1
                pipeline_dict[pipeline] = 1

    # The following code deals with the last row in the df
    if current is not None and len(pipeline_dict) > 0: # If there is no more 'cluster' cell, but current is still none and pipeline dict is greater than zero
        df.at[len(df)-1, 'Pipeline_Count'] = str(pipeline_dict).replace("{", "").replace("}", "").replace("\'", "") # Append the pipeline dict to the last line in the df

    return df



def unknown_column(data_frame):
    """
    This function acts to add a new column called 'Unknown_Count' to the dataframe which will contain one of the following:
    - 'N/A' if there is no unknowns within the cluster at all
    - 'UNKNOWN FOUND: 'Undiscovered' if there is an unknown but there are no other sequences that provide a classification for this family (of if there is another family, but it is a gold sequence - so doesn't count)
    - 'UNKNOWN FOUND: 'Discovered' if there is an unknown and there is at least one other sequence alluding to a classification within that cluster
    """
    current = None
    unknown_dict = {} # Initialize an empty dictionary to hold unknown values

    entries_in_cluster = 0 # This is initialized to keep track of how many rows are in a cluster
    unknown_found = 0 # this keeps track of how many unknowns are found within the cluster
    gold_found = 0 # This keeps track of how many gold sequences are found within the cluster - NOTE: I used gold sequences mainly when first building my pipeline, however when testing with real genomes, gold standard
                   # sequences are not present

    # These two are initialized so that we can have a final score of the proportion of unknowns discovered
    total_unknowns = 0
    discovered_unknowns = 0

    # Iterates through every row in the dataframe, retrieving the value in the column 'cluster', the value in the column 'Pipeline Used', and value in the column "Sequence Information" (for each row)
    for index, row in data_frame.iterrows():
        cluster = row['cluster']
        sequence_info = row["Sequence Information"]
        pipeline = row["Pipeline Used"]

        # The following lines are added to ensure compatability between data types and content written within certain columns
        if "Unknown_Count" not in data_frame.columns:
            data_frame["Unknown_Count"] = None
        else:
            data_frame["Unknown_Count"] = data_frame["Unknown_Count"].astype(object)

        entries_in_cluster += 1 # Adds 1 to the 'entries_in_cluster' count. This will reset to zero when a new cluster is breached

        # When the cluster changes, print out the current unknown dict to the last row in that cluster, indicating the unknown values (if any) in that cluster
        if current != cluster: # if current does not equal cluster (indicates change in cluster)
            if current is not None:
                if unknown_found == 0: # If there are no unknowns found in the cluster - write 'N/A' at the end of the cluster to denote that there are no unknown sequences present
                    data_frame.at[index-1, "Unknown_Count"] = str("N/A") # "data_frame.at[index-1, "Unknown_Count"]" accesses the 'Unknown_Count" column for the previous row, and assigns 'N/A' to that cell
                elif unknown_found > 0: # however, if there is an unknown found, write that there is an unknown and whether or not it was discovered
                    total_unknowns += 1 # Every time an unknown is present, add it to the total_unknowns count
                    if unknown_found == entries_in_cluster: # if unknowns = entries_in_cluster ; unknown is present but undiscovered - therefore, write that in the excel sheet
                        unknown_dict["UNKNOWN PRESENT"] = "Undiscovered"
                    elif gold_found + unknown_found == entries_in_cluster: # if there are only golds and unknowns in the cluster ; unknown is present but undiscovered
                        unknown_dict["UNKNOWN PRESENT"] = "Undiscovered"
                    else: # if there is another sequence that isn't an unknown or a gold in the cluster ; unknown is present and it's been 'discovered'
                        discovered_unknowns += 1 # Every time an unknown is discovered, add it to the list
                        unknown_dict["UNKNOWN PRESENT"] = "Discovered"
                    data_frame.at[index-1, "Unknown_Count"] = str(unknown_dict).replace("{", "").replace("}", "").replace("\'", "")

            unknown_dict = {} # reset the unknown_dict dictionary
            entries_in_cluster = 0 # reset the entries_in_cluster value to zero
            current = cluster # since our current cluster does not equal current, let's update that
            unknown_found = 0
            gold_found = 0

        if current == cluster: # However if the current cluster does equal current
            # 1. I should go through every row of the cluster and if a certain condition is met, then I should add [numerically, i.e. +1] to a variable
            # 2. Only after meeting these conditions, should I make actually make any actions
            search_query = 'unknown'
            gold_query = 'gold'
            if search_query in sequence_info.lower(): # if there is an 'Unknown' in the sequence info
                unknown_found += 1 # add to the unknown_found count
            elif gold_query.upper() in pipeline: # if there is a 'Gold' in the pipeline info
                gold_found += 1 # add to the gold_found count
            else: # If there is not an 'Unknown' in the sequence info ; don't do anything
                pass

    # Handle the last cluster - so this code only activates when it gets to the last_row+1 (first blank row) of the dataframe
    if entries_in_cluster == 0: # If entries = 0, that means that the previous line was the only one in it's cluster, and therefore it wasn't yet added to the number_of_entries list
        entries_in_cluster += 1 # To make sure the entries_in_cluster reflects that there is only one entry in the last cluster of the df, update it's value to 1
    if unknown_found == 0: # If there are no unknowns found in the last cluster of dataframe - print 'N/A' at the end of the cluster
        data_frame.at[index, "Unknown_Count"] = str("N/A")
    elif unknown_found > 0: # however, if there is an unknown found, print that there is an unknown and whether or not it was discovered
        if unknown_found == entries_in_cluster: # if unknowns = entries ; unknown is present but undiscovered
            unknown_dict["UNKNOWN PRESENT"] = "Undiscovered"
        elif gold_found + unknown_found == entries_in_cluster: # if there are only golds and unknowns in the cluster ; unknown is present but undiscovered
            unknown_dict["UNKNOWN PRESENT"] = "Undiscovered"
        else: # if there is another sequence that isn't an unknown or a gold in the cluster ; unknown is present and it's been 'discovered'
            unknown_dict["UNKNOWN PRESENT"] = "Discovered"
        data_frame.at[index, "Unknown_Count"] = str(unknown_dict).replace("{", "").replace("}", "").replace("\'", "")
    if total_unknowns > 0:
        percentage = round((discovered_unknowns / total_unknowns) * 100, 2)
        data_frame.at[index + 1, "Unknown_Count"] = str(f"Proportion of Unknowns found through clustering: {discovered_unknowns}/{total_unknowns} ({percentage}%)")

    return data_frame



def family_classification(dframe):
    """
    This function acts to add a new column called 'family_classifications' to the dataframe which will contain the different families within the cluster and their number of occurrences (e.g., 'name': 2, 'name2': 1 ...).
    """
    current = None
    family_dict = {}  # Initialize an empty dictionary to hold family counts

    # Iterates through every row in the dataframe, retrieving the value in the column 'cluster' and the value in the column 'Pipeline Used' and the value in the column "Sequence Information" (for each row)
    for index, row in dframe.iterrows():
        cluster = row['cluster']
        pipeline = row["Pipeline Used"]
        sequence_info = row["Sequence Information"]

        # The following line is added to ensure compatability between data types and content written within certain columns
        if "family_count" not in dframe.columns:
            dframe["family_count"] = None
        else:
            dframe["family_count"] = dframe["family_count"].astype(object)

        # When the cluster changes, print out the current family dict to the last row in that cluster, indicating the families in that cluster
        if current != cluster:
            if current is not None:
                # 'dframe.at[index-1,...' accesses the cell position just before the current row (which is the last row in the last cluster) and prints the family_count
                dframe.at[index-1, "family_count"] = str(family_dict).replace("{", "").replace("}", "").replace("\'", "")
                family_dict = {}

            current = cluster  # Since our current cluster does not equal current, let's update that

        if current == cluster:  # However if the current cluster does equal current
            # For ANNOSINE pipeline, add the number of 'SINEs' to a dict
            if pipeline == 'ANNOSINE':
                if 'SINE' in family_dict:
                    family_dict['SINE'] += 1
                else:
                    family_dict['SINE'] = 1
            # For MITEFINDER pipeline, add the number of 'MITEs' to a dict
            elif pipeline == 'MITEFINDER':
                if "MITE" in family_dict:
                    family_dict["MITE"] += 1
                else:
                    family_dict["MITE"] = 1
            # For HELIANO pipeline, denote whether or not it's non-auto, auto, or orfonly - and add that to dict
            elif pipeline == 'HELIANO':
                if '_auto_' in sequence_info:
                    if 'autonomous_helitron' in family_dict:
                        family_dict['autonomous_helitron'] += 1
                    else:
                        family_dict['autonomous_helitron'] = 1
                elif '_nonauto_' in sequence_info:
                    if 'non_autonomous_helitron' in family_dict:
                        family_dict['non_autonomous_helitron'] += 1
                    else:
                        family_dict['non_autonomous_helitron'] = 1
                elif 'orfonly' in sequence_info:
                    if 'orfonly' in family_dict:
                        family_dict['orfonly'] += 1
                    else:
                        family_dict['orfonly'] = 1
            # For HITE pipeline, add the family name embedded within the sequence info to a dict (unless the sequence info indicates 'unknown')
            elif pipeline == 'HITE':
                if "Unknown" in sequence_info:
                    pass
                elif "#" in sequence_info:
                    match = re.search(r'#(.*)', sequence_info)
                    if match and match.group(1) in family_dict:
                        family_dict[match.group(1)] += 1
                    elif match:
                        family_dict[match.group(1)] = 1
                elif "Homology" in sequence_info:
                    match = re.search(r'Homology_(.*?)_\d+$', sequence_info)  # when the sequence info has homology, the classification name is after Homology_
                    if match and match.group(1) in family_dict:
                        family_dict[match.group(1)] += 1
                    elif match:
                        family_dict[match.group(1)] = 1
            # For EARLGREY pipeline, add the family name embedded within the sequence to a dict (unless the sequence info indicates 'unknown')
            elif pipeline == "EARLGREY":
                if "Unknown" in sequence_info:
                    pass
                elif "Simple_repeat" in sequence_info:
                    if "Simple Repeat" in family_dict:
                        family_dict["Simple Repeat"] += 1
                    else:
                        family_dict["Simple Repeat"] = 1
                else:
                    pattern = r'#([^_]+)_'
                    match = re.search(pattern, sequence_info)
                    if match and match.group(1) in family_dict:
                        family_dict[match.group(1)] += 1
                    elif match:
                        family_dict[match.group(1)] = 1

    # The following code deals with the last row in the df
    if current is not None and len(family_dict) > 0:  # If there is no more 'cluster' cell, but current is still not None and family_dict is greater than zero
        dframe.at[len(dframe)-1, 'family_count'] = str(family_dict).replace("{", "").replace("}", "").replace("\'", "")  # Append the family dict to the last line in the df

    return dframe



if __name__ == "__main__":
    main()
