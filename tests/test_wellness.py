#!/usr/bin/env python3
"""
Test script for Holistic Wellness & Trait Profile module.
"""

import os
import sys

import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import analyze_wellness_snps


def create_sample_dna_data():
    """Create sample DNA data for testing wellness analyses."""
    # Synthetic data for testing purposes - not from real genetic data
    # Include SNPs from wellness analysis
    sample_data = {
        "rsID": [
            "rs4988235",  # Lactose Tolerance
            "rs762551",  # Caffeine Metabolism
            "rs601338",  # Vitamin B12 (FUT2)
            "rs1801133",  # Vitamin B12 (MTHFR)
            "rs7041",  # Vitamin D (GC)
            "rs4588",  # Vitamin D (GC)
            "rs2282679",  # Vitamin D (GC)
            "rs10741657",  # Vitamin D (CYP2R1)
            "rs1815739",  # Athletic Performance (ACTN3)
            "rs4680",  # Methylation (COMT)
            "rs7726159",  # Telomere Length (TERC)
            "rs2736100",  # Telomere Length (TERT)
            "rs11191865",  # Telomere Length (OBFC1)
            "rs2802292",  # Longevity (FOXO3)
            "rs429358",  # Longevity (APOE e2)
            "rs7412",  # Longevity (APOE e2)
            "rs1801260",  # Chronotype (CLOCK)
            "rs11063118",  # Chronotype (RGS16)
            "rs11252394",  # Insomnia Risk (MEIS1)
            "rs713598",  # Bitter Taste Perception
            "rs1726866",  # Bitter Taste Perception
            "rs10246939",  # Bitter Taste Perception
            "rs10427255",  # Photic Sneeze Reflex
            "rs4481887",  # Asparagus Metabolite Detection
        ],
        "genotype": [
            "CT",  # Lactase non-persistent
            "CT",  # Intermediate caffeine metabolizer
            "AG",  # Reduced B12
            "CT",  # Intermediate B12
            "CT",  # Intermediate Vitamin D
            "AG",  # Intermediate Vitamin D
            "CT",  # Intermediate Vitamin D
            "CT",  # Intermediate Vitamin D
            "CT",  # Mixed athletic performance
            "AG",  # Intermediate COMT
            "CT",  # Intermediate telomere
            "CT",  # Intermediate telomere
            "CT",  # Intermediate telomere
            "AG",  # Intermediate longevity
            "CT",  # APOE e4 carrier
            "CC",  # APOE e3/e3
            "CT",  # Intermediate chronotype
            "CT",  # Intermediate chronotype
            "CT",  # Intermediate insomnia risk
            "CT",  # Taster
            "GA",  # Taster
            "CT",  # Taster
            "CT",  # Carrier for photic sneeze
            "AG",  # Detector
        ],
        "chromosome": [
            "2",
            "15",
            "19",
            "1",
            "4",
            "4",
            "4",
            "11",
            "11",
            "22",
            "3",
            "5",
            "10",
            "6",
            "19",
            "19",
            "4",
            "1",
            "6",
            "7",
            "7",
            "7",
            "2",
            "1",
        ],
        "position": [
            "136608646",
            "74720201",
            "49206140",
            "11856378",
            "71752687",
            "71779229",
            "71779229",
            "14897199",
            "66560624",
            "19963748",
            "169482053",
            "1286516",
            "104887686",
            "108997995",
            "45411941",
            "45412079",
            "55462308",
            "182709906",
            "41934881",
            "141672861",
            "141672861",
            "141672861",
            "144807245",
            "248049508",
        ],
    }
    df = pd.DataFrame(sample_data)
    df.set_index("rsID", inplace=True)
    return df


def test_nutritional_genetics_profile():
    """Test nutritional genetics profile analysis."""
    print("Testing Nutritional Genetics Profile...")
    dna_data = create_sample_dna_data()

    wellness_results = analyze_wellness_snps(dna_data)

    # Check nutritional traits
    nutritional_traits = [
        "Lactose Tolerance",
        "Caffeine Metabolism",
        "Vitamin B12",
        "Vitamin D",
    ]
    found_traits = 0

    for rsid, data in wellness_results.items():
        if data["name"] in nutritional_traits:
            found_traits += 1
            assert "genotype" in data, f"Genotype missing for {rsid}"
            assert "interp" in data, f"Interpretation missing for {rsid}"
            if data["genotype"] != "Not Found":
                interpretation = "Not determined"
                if "interp" in data and data["genotype"] in data["interp"]:
                    interpretation = data["interp"][data["genotype"]]
                assert (
                    interpretation != "Not determined"
                ), f"No interpretation found for {data['name']} genotype {data['genotype']}"

    assert found_traits > 0, "No nutritional traits found in results"
    print(f"PASS: Found and analyzed {found_traits} nutritional traits")
    return True


def test_fitness_genetics_profile():
    """Test fitness genetics profile analysis."""
    print("Testing Fitness Genetics Profile...")
    dna_data = create_sample_dna_data()

    wellness_results = analyze_wellness_snps(dna_data)

    # Check fitness traits
    fitness_found = False
    for rsid, data in wellness_results.items():
        if data["name"] == "Athletic Performance (Power/Sprint vs. Endurance)":
            fitness_found = True
            assert "genotype" in data, f"Genotype missing for {rsid}"
            assert "interp" in data, f"Interpretation missing for {rsid}"
            if data["genotype"] != "Not Found":
                interpretation = "Not determined"
                if "interp" in data and data["genotype"] in data["interp"]:
                    interpretation = data["interp"][data["genotype"]]
                assert (
                    interpretation != "Not determined"
                ), f"No interpretation found for athletic performance genotype {data['genotype']}"
            break

    assert fitness_found, "Athletic performance trait not found"
    print("PASS: Athletic performance genetics analyzed correctly")
    return True


