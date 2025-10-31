#!/usr/bin/env python3
"""
Comprehensive Debugging Script for Genetic Analysis Pipeline

This script runs a DNA file through all analysis features to verify functionality
and identify any issues with the genetic analysis pipeline.

Usage: python debug_all_features.py <dna_file_path> [genome_build]

Arguments:
    dna_file_path: Path to the DNA file (AncestryDNA, 23andMe format)
    genome_build: Genome build ('GRCh37' or 'GRCh38', default: GRCh37)
"""

import logging
import os
import sys
import time
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

# Add src directory to path for imports
sys.path.append("src")

# Import analysis modules
try:
    from ancestry_inference import AncestryInference, infer_ancestry_from_snps
    from api_functions import get_api_health_status
    from bioinformatics_utils import *
    from genomewide_prs import GenomeWidePRS
    from local_data_utils import LocalGeneticData
    from run_analysis import (
        analyze_clinvar_variants,
        analyze_expanded_carrier_status,
        analyze_high_impact_risks,
        analyze_pgx_and_wellness,
        analyze_protective_variants,
        analyze_prs,
        analyze_recessive_carrier_status,
        process_dna_file,
    )
    from utils import *
except ImportError as e:
    print(f"ERROR: Failed to import required modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("debug_analysis.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class AnalysisDebugger:
    """Comprehensive debugger for genetic analysis pipeline"""

    def __init__(self, dna_file_path: str, genome_build: str = "GRCh37"):
        self.dna_file_path = dna_file_path
        self.genome_build = genome_build
        self.results = {}
        self.errors = []
        self.warnings = []
        self.start_time = time.time()

        # Check if file exists
        if not os.path.exists(dna_file_path):
            raise FileNotFoundError(f"DNA file not found: {dna_file_path}")

        logger.info(
            f"Initializing debugger for {dna_file_path} (build: {genome_build})"
        )

    def log_error(self, component: str, error: Exception, details: str = ""):
        """Log an error with context"""
        error_info = {
            "component": component,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "details": details,
            "traceback": traceback.format_exc(),
        }
        self.errors.append(error_info)
        logger.error(f"{component}: {error} - {details}")

    def log_warning(self, component: str, message: str):
        """Log a warning"""
        self.warnings.append({"component": component, "message": message})
        logger.warning(f"{component}: {message}")

    def log_success(self, component: str, message: str = ""):
        """Log successful completion"""
        logger.info(f"{component}: SUCCESS - {message}")

    def load_dna_data(self) -> pd.DataFrame:
        """Load and process DNA file"""
        try:
            logger.info("Loading DNA data...")
            df = process_dna_file(self.dna_file_path, self.genome_build)
            self.log_success("DNA Loading", f"Loaded {len(df)} SNPs")
            return df
        except Exception as e:
            self.log_error("DNA Loading", e, "Failed to load DNA file")
            raise

    def test_api_health(self) -> Dict:
        """Test API health status"""
        try:
            logger.info("Testing API health...")
            health = get_api_health_status()
            self.results["api_health"] = health

            # Check each API
            apis_to_check = ["gnomad", "clinvar", "pgs_catalog", "pharmgkb"]
            for api in apis_to_check:
                status = health.get(api, {}).get("status", "unknown")
                if status != "healthy":
                    self.log_warning("API Health", f"{api} API status: {status}")

            self.log_success("API Health", f"Checked {len(apis_to_check)} APIs")
            return health
        except Exception as e:
            self.log_error("API Health", e, "Failed to check API health")
            return {}

    def test_ancestry_inference(self, df: pd.DataFrame) -> Dict:
        """Test ancestry inference comprehensively"""
        try:
            logger.info("Testing ancestry inference...")

            # Debug: Check if rsid is the index or a column
            if "rsid" not in df.columns and df.index.name != "rsid":
                logger.error(
                    f"DataFrame missing 'rsid' column/index. Available columns: {list(df.columns)}, Index name: {df.index.name}"
                )
                return {
                    "success": False,
                    "error": "Missing rsid column/index in SNP data",
                }

            # Debug: Check ancestry file loading
            from ancestry_inference import AncestryInference

            ancestry_infer = AncestryInference()

            if ancestry_infer.aims_data is None:
                logger.error("Ancestry inference AIMs data not loaded")
                return {"success": False, "error": "AIMs data not available"}

            if "rsid" not in ancestry_infer.aims_data.columns:
                logger.error(
                    f"AIMs data missing 'rsid' column. Available columns: {list(ancestry_infer.aims_data.columns)}"
                )
                return {"success": False, "error": "AIMs data missing rsid column"}

            # Test basic ancestry inference
            ancestry_result = infer_ancestry_from_snps(df)

            if ancestry_result["success"]:
                self.log_success(
                    "Ancestry Inference",
                    f"Primary: {ancestry_result.get('primary_ancestry', 'Unknown')}, "
                    f"Confidence: {ancestry_result.get('confidence', 0):.2f}, "
                    f"SNPs used: {ancestry_result.get('snps_used', 0)}",
                )

                # Test ancestry adjustment parameters
                try:
                    from ancestry_inference import get_ancestry_adjusted_prs_params

                    adjustment_params = get_ancestry_adjusted_prs_params(
                        ancestry_result.get("primary_ancestry", "European")
                    )
                    self.log_success(
                        "Ancestry Adjustment",
                        f"Generated adjustment parameters for {ancestry_result.get('primary_ancestry', 'Unknown')}",
                    )
                except Exception as e:
                    self.log_warning(
                        "Ancestry Adjustment",
                        f"Failed to generate adjustment parameters: {e}",
                    )

                # Test ancestry validation
                try:
                    validation = ancestry_infer.validate_ancestry_inference(
                        df, ancestry_result
                    )
                    self.log_success(
                        "Ancestry Validation",
                        f"Coverage: {validation.get('coverage_percentage', 0):.1f}%, Confidence: {validation.get('confidence_assessment', 'Unknown')}",
                    )
                except Exception as e:
                    self.log_warning(
                        "Ancestry Validation", f"Failed to validate ancestry: {e}"
                    )

                # Test different inference methods
                try:
                    pca_result = ancestry_infer.infer_ancestry(df, method="pca")
                    if pca_result["success"]:
                        self.log_success(
                            "Ancestry PCA Method",
                            f"PCA result: {pca_result.get('primary_ancestry', 'Unknown')}",
                        )
                    else:
                        self.log_warning(
                            "Ancestry PCA Method",
                            f"PCA failed: {pca_result.get('error', 'Unknown')}",
                        )
                except Exception as e:
                    self.log_warning(
                        "Ancestry PCA Method", f"PCA method not available: {e}"
                    )

            else:
                self.log_warning(
                    "Ancestry Inference",
                    f"Failed: {ancestry_result.get('error', 'Unknown error')}",
                )

            self.results["ancestry"] = ancestry_result
            return ancestry_result
        except Exception as e:
            self.log_error("Ancestry Inference", e, "Ancestry inference failed")
            return {"success": False, "error": str(e)}

    def test_high_impact_risks(self, df: pd.DataFrame) -> pd.DataFrame:
        """Test high impact risk analysis"""
        try:
            logger.info("Testing high impact risk analysis...")
            risks_df = analyze_high_impact_risks(df)

            if not risks_df.empty:
                self.log_success(
                    "High Impact Risks", f"Found {len(risks_df)} risk variants"
                )
            else:
                self.log_success("High Impact Risks", "No high impact risks detected")

            self.results["high_impact_risks"] = risks_df
            return risks_df
        except Exception as e:
            self.log_error("High Impact Risks", e, "High impact risk analysis failed")
            return pd.DataFrame()

    def test_pgx_wellness(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Test PGx and wellness analysis comprehensively"""
        try:
            logger.info("Testing PGx and wellness analysis...")

            # Test PGx analysis
            pgx_df, wellness_df = analyze_pgx_and_wellness(df)

            self.log_success("PGx Analysis", f"Analyzed {len(pgx_df)} PGx variants")
            self.log_success(
                "Wellness Analysis", f"Analyzed {len(wellness_df)} wellness variants"
            )

            # Test individual wellness SNP analysis
            try:
                from utils import analyze_wellness_snps

                wellness_results = analyze_wellness_snps(df)
                found_snps = sum(
                    1
                    for result in wellness_results.values()
                    if result["genotype"] != "Not Found"
                )
                self.log_success(
                    "Individual Wellness SNPs",
                    f"Found {found_snps}/{len(wellness_results)} wellness SNPs in data",
                )
            except Exception as e:
                self.log_warning(
                    "Individual Wellness SNPs",
                    f"Failed to analyze individual SNPs: {e}",
                )

            # Test specific wellness categories
            wellness_categories = {
                "Nutrition": ["rs4988235", "rs762551", "rs601338"],
                "Fitness": ["rs1815739"],
                "Longevity": ["rs7726159", "rs2802292"],
                "Sleep": ["rs1801260", "rs11063118"],
            }

            for category, snps in wellness_categories.items():
                found_in_category = sum(1 for snp in snps if snp in df.index)
                self.log_success(
                    f"Wellness {category}",
                    f"Found {found_in_category}/{len(snps)} SNPs in {category.lower()} category",
                )

            self.results["pgx"] = pgx_df
            self.results["wellness"] = wellness_df
            return pgx_df, wellness_df
        except Exception as e:
            self.log_error("PGx/Wellness", e, "PGx and wellness analysis failed")
            return pd.DataFrame(), pd.DataFrame()

    def test_prs_analysis(self, df: pd.DataFrame) -> Dict:
        """Test PRS analysis comprehensively"""
        try:
            logger.info("Testing PRS analysis...")

            calculator = GenomeWidePRS()

            # Test PRS calculation methods
            try:
                # Test simple PRS calculation
                simple_model = {
                    "rsid": ["rs429358", "rs7412"],
                    "effect_weight": [0.5, 0.3],
                    "effect_allele": ["T", "C"],
                    "trait": "Test APOE PRS",
                }
                simple_result = calculator.calculate_simple_prs(df, simple_model)
                if simple_result["success"]:
                    self.log_success(
                        "Simple PRS", f"Score: {simple_result.get('prs_score', 0):.3f}"
                    )
                else:
                    self.log_warning(
                        "Simple PRS", f"Failed: {simple_result.get('error', 'Unknown')}"
                    )
            except Exception as e:
                self.log_warning("Simple PRS", f"Simple PRS test failed: {e}")

            # Test percentile calculation
            try:
                test_score = 1.5
                percentile = calculator.calculate_percentile(test_score, 1.0, 0.5)
                self.log_success(
                    "Percentile Calculation",
                    f"Score {test_score} = {percentile:.1f}th percentile",
                )
            except Exception as e:
                self.log_warning("Percentile Calculation", f"Failed: {e}")

            # Test ancestry-adjusted percentile
            try:
                adjusted_percentile = calculator.calculate_ancestry_adjusted_percentile(
                    test_score, 1.0, 0.5, "European"
                )
                self.log_success(
                    "Ancestry-Adjusted Percentile",
                    f"European adjustment: {adjusted_percentile:.1f}th percentile",
                )
            except Exception as e:
                self.log_warning("Ancestry-Adjusted Percentile", f"Failed: {e}")

            # Test with a few common PGS IDs
            test_pgs_ids = ["PGS000001", "PGS000002", "PGS000003"]  # Common disease PRS
            prs_results = []

            for pgs_id in test_pgs_ids:
                try:
                    result = calculator.calculate_genomewide_prs(
                        df, pgs_id, use_ancestry_adjustment=True
                    )
                    if result["success"]:
                        self.log_success(
                            f"PRS {pgs_id}",
                            f"Score: {result.get('prs_score', 0):.3f}, "
                            f"Percentile: {result.get('percentile', 0):.1f}, "
                            f"SNPs: {result.get('snps_used', 0)}/{result.get('total_snps', 0)}",
                        )
                    else:
                        self.log_warning(
                            f"PRS {pgs_id}",
                            f"Failed: {result.get('error', 'Unknown error')}",
                        )
                    prs_results.append(result)
                except Exception as e:
                    self.log_error(
                        f"PRS {pgs_id}", e, f"PRS calculation failed for {pgs_id}"
                    )
                    prs_results.append(
                        {"success": False, "error": str(e), "pgs_id": pgs_id}
                    )

            # Test PRS validation
            if prs_results and prs_results[0]["success"]:
                try:
                    validation = calculator.validate_prs_calculation(df, prs_results[0])
                    self.log_success(
                        "PRS Validation",
                        f"Coverage: {validation.get('coverage_percentage', 0):.1f}%",
                    )
                except Exception as e:
                    self.log_warning("PRS Validation", f"Failed: {e}")

            self.results["prs"] = prs_results
            return prs_results
        except Exception as e:
            self.log_error("PRS Analysis", e, "PRS analysis failed")
            return []

    def test_clinvar_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Test ClinVar variant analysis"""
        try:
            logger.info("Testing ClinVar analysis...")

            clinvar_path = "clinvar_pathogenic_variants.tsv"
            if not os.path.exists(clinvar_path):
                self.log_warning(
                    "ClinVar", "ClinVar TSV file not found, skipping analysis"
                )
                return pd.DataFrame()

            clinvar_df = analyze_clinvar_variants(df, clinvar_path)

            if not clinvar_df.empty:
                self.log_success("ClinVar", f"Found {len(clinvar_df)} ClinVar variants")
            else:
                self.log_success("ClinVar", "No ClinVar variants detected")

            self.results["clinvar"] = clinvar_df
            return clinvar_df
        except Exception as e:
            self.log_error("ClinVar", e, "ClinVar analysis failed")
            return pd.DataFrame()

    def test_carrier_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Test carrier status analysis"""
        try:
            logger.info("Testing carrier status analysis...")
            carrier_df = analyze_recessive_carrier_status(df)

            if not carrier_df.empty:
                self.log_success(
                    "Carrier Status", f"Analyzed {len(carrier_df)} carrier conditions"
                )
            else:
                self.log_success("Carrier Status", "No carrier analysis results")

            self.results["carrier_status"] = carrier_df
            return carrier_df
        except Exception as e:
            self.log_error("Carrier Status", e, "Carrier status analysis failed")
            return pd.DataFrame()

    def test_protective_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Test protective variant analysis"""
        try:
            logger.info("Testing protective variant analysis...")
            protective_df = analyze_protective_variants(df)

            if not protective_df.empty:
                self.log_success(
                    "Protective Variants",
                    f"Analyzed {len(protective_df)} protective variants",
                )
            else:
                self.log_success(
                    "Protective Variants", "No protective variants detected"
                )

            self.results["protective_variants"] = protective_df
            return protective_df
        except Exception as e:
            self.log_error(
                "Protective Variants", e, "Protective variant analysis failed"
            )
            return pd.DataFrame()

    def test_expanded_carrier_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Test expanded carrier status analysis"""
        try:
            logger.info("Testing expanded carrier analysis...")
            expanded_carrier_df = analyze_expanded_carrier_status(df)

            if not expanded_carrier_df.empty:
                self.log_success(
                    "Expanded Carrier",
                    f"Analyzed {len(expanded_carrier_df)} expanded carrier conditions",
                )
            else:
                self.log_success(
                    "Expanded Carrier", "No expanded carrier variants detected"
                )

            self.results["expanded_carrier"] = expanded_carrier_df
            return expanded_carrier_df
        except Exception as e:
            self.log_error("Expanded Carrier", e, "Expanded carrier analysis failed")
            return pd.DataFrame()

    def test_data_loading(self) -> Dict:
        """Test local data loading"""
        try:
            logger.info("Testing local data loading...")
            local_data = LocalGeneticData()
            local_data.load_datasets()

            data_status = {
                "pop_freq_loaded": local_data._pop_freq_df is not None,
                "gene_annot_loaded": local_data._gene_df is not None,
                "snp_annot_loaded": local_data._snp_df is not None,
            }

            success_count = sum(data_status.values())
            self.log_success(
                "Data Loading", f"Successfully loaded {success_count}/3 datasets"
            )

            for dataset, loaded in data_status.items():
                if not loaded:
                    self.log_warning("Data Loading", f"Failed to load {dataset}")

            self.results["data_loading"] = data_status
            return data_status
        except Exception as e:
            self.log_error("Data Loading", e, "Local data loading failed")
            return {}

    def generate_report(self):
        """Generate comprehensive debug report"""
        end_time = time.time()
        duration = end_time - self.start_time

        report = {
            "timestamp": datetime.now().isoformat(),
            "dna_file": self.dna_file_path,
            "genome_build": self.genome_build,
            "duration_seconds": duration,
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings),
            "results": self.results,
            "errors": self.errors,
            "warnings": self.warnings,
        }

        # Print summary to console
        print("\n" + "=" * 80)
        print("DEBUG ANALYSIS REPORT")
        print("=" * 80)
        print(f"DNA File: {self.dna_file_path}")
        print(f"Genome Build: {self.genome_build}")
        print(".2f")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")
        print()

        # Component status
        components = [
            "DNA Loading",
            "API Health",
            "Ancestry Inference",
            "High Impact Risks",
            "PGx Analysis",
            "Wellness Analysis",
            "PRS Analysis",
            "ClinVar",
            "Carrier Status",
            "Protective Variants",
            "Expanded Carrier",
            "Data Loading",
        ]

        print("COMPONENT STATUS:")
        for component in components:
            status = (
                "PASS"
                if component.lower().replace(" ", "_") in self.results
                else "FAIL"
            )
            print(f"  {component:<20} {status}")

        print("\nERRORS:")
        if self.errors:
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error['component']}: {error['error_message']}")
        else:
            print("  No errors detected")

        print("\nWARNINGS:")
        if self.warnings:
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning['component']}: {warning['message']}")
        else:
            print("  No warnings detected")

        print("\n" + "=" * 80)

        # Save detailed report
        report_file = f"debug_report_{int(time.time())}.json"
        import json

        with open(report_file, "w") as f:
            # Convert DataFrames to dict for JSON serialization
            json_report = report.copy()
            for key, value in json_report["results"].items():
                if isinstance(value, pd.DataFrame):
                    json_report["results"][key] = value.to_dict("records")
            json.dump(json_report, f, indent=2, default=str)

        print(f"Detailed report saved to: {report_file}")
        print(f"Log file: debug_analysis.log")

    def run_all_tests(self):
        """Run all debugging tests"""
        try:
            # Load DNA data first
            df = self.load_dna_data()

            # Test data loading
            self.test_data_loading()

            # Test API health
            self.test_api_health()

            # Run all analyses
            self.test_ancestry_inference(df)
            self.test_high_impact_risks(df)
            self.test_pgx_wellness(df)
            self.test_prs_analysis(df)
            self.test_clinvar_analysis(df)
            self.test_carrier_analysis(df)
            self.test_protective_analysis(df)
            self.test_expanded_carrier_analysis(df)

            # Generate report
            self.generate_report()

        except Exception as e:
            logger.error(f"Critical error during debugging: {e}")
            logger.error(traceback.format_exc())
            print(f"\nCRITICAL ERROR: {e}")
            print("Check debug_analysis.log for details")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python debug_all_features.py <dna_file_path> [genome_build]")
        print("  dna_file_path: Path to DNA file (AncestryDNA, 23andMe format)")
        print("  genome_build: GRCh37 or GRCh38 (default: GRCh37)")
        sys.exit(1)

    dna_file = sys.argv[1]
    genome_build = sys.argv[2] if len(sys.argv) > 2 else "GRCh37"

    print(f"Starting comprehensive debug analysis...")
    print(f"DNA File: {dna_file}")
    print(f"Genome Build: {genome_build}")
    print()

    debugger = AnalysisDebugger(dna_file, genome_build)
    debugger.run_all_tests()


if __name__ == "__main__":
    main()
