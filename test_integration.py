#!/usr/bin/env python3
"""
Test script to verify integration of local genetic datasets and bioinformatics utilities.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_local_data_integration():
    """Test that local data utilities work correctly."""
    print("Testing local data integration...")

    try:
        from local_data_utils import get_gene_info_local, get_snp_info_local, get_population_frequencies_local

        # Test gene lookup
        gene_info = get_gene_info_local('BRCA1')
        if gene_info:
            print(f"SUCCESS: Gene lookup works: BRCA1 found on chromosome {gene_info['chromosome']}")
        else:
            print("ERROR: Gene lookup failed")
            return False

        # Test SNP lookup
        snp_info = get_snp_info_local('rs1801133')
        if snp_info:
            print(f"SUCCESS: SNP lookup works: rs1801133 in gene {snp_info['gene']}")
        else:
            print("ERROR: SNP lookup failed")
            return False

        # Test population frequencies
        pop_freq = get_population_frequencies_local('rs1801133')
        if pop_freq is not None and not pop_freq.empty:
            print(f"SUCCESS: Population frequencies work: {len(pop_freq)} populations found")
        else:
            print("ERROR: Population frequencies failed")
            return False

        return True

    except Exception as e:
        print(f"ERROR: Error in local data integration: {e}")
        return False

def test_bioinformatics_utilities():
    """Test that bioinformatics utilities work correctly."""
    print("\nTesting bioinformatics utilities...")

    try:
        from bioinformatics_utils import analyze_genotype_quality, predict_functional_impact, calculate_maf

        # Test genotype quality analysis
        quality = analyze_genotype_quality('AA')
        if quality['zygosity'] == 'homozygous':
            print("SUCCESS: Genotype quality analysis works")
        else:
            print("ERROR: Genotype quality analysis failed")
            return False

        # Test functional impact prediction
        impact = predict_functional_impact('rs1801133', 'CT', 'MTHFR')
        if 'predicted_impact' in impact:
            print("SUCCESS: Functional impact prediction works")
        else:
            print("ERROR: Functional impact prediction failed")
            return False

        # Test MAF calculation
        genotypes = ['AA', 'AT', 'TT', 'AT', 'AA']
        maf_result = calculate_maf(genotypes)
        if 'MAF' in maf_result:
            print("SUCCESS: MAF calculation works")
        else:
            print("ERROR: MAF calculation failed")
            return False

        return True

    except Exception as e:
        print(f"ERROR: Error in bioinformatics utilities: {e}")
        return False

def test_data_integrity():
    """Test that datasets contain real, not simulated data."""
    print("\nTesting data integrity...")

    try:
        import pandas as pd

        # Check gene annotations
        gene_df = pd.read_csv('datasets/gene_annotations.tsv', sep='\t')
        brca1_row = gene_df[gene_df['gene_symbol'] == 'BRCA1']
        if not brca1_row.empty:
            brca1_chrom = brca1_row.iloc[0]['chromosome']
            if brca1_chrom == 17:  # BRCA1 should be on chromosome 17
                print("SUCCESS: Gene annotations contain real data (BRCA1 on chr 17)")
            else:
                print(f"ERROR: Gene annotations incorrect: BRCA1 on chr {brca1_chrom}")
                return False
        else:
            print("ERROR: BRCA1 not found in gene annotations")
            return False

        # Check SNP annotations
        snp_df = pd.read_csv('datasets/snp_annotations.tsv', sep='\t')
        mthfr_snp = snp_df[(snp_df['rsid'] == 'rs1801133') & (snp_df['gene'] == 'MTHFR')]
        if not mthfr_snp.empty:
            print("SUCCESS: SNP annotations contain real data (rs1801133 in MTHFR)")
        else:
            print("ERROR: SNP annotations incorrect")
            return False

        # Check population frequencies
        pop_df = pd.read_csv('datasets/population_frequencies.tsv', sep='\t')
        eur_freq = pop_df[(pop_df['rsid'] == 'rs1801133') & (pop_df['population'] == 'EUR')]
        if not eur_freq.empty:
            freq = eur_freq.iloc[0]['frequency']
            if 0.3 < freq < 0.5:  # Realistic frequency range
                print("SUCCESS: Population frequencies contain realistic data")
            else:
                print(f"ERROR: Population frequencies unrealistic: {freq}")
                return False
        else:
            print("ERROR: Population frequencies missing EUR data")
            return False

        return True

    except Exception as e:
        print(f"ERROR: Error in data integrity test: {e}")
        return False

def main():
    """Run all integration tests."""
    print("Genetic Analysis Dashboard - Integration Test")
    print("=" * 50)

    tests = [
        test_local_data_integration,
        test_bioinformatics_utilities,
        test_data_integrity
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("SUCCESS: All integration tests passed! The system is properly integrated.")
        return True
    else:
        print("ERROR: Some tests failed. Please check the integration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)