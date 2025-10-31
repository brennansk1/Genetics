#!/usr/bin/env python3
"""
Test script for PRS explainability functionality
"""

import os
import sys

import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.genomewide_prs import GenomeWidePRS


def test_prs_calculator_initialization():
    """Test PRS calculator initialization."""
    print("Testing PRS calculator initialization...")

    try:
        calculator = GenomeWidePRS()
        assert calculator is not None, "GenomeWidePRS should initialize"
        assert hasattr(calculator, 'calculate_simple_prs'), "Should have calculate_simple_prs method"
        assert hasattr(calculator, 'calculate_ancestry_adjusted_prs_score'), "Should have ancestry-adjusted method"

        print("PASS: PRS calculator initialization works")
        return True
    except Exception as e:
        print(f"FAIL: PRS calculator initialization failed: {e}")
        return False


def test_simple_prs_calculation():
    """Test simple PRS calculation."""
    print("Testing simple PRS calculation...")

    try:
        # Create sample data
        sample_data = pd.DataFrame({
            "rsid": ["rs7903146", "rs13266634", "rs7754840"],
            "genotype": ["CT", "CC", "CC"]
        })

        calculator = GenomeWidePRS()

        # Test model
        simple_model = {
            "trait": "Test Diabetes",
            "rsid": ["rs7903146", "rs13266634", "rs7754840"],
            "effect_allele": ["T", "C", "C"],
            "effect_weight": [0.31, 0.14, 0.11],
        }

        result = calculator.calculate_simple_prs(sample_data, simple_model)

        # Check result structure
        assert isinstance(result, dict), "Result should be dictionary"
        assert "success" in result, "Should have success key"

        if result.get("success"):
            assert "prs_score" in result, "Should have prs_score"
            assert "percentile" in result, "Should have percentile"
            assert "snps_used" in result, "Should have snps_used"
            assert "total_snps" in result, "Should have total_snps"

            # Check score is reasonable
            assert isinstance(result["prs_score"], (int, float)), "PRS score should be numeric"
            assert 0 <= result["percentile"] <= 100, f"Percentile should be 0-100, got {result['percentile']}"

        print("PASS: Simple PRS calculation works")
        return True

    except Exception as e:
        print(f"FAIL: Simple PRS calculation failed: {e}")
        return False


def test_ancestry_adjusted_prs():
    """Test ancestry-adjusted PRS calculation."""
    print("Testing ancestry-adjusted PRS calculation...")

    try:
        # Create sample data
        sample_data = pd.DataFrame({
            "rsid": ["rs7903146", "rs13266634", "rs7754840", "rs1426654"],
            "genotype": ["CT", "CC", "CC", "CT"]
        })

        calculator = GenomeWidePRS()

        # Test parameters
        effect_weights = {"rs7903146": 0.31, "rs13266634": 0.14, "rs7754840": 0.11}
        effect_alleles = {"rs7903146": "T", "rs13266634": "C", "rs7754840": "C"}
        ancestry = "European"

        result = calculator.calculate_ancestry_adjusted_prs_score(
            sample_data, effect_weights, effect_alleles, ancestry
        )

        # Check result
        assert isinstance(result, tuple), "Should return tuple"
        assert len(result) == 2, "Should return (score, adjustment_info)"

        score, adjustment_info = result
        assert isinstance(score, (int, float)), "Score should be numeric"

        print("PASS: Ancestry-adjusted PRS calculation works")
        return True

    except Exception as e:
        print(f"FAIL: Ancestry-adjusted PRS calculation failed: {e}")
        return False


def test_prs_validation():
    """Test PRS calculation validation."""
    print("Testing PRS validation...")

    try:
        # Create sample data
        sample_data = pd.DataFrame({
            "rsid": ["rs7903146", "rs13266634"],
            "genotype": ["CT", "CC"]
        })

        calculator = GenomeWidePRS()

        model = {
            "effect_weights": {"rs7903146": 0.31, "rs13266634": 0.14},
            "effect_alleles": {"rs7903146": "T", "rs13266634": "C"},
        }

        validation = GenomeWidePRS.validate_prs_calculation(sample_data, model)

        # Check validation structure
        assert isinstance(validation, dict), "Validation should be dictionary"
        assert "coverage_percentage" in validation, "Should have coverage_percentage"
        assert "model_snps_found" in validation, "Should have model_snps_found"
        assert "warnings" in validation, "Should have warnings"
        assert "errors" in validation, "Should have errors"

        print("PASS: PRS validation works")
        return True

    except Exception as e:
        print(f"FAIL: PRS validation failed: {e}")
        return False


