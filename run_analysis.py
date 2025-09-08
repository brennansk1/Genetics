import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
# import vcf  # PyVCF library (disabled due to installation issues)
from pyliftover import LiftOver  # pyliftover library
from Bio import Entrez  # Biopython library
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os
import io
import requests # Added for PharmGKB integration
from vcf_converter import convert_vcf_gz_to_tsv


# --- ClinVar Pathogenic Variant Screener ---
def analyze_clinvar_variants(df, clinvar_tsv_path):
    print("\n--- ClinVar Pathogenic Variant Screener ---")
    try:
        clinvar_df = pd.read_csv(clinvar_tsv_path, sep='\t', dtype={'rsid': str})
        # Merge with user's data
        merged_df = df.reset_index().merge(clinvar_df, on='rsid')
        if not merged_df.empty:
            print("Pathogenic or Likely Pathogenic variants found in your data:")
            print(merged_df[['rsid', 'chromosome', 'position', 'genotype', 'CLNSIG']])
            return merged_df
        else:
            print("No pathogenic or likely pathogenic variants from the ClinVar file were found in your data.")
            return pd.DataFrame()
    except FileNotFoundError:
        print(f"ClinVar TSV file not found at {clinvar_tsv_path}. Skipping this analysis.")
        return pd.DataFrame()


# --- Recessive Carrier Status (Example) ---
def analyze_recessive_carrier_status(df):
    print("\n--- Recessive Carrier Status ---")
    recessive_snps = {
        'rs113993960': {'gene': 'CFTR', 'condition': 'Cystic Fibrosis', 'risk_allele': 'T', 'interp': {'CT': 'Carrier', 'TT': 'Affected'}},
        'rs334': {'gene': 'HBB', 'condition': 'Sickle Cell Anemia', 'risk_allele': 'A', 'interp': {'GA': 'Carrier', 'AA': 'Affected'}}
    }
    results = []
    for rsid, info in recessive_snps.items():
        genotype, _ = get_genotype_info(df, rsid)
        status = 'Not a carrier (or not tested)'
        if genotype != 'Not in data':
            sorted_genotype = "".join(sorted(genotype))
            if sorted_genotype in info['interp']:
                status = info['interp'][sorted_genotype]
        results.append({'rsID': rsid, 'Gene': info['gene'], 'Condition': info['condition'], 'Genotype': genotype, 'Status': status})
    carrier_df = pd.DataFrame(results).set_index('rsID')
    print(carrier_df)
    return carrier_df

# --- Protective Variant Highlights (Example) ---
def analyze_protective_variants(df):
    print("\n--- Protective Variant Highlights ---")
    protective_snps = {
        'rs671': {'gene': 'ALDH2', 'trait': 'Alcohol Flush Protection', 'protective_allele': 'A', 'interp': {'GA': 'Reduced Alcohol Tolerance', 'AA': 'Strongly Reduced Alcohol Tolerance'}},
        'rs1229984': {'gene': 'ADH1B', 'trait': 'Alcoholism Protection', 'protective_allele': 'A', 'interp': {'GA': 'Reduced Alcoholism Risk', 'AA': 'Strongly Reduced Alcoholism Risk'}}
    }
    results = []
    for rsid, info in protective_snps.items():
        genotype, _ = get_genotype_info(df, rsid)
        status = 'No protective variant detected (or not tested)'
        if genotype != 'Not in data':
            sorted_genotype = "".join(sorted(genotype))
            if sorted_genotype in info['interp']:
                status = info['interp'][sorted_genotype]
        results.append({'rsID': rsid, 'Gene': info['gene'], 'Trait': info['trait'], 'Genotype': genotype, 'Status': status})
    protective_df = pd.DataFrame(results).set_index('rsID')
    print(protective_df)
    return protective_df

