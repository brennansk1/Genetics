#!/usr/bin/env python3
"""
End-to-end integration tests for family genomic CLI pipeline.

Tests the complete workflow from input genotype files through data processing,
individual analyses, family analyses, and report generation.
"""

import os
import tempfile
import shutil
import pytest
import pandas as pd
from pathlib import Path

# Import modules under test
from family_genomic_cli.data_processing import process_family_data, FamilyData
from family_genomic_cli.analysis_engine import run_individual_analyses
from family_genomic_cli.family_analyzer import run_family_analyses
from family_genomic_cli.reporting import generate_reports


class TestIntegration:
    """Integration tests for the complete family genomic analysis pipeline."""

    @pytest.fixture(scope="class")
    def temp_dir(self):
        """Create temporary directory for test files."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)

    @pytest.fixture(scope="class")
    def mock_genotype_data(self, temp_dir):
        """Create mock genotype data files for different family configurations."""
        data_files = {}

        # Common SNPs for testing
        common_snps = [
            ('rs1801133', 'MTHFR'),  # Folate metabolism
            ('rs4680', 'COMT'),     # Caffeine metabolism
            ('rs4988235', 'MCM6'),  # Lactose tolerance
            ('rs12785878', 'SLC45A2'),  # Vitamin D
            ('rs1800562', 'HFE'),   # Hemochromatosis
            ('rs11591147', 'CYP2C19'),  # Drug metabolism
            ('rs3892097', 'CYP2D6'),    # Drug metabolism
            ('rs9923231', 'VKORC1'),   # Warfarin response
            ('rs1799853', 'CYP2B6'),    # Drug metabolism
            ('rs776746', 'CYP3A5'),     # Drug metabolism
        ]

        # Trio configuration (child + both parents)
        trio_data = {
            'child': [
                ('rs1801133', 'CT'),  # Heterozygous
                ('rs4680', 'AA'),     # Homozygous
                ('rs4988235', 'TT'),  # Homozygous
                ('rs12785878', 'CC'), # Homozygous
                ('rs1800562', 'GG'),  # Homozygous
                ('rs11591147', 'GG'), # Homozygous
                ('rs3892097', 'TT'),  # Homozygous
                ('rs9923231', 'CC'),  # Homozygous
                ('rs1799853', 'GG'),  # Homozygous
                ('rs776746', 'AA'),   # Homozygous
            ],
            'mother': [
                ('rs1801133', 'CT'),  # Heterozygous
                ('rs4680', 'AG'),     # Heterozygous
                ('rs4988235', 'TT'),  # Homozygous
                ('rs12785878', 'CT'), # Heterozygous
                ('rs1800562', 'GG'),  # Homozygous
                ('rs11591147', 'AG'), # Heterozygous
                ('rs3892097', 'TT'),  # Homozygous
                ('rs9923231', 'CT'),  # Heterozygous
                ('rs1799853', 'GG'),  # Homozygous
                ('rs776746', 'GG'),   # Homozygous
            ],
            'father': [
                ('rs1801133', 'TT'),  # Homozygous
                ('rs4680', 'GG'),     # Homozygous
                ('rs4988235', 'CC'),  # Homozygous
                ('rs12785878', 'TT'), # Homozygous
                ('rs1800562', 'AG'),  # Heterozygous
                ('rs11591147', 'GG'), # Homozygous
                ('rs3892097', 'CC'),  # Homozygous
                ('rs9923231', 'CC'),  # Homozygous
                ('rs1799853', 'GT'),  # Heterozygous
                ('rs776746', 'AA'),   # Homozygous
            ]
        }

        # Create trio files
        for member, genotypes in trio_data.items():
            file_path = os.path.join(temp_dir, f'{member}_trio.csv')
            with open(file_path, 'w') as f:
                f.write('rsid,genotype\n')
                for rsid, genotype in genotypes:
                    f.write(f'{rsid},{genotype}\n')
            data_files[f'{member}_trio'] = file_path

        # Duo configuration (child + mother only)
        duo_data = {
            'child': trio_data['child'],
            'mother': trio_data['mother']
        }

        for member, genotypes in duo_data.items():
            file_path = os.path.join(temp_dir, f'{member}_duo.csv')
            with open(file_path, 'w') as f:
                f.write('rsid,genotype\n')
                for rsid, genotype in genotypes:
                    f.write(f'{rsid},{genotype}\n')
            data_files[f'{member}_duo'] = file_path

        # Singleton configuration (child only)
        singleton_data = {'child': trio_data['child']}
        file_path = os.path.join(temp_dir, 'child_singleton.csv')
        with open(file_path, 'w') as f:
            f.write('rsid,genotype\n')
            for rsid, genotype in singleton_data['child']:
                f.write(f'{rsid},{genotype}\n')
        data_files['child_singleton'] = file_path

        return data_files

    def test_data_processing_trio(self, mock_genotype_data):
        """Test data processing pipeline with trio configuration."""
        child_file = mock_genotype_data['child_trio']
        mother_file = mock_genotype_data['mother_trio']
        father_file = mock_genotype_data['father_trio']

        # Process family data
        family_data = process_family_data(
            child_file=child_file,
            mother_file=mother_file,
            father_file=father_file
        )

        # Verify FamilyData structure
        assert isinstance(family_data, FamilyData)
        assert isinstance(family_data.harmonized_data, pd.DataFrame)
        assert isinstance(family_data.qc_results, dict)
        assert isinstance(family_data.validation, dict)

        # Verify harmonized data
        assert len(family_data.harmonized_data) > 0
        expected_columns = ['child_genotype', 'mother_genotype', 'father_genotype']
        for col in expected_columns:
            assert col in family_data.harmonized_data.columns

        # Verify QC results
        assert 'total_snps' in family_data.qc_results
        assert 'error_count' in family_data.qc_results
        assert 'available_parents' in family_data.qc_results
        assert family_data.qc_results['available_parents'] == ['mother', 'father']

        # Verify validation
        assert 'valid_formats' in family_data.validation
        assert 'sufficient_overlap' in family_data.validation
        assert family_data.validation['valid_formats'] is True

    def test_data_processing_duo(self, mock_genotype_data):
        """Test data processing pipeline with duo configuration."""
        child_file = mock_genotype_data['child_duo']
        mother_file = mock_genotype_data['mother_duo']

        family_data = process_family_data(
            child_file=child_file,
            mother_file=mother_file
        )

        assert isinstance(family_data, FamilyData)
        assert len(family_data.harmonized_data) > 0
        expected_columns = ['child_genotype', 'mother_genotype']
        for col in expected_columns:
            assert col in family_data.harmonized_data.columns

        assert family_data.qc_results['available_parents'] == ['mother']

    def test_data_processing_singleton(self, mock_genotype_data):
        """Test data processing pipeline with singleton configuration."""
        child_file = mock_genotype_data['child_singleton']

        family_data = process_family_data(child_file=child_file)

        assert isinstance(family_data, FamilyData)
        assert len(family_data.harmonized_data) > 0
        expected_columns = ['child_genotype']
        for col in expected_columns:
            assert col in family_data.harmonized_data.columns

        assert family_data.qc_results['available_parents'] == []

    def test_individual_analyses(self, mock_genotype_data):
        """Test individual genomic analyses."""
        # Load child data for individual analysis
        from family_genomic_cli.copied_modules.utils import parse_dna_file
        child_data = parse_dna_file(mock_genotype_data['child_trio'])

        # Run individual analyses
        results = run_individual_analyses(child_data)

        # Verify results structure
        assert isinstance(results, dict)
        expected_keys = [
            'clinical_risk_screening',
            'pharmacogenomics',
            'polygenic_risk_scores',
            'wellness_traits',
            'carrier_status'
        ]

        for key in expected_keys:
            assert key in results
            # Results should not be error dicts (unless expected failures)
            if isinstance(results[key], dict) and 'error' in results[key]:
                # Allow expected errors for missing data
                continue
            assert isinstance(results[key], dict)

    def test_family_analyses(self, mock_genotype_data):
        """Test family-level analyses."""
        # Process family data first
        child_file = mock_genotype_data['child_trio']
        mother_file = mock_genotype_data['mother_trio']
        father_file = mock_genotype_data['father_trio']

        family_data = process_family_data(
            child_file=child_file,
            mother_file=mother_file,
            father_file=father_file
        )

        # Convert harmonized data back to dict format for family analyzer
        family_dict = {}
        for col in family_data.harmonized_data.columns:
            member = col.replace('_genotype', '')
            family_dict[member] = family_data.harmonized_data[[col]].rename(columns={col: 'genotype'})

        # Run individual analyses for risk aggregation
        individual_risks = {}
        for member, df in family_dict.items():
            individual_risks[member] = run_individual_analyses(df)

        # Run family analyses
        family_results = run_family_analyses(
            family_data=family_dict,
            risk_variants=['rs1801133', 'rs4680'],  # Test variant tracing
            individual_risks=individual_risks
        )

        # Verify results structure
        assert isinstance(family_results, dict)
        expected_keys = [
            'relationship_verification',
            'variant_origins',
            'shared_risks'
        ]

        for key in expected_keys:
            assert key in family_results
            assert isinstance(family_results[key], dict)

        # Verify relationship verification
        rel_verify = family_results['relationship_verification']
        assert 'family_configuration' in rel_verify
        assert 'type' in rel_verify['family_configuration']

    def test_reporting_generation(self, temp_dir, mock_genotype_data):
        """Test report generation."""
        # Process data and run analyses
        child_file = mock_genotype_data['child_trio']
        mother_file = mock_genotype_data['mother_trio']
        father_file = mock_genotype_data['father_trio']

        family_data = process_family_data(
            child_file=child_file,
            mother_file=mother_file,
            father_file=father_file
        )

        family_dict = {}
        for col in family_data.harmonized_data.columns:
            member = col.replace('_genotype', '')
            family_dict[member] = family_data.harmonized_data[[col]].rename(columns={col: 'genotype'})

        # Run analyses
        individual_risks = {}
        for member, df in family_dict.items():
            individual_risks[member] = run_individual_analyses(df)

        family_results = run_family_analyses(
            family_data=family_dict,
            individual_risks=individual_risks
        )

        # Generate reports
        output_dir = os.path.join(temp_dir, 'reports')
        generated_files = generate_reports(
            analysis_results=individual_risks,
            family_analysis_results=family_results,
            output_dir=output_dir,
            report_formats=['json', 'csv'],  # Skip PDF to avoid dependencies
            family_name='TestFamily'
        )

        # Verify report generation
        assert isinstance(generated_files, dict)
        assert 'json' in generated_files
        assert 'csv' in generated_files

        # Check that files were created
        for file_list in generated_files.values():
            for file_path in file_list:
                assert os.path.exists(file_path)
                assert os.path.getsize(file_path) > 0

    def test_end_to_end_pipeline(self, temp_dir, mock_genotype_data):
        """Test complete end-to-end pipeline from files to reports."""
        # Input files
        child_file = mock_genotype_data['child_trio']
        mother_file = mock_genotype_data['mother_trio']
        father_file = mock_genotype_data['father_trio']

        # Step 1: Data Processing
        family_data = process_family_data(
            child_file=child_file,
            mother_file=mother_file,
            father_file=father_file
        )

        # Step 2: Prepare data for analyses
        family_dict = {}
        for col in family_data.harmonized_data.columns:
            member = col.replace('_genotype', '')
            family_dict[member] = family_data.harmonized_data[[col]].rename(columns={col: 'genotype'})

        # Step 3: Individual Analyses
        individual_risks = {}
        for member, df in family_dict.items():
            individual_risks[member] = run_individual_analyses(df)

        # Step 4: Family Analyses
        family_results = run_family_analyses(
            family_data=family_dict,
            risk_variants=['rs1801133', 'rs4680', 'rs4988235'],
            gene_variants={'MTHFR': ['rs1801133']},
            individual_risks=individual_risks
        )

        # Step 5: Report Generation
        output_dir = os.path.join(temp_dir, 'e2e_reports')
        generated_files = generate_reports(
            analysis_results=individual_risks,
            family_analysis_results=family_results,
            output_dir=output_dir,
            report_formats=['json'],
            family_name='EndToEndTest'
        )

        # Verify complete pipeline success
        assert len(generated_files['json']) > 0
        json_file = generated_files['json'][0]
        assert os.path.exists(json_file)

        # Verify JSON content
        import json
        with open(json_file, 'r') as f:
            data = json.load(f)

        assert 'report_type' in data
        assert 'individual_results' in data
        assert 'family_analysis_results' in data
        assert data['report_type'] == 'family_genomic_analysis'

        # Verify individual results are present
        for member in ['child', 'mother', 'father']:
            assert member in data['individual_results']
            assert isinstance(data['individual_results'][member], dict)

        # Verify family results are present
        assert 'relationship_verification' in data['family_analysis_results']
        assert 'shared_risks' in data['family_analysis_results']

    def test_pipeline_error_handling(self, temp_dir):
        """Test pipeline error handling with invalid data."""
        # Create invalid file
        invalid_file = os.path.join(temp_dir, 'invalid.csv')
        with open(invalid_file, 'w') as f:
            f.write('invalid,data\n')
            f.write('no,genotype,column\n')

        # Should handle errors gracefully
        with pytest.raises(Exception):
            process_family_data(child_file=invalid_file)

    def test_configuration_variations(self, mock_genotype_data):
        """Test different family configurations work correctly."""
        configurations = [
            # Trio
            {
                'child': mock_genotype_data['child_trio'],
                'mother': mock_genotype_data['mother_trio'],
                'father': mock_genotype_data['father_trio'],
                'expected_parents': ['mother', 'father']
            },
            # Duo (mother only)
            {
                'child': mock_genotype_data['child_duo'],
                'mother': mock_genotype_data['mother_duo'],
                'expected_parents': ['mother']
            },
            # Singleton
            {
                'child': mock_genotype_data['child_singleton'],
                'expected_parents': []
            }
        ]

        for config in configurations:
            family_data = process_family_data(
                child_file=config['child'],
                mother_file=config.get('mother'),
                father_file=config.get('father')
            )

            assert family_data.qc_results['available_parents'] == config['expected_parents']

            # Run analyses for this configuration
            family_dict = {}
            for col in family_data.harmonized_data.columns:
                member = col.replace('_genotype', '')
                family_dict[member] = family_data.harmonized_data[[col]].rename(columns={col: 'genotype'})

            individual_risks = {}
            for member, df in family_dict.items():
                individual_risks[member] = run_individual_analyses(df)

            # Should complete without errors
            assert len(individual_risks) == len(family_dict)