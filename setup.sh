#!/bin/bash

# This script will download all the necessary dependencies, data files and containers for the pipeline
# To run: ./setup.sh

set -euo pipefail

# Load all dependencies
load_module() {
    if module avail "$1" 2>&1 | grep -q "$1"; then
        module load "$1"
    fi
}

module load StdEnv/2020
load_module gcc/13.3
load_module apptainer
load_module cd-hit/4.8.1
load_module python/3.11
load_module R/4.3.1
load_module emboss/6.6.0
load_module hmmer

if command -v python3 &> /dev/null; then
    python3 -m pip install --upgrade pip
    python3 -m pip install pandas biopython "numpy==1.25.2" matplotlib seaborn joblib "scikit-learn==1.3.2" "imbalanced-learn==0.11.0"
fi

if command -v R &> /dev/null; then
    Rscript -e "install.packages(c('stringr','dplyr','knitr','openxlsx','ftrCOOL'), repos='https://cloud.r-project.org')"
fi

# PFAM
# Create main directory
mkdir -p Databases
cd Databases

# Download Pfam database files
wget http://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.hmm.dat.gz
wget http://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.hmm.gz

# Create pfamdb and unpack
mkdir -p pfamdb

gunzip -c Pfam-A.hmm.dat.gz > pfamdb/Pfam-A.hmm.dat
gunzip -c Pfam-A.hmm.gz > pfamdb/Pfam-A.hmm

# Remove compressed files
rm Pfam-A.hmm.gz Pfam-A.hmm.dat.gz

# Clone pfam_scan
git clone https://github.com/aziele/pfam_scan

echo "Pfam database and pfam_scan successfully installed in Databases/"
cd ..


# Training Dataset and Sif Files from Zenodo
# Download TRAINING DATASET
wget -O training_dataset.CSV https://zenodo.org/records/18777048/files/training_dataset.CSV?download=1

# Download TE Sif Files
mkdir -p TE_pipeline_sif_files
wget -O TE_pipeline_sif_files/annosine_v2.sif https://zenodo.org/records/18777146/files/annosine_v2.sif?download=1
wget -O TE_pipeline_sif_files/earlgrey_v5.1.sif https://zenodo.org/records/18777146/files/earlgrey_v5.1.sif?download=1
wget -O TE_pipeline_sif_files/heliano.sif https://zenodo.org/records/18777146/files/heliano.sif?download=1
wget -O TE_pipeline_sif_files/HiTE_V3.3.3.sif https://zenodo.org/records/18777146/files/HiTE_V3.3.3.sif?download=1
