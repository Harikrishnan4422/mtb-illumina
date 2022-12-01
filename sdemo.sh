#!/bin/sh
Sample=$1
folder='sorted_bam'
samtools view -b -f 4 "$folder"/"$Sample".sorted.bam -o "$Sample"_unmapped.bam
samtools fastq -@ 16 "$Sample"_unmapped.bam -0 "$Sample"_unmapped_1.fastq.gz
kraken2  --db /attach/data/kraken/krdb --threads 24 "$Sample"_unmapped_1.fastq.gz  --output results/"$Sample"_Taxaids.txt --use-names

