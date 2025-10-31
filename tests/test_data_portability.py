#!/usr/bin/env python3
"""
Test script for Data Portability and Utility module.
"""

import os
import sys
import tempfile

import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pdf_generator import generate_pdf_report


def create_sample_dna_data():
    """Create sample DNA data for testing data portability."""
    # Synthetic data for testing purposes - not from real genetic data
    sample_data = {
        "rsID": [
            "rs1801133",
            "rs4988235",
            "rs4680",
            "rs429358",
            "rs7412",
            "rs3892097",
            "rs4244285",
            "rs1057910",
            "rs1800462",
            "rs1800460",
        ],
        "genotype": ["CT", "TT", "AG", "CT", "CC", "GG", "AG", "CT", "CT", "AG"],
        "chromosome": ["1", "2", "22", "19", "19", "22", "10", "10", "6", "2"],
        "position": [
            "11856378",
            "136608646",
            "19963748",
            "45411941",
            "45412079",
            "42522500",
            "96541615",
            "96702047",
            "18138995",
            "234668879",
        ],
    }
    df = pd.DataFrame(sample_data)
    df.set_index("rsID", inplace=True)
    return df


def test_csv_export():
    """Test CSV export functionality."""
    print("Testing CSV Export...")

    dna_data = create_sample_dna_data()
    dna_data_reset = dna_data.reset_index()

    csv_content = dna_data_reset.to_csv(index=False)

    # Verify CSV content
    assert "rsID" in csv_content, "rsID column missing from CSV"
    assert "genotype" in csv_content, "Genotype column missing from CSV"
    assert "chromosome" in csv_content, "Chromosome column missing from CSV"
    assert "position" in csv_content, "Position column missing from CSV"

    # Count lines (header + data rows)
    lines = csv_content.strip().split("\n")
    assert (
        len(lines) == len(dna_data) + 1
    ), f"Expected {len(dna_data) + 1} lines, got {len(lines)}"

    # Verify specific data
    assert "rs1801133" in csv_content, "Sample rsID not found in CSV"
    assert "CT" in csv_content, "Sample genotype not found in CSV"

    print("PASS: CSV export working correctly")
    return True


def test_tsv_export():
    """Test TSV export functionality."""
    print("Testing TSV Export...")

    dna_data = create_sample_dna_data()
    dna_data_reset = dna_data.reset_index()

    tsv_content = dna_data_reset.to_csv(index=False, sep="\t")

    # Verify TSV content
    assert "rsID" in tsv_content, "rsID column missing from TSV"
    assert "genotype" in tsv_content, "Genotype column missing from TSV"
    assert "\t" in tsv_content, "Tab separator not found in TSV"

    # Count lines
    lines = tsv_content.strip().split("\n")
    assert (
        len(lines) == len(dna_data) + 1
    ), f"Expected {len(dna_data) + 1} lines, got {len(lines)}"

    print("PASS: TSV export working correctly")
    return True


def test_json_export():
    """Test JSON export functionality."""
    print("Testing JSON Export...")

    dna_data = create_sample_dna_data()
    dna_data_reset = dna_data.reset_index()

    json_content = dna_data_reset.to_json(orient="records")

    # Verify JSON content
    assert "[" in json_content and "]" in json_content, "JSON array brackets missing"
    assert '"rsID"' in json_content, "rsID field missing from JSON"
    assert '"genotype"' in json_content, "Genotype field missing from JSON"

    # Parse JSON to verify structure
    import json

    parsed_data = json.loads(json_content)
    assert isinstance(parsed_data, list), "JSON should be a list"
    assert len(parsed_data) == len(
        dna_data
    ), f"Expected {len(dna_data)} records, got {len(parsed_data)}"

    # Check first record
    first_record = parsed_data[0]
    assert "rsID" in first_record, "rsID missing from first record"
    assert "genotype" in first_record, "Genotype missing from first record"

    print("PASS: JSON export working correctly")
    return True


def test_pdf_report_generation():
    """Test PDF report generation."""
    print("Testing PDF Report Generation...")

    dna_data = create_sample_dna_data()

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Generate PDF report
            generate_pdf_report({}, temp_dir, dna_data)

            # Check if PDF was created
            pdf_path = os.path.join(temp_dir, "Genomic_Health_Report.pdf")
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                assert file_size > 0, "PDF file is empty"
                print(
                    f"SUCCESS: PDF report generated successfully! Size: {file_size} bytes"
                )
                return True
            else:
                print("FAILURE: PDF file was not created")
                return False

        except Exception as e:
            print(f"FAILURE: Error during PDF generation: {str(e)}")
            import traceback

            traceback.print_exc()
            return False


