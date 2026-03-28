import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import yaml
import argparse
import logging

from family_genomic_cli.cli import load_config, validate_files, main


class TestLoadConfig:
    def test_load_config_existing(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_data = {"key": "value", "nested": {"item": 1}}
        config_file.write_text(yaml.dump(config_data))

        result = load_config(str(config_file))
        assert result == config_data

    def test_load_config_nonexisting(self):
        result = load_config("nonexisting.yaml")
        assert result == {}

    def test_load_config_none(self):
        result = load_config(None)
        assert result == {}


class TestValidateFiles:
    def test_validate_files_child_only_exists(self, tmp_path):
        child_file = tmp_path / "child.txt"
        child_file.write_text("sample data")

        # Should not raise
        validate_files(str(child_file))

    def test_validate_files_all_exist(self, tmp_path):
        child_file = tmp_path / "child.txt"
        mother_file = tmp_path / "mother.txt"
        father_file = tmp_path / "father.txt"

        for f in [child_file, mother_file, father_file]:
            f.write_text("sample data")

        # Should not raise
        validate_files(str(child_file), str(mother_file), str(father_file))

    def test_validate_files_child_missing(self):
        with pytest.raises(FileNotFoundError, match="Input file not found: missing_child.txt"):
            validate_files("missing_child.txt")

    def test_validate_files_mother_missing(self, tmp_path):
        child_file = tmp_path / "child.txt"
        child_file.write_text("sample data")

        with pytest.raises(FileNotFoundError, match="Input file not found: missing_mother.txt"):
            validate_files(str(child_file), "missing_mother.txt")

    def test_validate_files_father_missing(self, tmp_path):
        child_file = tmp_path / "child.txt"
        child_file.write_text("sample data")

        with pytest.raises(FileNotFoundError, match="Input file not found: missing_father.txt"):
            validate_files(str(child_file), None, "missing_father.txt")


class TestMainFunction:
    @patch('family_genomic_cli.cli.setup_logging')
    @patch('family_genomic_cli.cli.load_config')
    @patch('family_genomic_cli.cli.validate_files')
    def test_main_minimal_args_success(self, mock_validate, mock_load, mock_setup, tmp_path, caplog):
        child_file = tmp_path / "child.txt"
        child_file.write_text("sample data")

        mock_load.return_value = {}

        with patch('sys.argv', ['cli.py', '--child', str(child_file)]):
            main()

        mock_setup.assert_called_once_with(log_level=logging.INFO)
        mock_load.assert_called_once_with(None)
        mock_validate.assert_called_once_with(str(child_file), None, None)

        assert "Configuration loaded" in caplog.text
        assert "Input files validated" in caplog.text
        assert "Starting data processing..." in caplog.text
        assert "Starting analysis..." in caplog.text
        assert "Generating report..." in caplog.text
        assert "Analysis completed successfully" in caplog.text

    @patch('family_genomic_cli.cli.setup_logging')
    @patch('family_genomic_cli.cli.load_config')
    @patch('family_genomic_cli.cli.validate_files')
    def test_main_all_args_success(self, mock_validate, mock_load, mock_setup, tmp_path, caplog):
        child_file = tmp_path / "child.txt"
        mother_file = tmp_path / "mother.txt"
        father_file = tmp_path / "father.txt"
        config_file = tmp_path / "config.yaml"
        output_dir = tmp_path / "output"

        for f in [child_file, mother_file, father_file]:
            f.write_text("sample data")
        config_file.write_text("key: value\n")
        output_dir.mkdir()

        mock_load.return_value = {"key": "value"}

        with patch('sys.argv', [
            'cli.py',
            '--child', str(child_file),
            '--mother', str(mother_file),
            '--father', str(father_file),
            '--output', str(output_dir),
            '--config', str(config_file),
            '--log-level', 'DEBUG',
            '--format', 'json'
        ]):
            main()

        mock_setup.assert_called_once_with(log_level=logging.DEBUG)
        mock_load.assert_called_once_with(str(config_file))
        mock_validate.assert_called_once_with(str(child_file), str(mother_file), str(father_file))

        assert "Configuration loaded" in caplog.text
        assert "Input files validated" in caplog.text

    @patch('family_genomic_cli.cli.setup_logging')
    @patch('family_genomic_cli.cli.load_config')
    @patch('family_genomic_cli.cli.validate_files')
    def test_main_file_validation_error(self, mock_validate, mock_load, mock_setup, caplog):
        mock_load.return_value = {}
        mock_validate.side_effect = FileNotFoundError("File not found")

        with patch('sys.argv', ['cli.py', '--child', 'missing.txt']):
            with pytest.raises(SystemExit):
                main()

        assert "An error occurred: File not found" in caplog.text

    @patch('family_genomic_cli.cli.setup_logging')
    @patch('family_genomic_cli.cli.load_config')
    @patch('family_genomic_cli.cli.validate_files')
    def test_main_config_load_error(self, mock_validate, mock_load, mock_setup, caplog):
        mock_load.side_effect = Exception("Config error")

        with patch('sys.argv', ['cli.py', '--child', 'dummy.txt']):
            with pytest.raises(SystemExit):
                main()

        assert "An error occurred: Config error" in caplog.text

    def test_main_missing_required_arg(self, capsys):
        with patch('sys.argv', ['cli.py']):
            with pytest.raises(SystemExit):
                main()

        captured = capsys.readouterr()
        assert "the following arguments are required: --child" in captured.err

    def test_main_invalid_log_level(self, capsys):
        with patch('sys.argv', ['cli.py', '--child', 'dummy.txt', '--log-level', 'INVALID']):
            with pytest.raises(SystemExit):
                main()

        captured = capsys.readouterr()
        assert "invalid choice" in captured.err

    def test_main_invalid_format(self, capsys):
        with patch('sys.argv', ['cli.py', '--child', 'dummy.txt', '--format', 'invalid']):
            with pytest.raises(SystemExit):
                main()

        captured = capsys.readouterr()
        assert "invalid choice" in captured.err