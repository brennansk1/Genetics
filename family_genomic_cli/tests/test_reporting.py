import pytest
import json
import pandas as pd
import os
import tempfile
from unittest.mock import patch, MagicMock
from family_genomic_cli.reporting import (
    generate_individual_pdf_report,
    generate_family_pdf_report,
    generate_json_report,
    generate_csv_report,
    generate_reports,
    _extract_key_findings,
    _calculate_health_score,
    _extract_family_key_findings,
    _calculate_family_health_score
)


@pytest.fixture
def mock_individual_analysis_results():
    """Mock individual analysis results."""
    return {
        'dna_data': pd.DataFrame({
            'genotype': ['AA', 'AT', 'GG', 'CC'],
            'rsID': ['rs1', 'rs2', 'rs3', 'rs4']
        }),
        'polygenic_risk_scores': {
            'Coronary Artery Disease': {'percentile': 85, 'score': 1.2, 'risk_level': 'High'},
            'Type 2 Diabetes': {'percentile': 60, 'score': 0.8, 'risk_level': 'Moderate'},
            'Breast Cancer': {'percentile': 75, 'score': 1.1, 'risk_level': 'High'}
        },
        'carrier_status': [
            {'rsID': 'rs5', 'Condition': 'Cystic Fibrosis', 'Status': 'Carrier'},
            {'rsID': 'rs6', 'Condition': 'Sickle Cell', 'Status': 'Normal'}
        ],
        'pharmacogenomics': [
            {'Gene': 'CYP2D6', 'Genotype': '*1/*4', 'Metabolism': 'Intermediate'},
            {'Gene': 'CYP2C19', 'Genotype': '*1/*2', 'Metabolism': 'Intermediate'}
        ],
        'wellness_profile': [
            {'Trait': 'Eye Color', 'Value': 'Brown'},
            {'Trait': 'Hair Color', 'Value': 'Black'}
        ]
    }


@pytest.fixture
def mock_family_analysis_results():
    """Mock family analysis results."""
    return {
        'shared_risks': {
            'high_prs_shared': [
                {'disease': 'Coronary Artery Disease', 'members': ['Child', 'Mother']}
            ],
            'clinical_risks_shared': [
                {'variant': 'rs5', 'members': ['Child', 'Father']}
            ]
        },
        'relationship_verification': {
            'family_configuration': {'type': 'trio'},
            'child_mother': {'confidence_score': 0.95, 'predicted_relationship': 'parent_child'},
            'child_father': {'confidence_score': 0.92, 'predicted_relationship': 'parent_child'}
        },
        'compound_heterozygosity': {
            'GENE1': {
                'compound_het': True,
                'maternal_variants': [{'rsid': 'rs2'}],
                'paternal_variants': [{'rsid': 'rs6'}]
            }
        },
        'variant_origins': {
            'rs1': {'child_genotype': 'AA', 'origin': 'mother', 'possible_sources': ['mother']}
        }
    }


@pytest.fixture
def mock_individual_results_dict(mock_individual_analysis_results):
    """Mock dict of individual results."""
    return {
        'Child': mock_individual_analysis_results,
        'Mother': mock_individual_analysis_results.copy(),
        'Father': mock_individual_analysis_results.copy()
    }


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


class TestIndividualPDFReport:
    """Test individual PDF report generation."""

    @patch('family_genomic_cli.reporting.add_cover_page')
    @patch('family_genomic_cli.reporting.add_executive_summary')
    @patch('family_genomic_cli.reporting.add_genetic_snapshot')
    @patch('family_genomic_cli.reporting.add_detailed_health_chapter')
    @patch('family_genomic_cli.reporting.add_medication_guide_section')
    @patch('family_genomic_cli.reporting.add_comprehensive_carrier_status')
    @patch('family_genomic_cli.reporting.add_pharmacogenomics_profile')
    @patch('family_genomic_cli.reporting.add_disease_risk_assessment')
    @patch('family_genomic_cli.reporting.add_polygenic_risk_scores')
    @patch('family_genomic_cli.reporting.add_wellness_lifestyle_profile')
    @patch('family_genomic_cli.reporting.add_advanced_analytics_dashboard')
    @patch('family_genomic_cli.reporting.add_personalized_recommendations')
    @patch('family_genomic_cli.reporting.add_methodology_references')
    @patch('family_genomic_cli.reporting.add_appendix_raw_data')
    def test_generate_individual_pdf_success(self, mock_appendix, mock_references, mock_recommendations,
                                           mock_dashboard, mock_wellness, mock_prs, mock_risk_assessment,
                                           mock_carrier, mock_medication, mock_health_chapter,
                                           mock_snapshot, mock_executive, mock_cover,
                                           mock_individual_analysis_results, temp_output_dir):
        """Test successful individual PDF generation."""
        # Mock all PDF functions to do nothing
        for mock_func in [mock_cover, mock_executive, mock_snapshot, mock_health_chapter,
                         mock_medication, mock_carrier, mock_prs, mock_risk_assessment,
                         mock_wellness, mock_dashboard, mock_recommendations, mock_references, mock_appendix]:
            mock_func.return_value = None

        result = generate_individual_pdf_report(mock_individual_analysis_results, temp_output_dir, "TestMember")

        assert result != ""
        assert os.path.exists(result)
        assert result.endswith("testmember_genomic_report.pdf")

    def test_generate_individual_pdf_empty_results(self, temp_output_dir):
        """Test PDF generation with empty results."""
        empty_results = {}
        result = generate_individual_pdf_report(empty_results, temp_output_dir, "Empty")

        assert result != ""
        assert os.path.exists(result)

    @patch('reportlab.platypus.SimpleDocTemplate.build')
    def test_generate_individual_pdf_build_error(self, mock_build, mock_individual_analysis_results, temp_output_dir):
        """Test PDF generation with build error."""
        mock_build.side_effect = Exception("Build failed")

        result = generate_individual_pdf_report(mock_individual_analysis_results, temp_output_dir, "Error")

        assert result == ""


