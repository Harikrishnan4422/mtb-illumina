#!/bin/bash
# mv /data/kraken_db/* /data/
# aws s3 sync s3://webserver-deployment-data/nnaapipeline/kraken_db/ /data/kraken_db/
# mv paired_samples/* .
sample=$1 #sample name
# fastq_file_1=$2 #input 1st fastq file
# fastq_file_2=$3 #input 2ns fastq file

# # Check if the input files are single-end or paired-end
# if [ $# -eq 2 ]; then
#   # Single-end
#   fastq_file=$2
#   kraken2 --memory-mapping --use-names --thread 16 --db /data/kraken_db/ --report $sample $fastq_file
# else
#   # Paired-end
#   fastq_file_1=$2
#   fastq_file_2=$3
#   kraken2 --memory-mapping --use-names --thread 16 --db /data/kraken_db/ --report $sample --paired $fastq_file_1 $fastq_file_2
# fi

cp /data/kraken_db/$sample .
perl Kraken.pl $sample > $sample"_kraken.txt" #Parse the kraken output
Rscript Taxahist.R $sample"_kraken.txt" $sample #Plotting kraken output
# Printing top 10 species
grep -w "S" $sample | sort -nr | awk 'BEGIN {print "Sr No.\tOrganism Name\tTax ID\tNo. ofreads\tRead Density(%)"}{gsub("[][]","",$6); if($1>1) print NR"\t"$6" "$7" "$8" " $9"\t"$5"\t"$2"\t"$1}' > $sample"_tophit.txt"
