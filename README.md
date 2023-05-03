# Microbial Diversity
AAICare Microbial Diversity Pipeline for AWS deployment - Update 01 May 2023
Pipeline for detection of all different pathogens present from bacteria, fungal and viral species within a query sequence.

For Illumina - Single and Paired End and Nanopore Sequencing Samples.
Gives Microbial Diversity Report with different identified organisms and Read Density in Sequencing Samples.


## New Features and improvements - May 2023

 - Bug fixes and improvements
 - Database calling for single end and .fq.gz format files fixed
 - Using the update kraken2 database of 120GB size.

## Installed Packages

| Package   | Version      |
|-----------|--------------|
| R   | 4.2.3 |
| kraken2  | 2.1.2 |
| grep  | 3.7 |
| aws-cli  | 1.22.34   |
| perl | 5.34  |

## Installation

 - Clone this repository:

```sh
git clone https://github.com/AarogyaAI/microbial_diversity.git
```
 - Build the docker image
 
```sh
docker build -t aai_mdd .
```

 - Run the container 
 
```sh
docker run aai_mdd sample_id input_type q env
```

- This request the processing of file through boto3 api to AWS Batch Architecture.