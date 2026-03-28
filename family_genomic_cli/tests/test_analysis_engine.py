import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from family_genomic_cli.analysis_engine import (
    clinical_risk_screening,
    pgx_analysis,
    prs_analysis,
    wellness_traits_analysis,
    carrier_status_screening,
    run_individual_analyses,
    _screen_category,
    _classify_variant
)


@pytest.fixture
def sample_genotype_data():
    """Sample genotype data for testing."""
    return pd.DataFrame({
        'genotype': ['AA', 'AT', 'CC', 'GG', 'TT']
    }, index=['rs1', 'rs2', 'rs3', 'rs4', 'rs5'])


@pytest.fixture
def sample_genotype_dict():
    """Sample genotype data as dict."""
    return {
        'rs1': 'AA',
        'rs2': 'AT',
        'rs3': 'CC',
        'rs4': 'GG',
        'rs5': 'TT'
    }


class TestClassifyVariant:
    def test_classify_pathogenic(self):
        assert _classify_variant("Pathogenic") == "Pathogenic"

    def test_classify_likely_pathogenic(self):
        assert _classify_variant("Likely Pathogenic") == "Likely Pathogenic"

    def test_classify_vus(self):
        assert _classify_variant("Variant of uncertain significance") == "VUS"

    def test_classify_benign(self):
        assert _classify_variant("Benign") == "Benign"


class TestScreenCategory:
    def test_screen_category_with_findings(self, sample_genotype_data):
        snp_dict = {
            'rs1': {
                'gene': 'BRCA1',
                'condition': 'Breast Cancer',
                'risk': 'High',
                'interp': {'AA': 'Pathogenic'}
            },
            'rs6': {'gene': 'GENE2', 'interp': {'GG': 'Benign'}}  # Not in data
        }

        result = _screen_category(snp_dict, sample_genotype_data)

        assert 'rs1' in result
        assert result['rs1']['classification'] == 'Pathogenic'
        assert result['rs1']['gene'] == 'BRCA1'

    def test_screen_category_no_findings(self, sample_genotype_data):
        snp_dict = {
            'rs1': {'gene': 'GENE1', 'interp': {'AA': 'Benign'}}
        }

        result = _screen_category(snp_dict, sample_genotype_data)

        assert result == {}  # Benign not included

    def test_screen_category_missing_genotype(self, sample_genotype_data):
        snp_dict = {
            'rs_missing': {'gene': 'GENE1', 'interp': {'AA': 'Pathogenic'}}
        }

        result = _screen_category(snp_dict, sample_genotype_data)

        assert result == {}


class TestClinicalRiskScreening:
    @patch('family_genomic_cli.analysis_engine.snp_data')
    def test_clinical_risk_screening_dataframe(self, mock_snp_data, sample_genotype_data):
        # Mock SNP data functions
        mock_snp_data.get_cancer_snps.return_value = {
            'rs1': {'gene': 'BRCA1', 'condition': 'Breast Cancer', 'interp': {'AA': 'Pathogenic'}}
        }
        mock_snp_data.get_cardiovascular_snps.return_value = {}
        mock_snp_data.get_neuro_snps.return_value = {}
        mock_snp_data.get_mito_snps.return_value = {}
        mock_snp_data.get_acmg_sf_variants.return_value = {}

        result = clinical_risk_screening(sample_genotype_data)

        assert 'hereditary_cancer' in result
        assert 'rs1' in result['hereditary_cancer']
        assert result['hereditary_cancer']['rs1']['classification'] == 'Pathogenic'

    @patch('family_genomic_cli.analysis_engine.snp_data')
    def test_clinical_risk_screening_dict(self, mock_snp_data, sample_genotype_dict):
        mock_snp_data.get_cancer_snps.return_value = {}
        mock_snp_data.get_cardiovascular_snps.return_value = {}
        mock_snp_data.get_neuro_snps.return_value = {}
        mock_snp_data.get_mito_snps.return_value = {}
        mock_snp_data.get_acmg_sf_variants.return_value = {}

        result = clinical_risk_screening(sample_genotype_dict)

        assert isinstance(result, dict)
        assert 'hereditary_cancer' in result


