import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
from .logging_utils import get_logger

logger = get_logger(__name__)

class FamilyAnalyzer:
    def __init__(self, df1: pd.DataFrame, df2: pd.DataFrame, label1="Person 1", label2="Person 2"):
        self.df1 = df1
        self.df2 = df2
        self.label1 = label1
        self.label2 = label2
        
        # Find common SNPs
        self.common_snps = df1.index.intersection(df2.index)
        logger.info(f"Found {len(self.common_snps)} common SNPs between {label1} and {label2}")

    def calculate_identity_by_state(self) -> float:
        """
        Calculates the percentage of shared alleles (Identity by State - IBS).
        Simplified calculation:
        - Match (AA vs AA): 1.0
        - Partial (AA vs AB): 0.5
        - Mismatch (AA vs BB): 0.0
        """
        if len(self.common_snps) == 0:
            return 0.0
            
        score = 0.0
        count = 0
        
        # Iterate over a sample of SNPs for performance if needed, but for <1M SNPs it's fast enough
        # Vectorized approach is better
        
        g1 = self.df1.loc[self.common_snps, "genotype"].values
        g2 = self.df2.loc[self.common_snps, "genotype"].values
        
        # Ensure they are strings
        g1 = g1.astype(str)
        g2 = g2.astype(str)
        
        # Filter valid genotypes (length 2)
        valid_mask = np.array([len(s) == 2 for s in g1]) & np.array([len(s) == 2 for s in g2])
        g1 = g1[valid_mask]
        g2 = g2[valid_mask]
        
        if len(g1) == 0:
            return 0.0
            
        # Split alleles
        # g1_a1 = g1[:, 0] # This doesn't work on numpy strings directly like this easily without view
        # List comprehension is safer for mixed types
        
        matches = 0
        total_alleles = len(g1) * 2
        
        for i in range(len(g1)):
            gt1 = g1[i]
            gt2 = g2[i]
            
            # Count shared alleles
            # e.g. AG vs AG -> 2 shared
            # AG vs AA -> 1 shared (A)
            # AA vs GG -> 0 shared
            
            # Convert to lists to handle counting
            l1 = list(gt1)
            l2 = list(gt2)
            
            shared = 0
            for allele in l1:
                if allele in l2:
                    shared += 1
                    l2.remove(allele) # Remove to avoid double counting if duplicate alleles
            
            matches += shared
            
        ibs_score = matches / total_alleles
        return ibs_score

    def predict_relationship(self, ibs_score: float) -> str:
        """
        Predicts relationship based on IBS score.
        Note: This is a rough approximation. IBD (Identity by Descent) is better but requires phasing.
        
        Parent-Child: ~50% shared alleles (IBS is higher because of population frequency, usually >70% IBS for close relatives)
        Siblings: ~50% shared alleles
        Identical Twins: 100%
        Unrelated: Depends on population, but lower.
        
        Refining based on standard IBS thresholds (approximate):
        - > 0.98: Identical Twins / Duplicate
        - 0.70 - 0.90: Parent-Child / Full Sibling
        - 0.60 - 0.70: 2nd Degree (Grandparent, Half-sibling)
        - < 0.60: Distant / Unrelated
        """
        if ibs_score > 0.98:
            return "Identical Twins / Same Person"
        elif ibs_score >= 0.70: # Tuned threshold
            return "Parent-Child or Full Sibling"
        elif ibs_score > 0.65:
            return "2nd Degree Relative (e.g., Grandparent, Half-Sibling)"
        elif ibs_score > 0.55:
            return "3rd Degree Relative (e.g., Cousin)"
        else:
            return "Unrelated"

    def analyze_mendelian_errors(self) -> Dict:
        """
        Checks for Mendelian inconsistencies assuming Parent-Child relationship.
        Returns stats.
        """
        # Only valid if we assume one is parent and one is child.
        # Error: Parent AA, Child BB (impossible without mutation)
        # Error: Parent AA, Child AB (Possible if other parent is B)
        # Error: Parent AA, Child BC (Impossible)
        
        errors = 0
        comparisons = 0
        
        # Vectorized or loop
        # Loop for simplicity and clarity
        
        g1 = self.df1.loc[self.common_snps, "genotype"].astype(str).values # Parent
        g2 = self.df2.loc[self.common_snps, "genotype"].astype(str).values # Child
        
        valid_mask = np.array([len(s) == 2 for s in g1]) & np.array([len(s) == 2 for s in g2])
        g1 = g1[valid_mask]
        g2 = g2[valid_mask]
        
        for i in range(len(g1)):
            p = g1[i] # Parent
            c = g2[i] # Child
            
            # Parent alleles
            p_alleles = set(p)
            
            # Child must inherit at least one allele from Parent
            # So intersection of alleles must be non-empty
            
            c_alleles = set(c)
            
            if not p_alleles.intersection(c_alleles):
                errors += 1
            
            comparisons += 1
            
        error_rate = errors / comparisons if comparisons > 0 else 0
        
        return {
            "total_comparisons": comparisons,
            "mendelian_errors": errors,
            "error_rate": error_rate,
            "is_parent_child": error_rate < 0.02 # Threshold for genotyping error
        }
