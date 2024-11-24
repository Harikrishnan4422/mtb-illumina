<<<<<<< HEAD
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
=======
# microbial-diversity
Pipeline for detection of all different bacteria present within a query sequence.

 - For Illumina - Single and Paired End and Nanopore Sequencing Samples.
 - Gives Microbial Diversity Report with different Microbial Density and Read Density in Sequencing Samples.
 - Installed Libraries -  kraken2, g++, conda, minimap2, porechop, samtools, pandas, XlsxWriter, boto3, requests, flask, mysql-connector-python.

## New Features and improvements - Jan 2023

 - RDS Databases call added
 - Database login credentials stored in environment File
>>>>>>> b38db8b (Initial commit for v2 prod version)

## Installation

 - Clone this repository:

```sh
<<<<<<< HEAD
git clone https://github.com/AarogyaAI/microbial_diversity.git
```
 - Build the docker image
 
```sh
docker build -t aai_mdd .
=======
git clone https://github.com/AarogyaAI/microbial-diversity.git
```
 - Attach the kraken2 185GB Database also and install all above libraries after installing conda:
 
```sh
cd microbial-diversity
sudo apt-get install -y kraken2 g++ samtools
conda install minimiap2
pip install pandas Xlsxwriter boto3 requests flask mysql-connector-python
git clone https://github.com/rrwick/Porechop.git
cd Porechop
python3 setup.py install
cd ../
>>>>>>> b38db8b (Initial commit for v2 prod version)
```

 - Run the container 
 
```sh
<<<<<<< HEAD
docker run aai_mdd sample_id input_type q env
```

- This request the processing of file through boto3 api to AWS Batch Architecture.
=======
python3 create_results.py
```

- Now request the processing of file through Postman with Post requests in the deployment or throught the deployed Architecture rules.
>>>>>>> b38db8b (Initial commit for v2 prod version)
