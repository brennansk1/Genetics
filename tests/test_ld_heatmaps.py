#!/usr/bin/env python3
"""
Test script for LD heatmap functionality
"""

import os
import sys
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bioinformatics_utils import calculate_ld_matrix


def test_ld_matrix_calculation():
    """Test LD matrix calculation with sample data."""
    print("Testing LD matrix calculation...")

    try:
        # Create sample genotype data in the format expected by scikit-allel
        # Format: (n_variants, n_samples, ploidy) - 3D array
        genotype_data = np.array([
            [[0, 0], [1, 1]],  # SNP1: AA, TT
            [[1, 1], [0, 0]],  # SNP2: TT, AA
        ])
        snp_labels = ["rs1", "rs2"]

        ld_matrix, labels = calculate_ld_matrix(genotype_data, snp_labels)

        # Check result structure
        assert isinstance(ld_matrix, np.ndarray), "LD matrix should be numpy array"
        assert ld_matrix.shape == (2, 2), f"Should be 2x2 matrix, got {ld_matrix.shape}"
        assert len(labels) == 2, f"Should have 2 labels, got {len(labels)}"
        assert labels == snp_labels, f"Labels should match input, got {labels}"

        # Check matrix properties
        assert np.allclose(ld_matrix, ld_matrix.T), "LD matrix should be symmetric"
        assert np.all(np.diag(ld_matrix) == 1.0), "Diagonal should be 1.0 (perfect LD with self)"

        print("PASS: LD matrix calculation works correctly")
        return True

    except Exception as e:
        print(f"FAIL: LD matrix calculation failed: {e}")
        return False


def test_ld_matrix_properties():
    """Test mathematical properties of LD matrix."""
    print("Testing LD matrix mathematical properties...")

    try:
        # Create test data with known LD patterns
        # Perfect LD: SNPs are identical
        genotype_data_perfect = np.array([
            [[0, 0], [0, 0], [1, 1], [1, 1]],  # SNP1
            [[0, 0], [0, 0], [1, 1], [1, 1]],  # SNP2 (identical to SNP1)
        ])

        # No LD: SNPs are independent
        genotype_data_independent = np.array([
            [[0, 0], [0, 1], [1, 0], [1, 1]],  # SNP1
            [[1, 1], [0, 1], [0, 0], [1, 0]],  # SNP2 (random)
        ])

        snp_labels = ["rs1", "rs2"]

        # Test perfect LD
        ld_perfect, _ = calculate_ld_matrix(genotype_data_perfect, snp_labels)
        assert np.allclose(ld_perfect[0, 1], 1.0, atol=0.1), f"Perfect LD should be ~1.0, got {ld_perfect[0, 1]}"

        # Test independent SNPs
        ld_independent, _ = calculate_ld_matrix(genotype_data_independent, snp_labels)
        assert abs(ld_independent[0, 1]) < 0.5, f"Independent SNPs should have low LD, got {ld_independent[0, 1]}"

        print("PASS: LD matrix properties are correct")
        return True

    except Exception as e:
        print(f"FAIL: LD matrix properties test failed: {e}")
        return False


def test_ld_matrix_edge_cases():
    """Test LD matrix calculation with edge cases."""
    print("Testing LD matrix edge cases...")

    try:
        # Test with single SNP
        genotype_data_single = np.array([
            [[0, 0], [1, 1]],  # Single SNP
        ])
        ld_single, labels_single = calculate_ld_matrix(genotype_data_single, ["rs1"])
        assert ld_single.shape == (1, 1), f"Single SNP should give 1x1 matrix, got {ld_single.shape}"
        assert ld_single[0, 0] == 1.0, "Single SNP diagonal should be 1.0"

        # Test with no variation (all same genotype)
        genotype_data_no_var = np.array([
            [[0, 0], [0, 0], [0, 0]],  # SNP1: all AA
            [[1, 1], [1, 1], [1, 1]],  # SNP2: all TT
        ])
        ld_no_var, _ = calculate_ld_matrix(genotype_data_no_var, ["rs1", "rs2"])
        # Should handle gracefully (may return NaN or specific value)

        print("PASS: LD matrix handles edge cases correctly")
        return True

    except Exception as e:
        print(f"FAIL: LD matrix edge cases failed: {e}")
        return False