def test_holistic_pathway_analysis():
    """Test holistic pathway analysis."""
    print("Testing Holistic Pathway Analysis...")
    dna_data = create_sample_dna_data()

    wellness_results = analyze_wellness_snps(dna_data)

    # Check methylation/COMT
    comt_found = False
    for rsid, data in wellness_results.items():
        if data["name"] == "Methylation (COMT)":
            comt_found = True
            assert "genotype" in data, f"Genotype missing for {rsid}"
            assert "interp" in data, f"Interpretation missing for {rsid}"
            if data["genotype"] != "Not Found":
                interpretation = "Not determined"
                if "interp" in data and data["genotype"] in data["interp"]:
                    interpretation = data["interp"][data["genotype"]]
                assert (
                    interpretation != "Not determined"
                ), f"No interpretation found for COMT genotype {data['genotype']}"
            break

    assert comt_found, "COMT methylation trait not found"
    print("PASS: Holistic pathway analysis working correctly")
    return True


def test_longevity_cellular_aging():
    """Test longevity and cellular aging markers."""
    print("Testing Longevity and Cellular Aging Markers...")
    dna_data = create_sample_dna_data()

    wellness_results = analyze_wellness_snps(dna_data)

    longevity_traits = ["Telomere Length", "Longevity"]
    found_longevity = 0

    for rsid, data in wellness_results.items():
        if any(trait in data["name"] for trait in longevity_traits):
            found_longevity += 1
            assert "genotype" in data, f"Genotype missing for {rsid}"
            assert "interp" in data, f"Interpretation missing for {rsid}"

    assert found_longevity > 0, "No longevity traits found"
    print(f"PASS: Found and analyzed {found_longevity} longevity traits")
    return True


def test_chronobiology_sleep():
    """Test chronobiology and sleep traits."""
    print("Testing Chronobiology and Sleep Traits...")
    dna_data = create_sample_dna_data()

    wellness_results = analyze_wellness_snps(dna_data)

    chrono_traits = ["Chronotype", "Insomnia Risk"]
    found_chrono = 0

    for rsid, data in wellness_results.items():
        if any(trait in data["name"] for trait in chrono_traits):
            found_chrono += 1
            assert "genotype" in data, f"Genotype missing for {rsid}"
            assert "interp" in data, f"Interpretation missing for {rsid}"

    assert found_chrono > 0, "No chronobiology traits found"
    print(f"PASS: Found and analyzed {found_chrono} chronobiology traits")
    return True


def test_quirky_trait_report():
    """Test quirky trait report."""
    print("Testing Quirky Trait Report...")
    dna_data = create_sample_dna_data()

    wellness_results = analyze_wellness_snps(dna_data)

    quirky_traits = [
        "Bitter Taste Perception",
        "Photic Sneeze Reflex",
        "Asparagus Metabolite Detection",
    ]
    found_quirky = 0

    for rsid, data in wellness_results.items():
        if data["name"] in quirky_traits:
            found_quirky += 1
            assert "genotype" in data, f"Genotype missing for {rsid}"
            assert "interp" in data, f"Interpretation missing for {rsid}"
            if data["genotype"] != "Not Found":
                interpretation = "Not determined"
                if "interp" in data and data["genotype"] in data["interp"]:
                    interpretation = data["interp"][data["genotype"]]
                assert (
                    interpretation != "Not determined"
                ), f"No interpretation found for {data['name']} genotype {data['genotype']}"

    assert found_quirky > 0, "No quirky traits found"
    print(f"PASS: Found and analyzed {found_quirky} quirky traits")
    return True


def test_wellness_data_completeness():
    """Test that wellness analysis handles missing data appropriately."""
    print("Testing Wellness Data Completeness...")
    dna_data = create_sample_dna_data()

    # Remove some SNPs to test missing data handling
    incomplete_data = dna_data.drop(
        ["rs4988235", "rs762551"]
    )  # Remove lactose and caffeine SNPs

    wellness_results = analyze_wellness_snps(incomplete_data)

    # Check that missing SNPs are marked as "Not Found"
    assert (
        wellness_results["rs4988235"]["genotype"] == "Not Found"
    ), "Missing SNP not handled correctly"
    assert (
        wellness_results["rs762551"]["genotype"] == "Not Found"
    ), "Missing SNP not handled correctly"

    # Check that present SNPs still work
    assert (
        wellness_results["rs1801133"]["genotype"] != "Not Found"
    ), "Present SNP not found"

    print("PASS: Missing data handled correctly")
    return True


def run_all_wellness_tests():
    """Run all wellness and trait profile tests."""
    print("HOLISTIC WELLNESS & TRAIT PROFILE TESTS")
    print("=" * 50)

    tests = [
        test_nutritional_genetics_profile,
        test_fitness_genetics_profile,
        test_holistic_pathway_analysis,
        test_longevity_cellular_aging,
        test_chronobiology_sleep,
        test_quirky_trait_report,
        test_wellness_data_completeness,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__} - {str(e)}")

    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}/{total}")
    if passed == total:
        print("All wellness tests passed!")
        return True
    else:
        print("Some tests failed.")
        return False


if __name__ == "__main__":
    success = run_all_wellness_tests()
    if not success:
        exit(1)
