#!/usr/bin/env python

# FUNCTIONALITY: This script takes as input the cd_hit '.clstr' file (the one clustered at 80%), then runs it through R to get a rough excel output file.
              # After this rough excel file is produced, it gets run through the "_optimize_csv.py" file to get a better formatted version of the excel file.



import sys
import subprocess
import pandas as pd
sys.path.append('./Scripts') # I have to specify this path so the following two import statements work
import _optimize_csv
import _add_metrics



# Check if the correct number of arguments are provided
if len(sys.argv) != 2:
    print("Usage: python format_data.py <final_cdhit '.clstr' file>") # This is the template for the command line that was passed through in main.sh
    sys.exit(1)

# Assign variables and naming conventions
final_clstr = sys.argv[1]
final_clstr_location = f"../{final_clstr}"
final_clstr_no_extension = final_clstr.replace(".clstr", "")

# Print the final_clstr for debugging
print(f"final_clstr: {final_clstr}")



# Denote the working directory where the .clstr file (final_clstr) is located for the R script to run
path_to_wd = "./"

# _clstr_to_excel.R - The below format basically passes in these different variables to the R script like command-line-arguments
subprocess.run(["Rscript", "./Scripts/_clstr_to_excel.R", path_to_wd, final_clstr]) # Runs the clstr_to_excel R script - passing in the path to working directory and the .clstr file



# Now we call _optimize_excel.py to optimize the rough excel file
rough_excel = f"{final_clstr_no_extension}_PROTOTYPE.xlsx" # assign the rough excel variable to the output excel file produced from the above R script (which will be
                                                           # outputted to the main directory, and is named "{final_clstr_no_extension}_PROTOTYPE.xlsx)

formatted_excel = _optimize_csv.main(rough_excel) # Passes in the Prototype Excel File be converted into a better formatted Excel Datasheet



# In order to get the base name of the file (just the organism name essentially, so that we can add on to it for naming other files), simply replace the "FINAL_cdhit_" portion of the name
base_name = final_clstr_no_extension.replace("FINAL_cdhit_", "")

# _add_metrics.py - Add metrics (More columns) to the better formatted excel file and output file
final_metricized_excel = _add_metrics.main(formatted_excel)

# Output final Excel file
final_metricized_excel.to_csv(f"COMPLETE_TE_RESULTS_{base_name}.csv", index=False)


