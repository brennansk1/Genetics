import streamlit as st
import pandas as pd
from io import StringIO
import requests
import time
from functools import wraps

def api_call_with_retry(max_retries=3, delay=1):
    """
    Decorator for API calls with retry logic and error handling.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                        continue
                    else:
                        st.error(f"API call failed after {max_retries} attempts: {str(e)}")
                        return None
                except Exception as e:
                    last_exception = e
                    st.error(f"Unexpected error in API call: {str(e)}")
                    return None
            return None
        return wrapper
    return decorator

def parse_dna_file(uploaded_file, file_format="AncestryDNA"):
    """
    Parses the uploaded DNA file supporting multiple formats.
    """
    string_data = StringIO(uploaded_file.getvalue().decode("utf-8"))

    if file_format == "AncestryDNA":
        # Find the start of the data
        lines = string_data.readlines()
        start_index = 0
        for i, line in enumerate(lines):
            if line.startswith("rsid"):
                start_index = i
                break

        # Read the data into a pandas DataFrame
        df = pd.read_csv(StringIO("".join(lines[start_index:])), sep='\t', dtype={'rsid': str})

        # Combine allele1 and allele2 to create genotype
        if 'allele1' in df.columns and 'allele2' in df.columns:
            df['genotype'] = df['allele1'] + df['allele2']
            df.drop(columns=['allele1', 'allele2'], inplace=True)

    elif file_format == "23andMe":
        # 23andMe format: rsid, chromosome, position, genotype
        df = pd.read_csv(string_data, sep='\t', comment='#', header=None,
                        names=['rsid', 'chromosome', 'position', 'genotype'], dtype={'rsid': str})

        # Filter out invalid genotypes and non-SNP entries
        df = df[df['genotype'].isin(['AA', 'CC', 'GG', 'TT', 'AC', 'AG', 'AT', 'CG', 'CT', 'GT', '--', 'II', 'DD', 'DI', 'ID'])]

    elif file_format == "MyHeritage":
        # MyHeritage format: similar to 23andMe but may have different column names
        df = pd.read_csv(string_data, sep='\t', comment='#', dtype={'RSID': str})
        if 'RSID' in df.columns:
            df.rename(columns={'RSID': 'rsid'}, inplace=True)
        df['genotype'] = df['RESULT']  # MyHeritage uses 'RESULT' for genotype
        df = df[['rsid', 'genotype']]

    elif file_format == "LivingDNA":
        # LivingDNA format: rsid, genotype
        df = pd.read_csv(string_data, sep='\t', dtype={'rsid': str})

    else:
        raise ValueError(f"Unsupported file format: {file_format}")

    # Standardize columns
    required_cols = ['rsid', 'genotype']
    if 'chromosome' in df.columns:
        required_cols.append('chromosome')
    if 'position' in df.columns:
        required_cols.append('position')

    df = df[required_cols]
    df.dropna(subset=['rsid', 'genotype'], inplace=True)

    return df

def analyze_wellness_snps(dna_data):
    """
    Analyzes the user's DNA data for a predefined list of wellness-related SNPs.
    """
    snps_to_analyze = {
        # Nutritional Genetics
        "rs4988235": {"name": "Lactose Tolerance", "gene": "MCM6", "interp": {"CC": "Lactase non-persistent", "CT": "Lactase non-persistent", "TT": "Lactase persistent"}},
        "rs762551": {"name": "Caffeine Metabolism", "gene": "CYP1A2", "interp": {"CC": "Slow metabolizer", "CT": "Intermediate", "TT": "Fast metabolizer"}},
        "rs601338": {"name": "Vitamin B12", "gene": "FUT2", "interp": {"AA": "Normal", "AG": "Reduced", "GG": "Low"}},
        "rs1801133": {"name": "Vitamin B12", "gene": "MTHFR", "interp": {"CC": "Normal", "CT": "Intermediate", "TT": "Reduced"}},
        "rs7041": {"name": "Vitamin D", "gene": "GC", "interp": {"CC": "Normal", "CT": "Intermediate", "TT": "Low"}},
        "rs4588": {"name": "Vitamin D", "gene": "GC", "interp": {"AA": "Normal", "AG": "Intermediate", "GG": "Low"}},
        "rs2282679": {"name": "Vitamin D", "gene": "GC", "interp": {"CC": "Normal", "CT": "Intermediate", "TT": "Low"}},
        "rs10741657": {"name": "Vitamin D", "gene": "CYP2R1", "interp": {"CC": "Normal", "CT": "Intermediate", "TT": "Low"}},
        
        # Fitness Genetics
        "rs1815739": {"name": "Athletic Performance (Power/Sprint vs. Endurance)", "gene": "ACTN3", "interp": {"CC": "Endurance", "CT": "Mixed", "TT": "Power/Sprint"}},
        
        # Holistic Pathway Analysis
        "rs4680": {"name": "Methylation (COMT)", "gene": "COMT", "interp": {"GG": "Low activity", "AG": "Intermediate", "AA": "High activity"}},
        
        # Longevity and Cellular Aging Markers
        "rs7726159": {"name": "Telomere Length (TERC)", "gene": "TERC", "interp": {"CC": "Normal", "CT": "Intermediate", "TT": "Short"}},
        "rs2736100": {"name": "Telomere Length (TERT)", "gene": "TERT", "interp": {"CC": "Normal", "CT": "Intermediate", "TT": "Short"}},
        "rs11191865": {"name": "Telomere Length (OBFC1)", "gene": "OBFC1", "interp": {"CC": "Normal", "CT": "Intermediate", "TT": "Short"}},
        "rs2802292": {"name": "Longevity (FOXO3)", "gene": "FOXO3", "interp": {"AA": "Normal", "AG": "Intermediate", "GG": "Longevity"}},
        "rs429358": {"name": "Longevity (APOE e2)", "gene": "APOE", "interp": {"CC": "Normal", "CT": "Carrier", "TT": "e2/e2"}},
        "rs7412": {"name": "Longevity (APOE e2)", "gene": "APOE", "interp": {"CC": "Normal", "CT": "Carrier", "TT": "e2/e2"}},
        
        # Chronobiology and Sleep Traits
        "rs57875989": {"name": "Chronotype (PER3 VNTR)", "gene": "PER3", "interp": {"--": "Not determined"}},
        "rs1801260": {"name": "Chronotype (CLOCK)", "gene": "CLOCK", "interp": {"CC": "Morning", "CT": "Intermediate", "TT": "Evening"}},
        "rs11063118": {"name": "Chronotype (RGS16)", "gene": "RGS16", "interp": {"CC": "Morning", "CT": "Intermediate", "TT": "Evening"}},
        "rs11252394": {"name": "Insomnia Risk (MEIS1)", "gene": "MEIS1", "interp": {"CC": "Normal", "CT": "Intermediate", "TT": "High risk"}},
        
        # Quirky Trait Report
        "rs713598": {"name": "Bitter Taste Perception", "gene": "TAS2R38", "interp": {"CC": "Taster", "CT": "Taster", "TT": "Non-taster"}},
        "rs1726866": {"name": "Bitter Taste Perception", "gene": "TAS2R38", "interp": {"GG": "Taster", "GA": "Taster", "AA": "Non-taster"}},
        "rs10246939": {"name": "Bitter Taste Perception", "gene": "TAS2R38", "interp": {"CC": "Taster", "CT": "Taster", "TT": "Non-taster"}},
        "rs10427255": {"name": "Photic Sneeze Reflex", "gene": "ZEB2", "interp": {"CC": "No reflex", "CT": "Carrier", "TT": "Reflex"}},
        "rs4481887": {"name": "Asparagus Metabolite Detection", "gene": "OR2M7", "interp": {"AA": "Detector", "AG": "Detector", "GG": "Non-detector"}}
    }

    results = {}

    for rsid, info in snps_to_analyze.items():
        # Check if rsid is in the index (processed data) or as a column (raw data)
        if rsid in dna_data.index:
            genotype = dna_data.loc[rsid, 'genotype']
            results[rsid] = {"name": info["name"], "gene": info["gene"], "genotype": genotype, "interp": info.get("interp", {})}
        elif 'rsid' in dna_data.columns and rsid in dna_data['rsid'].values:
            user_genotype = dna_data[dna_data['rsid'] == rsid]
            genotype = user_genotype.iloc[0]['genotype']
            results[rsid] = {"name": info["name"], "gene": info["gene"], "genotype": genotype, "interp": info.get("interp", {})}
        else:
            results[rsid] = {"name": info["name"], "gene": info["gene"], "genotype": "Not Found", "interp": info.get("interp", {})}
            
    return results