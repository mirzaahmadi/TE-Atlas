# FUNCTIONALITY: This script is called my 'format_data.py'. This script will take as input the .clstr file produced by cd-hit, and convert it into a rough excel file.

args <- commandArgs(trailingOnly = TRUE) # Turn on R command line arguments so the 'format_data.py' file (the one that calls this R script)  file can pass in the appropriate arguments
path_to_this_folder <- args[1] # The first command line argument (in the 'format_data.py' file) will be the path to this folder (this is our current directory that holds all the needed files for this script to work)
setwd(path_to_this_folder) # sets the working directory

# Confirm the working directory

print("----------------------------------------- _clstr_to_excel.R -----------------------------------------")
print(paste("Working directory is set to:", getwd()))
cat("\n")

# If not already installed - necessary libraries will be installed
if (!require("stringr")) install.packages("stringr", dependencies=TRUE)
if (!require("dplyr")) install.packages("dplyr", dependencies=TRUE)
if (!require("knitr")) install.packages("knitr", dependencies=TRUE)
if (!require("openxlsx")) install.packages("openxlsx", dependencies=TRUE)

#load the necessary libraries
library(stringr)
library(dplyr)
library(knitr)
library(openxlsx)

# Read in one of my '.clstr' files and produce the first few lines of output (unchanged)
clstr_file <- args[2] # This takes in the second command line argument (from the 'format_data.py" file) as the clstr_file
clstr_file_no_parts <- strsplit(clstr_file,split = "\\.")[[1]] # Splits the string clstr_file at each dot and returns the first element of the list (the parts before and after the dot)
clstr_file_no_extension <- clstr_file_no_parts[1] # Extracts the first part of the split string, which is the base name of the file without the extension

print(paste("Reading file:", clstr_file)) # prints name of file - ensures you are reading the correct one
cat("\n")
clstr <- read.csv(clstr_file, sep = "\t", row.names = NULL, header = FALSE, stringsAsFactors = FALSE)
print("Initial data:")
kable(head(clstr))
cat("\n")

# Loop through the first column value of each row. If the column value is non numeric (eg. 'cluster 0') leave it as is.
# If it is numeric, make it equal to the last non numeric value (eg. '0' will turn to 'cluster 0')
clstr2 <- clstr
n <- nrow(clstr)  # nrow is used to determine number of rows
x <- 0
numbers_only <- function(x) !grepl("\\D", x)  # numbers_only function is created that checks if given input contains only numeric characters
for (row in 1:n) {  # iterates over each row in .clstr file in the first column only
  if (numbers_only(clstr2[row, 1]) == TRUE) {  # if value is numeric, assign the value of 'x' to that value
    clstr2[row, 1] <- x
  } else {
    x <- clstr2[row, 1]  # This assigns the value of the row to the variable x, ensuring x retains the last value it had in the loop
  }
}

# BELOW - These print statements are taken out, as not to confuse the pipeline with a more than necessary numnber of printed outputs to console
# print("Updated data:") #This prints what the updated data looks like - the first column should all be " Cluster 'x' "
# kable(head(clstr2))
# print("")

# counts up the frequency of each unique value in column 1
clstr.sums <- data.frame(dplyr::count(clstr2, V1))  # dataframe which holds the frequencies of each unique value

# BELOW - These print statements are taken out, as not to confuse the pipeline with a more than necessary numnber of printed outputs to console
# print("Cluster sums:")
# kable(head(clstr.sums))

# This just shows you the first transition point to make sure it is laid out as planned
if (nrow(clstr.sums) > 0) {
  switch <- clstr.sums[1, 2]  # selects the element in the first row and second column of the clstr.sums dataframe
  # print(paste("Switch value: ", switch))
} else {
  switch <- 1
  # print("Warning: 'clstr.sums' is empty, setting 'switch' to 1.")
}

# Adjust the indices to be within valid bounds
start_index <- max(1, switch - 4)
end_index <- min(n, switch + 4)
clstr3 <- cbind(clstr2[1], clstr)

# BELOW - These print statements are taken out, as not to confuse the pipeline with a more than necessary numnber of printed outputs to console
# print("Combined data:")
# kable(clstr3[start_index:end_index, ])

# This gets rid of rows that have an empty value for 'V2'
if ("V2" %in% colnames(clstr2)) {
  clstr4 <- clstr2[-which(clstr2$V2 == ""), ]
  print("Filtered data:")
  print(head(clstr4))
  cat("\n")
} else {
  clstr4 <- clstr2
  print("Warning: Column 'V2' not found, skipping filtering.")
}

# We need to * remove “>” * split V2 by “aa,” and by “… at” and by “%,”
clstr5 <- clstr4
clstr5[] <- lapply(clstr5, gsub, pattern='>', replacement='')
clstr5.2 <- data.frame(str_split_fixed(clstr5$V2, "nt, ", 2))
clstr5.3 <- data.frame(str_split_fixed(clstr5.2$X2, "... ", 2))
clstr6 <- cbind(clstr5[1], clstr5.2[1], clstr5.3[1:2])

# Finally, create the table that puts all of these columns together
colnames(clstr6) <- c("cluster", "length (nucleotides [nt] long)", "TE Id", "location + similarity percentage (* = Representative sequence)")
#clstr6 is the final Data

# BELOW - These print statements are taken out, as not to confuse the pipeline with a more than necessary numnber of printed outputs to console
# print("Final data:")
# kable(head(clstr6))

# Create Excel file for clstr6
excel_file <- file.path(path_to_this_folder, paste0(clstr_file_no_extension, "_PROTOTYPE.xlsx")) # This creates a full file path for the Excel file produced - the name of the Excel file ends with "_PROTOTYPE.xlsx"
write.xlsx(clstr6, excel_file) # This writes the dataframe clstr6 to the Excel file
print(paste("File", excel_file, "has been created.")) # This prints that the "xxx_PROTOTYPE.xlsx" file has been created to the console
cat("\n")
print("----------------------------------------------------------------------------------------------------")
cat("\n")
cat("\n")
cat("\n")
