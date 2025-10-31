# Comprehensive Genomic Health Dashboard

## 🧬 Project Overview

A comprehensive Streamlit-based web application for personal genomic analysis, providing detailed insights into clinical risks, pharmacogenomics, polygenic risk scores, wellness traits, and advanced analytics from DNA data. Features an enhanced PDF report generator that transforms genetic data into educational, actionable health insights with evidence-based star ratings and personalized recommendations.

## ✨ Key Features

### Core Analysis Modules
- **Clinical Risk & Carrier Status**: Assess genetic risks for 50+ diseases and carrier status for inherited conditions using ClinVar and local databases
- **Pharmacogenomics (PGx) Report**: Analyze how genetics affect drug metabolism and response for 12+ medications using star allele genotyping and CPIC guidelines
- **Polygenic Risk Score (PRS) Dashboard**: Calculate risk scores for complex diseases using both simplified (3-5 SNPs) and genome-wide models from PGS Catalog with enhanced explainability
- **Holistic Wellness & Trait Profile**: Explore genetic influences on 30+ wellness traits including nutritional genetics, fitness profiles, and lifestyle factors
- **Advanced Analytics & Exploration**: Deep dive with custom queries, population frequency analysis, functional impact analysis, and research tools using bioinformatics utilities
- **Data Portability**: Export and manage genetic data in multiple formats with comprehensive metadata

### Recent Upgrades & Enhancements

#### 🚀 Performance & Data Processing
- **Polars Migration**: Upgraded to Polars DataFrames for 10-100x faster data processing and memory efficiency compared to traditional Pandas workflows
- **Optimized Parsing**: Enhanced DNA file parsing with Polars for AncestryDNA, 23andMe, MyHeritage, and LivingDNA formats

#### 🧬 Ancestry Inference Improvements
- **Advanced Ancestry Detection**: PCA-based and KNN-based ancestry inference using ancestry-informative markers (AIMs)
- **Multi-Method Approach**: Combines frequency-based, PCA-based, and clustering-based inference for higher accuracy
- **Ancestry-Adjusted PRS**: Automatic ancestry inference for more accurate polygenic risk score calculations across diverse populations
- **Confidence Scoring**: Provides confidence scores for ancestry predictions with validation metrics

#### 📊 Linkage Disequilibrium (LD) Heatmaps
- **LD Matrix Visualization**: Interactive heatmaps showing linkage disequilibrium patterns between genetic variants
- **Population-Specific LD**: LD calculations adjusted for different ancestral populations
- **Research Tools**: Advanced analytics for geneticists and researchers studying haplotype blocks

#### 🔬 Functional Impact Analysis
- **SNP Effect Prediction**: Comprehensive analysis of how genetic variants affect protein function and enzyme activity
- **Mutation Classification**: Automated classification of missense, synonymous, and regulatory mutations
- **Drug Metabolism Insights**: Enhanced predictions for pharmacogenomic variants affecting drug response
- **Sequence Context Analysis**: Integration with BioPython for detailed sequence-based functional predictions

#### 📈 PRS Explainability Features
- **Transparent Scoring**: Detailed breakdown of how each SNP contributes to polygenic risk scores
- **Model Validation**: Comprehensive validation metrics for PRS calculations including coverage percentage and confidence intervals
- **Ancestry Adjustments**: Population-specific adjustments for more accurate risk assessments
- **Educational Insights**: Clear explanations of PRS methodology and limitations for better user understanding

### Enhanced PDF Report Generator
- **Educational Journey**: Transforms genetic data into engaging learning experiences with analogies and explanations
- **Evidence-Based**: Star ratings (★☆☆☆☆) showing scientific confidence for each finding based on clinical guidelines
- **Actionable Insights**: Clear next steps tailored to genetic profiles with personalized recommendations
- **Visual Explanations**: Interactive charts and metabolism funnel graphics for complex concepts
- **Comprehensive Coverage**: 100+ genetic conditions across multiple health categories
- **Privacy-First**: Local processing with no external data transmission

## 🔬 Data Sources & Scientific Foundation

