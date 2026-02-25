# SCRIPT 3

# This is the third script - It is an R script that takes as input the preprocessed training dataset, and then using the library ftrCool, hundreds of features are extracted from each sequence within the dataset. 



suppressWarnings({
  library(ftrCOOL)
})

# NOTE - so the dataset will be given to this script to be feature extracted

cat("\n")
cat("\n")
cat("-----------------------------------------------------------------------------------------------", "\n")
cat("STEP 3: Extract features from each sequence within the training dataset.", "\n")
cat("-----------------------------------------------------------------------------------------------", "\n")

# ----- args -----
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) >= 1)

infile <- as.character(args[1])          # ensure character
infile <- gsub("^\\.[/\\\\]", "", infile) # strip leading ./ or .\ (Windows)
if (!file.exists(infile)) stop(paste("Input file not found:", infile))

training_data <- read.csv(infile, stringsAsFactors = FALSE)


# Using ftrCool functions, extract a bunch of features
sequence_vector <- as.character(training_data$sequence_content)

# Compute features
suppressWarnings({
  kmer_matrix <- kNUComposition_DNA(seqs=sequence_vector, rng = 3) 
  APkNUCdi_matrix <- APkNUCdi_DNA(seqs=sequence_vector)
  APkNUCTri_matrix <- APkNUCTri_DNA(seqs=sequence_vector)
  CkSNUCpair_matrix <- CkSNUCpair_DNA(seqs=sequence_vector)
  ASDC_DNA_matrix <- ASDC_DNA(seqs=sequence_vector)
  codonUsage_matrix <- CodonUsage_DNA(seqs=sequence_vector)
  DPCP_DNA_matrix <- DPCP_DNA(seqs=sequence_vector)
  ExpectedValKmerNUC_DNA_matrix <- ExpectedValKmerNUC_DNA(seqs=sequence_vector)
  PCPseDNC_matrix <- PCPseDNC(seqs=sequence_vector)
  Mismatch_DNA_matrix <- Mismatch_DNA(seqs=sequence_vector)
  CodonFraction_matrix <- CodonFraction(seqs=sequence_vector)
  MMI_DNA_matrix <- MMI_DNA(seqs=sequence_vector)
  PseEIIP_matrix <- PseEIIP(seqs=sequence_vector)
  NUCKpartComposition_DNA_matrix <- NUCKpartComposition_DNA(seqs=sequence_vector)
  PSEkNUCdi_DNA_matrix <- PSEkNUCdi_DNA(seqs=sequence_vector)
  PSEkNUCTri_DNA_matrix <- PSEkNUCTri_DNA(seqs=sequence_vector)
})

# Add suffixes to column names for clarity
colnames(kmer_matrix) <- paste0(colnames(kmer_matrix), "_KNUComposition_DNA")
colnames(APkNUCdi_matrix) <- paste0(colnames(APkNUCdi_matrix), "_APkNUCdi_DNA")
colnames(APkNUCTri_matrix) <- paste0(colnames(APkNUCTri_matrix), "_APkNUCTri_DNA")
colnames(CkSNUCpair_matrix) <- paste0(colnames(CkSNUCpair_matrix), "_CkSNUCpair_DNA")
colnames(ASDC_DNA_matrix) <- paste0(colnames(ASDC_DNA_matrix), "_ASDC_DNA")
colnames(codonUsage_matrix) <- paste0(colnames(codonUsage_matrix), "_CodonUsage_DNA")
colnames(DPCP_DNA_matrix) <- paste0(colnames(DPCP_DNA_matrix), "_DPCP_DNA")
colnames(ExpectedValKmerNUC_DNA_matrix) <- paste0(colnames(ExpectedValKmerNUC_DNA_matrix), "_ExpectedValKmerNUC_DNA")
colnames(PCPseDNC_matrix) <- paste0(colnames(PCPseDNC_matrix), "_PCPseDNC")
colnames(Mismatch_DNA_matrix) <- paste0(colnames(Mismatch_DNA_matrix), "_Mismatch_DNA")
colnames(CodonFraction_matrix) <- paste0(colnames(CodonFraction_matrix), "_CodonFraction")
colnames(MMI_DNA_matrix) <- paste0(colnames(MMI_DNA_matrix), "_MMI_DNA")
colnames(PseEIIP_matrix) <- paste0(colnames(PseEIIP_matrix), "_PseEIIP")
colnames(NUCKpartComposition_DNA_matrix) <- paste0(colnames(NUCKpartComposition_DNA_matrix), "_NUCKpartComposition_DNA")
colnames(PSEkNUCdi_DNA_matrix) <- paste0(colnames(PSEkNUCdi_DNA_matrix), "_PSEkNUCdi_DNA")
colnames(PSEkNUCTri_DNA_matrix) <- paste0(colnames(PSEkNUCTri_DNA_matrix), "_PSEkNUCTri_DNA")
  
# Handle ZCurve separately
valid_seqs <- unlist(alphabetCheck(sequence_vector, alphabet = "dna"))

