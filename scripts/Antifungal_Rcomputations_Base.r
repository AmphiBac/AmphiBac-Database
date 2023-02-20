
if (!require("readr")) {
  install.packages("readr", repos="http://cran.rstudio.com/") 
  library("readr")
}

if (!require("magrittr")) {
  install.packages("magrittr", repos="http://cran.rstudio.com/") 
  library("magrittr")
}


if (!require("dplyr")) {
  install.packages("dplyr", repos="http://cran.rstudio.com/") 
  library("dplyr")
}

if (!require("purrr")) {
  install.packages("purrr", repos="http://cran.rstudio.com/") 
  library("purrr")
}

if (!require("stringr")) {
  install.packages("stringr", repos="http://cran.rstudio.com/") 
  library("stringr")
}

if (!require("devtools")) {
  install.packages("devtools", repos="http://cran.rstudio.com/") 
  library("devtools")
}

if (!require("qiime2R")) {
  install_github("jbisanz/qiime2R") 
  library("qiime2R")
}



Antifungal_table = qiime2R::read_qza("Antifungal_Matches_99/clustered_table.qza")

Antifungal_table = as.data.frame(Antifungal_table$data)

TotalAntiFungal = Antifungal_table %>%
    select_if(is.numeric) %>%
    map_dbl(sum)

TotalAntiFungal = as.data.frame(TotalAntiFungal)

TotalAntiFungal = cbind(SampleID = rownames(TotalAntiFungal), TotalAntiFungal)

rownames(TotalAntiFungal) <- NULL

cat("Enter rarefying depth:");
rardepth <- readLines("stdin",n=1);
cat("You entered")
 str(rardepth);
cat( "\n" )

rardepth <- as.numeric(rardepth)

TotalAntiFungal_data = TotalAntiFungal %>%
  mutate(Propor_TotalAntiFungal = TotalAntiFungal/rardepth)

cat("Enter Metadata filepath:");
Metapath <- readLines("stdin",n=1);
cat("You entered")
 str(Metapath);
cat( "\n" )

Metapath <- str_trim(Metapath)

Metadata = readr::read_tsv(Metapath)

Metadata_Antifungal = TotalAntiFungal_data %>%
  left_join(Metadata, by = "SampleID")
  
Antifungal_tablePA = qiime2R::read_qza("Antifungal_Matches_99/PresAbs_clustered_table.qza")

Antifungal_tablePA = as.data.frame(Antifungal_tablePA$data)

AntiFungal_Richness = Antifungal_tablePA %>%
    select_if(is.numeric) %>%
    map_dbl(sum)

AntiFungal_Richness = as.data.frame(AntiFungal_Richness)

AntiFungal_Richness = cbind(SampleID = rownames(AntiFungal_Richness), AntiFungal_Richness)

rownames(AntiFungal_Richness) <- NULL

Metadata_Antifungal_Richness = Metadata_Antifungal %>%
  left_join(AntiFungal_Richness, by = "SampleID")
  
Metadata_Antifungal_Richness = Metadata_Antifungal_Richness %>%
	select(-TotalAntiFungal,everything())  %>%
	select(-Propor_TotalAntiFungal, everything())
	 
 
readr::write_tsv(Metadata_Antifungal_Richness,"Metadata_Antifungal_Predictions.txt")