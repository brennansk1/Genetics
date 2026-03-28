import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile

from family_genomic_cli.data_processing import (
    load_family_data,
    harmonize_genotypes,
    perform_qc_checks,
    get_possible_child_genotypes,
    get_possible_from_one_parent,
    apply_liftover,
    validate_data,
    process_family_data,
    FamilyData
)


@pytest.fixture
def sample_child_data():
    """Sample child genotype data."""
    return pd.DataFrame({
        'rsid': ['rs1', 'rs2', 'rs3', 'rs4'],
        'chromosome': [1, 1, 2, 2],
        'position': [100, 200, 300, 400],
        'genotype': ['AA', 'AT', 'CC', 'GG']
    }).set_index('rsid')


@pytest.fixture
def sample_mother_data():
    """Sample mother genotype data."""
    return pd.DataFrame({
        'rsid': ['rs1', 'rs2', 'rs3'],
        'chromosome': [1, 1, 2],
        'position': [100, 200, 300],
        'genotype': ['AA', 'TT', 'CT']
    }).set_index('rsid')


@pytest.fixture
def sample_father_data():
    """Sample father genotype data."""
    return pd.DataFrame({
        'rsid': ['rs1', 'rs2', 'rs4'],
        'chromosome': [1, 1, 2],
        'position': [100, 200, 400],
        'genotype': ['AT', 'AT', 'GG']
    }).set_index('rsid')


class TestLoadFamilyData:
    @patch('family_genomic_cli.data_processing.parse_dna_file')
    def test_load_child_only(self, mock_parse, tmp_path, sample_child_data):
        child_file = tmp_path / "child.txt"
        child_file.write_text("dummy")

        mock_parse.return_value = sample_child_data

        result = load_family_data(str(child_file))

        assert 'child' in result
        assert len(result) == 1
        mock_parse.assert_called_once_with(str(child_file), 'AncestryDNA')

    @patch('family_genomic_cli.data_processing.parse_dna_file')
    def test_load_with_parents(self, mock_parse, tmp_path, sample_child_data, sample_mother_data, sample_father_data):
        child_file = tmp_path / "child.txt"
        mother_file = tmp_path / "mother.txt"
        father_file = tmp_path / "father.txt"

        for f in [child_file, mother_file, father_file]:
            f.write_text("dummy")

        mock_parse.side_effect = [sample_child_data, sample_mother_data, sample_father_data]

        result = load_family_data(str(child_file), str(mother_file), str(father_file))

        assert len(result) == 3
        assert 'child' in result
        assert 'mother' in result
        assert 'father' in result

    @patch('family_genomic_cli.data_processing.parse_dna_file')
    def test_load_with_file_formats(self, mock_parse, tmp_path, sample_child_data):
        child_file = tmp_path / "child.txt"
        child_file.write_text("dummy")

        mock_parse.return_value = sample_child_data

        formats = {'child': '23andMe'}
        result = load_family_data(str(child_file), file_formats=formats)

        mock_parse.assert_called_once_with(str(child_file), '23andMe')


class TestHarmonizeGenotypes:
    def test_harmonize_single_member(self, sample_child_data):
        family_data = {'child': sample_child_data}

        result = harmonize_genotypes(family_data)

        assert len(result) == 4
        assert 'child_genotype' in result.columns

    def test_harmonize_multiple_members(self, sample_child_data, sample_mother_data, sample_father_data):
        family_data = {
            'child': sample_child_data,
            'mother': sample_mother_data,
            'father': sample_father_data
        }

        result = harmonize_genotypes(family_data)

        # Should have intersection of rsids: rs1, rs2
        assert len(result) == 2
        assert 'child_genotype' in result.columns
        assert 'mother_genotype' in result.columns
        assert 'father_genotype' in result.columns

    def test_harmonize_empty_data(self):
        family_data = {}

        result = harmonize_genotypes(family_data)

        assert result.empty