class TestFamilyPDFReport:
    """Test family PDF report generation."""

    @patch('family_genomic_cli.reporting.add_cover_page')
    @patch('family_genomic_cli.reporting.add_executive_summary')
    @patch('family_genomic_cli.reporting.add_family_executive_summary')
    @patch('family_genomic_cli.reporting.add_genetic_inheritance_map')
    @patch('family_genomic_cli.reporting.add_family_clinical_risks')
    @patch('family_genomic_cli.reporting.add_carrier_status_compound_risks')
    @patch('family_genomic_cli.reporting.add_family_pharmacogenomics')
    @patch('family_genomic_cli.reporting.add_family_polygenic_risk_scores')
    @patch('family_genomic_cli.reporting.add_family_wellness_profile')
    @patch('family_genomic_cli.reporting.add_advanced_family_analytics')
    @patch('family_genomic_cli.reporting.add_family_qc_appendix')
    def test_generate_family_pdf_success(self, mock_qc, mock_analytics, mock_wellness, mock_prs,
                                       mock_pgx, mock_carrier, mock_clinical, mock_inheritance,
                                       mock_exec, mock_summary, mock_cover,
                                       mock_family_analysis_results, mock_individual_results_dict, temp_output_dir):
        """Test successful family PDF generation."""
        for mock_func in [mock_cover, mock_summary, mock_exec, mock_inheritance, mock_clinical,
                         mock_carrier, mock_pgx, mock_prs, mock_wellness, mock_analytics, mock_qc]:
            mock_func.return_value = None

        result = generate_family_pdf_report(mock_family_analysis_results, mock_individual_results_dict,
                                          temp_output_dir, "TestFamily")

        assert result != ""
        assert os.path.exists(result)
        assert result.endswith("testfamily_family_genomic_report.pdf")

    def test_generate_family_pdf_empty_results(self, temp_output_dir):
        """Test family PDF with empty results."""
        result = generate_family_pdf_report({}, {}, temp_output_dir, "Empty")

        assert result != ""
        assert os.path.exists(result)


class TestJSONReport:
    """Test JSON report generation."""

    def test_generate_json_individual_success(self, mock_individual_analysis_results, temp_output_dir):
        """Test successful individual JSON generation."""
        result = generate_json_report(mock_individual_analysis_results, output_dir=temp_output_dir,
                                    filename="test_individual.json")

        assert result != ""
        assert os.path.exists(result)

        # Verify JSON content
        with open(result, 'r') as f:
            data = json.load(f)

        assert 'report_type' in data
        assert data['report_type'] == 'individual_genomic_analysis'
        assert 'individual_results' in data
        assert 'timestamp' in data

    def test_generate_json_family_success(self, mock_individual_analysis_results, mock_family_analysis_results, temp_output_dir):
        """Test successful family JSON generation."""
        result = generate_json_report(mock_individual_analysis_results, mock_family_analysis_results,
                                    output_dir=temp_output_dir, filename="test_family.json")

        assert result != ""
        assert os.path.exists(result)

        with open(result, 'r') as f:
            data = json.load(f)

        assert data['report_type'] == 'family_genomic_analysis'
        assert 'family_analysis_results' in data

    def test_generate_json_empty_results(self, temp_output_dir):
        """Test JSON generation with empty results."""
        result = generate_json_report({}, output_dir=temp_output_dir, filename="empty.json")

        assert result != ""
        assert os.path.exists(result)

    @patch('builtins.open', side_effect=OSError("Write error"))
    def test_generate_json_write_error(self, mock_open, mock_individual_analysis_results, temp_output_dir):
        """Test JSON generation with write error."""
        result = generate_json_report(mock_individual_analysis_results, output_dir=temp_output_dir)

        assert result == ""