def analyze_expanded_carrier_status(df):
    print_header("Expanded Carrier Status Screening")

    ashkenazi_panel = {
        'rs387906309': {'gene': 'HEXA', 'condition': 'Tay-Sachs Disease'},
        'rs28940279': {'gene': 'ASPA', 'condition': 'Canavan Disease'},
        'rs111033171': {'gene': 'IKBKAP', 'condition': 'Familial Dysautonomia'},
        'rs113993962': {'gene': 'BLM', 'condition': 'Bloom Syndrome'},
    }

    northern_european_panel = {
        'rs1800562': {'gene': 'HFE', 'condition': 'Hereditary Hemochromatosis (C282Y)'},
        'rs1799945': {'gene': 'HFE', 'condition': 'Hereditary Hemochromatosis (H63D)'},
    }

    thalassemia_panel = {
        'rs334': {'gene': 'HBB', 'condition': 'Beta-thalassemia (p.Glu7Val)'},
        'rs33930165': {'gene': 'HBB', 'condition': 'Beta-thalassemia (p.Glu7Lys)'},
        'rs33950507': {'gene': 'HBB', 'condition': 'Beta-thalassemia (p.Glu27Lys)'},
        'rs11549407': {'gene': 'HBB', 'condition': 'Beta-thalassemia (p.Gln40Ter)'},
        'rs41464951': {'gene': 'HBA1/HBA2', 'condition': 'Alpha-thalassemia (Hb Constant Spring)'},
        'rs63751269': {'gene': 'HBA2', 'condition': 'Alpha-thalassemia'},
        'rs41397847': {'gene': 'HBA2', 'condition': 'Alpha-thalassemia (Hb Quong Sze)'},
        'rs28928875': {'gene': 'HBA1', 'condition': 'Alpha-thalassemia (Hb Q-Thailand)'},
    }

    mitochondrial_panel = {
        'rs199476118': {'gene': 'MT-ND1', 'condition': 'LHON (m.3460G>A)'},
        'rs199476112': {'gene': 'MT-ND4', 'condition': 'LHON (m.11778G>A)'},
        'rs199476104': {'gene': 'MT-ND6', 'condition': 'LHON (m.14484T>C)'},
        'rs199474657': {'gene': 'MT-TL1', 'condition': 'MELAS (m.3243A>G)'},
    }

    panels = {
        "Ashkenazi Jewish Ancestry Panel": ashkenazi_panel,
        "Northern European Ancestry Panel": northern_european_panel,
        "Thalassemia Panel": thalassemia_panel,
        "Mitochondrial Health Panel": mitochondrial_panel,
    }

    all_results = []
    for panel_name, panel_snps in panels.items():
        print(f"\n--- {panel_name} ---")
        panel_results = []
        for rsid, info in panel_snps.items():
            genotype, _ = get_genotype_info(df, rsid)
            if genotype != 'Not in data':
                result = {'rsID': rsid, 'Gene': info['gene'], 'Condition': info['condition'], 'Genotype': genotype, 'Status': 'Variant Detected'}
                panel_results.append(result)
                all_results.append(result)
        
        if panel_results:
            print(pd.DataFrame(panel_results).set_index('rsID'))
        else:
            print("No variants from this panel were detected in your data.")

    print("\nNote on SMA (Spinal Muscular Atrophy): SMA carrier status is primarily determined by the number of copies of the SMN1 gene. This type of analysis (Copy Number Variation) cannot be reliably performed using data from most consumer DNA tests. For an accurate SMA carrier screening, please consult a healthcare provider about clinical-grade genetic testing.")

    return pd.DataFrame(all_results) if all_results else pd.DataFrame()


# ---
# Genomic Health Dashboard (Advanced Command-Line Version)
# ---

# --- CONFIGURATION ---
# IMPORTANT: Update these paths to point to your local files.
# Your raw DNA file (e.g., from Ancestry, 23andMe)
DNA_FILE_PATH = "AncestryDNA.txt"
# The genome build of your DNA file ('GRCh37' or 'GRCh38')
GENOME_BUILD = "GRCh37"
# The large ClinVar VCF file you downloaded
# CLINVAR_VCF_PATH = "clinvar.vcf\clinvar.vcf"
# The liftover chain file (only needed if your GENOME_BUILD is GRCh38)
LIFTOVER_CHAIN_PATH = "hg38ToHg19.over.chain/hg38ToHg19.over.chain"
# Your email for NCBI API access (required by their usage policy)
NCBI_EMAIL = "brennanskelley@gmail.com"
# --- END OF CONFIGURATION ---


# --- Helper Functions ---
def print_header(title):
    """Prints a formatted header to the console."""
    print("\n" + "="*80)
    print(f"| {title:^76} |")
    print("="*80)

