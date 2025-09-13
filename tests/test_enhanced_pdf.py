#!/usr/bin/env python3
"""
Test script for the enhanced PDF report generator.
"""

import pandas as pd
import tempfile
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pdf_generator import generate_enhanced_pdf_report

def create_sample_dna_data():
    """Create sample DNA data for testing."""
    sample_data = {
        'rsid': ['rs10757274', 'rs10757278', 'rs1333049', 'rs2383206'],
        'genotype': ['GG', 'GG', 'CC', 'AA'],
        'chromosome': ['9', '9', '9', '9'],
        'position': ['22098599', '22100145', '22125205', '22125205']
    }
    df = pd.DataFrame(sample_data)
    df.set_index('rsid', inplace=True)
    return df

def test_enhanced_pdf_generation():
    """Test the enhanced PDF generation functionality."""
    print("Testing Enhanced PDF Report Generation...")

    # Create sample DNA data
    dna_data = create_sample_dna_data()
    print(f"Created sample DNA data with {len(dna_data)} SNPs")

    # Create temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary directory: {temp_dir}")

        try:
            # Generate the enhanced PDF report
            generate_enhanced_pdf_report(dna_data, temp_dir, "TEST_USER_001")

            # Check if PDF was created
            pdf_path = os.path.join(temp_dir, "Enhanced_Genomic_Health_Report.pdf")
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                print(f"SUCCESS: Enhanced PDF report generated successfully!")
                print(f"   File: {pdf_path}")
                print(f"   Size: {file_size} bytes")
                return True
            else:
                print("FAILURE: PDF file was not created")
                return False

        except Exception as e:
            print(f"FAILURE: Error during PDF generation: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_enhanced_pdf_generation()
    if success:
        print("\nAll tests passed! The enhanced PDF generator is working correctly.")
    else:
        print("\nTests failed. Please check the error messages above.")
        exit(1)