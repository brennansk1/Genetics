"""
Bioinformatics Utilities for SNP Analysis

This module provides advanced bioinformatics functions for SNP analysis
using specialized Python packages like biopython, pysam, pyfaidx, etc.
"""

import os
import warnings
from collections import Counter
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

# Import bioinformatics packages with fallbacks
try:
    from Bio import AlignIO, SeqIO
    from Bio.Seq import Seq
    from Bio.SeqRecord import SeqRecord

    BIO_AVAILABLE = True
except ImportError:
    BIO_AVAILABLE = False
    warnings.warn("BioPython not available. Some features will be limited.")

# Import local data utilities
try:
    from .local_data_utils import get_gene_info_local, get_snp_info_local

    LOCAL_DATA_AVAILABLE = True
except ImportError:
    LOCAL_DATA_AVAILABLE = False
    warnings.warn("Local data utilities not available. Some features will be limited.")

try:
    import pysam

    PYSAM_AVAILABLE = True
except ImportError:
    PYSAM_AVAILABLE = False
    warnings.warn("PySAM not available. VCF processing will be limited.")

try:
    from pyfaidx import Fasta

    PYFAIDX_AVAILABLE = True
except ImportError:
    PYFAIDX_AVAILABLE = False
    warnings.warn("PyFAIDX not available. FASTA file access will be limited.")

try:
    import vcf

    VCF_AVAILABLE = True
except ImportError:
    try:
        import pysam

        VCF_AVAILABLE = True
    except ImportError:
        VCF_AVAILABLE = False
        warnings.warn(
            "VCF parsing libraries not available. VCF processing will be limited."
        )

try:
    import allel

    ALLEL_AVAILABLE = True
except ImportError:
    ALLEL_AVAILABLE = False
    warnings.warn("scikit-allel not available. LD calculations will be limited.")


