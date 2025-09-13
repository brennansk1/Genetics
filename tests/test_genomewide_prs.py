#!/usr/bin/env python3
"""
Test script for genome-wide PRS implementation
"""

import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.genomewide_prs import GenomeWidePRS
from src.api_functions import get_pgs_catalog_data, get_pgs_model_data
from src.snp_data import prs_models, get_genomewide_models, get_simple_model

def test_pgs_catalog_integration():
    """Test PGS Catalog API integration"""
    print("Testing PGS Catalog integration...")

    # Test searching for models
    try:
        results = get_pgs_catalog_data("diabetes", max_results=5)
        print(f"Found {len(results)} diabetes-related models")
        if results:
            print(f"First model: {results[0].get('id', 'N/A')} - {results[0].get('trait_reported', 'N/A')}")
    except Exception as e:
        print(f"Error testing PGS search: {e}")

    # Test getting specific model
    try:
        model_data = get_pgs_model_data("PGS000001", include_metadata=False)
        if model_data:
            print(f"Successfully loaded PGS000001 with {model_data.get('num_variants', 0)} variants")
        else:
            print("Failed to load PGS000001")
    except Exception as e:
        print(f"Error loading PGS model: {e}")

def test_prs_calculator():
    """Test PRS calculator functionality"""
    print("\nTesting PRS calculator...")

    # Create sample DNA data
    sample_data = pd.DataFrame({
        'rsid': ['rs7903146', 'rs13266634', 'rs7754840'],
        'genotype': ['CT', 'CC', 'CC']
    })

    calculator = GenomeWidePRS()

    # Test simple PRS calculation
    simple_model = {
        'rsid': ['rs7903146', 'rs13266634', 'rs7754840'],
        'effect_allele': ['T', 'C', 'C'],
        'effect_weight': [0.31, 0.14, 0.11]
    }

    result = calculator.calculate_simple_prs(sample_data, {'trait': 'Test Diabetes', **simple_model})

    if result['success']:
        print(f"PRS Score: {result['prs_score']:.4f}")
        print(f"Percentile: {result['percentile']:.1f}th")
        print(f"SNPs used: {result['snps_used']}/{result['total_snps']}")
    else:
        print(f"PRS calculation failed: {result.get('error', 'Unknown error')}")

def test_model_structure():
    """Test the updated PRS model structure"""
    print("\nTesting PRS model structure...")

    # Test getting genome-wide models
    coronary_models = get_genomewide_models("Coronary Artery Disease")
    print(f"Coronary Artery Disease has {len(coronary_models)} genome-wide models")

    # Test getting simple model
    simple_model = get_simple_model("Type 2 Diabetes")
    if simple_model:
        print(f"Type 2 Diabetes simple model has {len(simple_model['rsid'])} SNPs")
    else:
        print("No simple model found for Type 2 Diabetes")

def main():
    """Run all tests"""
    print("=== Genome-wide PRS Implementation Test ===\n")

    test_pgs_catalog_integration()
    test_prs_calculator()
    test_model_structure()

    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()