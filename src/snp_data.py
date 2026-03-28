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

# --- Migrated Static Data via SQLAlchemy ---
import os
import sys

# Hacky path adjustment if called directly in the old dir
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from backend.src.database_setup import SessionLocal, AncestryPanel, Guidance

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_ancestry_panels() -> Dict:
    """Fetch ancestry panel definitions from SQLite."""
    db = next(get_db())
    panels = db.query(AncestryPanel).all()
    
    results = {}
    for panel in panels:
        if panel.population not in results:
            results[panel.population] = {}
        
        results[panel.population][panel.rsid] = {
            "gene": panel.gene,
            "condition": panel.condition
        }
    return results

def get_guidance_data() -> Dict:
    """Fetch clinical guidance data from SQLite."""
    db = next(get_db())
    guidance_entries = db.query(Guidance).all()

    results = {}
    for guidance in guidance_entries:
        results[guidance.condition] = {
            "lifestyle": guidance.lifestyle,
            "monitoring": guidance.monitoring,
            "medical": guidance.medical,
            "screening": guidance.screening
        }
    return results


# --- Module-level variable aliases for backward compatibility ---
# Callers can import these directly: from .snp_data import ancestry_panels
try:
    ancestry_panels = get_ancestry_panels()
except Exception:
    ancestry_panels = {}

try:
    guidance_data = get_guidance_data()
except Exception:
    guidance_data = {}

try:
    pgx_snps = get_pgx_snps()
except Exception:
    pgx_snps = {}

try:
    prs_models = get_prs_models()
except Exception:
    prs_models = {}