### Primary Data Sources
- **ClinVar** (NCBI): Curated database of genetic variants and their clinical significance
- **dbSNP** (NCBI): Comprehensive catalog of genetic variation
- **Ensembl**: Genome annotation and variation data
- **1000 Genomes Project**: Global population genetic variation reference
- **GWAS Catalog**: Genome-wide association study results
- **PGS Catalog**: Polygenic risk score models and validation data

### Pharmacogenomics Databases
- **PharmGKB**: Pharmacogenomics knowledge resource
- **CPIC Guidelines**: Clinical Pharmacogenetics Implementation Consortium
- **DrugBank**: Comprehensive drug information database

### Local Datasets
- Gene annotations with chromosomal locations
- SNP annotations with clinical significance
- Population frequency data across ethnic groups
- ClinVar pathogenic variants database

### Quality Assurance
- **Peer-reviewed studies**: All risk associations based on published GWAS
- **Clinical validation**: PGx recommendations from CPIC and FDA guidelines
- **Population diversity**: Models validated across multiple ethnic groups
- **Regular updates**: SNP databases updated quarterly from primary sources
- **Evidence-based star ratings**: ★★★★★ (monogenic/cancer), ★★★★☆ (cardiovascular/PGx), ★★★☆☆ (wellness)

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager
- Git
- 4GB+ RAM recommended for genome-wide PRS
- Additional dependencies for enhanced features:
  - Polars >=0.19.0 (for high-performance data processing)
  - scikit-learn >=1.3.0 (for ancestry inference and machine learning)
  - statsmodels >=0.14.0 (for statistical analysis and LD calculations)

### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd genetics

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run src/app.py
```

### Docker Deployment (Future)
```bash
docker build -t genomic-dashboard .
docker run -p 8501:8501 genomic-dashboard
```

### Data Files Setup

This application requires the ClinVar database files for clinical variant analysis. These are large files (~1GB compressed) that need to be downloaded locally.

#### Download ClinVar Database Files

1. **Download the compressed VCF file**:
   ```bash
   cd data/
   wget ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz
   ```

2. **Download the tabix index file** (required for efficient querying):
   ```bash
   wget ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz.tbi
   ```

3. **Optional: Extract the uncompressed VCF file** (if needed for certain analyses):
   ```bash
   gunzip -c clinvar.vcf.gz > clinvar.vcf
   ```

#### Alternative Download Methods

- **Using curl**:
  ```bash
  curl -O ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz
  curl -O ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz.tbi
  ```

- **Manual Download**: Visit [NCBI ClinVar FTP](ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/) and download `clinvar.vcf.gz` and `clinvar.vcf.gz.tbi`

#### File Locations

Ensure the files are placed in the `data/` directory:
- `data/clinvar.vcf.gz` (compressed VCF file)
- `data/clinvar.vcf.gz.tbi` (tabix index)
- `data/clinvar.vcf` (uncompressed VCF, optional)

#### Notes

- The download may take several minutes depending on your internet connection
- These files are updated regularly by NCBI; check for newer versions periodically
- The application will use local files when available, falling back to API queries if files are missing

## 📊 Usage Guide

1. **Launch Application**: `streamlit run src/app.py`
2. **Upload DNA Data**: Support for AncestryDNA, 23andMe, MyHeritage, LivingDNA formats
3. **Navigate Modules**: Use sidebar to explore different analysis types
4. **Configure Analysis**: Choose between simplified or genome-wide models
5. **Generate Reports**: Create comprehensive PDF reports with educational content
6. **Export Results**: Download analysis in multiple formats (PDF, JSON, CSV)

### Module-Specific Usage

#### Clinical Risk Analysis
- Pathogenic variant screening using ClinVar API with local fallback
- Recessive carrier status for 50+ genetic conditions
- Hereditary cancer syndrome analysis
- Cardiovascular and neurodegenerative risk assessment
- ACMG secondary findings screening

#### Pharmacogenomics (PGx)
- Star allele genotyping for CYP2C19, CYP2D6, CYP2C9, TPMT, DPYD
- CPIC guideline-based dosing recommendations
- Adverse drug reaction sensitivity analysis
- Drug-gene interaction visualization

#### Polygenic Risk Scores (PRS)
- Simplified models (3-5 SNPs) for quick assessment
- Genome-wide models (thousands of SNPs) from PGS Catalog
- Ancestry-aware calculations with automatic inference and confidence scoring
- PRS Explainability: Detailed breakdown of SNP contributions and model validation
- Lifetime risk projections with scenario analysis
- Population comparison visualizations with ancestry adjustments

#### Wellness & Trait Analysis
- Nutritional genetics (lactose tolerance, caffeine metabolism, vitamin processing)
- Fitness genetics (ACTN3 power/sprint vs endurance analysis)
- Methylation pathway analysis (COMT enzyme activity)
- Chronobiology and sleep traits
- Sensory perception genetics (taste, smell)

## 🏥 Medical & Ethical Considerations

### Important Disclaimers
**This application is for informational and educational purposes only. It is not a medical device and should not be used for medical diagnosis or treatment decisions.**

- **Not Medical Advice**: Results should not replace professional medical consultation
- **Research Tool**: Intended for educational and research purposes
- **Clinical Validation**: Recommendations based on peer-reviewed studies
- **Individual Variation**: Genetic risks are probabilistic, not deterministic
- **Regular Updates**: Genetic knowledge evolves; use latest version

### Privacy & Security
- **Local Processing**: All analysis performed client-side
- **No Data Storage**: Genetic data never transmitted to external servers
- **GDPR Compliant**: No personal data collection or tracking
- **Open Source**: Transparent algorithms and data sources
- **API Rate Limiting**: Respectful use of external APIs with caching

## 🏗️ Technical Architecture

### Core Technologies
- **Frontend**: Streamlit with responsive design
- **Backend**: Python 3.8+ with async processing
- **Data Processing**: Polars (primary), Pandas, NumPy, SciPy for statistical analysis
- **Machine Learning**: scikit-learn for ancestry inference and PRS modeling
- **Visualization**: Plotly, Matplotlib, Seaborn for interactive charts and LD heatmaps
- **PDF Generation**: ReportLab with custom educational templates
- **Bioinformatics**: Biopython, PyVCF, PySAM, PyFAIDX for sequence analysis and functional impact
- **APIs**: RESTful integration with ClinVar, PharmGKB, PGS Catalog, PubMed, gnomAD
- **Testing**: pytest with comprehensive unit and integration tests

### Project Structure
```
genetics/
├── src/                          # Source code
│   ├── app.py                    # Main Streamlit application
│   ├── utils.py                  # Utility functions and DNA file parsing (Polars-enabled)
│   ├── render_*.py               # Module-specific renderers
│   ├── bioinformatics_utils.py   # Advanced SNP analysis tools with functional impact
│   ├── api_functions.py          # External API integrations with caching
│   ├── local_data_utils.py       # Offline dataset management
│   ├── pgx_star_alleles.py       # Star allele genotyping
│   ├── genomewide_prs.py         # Genome-wide PRS calculations with explainability
│   ├── ancestry_inference.py     # Advanced ancestry inference (PCA/KNN-based)
│   ├── lifetime_risk.py          # Lifetime risk projections
│   ├── pdf_generator/            # Enhanced PDF generator
│   │   ├── main.py              # PDF orchestration
│   │   ├── sections.py          # Report sections
│   │   ├── visualizations.py    # Charts and graphics
│   │   └── utils.py             # PDF utilities
│   └── snp_data.py              # Genetic variant databases
├── data/                         # Datasets and references
│   ├── datasets/                 # Local genetic datasets
│   │   ├── gene_annotations.tsv
│   │   ├── snp_annotations.tsv
│   │   └── population_frequencies.tsv
│   ├── ancestry_knn_model.joblib # KNN ancestry model
│   ├── ancestry_pca_model.joblib # PCA ancestry model
│   ├── ancestry_snps.npy         # Ancestry-informative SNPs
│   ├── clinvar.vcf.gz           # ClinVar database
│   └── cache/                   # API response cache
├── tests/                        # Test suite
│   ├── test_*.py                # Unit and integration tests
│   ├── test_polars_migration.py  # Polars migration tests
│   ├── test_ancestry_inference.py # Ancestry inference tests
│   ├── test_ld_heatmaps.py       # LD heatmap tests
│   ├── test_functional_impact.py # Functional impact tests
│   └── test_prs_explainability.py # PRS explainability tests
├── docs/                         # Documentation
└── requirements.txt             # Python dependencies
```

### API Integration Architecture
- **Rate Limiting**: 30 requests/minute with exponential backoff
- **Caching**: File-based cache with 24-hour expiry
- **Fallbacks**: Local data when APIs unavailable
- **Error Handling**: Graceful degradation with user notifications
- **Health Monitoring**: Real-time API status checking

## 🧪 Testing

### Test Coverage
```bash
# Run full test suite
python -m pytest tests/