def get_genotype_info(df, rsid, interpretation_map=None):
    """Helper function to get genotype and optional interpretation for a given rsID."""
    try:
        genotype = df.loc[rsid, 'genotype']
        if genotype in ['00', '--']:
            interpretation = 'Not genotyped or no call.'
        else:
            sorted_genotype = "".join(sorted(genotype))
            if interpretation_map:
                interpretation = interpretation_map.get(sorted_genotype, 'Variant not standard.')
            else:
                interpretation = "See analysis for interpretation."
    except KeyError:
        genotype = 'Not in data'
        interpretation = 'This SNP was not tested in your file.'
    return genotype, interpretation

def process_dna_file(file_path, build, liftover_chain_path=None):
    """Reads and processes a raw DNA file, with optional liftover."""
    print(f"Reading DNA file: {file_path}")
    with open(file_path, 'r') as f:
        content = f.read()

    lines = content.split('\n')
    data_start_line = 0
    # This loop is specifically for AncestryDNA format to find the header
    for i, line in enumerate(lines):
        if line.startswith('rsid'):
            data_start_line = i
            break
            
    df = pd.read_csv(io.StringIO('\n'.join(lines[data_start_line:])), sep='\t', header=0, comment='#', dtype={'rsid': str}).dropna()
    
    # AncestryDNA files have 'allele1' and 'allele2' instead of 'genotype'
    # Combine them to create a 'genotype' column
    if 'allele1' in df.columns and 'allele2' in df.columns:
        df['genotype'] = df['allele1'] + df['allele2']
        # Drop the original allele columns if no longer needed
        df.drop(columns=['allele1', 'allele2'], inplace=True)
    else:
        # Fallback if the file format is different and 'genotype' is expected
        df.rename(columns={'rsid': 'rsid', 'chromosome': 'chromosome', 'position': 'position', 'genotype': 'genotype'}, inplace=True)

    df['position'] = pd.to_numeric(df['position'], errors='coerce')
    df.dropna(subset=['position'], inplace=True)
    df['position'] = df['position'].astype(int)
    df.set_index('rsid', inplace=True)
    print(f"Successfully loaded {len(df)} SNPs.")

    if build.upper() == 'GRCH38':
        if not liftover_chain_path or not os.path.exists(liftover_chain_path):
            raise FileNotFoundError("GRCh38 build specified, but a valid liftover chain file was not provided or found.")
        print("GRCh38 build detected. Applying liftover to convert to GRCh37...")
        lo = LiftOver(liftover_chain_path)
        converted_data = []
        for index, row in df.iterrows():
            chrom = 'chr' + str(row['chromosome'])
            pos = int(row['position'])
            new_coords = lo.convert_coordinate(chrom, pos)
            if new_coords:
                converted_data.append({'rsid': index, 'chromosome': str(row['chromosome']), 'position': new_coords[0][1], 'genotype': row['genotype']})
        
        df = pd.DataFrame(converted_data).set_index('rsid')
        print(f"Liftover successful. {len(df)} SNPs converted to GRCh37.")
    
    return df

# --- Analysis Modules ---