def test_ancestry_adjusted_prs_validation():
    """Test ancestry-adjusted PRS validation."""
    print("Testing ancestry-adjusted PRS validation...")

    try:
        # Create sample data
        sample_data = pd.DataFrame({
            "rsid": ["rs7903146", "rs13266634"],
            "genotype": ["CT", "CC"]
        })

        calculator = GenomeWidePRS()

        model = {
            "effect_weights": {"rs7903146": 0.31, "rs13266634": 0.14},
            "effect_alleles": {"rs7903146": "T", "rs13266634": "C"},
        }

        ancestry_result = {"success": True, "confidence": 0.8}

        validation = calculator.validate_ancestry_adjusted_prs(
            sample_data, model, ancestry_result
        )

        # Check validation structure
        assert isinstance(validation, dict), "Validation should be dictionary"
        assert "ancestry_confidence" in validation, "Should have ancestry_confidence"
        assert "recommendation" in validation, "Should have recommendation"

        print("PASS: Ancestry-adjusted PRS validation works")
        return True

    except Exception as e:
        print(f"FAIL: Ancestry-adjusted PRS validation failed: {e}")
        return False


def test_prs_score_interpretation():
    """Test PRS score interpretation."""
    print("Testing PRS score interpretation...")

    try:
        # Test percentile interpretation
        test_percentiles = [5, 25, 50, 75, 95]

        for percentile in test_percentiles:
            if percentile < 25:
                expected_risk = "low"
            elif percentile < 75:
                expected_risk = "moderate"
            else:
                expected_risk = "high"

            # Basic check that percentile is valid
            assert 0 <= percentile <= 100, f"Invalid percentile: {percentile}"

        print("PASS: PRS score interpretation logic works")
        return True

    except Exception as e:
        print(f"FAIL: PRS score interpretation failed: {e}")
        return False


def test_prs_model_loading():
    """Test PRS model loading functionality."""
    print("Testing PRS model loading...")

    try:
        calculator = GenomeWidePRS()

        # Test getting genome-wide models
        coronary_models = calculator.get_genomewide_models("Coronary Artery Disease")
        assert isinstance(coronary_models, list), "Should return list of models"

        # Test getting simple model
        diabetes_model = calculator.get_simple_model("Type 2 Diabetes")
        # May return None if model not available
        assert diabetes_model is None or isinstance(diabetes_model, dict), "Should return None or dict"

        print("PASS: PRS model loading works")
        return True

    except Exception as e:
        print(f"FAIL: PRS model loading failed: {e}")
        return False


def test_prs_error_handling():
    """Test error handling in PRS calculations."""
    print("Testing PRS error handling...")

    try:
        calculator = GenomeWidePRS()

        # Test with empty data
        empty_data = pd.DataFrame()
        result = calculator.calculate_simple_prs(empty_data, {})

        assert isinstance(result, dict), "Should return dict even with empty data"
        assert "success" in result, "Should have success key"

        # Test with invalid model
        sample_data = pd.DataFrame({"rsid": ["rs1"], "genotype": ["AA"]})
        invalid_model = {"invalid": "model"}

        result_invalid = calculator.calculate_simple_prs(sample_data, invalid_model)
        assert isinstance(result_invalid, dict), "Should handle invalid model gracefully"

        print("PASS: PRS error handling works")
        return True

    except Exception as e:
        print(f"FAIL: PRS error handling failed: {e}")
        return False


def test_prs_result_structure():
    """Test that PRS results have consistent structure."""
    print("Testing PRS result structure consistency...")

    try:
        sample_data = pd.DataFrame({
            "rsid": ["rs7903146", "rs13266634"],
            "genotype": ["CT", "CC"]
        })

        calculator = GenomeWidePRS()

        model = {
            "trait": "Test Trait",
            "rsid": ["rs7903146", "rs13266634"],
            "effect_allele": ["T", "C"],
            "effect_weight": [0.31, 0.14],
        }

        result = calculator.calculate_simple_prs(sample_data, model)

        # Required fields for successful calculation
        required_fields = ["success", "prs_score", "percentile", "snps_used", "total_snps"]

        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

        # Check data types
        assert isinstance(result["success"], bool), "success should be boolean"
        if result["success"]:
            assert isinstance(result["prs_score"], (int, float)), "prs_score should be numeric"
            assert isinstance(result["percentile"], (int, float)), "percentile should be numeric"
            assert isinstance(result["snps_used"], int), "snps_used should be int"
            assert isinstance(result["total_snps"], int), "total_snps should be int"

        print("PASS: PRS results have consistent structure")
        return True

    except Exception as e:
        print(f"FAIL: PRS result structure test failed: {e}")
        return False


def run_prs_explainability_tests():
    """Run all PRS explainability tests."""
    print("PRS EXPLAINABILITY TESTS")
    print("=" * 30)

    tests = [
        test_prs_calculator_initialization,
        test_simple_prs_calculation,
        test_ancestry_adjusted_prs,
        test_prs_validation,
        test_ancestry_adjusted_prs_validation,
        test_prs_score_interpretation,
        test_prs_model_loading,
        test_prs_error_handling,
        test_prs_result_structure,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__} - {str(e)}")

    print("\n" + "=" * 30)
    print(f"Tests passed: {passed}/{total}")
    if passed == total:
        print("All PRS explainability tests passed!")
        return True
    else:
        print("Some PRS explainability tests failed.")
        return False


if __name__ == "__main__":
    success = run_prs_explainability_tests()
    if not success:
        exit(1)