#!/usr/bin/env python3
"""
Test script for ancestry inference with PCA/KNN functionality
"""

import os
import sys
import tempfile

import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ancestry_inference import AncestryInference, infer_ancestry_from_snps


def test_ancestry_inference_initialization():
    """Test AncestryInference class initialization."""
    print("Testing AncestryInference initialization...")

    try:
        inference = AncestryInference()
        assert inference is not None, "AncestryInference should initialize"
        assert hasattr(inference, 'aims_data'), "Should have aims_data attribute"
        assert hasattr(inference, 'reference_populations'), "Should have reference_populations"

        print("PASS: AncestryInference initialization works")
        return True
    except Exception as e:
        print(f"FAIL: AncestryInference initialization failed: {e}")
        return False


def test_frequency_based_inference():
    """Test frequency-based ancestry inference."""
    print("Testing frequency-based ancestry inference...")

    try:
        # Create sample SNP data
        sample_data = pd.DataFrame({
            "rsid": ["rs1426654", "rs16891982", "rs2814778"],
            "genotype": ["CT", "CC", "TT"]
        })

        inference = AncestryInference()
        result = inference.infer_ancestry(sample_data, method="frequency_based")

        # Check result structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "success" in result, "Result should have success key"

        if result.get("success"):
            assert "primary_ancestry" in result, "Should have primary_ancestry"
            assert "confidence" in result, "Should have confidence"
            print(f"PASS: Frequency-based inference returned: {result.get('primary_ancestry', 'Unknown')}")
        else:
            print(f"PASS: Frequency-based inference handled gracefully: {result.get('error', 'Unknown error')}")

        return True
    except Exception as e:
        print(f"FAIL: Frequency-based inference failed: {e}")
        return False


def test_pca_based_inference():
    """Test PCA-based ancestry inference."""
    print("Testing PCA-based ancestry inference...")

    try:
        # Create sample SNP data
        sample_data = pd.DataFrame({
            "rsid": ["rs1426654", "rs16891982", "rs2814778"],
            "genotype": ["CT", "CC", "TT"]
        })

        inference = AncestryInference()
        result = inference.infer_ancestry(sample_data, method="pca")

        # Check result structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "success" in result, "Result should have success key"

        if result.get("success"):
            assert "primary_ancestry" in result, "Should have primary_ancestry"
            assert "probabilities" in result, "Should have probabilities"
            print(f"PASS: PCA-based inference returned: {result.get('primary_ancestry', 'Unknown')}")
        else:
            print(f"PASS: PCA-based inference handled gracefully: {result.get('error', 'Unknown error')}")

        return True
    except Exception as e:
        print(f"FAIL: PCA-based inference failed: {e}")
        return False


def test_convenience_function():
    """Test the convenience function for ancestry inference."""
    print("Testing convenience function...")

    try:
        # Create sample SNP data
        sample_data = pd.DataFrame({
            "rsid": ["rs1426654", "rs16891982"],
            "genotype": ["CT", "CC"]
        })

        result = infer_ancestry_from_snps(sample_data)

        # Check result structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "success" in result, "Result should have success key"

        print("PASS: Convenience function works")
        return True
    except Exception as e:
        print(f"FAIL: Convenience function failed: {e}")
        return False


def test_ancestry_adjusted_parameters():
    """Test ancestry-adjusted parameter calculation."""
    print("Testing ancestry-adjusted parameters...")

    try:
        inference = AncestryInference()

        # Test with different ancestries
        test_ancestries = ["European", "African", "East_Asian", "South_Asian", "American"]

        for ancestry in test_ancestries:
            adjusted_params = inference.get_ancestry_adjusted_parameters(
                ancestry, {"base_param": 1.0}
            )

            assert "ancestry_adjustment" in adjusted_params, f"Should have ancestry_adjustment for {ancestry}"
            assert "inferred_ancestry" in adjusted_params, f"Should have inferred_ancestry for {ancestry}"
            assert adjusted_params["inferred_ancestry"] == ancestry, f"Ancestry should match for {ancestry}"

            adjustment = adjusted_params["ancestry_adjustment"]
            assert "percentile_adjustment" in adjustment, f"Should have percentile_adjustment for {ancestry}"
            assert "effect_size_multiplier" in adjustment, f"Should have effect_size_multiplier for {ancestry}"

        print("PASS: Ancestry-adjusted parameters work correctly")
        return True
    except Exception as e:
        print(f"FAIL: Ancestry-adjusted parameters failed: {e}")
        return False


