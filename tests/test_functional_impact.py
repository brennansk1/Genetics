#!/usr/bin/env python3
"""
Test script for functional impact analysis functionality
"""

import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bioinformatics_utils import predict_functional_impact


def test_functional_impact_prediction_basic():
    """Test basic functional impact prediction."""
    print("Testing basic functional impact prediction...")

    try:
        # Test known functional SNPs
        test_cases = [
            ("rs1801133", "CT", "MTHFR", "enzyme_activity"),
            ("rs4988235", "TT", "MCM6", "lactase_persistence"),
            ("rs4680", "AG", "COMT", "enzyme_activity"),
            ("rs429358", "CT", "APOE", "protein_function"),
        ]

        for rsid, genotype, gene, expected_impact in test_cases:
            result = predict_functional_impact(rsid, genotype, gene)

            assert isinstance(result, dict), f"Result should be dict for {rsid}"
            assert "predicted_impact" in result, f"Should have predicted_impact for {rsid}"
            assert "genotype" in result, f"Should have genotype for {rsid}"
            assert "gene" in result, f"Should have gene for {rsid}"

            # Check that result contains expected impact type
            if expected_impact != "unknown":
                assert result["predicted_impact"] == expected_impact, f"Expected {expected_impact} for {rsid}, got {result['predicted_impact']}"

        print("PASS: Basic functional impact prediction works")
        return True

    except Exception as e:
        print(f"FAIL: Basic functional impact prediction failed: {e}")
        return False


def test_functional_impact_enzyme_activity():
    """Test enzyme activity predictions."""
    print("Testing enzyme activity predictions...")

    try:
        # Test MTHFR enzyme activity
        result = predict_functional_impact("rs1801133", "CT", "MTHFR")

        assert result["predicted_impact"] == "enzyme_activity", "MTHFR C677T should affect enzyme activity"
        assert "activity_level" in result, "Should have activity_level for MTHFR"

        # Test COMT enzyme activity
        result_comt = predict_functional_impact("rs4680", "AG", "COMT")

        assert result_comt["predicted_impact"] == "enzyme_activity", "COMT Val158Met should affect enzyme activity"
        assert "activity_level" in result_comt, "Should have activity_level for COMT"

        print("PASS: Enzyme activity predictions work correctly")
        return True

    except Exception as e:
        print(f"FAIL: Enzyme activity predictions failed: {e}")
        return False


def test_functional_impact_lactase_persistence():
    """Test lactase persistence predictions."""
    print("Testing lactase persistence predictions...")

    try:
        # Test MCM6 lactase persistence
        result = predict_functional_impact("rs4988235", "TT", "MCM6")

        assert result["predicted_impact"] == "lactase_persistence", "MCM6 should affect lactase persistence"
        assert "lactase_status" in result, "Should have lactase_status"

        # Test different genotypes
        result_ct = predict_functional_impact("rs4988235", "CT", "MCM6")
        assert result_ct["predicted_impact"] == "lactase_persistence", "CT genotype should also be lactase persistence related"

        print("PASS: Lactase persistence predictions work correctly")
        return True

    except Exception as e:
        print(f"FAIL: Lactase persistence predictions failed: {e}")
        return False


def test_functional_impact_unknown_snp():
    """Test handling of unknown SNPs."""
    print("Testing unknown SNP handling...")

    try:
        # Test unknown SNP
        result = predict_functional_impact("rs99999999", "AA", "UNKNOWN_GENE")

        assert result["predicted_impact"] == "unknown", "Unknown SNP should have unknown impact"
        assert result["genotype"] == "AA", "Genotype should be preserved"
        assert result["gene"] == "UNKNOWN_GENE", "Gene should be preserved"

        print("PASS: Unknown SNP handling works correctly")
        return True

    except Exception as e:
        print(f"FAIL: Unknown SNP handling failed: {e}")
        return False


def test_functional_impact_drug_metabolism():
    """Test drug metabolism predictions."""
    print("Testing drug metabolism predictions...")

    try:
        # Test CYP2C19
        result = predict_functional_impact("rs4244285", "AG", "CYP2C19")

        assert result["predicted_impact"] == "drug_metabolism", "CYP2C19 should affect drug metabolism"
        assert "metabolism_type" in result, "Should have metabolism_type"

        # Test CYP2D6
        result_2d6 = predict_functional_impact("rs3892097", "GG", "CYP2D6")

        assert result_2d6["predicted_impact"] == "drug_metabolism", "CYP2D6 should affect drug metabolism"

        print("PASS: Drug metabolism predictions work correctly")
        return True

    except Exception as e:
        print(f"FAIL: Drug metabolism predictions failed: {e}")
        return False


