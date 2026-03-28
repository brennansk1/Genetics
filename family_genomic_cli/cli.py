import argparse
import logging
import os
import sys
from pathlib import Path
import yaml

# Add current directory to path for relative imports when running as script
sys.path.insert(0, os.path.dirname(__file__))

from copied_modules.logging_utils import setup_logging
from data_processing import process_family_data
from analysis_engine import run_individual_analyses
from family_analyzer import run_family_analyses
from reporting import generate_reports

def list_analyses():
    """Print a list of all analyses performed by the tool."""
    print("Available Analyses:")
    print()
    print("1. Clinical Risk Screening:")
    print("   - Assesses genetic risk for various diseases and conditions")
    print("   - Includes monogenic and complex trait analysis")
    print("   - Provides risk estimates based on genetic variants")
    print()
    print("2. Pharmacogenomics:")
    print("   - Analyzes genetic variants affecting drug metabolism")
    print("   - Predicts drug response and potential adverse reactions")
    print("   - Includes star allele calling for key pharmacogenes")
    print()
    print("3. Polygenic Risk Scores:")
    print("   - Calculates risk scores for complex traits using genome-wide data")
    print("   - Includes ancestry-adjusted PRS for better accuracy")
    print("   - Provides percentile rankings and risk interpretations")
    print()
    print("4. Wellness Traits:")
    print("   - Analyzes genetic factors influencing lifestyle and wellness")
    print("   - Includes traits like caffeine metabolism, alcohol sensitivity")
    print("   - Provides personalized wellness recommendations")
    print()
    print("5. Carrier Status:")
    print("   - Identifies carrier status for recessive genetic conditions")
    print("   - Screens for pathogenic variants in disease-associated genes")
    print("   - Important for family planning and reproductive health")
    print()
    print("6. Family Analyses:")
    print("   - Performs trio analysis for parent-child relationships")
    print("   - Identifies de novo mutations and inheritance patterns")
    print("   - Provides family-specific genetic insights")
    print()
    print("7. Reporting Options:")
    print("   - Generates comprehensive PDF reports")
    print("   - Supports JSON and CSV output formats")
    print("   - Includes visualizations and detailed explanations")

def load_config(config_path):
    """Load configuration from YAML file."""
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}

def validate_files(child_path, mother_path=None, father_path=None):
    """Validate that input files exist."""
    files_to_check = [child_path]
    if mother_path:
        files_to_check.append(mother_path)
    if father_path:
        files_to_check.append(father_path)

    for file_path in files_to_check:
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")

def main():
    parser = argparse.ArgumentParser(description="Family Genomic Analysis CLI")
    parser.add_argument('--child', help='Path to child\'s DNA file')
    parser.add_argument('--mother', help='Path to mother\'s DNA file')
    parser.add_argument('--father', help='Path to father\'s DNA file')
    parser.add_argument('--output', default='.', help='Output directory (default: current directory)')
    parser.add_argument('--config', help='Path to config.yaml file')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO', help='Logging level')
    parser.add_argument('--format', choices=['pdf', 'json', 'csv'], default='pdf', help='Output format')
    parser.add_argument('--list-analyses', action='store_true', help='List all available analyses')

    args = parser.parse_args()

    # Validate required arguments
    if not args.list_analyses and not args.child:
        parser.error("--child is required unless --list-analyses is specified")

    # Handle list-analyses argument
    if args.list_analyses:
        list_analyses()
        sys.exit(0)

    # Setup logging
    setup_logging(log_level=getattr(logging, args.log_level))

    try:
        # Load configuration
        config = load_config(args.config)
        logging.info("Configuration loaded")

        # Validate input files
        validate_files(args.child, args.mother, args.father)
        logging.info("Input files validated")

        # Data processing
        logging.info("Starting data processing...")
        file_formats = {'child': 'AncestryDNA', 'mother': 'AncestryDNA', 'father': 'AncestryDNA'}
        family_data = process_family_data(
            child_file=args.child,
            mother_file=args.mother,
            father_file=args.father,
            file_formats=file_formats
        )
        logging.info("Data processing completed")

        # Prepare data for analyses
        family_dict = {}
        for col in family_data.harmonized_data.columns:
            member = col.replace('_genotype', '')
            family_dict[member] = family_data.harmonized_data[[col]].rename(columns={col: 'genotype'})

        # Individual analyses
        logging.info("Starting individual analyses...")
        individual_risks = {}
        for member, df in family_dict.items():
            logging.debug(f"Running analyses for {member}")
            individual_risks[member] = run_individual_analyses(df)
        logging.info("Individual analyses completed")

        # Family analyses
        logging.info("Starting family analyses...")
        risk_variants = ['rs1801133', 'rs4680', 'rs4988235']  # Common risk variants for testing
        family_results = run_family_analyses(
            family_data=family_dict,
            risk_variants=risk_variants,
            individual_risks=individual_risks
        )
        logging.info("Family analyses completed")

        # Reporting
        logging.info("Generating reports...")
        report_formats = [args.format] if args.format != 'pdf' else ['pdf']
        generated_files = generate_reports(
            analysis_results=individual_risks,
            family_analysis_results=family_results,
            output_dir=args.output,
            report_formats=report_formats,
            family_name="TestFamily"
        )
        logging.info(f"Reports generated: {generated_files}")

        logging.info("Analysis completed successfully")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
