"""
Bioinformatics Utilities for SNP Analysis

This module provides advanced bioinformatics functions for SNP analysis
using specialized Python packages like biopython, pysam, pyfaidx, etc.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from collections import Counter
import os
import warnings

# Import bioinformatics packages with fallbacks
try:
    from Bio import SeqIO, AlignIO
    from Bio.Seq import Seq
    from Bio.SeqRecord import SeqRecord
    BIO_AVAILABLE = True
except ImportError:
    BIO_AVAILABLE = False
    warnings.warn("BioPython not available. Some features will be limited.")

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
        warnings.warn("VCF parsing libraries not available. VCF processing will be limited.")

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

    def analyze_genotype_quality(self, genotype: str, quality_score: Optional[float] = None) -> Dict[str, Union[str, float]]:
        """
        Analyze genotype quality and characteristics.

        Args:
            genotype: Genotype string (e.g., 'AA', 'AT', 'TT')
            quality_score: Optional quality score

        Returns:
            Dictionary with genotype analysis
        """
        analysis = {
            'genotype': genotype,
            'zygosity': 'homozygous' if len(set(genotype)) == 1 else 'heterozygous',
            'alleles': list(genotype),
            'allele_count': len(set(genotype))
        }

        if quality_score is not None:
            analysis['quality_score'] = quality_score
            # PHRED quality score interpretation
            if quality_score >= 30:
                analysis['quality_interpretation'] = 'high_confidence'
            elif quality_score >= 20:
                analysis['quality_interpretation'] = 'moderate_confidence'
            else:
                analysis['quality_interpretation'] = 'low_confidence'

        return analysis

    def calculate_minor_allele_frequency(self, genotypes: List[str]) -> Dict[str, float]:
        """
        Calculate minor allele frequency from a list of genotypes.

        Args:
            genotypes: List of genotype strings

        Returns:
            Dictionary with allele frequencies
        """
        all_alleles = []
        for genotype in genotypes:
            if genotype and genotype != '--' and genotype != 'II' and genotype != 'DD':
                all_alleles.extend(list(genotype))

        if not all_alleles:
            return {'MAF': 0.0, 'total_alleles': 0}

        allele_counts = Counter(all_alleles)
        total_alleles = sum(allele_counts.values())

        if total_alleles == 0:
            return {'MAF': 0.0, 'total_alleles': 0}

        # Calculate frequencies
        frequencies = {allele: count / total_alleles for allele, count in allele_counts.items()}

        # Find minor allele frequency
        sorted_freqs = sorted(frequencies.values())
        maf = sorted_freqs[0] if len(sorted_freqs) > 1 else 0.0

        return {
            'MAF': maf,
            'total_alleles': total_alleles,
            'allele_frequencies': frequencies
        }

    def predict_functional_impact(self, rsid: str, genotype: str, gene: str) -> Dict[str, Union[str, float]]:
        """
        Predict functional impact of a SNP based on genotype and gene context.

        Args:
            rsid: SNP rsID
            genotype: Genotype string
            gene: Associated gene

        Returns:
            Dictionary with functional impact prediction
        """
        impact = {
            'rsid': rsid,
            'genotype': genotype,
            'gene': gene,
            'predicted_impact': 'unknown'
        }

        # Known functional SNPs
        functional_snps = {
            'rs1801133': {'gene': 'MTHFR', 'impact': 'enzyme_activity'},
            'rs4988235': {'gene': 'MCM6', 'impact': 'lactase_persistence'},
            'rs4680': {'gene': 'COMT', 'impact': 'enzyme_activity'},
            'rs3892097': {'gene': 'CYP2D6', 'impact': 'drug_metabolism'},
            'rs4244285': {'gene': 'CYP2C19', 'impact': 'drug_metabolism'},
            'rs1057910': {'gene': 'CYP2C9', 'impact': 'drug_metabolism'},
            'rs1800462': {'gene': 'TPMT', 'impact': 'drug_metabolism'},
            'rs1800460': {'gene': 'UGT1A1', 'impact': 'drug_metabolism'}
        }

        if rsid in functional_snps:
            snp_info = functional_snps[rsid]
            impact['predicted_impact'] = snp_info['impact']

            # Genotype-specific predictions
            if snp_info['impact'] == 'enzyme_activity':
                if genotype in ['AA', 'TT']:
                    impact['activity_level'] = 'reduced'
                else:
                    impact['activity_level'] = 'normal'
            elif snp_info['impact'] == 'lactase_persistence':
                if genotype == 'TT':
                    impact['lactase_status'] = 'persistent'
                else:
                    impact['lactase_status'] = 'non_persistent'
            elif snp_info['impact'] == 'drug_metabolism':
                if genotype in ['AA', 'TT']:
                    impact['metabolism_type'] = 'poor_metabolizer'
                elif len(set(genotype)) > 1:
                    impact['metabolism_type'] = 'intermediate_metabolizer'
                else:
                    impact['metabolism_type'] = 'normal_metabolizer'

        return impact

    def analyze_ld_block(self, snp_list: List[str], genotypes: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Analyze linkage disequilibrium patterns (simplified).

        Args:
            snp_list: List of SNP rsIDs
            genotypes: Dictionary mapping rsIDs to genotypes

        Returns:
            Dictionary with LD block information
        """
        ld_blocks = {}
        haplotypes = []

        # Simple haplotype construction
        for rsid in snp_list:
            if rsid in genotypes:
                genotype = genotypes[rsid]
                if len(genotype) == 2:
                    haplotypes.append(genotype)

        if haplotypes:
            # Group similar haplotypes
            haplotype_counts = Counter(haplotypes)
            ld_blocks['haplotypes'] = dict(haplotype_counts)
            ld_blocks['most_common_haplotype'] = haplotype_counts.most_common(1)[0][0]

        return ld_blocks

    def calculate_genetic_distance(self, pos1: int, pos2: int, chromosome: str) -> float:
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

    def identify_compound_heterozygotes(self, gene_snps: Dict[str, List[str]],
                                       genotypes: Dict[str, str]) -> Dict[str, List[str]]:
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

    def extract_sequence_context(self, chromosome: str, position: int,
                               flank_size: int = 50) -> Optional[str]:
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

            seq = self.fasta[chromosome][start-1:end].seq
            return str(seq).upper()
        except Exception:
            return None

    def analyze_snp_conservation(self, chromosome: str, position: int) -> Dict[str, Union[str, float]]:
        """
        Analyze conservation around a SNP position (placeholder for more advanced analysis).

        Args:
            chromosome: Chromosome
            position: SNP position

        Returns:
            Dictionary with conservation analysis
        """
        conservation = {
            'chromosome': chromosome,
            'position': position,
            'conservation_score': 'unknown'
        }

        # Extract sequence context
        context = self.extract_sequence_context(chromosome, position)
        if context:
            conservation['sequence_context'] = context

            # Simple conservation proxy based on GC content
            gc_content = (context.count('G') + context.count('C')) / len(context)
            conservation['gc_content'] = gc_content

            if gc_content > 0.6:
                conservation['conservation_score'] = 'high'
            elif gc_content > 0.4:
                conservation['conservation_score'] = 'moderate'
            else:
                conservation['conservation_score'] = 'low'

        return conservation

# Global analyzer instance
snp_analyzer = SNPAnalyzer()

def analyze_genotype_quality(genotype: str, quality_score: Optional[float] = None) -> Dict[str, Union[str, float]]:
    """Convenience function for genotype quality analysis."""
    return snp_analyzer.analyze_genotype_quality(genotype, quality_score)

def calculate_maf(genotypes: List[str]) -> Dict[str, float]:
    """Convenience function for MAF calculation."""
    return snp_analyzer.calculate_minor_allele_frequency(genotypes)

def predict_functional_impact(rsid: str, genotype: str, gene: str) -> Dict[str, Union[str, float]]:
    """Convenience function for functional impact prediction."""
    return snp_analyzer.predict_functional_impact(rsid, genotype, gene)

def analyze_ld_patterns(snp_list: List[str], genotypes: Dict[str, str]) -> Dict[str, List[str]]:
    """Convenience function for LD analysis."""
    return snp_analyzer.analyze_ld_block(snp_list, genotypes)

def identify_compound_heterozygotes(gene_snps: Dict[str, List[str]], genotypes: Dict[str, str]) -> Dict[str, List[str]]:
    """Convenience function for compound heterozygote identification."""
    return snp_analyzer.identify_compound_heterozygotes(gene_snps, genotypes)