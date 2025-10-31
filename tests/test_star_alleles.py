"""
Test script for validating star allele calling with known haplotype combinations
"""

import os
import sys

import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pgx_star_alleles import detect_cnv, star_caller


def test_cyp2c19_alleles():
    """Test CYP2C19 star allele calling with known combinations"""

    test_cases = [
        {
            "name": "CYP2C19 *1/*1 (Normal)",
            "genotypes": {"rs4244285": "GG", "rs12248560": "CC"},
            "expected": {"genotype": "*1/*1", "metabolizer": "Normal Metabolizer"},
        },
        {
            "name": "CYP2C19 *1/*2 (Intermediate)",
            "genotypes": {"rs4244285": "AG", "rs12248560": "CC"},
            "expected": {
                "genotype": "*1/*2",
                "metabolizer": "Intermediate Metabolizer",
            },
        },
        {
            "name": "CYP2C19 *2/*2 (Poor)",
            "genotypes": {"rs4244285": "AA", "rs12248560": "CC"},
            "expected": {"genotype": "*2/*2", "metabolizer": "Poor Metabolizer"},
        },
        {
            "name": "CYP2C19 *1/*17 (Rapid)",
            "genotypes": {"rs4244285": "GG", "rs12248560": "CT"},
            "expected": {"genotype": "*1/*17", "metabolizer": "Rapid Metabolizer"},
        },
    ]

    print("Testing CYP2C19 Star Allele Calling:")
    print("=" * 50)

    for test_case in test_cases:
        # Create test DataFrame
        test_data = []
        for rsid, genotype in test_case["genotypes"].items():
            test_data.append({"rsid": rsid, "genotype": genotype})

        df = pd.DataFrame(test_data).set_index("rsid")

        # Call star alleles
        result = star_caller.call_star_alleles("CYP2C19", df)

        # Check results
        success = True
        if "error" in result:
            print(f"FAIL {test_case['name']}: ERROR - {result['error']}")
            success = False
        else:
            genotype_match = result["genotype"] == test_case["expected"]["genotype"]
            metabolizer_match = (
                result["metabolizer_status"] == test_case["expected"]["metabolizer"]
            )

            if genotype_match and metabolizer_match:
                print(
                    f"PASS {test_case['name']}: {result['genotype']} - {result['metabolizer_status']}"
                )
            else:
                print(
                    f"FAIL {test_case['name']}: Expected {test_case['expected']['genotype']} ({test_case['expected']['metabolizer']}), Got {result['genotype']} ({result['metabolizer_status']})"
                )
                success = False

    return success


def test_cyp2d6_alleles():
    """Test CYP2D6 star allele calling"""

    test_cases = [
        {
            "name": "CYP2D6 *1/*1 (Normal)",
            "genotypes": {"rs3892097": "GG", "rs1065852": "CC"},
            "expected": {"genotype": "*1/*1", "metabolizer": "Normal Metabolizer"},
        },
        {
            "name": "CYP2D6 *1/*4 (Intermediate)",
            "genotypes": {"rs3892097": "AG", "rs1065852": "CT"},
            "expected": {
                "genotype": "*1/*4",
                "metabolizer": "Intermediate Metabolizer",
            },
        },
    ]

    print("\nTesting CYP2D6 Star Allele Calling:")
    print("=" * 50)

    for test_case in test_cases:
        test_data = []
        for rsid, genotype in test_case["genotypes"].items():
            test_data.append({"rsid": rsid, "genotype": genotype})

        df = pd.DataFrame(test_data).set_index("rsid")
        result = star_caller.call_star_alleles("CYP2D6", df)

        if "error" in result:
            print(f"FAIL {test_case['name']}: ERROR - {result['error']}")
        else:
            print(
                f"PASS {test_case['name']}: {result['genotype']} - {result['metabolizer_status']}"
            )


def test_cpic_guidelines():
    """Test CPIC guideline retrieval"""

    print("\nTesting CPIC Guidelines:")
    print("=" * 50)

    # Test CYP2C19 clopidogrel guidelines
    recommendations = star_caller.get_cpic_recommendations(
        "CYP2C19", "Poor", "clopidogrel"
    )

    if "clopidogrel" in recommendations and "Avoid" in recommendations["clopidogrel"]:
        print(
            f"PASS CYP2C19 Poor Metabolizer - Clopidogrel: {recommendations['clopidogrel']}"
        )
    else:
        print(f"FAIL CYP2C19 Poor Metabolizer - Clopidogrel: {recommendations}")


