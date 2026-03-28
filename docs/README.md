# Comprehensive Genomic Health Dashboard

## Project Overview

A Streamlit-based web application for personal genomic analysis, providing comprehensive insights into clinical risks, pharmacogenomics, polygenic risk scores, wellness traits, and advanced analytics from DNA data uploaded by users.

## Features
- **Optimized File Parsing**: Enhanced parsing for all supported DNA file formats

### 🧬 Advanced Ancestry Inference
- **Multi-Method Ancestry Detection**: PCA-based, KNN-based, and frequency-based ancestry inference
- **Ancestry-Adjusted PRS**: Automatic ancestry inference for accurate polygenic risk calculations
- **Confidence Scoring**: Validation metrics and confidence scores for ancestry predictions

### 📊 Linkage Disequilibrium Analysis
- **LD Heatmap Visualization**: Interactive heatmaps showing genetic variant correlations
- **Population-Specific LD**: Ancestry-adjusted linkage disequilibrium calculations

### 🔬 Functional Impact Analysis
- **SNP Effect Prediction**: Comprehensive analysis of genetic variant functional consequences
- **Mutation Classification**: Automated categorization of missense, synonymous, and regulatory variants
- **Drug Metabolism Insights**: Enhanced pharmacogenomic predictions

### 📈 PRS Explainability
- **Transparent Risk Scoring**: Detailed breakdown of SNP contributions to polygenic risk
- **Model Validation**: Comprehensive validation metrics and coverage analysis
- **Educational Insights**: Clear explanations of PRS methodology and limitations

### 💊 Enhanced Clinical Tools
- **Drug-Drug-Gene Interactions**: Comprehensive interaction checking considering both drug-drug and drug-gene (PGx) factors
- **Family Analysis**: IBD/IBS analysis for determining genetic relatedness
- **VCF Support**: Native support for VCF (Variant Call Format) files for clinical-grade data analysis

## Installation

1. Clone this repository:
    ```bash
    git clone <repository-url>
    cd genetics
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. (Optional) For enhanced ancestry inference performance, download pre-trained models:
    ```bash
    # Models are included in the data/ directory
    # ancestry_knn_model.joblib, ancestry_pca_model.joblib, ancestry_snps.npy
    ```

4. Run the application:
    ```bash
    streamlit run src/app.py
    ```

### Enhanced Feature Requirements

The following dependencies are required for the new features:

- **Polars** (>=0.19.0): High-performance data processing
- **scikit-learn** (>=1.3.0): Machine learning for ancestry inference
- **statsmodels** (>=0.14.0): Statistical analysis for LD calculations

All requirements are included in `requirements.txt` and will be installed automatically.

## Usage

1. Launch the application using the command above
2. Upload your DNA data file in the sidebar (supported formats: .txt, .csv, .tsv)
3. Select the desired analysis module from the navigation menu
4. Explore your personalized genomic insights

### New Feature Usage Examples

#### Ancestry Inference
```python
from src.ancestry_inference import infer_ancestry_from_snps

# Infer ancestry from SNP data
result = infer_ancestry_from_snps(your_snp_dataframe)
print(f"Predicted ancestry: {result['predicted_ancestry']}")
print(f"Confidence: {result['confidence']:.2f}")
```

#### Functional Impact Analysis
```python
from src.bioinformatics_utils import predict_functional_impact

# Analyze SNP functional impact
impact = predict_functional_impact("rs1801133", "CT", "MTHFR")
print(f"Predicted impact: {impact['predicted_impact']}")
```

#### PRS with Explainability
```python
from src.genomewide_prs import GenomeWidePRS

