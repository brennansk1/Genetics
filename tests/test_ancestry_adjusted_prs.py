#!/usr/bin/env python3
"""
Test script for ancestry-adjusted PRS implementation
"""

import os
import sys

import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ancestry_inference import AncestryInference, infer_ancestry_from_snps
from src.genomewide_prs import GenomeWidePRS


def test_ancestry_inference():
    """Test ancestry inference functionality"""
    print("Testing ancestry inference...")

    # Synthetic data for testing purposes - not from real genetic data
    # Create sample DNA data with some AIMs
    sample_data = pd.DataFrame(
        {
            "rsid": ["rs1426654", "rs16891982", "rs2814778", "rs3827760"],
            "genotype": ["CT", "CC", "TT", "GG"],
        }
    )

    # Test ancestry inference
    ancestry_result = infer_ancestry_from_snps(sample_data)

    print(f"Ancestry inference success: {ancestry_result.get('success', False)}")
    if ancestry_result.get("success"):
        print(
            f"Inferred ancestry: {ancestry_result.get('primary_ancestry', 'Unknown')}"
        )
        print(f"Confidence: {ancestry_result.get('confidence', 0.0):.2f}")
        print(
            f"Admixture proportions: {ancestry_result.get('admixture_proportions', {})}"
        )
        print(f"SNPs used: {ancestry_result.get('snps_used', 0)}")
    else:
        print(f"Error: {ancestry_result.get('error', 'Unknown error')}")

    return ancestry_result


def test_ancestry_adjusted_prs():
    """Test ancestry-adjusted PRS calculation"""
    print("\nTesting ancestry-adjusted PRS...")

    # Synthetic data for testing purposes - not from real genetic data
    # Create sample DNA data
    sample_data = pd.DataFrame(
        {
            "rsid": ["rs7903146", "rs13266634", "rs7754840", "rs1426654", "rs16891982"],
            "genotype": ["CT", "CC", "CC", "CT", "CC"],
        }
    )

    calculator = GenomeWidePRS()

    # Test simple PRS calculation (fallback)
    simple_model = {
        "trait": "Test Diabetes",
        "rsid": ["rs7903146", "rs13266634", "rs7754840"],
        "effect_allele": ["T", "C", "C"],
        "effect_weight": [0.31, 0.14, 0.11],
    }

    # Test unadjusted PRS
    unadjusted_result = calculator.calculate_simple_prs(sample_data, simple_model)
    print("Unadjusted PRS:")
    print(f"  Score: {unadjusted_result.get('prs_score', 0):.4f}")
    print(f"  Percentile: {unadjusted_result.get('percentile', 0):.1f}th")

    # Test ancestry inference
    ancestry_result = test_ancestry_inference()

    if ancestry_result.get("success"):
        # Test ancestry-adjusted calculation
        adjusted_result = calculator.calculate_ancestry_adjusted_prs_score(
            sample_data,
            dict(zip(simple_model["rsid"], simple_model["effect_weight"])),
            dict(zip(simple_model["rsid"], simple_model["effect_allele"])),
            ancestry_result.get("primary_ancestry", "European"),
        )

        print("\nAncestry-adjusted PRS:")
        print(f"  Score: {adjusted_result[0]:.4f}")
        print(
            f"  Adjustment factor: {adjusted_result[0] / unadjusted_result.get('prs_score', 1):.3f}"
        )

    return unadjusted_result, ancestry_result


def test_validation_functions():
    """Test validation functions"""
    print("\nTesting validation functions...")

    # Create sample data
    sample_data = pd.DataFrame(
        {
            "rsid": ["rs1426654", "rs16891982", "rs7903146", "rs13266634"],
            "genotype": ["CT", "CC", "CT", "CC"],
        }
    )

    calculator = GenomeWidePRS()

    # Test basic validation
    model = {
        "effect_weights": {"rs7903146": 0.31, "rs13266634": 0.14},
        "effect_alleles": {"rs7903146": "T", "rs13266634": "C"},
    }

    validation = GenomeWidePRS.validate_prs_calculation(sample_data, model)
    print("PRS Validation:")
    print(f"  Coverage: {validation.get('coverage_percentage', 0):.1f}%")
    print(f"  SNPs found: {validation.get('model_snps_found', 0)}")
    print(f"  Warnings: {len(validation.get('warnings', []))}")
    print(f"  Errors: {len(validation.get('errors', []))}")

    # Test ancestry validation
    ancestry_result = {"success": True, "confidence": 0.8, "snps_used": 2}
    ancestry_validation = calculator.validate_ancestry_adjusted_prs(
        sample_data, model, ancestry_result
    )

    print("\nAncestry-adjusted PRS Validation:")
    print(
        f"  Ancestry confidence: {ancestry_validation.get('ancestry_confidence', 0):.2f}"
    )
    print(f"  Recommendation: {ancestry_validation.get('recommendation', 'Unknown')}")


def test_compare_adjusted_vs_unadjusted():
    """Test comparison between adjusted and unadjusted PRS"""
    print("\nTesting adjusted vs unadjusted comparison...")

    # This would require a real PGS ID, so we'll skip for now
    print("Comparison test requires real PGS model - skipping in basic test")


def main():
    """Run all ancestry-adjusted PRS tests"""
    print("=== Ancestry-Adjusted PRS Implementation Test ===\n")

    test_ancestry_inference()
    test_ancestry_adjusted_prs()
    test_validation_functions()
    test_compare_adjusted_vs_unadjusted()

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    main()