def analyze_high_impact_risks(df):
    print_header("Module 1: High-Impact Genetic Health Risks")
    
    # APOE / Alzheimer's Analysis
    rs429358_geno, _ = get_genotype_info(df, 'rs429358')
    rs7412_geno, _ = get_genotype_info(df, 'rs7412')
    
    apoe_status = "Undetermined (required SNPs not in data)"
    if rs429358_geno != 'Not in data' and rs7412_geno != 'Not in data':
        if 'T' in rs429358_geno and 'T' in rs7412_geno and len(set(rs429358_geno)) == 1 and len(set(rs7412_geno)) == 1: apoe_status = "E2/E2 (Lower Risk)"
        elif 'T' in rs429358_geno and 'C' in rs7412_geno: apoe_status = "E2/E3"
        elif 'C' in rs429358_geno and 'T' in rs7412_geno: apoe_status = "E3/E4 (Increased Risk)"
        elif 'C' in rs429358_geno and 'C' in rs7412_geno and len(set(rs429358_geno)) == 1 and len(set(rs7412_geno)) == 1: apoe_status = "E4/E4 (Significantly Increased Risk)"
        elif ('C' in rs429358_geno and 'T' in rs429358_geno) and ('T' in rs7412_geno): apoe_status = "E2/E4 (Increased Risk)"
        else: apoe_status = "E3/E3 (Typical Risk)"

    print("\n--- Neurodegenerative Conditions ---")
    print(f"  APOE Genotype (Alzheimer's Risk): {apoe_status}")
    print(f"    (rs429358: {rs429358_geno}, rs7412: {rs7412_geno})")


    # Curated list of high-impact risks
    high_impact_snps = {
        'Hereditary Cancer Syndromes': {
            'rs80357906': {'gene': 'BRCA1', 'risk': 'Hereditary Cancer Risk (185delAG)'},
            'rs80357713': {'gene': 'BRCA1', 'risk': 'Hereditary Cancer Risk (5382insC)'},
            'rs80359551': {'gene': 'BRCA2', 'risk': 'Hereditary Cancer Risk (6174delT)'},
            'rs63750247': {'gene': 'MSH2', 'risk': 'Lynch Syndrome (Colorectal Cancer Risk)'},
            'rs1447295': {'gene': '8q24 region', 'risk': 'Prostate Cancer'},
            'rs1805007': {'gene': 'MC1R', 'risk': 'Melanoma Skin Cancer (R151C)'},
            'rs1805008': {'gene': 'MC1R', 'risk': 'Melanoma Skin Cancer (R160W)'},
            'rs1042522': {'gene': 'TP53', 'risk': 'Li-Fraumeni Syndrome (Common Polymorphism)'},
            'rs121964876': {'gene': 'CDH1', 'risk': 'Hereditary Diffuse Gastric Cancer'},
            'rs74799832': {'gene': 'RET', 'risk': 'Multiple Endocrine Neoplasia Type 2'},
            'rs104893829': {'gene': 'VHL', 'risk': 'Von Hippel-Lindau Syndrome'},
            'rs749979841': {'gene': 'TSC1', 'risk': 'Tuberous Sclerosis Complex'},
            'rs28934872': {'gene': 'TSC2', 'risk': 'Tuberous Sclerosis Complex'},
        },
        'Cardiovascular Conditions': {
            'rs6025': {'gene': 'F5', 'risk': 'Factor V Leiden (Hereditary Clotting Risk)'},
            'rs1799963': {'gene': 'F2', 'risk': 'Prothrombin G20210A (Hereditary Clotting Risk)'},
            'rs5925': {'gene': 'LDLR', 'risk': 'Familial Hypercholesterolemia'}
        },
        'Autoimmune & Inflammatory Conditions': {
            'rs2066844': {'gene': 'NOD2', 'risk': "Crohn's Disease"},
            'rs2476601': {'gene': 'PTPN22', 'risk': 'Rheumatoid Arthritis & Autoimmunity'},
            'rs2187668': {'gene': 'HLA-DQA1/B1', 'risk': 'Celiac Disease'}
        },
        'Other Major Diseases': {
            'rs34637585': {'gene': 'LRRK2', 'risk': "Parkinson's Disease (G2019S)"},
            'rs76763715': {'gene': 'GBA', 'risk': "Parkinson's Disease (N370S)"},
            'rs1061170': {'gene': 'CFH', 'risk': 'Age-Related Macular Degeneration (AMD)'},
            'rs28929474': {'gene': 'SERPINA1', 'risk': 'Alpha-1 Antitrypsin Deficiency (PiZ allele)'}
        }
    }
    
    all_results = []
    for category, snps in high_impact_snps.items():
        print(f"\n--- {category} ---")
        category_results = []
        for rsid, info in snps.items():
            genotype, _ = get_genotype_info(df, rsid)
            # Simple check for heterozygous risk allele, as most are dominant or co-dominant for risk
            if genotype != 'Not in data' and len(set(list(genotype))) > 1: 
                result = {'rsID': rsid, 'Gene/Locus': info['gene'], 'Associated Risk': info['risk'], 'Genotype': genotype, 'Interpretation': 'Risk variant detected. CONSULT A GENETIC COUNSELOR.'}
                category_results.append(result)
                all_results.append(result)
        
        if category_results:
            print(pd.DataFrame(category_results).set_index('rsID'))
        else:
            print("No common risk variants detected in this category.")
    
    print("\nNote on BRCA for Males: While often associated with breast cancer, BRCA mutations also significantly increase the risk of prostate cancer, pancreatic cancer, and male breast cancer.")

    return pd.DataFrame(all_results) if all_results else pd.DataFrame()