# Run specific test
python -m pytest tests/test_enhanced_pdf.py

# Run with coverage
python -m pytest --cov=src tests/

# Run integration tests
python -m pytest tests/test_integration.py
```

### Test Categories
- **Unit Tests**: Individual function testing
- **Integration Tests**: API and data pipeline testing
- **PDF Generation Tests**: Report generation validation
- **Bioinformatics Tests**: SNP analysis accuracy and functional impact
- **Polars Migration Tests**: Data processing performance and compatibility
- **Ancestry Inference Tests**: PCA/KNN model accuracy and validation
- **LD Heatmap Tests**: Linkage disequilibrium calculations and visualization
- **PRS Explainability Tests**: Risk score transparency and model validation
- **UI Tests**: Streamlit interface functionality

## 🤝 Contributing

We welcome contributions from the genomics, bioinformatics, and healthcare communities!

### Development Guidelines
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Test** thoroughly with existing test suite
4. **Document** new features and API changes
5. **Submit** a Pull Request with detailed description

### Code Standards
- **PEP 8** compliance for Python code
- **Comprehensive testing** (unit tests, integration tests)
- **Documentation** for all public functions
- **Type hints** for better code maintainability
- **Error handling** with informative messages

## 📚 Documentation & Resources

### User Guides
- [Getting Started Guide](docs/getting-started.md)
- [Analysis Modules Overview](docs/analysis-modules.md)
- [PDF Report Guide](docs/pdf-reports.md)
- [Troubleshooting FAQ](docs/troubleshooting.md)
- [New Features Guide](docs/new-features.md) - Polars migration, ancestry inference, LD heatmaps, functional impact, PRS explainability

### Technical Documentation
- [API Reference](docs/api-reference.md)
- [Data Sources Guide](docs/data-sources.md)
- [Development Setup](docs/development.md)
- [Testing Guide](docs/testing.md)
- [Performance Optimization](docs/performance.md) - Polars best practices and benchmarking

### Scientific References
- [Genetic Risk Factors](docs/genetic-risks.md)
- [Pharmacogenomics Guide](docs/pharmacogenomics.md)
- [Polygenic Risk Scores](docs/polygenic-risks.md)
- [Ancestry Inference Methods](docs/ancestry-inference.md)
- [Linkage Disequilibrium Analysis](docs/ld-analysis.md)
- [Functional Impact Prediction](docs/functional-impact.md)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

### Scientific Collaborations
- **NCBI ClinVar**: For comprehensive variant interpretation
- **Ensembl Project**: For genome annotation data
- **GWAS Catalog**: For association study results
- **PGS Catalog**: For polygenic risk score resources
- **PharmGKB**: For pharmacogenomics knowledge
- **CPIC**: For clinical dosing guidelines

### Open Source Libraries
- **Streamlit**: For the web application framework
- **Biopython**: For bioinformatics utilities
- **ReportLab**: For PDF generation capabilities
- **Pandas/NumPy**: For data manipulation and analysis
- **Plotly**: For interactive visualizations

### Research Community
- Built with contributions from the personal genomics and precision medicine research community
- Inspired by the growing field of consumer genetics and direct-to-consumer genetic testing
- Committed to advancing genomic literacy and responsible genetic testing practices

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Documentation**: [Project Wiki](https://github.com/your-repo/wiki)
- **Email**: [Contact Information]

---

**Last Updated**: October 2025
**Version**: 2.2.0
**Python Version**: 3.8+
**License**: MIT