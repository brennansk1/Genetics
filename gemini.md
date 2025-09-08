This document outlines the complete design for the Genomic Health Dashboard program, incorporating all features discussed, including clinical reports, wellness analysis, and advanced data exploration tools.

---

### **Program Design Document: Comprehensive Genomic Health Dashboard**

#### **1. Project Overview**

**1.1. Project Objective**
To develop a standalone application that leverages Python to analyze consumer raw DNA data. The program's goal is to provide users with comprehensive, educational, and engaging health and wellness insights by consolidating data from multiple public-domain genomic databases. This platform will serve as a powerful analytical tool that surpasses the scope of standard reports offered by commercial testing companies.

**1.2. Scope and Limitations**
* **Input Data:** The application will process raw DNA files from AncestryDNA (standard `.txt` format). Future expansion could allow parsing of data from other services like 23andMe.
* **Core Philosophy:** The program operates on three levels of analysis: 1) Actionable Health Insights, 2) Holistic Wellness & Lifestyle, and 3) Advanced Data Exploration.
* **Medical Disclaimer:** This application is **not a medical device**. All outputs are for informational and educational purposes only. Users must consult with a qualified healthcare professional or genetic counselor before making any health decisions based on these results. A prominent disclaimer will be present throughout the application.

**1.3. Target Audience**
* **Primary User:** Health-conscious individuals seeking to understand genetic predispositions for health, nutrition, and fitness.
* **Secondary User:** "Citizen scientists" and genealogists interested in advanced data exploration, trait analysis, and understanding genetic diversity.

---

#### **2. System Architecture and Technology Stack**

**2.1. Core Technology Stack**
* **Application Framework:** **Streamlit** (or **Plotly Dash**). Chosen for its capability to build interactive web applications and dashboards using only Python. It handles all UI components, data interaction, and visualization rendering.
* **Data Manipulation:** **Pandas**. Used for reading the large, tab-delimited SNP input file, filtering by rsID, and structuring data for analysis.
* **Numerical Computation:** **NumPy**. Used for high-speed calculations, particularly for aggregating Polygenic Risk Scores across thousands of variants.
* **Visualization Engine:** **Plotly Express** and **Altair**. Used to generate interactive charts, including bell curves, bar charts, and scatter plots for data exploration.
* **API & Data Integration:** **Requests**. Used for live API calls to external databases to fetch a variant's most current classification or related research.
* **Report Generation:** **ReportLab** (or similar PDF library). Used to generate printable summary reports for users to share with healthcare providers.

**2.2. External Data Sources**
* **Clinical Significance:** **NCBI ClinVar** (for pathogenic/benign variant status).
* **Pharmacogenomics:** **PharmGKB** (for drug-gene interactions and dosing guidelines).
* **Complex Disease Risk:** **PGS Catalog** (for validated Polygenic Risk Score models).
* **Population Frequency:** **gnoAD** and **1000 Genomes Project** (for global genotype frequency comparisons).
* **Research Literature:** **NCBI PubMed** (for linking SNPs to scientific studies).

**2.3. Data Flow Overview**
1.  **Upload:** User uploads their raw DNA file via the Streamlit interface.
2.  **Parsing & Annotation:** The application parses the file with Pandas. A pre-processing step may cross-reference user SNPs against a master database compiled from ClinVar and PharmGKB to flag key variants.
3.  **User Navigation:** User selects an analysis module from the sidebar (e.g., Clinical Risk, Wellness Profile).
4.  **On-Demand Analysis:** Python functions execute to perform the requested analysis (e.g., calculate PRS, query population data).
5.  **Interactive Visualization:** Results are rendered dynamically in the main application window using Plotly charts and data tables.

---

#### **3. Detailed Feature Specification**

This breakdown provides a detailed manifest of specific genes, variants, and conditions for each enhanced module, integrating advanced analytics directly into your original framework.

***

### Module 1: Clinical Risk & Carrier Status (Enhanced Panel)

This module is expanded to include systematic screening based on clinical standards (ACMG) and broader population-specific carrier screening.

**1.1. Pathogenic Variant Screener (Expanded Scope: ACMG Secondary Findings Integration)**
This analysis screens for pathogenic/likely pathogenic variants in clinically significant genes, now prioritized to include the full ACMG SF v3.x list for reporting actionable incidental findings.

* **Hereditary Cancer Syndromes (Expanded beyond BRCA/Lynch):**
    * **Li-Fraumeni Syndrome:** Gene: **TP53**
    * **Hereditary Diffuse Gastric Cancer:** Gene: **CDH1**
    * **Multiple Endocrine Neoplasia Type 2:** Gene: **RET**
    * **Von Hippel-Lindau Syndrome:** Gene: **VHL**
    * **Tuberous Sclerosis Complex:** Genes: **TSC1**, **TSC2**