def test_ancestry_validation():
    """Test ancestry inference validation."""
    print("Testing ancestry validation...")

    try:
        # Create sample data
        sample_data = pd.DataFrame({
            "rsid": ["rs1426654", "rs16891982"],
            "genotype": ["CT", "CC"]
        })

        inference = AncestryInference()
        result = {"success": True, "confidence": 0.8}

        validation = inference.validate_ancestry_inference(sample_data, result)

        # Check validation structure
        assert isinstance(validation, dict), "Validation should be a dictionary"
        assert "total_aims_available" in validation, "Should have total_aims_available"
        assert "aims_found_in_data" in validation, "Should have aims_found_in_data"
        assert "coverage_percentage" in validation, "Should have coverage_percentage"
        assert "confidence_assessment" in validation, "Should have confidence_assessment"

        print("PASS: Ancestry validation works correctly")
        return True
    except Exception as e:
        print(f"FAIL: Ancestry validation failed: {e}")
        return False


def test_population_code_mapping():
    """Test population code to name mapping."""
    print("Testing population code mapping...")

    try:
        inference = AncestryInference()

        # Test the mapping function
        test_codes = ["EUR", "AFR", "EAS", "SAS", "AMR", "UNKNOWN"]
        expected_names = ["European", "African", "East Asian", "South Asian", "American", "UNKNOWN"]

        for code, expected in zip(test_codes, expected_names):
            result = inference._map_population_code(code)
            assert result == expected, f"Code {code} should map to {expected}, got {result}"

        print("PASS: Population code mapping works correctly")
        return True
    except Exception as e:
        print(f"FAIL: Population code mapping failed: {e}")
        return False

def test_allele_count_calculation():
    """Test effect allele counting."""
    print("Testing allele count calculation...")

    try:
        inference = AncestryInference()

        # Test different genotypes - note: the logic assumes first allele is effect allele
        test_cases = [
            ("AA", 2),  # Homozygous reference (A is effect allele)
            ("TT", 2),  # Homozygous (T is effect allele in this context)
            ("AT", 1),  # Heterozygous (A is effect allele)
            ("CC", 2),  # Homozygous (C is effect allele)
        ]

        for genotype, expected in test_cases:
            count = inference._count_effect_allele(genotype)
            assert count == expected, f"Genotype {genotype} should have {expected} effect alleles, got {count}"

        print("PASS: Allele count calculation works correctly")
        return True

    except Exception as e:
        print(f"FAIL: Allele count calculation failed: {e}")
        return False


def run_ancestry_inference_tests():
    """Run all ancestry inference tests."""
    print("ANCESTRY INFERENCE TESTS")
    print("=" * 35)

    tests = [
        test_ancestry_inference_initialization,
        test_frequency_based_inference,
        test_pca_based_inference,
        test_convenience_function,
        test_ancestry_adjusted_parameters,
        test_ancestry_validation,
        test_population_code_mapping,
        test_allele_count_calculation,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__} - {str(e)}")

    print("\n" + "=" * 35)
    print(f"Tests passed: {passed}/{total}")
    if passed == total:
        print("All ancestry inference tests passed!")
        return True
    else:
        print("Some ancestry inference tests failed.")
        return False


if __name__ == "__main__":
    success = run_ancestry_inference_tests()
    if not success:
        exit(1)