def analyze_pgx_and_wellness(df):
    print_header("Module 2 & 4: Pharmacogenomics and Wellness Traits")
    
    pgx_snps = {
        'rs4244285': {'gene': 'CYP2C19', 'relevance': 'Clopidogrel Metabolism', 'interp': {'GG': 'Normal Metabolizer', 'AG': 'Intermediate', 'AA': 'Poor'}},
        'rs1057910': {'gene': 'CYP2C9*2', 'relevance': 'Warfarin/NSAID Metabolism', 'interp': {'CC': 'Normal', 'CT': 'Intermediate', 'TT': 'Poor'}},
        'rs1799853': {'gene': 'CYP2C9*3', 'relevance': 'Warfarin/NSAID Metabolism', 'interp': {'AA': 'Normal', 'AC': 'Intermediate', 'CC': 'Poor'}},
        'rs4149056': {'gene': 'SLCO1B1', 'relevance': 'Simvastatin Myopathy Risk', 'interp': {'TT': 'Normal risk', 'CT': 'Increased risk', 'CC': 'High risk'}},
        'rs9923231': {'gene': 'VKORC1', 'relevance': 'Warfarin Sensitivity', 'interp': {'GG': 'Normal sensitivity', 'AG': 'Increased', 'AA': 'High'}},
        'rs1800460': {'gene': 'UGT1A1', 'relevance': 'Irinotecan (Chemo) Toxicity', 'interp': {'GG': 'Normal', 'AG': 'Increased risk', 'AA': 'High risk'}},
        'rs3918290': {'gene': 'HLA-B*15:02', 'relevance': 'Carbamazepine SJS Risk', 'interp': {'GG': 'Normal', 'GT': 'Significantly Increased Risk', 'TT': 'Significantly Increased Risk'}}
    }
    
    wellness_snps = {
        'rs762551': {'trait': 'Caffeine Metabolism', 'interp': {'AA': 'Fast', 'AC': 'Slow', 'CC': 'Slow'}},
        'rs4988235': {'trait': 'Lactose Intolerance', 'interp': {'GG': 'Likely Tolerant', 'AG': 'Likely Tolerant', 'AA': 'Likely Intolerant'}},
        'rs1815739': {'trait': 'Muscle Performance (ACTN3)', 'interp': {'CC': 'Power/Sprint Profile', 'CT': 'Mixed Profile', 'TT': 'Endurance Profile'}},
        'rs1801133': {'gene': 'MTHFR C677T', 'trait': 'Folate Processing', 'interp': {'GG': 'Normal', 'AG': 'Reduced', 'AA': 'Significantly Reduced'}},
        'rs174547': {'gene': 'FADS1', 'trait': 'Fatty Acid Processing (Omega-3/6)', 'interp': {'CC': 'Normal conversion', 'CT': 'Reduced', 'TT': 'Reduced'}},
        'rs2282679': {'gene': 'GC', 'trait': 'Vitamin D Levels', 'interp': {'AA': 'Typical levels', 'AG': 'Predisposition to lower levels', 'GG': 'Predisposition to lower levels'}}
    }

    pgx_results, wellness_results = [], []
    for rsid, info in pgx_snps.items():
        genotype, interpretation = get_genotype_info(df, rsid, info['interp'])
        pgx_results.append({'rsID': rsid, 'Gene/Locus': info['gene'], 'Relevance': info['relevance'], 'Genotype': genotype, 'Interpretation': interpretation})
    for rsid, info in wellness_snps.items():
        genotype, interpretation = get_genotype_info(df, rsid, info['interp'])
        trait_key = info.get('trait', info.get('gene'))
        wellness_results.append({'rsID': rsid, 'Trait/Gene': trait_key, 'Genotype': genotype, 'Interpretation': interpretation})

    pgx_df = pd.DataFrame(pgx_results).set_index('rsID')
    wellness_df = pd.DataFrame(wellness_results).set_index('rsID')
    
    print("\n--- Pharmacogenomics (PGx) Summary ---")
    print(pgx_df)
    print("\n--- Wellness & Trait Profile ---")
    print(wellness_df)
    
    return pgx_df, wellness_df