* **Cardiovascular Conditions (Expanded Panel):**
    * **Hypertrophic Cardiomyopathy (HCM):** Genes: **MYH7**, **MYBPC3**
    * **Dilated Cardiomyopathy (DCM):** Genes: **TTN** (truncating variants), **LMNA**
    * **Arrhythmogenic Right Ventricular Cardiomyopathy (ARVC):** Genes: **PKP2**, **DSP**, **DSG2**
    * **Long QT Syndrome (LQTS):** Genes: **KCNQ1**, **KCNH2**, **SCN5A**
    * **Brugada Syndrome:** Gene: **SCN5A**
    * **Hereditary Aortopathies/Connective Tissue Disorders:** Gene: **FBN1** (Marfan Syndrome), **COL3A1** (Vascular Ehlers-Danlos)
* **Metabolic Disorders:**
    * **Familial Hypercholesterolemia (Expanded):** Genes: **LDLR**, **APOB**, **PCSK9** (gain-of-function variants)

**1.2. High-Impact & Recessive Carrier Status (Expanded Ancestry-Specific Panel)**
This section retains all original targets (e.g., *APOE*, *F5* Leiden) and adds comprehensive ancestry-aware screening.

* **Neurodegenerative Conditions (Original):**
    * **Alzheimer's Disease:** *APOE* variants (rs429358, rs7412) to determine e2/e3/e4 status.
    * **Parkinson's Disease:** *LRRK2* (rs34637585), *GBA* (rs76763715).
* **Hereditary Cancer Syndromes (Original Key Variants):**
    * **BRCA1/BRCA2:** Founder mutations (rs80357906, rs80357713, rs80359551).
    * **Lynch Syndrome:** *MSH2* (rs63750247).
* **Cardiovascular Conditions (Original Key Variants):**
    * **Factor V Leiden:** *F5* (rs6025).
    * **Prothrombin:** *F2* (rs1799963).
* **Expanded Carrier Panel (Ancestry-Specific Additions):**
    * **Ashkenazi Jewish Ancestry Panel:** Tay-Sachs Disease (*HEXA*), Canavan Disease (*ASPA*), Familial Dysautonomia (*IKBKAP*), Bloom Syndrome (*BLM*).
    * **Mediterranean & Southeast Asian Ancestry Panel:** Beta-thalassemia (key *HBB* mutations), Alpha-thalassemia (*HBA1* and *HBA2* deletions and point mutations).
    * **Northern European Ancestry Panel:** Hereditary Hemochromatosis (*HFE* C282Y and H63D variants).
    * **General Population Panel Additions:** Spinal Muscular Atrophy (*SMN1* copy number).
* **Mitochondrial Health Analysis (New Subsection):**
    * **Leber's Hereditary Optic Neuropathy (LHON):** mtDNA variants m.3460G>A, m.11778G>A, m.14484T>C.
    * **Mitochondrial Encephalomyopathy (MELAS):** mtDNA variant m.3243A>G.

---

### Module 2: Pharmacogenomics (PGx) Report (Comprehensive CPIC-Aligned Panel)

This module expands to cover a wider range of drug classes, focusing on CPIC guidelines and including complex variant types like copy number variations (CNVs).

* **Cardiovascular Medications:**
    * **Clopidogrel (Plavix):** Gene: **CYP2C19** (including standard star alleles *2, *3, *17, and CNVs) for metabolizer status.
    * **Statins (Simvastatin):** Gene: **SLCO1B1** (rs4149056) for myopathy risk.
    * **Warfarin:** Genes: **CYP2C9** (star alleles *2, *3) and **VKORC1** (rs9923231) for dosing algorithm input.
* **Psychiatric Medications (New Panel):**
    * **SSRIs/SNRIs/Tricyclics** (e.g., Fluoxetine, Sertraline, Citalopram, Amitriptyline):
        * Gene: **CYP2D6** (including star alleles *3, *4, *5, *6, *10, *17, *41, and CNVs to define poor, intermediate, normal, and ultra-rapid metabolizers).
        * Gene: **CYP2C19** (as above, for drugs like Citalopram and Escitalopram).
* **Pain Management (New Panel):**
    * **Opioids** (Codeine, Tramadol, Hydrocodone): Gene: **CYP2D6** (Ultra-rapid metabolizers risk toxicity; poor metabolizers experience lack of efficacy).
    * **NSAIDs** (Celecoxib, Ibuprofen): Gene: **CYP2C9** (Poor metabolizers have increased risk of adverse effects/GI bleed).
* **Chemotherapy and Immunosuppressants (New Panel):**
    * **Thiopurines** (Azathioprine, Mercaptopurine): Genes: **TPMT** and **NUDT15** (Risk of severe myelosuppression).
    * **Fluoropyrimidines** (5-Fluorouracil, Capecitabine): Gene: **DPYD** (Risk of severe, life-threatening toxicity).