def test_ld_visualization_data():
    """Test that LD matrix produces data suitable for heatmap visualization."""
    print("Testing LD visualization data...")

    try:
        # Create sample data
        genotype_data = np.array([
            [[0, 0], [0, 1], [1, 1]],  # SNP1
            [[0, 1], [1, 0], [1, 1]],  # SNP2
            [[1, 1], [0, 0], [0, 1]],  # SNP3
        ])
        snp_labels = ["rs1", "rs2", "rs3"]

        ld_matrix, labels = calculate_ld_matrix(genotype_data, snp_labels)

        # Check visualization requirements
        assert ld_matrix.shape[0] == len(labels), "Matrix size should match number of labels"
        assert all(isinstance(label, str) for label in labels), "All labels should be strings"

        # Check matrix values are in valid range for r²
        assert np.all((ld_matrix >= 0) & (ld_matrix <= 1)), f"LD values should be in [0,1], got range [{np.min(ld_matrix)}, {np.max(ld_matrix)}]"

        # Check for NaN values (should be handled)
        assert not np.any(np.isnan(ld_matrix)), "LD matrix should not contain NaN values"

        print("PASS: LD matrix suitable for heatmap visualization")
        return True

    except Exception as e:
        print(f"FAIL: LD visualization data test failed: {e}")
        return False


def test_ld_calculation_error_handling():
    """Test error handling in LD calculations."""
    print("Testing LD calculation error handling...")

    try:
        # Test with empty data
        try:
            ld_matrix, labels = calculate_ld_matrix([], [])
            # Should either return empty result or raise appropriate error
        except (ValueError, IndexError):
            pass  # Expected

        # Test with mismatched data
        try:
            genotype_data = [
                [[0, 0], [1, 1]],  # 2 samples
            ]
            # This should be handled gracefully
            ld_matrix, labels = calculate_ld_matrix(genotype_data, ["rs1"])
        except Exception:
            pass  # Expected for invalid input

        print("PASS: LD calculation error handling works")
        return True

    except Exception as e:
        print(f"FAIL: LD calculation error handling failed: {e}")
        return False


def test_ld_statistics():
    """Test LD statistics calculations."""
    print("Testing LD statistics...")

    try:
        # Create test data with varying LD patterns
        genotype_data = np.array([
            [[0, 0], [0, 1], [1, 0], [1, 1]],  # SNP1
            [[0, 0], [0, 1], [1, 0], [1, 1]],  # SNP2 (moderate LD)
            [[1, 1], [1, 0], [0, 1], [0, 0]],  # SNP3 (different pattern)
        ])
        snp_labels = ["rs1", "rs2", "rs3"]

        ld_matrix, labels = calculate_ld_matrix(genotype_data, snp_labels)

        # Calculate basic statistics
        mean_ld = np.mean(ld_matrix)
        max_ld = np.max(ld_matrix)
        min_ld = np.min(ld_matrix[np.triu_indices_from(ld_matrix, k=1)])  # Off-diagonal minimum

        # Basic sanity checks
        assert 0 <= mean_ld <= 1, f"Mean LD should be in [0,1], got {mean_ld}"
        assert 0 <= max_ld <= 1, f"Max LD should be in [0,1], got {max_ld}"
        assert 0 <= min_ld <= 1, f"Min LD should be in [0,1], got {min_ld}"

        print(f"PASS: LD statistics calculated correctly (mean: {mean_ld:.3f}, max: {max_ld:.3f})")
        return True

    except Exception as e:
        print(f"FAIL: LD statistics test failed: {e}")
        return False


def run_ld_heatmap_tests():
    """Run all LD heatmap tests."""
    print("LD HEATMAP TESTS")
    print("=" * 20)

    tests = [
        test_ld_matrix_calculation,
        test_ld_matrix_properties,
        test_ld_matrix_edge_cases,
        test_ld_visualization_data,
        test_ld_calculation_error_handling,
        test_ld_statistics,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__} - {str(e)}")

    print("\n" + "=" * 20)
    print(f"Tests passed: {passed}/{total}")
    if passed == total:
        print("All LD heatmap tests passed!")
        return True
    else:
        print("Some LD heatmap tests failed.")
        return False


if __name__ == "__main__":
    success = run_ld_heatmap_tests()
    if not success:
        exit(1)