def analyze_prs(df, results_dir):
    print_header("Module 3: Polygenic Risk Score (PRS) Analysis")
    
    def calculate_prs_and_plot(model_data, condition_name):
        prs_model_df = pd.DataFrame(model_data).set_index('rsid')
        
        # Join user's data (df) with the PRS model data
        # This ensures all columns from df (including 'genotype') are kept
        # and only adds 'effect_allele' and 'effect_weight' for matching rsids.
        merged_df = df.join(prs_model_df, how='inner')

        # Check if merged_df is empty after the join
        if merged_df.empty:
            print(f"No overlapping SNPs found for {condition_name} PRS model. Skipping.")
            return

        # Debugging statements (keep for now)
        print(f"DEBUG: merged_df columns for {condition_name}: {merged_df.columns}")
        print(f"DEBUG: merged_df head for {condition_name}:\n{merged_df.head()}")

        # Now 'genotype' should be present in merged_df
        merged_df['allele_count'] = merged_df.apply(lambda row: row['genotype'].upper().count(row['effect_allele']), axis=1)
        merged_df['score_contribution'] = merged_df['allele_count'] * merged_df['effect_weight']
        user_prs = merged_df['score_contribution'].sum()
        
        np.random.seed(hash(condition_name) % (2**32 - 1))
        population_scores = np.random.normal(loc=np.mean(prs_model_df.effect_weight), scale=np.std(prs_model_df.effect_weight)*2.5, size=10000)
        percentile = (np.sum(population_scores < user_prs) / len(population_scores)) * 100

        fig = go.Figure()
        fig.add_trace(go.Histogram(x=population_scores, name='Population', nbinsx=50, marker_color='#636EFA'))
        fig.add_vline(x=user_prs, line_width=3, line_dash="dash", line_color="red", annotation_text=f"Your Score: {user_prs:.3f}", annotation_position="top right")
        fig.update_layout(title_text=f'Polygenic Risk Score for {condition_name}<br>Your score is at the {percentile:.1f}th percentile.')
        
        output_path = os.path.join(results_dir, f"prs_{condition_name.replace(' ', '_')}.html")
        fig.write_html(output_path, auto_open=False)
        print(f"Generated PRS graph for {condition_name}: {output_path}")

    # Models
    cad_model = {'rsid': ['rs10757274', 'rs10757278', 'rs1333049', 'rs2383206'], 'effect_allele': ['G', 'G', 'C', 'A'], 'effect_weight': [0.177, 0.198, 0.126, 0.106]}
    t2d_model = {'rsid': ['rs7903146', 'rs13266634', 'rs7754840', 'rs10811661', 'rs4506565'], 'effect_allele': ['T', 'C', 'C', 'T', 'T'], 'effect_weight': [0.31, 0.14, 0.11, 0.22, 0.12]}
    afib_model = {'rsid': ['rs2200733', 'rs10033464', 'rs6817105'], 'effect_allele': ['T', 'T', 'D'], 'effect_weight': [0.45, 0.30, 0.22]}
    crc_model = {'rsid': ['rs6983267', 'rs4939827', 'rs10795668'], 'effect_allele': ['G', 'C', 'G'], 'effect_weight': [0.15, 0.14, 0.09]}
    prc_model = {'rsid': ['rs1447295', 'rs6983267'], 'effect_allele': ['A', 'G'], 'effect_weight': [0.30, 0.25]}
    stroke_model = {'rsid': ['rs12425791', 'rs11833579', 'rs2200733'], 'effect_allele': ['A', 'A', 'T'], 'effect_weight': [0.18, 0.15, 0.28]}

    
    calculate_prs_and_plot(cad_model, "Coronary Artery Disease")
    print("  > Guidance: Manage blood pressure, cholesterol, maintain a healthy weight, and avoid smoking.")
    calculate_prs_and_plot(t2d_model, "Type 2 Diabetes")
    print("  > Guidance: Maintain a healthy diet, engage in regular physical activity, and manage weight.")
    calculate_prs_and_plot(afib_model, "Atrial Fibrillation")
    print("  > Guidance: Healthy lifestyle, managing blood pressure, and avoiding excessive alcohol are key preventative measures.")
    calculate_prs_and_plot(stroke_model, "Ischemic Stroke")
    print("  > Guidance: Controlling blood pressure and cholesterol are the most critical preventative steps.")
    calculate_prs_and_plot(crc_model, "Colorectal Cancer")
    print("  > Guidance: Adherence to screening guidelines (e.g., colonoscopy) is critical.")
    calculate_prs_and_plot(prc_model, "Prostate Cancer")
    print("  > Guidance: Discuss PSA screening and family history with your doctor.")