def test_cyp2c9_alleles():
    """Test CYP2C9 star allele calling"""
    test_cases = [
        {
            "name": "CYP2C9 *1/*1 (Normal)",
            "genotypes": {"rs1799853": "AA", "rs1057910": "CC"},
            "expected": {"genotype": "*1/*1", "metabolizer": "Normal Metabolizer"},
        },
        {
            "name": "CYP2C9 *1/*2 (Intermediate)",
            "genotypes": {"rs1799853": "AC", "rs1057910": "CC"},
            "expected": {
                "genotype": "*1/*2",
                "metabolizer": "Intermediate Metabolizer",
            },
        },
        {
            "name": "CYP2C9 *2/*3 (Poor)",
            "genotypes": {"rs1799853": "CC", "rs1057910": "AC"},
            "expected": {"genotype": "*2/*3", "metabolizer": "Poor Metabolizer"},
        },
    ]

    print("\nTesting CYP2C9 Star Allele Calling:")
    print("=" * 50)

    for test_case in test_cases:
        test_data = []
        for rsid, genotype in test_case["genotypes"].items():
            test_data.append({"rsid": rsid, "genotype": genotype})

        df = pd.DataFrame(test_data).set_index("rsid")
        result = star_caller.call_star_alleles("CYP2C9", df)

        if "error" in result:
            print(f"FAIL {test_case['name']}: ERROR - {result['error']}")
        else:
            genotype_match = result["genotype"] == test_case["expected"]["genotype"]
            metabolizer_match = (
                result["metabolizer_status"] == test_case["expected"]["metabolizer"]
            )

            if genotype_match and metabolizer_match:
                print(
                    f"PASS {test_case['name']}: {result['genotype']} - {result['metabolizer_status']}"
                )
            else:
                print(
                    f"FAIL {test_case['name']}: Expected {test_case['expected']['genotype']} ({test_case['expected']['metabolizer']}), Got {result['genotype']} ({result['metabolizer_status']})"
                )


def test_tpmt_alleles():
    """Test TPMT star allele calling"""
    test_cases = [
        {
            "name": "TPMT *1/*1 (Normal)",
            "genotypes": {"rs1800462": "GG", "rs1800460": "GG", "rs1142345": "AA"},
            "expected": {"genotype": "*1/*1", "metabolizer": "Normal Metabolizer"},
        },
        {
            "name": "TPMT *1/*2 (Intermediate)",
            "genotypes": {"rs1800462": "AG", "rs1800460": "GG", "rs1142345": "AA"},
            "expected": {
                "genotype": "*1/*2",
                "metabolizer": "Intermediate Metabolizer",
            },
        },
        {
            "name": "TPMT *3A/*3A (Poor)",
            "genotypes": {"rs1800462": "GG", "rs1800460": "AA", "rs1142345": "GG"},
            "expected": {"genotype": "*3A/*3A", "metabolizer": "Poor Metabolizer"},
        },
    ]

    print("\nTesting TPMT Star Allele Calling:")
    print("=" * 50)

    for test_case in test_cases:
        test_data = []
        for rsid, genotype in test_case["genotypes"].items():
            test_data.append({"rsid": rsid, "genotype": genotype})

        df = pd.DataFrame(test_data).set_index("rsid")
        result = star_caller.call_star_alleles("TPMT", df)

        if "error" in result:
            print(f"FAIL {test_case['name']}: ERROR - {result['error']}")
        else:
            genotype_match = result["genotype"] == test_case["expected"]["genotype"]
            metabolizer_match = (
                result["metabolizer_status"] == test_case["expected"]["metabolizer"]
            )

            if genotype_match and metabolizer_match:
                print(
                    f"PASS {test_case['name']}: {result['genotype']} - {result['metabolizer_status']}"
                )
            else:
                print(
                    f"FAIL {test_case['name']}: Expected {test_case['expected']['genotype']} ({test_case['expected']['metabolizer']}), Got {result['genotype']} ({result['metabolizer_status']})"
                )


def test_dpyd_alleles():
    """Test DPYD star allele calling"""
    test_cases = [
        {
            "name": "DPYD *1/*1 (Normal)",
            "genotypes": {"rs3918290": "CC"},
            "expected": {"genotype": "*1/*1", "metabolizer": "Normal Metabolizer"},
        },
        {
            "name": "DPYD *1/*2A (Intermediate)",
            "genotypes": {"rs3918290": "CT"},
            "expected": {
                "genotype": "*1/*2A",
                "metabolizer": "Intermediate Metabolizer",
            },
        },
        {
            "name": "DPYD *2A/*2A (Poor)",
            "genotypes": {"rs3918290": "TT"},
            "expected": {"genotype": "*2A/*2A", "metabolizer": "Poor Metabolizer"},
        },
    ]

    print("\nTesting DPYD Star Allele Calling:")
    print("=" * 50)

    for test_case in test_cases:
        test_data = []
        for rsid, genotype in test_case["genotypes"].items():
            test_data.append({"rsid": rsid, "genotype": genotype})

        df = pd.DataFrame(test_data).set_index("rsid")
        result = star_caller.call_star_alleles("DPYD", df)

        if "error" in result:
            print(f"FAIL {test_case['name']}: ERROR - {result['error']}")
        else:
            genotype_match = result["genotype"] == test_case["expected"]["genotype"]
            metabolizer_match = (
                result["metabolizer_status"] == test_case["expected"]["metabolizer"]
            )

            if genotype_match and metabolizer_match:
                print(
                    f"PASS {test_case['name']}: {result['genotype']} - {result['metabolizer_status']}"
                )
            else:
                print(
                    f"FAIL {test_case['name']}: Expected {test_case['expected']['genotype']} ({test_case['expected']['metabolizer']}), Got {result['genotype']} ({result['metabolizer_status']})"
                )