def test_enhanced_pdf_report_generation():
    """Test enhanced PDF report generation."""
    print("Testing Enhanced PDF Report Generation...")

    dna_data = create_sample_dna_data()

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            from src.pdf_generator import generate_enhanced_pdf_report

            # Generate enhanced PDF report
            generate_enhanced_pdf_report(dna_data, temp_dir, "TEST_USER_001")

            # Check if PDF was created
            pdf_path = os.path.join(temp_dir, "Enhanced_Genomic_Health_Report.pdf")
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                assert file_size > 0, "Enhanced PDF file is empty"
                print(
                    f"SUCCESS: Enhanced PDF report generated successfully! Size: {file_size} bytes"
                )
                return True
            else:
                print("FAILURE: Enhanced PDF file was not created")
                return False

        except Exception as e:
            print(f"FAILURE: Error during enhanced PDF generation: {str(e)}")
            import traceback

            traceback.print_exc()
            return False


def test_data_export_completeness():
    """Test that all data is properly exported."""
    print("Testing Data Export Completeness...")

    dna_data = create_sample_dna_data()
    dna_data_reset = dna_data.reset_index()

    # Test CSV completeness
    csv_content = dna_data_reset.to_csv(index=False)
    for rsid in dna_data.index:
        assert rsid in csv_content, f"rsID {rsid} missing from CSV export"

    for genotype in dna_data["genotype"]:
        assert genotype in csv_content, f"Genotype {genotype} missing from CSV export"

    # Test JSON completeness
    json_content = dna_data_reset.to_json(orient="records")
    import json

    parsed_data = json.loads(json_content)

    exported_rsids = [record["rsID"] for record in parsed_data]
    assert set(exported_rsids) == set(dna_data.index), "rsID mismatch in JSON export"

    print("PASS: Data export completeness verified")
    return True


def test_export_format_consistency():
    """Test that different export formats contain consistent data."""
    print("Testing Export Format Consistency...")

    dna_data = create_sample_dna_data()
    dna_data_reset = dna_data.reset_index()

    # Get data from different formats
    csv_content = dna_data_reset.to_csv(index=False)
    tsv_content = dna_data_reset.to_csv(index=False, sep="\t")
    json_content = dna_data_reset.to_json(orient="records")

    # Parse JSON
    import json

    json_data = json.loads(json_content)

    # Check that all formats have the same number of records
    csv_lines = csv_content.strip().split("\n")
    tsv_lines = tsv_content.strip().split("\n")

    assert len(csv_lines) - 1 == len(json_data), "CSV and JSON record count mismatch"
    assert len(tsv_lines) - 1 == len(json_data), "TSV and JSON record count mismatch"

    # Check that key fields are present in all formats
    assert (
        "rsID" in csv_content and "rsID" in tsv_content
    ), "rsID field missing from CSV/TSV"
    assert all(
        "rsID" in record for record in json_data
    ), "rsID field missing from JSON records"

    print("PASS: Export format consistency verified")
    return True


def test_directory_creation():
    """Test that results directory is created if it doesn't exist."""
    print("Testing Directory Creation...")

    dna_data = create_sample_dna_data()

    with tempfile.TemporaryDirectory() as temp_base_dir:
        results_dir = os.path.join(temp_base_dir, "test_results")

        # Ensure directory doesn't exist initially
        assert not os.path.exists(
            results_dir
        ), "Test directory should not exist initially"

        try:
            # Generate PDF report (this should create the directory)
            generate_pdf_report({}, results_dir, dna_data)

            # Check if directory was created
            assert os.path.exists(results_dir), "Results directory was not created"

            # Check if PDF was created in the directory
            pdf_path = os.path.join(results_dir, "Genomic_Health_Report.pdf")
            assert os.path.exists(pdf_path), "PDF was not created in the new directory"

            print("PASS: Directory creation working correctly")
            return True

        except Exception as e:
            print(f"FAILURE: Error testing directory creation: {str(e)}")
            return False


def run_all_data_portability_tests():
    """Run all data portability and utility tests."""
    print("DATA PORTABILITY AND UTILITY TESTS")
    print("=" * 40)

    tests = [
        test_csv_export,
        test_tsv_export,
        test_json_export,
        test_pdf_report_generation,
        test_enhanced_pdf_report_generation,
        test_data_export_completeness,
        test_export_format_consistency,
        test_directory_creation,
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
        print("All data portability tests passed!")
        return True
    else:
        print("Some tests failed.")
        return False


if __name__ == "__main__":
    success = run_all_data_portability_tests()
    if not success:
        exit(1)
