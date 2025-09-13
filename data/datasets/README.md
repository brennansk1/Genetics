# Local Genetic Datasets

This directory contains offline genetic datasets that can be used for enhanced analysis without requiring external API calls.

## Available Datasets

### 1. Gene Annotations (gene_annotations.tsv)
- Contains basic gene information for common genes
- Fields: gene_symbol, chromosome, start, end, strand, description
- Source: Ensembl (pre-downloaded for offline use)

### 2. SNP Annotations (snp_annotations.tsv)
- Contains annotations for common SNPs
- Fields: rsid, chromosome, position, ref_allele, alt_allele, maf, clinical_significance
- Source: dbSNP and ClinVar (pre-downloaded)

### 3. Population Frequencies (population_frequencies.tsv)
- Contains allele frequencies across different populations
- Fields: rsid, population, allele, frequency
- Source: 1000 Genomes Project (pre-downloaded)

### 4. Gene Ontology (gene_ontology.tsv)
- Contains gene ontology annotations
- Fields: gene_symbol, go_id, go_term, category
- Source: Gene Ontology Consortium (pre-downloaded)

### 5. Pathway Data (pathway_data.tsv)
- Contains pathway membership information
- Fields: gene_symbol, pathway_id, pathway_name, source
- Source: KEGG and Reactome (pre-downloaded)

### 6. Age-Specific Risk Data (age_specific_risks.tsv)
- Contains age-stratified incidence rates for common conditions
- Fields: condition, sex, age_start, age_end, incidence_rate, source
- Source: SEER, CDC NHANES, Alzheimer Association (pre-processed)

## Usage

These datasets can be loaded locally using pandas:

```python
import pandas as pd

# Load gene annotations
gene_df = pd.read_csv('datasets/gene_annotations.tsv', sep='\t')

# Load SNP annotations
snp_df = pd.read_csv('datasets/snp_annotations.tsv', sep='\t')
```

## Data Sources

All data has been sourced from real genetic databases and pre-processed for offline use:

### Gene Annotations (gene_annotations.tsv)
- **Source:** Ensembl BioMart (GRCh38/hg38)
- **Content:** Gene coordinates, descriptions, and basic annotations
- **Last Updated:** Based on Ensembl release 109
- **Fields:** gene_symbol, chromosome, start, end, strand, description

### SNP Annotations (snp_annotations.tsv)
- **Source:** dbSNP (build 155) and ClinVar
- **Content:** SNP positions, alleles, minor allele frequencies, clinical significance
- **Last Updated:** Based on dbSNP build 155 and ClinVar release
- **Fields:** rsid, chromosome, position, ref_allele, alt_allele, maf, clinical_significance, gene

### Population Frequencies (population_frequencies.tsv)
- **Source:** 1000 Genomes Project Phase 3
- **Content:** Allele frequencies across 5 major population groups (AFR, AMR, EAS, EUR, SAS)
- **Last Updated:** Based on 1000 Genomes Project Phase 3 (2015)
- **Fields:** rsid, population, allele, frequency

### Age-Specific Risk Data (age_specific_risks.tsv)
- **Source:** SEER Cancer Statistics, CDC NHANES, Alzheimer Association
- **Content:** Age-stratified incidence rates for 6 major conditions (breast cancer, prostate cancer, colorectal cancer, coronary artery disease, type 2 diabetes, Alzheimer's disease)
- **Last Updated:** Based on 2020 epidemiological data
- **Fields:** condition, sex, age_start, age_end, incidence_rate, source

## Data Processing

The datasets have been:
1. Downloaded from official sources
2. Filtered for commonly studied variants
3. Standardized for consistent formatting
4. Validated for data integrity
5. Compressed and optimized for fast loading

## Usage Notes

- All genomic coordinates are based on GRCh38/hg38 assembly
- Population codes follow 1000 Genomes Project standards
- Clinical significance follows ACMG/AMP guidelines
- Data is for research and educational purposes

## Citation

If using this data in publications, please cite the original sources:
- Ensembl: Yates et al. (2020) Nucleic Acids Research
- dbSNP: Sherry et al. (2001) Nucleic Acids Research
- ClinVar: Landrum et al. (2018) Nucleic Acids Research
- 1000 Genomes: Auton et al. (2015) Nature
- SEER: National Cancer Institute Surveillance, Epidemiology, and End Results Program
- CDC NHANES: Centers for Disease Control and Prevention National Health and Nutrition Examination Survey
- Alzheimer Association: 2020 Alzheimer Disease Facts and Figures

## License

Data is provided for educational and research purposes. Please check individual data source licenses for commercial use.