* **Gout and Hypersensitivity Reactions (New Panel):**
    * **Allopurinol:** Allele: **HLA-B\*58:01** (High risk of Stevens-Johnson Syndrome/Toxic Epidermal Necrolysis).
    * **Carbamazepine:** Allele: **HLA-B\*15:02** (for Asian ancestry) and **HLA-A\*31:01** (for European ancestry) for SJS/TEN risk.

---

### Module 3: Polygenic Risk Score (PRS) Dashboard (Advanced Methodology)

This module shifts from a simple SNP list to a **genome-wide calculation methodology**, where risk scores are generated by analyzing thousands of variants. The report visualizes risk as a percentile compared to a reference population.

* **Cardiometabolic Diseases:**
    * Coronary Artery Disease (CAD)
    * Type 2 Diabetes (T2D)
    * Atrial Fibrillation
    * Ischemic Stroke
    * Hypertension
* **Cancer Risks:**
    * Prostate Cancer
    * Breast Cancer
    * Colorectal Cancer
    * Melanoma
* **Autoimmune and Inflammatory Conditions (New PRS Category):**
    * Inflammatory Bowel Disease (Crohn's Disease and Ulcerative Colitis)
    * Rheumatoid Arthritis
    * Lupus (SLE)
    * Multiple Sclerosis
    * Celiac Disease (in addition to single-gene HLA analysis)
* **Mental Health Conditions (New PRS Category):**
    * Major Depressive Disorder (MDD)
    * Bipolar Disorder
    * Schizophrenia
    * ADHD
* **Skeletal and Other Conditions (New PRS Category):**
    * Osteoporosis / Bone Mineral Density
    * Asthma

---

### Module 4: Holistic Wellness & Trait Profile (Expanded Insights)

This module retains foundational wellness traits while adding metrics for longevity and chronobiology.

* **Nutritional Genetics (Original Panel):**
    * **Lactose Intolerance:** *LCT/MCM6* (rs4988235)
    * **Caffeine Metabolism:** *CYP1A2* (rs762551)
    * **Folate Processing:** *MTHFR* (rs1801133 - C677T)
    * **Vitamin B12 Levels:** *FUT2* (rs601338)
    * **Vitamin D Levels:** *GC*, *CYP2R1* (rs7041, rs4588, rs10741657)
    * **Omega-3/6 Processing:** *FADS1* (rs174547)
    * **Alcohol Flush/Tolerance:** *ALDH2* (rs671), *ADH1B* (rs1229984)
* **Fitness Genetics (Original Panel):**
    * **Power vs. Endurance Profile:** *ACTN3* (rs1815739)
* **Longevity and Cellular Aging Markers (New Subsection):**
    * **Biological Age Predisposition:** Imputed telomere length based on SNPs in or near genes like **TERC**, **TERT**, and **OBFC1**.
    * **Longevity-Associated Genotype:** Re-analysis of **APOE** status (e.g., e2 allele association with longevity) and **FOXO3** variants.
* **Chronobiology and Sleep Traits (New Subsection):**
    * **Chronotype (Morning vs. Evening Preference):** Variants in **PER3** (VNTR), **CLOCK**, and **RGS16**.
    * **Genetic Sleep Duration Needs:** Variants associated with natural short sleep (e.g., *DEC2*) or predisposition to longer sleep duration.
    * **Insomnia Risk:** Genetic predisposition variants identified in large-scale sleep studies.
* **Sensory and Quirky Traits (Original Panel):**
    * **Bitter Taste Perception:** *TAS2R38* (rs713598, rs1726866)
    * **Photic Sneeze Reflex:** *ZEB2* region (rs10427255)
    * **Asparagus Metabolite Detection:** *OR2M7* region (rs4481887)

---

##### **Module 5: Advanced Analytics & Exploration Tools**
* **Goal:** To provide powerful tools for "citizen scientists" to explore their data in greater depth.
* **Features:**
    * **5.1. Interactive Chromosome Explorer:** A visual tool displaying a graphical representation of each chromosome. Users can scroll along the chromosome, with genes and notable SNPs from their file highlighted with pop-up annotations.
    * **5.2. Global Population Frequency Viewer:** For selected SNPs, displays a map or chart showing the frequency of the user's genotype in different global populations (e.g., African, European, East Asian) based on gnoAD data.
    * **5.3. Research Portal:** A search tool where users can look up specific genes or SNPs, with results linking directly to recent scientific papers on PubMed.

##### **Module 6: Data Portability and Utility**
* **Goal:** To enable users to take their data outside the application for real-world use.
* **Features:**
    * **6.1. Printable Health Summary Report (PDF):** A "Download Report" button that generates a concise PDF summarizing critical findings. The report will include:
        * User identifying information (optional).
        * A summary of PGx findings for discussion with a pharmacist or doctor.
        * A list of any high-confidence pathogenic variants found in Module 1.
        * The program's medical disclaimer.