calculator = GenomeWidePRS()
result = calculator.calculate_simple_prs(snp_data, model)
print(f"PRS Score: {result['prs_score']}")
print(f"Percentile: {result['percentile']}")
print(f"SNPs used: {result['snps_used']}/{result['total_snps']}")
```

#### LD Heatmap Analysis
Access through the Advanced Analytics module in the Streamlit interface to visualize linkage disequilibrium patterns between genetic variants.

## Medical Disclaimer

**IMPORTANT:** This application is for informational and educational purposes only. It is not a medical device and should not be used for medical diagnosis or treatment decisions. The information provided is not intended to be a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. Never disregard professional medical advice or delay in seeking it because of something you have read here.

## Data Privacy

This application processes genetic data locally and does not store or transmit personal genetic information to external servers. All analysis is performed client-side for maximum privacy protection.

## Development Plans

### Phase 1: Enhanced User Experience (Q1 2024)
- [ ] Add support for additional DNA file formats (FamilyTreeDNA, Nebula Genomics)
- [ ] Implement user authentication and secure session management
- [ ] Enhance UI/UX with modern design patterns and responsive layout
- [ ] Add export functionality for analysis reports (PDF, JSON, CSV formats)

### Phase 2: Advanced Analytics (Q2-Q3 2024)
- [ ] Integrate with external genetic databases (GWAS Catalog, OMIM, Ensembl)
- [ ] Develop machine learning models for improved risk prediction accuracy
- [ ] Implement real-time data validation and quality checks
- [ ] Add comparative analysis features (population vs individual)

### Phase 3: Ecosystem Expansion (Q4 2024 - Q1 2025)
- [ ] Develop REST API endpoints for third-party integrations
- [ ] Create mobile application (React Native for iOS/Android)
- [ ] Implement collaboration features for sharing results with healthcare providers
- [ ] Add support for longitudinal genetic data tracking

### Phase 4: AI and Automation (2025)
- [x] Integrate advanced AI models for ancestry inference (PCA/KNN-based)
- [x] Implement automated report generation with natural language summaries
- [x] Add predictive modeling for disease prevention strategies (PRS explainability)
- [ ] Develop integration with wearable devices and health tracking platforms

### Phase 5: Research and Education (2025-2026)
- [x] Partner with research institutions for novel genetic insights (functional impact analysis)
- [x] Develop educational modules and interactive tutorials (LD heatmaps, PRS transparency)
- [ ] Implement research data contribution features (with consent)
- [ ] Create API for academic and research collaborations

### Completed Enhancements (v2.2.0)
- [x] Polars migration for high-performance data processing
- [x] Advanced ancestry inference with confidence scoring
- [x] Linkage disequilibrium heatmap visualization
- [x] Functional impact analysis for SNPs
- [x] PRS explainability and model validation
- [x] Enhanced bioinformatics utilities

## Folder Structure

The project is organized into the following directories:

```
genetics/
├── src/                          # Source code directory
│   ├── app.py                    # Main Streamlit application
│   ├── utils.py                  # Utility functions (Polars-enabled)
│   ├── render_*.py               # Module renderers
│   ├── bioinformatics_utils.py   # Bioinformatics helpers with functional impact
│   ├── ancestry_inference.py     # Advanced ancestry inference (PCA/KNN)
│   ├── genomewide_prs.py         # Genome-wide PRS with explainability
│   ├── api_functions.py          # API integrations
│   ├── pdf_generator/            # PDF generation module
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── sections.py
│   │   ├── utils.py
│   │   └── visualizations.py
│   └── ...                       # Other source files
├── tests/                        # Test files directory
│   ├── test_*.py                 # Unit and integration tests
│   ├── test_polars_migration.py  # Polars performance tests
│   ├── test_ancestry_inference.py # Ancestry inference tests
│   ├── test_ld_heatmaps.py       # LD visualization tests
│   ├── test_functional_impact.py # Functional impact tests
│   └── test_prs_explainability.py # PRS transparency tests
├── data/                         # Datasets and data files
│   ├── datasets/                 # Genetic datasets
│   │   ├── gene_annotations.tsv
│   │   ├── snp_annotations.tsv
│   │   └── population_frequencies.tsv
│   ├── ancestry_knn_model.joblib # KNN ancestry model
│   ├── ancestry_pca_model.joblib # PCA ancestry model
│   ├── ancestry_snps.npy         # Ancestry-informative SNPs
│   ├── clinvar.vcf.gz            # ClinVar data
│   ├── cache/                    # Cached data
│   └── ...                       # Other data files
├── docs/                         # Documentation
│   ├── README.md                 # This file
│   ├── context/                  # Additional context files
│   └── ...                       # Other docs
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
└── README.md                     # Root README
```

## Dependencies

Key dependencies include:
- Streamlit: Web application framework
- **Polars** (>=0.19.0): High-performance data processing
- Pandas: Data manipulation and analysis (secondary)
- NumPy: Numerical computing
- **scikit-learn** (>=1.3.0): Machine learning for ancestry inference
- Plotly: Interactive visualizations and LD heatmaps
- SciPy: Scientific computing
- **statsmodels** (>=0.14.0): Statistical analysis for LD calculations
- Biopython: Bioinformatics tools and functional impact analysis

## Contributing

We welcome contributions from the community! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure all contributions include appropriate tests and documentation.

## Testing

Run the test suite:
```bash
python -m pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this tool in your research or publications, please cite:

```
Comprehensive Genomic Health Dashboard
[Year]. Available at: [repository-url]
```

## Support

For questions, issues, or contributions, please:
- Open an issue on GitHub
- Contact the development team
- Check the documentation in the `docs/` directory (planned for future release)

## Acknowledgments

- Built with Streamlit framework
- Utilizes public genetic databases (Ensembl, dbSNP, ClinVar, 1000 Genomes)
- Inspired by the growing field of personal genomics and precision medicine