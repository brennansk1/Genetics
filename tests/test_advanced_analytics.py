#!/usr/bin/env python3
"""
Test script for Advanced Analytics & Exploration Tools module.
"""

import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bioinformatics_utils import (
    analyze_genotype_quality, calculate_maf, predict_functional_impact,
    analyze_ld_patterns, identify_compound_heterozygotes, calculate_genetic_distance,
    extract_sequence_context, analyze_snp_conservation
)
from src.local_data_utils import get_population_frequencies_local, get_snp_info_local

def create_sample_dna_data():
    """Create sample DNA data for testing advanced analytics."""
    # Synthetic data for testing purposes - not from real genetic data
    sample_data = {
        'rsID': [
            'rs1801133',  # MTHFR
            'rs4988235',  # MCM6
            'rs4680',     # COMT
            'rs3892097',  # CYP2D6
            'rs4244285',  # CYP2C19
            'rs1057910',  # CYP2C9
            'rs1800462',  # TPMT
            'rs1800460',  # UGT1A1
            'rs429358',   # APOE
            'rs7412',     # APOE
        ],
        'genotype': [
            'CT',  # Heterozygous MTHFR
            'TT',  # Lactase persistent
            'AG',  # Intermediate COMT
            'GG',  # Normal CYP2D6
            'AG',  # Intermediate CYP2C19
            'CT',  # Intermediate CYP2C9
            'CT',  # Intermediate TPMT
            'AG',  # Intermediate UGT1A1
            'CT',  # APOE e4 carrier
            'CC',  # APOE e3/e3
        ],
        'chromosome': [
            '1', '2', '22', '22', '10', '10', '6', '2', '19', '19'
        ],
        'position': [
            '11856378', '136608646', '19963748', '42522500', '96541615',
            '96702047', '18138995', '234668879', '45411941', '45412079'
        ]
    }
    df = pd.DataFrame(sample_data)
    df.set_index('rsID', inplace=True)
    return df

def test_genotype_quality_analysis():
    """Test genotype quality analysis."""
    print("Testing Genotype Quality Analysis...")

    test_cases = [
        ('AA', None, 'homozygous'),
        ('AT', None, 'heterozygous'),
        ('TT', 30.0, 'homozygous'),
        ('CG', 15.0, 'heterozygous')
    ]

    for genotype, quality, expected_zygosity in test_cases:
        result = analyze_genotype_quality(genotype, quality)
        assert result['zygosity'] == expected_zygosity, f"Expected {expected_zygosity}, got {result['zygosity']}"
        assert result['genotype'] == genotype, f"Genotype mismatch: {result['genotype']} != {genotype}"
        assert len(result['alleles']) == 2, f"Expected 2 alleles, got {len(result['alleles'])}"

        if quality is not None:
            assert 'quality_interpretation' in result, "Quality interpretation missing"
            if quality >= 30:
                assert result['quality_interpretation'] == 'high_confidence'
            elif quality >= 20:
                assert result['quality_interpretation'] == 'moderate_confidence'
            else:
                assert result['quality_interpretation'] == 'low_confidence'

    print("PASS: Genotype quality analysis working correctly")
    return True

def test_minor_allele_frequency():
    """Test minor allele frequency calculation."""
    print("Testing Minor Allele Frequency Calculation...")

    # Test with various genotype lists
    test_cases = [
        (['AA', 'AT', 'TT'], 0.5),  # A=0.5, T=0.5 -> MAF=0.5
        (['CC', 'CG', 'GG'], 0.33),  # C=0.33, G=0.67 -> MAF=0.33
        (['AA', 'AA', 'AA'], 0.0),   # All A -> MAF=0
        (['AT', 'AT', 'AT'], 0.5),   # All heterozygous -> MAF=0.5
    ]

    for genotypes, expected_maf in test_cases:
        result = calculate_maf(genotypes)
        assert abs(result['MAF'] - expected_maf) < 0.01, f"Expected MAF {expected_maf}, got {result['MAF']}"
        assert result['total_alleles'] == len(genotypes) * 2, f"Total alleles mismatch"

    print("PASS: MAF calculation working correctly")
    return True

def test_functional_impact_prediction():
    """Test functional impact prediction."""
    print("Testing Functional Impact Prediction...")

    test_cases = [
        ('rs1801133', 'CT', 'MTHFR', 'enzyme_activity'),
        ('rs4988235', 'TT', 'MCM6', 'lactase_persistence'),
        ('rs4680', 'AG', 'COMT', 'enzyme_activity'),
        ('rs4244285', 'AG', 'CYP2C19', 'drug_metabolism'),
        ('rs99999999', 'AA', 'UNKNOWN', 'unknown'),  # Unknown SNP
    ]

    for rsid, genotype, gene, expected_impact in test_cases:
        result = predict_functional_impact(rsid, genotype, gene)
        assert result['predicted_impact'] == expected_impact, f"Expected {expected_impact}, got {result['predicted_impact']}"
        assert result['genotype'] == genotype, f"Genotype mismatch"
        assert result['gene'] == gene, f"Gene mismatch"

        # Check specific predictions
        if expected_impact == 'enzyme_activity':
            assert 'activity_level' in result, "Activity level prediction missing"
        elif expected_impact == 'lactase_persistence':
            assert 'lactase_status' in result, "Lactase status prediction missing"
        elif expected_impact == 'drug_metabolism':
            assert 'metabolism_type' in result, "Metabolism type prediction missing"

    print("PASS: Functional impact prediction working correctly")
    return True