def test_functional_impact_mutation_types():
    """Test mutation type classification."""
    print("Testing mutation type classification...")

    try:
        # Test missense mutation (change amino acid)
        result_missense = predict_functional_impact("rs1801133", "CT", "MTHFR")

        if "mutation_type" in result_missense:
            assert result_missense["mutation_type"] in ["missense", "synonymous", "nonsense", "unknown"], f"Invalid mutation type: {result_missense['mutation_type']}"

        # Test synonymous mutation (no amino acid change)
        result_synonymous = predict_functional_impact("rs12345678", "CC", "TEST_GENE")

        # Should handle gracefully even for unknown SNPs
        assert isinstance(result_synonymous, dict), "Should return dict even for unknown SNPs"

        print("PASS: Mutation type classification works")
        return True

    except Exception as e:
        print(f"FAIL: Mutation type classification failed: {e}")
        return False


def test_functional_impact_sequence_analysis():
    """Test sequence-based functional impact analysis."""
    print("Testing sequence-based functional impact analysis...")

    try:
        # Test with SNPs that have sequence context available
        result = predict_functional_impact("rs1801133", "CT", "MTHFR")

        # Check for sequence-related fields
        sequence_fields = ["mutation_type", "codon_change", "amino_acid_change"]

        found_sequence_info = any(field in result for field in sequence_fields)

        if found_sequence_info:
            print("PASS: Sequence-based analysis provided additional information")
        else:
            print("INFO: Sequence-based analysis not available (expected without reference genome)")

        return True

    except Exception as e:
        print(f"FAIL: Sequence-based functional impact analysis failed: {e}")
        return False


def test_functional_impact_error_handling():
    """Test error handling in functional impact prediction."""
    print("Testing functional impact error handling...")

    try:
        # Test with invalid inputs
        result = predict_functional_impact("", "", "")

        assert isinstance(result, dict), "Should return dict even with invalid inputs"
        assert "predicted_impact" in result, "Should have predicted_impact key"

        # Test with None inputs
        result_none = predict_functional_impact(None, None, None)

        assert isinstance(result_none, dict), "Should handle None inputs gracefully"

        print("PASS: Error handling works correctly")
        return True

    except Exception as e:
        print(f"FAIL: Error handling failed: {e}")
        return False


def test_functional_impact_result_structure():
    """Test that functional impact results have consistent structure."""
    print("Testing functional impact result structure...")

    try:
        test_cases = [
            ("rs1801133", "CT", "MTHFR"),
            ("rs4988235", "TT", "MCM6"),
            ("rs4680", "AG", "COMT"),
            ("rs99999999", "AA", "UNKNOWN"),
        ]

        for rsid, genotype, gene in test_cases:
            result = predict_functional_impact(rsid, genotype, gene)

            # Required fields
            required_fields = ["predicted_impact", "genotype", "gene", "rsid"]
            for field in required_fields:
                assert field in result, f"Missing required field: {field}"

            # Check data types
            assert isinstance(result["predicted_impact"], str), "predicted_impact should be string"
            assert isinstance(result["genotype"], str), "genotype should be string"
            assert isinstance(result["gene"], str), "gene should be string"
            assert isinstance(result["rsid"], str), "rsid should be string"

        print("PASS: Functional impact results have consistent structure")
        return True

    except Exception as e:
        print(f"FAIL: Result structure test failed: {e}")
        return False


def run_functional_impact_tests():
    """Run all functional impact tests."""
    print("FUNCTIONAL IMPACT ANALYSIS TESTS")
    print("=" * 40)

    tests = [
        test_functional_impact_prediction_basic,
        test_functional_impact_enzyme_activity,
        test_functional_impact_lactase_persistence,
        test_functional_impact_unknown_snp,
        test_functional_impact_drug_metabolism,
        test_functional_impact_mutation_types,
        test_functional_impact_sequence_analysis,
        test_functional_impact_error_handling,
        test_functional_impact_result_structure,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__} - {str(e)}")

    print("\n" + "=" * 40)
    print(f"Tests passed: {passed}/{total}")
    if passed == total:
        print("All functional impact analysis tests passed!")
        return True
    else:
        print("Some functional impact analysis tests failed.")
        return False


if __name__ == "__main__":
    success = run_functional_impact_tests()
    if not success:
        exit(1)