def generate_pdf_report(report_data, results_dir):
    print_header("Module 6: Generating PDF Summary Report")
    
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    
    doc = SimpleDocTemplate(os.path.join(results_dir, "Genomic_Health_Report.pdf"))
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("Genomic Health Summary Report", styles['h1']))
    story.append(Spacer(1, 0.2 * inch))

    # Disclaimer
    disclaimer_text = "DISCLAIMER: For informational purposes only. Not a substitute for professional medical advice."
    story.append(Paragraph(disclaimer_text, styles['Italic']))
    story.append(Spacer(1, 0.2 * inch))

    # High-Impact Health Risks
    if 'high_impact' in report_data and not report_data['high_impact'].empty:
        story.append(Paragraph("High-Impact Health Risks", styles['h2']))
        data = [report_data['high_impact'].columns.tolist()] + report_data['high_impact'].values.tolist()
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 0.2 * inch))

    # Pharmacogenomics (PGx)
    if 'pgx' in report_data and not report_data['pgx'].empty:
        story.append(Paragraph("Pharmacogenomics (PGx)", styles['h2']))
        data = [report_data['pgx'].columns.tolist()] + report_data['pgx'].values.tolist()
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 0.2 * inch))

    # Wellness & Nutrition Traits
    if 'wellness' in report_data and not report_data['wellness'].empty:
        story.append(Paragraph("Wellness & Nutrition Traits", styles['h2']))
        data = [report_data['wellness'].columns.tolist()] + report_data['wellness'].values.tolist()
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 0.2 * inch))

    try:
        doc.build(story)
        print(f"Successfully generated PDF report: {os.path.join(results_dir, \"Genomic_Health_Report.pdf\")}")
    except Exception as e:
        print(f"Error generating PDF: {e}")


def main():
    print_header("Genomic Analysis Pipeline Initializing")
    print("This script provides health insights far beyond standard AncestryDNA reports.")
    print("It analyzes clinical risks, medication responses, complex diseases, and wellness traits.")

    # --- Use CONFIG variables ---
    dna_path = DNA_FILE_PATH
    build = GENOME_BUILD
    liftover_path = LIFTOVER_CHAIN_PATH if build.upper() == 'GRCH38' else None
    clinvar_vcf_path = "clinvar.vcf.gz"
    clinvar_tsv_path = "clinvar_pathogenic_variants.tsv"

    # Create results directory
    results_dir = "results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # --- VCF to TSV Conversion ---
    if not os.path.exists(clinvar_tsv_path):
        print(f"'{clinvar_tsv_path}' not found. Converting '{clinvar_vcf_path}' to TSV...")
        try:
            convert_vcf_gz_to_tsv(clinvar_vcf_path, clinvar_tsv_path)
        except FileNotFoundError:
            print(f"ERROR: '{clinvar_vcf_path}' not found. Please download it and place it in the same directory.")
            return
        except Exception as e:
            print(f"An error occurred during VCF conversion: {e}")
            return

    # --- Run Pipeline ---
    try:
        user_df = process_dna_file(dna_path, build, liftover_path)
        
        report_data = {}
        
        high_impact_df = analyze_high_impact_risks(user_df)
        report_data['high_impact'] = high_impact_df

        clinvar_df = analyze_clinvar_variants(user_df, clinvar_tsv_path)
        report_data['clinvar'] = clinvar_df

        carrier_df = analyze_recessive_carrier_status(user_df)
        report_data['carrier_status'] = carrier_df

        protective_df = analyze_protective_variants(user_df)
        report_data['protective_variants'] = protective_df
        
        pgx_df, wellness_df = analyze_pgx_and_wellness(user_df)
        report_data['pgx'], report_data['wellness'] = pgx_df, wellness_df
        
        analyze_prs(user_df, results_dir)
        
        generate_pdf_report(report_data, results_dir)
        
        print_header("Analysis Complete")
        print(f"All reports and graphs have been saved to the '{results_dir}' folder.")

    except FileNotFoundError as e:
        print(f"\nERROR: A required file was not found. Please check your paths in the CONFIG section.\nDetails: {e}")
    except Exception as e:
        print(f"\nAN UNEXPECTED ERROR OCCURRED: {e}")


if __name__ == "__main__":
    main()