class TestGetPossibleChildGenotypes:
    def test_both_parents_known(self):
        # AA x AT -> possible: AA, AT
        result = get_possible_child_genotypes('AA', 'AT')
        assert result == {'AA', 'AT'}

        # CC x GG -> possible: CG
        result = get_possible_child_genotypes('CC', 'GG')
        assert result == {'CG'}

    def test_one_parent_known(self):
        # Mother AA -> child can be AA or A + any other
        result = get_possible_child_genotypes('AA', None)
        expected = {'AA', 'AC', 'AG', 'AT'}
        assert result == expected

    def test_no_parents_known(self):
        result = get_possible_child_genotypes(None, None)
        assert result == set()

    def test_invalid_parent_data(self):
        result = get_possible_child_genotypes('--', 'AT')
        assert result == set()


class TestGetPossibleFromOneParent:
    def test_homozygous_parent(self):
        result = get_possible_from_one_parent('AA')
        expected = {'AA', 'AC', 'AG', 'AT'}
        assert result == expected

    def test_heterozygous_parent(self):
        result = get_possible_from_one_parent('AT')
        expected = {'AA', 'AC', 'AG', 'AT', 'TT', 'TC', 'TG', 'TA'}
        assert result == expected

    def test_invalid_parent(self):
        result = get_possible_from_one_parent('--')
        assert result == set()


class TestPerformQcChecks:
    def test_qc_no_parents(self, sample_child_data):
        harmonized = sample_child_data[['genotype']].rename(columns={'genotype': 'child_genotype'})

        result = perform_qc_checks(harmonized)

        assert result['available_parents'] == []
        assert result['error_count'] == 0

    def test_qc_with_parents_valid(self, sample_child_data, sample_mother_data, sample_father_data):
        # Create harmonized data with valid mendelian inheritance
        harmonized = pd.DataFrame({
            'child_genotype': ['AA', 'AT'],  # rs1: AA from AA+AT, rs2: AT from TT+AT
            'mother_genotype': ['AA', 'TT'],
            'father_genotype': ['AT', 'AT']
        }, index=['rs1', 'rs2'])

        result = perform_qc_checks(harmonized)

        assert result['available_parents'] == ['mother', 'father']
        assert result['error_count'] == 0
        assert result['error_rate'] == 0.0

    def test_qc_with_mendelian_error(self):
        # Child genotype impossible from parents
        harmonized = pd.DataFrame({
            'child_genotype': ['CC'],  # Impossible from AA + GG
            'mother_genotype': ['AA'],
            'father_genotype': ['GG']
        }, index=['rs1'])

        result = perform_qc_checks(harmonized)

        assert result['error_count'] == 1
        assert result['error_rate'] == 1.0
        assert len(result['errors']) == 1

    def test_qc_missing_child_genotype(self):
        harmonized = pd.DataFrame({
            'child_genotype': ['--'],
            'mother_genotype': ['AA'],
            'father_genotype': ['AT']
        }, index=['rs1'])

        result = perform_qc_checks(harmonized)

        assert result['error_count'] == 0  # Skipped due to missing child


class TestApplyLiftover:
    @patch('family_genomic_cli.data_processing.LIFTOVER_AVAILABLE', True)
    @patch('family_genomic_cli.data_processing.LiftOver')
    def test_liftover_success(self, mock_liftover_class, sample_child_data):
        mock_lo = MagicMock()
        mock_lo.convert_coordinate.return_value = [('chr1', 150)]
        mock_liftover_class.return_value = mock_lo

        family_data = {'child': sample_child_data}

        result = apply_liftover(family_data, 'dummy_chain')

        mock_liftover_class.assert_called_once_with('dummy_chain')
        assert result['child'].loc['rs1', 'position'] == 150

    @patch('family_genomic_cli.data_processing.LIFTOVER_AVAILABLE', False)
    def test_liftover_not_available(self, sample_child_data):
        family_data = {'child': sample_child_data}

        result = apply_liftover(family_data, 'dummy_chain')

        # Should return unchanged
        assert result == family_data

    @patch('family_genomic_cli.data_processing.LIFTOVER_AVAILABLE', True)
    @patch('family_genomic_cli.data_processing.LiftOver')
    def test_liftover_missing_columns(self, mock_liftover_class):
        # DataFrame without chromosome/position
        df = pd.DataFrame({
            'rsid': ['rs1'],
            'genotype': ['AA']
        }).set_index('rsid')

        family_data = {'child': df}

        result = apply_liftover(family_data, 'dummy_chain')

        # Should return unchanged
        assert result == family_data


