# Comprehensive Genomic Health Dashboard

## 🧬 Project Overview

A comprehensive Streamlit-based web application for personal genomic analysis, providing detailed insights into clinical risks, pharmacogenomics, polygenic risk scores, wellness traits, and advanced analytics from DNA data. Features an enhanced PDF report generator that transforms genetic data into educational, actionable health insights with evidence-based star ratings and personalized recommendations.

## ✨ Key Features

### Core Analysis Modules
- **Clinical Risk & Carrier Status**: Assess genetic risks for 50+ diseases and carrier status for inherited conditions using ClinVar and local databases
- **Pharmacogenomics (PGx) Report**: Analyze how genetics affect drug metabolism and response for 12+ medications using star allele genotyping and CPIC guidelines
- **Polygenic Risk Score (PRS) Dashboard**: Calculate risk scores for complex diseases using both simplified (3-5 SNPs) and genome-wide models from PGS Catalog
- **Holistic Wellness & Trait Profile**: Explore genetic influences on 30+ wellness traits including nutritional genetics, fitness profiles, and lifestyle factors
- **Advanced Analytics & Exploration**: Deep dive with custom queries, population frequency analysis, and research tools using bioinformatics utilities
- **Data Portability**: Export and manage genetic data in multiple formats with comprehensive metadata

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
- Ancestry-aware calculations with automatic inference
- Lifetime risk projections with scenario analysis
- Population comparison visualizations

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
- **Data Processing**: Pandas, NumPy, SciPy for statistical analysis
- **Visualization**: Plotly, Matplotlib, Seaborn for interactive charts
- **PDF Generation**: ReportLab with custom educational templates
- **Bioinformatics**: Biopython, PyVCF, PySAM, PyFAIDX for sequence analysis
- **APIs**: RESTful integration with ClinVar, PharmGKB, PGS Catalog, PubMed, gnomAD
- **Testing**: pytest with comprehensive unit and integration tests

### Project Structure
```
genetics/
├── src/                          # Source code
│   ├── app.py                    # Main Streamlit application
│   ├── utils.py                  # Utility functions and DNA file parsing
│   ├── render_*.py               # Module-specific renderers
│   ├── bioinformatics_utils.py   # Advanced SNP analysis tools
│   ├── api_functions.py          # External API integrations with caching
│   ├── local_data_utils.py       # Offline dataset management
│   ├── pgx_star_alleles.py       # Star allele genotyping
│   ├── genomewide_prs.py         # Genome-wide PRS calculations
│   ├── lifetime_risk.py         # Lifetime risk projections
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
│   ├── clinvar.vcf.gz           # ClinVar database
│   └── cache/                   # API response cache
├── tests/                        # Test suite
│   ├── test_*.py                # Unit and integration tests
│   └── test_enhanced_pdf.py     # PDF generator tests
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
- **Bioinformatics Tests**: SNP analysis accuracy
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

### Technical Documentation
- [API Reference](docs/api-reference.md)
- [Data Sources Guide](docs/data-sources.md)
- [Development Setup](docs/development.md)
- [Testing Guide](docs/testing.md)

### Scientific References
- [Genetic Risk Factors](docs/genetic-risks.md)
- [Pharmacogenomics Guide](docs/pharmacogenomics.md)
- [Polygenic Risk Scores](docs/polygenic-risks.md)

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

**Last Updated**: September 2025
**Version**: 2.1.0
**Python Version**: 3.8+
**License**: MIT