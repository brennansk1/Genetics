# Genomic Health Dashboard

A full-stack personal genomics platform that analyzes consumer DNA files (AncestryDNA, 23andMe, MyHeritage, VCF) and provides evidence-backed health insights across clinical risk, pharmacogenomics, polygenic risk scores, wellness traits, ancestry, and family DNA comparison.

## Architecture

```
Frontend (Next.js 16)          Backend (FastAPI)          Analysis Core (Python)
  React 19 + TypeScript     -->  REST API + CORS       -->  Genomic Analysis Modules
  Tailwind CSS dark UI           In-memory cache (TTL)      Evidence-based annotation
  Recharts visualizations        File upload (multipart)    Free API integrations
```

- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS, Heroicons, Recharts
- **Backend**: FastAPI, Pydantic, uvicorn, python-multipart
- **Analysis**: pandas, NumPy, scikit-learn, scipy, Polars, ReportLab, pyliftover
- **Database**: SQLite (clinical knowledge: SNPs, CPIC guidelines, PRS models, star alleles)

## Features

### Individual Analysis
- **Clinical Risk Screening** -- ClinVar pathogenic variants, high-impact risk variants, ACMG secondary findings
- **Carrier Screening** -- Ashkenazi Jewish, Northern European, Thalassemia, Mitochondrial panels
- **Pharmacogenomics (PGx)** -- CYP2C19, CYP2D6, CYP3A5, SLCO1B1 and more with CPIC guidelines
- **Polygenic Risk Scores** -- 15 conditions (CAD, T2D, cancer, autoimmune, psychiatric, etc.)
- **Wellness Traits** -- Caffeine metabolism, lactose tolerance, vitamin levels, fitness, sleep, longevity
- **Ancestry Inference** -- PCA/KNN-based population classification

### Family DNA Comparison
- Upload two DNA files and compare father-son, siblings, or any two individuals
- **Identity-by-State (IBS)** scoring with relationship prediction
- **Mendelian error detection** to confirm parent-child relationships
- Side-by-side PRS comparison, shared variant analysis, inherited risk tracking

### Evidence-Based Enrichment (Free APIs, No Signup)
Every variant is annotated with real data from multiple sources:

| API | Data Provided | Signup |
|-----|---------------|--------|
| **MyVariant.info** | ClinVar significance, gnomAD allele frequencies, CADD scores | None |
| **Ensembl VEP** | Functional consequence, SIFT/PolyPhen predictions, impact level | None |
| **Open Targets** | Disease-gene association evidence scores | None |
| **NCBI ClinVar** | Pathogenicity assertions with review star ratings | None |
| **PGS Catalog** | Polygenic risk score models | None |
| **gnomAD** | Population allele frequencies (AFR, AMR, EAS, EUR, SAS) | None |

Key evidence improvements:
- Variants with gnomAD AF > 5% are automatically classified as **benign** regardless of ClinVar assertions (catches false positives like TP53 rs1042522)
- PRS percentiles use **real gnomAD allele frequencies** for population reference distributions instead of simulated data
- Carrier screening distinguishes **true pathogenic carriers** (rare + ClinVar confirmed) from common benign variants

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+

### 1. Install dependencies

```bash
# Python
pip install -r requirements.txt

# Frontend
cd frontend && npm install && cd ..
```

### 2. Initialize the database

```bash
python3 -c "from src.database import init_db, migrate_static_data; init_db(); migrate_static_data()"
```

### 3. Start the application

```bash
# Terminal 1 -- Backend (port 8000)
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Terminal 2 -- Frontend (port 3000)
cd frontend && npm run dev
```

Open http://localhost:3000 to use the dashboard.

### 4. API docs

FastAPI auto-generates interactive API documentation at http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analysis/process-dna` | Upload and analyze a DNA file |
| POST | `/analysis/family-compare` | Compare two DNA files |
| GET | `/analysis/results/{id}` | Full cached results |
| GET | `/clinical/risks/{id}` | Clinical risk variants |
| GET | `/clinical/carrier-status/{id}` | Carrier screening |
| GET | `/clinical/cancer-risk/{id}` | Cancer-specific risks |
| GET | `/pgx/report/{id}` | Pharmacogenomics report |
| GET | `/prs/scores/{id}` | Polygenic risk scores |
| GET | `/wellness/traits/{id}` | Wellness traits |
| GET | `/wellness/ancestry/{id}` | Ancestry inference |

## Project Structure

```
.
├── backend/                  # FastAPI backend
│   ├── main.py              # App entry point
│   └── src/
│       ├── routers/analysis.py  # All API endpoints
│       ├── models.py            # Pydantic schemas
│       └── analysis_store.py    # In-memory result cache
├── frontend/                 # Next.js frontend
│   └── src/
│       ├── app/             # Pages (home, dashboard, family)
│       ├── components/      # UI components
│       └── lib/api.ts       # Typed API client
├── src/                      # Analysis core
│   ├── run_analysis.py      # Main analysis pipeline
│   ├── variant_evidence.py  # Evidence-based API enrichment
│   ├── family_analysis.py   # IBS/Mendelian family comparison
│   ├── genomewide_prs.py    # Polygenic risk score calculator
│   ├── ancestry_inference.py # PCA/KNN ancestry classification
│   ├── snp_data.py          # Database access layer
│   ├── database.py          # SQLite schema and migrations
│   ├── api_functions.py     # External API integrations
│   └── pdf_generator/       # ReportLab PDF generation
├── data/                     # Reference data and models
│   ├── genetics.db          # SQLite clinical knowledge DB
│   ├── datasets/            # TSV reference datasets
│   └── ancestry_*.joblib    # Trained ML models
├── tests/                    # Test suite
└── family_genomic_cli/       # CLI tool for family analysis
```

## Supported DNA File Formats

- AncestryDNA (tab-separated, allele1/allele2 columns)
- 23andMe (tab-separated, genotype column)
- MyHeritage
- LivingDNA
- VCF (Variant Call Format)

## Privacy

DNA files are **never committed to the repository**. The `.gitignore` excludes all personal genetic data, generated reports, and API credentials. Analysis results are cached in-memory with a 1-hour TTL and are never persisted to disk.

## Disclaimer

This tool is for **educational and research purposes only**. It is not a medical device and should not be used for clinical decision-making. Always consult a qualified healthcare provider or genetic counselor for medical advice. Polygenic risk scores are statistical estimates based on limited SNP models and should not be interpreted as diagnostic.

## License

Private project.
