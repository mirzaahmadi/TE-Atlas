# FUNCTIONALITY: This script is called by 'format_data.py'. After the rough excel file is produced by '_clstr_to_excel.R' (which is a script also called by 'format_data.py'), this file will take that rough excel
                # file as input, and convert it to a much better formatted file (More interpretable columns with better aesthetics and clarity).

import pandas as pd



def main(file_name):
    modified_df = modify(file_name) # format the file so it's easily readable
    return modified_df



def modify(file_name):
    # Read the rough Excel file into a DataFrame
    df = pd.read_excel(file_name)
    # Splitting 'TE Id' column into two columns
    df[['Pipeline Used', 'Sequence Information']] = df['TE Id'].str.split('_', n=1, expand=True)
    # Splitting 'location + similarity percentage (* = Representative sequence)' column into two columns
    df[['location', 'similarity (%)']] = df['location + similarity percentage (* = Representative sequence)'].str.rsplit('/', n=1, expand=True)
    # Adding 'Representative Sequence?' column based on '*'
    df['Representative Sequence?'] = df.apply(lambda row: 'YES' if '*' in row["location + similarity percentage (* = Representative sequence)"] else 'No', axis=1)
    # Reordering columns
    df = df[['cluster', 'length (nucleotides [nt] long)', 'Pipeline Used', 'Sequence Information',
            'location', 'similarity (%)', 'Representative Sequence?']]

    return df



if __name__ == "__main__":
    main()
