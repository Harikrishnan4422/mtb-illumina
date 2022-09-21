#!/bin/sh
Sample=$1
folder='sorted_bam'
porechop -i "$folder"/"$Sample".fastq.gz > "$Sample"_trimmed.fastq -t 8
minimap2 -ax map-ont genes/ref.fna "$Sample"_trimmed.fastq > "$Sample".sam
samtools view -bS "$Sample".sam > "$Sample".bam
samtools sort -@ 16 "$Sample".bam > "$Sample".sorted.bam
samtools view -b -f 4 "$Sample".sorted.bam -o "$Sample"_unmapped.bam
samtools fastq -@ 16 "$Sample"_unmapped.bam -0 "$Sample"_unmapped_1.fastq.gz
kraken2  --db /attach/data/kraken/krdb --threads 24 "$Sample"_unmapped_1.fastq.gz  --output results/"$Sample"_Taxaids.txt --use-names