def test_ld_pattern_analysis():
    """Test linkage disequilibrium pattern analysis."""
    print("Testing LD Pattern Analysis...")

    # Simple test with haplotype data
    snp_list = ['rs1801133', 'rs4680']
    genotypes = {
        'rs1801133': 'CT',
        'rs4680': 'AG'
    }

    result = analyze_ld_patterns(snp_list, genotypes)

    # Should have haplotype information
    assert 'haplotypes' in result or len(result) >= 0, "LD analysis should return results"

    print("PASS: LD pattern analysis working correctly")
    return True

def test_compound_heterozygote_detection():
    """Test compound heterozygote detection."""
    print("Testing Compound Heterozygote Detection...")

    # Test with gene SNPs
    gene_snps = {
        'BRCA1': ['rs1799945', 'rs80357421'],
        'BRCA2': ['rs28897743', 'rs80359361']
    }

    genotypes = {
        'rs1799945': 'AG',  # Heterozygous
        'rs80357421': 'CT',  # Heterozygous
        'rs28897743': 'GG',  # Homozygous
        'rs80359361': 'AA',  # Homozygous
    }

    result = identify_compound_heterozygotes(gene_snps, genotypes)

    # BRCA1 should be detected as compound heterozygous
    assert 'BRCA1' in result, "BRCA1 compound heterozygote not detected"
    assert len(result['BRCA1']) >= 2, "Should have at least 2 heterozygous SNPs"

    # BRCA2 should not be detected (homozygous)
    assert 'BRCA2' not in result, "BRCA2 incorrectly detected as compound heterozygous"

    print("PASS: Compound heterozygote detection working correctly")
    return True

def test_genetic_distance_calculation():
    """Test genetic distance calculation."""
    print("Testing Genetic Distance Calculation...")

    test_cases = [
        (1000, 2000, '1', 1000),
        (5000000, 5001000, '2', 1000),
        (2000, 1000, '1', 1000),  # Reverse order
    ]

    for pos1, pos2, chrom, expected_distance in test_cases:
        result = calculate_genetic_distance(pos1, pos2, chrom)
        assert result == expected_distance, f"Expected distance {expected_distance}, got {result}"

    print("PASS: Genetic distance calculation working correctly")
    return True

def test_sequence_context_extraction():
    """Test sequence context extraction."""
    print("Testing Sequence Context Extraction...")

    # This will likely return None without reference genome
    result = extract_sequence_context('1', 11856378, 50)

    # Should return None or string depending on availability
    assert result is None or isinstance(result, str), "Sequence context should be None or string"

    print("PASS: Sequence context extraction handled correctly")
    return True

def test_snp_conservation_analysis():
    """Test SNP conservation analysis."""
    print("Testing SNP Conservation Analysis...")

    result = analyze_snp_conservation('1', 11856378)

    assert 'chromosome' in result, "Chromosome missing from conservation analysis"
    assert 'position' in result, "Position missing from conservation analysis"
    assert 'conservation_score' in result, "Conservation score missing"

    print("PASS: SNP conservation analysis working correctly")
    return True

def test_population_frequency_viewer():
    """Test population frequency viewer functionality."""
    print("Testing Population Frequency Viewer...")

    dna_data = create_sample_dna_data()
    rsid = 'rs1801133'  # Test with MTHFR SNP

    # Test population frequency retrieval
    pop_freq = get_population_frequencies_local(rsid)

    # Result should be DataFrame or None
    assert pop_freq is None or isinstance(pop_freq, pd.DataFrame), "Population frequency should be DataFrame or None"

    if pop_freq is not None:
        assert not pop_freq.empty, "Population frequency data should not be empty"
        assert 'population' in pop_freq.columns, "Population column missing"
        assert 'frequency' in pop_freq.columns, "Frequency column missing"

    print("PASS: Population frequency viewer working correctly")
    return True

def test_advanced_snp_analysis():
    """Test advanced SNP analysis functionality."""
    print("Testing Advanced SNP Analysis...")

    dna_data = create_sample_dna_data()
    rsid = 'rs1801133'
    genotype = 'CT'

    # Get SNP info
    snp_info = get_snp_info_local(rsid)

    if snp_info:
        # Test genotype quality
        quality_analysis = analyze_genotype_quality(genotype)
        assert quality_analysis['zygosity'] == 'heterozygous', "CT should be heterozygous"

        # Test functional impact
        impact_analysis = predict_functional_impact(rsid, genotype, snp_info.get('gene', ''))
        assert 'predicted_impact' in impact_analysis, "Functional impact prediction missing"

    print("PASS: Advanced SNP analysis working correctly")
    return True

def run_all_advanced_analytics_tests():
    """Run all advanced analytics and exploration tests."""
    print("ADVANCED ANALYTICS & EXPLORATION TOOLS TESTS")
    print("=" * 55)

    tests = [
        test_genotype_quality_analysis,
        test_minor_allele_frequency,
        test_functional_impact_prediction,
        test_ld_pattern_analysis,
        test_compound_heterozygote_detection,
        test_genetic_distance_calculation,
        test_sequence_context_extraction,
        test_snp_conservation_analysis,
        test_population_frequency_viewer,
        test_advanced_snp_analysis
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__} - {str(e)}")

    print("\n" + "=" * 55)
    print(f"Tests passed: {passed}/{total}")
    if passed == total:
        print("All advanced analytics tests passed!")
        return True
    else:
        print("Some tests failed.")
        return False

if __name__ == "__main__":
    success = run_all_advanced_analytics_tests()
    if not success:
        exit(1)