class TestPgxAnalysis:
    @patch('family_genomic_cli.analysis_engine.pgx_star_alleles')
    def test_pgx_analysis_success(self, mock_pgx, sample_genotype_data):
        mock_caller = MagicMock()
        mock_caller.call_star_alleles.return_value = {
            'metabolizer_status': 'Normal Metabolizer',
            'alleles': ['*1/*1']
        }
        mock_caller.get_cpic_recommendations.return_value = {
            'drugs': ['clopidogrel'],
            'recommendations': ['Normal dose']
        }
        mock_pgx.star_caller = mock_caller

        result = pgx_analysis(sample_genotype_data)

        assert 'CYP2C19' in result
        assert result['CYP2C19']['metabolizer_status'] == 'Normal Metabolizer'
        assert 'drug_recommendations' in result['CYP2C19']

    @patch('family_genomic_cli.analysis_engine.pgx_star_alleles')
    def test_pgx_analysis_error(self, mock_pgx, sample_genotype_data):
        mock_caller = MagicMock()
        mock_caller.call_star_alleles.return_value = {'error': 'Analysis failed'}
        mock_pgx.star_caller = mock_caller

        result = pgx_analysis(sample_genotype_data)

        assert 'CYP2C19' in result
        assert 'error' in result['CYP2C19']


class TestPrsAnalysis:
    @patch('family_genomic_cli.analysis_engine.genomewide_prs')
    @patch('family_genomic_cli.analysis_engine.snp_data')
    def test_prs_analysis_success(self, mock_snp_data, mock_prs_module, sample_genotype_data):
        mock_snp_data.get_prs_models_by_category.return_value = {'model1': {}}

        mock_prs_calc = MagicMock()
        mock_prs_calc.calculate_genomewide_prs.return_value = {
            'success': True,
            'prs_score': 1.5,
            'percentile': 75,
            'normalized_score': 0.8,
            'snps_used': 100,
            'total_snps': 120,
            'coverage': 0.83
        }
        mock_prs_module.GenomeWidePRS.return_value = mock_prs_calc

        result = prs_analysis(sample_genotype_data)

        assert 'Type 2 Diabetes' in result
        assert result['Type 2 Diabetes']['score'] == 1.5
        assert result['Type 2 Diabetes']['percentile'] == 75

    @patch('family_genomic_cli.analysis_engine.genomewide_prs')
    @patch('family_genomic_cli.analysis_engine.snp_data')
    def test_prs_analysis_no_models(self, mock_snp_data, mock_prs_module, sample_genotype_data):
        mock_snp_data.get_prs_models_by_category.return_value = {}

        result = prs_analysis(sample_genotype_data)

        assert result == {}  # No diseases analyzed if no models

    @patch('family_genomic_cli.analysis_engine.genomewide_prs')
    @patch('family_genomic_cli.analysis_engine.snp_data')
    def test_prs_analysis_calculation_failure(self, mock_snp_data, mock_prs_module, sample_genotype_data):
        mock_snp_data.get_prs_models_by_category.return_value = {'model1': {}}

        mock_prs_calc = MagicMock()
        mock_prs_calc.calculate_genomewide_prs.return_value = {'success': False}
        mock_prs_module.GenomeWidePRS.return_value = mock_prs_calc

        result = prs_analysis(sample_genotype_data)

        assert 'Type 2 Diabetes' in result
        assert 'error' in result['Type 2 Diabetes']


class TestWellnessTraitsAnalysis:
    @patch('family_genomic_cli.analysis_engine.bioinformatics_utils')
    def test_wellness_traits_analysis_success(self, mock_bio_utils, sample_genotype_data):
        mock_bio_utils.predict_functional_impact.return_value = {
            'predicted_impact': 'moderate',
            'details': 'Some details'
        }

        result = wellness_traits_analysis(sample_genotype_data)

        # rs4680 is in the wellness SNPs
        assert 'Caffeine Metabolism' in result
        assert result['Caffeine Metabolism']['predicted_impact'] == 'moderate'

    @patch('family_genomic_cli.analysis_engine.bioinformatics_utils')
    def test_wellness_traits_analysis_missing_snp(self, mock_bio_utils):
        # DataFrame without the wellness SNPs
        genotype_data = pd.DataFrame({
            'genotype': ['AA']
        }, index=['rs_unknown'])

        result = wellness_traits_analysis(genotype_data)

        assert result == {}

    @patch('family_genomic_cli.analysis_engine.bioinformatics_utils')
    def test_wellness_traits_analysis_error(self, mock_bio_utils, sample_genotype_data):
        mock_bio_utils.predict_functional_impact.side_effect = Exception("Prediction failed")

        result = wellness_traits_analysis(sample_genotype_data)

        assert 'Caffeine Metabolism' in result
        assert 'error' in result['Caffeine Metabolism']


