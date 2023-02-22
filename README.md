# AmphiBac-Database

The AmphiBac database contains sequence and Batrachochytrium-inhibiting functional information from bacteria isolated from the skin of amphibians.  Collation and curation of this database begain with the [Woodhams et al. 2015 Ecological Archives publication](https://esajournals.onlinelibrary.wiley.com/doi/abs/10.1890/14-1837.1). One of the primary uses of these data are predicting Batrachytrium-inhibiting function of host microbiome data generated via next generation targeted amplicon sequencing.

## Current Database

We have now updated and expanded this database to include over 7,900 isolates. The current release of the database is version: [AmphiBac-2023.2](https://github.com/AmphiBac/AmphiBac-Database/tree/main/AmphiBac-2023.2)

sequence data files are provided in two formats: fasta files and qza files.

Four distinct sequence datasets are currently provided:

(1) AmphiBac_FullDatabase_2023.2: This represents all sequenced isolates in the database including all functional categories [inhibitory, faciliating, no effect, and not tested]

(2) AmphiBac_Inhibitory_2023.2: This represents all sequenced isolates that exhibited inhibitory function against 1 or more *Batrachochytrium* fungi.

(3) AmphiBac_Facilitating_2023.2: This represents all sequenced isolates that exhibited facilitating function against 1 or more *Batrachochytrium* fungi.

(4) AmphiBac_InhibitoryStrict_2023.2: This represents a strict curation of the  sequenced isolates that exhibited inhibitory function against 1 or more *Batrachochytrium* fungi that has been filtered to remove isolates that are 100% matches to isolates that exhibited facilitating function. <span style="color:purple">**This is the reccomended curation of the database for inhibitory predictions**</span>

## Usage of antifungal prediction script files

A bash script enabling functional predictions from microbial community data (using QIIME2) is provided in the [scripts folder](https://github.com/AmphiBac/AmphiBac-Database/tree/main/scripts)

Please see the [ReadME_Antifungal file](https://github.com/AmphiBac/AmphiBac-Database/blob/main/scripts/README_Antifungal.txt) for brieft guidance on usage.

## Questions

*Please note: these pages and information are still under construction* Please contact [Molly Bletz](molly.bletz@gmail.com) or [Douglas Woodhams](dwoodhams@gmail.com) if you have questions.

