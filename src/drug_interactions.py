import pandas as pd
from typing import List, Dict, Tuple
from .snp_data import get_pgx_snps
from .logging_utils import get_logger

logger = get_logger(__name__)

# Mock database of Drug-Drug Interactions (DDIs)
# In a real app, this would come from an API like DrugBank or RxNorm
DRUG_DRUG_INTERACTIONS = {
    frozenset(["warfarin", "aspirin"]): {
        "severity": "Major",
        "description": "Increased risk of bleeding.",
        "management": "Monitor INR closely."
    },
    frozenset(["simvastatin", "amiodarone"]): {
        "severity": "Major",
        "description": "Increased risk of myopathy/rhabdomyolysis.",
        "management": "Limit simvastatin dose to 20mg/day."
    },
    frozenset(["clopidogrel", "omeprazole"]): {
        "severity": "Major",
        "description": "Reduced antiplatelet effect of clopidogrel (CYP2C19 inhibition).",
        "management": "Avoid concurrent use; consider pantoprazole."
    },
    frozenset(["lisinopril", "potassium"]): {
        "severity": "Moderate",
        "description": "Risk of hyperkalemia.",
        "management": "Monitor serum potassium."
    }
}

# Drug-Gene Interactions (PGx) mapping
# Maps drug name to relevant gene and RSIDs
DRUG_GENE_MAPPING = {
    "warfarin": {"gene": "CYP2C9", "rsids": ["rs1799853", "rs1057910"], "gene_vk": "VKORC1", "rsids_vk": ["rs9923231"]},
    "clopidogrel": {"gene": "CYP2C19", "rsids": ["rs4244285", "rs12248560"]},
    "simvastatin": {"gene": "SLCO1B1", "rsids": ["rs4149056"]},
    "codeine": {"gene": "CYP2D6", "rsids": ["rs3892097"]},
    "tacrolimus": {"gene": "CYP3A5", "rsids": ["rs776746"]},
}

class InteractionChecker:
    def __init__(self, dna_data: pd.DataFrame):
        self.dna_data = dna_data

    def check_drug_drug_interactions(self, medications: List[str]) -> List[Dict]:
        """
        Checks for interactions between a list of medications.
        """
        interactions = []
        meds_lower = [m.lower() for m in medications]
        
        # Check all pairs
        for i in range(len(meds_lower)):
            for j in range(i + 1, len(meds_lower)):
                pair = frozenset([meds_lower[i], meds_lower[j]])
                if pair in DRUG_DRUG_INTERACTIONS:
                    info = DRUG_DRUG_INTERACTIONS[pair]
                    interactions.append({
                        "drugs": list(pair),
                        "severity": info["severity"],
                        "description": info["description"],
                        "management": info["management"]
                    })
        return interactions

    def check_drug_gene_interactions(self, medications: List[str]) -> List[Dict]:
        """
        Checks for interactions between medications and the user's genetic profile.
        """
        interactions = []
        meds_lower = [m.lower() for m in medications]
        pgx_snps = get_pgx_snps()
        
        for drug in meds_lower:
            if drug in DRUG_GENE_MAPPING:
                mapping = DRUG_GENE_MAPPING[drug]
                gene = mapping["gene"]
                rsids = mapping["rsids"]
                
                # Check genotypes
                found_variants = []
                phenotype = "Normal Metabolizer" # Default
                
                # Simplified logic: Check for specific risk alleles defined in pgx_snps
                # This is a basic implementation. Full star-allele calling is complex.
                
                for rsid in rsids:
                    if rsid in self.dna_data.index:
                        genotype = self.dna_data.loc[rsid, "genotype"]
                        # Look up in pgx_snps
                        if rsid in pgx_snps:
                            interp_map = pgx_snps[rsid]["interp"]
                            # Sort genotype for matching
                            sorted_gt = "".join(sorted(genotype))
                            # Try both sorted and unsorted (some dicts might be specific)
                            # But usually we sort.
                            
                            # Check if we have a match
                            # Note: pgx_snps keys might not be sorted in the static file, 
                            # but usually we assume standard format.
                            # Let's try to match.
                            
                            interpretation = interp_map.get(genotype) or interp_map.get(sorted_gt)
                            
                            if interpretation and "Normal" not in interpretation:
                                found_variants.append({
                                    "rsid": rsid,
                                    "genotype": genotype,
                                    "interpretation": interpretation
                                })
                                # Update phenotype based on worst finding (simplified)
                                phenotype = interpretation

                if found_variants:
                    interactions.append({
                        "drug": drug,
                        "gene": gene,
                        "phenotype": phenotype,
                        "details": found_variants,
                        "recommendation": f"Consult guidelines for {drug} in {phenotype}s."
                    })
                else:
                    # If no variants found (or all normal), still report as Normal/Extensive
                    interactions.append({
                        "drug": drug,
                        "gene": gene,
                        "phenotype": "Normal Metabolizer",
                        "details": [], # No specific risk variants found
                        "recommendation": "Standard dosing guidelines likely apply."
                    })
                    
        return interactions

    def analyze(self, medications: List[str]) -> Dict:
        return {
            "drug_drug": self.check_drug_drug_interactions(medications),
            "drug_gene": self.check_drug_gene_interactions(medications)
        }
