#!/bin/sh
Sample=$1
folder='sorted_bam'
samtools view -b -f 4 "$folder"/"$Sample".sorted.bam -o "$Sample"_unmapped.bam # extract unmapped reads from input bam file
samtools fastq -@ 16 "$Sample"_unmapped.bam -1 "$Sample"_unmapped_1.fastq.gz -2 "$Sample"_unmapped_2.fastq.gz # convert unmapped bam to fastq
kraken2  --db /attach/data/kraken/krdb --threads 24  "$Sample"_unmapped_1.fastq.gz  "$Sample"_unmapped_2.fastq.gz  --output results/"$Sample"_Taxaids.txt --use-names # kraken2 to detect microbial diveristy

