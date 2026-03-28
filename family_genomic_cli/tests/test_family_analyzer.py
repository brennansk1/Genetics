import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from family_genomic_cli.family_analyzer import AdvancedFamilyAnalyzer, run_family_analyses


@pytest.fixture
def mock_trio_data():
    """Mock data for a complete family trio."""
    # Common SNPs
    snps = ['rs1', 'rs2', 'rs3', 'rs4', 'rs5', 'rs6']

    # Child genotypes
    child_df = pd.DataFrame({
        'genotype': ['AA', 'AT', 'GG', 'CC', 'TT', 'AG']
    }, index=snps)

    # Mother genotypes (some matching child)
    mother_df = pd.DataFrame({
        'genotype': ['AA', 'AT', 'GG', 'CT', 'TT', 'AG']
    }, index=snps)

    # Father genotypes
    father_df = pd.DataFrame({
        'genotype': ['AT', 'TT', 'GG', 'CC', 'TT', 'GG']
    }, index=snps)

    return {
        'child': child_df,
        'mother': mother_df,
        'father': father_df
    }


@pytest.fixture
def mock_duo_data():
    """Mock data for mother-child duo."""
    snps = ['rs1', 'rs2', 'rs3']
    child_df = pd.DataFrame({'genotype': ['AA', 'AT', 'GG']}, index=snps)
    mother_df = pd.DataFrame({'genotype': ['AA', 'AT', 'AG']}, index=snps)

    return {
        'child': child_df,
        'mother': mother_df
    }


@pytest.fixture
def mock_invalid_data():
    """Mock data with invalid genotypes."""
    snps = ['rs1', 'rs2']
    child_df = pd.DataFrame({'genotype': ['--', '']}, index=snps)
    mother_df = pd.DataFrame({'genotype': ['AA', 'AT']}, index=snps)

    return {
        'child': child_df,
        'mother': mother_df
    }


@pytest.fixture
def mock_individual_risks():
    """Mock individual risk data."""
    return {
        'child': {
            'polygenic_risk_scores': {
                'disease1': {'percentile': 80},
                'disease2': {'percentile': 60}
            },
            'clinical_risk_screening': {
                'category1': {'variant1': 'risk', 'variant2': 'normal'}
            }
        },
        'mother': {
            'polygenic_risk_scores': {
                'disease1': {'percentile': 85},
                'disease3': {'percentile': 70}
            },
            'clinical_risk_screening': {
                'category1': {'variant1': 'risk'}
            }
        },
        'father': {
            'polygenic_risk_scores': {
                'disease1': {'percentile': 75},
                'disease2': {'percentile': 65}
            },
            'clinical_risk_screening': {
                'category1': {'variant2': 'risk'}
            }
        }
    }