suppressWarnings({
  Zcurve36bit_DNA_matrix <- Zcurve36bit_DNA(valid_seqs)
  Zcurve144bit_DNA_matrix <- Zcurve144bit_DNA(valid_seqs)
  Zcurve12bit_DNA_matrix <- Zcurve12bit_DNA(valid_seqs)
  Zcurve48bit_DNA_matrix <- Zcurve48bit_DNA(valid_seqs)
  Zcurve9bit_DNA_matrix <- Zcurve9bit_DNA(valid_seqs)
})  

# Add suffixes to Zcurve matrices
colnames(Zcurve36bit_DNA_matrix) <- paste0(colnames(Zcurve36bit_DNA_matrix), "_Zcurve36bit_DNA")
colnames(Zcurve144bit_DNA_matrix) <- paste0(colnames(Zcurve144bit_DNA_matrix), "_Zcurve144bit_DNA")
colnames(Zcurve12bit_DNA_matrix) <- paste0(colnames(Zcurve12bit_DNA_matrix), "_Zcurve12bit_DNA")
colnames(Zcurve48bit_DNA_matrix) <- paste0(colnames(Zcurve48bit_DNA_matrix), "_Zcurve48bit_DNA")
colnames(Zcurve9bit_DNA_matrix) <- paste0(colnames(Zcurve9bit_DNA_matrix), "_Zcurve9bit_DNA")

rownames(Zcurve36bit_DNA_matrix) <- valid_seqs
rownames(Zcurve144bit_DNA_matrix) <- valid_seqs
rownames(Zcurve12bit_DNA_matrix) <- valid_seqs
rownames(Zcurve48bit_DNA_matrix) <- valid_seqs
rownames(Zcurve9bit_DNA_matrix) <- valid_seqs
  
# Get shared valid sequences
common_rows <- Reduce(intersect, list(
  rownames(kmer_matrix), rownames(APkNUCdi_matrix), rownames(APkNUCTri_matrix),
  rownames(CkSNUCpair_matrix), rownames(ASDC_DNA_matrix), rownames(codonUsage_matrix),
  rownames(DPCP_DNA_matrix), rownames(ExpectedValKmerNUC_DNA_matrix),
  rownames(PCPseDNC_matrix), rownames(Mismatch_DNA_matrix), rownames(CodonFraction_matrix),
  rownames(MMI_DNA_matrix), rownames(PseEIIP_matrix), rownames(NUCKpartComposition_DNA_matrix),
  rownames(PSEkNUCdi_DNA_matrix), rownames(PSEkNUCTri_DNA_matrix),
  rownames(Zcurve36bit_DNA_matrix), rownames(Zcurve144bit_DNA_matrix),
  rownames(Zcurve12bit_DNA_matrix), rownames(Zcurve48bit_DNA_matrix), rownames(Zcurve9bit_DNA_matrix)
))
  
# Filter matrices to common rows
filtered_matrices <- lapply(list(
  kmer_matrix, APkNUCdi_matrix, APkNUCTri_matrix, CkSNUCpair_matrix,
  ASDC_DNA_matrix, codonUsage_matrix, DPCP_DNA_matrix, ExpectedValKmerNUC_DNA_matrix,
  PCPseDNC_matrix, Mismatch_DNA_matrix, CodonFraction_matrix, MMI_DNA_matrix,
  PseEIIP_matrix, NUCKpartComposition_DNA_matrix, PSEkNUCdi_DNA_matrix,
  PSEkNUCTri_DNA_matrix, Zcurve36bit_DNA_matrix, Zcurve144bit_DNA_matrix,
  Zcurve12bit_DNA_matrix, Zcurve48bit_DNA_matrix, Zcurve9bit_DNA_matrix
), function(mat) mat[common_rows, , drop = FALSE])

# Combine features
combined_matrix <- do.call(cbind, filtered_matrices)

# Get class labels in the correct order
subset_df <- training_data[training_data$sequence_content %in% common_rows, c("sequence_content", "TE_Order")]
subset_df <- subset_df[match(common_rows, subset_df$sequence_content), , drop = FALSE]

stopifnot(identical(common_rows, subset_df$sequence_content))

# Build final dataframe
combined_df <- cbind(seq_length = nchar(common_rows), combined_matrix, TE_Order = subset_df$TE_Order)
combined_df <- cbind(sequence_content = common_rows,
                     seq_length = nchar(common_rows),
                     combined_matrix,
                     TE_Order = subset_df$TE_Order)

# Clean output name
base_name <- basename(infile)                                    # strip any path like ./ or .\
base_name <- sub("\\.csv$", "", base_name, ignore.case = TRUE) # remove .csv
base_name <- sub("^PREPROCESSED_", "", base_name)              # remove PREPROCESSED_
output_path <- paste0("ftrCool_extracted_", base_name, ".csv")

# Write output
write.csv(combined_df, file = output_path, row.names = FALSE)
cat("\nFeature-extracted dataset saved to:", output_path, "\n")