class TestCSVReport:
    """Test CSV report generation."""

    def test_generate_csv_individual_success(self, mock_individual_analysis_results, temp_output_dir):
        """Test successful individual CSV generation."""
        results = generate_csv_report(mock_individual_analysis_results, output_dir=temp_output_dir,
                                    filename_prefix="test_individual")

        assert len(results) == 3  # key_findings, risks, prs
        for csv_file in results:
            assert os.path.exists(csv_file)
            assert csv_file.endswith('.csv')

    def test_generate_csv_family_success(self, mock_individual_results_dict, mock_family_analysis_results, temp_output_dir):
        """Test successful family CSV generation."""
        results = generate_csv_report(mock_individual_results_dict, mock_family_analysis_results,
                                    output_dir=temp_output_dir, filename_prefix="test_family")

        assert len(results) == 3
        for csv_file in results:
            assert os.path.exists(csv_file)

    def test_generate_csv_empty_results(self, temp_output_dir):
        """Test CSV generation with empty results."""
        results = generate_csv_report({}, output_dir=temp_output_dir, filename_prefix="empty")

        assert len(results) == 0

    @patch('pandas.DataFrame.to_csv', side_effect=OSError("Write error"))
    def test_generate_csv_write_error(self, mock_to_csv, mock_individual_analysis_results, temp_output_dir):
        """Test CSV generation with write error."""
        results = generate_csv_report(mock_individual_analysis_results, output_dir=temp_output_dir)

        assert len(results) == 0


class TestGenerateReports:
    """Test the main generate_reports function."""

    @patch('family_genomic_cli.reporting.generate_individual_pdf_report')
    @patch('family_genomic_cli.reporting.generate_family_pdf_report')
    @patch('family_genomic_cli.reporting.generate_json_report')
    @patch('family_genomic_cli.reporting.generate_csv_report')
    def test_generate_reports_all_formats(self, mock_csv, mock_json, mock_family_pdf, mock_individual_pdf,
                                        mock_individual_results_dict, mock_family_analysis_results, temp_output_dir):
        """Test generate_reports with all formats."""
        mock_individual_pdf.return_value = os.path.join(temp_output_dir, "individual.pdf")
        mock_family_pdf.return_value = os.path.join(temp_output_dir, "family.pdf")
        mock_json.return_value = os.path.join(temp_output_dir, "report.json")
        mock_csv.return_value = [os.path.join(temp_output_dir, "report_key_findings.csv")]

        result = generate_reports(mock_individual_results_dict, mock_family_analysis_results,
                                output_dir=temp_output_dir, report_formats=['pdf', 'json', 'csv'])

        assert 'pdf' in result
        assert 'json' in result
        assert 'csv' in result
        assert len(result['pdf']) == 4  # 3 individual + 1 family
        assert len(result['json']) == 1
        assert len(result['csv']) == 1

    def test_generate_reports_default_formats(self, mock_individual_results_dict, mock_family_analysis_results, temp_output_dir):
        """Test generate_reports with default formats."""
        result = generate_reports(mock_individual_results_dict, mock_family_analysis_results,
                                output_dir=temp_output_dir)

        assert 'pdf' in result
        assert 'json' in result
        assert 'csv' in result


class TestHelperFunctions:
    """Test helper functions."""

    def test_extract_key_findings(self, mock_individual_analysis_results):
        """Test key findings extraction."""
        findings = _extract_key_findings(mock_individual_analysis_results)

        assert isinstance(findings, list)
        assert len(findings) > 0
        assert "High genetic risk for Coronary Artery Disease" in findings
        assert "Carrier status detected for 1 conditions" in findings

    def test_extract_key_findings_empty(self):
        """Test key findings with empty results."""
        findings = _extract_key_findings({})

        assert isinstance(findings, list)
        assert len(findings) == 1
        assert "Analysis completed" in findings[0]

    def test_calculate_health_score(self, mock_individual_analysis_results):
        """Test health score calculation."""
        score = _calculate_health_score(mock_individual_analysis_results)

        assert isinstance(score, int)
        assert 0 <= score <= 100

    def test_calculate_health_score_empty(self):
        """Test health score with empty results."""
        score = _calculate_health_score({})

        assert score == 75  # Default

    def test_extract_family_key_findings(self, mock_family_analysis_results, mock_individual_results_dict):
        """Test family key findings extraction."""
        findings = _extract_family_key_findings(mock_family_analysis_results, mock_individual_results_dict)

        assert isinstance(findings, list)
        assert len(findings) > 0

    def test_calculate_family_health_score(self, mock_individual_results_dict):
        """Test family health score calculation."""
        score = _calculate_family_health_score(mock_individual_results_dict)

        assert isinstance(score, int)
        assert 0 <= score <= 100

    def test_calculate_family_health_score_empty(self):
        """Test family health score with empty dict."""
        score = _calculate_family_health_score({})

        assert score == 75