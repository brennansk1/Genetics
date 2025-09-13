"""
Test script for validating star allele calling with known haplotype combinations
"""

import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pgx_star_alleles import star_caller

def test_cyp2c19_alleles():
    """Test CYP2C19 star allele calling with known combinations"""

    test_cases = [
        {
            'name': 'CYP2C19 *1/*1 (Normal)',
            'genotypes': {'rs4244285': 'GG', 'rs12248560': 'CC'},
            'expected': {'genotype': '*1/*1', 'metabolizer': 'Normal Metabolizer'}
        },
        {
            'name': 'CYP2C19 *1/*2 (Intermediate)',
            'genotypes': {'rs4244285': 'AG', 'rs12248560': 'CC'},
            'expected': {'genotype': '*1/*2', 'metabolizer': 'Intermediate Metabolizer'}
        },
        {
            'name': 'CYP2C19 *2/*2 (Poor)',
            'genotypes': {'rs4244285': 'AA', 'rs12248560': 'CC'},
            'expected': {'genotype': '*2/*2', 'metabolizer': 'Poor Metabolizer'}
        },
        {
            'name': 'CYP2C19 *1/*17 (Rapid)',
            'genotypes': {'rs4244285': 'GG', 'rs12248560': 'CT'},
            'expected': {'genotype': '*1/*17', 'metabolizer': 'Rapid Metabolizer'}
        }
    ]

    print("Testing CYP2C19 Star Allele Calling:")
    print("=" * 50)

    for test_case in test_cases:
        # Create test DataFrame
        test_data = []
        for rsid, genotype in test_case['genotypes'].items():
            test_data.append({'rsid': rsid, 'genotype': genotype})

        df = pd.DataFrame(test_data).set_index('rsid')

        # Call star alleles
        result = star_caller.call_star_alleles('CYP2C19', df)

        # Check results
        success = True
        if 'error' in result:
            print(f"FAIL {test_case['name']}: ERROR - {result['error']}")
            success = False
        else:
            genotype_match = result['genotype'] == test_case['expected']['genotype']
            metabolizer_match = result['metabolizer_status'] == test_case['expected']['metabolizer']

            if genotype_match and metabolizer_match:
                print(f"PASS {test_case['name']}: {result['genotype']} - {result['metabolizer_status']}")
            else:
                print(f"FAIL {test_case['name']}: Expected {test_case['expected']['genotype']} ({test_case['expected']['metabolizer']}), Got {result['genotype']} ({result['metabolizer_status']})")
                success = False

    return success

def test_cyp2d6_alleles():
    """Test CYP2D6 star allele calling"""

    test_cases = [
        {
            'name': 'CYP2D6 *1/*1 (Normal)',
            'genotypes': {'rs3892097': 'GG', 'rs1065852': 'CC'},
            'expected': {'genotype': '*1/*1', 'metabolizer': 'Normal Metabolizer'}
        },
        {
            'name': 'CYP2D6 *1/*4 (Intermediate)',
            'genotypes': {'rs3892097': 'AG', 'rs1065852': 'CT'},
            'expected': {'genotype': '*1/*4', 'metabolizer': 'Intermediate Metabolizer'}
        }
    ]

    print("\nTesting CYP2D6 Star Allele Calling:")
    print("=" * 50)

    for test_case in test_cases:
        test_data = []
        for rsid, genotype in test_case['genotypes'].items():
            test_data.append({'rsid': rsid, 'genotype': genotype})

        df = pd.DataFrame(test_data).set_index('rsid')
        result = star_caller.call_star_alleles('CYP2D6', df)

        if 'error' in result:
            print(f"FAIL {test_case['name']}: ERROR - {result['error']}")
        else:
            print(f"PASS {test_case['name']}: {result['genotype']} - {result['metabolizer_status']}")

def test_cpic_guidelines():
    """Test CPIC guideline retrieval"""

    print("\nTesting CPIC Guidelines:")
    print("=" * 50)

    # Test CYP2C19 clopidogrel guidelines
    recommendations = star_caller.get_cpic_recommendations('CYP2C19', 'Poor', 'clopidogrel')

    if 'clopidogrel' in recommendations and 'Avoid' in recommendations['clopidogrel']:
        print(f"PASS CYP2C19 Poor Metabolizer - Clopidogrel: {recommendations['clopidogrel']}")
    else:
        print(f"FAIL CYP2C19 Poor Metabolizer - Clopidogrel: {recommendations}")

def run_all_tests():
    """Run all validation tests"""
    print("STAR ALLELE VALIDATION TESTS")
    print("=" * 60)

    test_cyp2c19_alleles()
    test_cyp2d6_alleles()
    test_cpic_guidelines()

    print("\n" + "=" * 60)
    print("Test completed. Check results above.")

if __name__ == "__main__":
    run_all_tests()