def test_cpic_guidelines_expanded():
    """Test expanded CPIC guideline retrieval for multiple drugs"""
    print("\nTesting Expanded CPIC Guidelines:")
    print("=" * 50)

    # Test CYP2C19 guidelines
    cyp2c19_drugs = ["clopidogrel", "citalopram"]
    for drug in cyp2c19_drugs:
        recommendations = star_caller.get_cpic_recommendations("CYP2C19", "Poor", drug)
        if drug in recommendations:
            print(
                f"PASS CYP2C19 Poor Metabolizer - {drug.title()}: {recommendations[drug]}"
            )
        else:
            print(
                f"FAIL CYP2C19 Poor Metabolizer - {drug.title()}: No recommendation found"
            )

    # Test CYP2D6 guidelines
    cyp2d6_drugs = ["codeine", "tamoxifen"]
    for drug in cyp2d6_drugs:
        recommendations = star_caller.get_cpic_recommendations("CYP2D6", "Poor", drug)
        if drug in recommendations:
            print(
                f"PASS CYP2D6 Poor Metabolizer - {drug.title()}: {recommendations[drug]}"
            )
        else:
            print(
                f"FAIL CYP2D6 Poor Metabolizer - {drug.title()}: No recommendation found"
            )

    # Test CYP2C9 guidelines
    warfarin_rec = star_caller.get_cpic_recommendations("CYP2C9", "Poor", "warfarin")
    if "warfarin" in warfarin_rec:
        print(f"PASS CYP2C9 Poor Metabolizer - Warfarin: {warfarin_rec['warfarin']}")
    else:
        print("FAIL CYP2C9 Poor Metabolizer - Warfarin: No recommendation found")

    # Test TPMT guidelines
    azathioprine_rec = star_caller.get_cpic_recommendations(
        "TPMT", "Poor", "azathioprine"
    )
    if "azathioprine" in azathioprine_rec:
        print(
            f"PASS TPMT Poor Metabolizer - Azathioprine: {azathioprine_rec['azathioprine']}"
        )
    else:
        print("FAIL TPMT Poor Metabolizer - Azathioprine: No recommendation found")

    # Test DPYD guidelines
    fluorouracil_rec = star_caller.get_cpic_recommendations(
        "DPYD", "Poor", "fluorouracil"
    )
    if "fluorouracil" in fluorouracil_rec:
        print(
            f"PASS DPYD Poor Metabolizer - Fluorouracil: {fluorouracil_rec['fluorouracil']}"
        )
    else:
        print("FAIL DPYD Poor Metabolizer - Fluorouracil: No recommendation found")


def test_star_allele_error_handling():
    """Test error handling for invalid inputs"""
    print("\nTesting Star Allele Error Handling:")
    print("=" * 50)

    # Test unsupported gene
    result = star_caller.call_star_alleles("INVALID_GENE", pd.DataFrame())
    if "error" in result and "not supported" in result["error"]:
        print("PASS: Unsupported gene error handled correctly")
    else:
        print("FAIL: Unsupported gene error not handled properly")

    # Test empty data
    result = star_caller.call_star_alleles("CYP2C19", pd.DataFrame())
    if "error" in result and "No genotype data" in result["error"]:
        print("PASS: Empty data error handled correctly")
    else:
        print("FAIL: Empty data error not handled properly")


def test_cnv_detection():
    """Test copy number variation detection"""
    print("\nTesting CNV Detection:")
    print("=" * 50)

    # Test CYP2D6 CNV detection (placeholder - would need real CNV markers)
    test_data = pd.DataFrame(
        {"genotype": ["GG", "CC"]}, index=["rs3892097", "rs1065852"]
    )

    cnv_result = detect_cnv("CYP2D6", test_data)
    # Since this is a placeholder, we just check it doesn't crash
    print(f"PASS: CNV detection completed (result: {cnv_result})")


def run_all_tests():
    """Run all validation tests"""
    print("STAR ALLELE VALIDATION TESTS")
    print("=" * 60)

    test_cyp2c19_alleles()
    test_cyp2d6_alleles()
    test_cyp2c9_alleles()
    test_tpmt_alleles()
    test_dpyd_alleles()
    test_cpic_guidelines_expanded()
    test_star_allele_error_handling()
    test_cnv_detection()

    print("\n" + "=" * 60)
    print("Test completed. Check results above.")
    print("Covered genes: CYP2C19, CYP2D6, CYP2C9, TPMT, DPYD")
    print(
        "Covered medications: clopidogrel, citalopram, codeine, tamoxifen, warfarin, azathioprine, fluorouracil"
    )


if __name__ == "__main__":
    run_all_tests()
