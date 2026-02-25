# SCRIPT 3 - NOTE: This script only works for extracting features from an UNLABELLED dataset (ie. No TE_Order column)

# This script takes as input a preprocessed dataset and extracts hundreds of sequence features using the ftrCOOL package.

suppressWarnings({
  library(ftrCOOL)
})

cat("\n")
cat("\n")
cat("-----------------------------------------------------------------------------------------------", "\n")
cat("STEP 3: Extract features from each sequence within the dataset.", "\n")
cat("-----------------------------------------------------------------------------------------------", "\n")

# ----- args -----
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) >= 2)

infile <- as.character(args[1])
dataset_name <- as.character(args[2])

infile <- gsub("^\\.[/\\\\]", "", infile)
if (!file.exists(infile)) stop(paste("Input file not found:", infile))

training_data <- read.csv(infile, stringsAsFactors = FALSE)

# Using ftrCOOL functions, extract a bunch of features
sequence_vector <- as.character(training_data$sequence_content[1:100]) # FOR TESTING - first 100 sequences only.

# Keep the Sequence_ID column aligned with sequence_content
sequence_ids <- as.character(training_data$Sequence_ID[1:100])

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

# Add suffixes to column names
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
  Zcurve9bit_DNA_matrix  <- Zcurve9bit_DNA(valid_seqs)
})

# Add suffixes to Zcurve matrices
colnames(Zcurve36bit_DNA_matrix)  <- paste0(colnames(Zcurve36bit_DNA_matrix),  "_Zcurve36bit_DNA")
colnames(Zcurve144bit_DNA_matrix) <- paste0(colnames(Zcurve144bit_DNA_matrix), "_Zcurve144bit_DNA")
colnames(Zcurve12bit_DNA_matrix)  <- paste0(colnames(Zcurve12bit_DNA_matrix),  "_Zcurve12bit_DNA")
colnames(Zcurve48bit_DNA_matrix)  <- paste0(colnames(Zcurve48bit_DNA_matrix),  "_Zcurve48bit_DNA")
colnames(Zcurve9bit_DNA_matrix)   <- paste0(colnames(Zcurve9bit_DNA_matrix),   "_Zcurve9bit_DNA")

rownames(Zcurve36bit_DNA_matrix)  <- valid_seqs
rownames(Zcurve144bit_DNA_matrix) <- valid_seqs
rownames(Zcurve12bit_DNA_matrix)  <- valid_seqs
rownames(Zcurve48bit_DNA_matrix)  <- valid_seqs
rownames(Zcurve9bit_DNA_matrix)   <- valid_seqs

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

filtered_matrices <- lapply(list(
  kmer_matrix, APkNUCdi_matrix, APkNUCTri_matrix, CkSNUCpair_matrix,
  ASDC_DNA_matrix, codonUsage_matrix, DPCP_DNA_matrix, ExpectedValKmerNUC_DNA_matrix,
  PCPseDNC_matrix, Mismatch_DNA_matrix, CodonFraction_matrix, MMI_DNA_matrix,
  PseEIIP_matrix, NUCKpartComposition_DNA_matrix, PSEkNUCdi_DNA_matrix,
  PSEkNUCTri_DNA_matrix, Zcurve36bit_DNA_matrix, Zcurve144bit_DNA_matrix,
  Zcurve12bit_DNA_matrix, Zcurve48bit_DNA_matrix, Zcurve9bit_DNA_matrix
), function(mat) mat[common_rows, , drop = FALSE])

combined_matrix <- do.call(cbind, filtered_matrices)

# Add Sequence_ID column
combined_df <- cbind(
  Sequence_ID = sequence_ids,
  sequence_content = common_rows,
  seq_length = nchar(common_rows),
  combined_matrix
)

# Use the dataset_name (passed from Python) to name the output file
output_path <- paste0("ftrCool_extracted_", dataset_name, ".csv")

write.csv(combined_df, file = output_path, row.names = FALSE)
cat("\nFeature-extracted dataset saved to:", output_path, "\n")
