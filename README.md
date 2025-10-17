# AmphiBac-Database

The AmphiBac database contains sequence and Batrachochytrium-inhibiting functional information from bacteria isolated from the skin of amphibians.  Collation and curation of this database begain with the [Woodhams et al. 2015 Ecological Archives publication](https://esajournals.onlinelibrary.wiley.com/doi/abs/10.1890/14-1837.1). One of the primary uses of these data are predicting Batrachytrium-inhibiting function of host microbiome data generated via next generation targeted amplicon sequencing.


## Current Database

**Current Database**: 2025.1 

2025.1: This database to include  8,739 isolates. Recent updates include isolates from Brazil and New Zealand)

sequence data files are provided in two formats: fasta files and qza files.

Four distinct sequence datasets are currently provided:

(1) AmphiBac_FullDatabase_2025.1: This represents all sequenced isolates in the database including all functional categories [inhibitory, faciliating, no effect, and not tested]

(2) AmphiBac_Inhibitory_2025.1: This represents all sequenced isolates that exhibited inhibitory function against 1 or more *Batrachochytrium* fungi.

(3) AmphiBac_Facilitating_2025.1: This represents all sequenced isolates that exhibited facilitating function against 1 or more *Batrachochytrium* fungi.

(4) AmphiBac_InhibitoryStrict_2025.1: This represents a strict curation of the sequenced isolates that exhibited inhibitory function against 1 or more *Batrachochytrium* fungi that has been filtered to remove isolates that are 100% matches to isolates that exhibited facilitating function. <span style="color:purple">**This is the reccomended curation of the database for inhibitory predictions**</span>

# *NEW* AmphiBac Antifungal Prediction Pipeline

THis is a beta version of a python script for predictions, providing a unified workflow for predicting antifungal functional profiles from Illumina amplicon data using the AmphiBac database. *Disclaimer:  this has been tested on one computer so far.* Give it a go and I welcome questions and comments on utility!

# Overview

This pipeline automates antifungal function predictions using QIIME 2 and the AmphiBac reference database. You can find the antifungal_predictions_pipeline.py script in the tools folder

**Overall, it does the following:**

1. Pulls the correct AmphiBac database version from GitHub.
2. Runs closed-reference clustering of user sequences against AmphiBac (full, inhibitory, inhibitory-strict, or facilitating subsets).
3. Summarizes antifungal abundance, proportional abundance, and richness per sample.
4. Merges results into your metadata file for downstream analysis.

# Requirements

You do not need to run this inside QIIME 2 — the script automatically accesses your QIIME environment through conda run.

# Required software


| Tool                          | Purpose                | Installation      |
| ----------------------------- | ---------------------- | ----------------- |
| conda (Anaconda or Miniconda) | environment management | Install Miniconda |
|       QIIME 2 environment                        |   provides qiime, vsearch, and biom                     |     conda create -n qiime2-amplicon-2025.7 -c qiime2 -c conda-forge qiime2              |
|  Python packages: pandas, argparse                             |      data manipulation and parsing                  |    pip install pandas argparse               |

*Note*: If you are a frequent qiimer you likely have everything you need installed.  I needed to install pandas and argparse only when I trialed the script.

# Input files


| Input | Description |
| ----- | ----------- |
|  --otu-table     |      Your feature table (.qza)       |
|  --rep-seqs     |      Your representative sequences (.qza)       |
|   --metadata-file    |     Sample metadata (.tsv)        |
| --db-version  | AmphiBac version (folder name on GitHub)	2025.1        |


# Output files

Outputs are organized under the chosen --output-dir, for example:

Results
*  full/
    *  intermediate/
    *  metadata/
        *  Metadata_full_Predictions.txt
* inhibitory/
    * intermediate/
    * metadata/
        * Metadata_inhibitory_Predictions.txt
*  inhibitory_strict/
    * intermediate/
    *  metadata/
        *  Metadata_inhibitory_strict_Predictions.txt