class TestAdvancedFamilyAnalyzer:

    def test_init_with_trio(self, mock_trio_data):
        """Test initialization with complete trio data."""
        analyzer = AdvancedFamilyAnalyzer(mock_trio_data)
        assert analyzer.child_df is not None
        assert analyzer.mother_df is not None
        assert analyzer.father_df is not None
        assert len(analyzer.common_snps) == 6

    def test_init_with_duo(self, mock_duo_data):
        """Test initialization with duo data."""
        analyzer = AdvancedFamilyAnalyzer(mock_duo_data)
        assert analyzer.child_df is not None
        assert analyzer.mother_df is not None
        assert analyzer.father_df is None
        assert len(analyzer.common_snps) == 3

    def test_init_no_child(self):
        """Test initialization without child data raises error."""
        with pytest.raises(ValueError, match="Child genotype data is required"):
            AdvancedFamilyAnalyzer({})

    def test_init_empty_child(self):
        """Test initialization with empty child DataFrame."""
        empty_child = pd.DataFrame({'genotype': []}, index=[])
        with pytest.raises(ValueError, match="Child genotype data is required"):
            AdvancedFamilyAnalyzer({'child': empty_child})

    def test_trace_variant_origins(self, mock_trio_data):
        """Test variant origin tracing."""
        analyzer = AdvancedFamilyAnalyzer(mock_trio_data)
        risk_variants = ['rs1', 'rs2', 'rs3', 'rs4']

        results = analyzer.trace_variant_origins(risk_variants)

        assert 'rs1' in results
        assert results['rs1']['origin'] == 'mother'  # AA from mother AA
        assert results['rs2']['origin'] == 'inherited_from_both'  # AT from both
        assert results['rs3']['origin'] == 'inherited_from_both'  # GG from both
        assert results['rs4']['origin'] == 'father'  # CC from father CC

    def test_trace_variant_origins_missing_variant(self, mock_trio_data):
        """Test tracing with variant not in child data."""
        analyzer = AdvancedFamilyAnalyzer(mock_trio_data)
        results = analyzer.trace_variant_origins(['rs999'])
        assert len(results) == 0

    def test_trace_variant_origins_invalid_genotype(self, mock_invalid_data):
        """Test tracing with invalid genotypes."""
        analyzer = AdvancedFamilyAnalyzer(mock_invalid_data)
        results = analyzer.trace_variant_origins(['rs1', 'rs2'])
        assert len(results) == 0  # Both invalid

    def test_detect_compound_heterozygosity(self, mock_trio_data):
        """Test compound heterozygosity detection."""
        analyzer = AdvancedFamilyAnalyzer(mock_trio_data)
        gene_variants = {
            'GENE1': ['rs2', 'rs6'],  # rs2 het from both, rs6 AG from mother
            'GENE2': ['rs1', 'rs3']   # Both homozygous
        }

        results = analyzer.detect_compound_heterozygosity(gene_variants)

        # Should detect for GENE1
        assert 'GENE1' in results
        assert results['GENE1']['compound_het'] is True
        assert len(results['GENE1']['maternal_variants']) > 0
        assert len(results['GENE1']['paternal_variants']) > 0

        # Not for GENE2
        assert 'GENE2' not in results

    def test_detect_compound_heterozygosity_no_compound(self, mock_trio_data):
        """Test when no compound heterozygosity."""
        analyzer = AdvancedFamilyAnalyzer(mock_trio_data)
        gene_variants = {'GENE1': ['rs1', 'rs3']}  # Both not het or same origin

        results = analyzer.detect_compound_heterozygosity(gene_variants)
        assert len(results) == 0

    def test_aggregate_shared_risks(self, mock_trio_data, mock_individual_risks):
        """Test shared risks aggregation."""
        analyzer = AdvancedFamilyAnalyzer(mock_trio_data)
        results = analyzer.aggregate_shared_risks(mock_individual_risks)

        assert 'high_prs_shared' in results
        assert 'clinical_risks_shared' in results

        # disease1 shared by all three
        shared_prs = [r for r in results['high_prs_shared'] if r['disease'] == 'disease1']
        assert len(shared_prs) == 1
        assert set(shared_prs[0]['members']) == {'child', 'mother', 'father'}

        # variant1 shared by child and mother
        shared_clinical = [r for r in results['clinical_risks_shared'] if r['variant'] == 'variant1']
        assert len(shared_clinical) == 1
        assert set(shared_clinical[0]['members']) == {'child', 'mother'}

    def test_detect_uniparental_disomy(self, mock_trio_data):
        """Test UPD detection."""
        analyzer = AdvancedFamilyAnalyzer(mock_trio_data)
        chromosome_regions = {
            '1': [(1000000, 2000000)],
            '2': [(1500000, 2500000)]
        }

        results = analyzer.detect_uniparental_disomy(chromosome_regions)

        # This is simplified, but should return dict
        assert isinstance(results, dict)

    @patch('family_genomic_cli.family_analyzer.FamilyAnalyzer')
    def test_enhanced_relationship_verification_trio(self, mock_family_analyzer, mock_trio_data):
        """Test relationship verification for trio."""
        # Mock the FamilyAnalyzer instances
        mock_analyzer = MagicMock()
        mock_analyzer.calculate_identity_by_state.return_value = 0.8
        mock_analyzer.predict_relationship.return_value = 'parent_child'
        mock_analyzer.analyze_mendelian_errors.return_value = {'error_rate': 0.02}
        mock_family_analyzer.return_value = mock_analyzer

        analyzer = AdvancedFamilyAnalyzer(mock_trio_data)
        results = analyzer.enhanced_relationship_verification()

        assert 'child_mother' in results
        assert 'child_father' in results
        assert 'mother_father' in results
        assert 'family_configuration' in results
        assert results['family_configuration']['type'] == 'trio'

    @patch('family_genomic_cli.family_analyzer.FamilyAnalyzer')
    def test_enhanced_relationship_verification_duo(self, mock_family_analyzer, mock_duo_data):
        """Test relationship verification for duo."""
        mock_analyzer = MagicMock()
        mock_analyzer.calculate_identity_by_state.return_value = 0.75
        mock_analyzer.predict_relationship.return_value = 'parent_child'
        mock_analyzer.analyze_mendelian_errors.return_value = {'error_rate': 0.05}
        mock_family_analyzer.return_value = mock_analyzer

        analyzer = AdvancedFamilyAnalyzer(mock_duo_data)
        results = analyzer.enhanced_relationship_verification()

        assert 'child_mother' in results
        assert 'child_father' not in results
        assert results['family_configuration']['type'] == 'duo_maternal'

    def test_run_family_analyses_complete(self, mock_trio_data, mock_individual_risks):
        """Test complete family analyses run."""
        risk_variants = ['rs1', 'rs2']
        gene_variants = {'GENE1': ['rs2', 'rs6']}
        chromosome_regions = {'1': [(1000000, 2000000)]}

        results = run_family_analyses(
            mock_trio_data,
            risk_variants=risk_variants,
            gene_variants=gene_variants,
            chromosome_regions=chromosome_regions,
            individual_risks=mock_individual_risks
        )

        assert 'relationship_verification' in results
        assert 'variant_origins' in results
        assert 'compound_heterozygosity' in results
        assert 'shared_risks' in results
        assert 'uniparental_disomy' in results

    def test_run_family_analyses_minimal(self, mock_duo_data):
        """Test minimal family analyses run."""
        results = run_family_analyses(mock_duo_data)

        assert 'relationship_verification' in results
        assert 'variant_origins' not in results

    def test_run_family_analyses_error(self):
        """Test error handling in run_family_analyses."""
        with pytest.raises(ValueError):
            run_family_analyses({})  # No child data