class TestCarrierStatusScreening:
    @patch('family_genomic_cli.analysis_engine.snp_data')
    def test_carrier_status_screening_carrier_found(self, mock_snp_data, sample_genotype_data):
        mock_snp_data.get_recessive_snps.return_value = {
            'rs2': {  # AT is heterozygous
                'condition': 'Cystic Fibrosis',
                'gene': 'CFTR',
                'interp': {'AT': 'Carrier'}
            }
        }

        result = carrier_status_screening(sample_genotype_data)

        assert 'rs2' in result
        assert result['rs2']['carrier_status'] == 'Carrier'
        assert result['rs2']['condition'] == 'Cystic Fibrosis'

    @patch('family_genomic_cli.analysis_engine.snp_data')
    def test_carrier_status_screening_no_carriers(self, mock_snp_data, sample_genotype_data):
        mock_snp_data.get_recessive_snps.return_value = {
            'rs1': {  # AA is homozygous
                'condition': 'Disease',
                'interp': {'AA': 'Not carrier'}
            }
        }

        result = carrier_status_screening(sample_genotype_data)

        assert result == {}

    @patch('family_genomic_cli.analysis_engine.snp_data')
    def test_carrier_status_screening_missing_snp(self, mock_snp_data, sample_genotype_data):
        mock_snp_data.get_recessive_snps.return_value = {
            'rs_missing': {
                'condition': 'Disease',
                'interp': {'AT': 'Carrier'}
            }
        }

        result = carrier_status_screening(sample_genotype_data)

        assert result == {}


class TestRunIndividualAnalyses:
    @patch('family_genomic_cli.analysis_engine.clinical_risk_screening')
    @patch('family_genomic_cli.analysis_engine.pgx_analysis')
    @patch('family_genomic_cli.analysis_engine.prs_analysis')
    @patch('family_genomic_cli.analysis_engine.wellness_traits_analysis')
    @patch('family_genomic_cli.analysis_engine.carrier_status_screening')
    def test_run_individual_analyses_success(self, mock_carrier, mock_wellness, mock_prs, mock_pgx, mock_clinical, sample_genotype_data):
        mock_clinical.return_value = {'cancer': {}}
        mock_pgx.return_value = {'CYP2C19': {}}
        mock_prs.return_value = {'Diabetes': {}}
        mock_wellness.return_value = {'Caffeine': {}}
        mock_carrier.return_value = {'rs1': {}}

        result = run_individual_analyses(sample_genotype_data)

        assert 'clinical_risk_screening' in result
        assert 'pharmacogenomics' in result
        assert 'polygenic_risk_scores' in result
        assert 'wellness_traits' in result
        assert 'carrier_status' in result

    @patch('family_genomic_cli.analysis_engine.clinical_risk_screening')
    @patch('family_genomic_cli.analysis_engine.pgx_analysis')
    @patch('family_genomic_cli.analysis_engine.prs_analysis')
    @patch('family_genomic_cli.analysis_engine.wellness_traits_analysis')
    @patch('family_genomic_cli.analysis_engine.carrier_status_screening')
    def test_run_individual_analyses_clinical_error(self, mock_carrier, mock_wellness, mock_prs, mock_pgx, mock_clinical, sample_genotype_data):
        mock_clinical.side_effect = Exception("Clinical failed")
        mock_pgx.return_value = {}
        mock_prs.return_value = {}
        mock_wellness.return_value = {}
        mock_carrier.return_value = {}

        result = run_individual_analyses(sample_genotype_data)

        assert 'error' in result['clinical_risk_screening']
        assert 'pharmacogenomics' in result  # Others should still run