* facilitating/
    *   intermediate/
    *   metadata/
        *   Metadata_facilitating_Predictions.txt


If you run with --modes all, a combined metadata file is generated:

Results
* Combined_Metadata_Predictions.txt

# Running the pipeline

Use the full absolute path to the script for portability across systems.

```
python /full/path/to/antifungal_predictions_pipeline.py \
  --qiime-env qiime2-amplicon-2025.7 \
  --otu-table /full/path/to/rarefied_table.qza \
  --rep-seqs /full/path/to/rep-seqs.qza \
  --metadata-file /full/path/to/sample_metadata.tsv \
  --db-version 2025.1 \
  --output-dir /full/path/to/results \
  --rarefying-depth 5000 \
  --modes all
```

# Command-line options

```
--qiime-env	Name of the QIIME 2 conda environment to use	(e.g. qiime2-amplicon-2025.7)
--otu-table	Path to feature table .qza	Required
--rep-seqs	Path to representative sequences .qza	Required
--metadata-file	Path to metadata .tsv	Required
--sample-id-col	Column name for sample IDs in metadata	(e.g. SampleID) Required
--db-version	Version of AmphiBac database to use (e.g. 2025.1)	Required
--modes	Which database subsets to use: full, inhibitory, inhibitory_strict, facilitating, or all	all (default)
--identity	Sequence identity threshold for clustering	0.99 (default)
--rarefying-depth	Rarefaction depth for proportional abundance calculations (e.g.5000)	Required
--output-dir	Directory where results will be written	(e.g.,./results) Required
```
# What each mode does

**full:** uses AmphibBac_FullDatabase_<version>.qza	to predict matches to all all isolates in the database. 
* Output columns include Full_Total, Full_Proportion, Full_Richness
    
**inhibitory:**	uses AmphibBac_Inhibitory_<version>.qza	to predict matches to Bd/Bsal inhibitory isolates.
* Output columns include Inhibitory_Total, Inhibitory_Proportion, Inhibitory_Richness

**inhibitory_strict:**	uses AmphibBac_InhibitoryStrict_<version>.qza to predict matches to the strict* inhibitory isolates.	
* Output columns include Inhibitory_strict_Total, Inhibitory_strict_Proportion, Inhibitory_strict_Richness

**facilitating:** uses AmphibBac_Facilitating_<version>.qza to predict matches to facilitating isolates.	
* Output includes Facilitating_Total, Facilitating_Proportion, Facilitating_Richness

**all:** runs all the predictions outlined above and compiled them into one metadata file. 


# Example test run
```
python /Users/mcbletz/SOFTWARE/CustomScripts/antifungal_predictions_pipeline.py \
  --qiime-env qiime2-amplicon-2025.7 \
  --otu-table /Users/mcbletz/TestData/rarefied_table.qza \
  --rep-seqs /Users/mcbletz/TestData/rep-seqs.qza \
  --metadata-file /Users/mcbletz/TestData/metadata.tsv \
  --db-version 2025.1 \
  --output-dir /Users/mcbletz/TestRun \
  --rarefying-depth 5000 \
  --modes inhibitory
```

Output:

✅ Completed INHIBITORY predictions → /Users/mcbletz/TestRun/inhibitory/metadata/Metadata_inhibitory_Predictions.txt

# Final Thoughts

Have fun! And reach out to molly.bletz@psu.edu if you have questions.

## Previous Usage of antifungal prediction script files

A bash script enabling functional predictions from microbial community data (using QIIME2) is provided in the [scripts folder](https://github.com/AmphiBac/AmphiBac-Database/tree/main/scripts)

Please see the [ReadME_Antifungal file](https://github.com/AmphiBac/AmphiBac-Database/blob/main/scripts/README_Antifungal.txt) for brieft guidance on usage.

## Questions

**Please contact:** [Molly Bletz](molly.bletz@gmail.com) or [Douglas Woodhams](dwoodhams@gmail.com) if you have questions.

