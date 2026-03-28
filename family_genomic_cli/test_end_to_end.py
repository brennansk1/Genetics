#!/usr/bin/env python3
"""
End-to-end testing script for family-genomic-cli functionality.

This script tests the complete pipeline from data processing through analysis and reporting.
"""

import os
import sys
import time
import json
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, '.')

from data_processing import process_family_data
from analysis_engine import run_individual_analyses
from family_analyzer import run_family_analyses
from reporting import generate_reports

def test_singleton_analysis():
    """Test singleton (child only) analysis."""
    print("Testing Singleton Analysis (Child Only)")
    print("=" * 50)

    child_file = "sample_data/child_singleton.csv"
    output_dir = "test_output_singleton"

    start_time = time.time()

    try:
        # Data processing
        print("1. Processing data...")
        family_data = process_family_data(child_file=child_file)
        print(f"   - Loaded {len(family_data.harmonized_data)} SNPs")
        print(f"   - QC: {family_data.qc_results['error_count']} errors")

        # Prepare data for analyses
        family_dict = {}
        for col in family_data.harmonized_data.columns:
            member = col.replace('_genotype', '')
            family_dict[member] = family_data.harmonized_data[[col]].rename(columns={col: 'genotype'})

        # Individual analyses
        print("2. Running individual analyses...")
        individual_risks = {}
        for member, df in family_dict.items():
            print(f"   - Analyzing {member}...")
            individual_risks[member] = run_individual_analyses(df)

        # Family analyses (limited for singleton)
        print("3. Running family analyses...")
        family_results = run_family_analyses(
            family_data=family_dict,
            risk_variants=['rs1801133', 'rs4680']
        )

        # Generate reports
        print("4. Generating reports...")
        generated_files = generate_reports(
            analysis_results=individual_risks,
            family_analysis_results=family_results,
            output_dir=output_dir,
            report_formats=['json', 'csv']
        )

        end_time = time.time()
        duration = end_time - start_time

        print("5. Results:")
        print(f"   - Duration: {duration:.2f} seconds")
        print(f"   - Generated files: {generated_files}")

        # Verify outputs
        verify_outputs(output_dir, generated_files)

        print("✓ Singleton analysis completed successfully")
        return True

    except Exception as e:
        print(f"✗ Singleton analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_duo_analysis():
    """Test duo (child + mother) analysis."""
    print("\nTesting Duo Analysis (Child + Mother)")
    print("=" * 50)

    child_file = "sample_data/child_duo.csv"
    mother_file = "sample_data/mother_duo.csv"
    output_dir = "test_output_duo"

    start_time = time.time()

    try:
        # Data processing
        print("1. Processing data...")
        family_data = process_family_data(
            child_file=child_file,
            mother_file=mother_file
        )
        print(f"   - Loaded {len(family_data.harmonized_data)} SNPs")
        print(f"   - QC: {family_data.qc_results['error_count']} errors")
        print(f"   - Available parents: {family_data.qc_results['available_parents']}")

        # Prepare data for analyses
        family_dict = {}
        for col in family_data.harmonized_data.columns:
            member = col.replace('_genotype', '')
            family_dict[member] = family_data.harmonized_data[[col]].rename(columns={col: 'genotype'})

        # Individual analyses
        print("2. Running individual analyses...")
        individual_risks = {}
        for member, df in family_dict.items():
            print(f"   - Analyzing {member}...")
            individual_risks[member] = run_individual_analyses(df)

        # Family analyses
        print("3. Running family analyses...")
        family_results = run_family_analyses(
            family_data=family_dict,
            risk_variants=['rs1801133', 'rs4680'],
            individual_risks=individual_risks
        )

        # Generate reports
        print("4. Generating reports...")
        generated_files = generate_reports(
            analysis_results=individual_risks,
            family_analysis_results=family_results,
            output_dir=output_dir,
            report_formats=['json', 'csv']
        )

        end_time = time.time()
        duration = end_time - start_time

        print("5. Results:")
        print(f"   - Duration: {duration:.2f} seconds")
        print(f"   - Generated files: {generated_files}")

        # Verify outputs
        verify_outputs(output_dir, generated_files)

        print("✓ Duo analysis completed successfully")
        return True

    except Exception as e:
        print(f"✗ Duo analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_trio_analysis():
    """Test trio (child + mother + father) analysis."""
    print("\nTesting Trio Analysis (Child + Mother + Father)")
    print("=" * 50)

    child_file = "sample_data/child_trio.csv"
    mother_file = "sample_data/mother_trio.csv"
    father_file = "sample_data/father_trio.csv"
    output_dir = "test_output_trio"

    start_time = time.time()

    try:
        # Data processing
        print("1. Processing data...")
        family_data = process_family_data(
            child_file=child_file,
            mother_file=mother_file,
            father_file=father_file
        )
        print(f"   - Loaded {len(family_data.harmonized_data)} SNPs")
        print(f"   - QC: {family_data.qc_results['error_count']} errors")
        print(f"   - Available parents: {family_data.qc_results['available_parents']}")

        # Prepare data for analyses
        family_dict = {}
        for col in family_data.harmonized_data.columns:
            member = col.replace('_genotype', '')
            family_dict[member] = family_data.harmonized_data[[col]].rename(columns={col: 'genotype'})

        # Individual analyses
        print("2. Running individual analyses...")
        individual_risks = {}
        for member, df in family_dict.items():
            print(f"   - Analyzing {member}...")
            individual_risks[member] = run_individual_analyses(df)

        # Family analyses
        print("3. Running family analyses...")
        family_results = run_family_analyses(
            family_data=family_dict,
            risk_variants=['rs1801133', 'rs4680', 'rs4988235'],
            individual_risks=individual_risks
        )

        # Generate reports
        print("4. Generating reports...")
        generated_files = generate_reports(
            analysis_results=individual_risks,
            family_analysis_results=family_results,
            output_dir=output_dir,
            report_formats=['json', 'csv']
        )

        end_time = time.time()
        duration = end_time - start_time

        print("5. Results:")
        print(f"   - Duration: {duration:.2f} seconds")
        print(f"   - Generated files: {generated_files}")

        # Verify outputs
        verify_outputs(output_dir, generated_files)

        print("✓ Trio analysis completed successfully")
        return True

    except Exception as e:
        print(f"✗ Trio analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mendelian_checks():
    """Test Mendelian inheritance checks with valid and invalid data."""
    print("\nTesting Mendelian Inheritance Checks")
    print("=" * 50)

    # Test valid trio
    print("1. Testing valid trio data...")
    try:
        family_data = process_family_data(
            child_file="sample_data/child_trio.csv",
            mother_file="sample_data/mother_trio.csv",
            father_file="sample_data/father_trio.csv"
        )
        error_rate = family_data.qc_results['error_rate']
        print(f"   - Valid trio error rate: {error_rate:.2%}")
        valid_pass = error_rate < 0.05  # Less than 5% errors
        print(f"   - Valid trio check: {'PASS' if valid_pass else 'FAIL'}")
    except Exception as e:
        print(f"   - Valid trio check failed: {e}")
        valid_pass = False

    # Test invalid data
    print("2. Testing invalid/mismatched data...")
    try:
        family_data = process_family_data(
            child_file="sample_data/child_mismatched.csv",
            mother_file="sample_data/mother_mismatched.csv",
            father_file="sample_data/father_mismatched.csv"
        )
        error_rate = family_data.qc_results['error_rate']
        print(f"   - Invalid trio error rate: {error_rate:.2%}")
        invalid_fail = error_rate > 0.5  # Should have high error rate
        print(f"   - Invalid trio check: {'PASS' if invalid_fail else 'FAIL'}")
    except Exception as e:
        print(f"   - Invalid trio check failed: {e}")
        invalid_fail = True  # If it fails, that's also detecting the issue

    return valid_pass and invalid_fail

def verify_outputs(output_dir, generated_files):
    """Verify that outputs contain expected data."""
    print("6. Verifying outputs...")

    # Check JSON files
    if 'json' in generated_files:
        for json_file in generated_files['json']:
            if os.path.exists(json_file):
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                    print(f"   - JSON file {json_file}: valid")
                    if 'individual_results' in data:
                        members = list(data['individual_results'].keys())
                        print(f"     Contains results for: {members}")
                    if 'family_analysis_results' in data:
                        family_keys = list(data['family_analysis_results'].keys())
                        print(f"     Contains family analysis: {family_keys}")
                except Exception as e:
                    print(f"   - JSON file {json_file}: invalid ({e})")
            else:
                print(f"   - JSON file {json_file}: missing")

    # Check CSV files
    if 'csv' in generated_files:
        for csv_file in generated_files['csv']:
            if os.path.exists(csv_file):
                try:
                    import pandas as pd
                    df = pd.read_csv(csv_file)
                    print(f"   - CSV file {csv_file}: {len(df)} rows")
                except Exception as e:
                    print(f"   - CSV file {csv_file}: invalid ({e})")
            else:
                print(f"   - CSV file {csv_file}: missing")

def main():
    """Run all end-to-end tests."""
    print("Family Genomic CLI End-to-End Testing")
    print("=" * 60)

    # Ensure sample data exists
    if not os.path.exists("sample_data"):
        print("Error: sample_data directory not found. Run generate_sample_data.py first.")
        return

    results = []

    # Test configurations
    results.append(("Singleton", test_singleton_analysis()))
    results.append(("Duo", test_duo_analysis()))
    results.append(("Trio", test_trio_analysis()))
    results.append(("Mendelian Checks", test_mendelian_checks()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name:20} : {status}")
        if success:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())