class TestValidateData:
    def test_validate_sufficient_overlap(self, sample_child_data, sample_mother_data):
        family_data = {'child': sample_child_data, 'mother': sample_mother_data}
        harmonized = pd.DataFrame({'dummy': []})  # Simulate overlap
        harmonized = harmonized.head(15000)  # Mock sufficient overlap

        result = validate_data(family_data, harmonized)

        assert result['sufficient_overlap'] is True
        assert result['valid_formats'] is True

    def test_validate_insufficient_overlap(self, sample_child_data):
        family_data = {'child': sample_child_data}
        harmonized = pd.DataFrame()  # Empty

        result = validate_data(family_data, harmonized)

        assert result['sufficient_overlap'] is False
        assert 'Insufficient SNP overlap' in str(result['errors'])

    def test_validate_empty_data(self):
        family_data = {'child': pd.DataFrame()}
        harmonized = pd.DataFrame()

        result = validate_data(family_data, harmonized)

        assert result['valid_formats'] is False
        assert 'Empty data for child' in str(result['errors'])

    def test_validate_missing_genotype_column(self):
        df = pd.DataFrame({'rsid': ['rs1']}).set_index('rsid')
        family_data = {'child': df}
        harmonized = pd.DataFrame()

        result = validate_data(family_data, harmonized)

        assert result['valid_formats'] is False
        assert 'Missing genotype column' in str(result['errors'])


class TestProcessFamilyData:
    @patch('family_genomic_cli.data_processing.load_family_data')
    @patch('family_genomic_cli.data_processing.apply_liftover')
    @patch('family_genomic_cli.data_processing.harmonize_genotypes')
    @patch('family_genomic_cli.data_processing.perform_qc_checks')
    @patch('family_genomic_cli.data_processing.validate_data')
    def test_process_family_data_success(self, mock_validate, mock_qc, mock_harmonize, mock_liftover, mock_load,
                                         sample_child_data):
        mock_load.return_value = {'child': sample_child_data}
        mock_liftover.return_value = {'child': sample_child_data}
        mock_harmonize.return_value = sample_child_data[['genotype']].rename(columns={'genotype': 'child_genotype'})
        mock_qc.return_value = {'error_count': 0}
        mock_validate.return_value = {'valid_formats': True, 'sufficient_overlap': True}

        result = process_family_data('child.txt')

        assert isinstance(result, FamilyData)
        assert result.qc_results == {'error_count': 0}
        assert result.validation == {'valid_formats': True, 'sufficient_overlap': True}

    @patch('family_genomic_cli.data_processing.load_family_data')
    def test_process_family_data_load_error(self, mock_load):
        mock_load.side_effect = Exception("Load failed")

        with pytest.raises(Exception, match="Load failed"):
            process_family_data('child.txt')

    @patch('family_genomic_cli.data_processing.load_family_data')
    @patch('family_genomic_cli.data_processing.apply_liftover')
    @patch('family_genomic_cli.data_processing.harmonize_genotypes')
    @patch('family_genomic_cli.data_processing.perform_qc_checks')
    @patch('family_genomic_cli.data_processing.validate_data')
    def test_process_family_data_with_liftover(self, mock_validate, mock_qc, mock_harmonize, mock_liftover, mock_load,
                                               sample_child_data):
        mock_load.return_value = {'child': sample_child_data}
        mock_liftover.return_value = {'child': sample_child_data}
        mock_harmonize.return_value = sample_child_data[['genotype']].rename(columns={'genotype': 'child_genotype'})
        mock_qc.return_value = {'error_count': 0}
        mock_validate.return_value = {'valid_formats': True, 'sufficient_overlap': True}

        result = process_family_data('child.txt', liftover_chain_path='chain.gz')

        mock_liftover.assert_called_once()