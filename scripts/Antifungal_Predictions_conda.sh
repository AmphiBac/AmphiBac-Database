#!/usr/bin/env/bash
#!/usr/bin/Rscript   
                        
echo "Whats the qiime environment you want to activate (e.g.  qiime2-2020.2)"

read qiimename

eval "$(conda shell.bash hook)"
conda activate "$qiimename"

echo "Whats the path to your rarified OTU table?"

read file1

echo "Whats the path to your representative sequence file?"

read file2

echo "Whats the path to the Antifungal database file?"

read file3

mkdir Antifungal_Predictions

cd Antifungal_Predictions

# (1) filter repset to OTU table
qiime feature-table filter-seqs --i-table "$file1" --i-data "$file2" --p-no-exclude-ids --o-filtered-data OTUtable-filtered_Repset.qza

# (2) Vsearch cluster
qiime vsearch cluster-features-closed-reference --i-sequences OTUtable-filtered_Repset.qza --i-table "$file1" --i-reference-sequences "$file3" --p-perc-identity 0.99 --p-strand both --output-dir Antifungal_Matches_99

# (3) Make a presence absence 
qiime feature-table presence-absence --i-table Antifungal_Matches_99/clustered_table.qza --o-presence-absence-table Antifungal_Matches_99/PresAbs_clustered_table.qza

# need to get out of qiime2 to run the R scripts
conda deactivate 

# 
echo "Whats the path to the Rscript file? Note: lots of code may run....its installing R dependencies" 

read Rcode

# (4) R script computations
Rscript "$Rcode"
	
