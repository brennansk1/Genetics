# SNP data access layer
from typing import Dict, List, Optional
import json
from .database import get_db_connection
from .logging_utils import get_logger

logger = get_logger(__name__)

def _fetch_category_data(category: str) -> Dict:
    """Helper to fetch all variants for a category."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all SNPs in category
    cursor.execute('SELECT * FROM snps WHERE category = ?', (category,))
    snps = cursor.fetchall()
    
    results = {}
    for snp in snps:
        rsid = snp['rsid']
        snp_data = dict(snp)
        
        # Get interpretations
        cursor.execute('SELECT * FROM variant_interpretations WHERE rsid = ?', (rsid,))
        interps = cursor.fetchall()
        
        # Reconstruct the dictionary structure expected by renderers
        if category == 'Recessive Carrier':
            snp_data['condition'] = interps[0]['condition'] if interps else 'Unknown'
            snp_data['interp'] = {i['genotype']: i['interpretation'] for i in interps if i['genotype']}
            
        elif category == 'Hereditary Cancer':
            if interps:
                snp_data['risk'] = interps[0]['risk_level']
        
        elif category == 'Cardiovascular':
            if interps:
                snp_data['risk'] = interps[0]['risk_level']

        elif category == 'Neurodegenerative':
             if interps:
                snp_data['risk'] = interps[0]['risk_level']
        
        elif category == 'Mitochondrial':
             if interps:
                snp_data['risk'] = interps[0]['risk_level']

        elif category == 'Protective':
            if interps:
                snp_data['trait'] = interps[0]['trait']
                snp_data['interp'] = {i['genotype']: i['interpretation'] for i in interps if i['genotype']}

        elif category == 'ACMG Secondary Findings':
             if interps:
                snp_data['condition'] = interps[0]['condition']

        results[rsid] = snp_data
        
    conn.close()
    return results

# Accessors for migrated data
def get_recessive_snps(): return _fetch_category_data('Recessive Carrier')
def get_cancer_snps(): return _fetch_category_data('Hereditary Cancer')
def get_cardiovascular_snps(): return _fetch_category_data('Cardiovascular')
def get_neuro_snps(): return _fetch_category_data('Neurodegenerative')
def get_mito_snps(): return _fetch_category_data('Mitochondrial')
def get_protective_snps(): return _fetch_category_data('Protective')
def get_acmg_sf_variants(): return _fetch_category_data('ACMG Secondary Findings')


def get_pgx_snps() -> Dict:
    """Fetch Pharmacogenomics SNPs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM snps WHERE category = 'Pharmacogenomics'")
    snps = cursor.fetchall()
    
    results = {}
    for snp in snps:
        rsid = snp['rsid']
        snp_data = dict(snp)
        
        cursor.execute("SELECT * FROM variant_interpretations WHERE rsid = ?", (rsid,))
        interps = cursor.fetchall()
        
        if interps:
            snp_data['relevance'] = interps[0]['condition'] # Stored in condition field
            snp_data['interp'] = {i['genotype']: i['interpretation'] for i in interps}
            
        results[rsid] = snp_data
        
    conn.close()
    return results

def get_adverse_reaction_snps() -> Dict:
    """Fetch Adverse Reaction SNPs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM snps WHERE category = 'Adverse Reaction'")
    snps = cursor.fetchall()
    
    results = {}
    for snp in snps:
        rsid = snp['rsid']
        snp_data = dict(snp)
        
        cursor.execute("SELECT * FROM variant_interpretations WHERE rsid = ?", (rsid,))
        interps = cursor.fetchall()
        
        if interps:
            snp_data['relevance'] = interps[0]['condition']
            snp_data['interp'] = {i['genotype']: i['interpretation'] for i in interps}
            
        results[rsid] = snp_data
        
    conn.close()
    return results

def get_star_allele_definitions() -> Dict:
    """Fetch Star Allele Definitions."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM star_alleles")
    rows = cursor.fetchall()
    
    results = {}
    for row in rows:
        gene = row['gene']
        if gene not in results:
            results[gene] = {}
            
        results[gene][row['star_allele']] = {
            "haplotypes": json.loads(row['haplotypes']),
            "function": row['function'],
            "description": row['description']
        }
        
    conn.close()
    return results

def get_cpic_guidelines() -> Dict:
    """Fetch CPIC Guidelines."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM cpic_guidelines")
    rows = cursor.fetchall()
    
    results = {}
    for row in rows:
        gene = row['gene']
        drug = row['drug']
        if gene not in results:
            results[gene] = {}
        if drug not in results[gene]:
            results[gene][drug] = {}
            
        results[gene][drug][row['phenotype']] = row['recommendation']
        
    conn.close()
    return results

def get_prs_models() -> Dict:
    """Fetch PRS Models."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM prs_definitions WHERE category != 'Legacy'")
    rows = cursor.fetchall()
    
    results = {}
    for row in rows:
        condition = row['condition']
        if condition not in results:
            results[condition] = {
                "category": row['category'],
                "description": row['description']
            }
            
        if row['model_type'] == 'simple':
            results[condition]['simple_model'] = json.loads(row['model_data'])
        elif row['model_type'] == 'genomewide':
            results[condition]['genomewide_models'] = json.loads(row['model_data'])
            
    conn.close()
    return results

def get_legacy_prs_models() -> Dict:
    """Fetch Legacy PRS Models."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM prs_definitions WHERE category = 'Legacy'")
    rows = cursor.fetchall()
    
    results = {}
    for row in rows:
        results[row['condition']] = json.loads(row['model_data'])
        
    conn.close()
    return results

def get_prs_model_categories() -> List[str]:
    """Get list of unique PRS categories."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM prs_definitions WHERE category != 'Legacy'")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories

def get_prs_models_by_category(category: str) -> Dict:
    """Get PRS models filtered by category."""
    all_models = get_prs_models()
    return {k: v for k, v in all_models.items() if v.get('category') == category}

def get_trait_description(trait: str) -> str:
    """Get description for a specific trait/condition."""
    all_models = get_prs_models()
    if trait in all_models:
        return all_models[trait].get('description', '')
    return ""

def get_genomewide_models(condition: str) -> List[Dict]:
    """Get genome-wide models for a condition."""
    models = get_prs_models()
    if condition in models:
        return models[condition].get("genomewide_models", [])
    return []

def get_simple_model(condition: str) -> Optional[Dict]:
    """Get simple model for a condition."""
    models = get_prs_models()
    if condition in models:
        return models[condition].get("simple_model")
    return None

# --- Non-Migrated Static Data ---

# Ancestry panel SNP data sourced from 1000 Genomes Project and literature
ancestry_panels = {
    "Ashkenazi Jewish": {
        "rs387906309": {"gene": "HEXA", "condition": "Tay-Sachs Disease"},
        "rs28940279": {"gene": "ASPA", "condition": "Canavan Disease"},
        "rs111033171": {"gene": "IKBKAP", "condition": "Familial Dysautonomia"},
        "rs113993962": {"gene": "BLM", "condition": "Bloom Syndrome"},
    },
    "Northern European": {
        "rs1800562": {"gene": "HFE", "condition": "Hereditary Hemochromatosis (C282Y)"},
        "rs1799945": {"gene": "HFE", "condition": "Hereditary Hemochromatosis (H63D)"},
    },
    "Mediterranean/South Asian": {
        "rs334": {"gene": "HBB", "condition": "Beta-thalassemia (p.Glu7Val)"},
        "rs33930165": {"gene": "HBB", "condition": "Beta-thalassemia (p.Glu7Lys)"},
        "rs33950507": {"gene": "HBB", "condition": "Beta-thalassemia (p.Glu27Lys)"},
    },
    "Southeast Asian": {
        "rs4149056": {"gene": "SLCO1B1", "condition": "Statin-induced myopathy risk"},
        "rs671": {"gene": "ALDH2", "condition": "Alcohol intolerance"},
    },
    "African Ancestry": {
        "rs334": {"gene": "HBB", "condition": "Sickle Cell Disease"},
        "rs113993960": {"gene": "CFTR", "condition": "Cystic Fibrosis (less common)"},
    },
}

# Guidance data for interactive tool
guidance_data = {
    "Coronary Artery Disease": {
        "lifestyle": [
            "Adopt a Mediterranean diet rich in fruits, vegetables, and healthy fats",
            "Engage in at least 150 minutes of moderate aerobic activity per week",
            "Maintain a healthy weight (BMI 18.5-24.9)",
            "Quit smoking and limit alcohol intake",
        ],
        "monitoring": [
            "Regular blood pressure checks (at least annually)",
            "Lipid panel screening every 4-6 years (more frequent if high risk)",
            "Blood glucose monitoring if overweight or family history of diabetes",
        ],
        "medical": [
            "Discuss statin therapy with your doctor if LDL cholesterol is elevated",
            "Consider low-dose aspirin if recommended by a cardiologist",
            "Manage comorbidities like hypertension and diabetes aggressively",
        ],
        "screening": [
            "Coronary calcium scan (CAC) may be considered for risk refinement",
            "Stress testing if symptomatic",
        ],
    },
    "Type 2 Diabetes": {
        "lifestyle": [
            "Focus on a low-glycemic index diet with whole grains and fiber",
            "Aim for 5-7% weight loss if overweight",
            "Include resistance training 2-3 times per week",
            "Avoid sugary beverages and processed foods",
        ],
        "monitoring": [
            "Annual HbA1c testing",
            "Regular foot and eye exams if diagnosed",
            "Monitor blood pressure and cholesterol",
        ],
        "medical": [
            "Metformin may be considered for pre-diabetes",
            "Discuss GLP-1 agonists or SGLT2 inhibitors if high risk",
        ],
        "screening": [
            "Screening for diabetes starting at age 35 for overweight adults",
        ],
    },
    "Atrial Fibrillation": {
        "lifestyle": [
            "Limit alcohol consumption (a known trigger)",
            "Manage stress and treat sleep apnea if present",
            "Maintain a healthy weight to reduce burden on the heart",
        ],
        "monitoring": [
            "Monitor pulse for irregularity",
            "Use wearable devices (e.g., Apple Watch) for rhythm monitoring if advised",
        ],
        "medical": [
            "Anticoagulation therapy may be needed based on CHA2DS2-VASc score",
            "Rate or rhythm control medications as prescribed",
        ],
        "screening": [
            "Opportunistic screening for AFib in patients >65 years",
        ],
    },
    "Colorectal Cancer": {
        "lifestyle": [
            "Limit red and processed meat consumption",
            "Increase fiber intake from fruits, vegetables, and grains",
            "Maintain a healthy weight and stay active",
            "Limit alcohol and avoid tobacco",
        ],
        "monitoring": [
            "Monitor for symptoms like rectal bleeding or changes in bowel habits",
        ],
        "medical": [
            "Discuss aspirin chemoprevention with your doctor",
        ],
        "screening": [
            "Colonoscopy starting at age 45 (or earlier if high risk)",
            "Stool-based tests (FIT/Cologuard) as an alternative",
        ],
    },
}