class SNPAnalyzer:
    """Advanced SNP analysis using bioinformatics tools."""

    def __init__(self, reference_genome: Optional[str] = None):
        """
        Initialize SNP analyzer.

        Args:
            reference_genome: Path to reference genome FASTA file
        """
        self.reference_genome = reference_genome
        self.fasta = None

        if reference_genome and PYFAIDX_AVAILABLE and os.path.exists(reference_genome):
            try:
                self.fasta = Fasta(reference_genome)
            except Exception as e:
                warnings.warn(f"Could not load reference genome: {e}")

    def analyze_genotype_quality(
        self, genotype: str, quality_score: Optional[float] = None
    ) -> Dict[str, Union[str, float]]:
        """
        Analyze genotype quality and characteristics.

        Args:
            genotype: Genotype string (e.g., 'AA', 'AT', 'TT')
            quality_score: Optional quality score

        Returns:
            Dictionary with genotype analysis
        """
        analysis = {
            "genotype": genotype,
            "zygosity": "homozygous" if len(set(genotype)) == 1 else "heterozygous",
            "alleles": list(genotype),
            "allele_count": len(set(genotype)),
        }

        if quality_score is not None:
            analysis["quality_score"] = quality_score
            # PHRED quality score interpretation
            if quality_score >= 30:
                analysis["quality_interpretation"] = "high_confidence"
            elif quality_score >= 20:
                analysis["quality_interpretation"] = "moderate_confidence"
            else:
                analysis["quality_interpretation"] = "low_confidence"

        return analysis

    def calculate_minor_allele_frequency(
        self, genotypes: List[str]
    ) -> Dict[str, float]:
        """
        Calculate minor allele frequency from a list of genotypes.

        Args:
            genotypes: List of genotype strings

        Returns:
            Dictionary with allele frequencies
        """
        all_alleles = []
        for genotype in genotypes:
            if genotype and genotype != "--" and genotype != "II" and genotype != "DD":
                all_alleles.extend(list(genotype))

        if not all_alleles:
            return {"MAF": 0.0, "total_alleles": 0}

        allele_counts = Counter(all_alleles)
        total_alleles = sum(allele_counts.values())

        if total_alleles == 0:
            return {"MAF": 0.0, "total_alleles": 0}

        # Calculate frequencies
        frequencies = {
            allele: count / total_alleles for allele, count in allele_counts.items()
        }

        # Find minor allele frequency
        sorted_freqs = sorted(frequencies.values())
        maf = sorted_freqs[0] if len(sorted_freqs) > 1 else 0.0

        return {
            "MAF": maf,
            "total_alleles": total_alleles,
            "allele_frequencies": frequencies,
        }

    def predict_functional_impact(
        self, rsid: str, genotype: str, gene: str
    ) -> Dict[str, Union[str, float]]:
        """
        Predict functional impact of a SNP based on genotype and gene context.
        Enhanced with biopython sequence analysis for mutation type classification.

        Args:
            rsid: SNP rsID
            genotype: Genotype string
            gene: Associated gene

        Returns:
            Dictionary with functional impact prediction
        """
        impact = {
            "rsid": rsid,
            "genotype": genotype,
            "gene": gene,
            "predicted_impact": "unknown",
            "mutation_type": "unknown",
            "codon_change": None,
            "amino_acid_change": None,
        }

        # Get SNP and gene information from local data
        snp_info = None
        gene_info = None

        if LOCAL_DATA_AVAILABLE:
            snp_info = get_snp_info_local(rsid)
            gene_info = get_gene_info_local(gene)

        # Known functional SNPs (fallback)
        functional_snps = {
            "rs1801133": {"gene": "MTHFR", "impact": "enzyme_activity"},
            "rs4988235": {"gene": "MCM6", "impact": "lactase_persistence"},
            "rs4680": {"gene": "COMT", "impact": "enzyme_activity"},
            "rs3892097": {"gene": "CYP2D6", "impact": "drug_metabolism"},
            "rs4244285": {"gene": "CYP2C19", "impact": "drug_metabolism"},
            "rs1057910": {"gene": "CYP2C9", "impact": "drug_metabolism"},
            "rs1800462": {"gene": "TPMT", "impact": "drug_metabolism"},
            "rs1800460": {"gene": "UGT1A1", "impact": "drug_metabolism"},
        }

        # Determine alleles from genotype
        alleles = list(set(genotype))
        if len(alleles) == 1:
            alt_allele = alleles[0]
        elif len(alleles) == 2:
            # For heterozygous, analyze both alleles
            alt_allele = (
                alleles[1]
                if alleles[0] == snp_info.get("ref_allele", alleles[0])
                else alleles[0]
            )
        else:
            alt_allele = alleles[0]  # fallback

        # Perform sequence-based analysis if we have SNP and gene info
        if snp_info and gene_info and BIO_AVAILABLE and LOCAL_DATA_AVAILABLE:
            try:
                chromosome = snp_info["chromosome"]
                position = snp_info["position"]
                ref_allele = snp_info["ref_allele"]

                # For simplicity, assume CDS spans the entire gene region
                # In reality, you'd need exon/CDS coordinates
                cds_start = gene_info["start"]
                cds_end = gene_info["end"]
                strand = gene_info["strand"]

                # Check if SNP is within CDS
                if cds_start <= position <= cds_end:
                    # Calculate position within CDS
                    if strand == "+":
                        cds_position = position - cds_start
                    else:
                        cds_position = cds_end - position

                    # Get codon position (0-based within codon)
                    codon_start = (cds_position // 3) * 3
                    codon_pos_in_codon = cds_position % 3

                    # For demonstration, create a mock CDS sequence
                    # In practice, you'd load actual CDS sequence from reference genome
                    mock_cds_length = cds_end - cds_start + 1
                    # Create a simple repeating pattern for demo
                    bases = ["A", "T", "G", "C"]
                    mock_cds = "".join(bases[i % 4] for i in range(mock_cds_length))

                    if strand == "-":
                        # Reverse complement for negative strand
                        complement = {"A": "T", "T": "A", "G": "C", "C": "G"}
                        mock_cds = "".join(
                            complement.get(base, base) for base in reversed(mock_cds)
                        )

                    # Extract codon
                    if codon_start + 3 <= len(mock_cds):
                        codon = mock_cds[codon_start : codon_start + 3]
                        ref_aa = str(Seq(codon).translate())

                        # Create mutant codon
                        mutant_codon = list(codon)
                        mutant_codon[codon_pos_in_codon] = alt_allele
                        mutant_codon = "".join(mutant_codon)
                        alt_aa = str(Seq(mutant_codon).translate())

                        impact["codon_change"] = f"{codon}>{mutant_codon}"
                        impact["amino_acid_change"] = f"{ref_aa}>{alt_aa}"

                        # Determine mutation type
                        if ref_aa == alt_aa:
                            impact["mutation_type"] = "silent"
                        elif alt_aa == "*":
                            impact["mutation_type"] = "nonsense"
                        else:
                            impact["mutation_type"] = "missense"

                        # Set predicted impact based on mutation type
                        if impact["mutation_type"] == "nonsense":
                            impact["predicted_impact"] = "loss_of_function"
                        elif impact["mutation_type"] == "missense":
                            impact["predicted_impact"] = "functional_change"
                        elif impact["mutation_type"] == "silent":
                            impact["predicted_impact"] = "synonymous"

            except Exception as e:
                warnings.warn(f"Error in sequence analysis: {e}")

        # Fallback to known functional SNPs if sequence analysis didn't work
        if rsid in functional_snps and impact["predicted_impact"] == "unknown":
            snp_info_known = functional_snps[rsid]
            impact["predicted_impact"] = snp_info_known["impact"]

            # Genotype-specific predictions
            if snp_info_known["impact"] == "enzyme_activity":
                if genotype in ["AA", "TT"]:
                    impact["activity_level"] = "reduced"
                else:
                    impact["activity_level"] = "normal"
            elif snp_info_known["impact"] == "lactase_persistence":
                if genotype == "TT":
                    impact["lactase_status"] = "persistent"
                else:
                    impact["lactase_status"] = "non_persistent"
            elif snp_info_known["impact"] == "drug_metabolism":
                if genotype in ["AA", "TT"]:
                    impact["metabolism_type"] = "poor_metabolizer"
                elif len(set(genotype)) > 1:
                    impact["metabolism_type"] = "intermediate_metabolizer"
                else:
                    impact["metabolism_type"] = "normal_metabolizer"

        # Prioritize known functional SNPs over sequence analysis
        if rsid in functional_snps:
            snp_info_known = functional_snps[rsid]
            impact["predicted_impact"] = snp_info_known["impact"]

            # Genotype-specific predictions
            if snp_info_known["impact"] == "enzyme_activity":
                if genotype in ["AA", "TT"]:
                    impact["activity_level"] = "reduced"
                else:
                    impact["activity_level"] = "normal"
            elif snp_info_known["impact"] == "lactase_persistence":
                if genotype == "TT":
                    impact["lactase_status"] = "persistent"
                else:
                    impact["lactase_status"] = "non_persistent"
            elif snp_info_known["impact"] == "drug_metabolism":
                if genotype in ["AA", "TT"]:
                    impact["metabolism_type"] = "poor_metabolizer"
                elif len(set(genotype)) > 1:
                    impact["metabolism_type"] = "intermediate_metabolizer"
                else:
                    impact["metabolism_type"] = "normal_metabolizer"
        # If still unknown, try to determine from sequence analysis if available
        elif impact["predicted_impact"] == "unknown" and impact["mutation_type"] != "unknown":
            if impact["mutation_type"] == "nonsense":
                impact["predicted_impact"] = "loss_of_function"
            elif impact["mutation_type"] == "missense":
                impact["predicted_impact"] = "functional_change"
            elif impact["mutation_type"] == "silent":
                impact["predicted_impact"] = "synonymous"

        return impact

    def calculate_ld_matrix(
        self, genotype_data: np.ndarray, snp_labels: List[str]
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Calculate linkage disequilibrium matrix using scikit-allel.

        Args:
            genotype_data: Genotype array (n_variants, n_samples, ploidy)
            snp_labels: List of SNP identifiers

        Returns:
            Tuple of (LD matrix, SNP labels)
        """
        if not ALLEL_AVAILABLE:
            raise ImportError("scikit-allel is required for LD calculations")

        # Convert to GenotypeArray
        g = allel.GenotypeArray(genotype_data)

        # Calculate allele counts
        ac = g.count_alleles()

        # Calculate r² matrix
        r_squared = allel.rogers_huff_r_between(g, ac)

        return r_squared, snp_labels

    def calculate_genetic_distance(
        self, pos1: int, pos2: int, chromosome: str
    ) -> float:
        """
        Calculate genetic distance between two positions.

        Args:
            pos1: First position
            pos2: Second position
            chromosome: Chromosome

        Returns:
            Genetic distance in base pairs
        """
        return abs(pos1 - pos2)

    def identify_compound_heterozygotes(
        self, gene_snps: Dict[str, List[str]], genotypes: Dict[str, str]
    ) -> Dict[str, List[str]]:
        """
        Identify compound heterozygous patterns in genes.

        Args:
            gene_snps: Dictionary mapping genes to lists of SNP rsIDs
            genotypes: Dictionary mapping rsIDs to genotypes

        Returns:
            Dictionary with compound heterozygous findings
        """
        compound_het = {}

        for gene, snps in gene_snps.items():
            het_snps = []
            hom_snps = []

            for rsid in snps:
                if rsid in genotypes:
                    genotype = genotypes[rsid]
                    if len(set(genotype)) > 1:  # Heterozygous
                        het_snps.append(rsid)
                    else:  # Homozygous
                        hom_snps.append(rsid)

            if len(het_snps) >= 2:
                compound_het[gene] = het_snps

        return compound_het

    def extract_sequence_context(
        self, chromosome: str, position: int, flank_size: int = 50
    ) -> Optional[str]:
        """
        Extract sequence context around a SNP position.

        Args:
            chromosome: Chromosome
            position: SNP position
            flank_size: Size of flanking sequence to extract

        Returns:
            Sequence context string or None if not available
        """
        if not self.fasta or not PYFAIDX_AVAILABLE:
            return None

        try:
            start = max(1, position - flank_size)
            end = position + flank_size

            seq = self.fasta[chromosome][start - 1 : end].seq
            return str(seq).upper()
        except Exception:
            return None

    def analyze_snp_conservation(
        self, chromosome: str, position: int
    ) -> Dict[str, Union[str, float]]:
        """
        Analyze conservation around a SNP position (placeholder for more advanced analysis).

        Args:
            chromosome: Chromosome
            position: SNP position

        Returns:
            Dictionary with conservation analysis
        """
        conservation = {
            "chromosome": chromosome,
            "position": position,
            "conservation_score": "unknown",
        }

        # Extract sequence context
        context = self.extract_sequence_context(chromosome, position)
        if context:
            conservation["sequence_context"] = context

            # Simple conservation proxy based on GC content
            gc_content = (context.count("G") + context.count("C")) / len(context)
            conservation["gc_content"] = gc_content

            if gc_content > 0.6:
                conservation["conservation_score"] = "high"
            elif gc_content > 0.4:
                conservation["conservation_score"] = "moderate"
            else:
                conservation["conservation_score"] = "low"

        return conservation


# Global analyzer instance
snp_analyzer = SNPAnalyzer()


def analyze_genotype_quality(
    genotype: str, quality_score: Optional[float] = None
) -> Dict[str, Union[str, float]]:
    """Convenience function for genotype quality analysis."""
    return snp_analyzer.analyze_genotype_quality(genotype, quality_score)


def calculate_maf(genotypes: List[str]) -> Dict[str, float]:
    """Convenience function for MAF calculation."""
    return snp_analyzer.calculate_minor_allele_frequency(genotypes)


def predict_functional_impact(
    rsid: str, genotype: str, gene: str
) -> Dict[str, Union[str, float]]:
    """Convenience function for functional impact prediction."""
    return snp_analyzer.predict_functional_impact(rsid, genotype, gene)


def calculate_ld_matrix(
    genotype_data: np.ndarray, snp_labels: List[str]
) -> Tuple[np.ndarray, List[str]]:
    """Convenience function for LD matrix calculation."""
    return snp_analyzer.calculate_ld_matrix(genotype_data, snp_labels)


def identify_compound_heterozygotes(
    gene_snps: Dict[str, List[str]], genotypes: Dict[str, str]
) -> Dict[str, List[str]]:
    """Convenience function for compound heterozygote identification."""
    return snp_analyzer.identify_compound_heterozygotes(gene_snps, genotypes)


def calculate_genetic_distance(pos1: int, pos2: int, chromosome: str) -> float:
    """Convenience function for genetic distance calculation."""
    return snp_analyzer.calculate_genetic_distance(pos1, pos2, chromosome)


def extract_sequence_context(
    chromosome: str, position: int, flank_size: int = 50
) -> Optional[str]:
    """Convenience function for sequence context extraction."""
    return snp_analyzer.extract_sequence_context(chromosome, position, flank_size)


def analyze_ld_patterns(
    snp_list: List[str], genotypes: Dict[str, str]
) -> Dict[str, Union[str, float]]:
    """
    Analyze linkage disequilibrium patterns between SNPs.

    Args:
        snp_list: List of SNP rsIDs
        genotypes: Dictionary mapping rsIDs to genotypes

    Returns:
        Dictionary with LD analysis results
    """
    # Simple LD analysis - calculate pairwise correlations
    ld_results = {
        "snps_analyzed": snp_list,
        "pairwise_ld": {},
        "haplotypes": []
    }

    # Generate possible haplotypes from genotypes
    if len(snp_list) >= 2:
        # For each pair of SNPs
        for i in range(len(snp_list)):
            for j in range(i+1, len(snp_list)):
                snp1 = snp_list[i]
                snp2 = snp_list[j]

                if snp1 in genotypes and snp2 in genotypes:
                    gt1 = genotypes[snp1]
                    gt2 = genotypes[snp2]

                    # Simple haplotype inference (this is a simplification)
                    # In reality, LD analysis would be more complex
                    pair_key = f"{snp1}-{snp2}"
                    ld_results["pairwise_ld"][pair_key] = {
                        "snp1": snp1,
                        "snp2": snp2,
                        "genotype1": gt1,
                        "genotype2": gt2,
                        "ld_measure": "simplified"  # Placeholder for actual LD calculation
                    }

    return ld_results


def analyze_snp_conservation(
    chromosome: str, position: int
) -> Dict[str, Union[str, float]]:
    """Convenience function for SNP conservation analysis."""
    return snp_analyzer.analyze_snp_conservation(chromosome, position)
