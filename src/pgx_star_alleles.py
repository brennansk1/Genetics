"""
Pharmacogenomic Star Allele Calling Module

This module implements comprehensive star allele determination for pharmacogenomic genes,
including haplotype reconstruction, CNV detection, and metabolizer status classification
according to CPIC guidelines.
"""

from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd

from .snp_data import cpic_guidelines, star_allele_definitions

# Star allele definitions with haplotype patterns
STAR_ALLELE_DEFINITIONS = star_allele_definitions

# CPIC dosing guidelines
CPIC_GUIDELINES = cpic_guidelines


class StarAlleleCaller:
    """Main class for star allele calling and metabolizer status determination"""

    def __init__(self):
        self.star_definitions = STAR_ALLELE_DEFINITIONS
        self.cpic_guidelines = CPIC_GUIDELINES

    def call_star_alleles(
        self, gene: str, genotype_data: pd.DataFrame
    ) -> Dict[str, str]:
        """
        Call star alleles for a given gene based on genotype data

        Args:
            gene: Gene name (e.g., 'CYP2C19')
            genotype_data: DataFrame with rsID as index and genotype column

        Returns:
            Dictionary with allele calls and metabolizer status
        """
        try:
            if gene not in self.star_definitions:
                return {"error": f"Gene {gene} not supported for star allele analysis"}

            if genotype_data is None or genotype_data.empty:
                return {"error": "No genotype data provided"}

            alleles = self.star_definitions[gene]
            user_haplotypes = self._extract_haplotypes(genotype_data)

            if not user_haplotypes:
                return {"error": f"No relevant SNPs found for {gene} in genotype data"}

            # Call alleles for each haplotype
            allele1, allele2 = self._determine_alleles(alleles, user_haplotypes)

            # Check for incomplete haplotype data
            haplotype_completeness = self._check_haplotype_completeness(
                alleles, user_haplotypes
            )

            # Determine metabolizer status
            metabolizer_status = self._determine_metabolizer_status(
                allele1, allele2, alleles
            )

            result = {
                "gene": gene,
                "allele1": allele1,
                "allele2": allele2,
                "genotype": f"{allele1}/{allele2}",
                "metabolizer_status": metabolizer_status,
                "function": self._get_function_description(allele1, allele2, alleles),
                "haplotype_completeness": haplotype_completeness,
            }

            if haplotype_completeness < 0.5:
                result["warning"] = (
                    "Incomplete haplotype data - results may be less accurate"
                )

            return result

        except Exception as e:
            return {"error": f"Error in star allele calling for {gene}: {str(e)}"}

    def _extract_haplotypes(self, genotype_data: pd.DataFrame) -> List[str]:
        """Extract haplotype information from genotype data"""
        haplotypes = []
        for rsid in genotype_data.index:
            if rsid in genotype_data.index:
                genotype = genotype_data.loc[rsid, "genotype"]
                if genotype and len(genotype) == 2:
                    # For diploid genotypes
                    if genotype[0] == genotype[1]:
                        # Homozygous - both alleles are the same
                        haplotypes.extend(
                            [f"{rsid}:{genotype[0]}", f"{rsid}:{genotype[0]}"]
                        )
                    else:
                        # Heterozygous - different alleles
                        haplotypes.extend(
                            [f"{rsid}:{genotype[0]}", f"{rsid}:{genotype[1]}"]
                        )
                elif genotype:
                    # Single allele or other format
                    haplotypes.append(f"{rsid}:{genotype}")
        return haplotypes

    def _determine_alleles(
        self, alleles: Dict, user_haplotypes: List[str]
    ) -> Tuple[str, str]:
        """Determine the most likely star alleles based on haplotypes"""
        # Count how many times each allele's haplotypes are satisfied
        allele_counts = defaultdict(int)

        for allele_name, allele_info in alleles.items():
            required_haps = set(allele_info["haplotypes"])
            if not required_haps:  # Reference allele *1
                allele_counts[allele_name] = 1  # Always available as fallback
            else:
                # Check if all required haplotypes are present
                if all(hap in user_haplotypes for hap in required_haps):
                    # Count how many copies of this allele we can assign
                    allele_counts[allele_name] = (
                        user_haplotypes.count(list(required_haps)[0])
                        if required_haps
                        else 1
                    )

        # Get the alleles sorted by how well they match
        sorted_alleles = sorted(allele_counts.items(), key=lambda x: x[1], reverse=True)

        # Assign alleles based on haplotype matching
        assigned_alleles = []
        remaining_haplotypes = user_haplotypes.copy()

        # First pass: assign non-reference alleles
        for allele_name, count in sorted_alleles:
            if allele_name == "*1":
                continue  # Handle reference separately

            allele_haps = set(alleles[allele_name]["haplotypes"])
            if allele_haps:
                # Count how many complete sets of this allele's haplotypes we have
                allele_hap_count = (
                    min(remaining_haplotypes.count(hap) for hap in allele_haps)
                    if allele_haps
                    else 0
                )

                for _ in range(min(allele_hap_count, 2 - len(assigned_alleles))):
                    assigned_alleles.append(allele_name)
                    # Remove one set of matched haplotypes
                    for hap in allele_haps:
                        if hap in remaining_haplotypes:
                            remaining_haplotypes.remove(hap)

        # Fill remaining slots with *1 (reference)
        while len(assigned_alleles) < 2:
            assigned_alleles.append("*1")

        # Sort alleles for consistent output (*1 first, then by allele number)
        def allele_sort_key(allele):
            if allele == "*1":
                return (0, 0)
            else:
                # Extract number from *N format
                try:
                    num = int(allele[1:])  # Remove * and convert to int
                    return (1, num)
                except:
                    return (2, 0)  # Fallback for non-numeric alleles

        sorted_alleles = sorted(assigned_alleles, key=allele_sort_key)

        # For homozygous detection: if we have the same non-reference allele twice
        if (
            len(sorted_alleles) == 2
            and sorted_alleles[0] == sorted_alleles[1]
            and sorted_alleles[0] != "*1"
        ):
            return sorted_alleles[0], sorted_alleles[0]

        return sorted_alleles[0], sorted_alleles[1]

    def _determine_metabolizer_status(
        self, allele1: str, allele2: str, alleles: Dict
    ) -> str:
        """Determine metabolizer status based on allele functions"""
        func1 = alleles.get(allele1, {}).get("function", "Normal")
        func2 = alleles.get(allele2, {}).get("function", "Normal")

        functions = [func1, func2]

        if "No function" in functions:
            if functions.count("No function") == 2:
                return "Poor Metabolizer"
            else:
                return "Intermediate Metabolizer"
        elif "Decreased function" in functions:
            if functions.count("Decreased function") == 2:
                return "Poor Metabolizer"
            else:
                return "Intermediate Metabolizer"
        elif "Increased function" in functions:
            return "Rapid Metabolizer"
        else:
            return "Normal Metabolizer"

    def _get_function_description(
        self, allele1: str, allele2: str, alleles: Dict
    ) -> str:
        """Get combined function description"""
        func1 = alleles.get(allele1, {}).get("function", "Normal")
        func2 = alleles.get(allele2, {}).get("function", "Normal")
        return f"{func1}/{func2}"

    def _check_haplotype_completeness(
        self, alleles: Dict, user_haplotypes: List[str]
    ) -> float:
        """Check completeness of haplotype data for allele calling"""
        all_required_snps = set()
        for allele_info in alleles.values():
            all_required_snps.update(allele_info["haplotypes"])

        if not all_required_snps:
            return 1.0  # Reference allele, no SNPs required

        # Remove 'deletion' from required SNPs as it's not a real SNP
        all_required_snps = {snp for snp in all_required_snps if snp != "deletion"}

        # Extract SNP IDs from user haplotypes
        user_snp_ids = {hap.split(":")[0] for hap in user_haplotypes}

        # Calculate completeness
        found_snps = all_required_snps.intersection(user_snp_ids)
        completeness = (
            len(found_snps) / len(all_required_snps) if all_required_snps else 1.0
        )

        return completeness

    def get_cpic_recommendations(
        self, gene: str, metabolizer_status: str, drug: str = None
    ) -> Dict[str, str]:
        """Get CPIC dosing recommendations"""
        if gene not in self.cpic_guidelines:
            return {"error": f"No CPIC guidelines available for {gene}"}

        gene_guidelines = self.cpic_guidelines[gene]

        if drug and drug in gene_guidelines:
            return {
                drug: gene_guidelines[drug].get(
                    metabolizer_status, "No specific recommendation"
                )
            }
        else:
            # Return all drugs for this gene
            recommendations = {}
            for drug_name, statuses in gene_guidelines.items():
                recommendations[drug_name] = statuses.get(
                    metabolizer_status, "No specific recommendation"
                )
            return recommendations


def detect_cnv(gene: str, genotype_data: pd.DataFrame) -> Optional[str]:
    """
    Detect copy number variations (CNVs) for genes that support them

    Args:
        gene: Gene name
        genotype_data: Genotype data

    Returns:
        CNV status or None if not detected
    """
    cnv_genes = {
        "CYP2D6": ["rs1065852", "rs3892097"],  # Example markers for CNV detection
        "CYP2C19": ["rs4244285", "rs12248560"],
    }

    if gene not in cnv_genes:
        return None

    # Simple CNV detection based on genotype patterns
    # This is a placeholder - real CNV detection requires specialized tools
    markers = cnv_genes[gene]
    marker_data = genotype_data[genotype_data.index.isin(markers)]

    if len(marker_data) < len(markers):
        return None

    # Check for unusual genotype patterns that might indicate CNV
    genotypes = marker_data["genotype"].tolist()

    # If all genotypes are heterozygous, might indicate duplication
    if all(len(gt) > 2 for gt in genotypes if gt):
        return "Possible duplication (*1xN)"
    elif all(len(gt) == 0 for gt in genotypes if gt):
        return "Possible deletion (*5)"

    return None


# Global instance for easy access
star_caller = StarAlleleCaller()
