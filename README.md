# microbial-diversity
Pipeline for detection of all different bacteria present within a query sequence.

 - For Illumina - Single and Paired End and Nanopore Sequencing Samples.
 - Gives Microbial Diversity Report with different Microbial Density and Read Density in Sequencing Samples.
 - Installed Libraries -  kraken2, g++, conda, minimap2, porechop, samtools, pandas, XlsxWriter, boto3, requests, flask, mysql-connector-python.

## New Features and improvements - Jan 2023

 - RDS Databases call added
 - Database login credentials stored in environment File

## Installation

 - Clone this repository:

```sh
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
```

 - Run the container 
 
```sh
python3 create_results.py
```

- Now request the processing of file through Postman with Post requests in the deployment or throught the deployed Architecture rules.
