"""
Parallel Processing Utilities for Genetic Analysis

This module provides Dask-based parallel execution of genetic analyses
with proper error handling and backward compatibility.
"""

from typing import Callable, Dict, List, Optional, Tuple

import pandas as pd

from .utils import CONFIG

# Optional Dask dependency
try:
    import dask
    from dask import delayed
    from dask.distributed import Client, LocalCluster

    DASK_AVAILABLE = True
except ImportError:
    DASK_AVAILABLE = False


class ParallelGeneticAnalysis:
    """Orchestrates parallel execution of genetic analyses using Dask."""

    def __init__(self):
        self.client = None
        self._init_dask()

    def _init_dask(self):
        """Initialize Dask client if parallel processing is enabled."""
        if (
            not CONFIG["performance"]["enable_parallel_processing"]
            or not DASK_AVAILABLE
        ):
            return

        try:
            if CONFIG["parallel"]["scheduler"] == "processes":
                self.client = Client(
                    processes=True,
                    threads_per_worker=1,
                    n_workers=CONFIG["parallel"]["num_workers"] or None,
                )
            elif CONFIG["parallel"]["scheduler"] == "threads":
                self.client = Client(
                    processes=False,
                    threads_per_worker=2,
                    n_workers=CONFIG["parallel"]["num_workers"] or None,
                )
            else:
                # Synchronous scheduler for debugging
                pass

            if self.client:
                print(f"Dask client initialized with {self.client.ncores()} cores")

        except Exception as e:
            print(
                f"Failed to initialize Dask client: {e}. Falling back to sequential processing."
            )
            self.client = None

    def run_analyses_parallel(self, df: pd.DataFrame, results_dir: str) -> Dict:
        """
        Run all genetic analyses in parallel

        Args:
            df: SNP data DataFrame
            results_dir: Directory for results

        Returns:
            Dictionary with analysis results
        """
        if (
            not CONFIG["performance"]["enable_parallel_processing"]
            or not DASK_AVAILABLE
            or not self.client
        ):
            # Fallback to sequential execution
            return self._run_analyses_sequential(df, results_dir)

        try:
            # Import analysis functions here to avoid circular imports
            from .run_analysis import (
                analyze_clinvar_variants,
                analyze_expanded_carrier_status,
                analyze_high_impact_risks,
                analyze_pgx_and_wellness,
                analyze_protective_variants,
                analyze_prs,
                analyze_recessive_carrier_status,
            )

            # Create delayed tasks
            high_impact_task = delayed(analyze_high_impact_risks)(df)
            pgx_wellness_task = delayed(analyze_pgx_and_wellness)(df)
            prs_task = delayed(analyze_prs)(df, results_dir)
            clinvar_task = delayed(analyze_clinvar_variants)(
                df, None
            )  # Will handle missing file
            carrier_task = delayed(analyze_recessive_carrier_status)(df)
            protective_task = delayed(analyze_protective_variants)(df)
            expanded_carrier_task = delayed(analyze_expanded_carrier_status)(df)

            # Execute in parallel
            print("Running analyses in parallel...")
            results = dask.compute(
                high_impact_task,
                pgx_wellness_task,
                prs_task,
                clinvar_task,
                carrier_task,
                protective_task,
                expanded_carrier_task,
            )

            # Package results
            analysis_results = {
                "high_impact": results[0],
                "pgx": results[1][0],
                "wellness": results[1][1],
                "prs": None,  # PRS returns None, generates files
                "clinvar": results[3],
                "carrier_status": results[4],
                "protective_variants": results[5],
                "expanded_carrier": results[6],
                "parallel_execution": True,
            }

            print("Parallel analyses completed successfully")
            return analysis_results

        except Exception as e:
            print(
                f"Parallel execution failed: {e}. Falling back to sequential processing."
            )
            return self._run_analyses_sequential(df, results_dir)

    def _run_analyses_sequential(self, df: pd.DataFrame, results_dir: str) -> Dict:
        """
        Run analyses sequentially as fallback

        Args:
            df: SNP data DataFrame
            results_dir: Directory for results

        Returns:
            Dictionary with analysis results
        """
        from .run_analysis import (
            analyze_clinvar_variants,
            analyze_expanded_carrier_status,
            analyze_high_impact_risks,
            analyze_pgx_and_wellness,
            analyze_protective_variants,
            analyze_prs,
            analyze_recessive_carrier_status,
        )

        print("Running analyses sequentially...")

        high_impact = analyze_high_impact_risks(df)
        pgx, wellness = analyze_pgx_and_wellness(df)
        analyze_prs(df, results_dir)  # Generates files, no return
        clinvar = analyze_clinvar_variants(df, None)
        carrier = analyze_recessive_carrier_status(df)
        protective = analyze_protective_variants(df)
        expanded_carrier = analyze_expanded_carrier_status(df)

        return {
            "high_impact": high_impact,
            "pgx": pgx,
            "wellness": wellness,
            "prs": None,
            "clinvar": clinvar,
            "carrier_status": carrier,
            "protective_variants": protective,
            "expanded_carrier": expanded_carrier,
            "parallel_execution": False,
        }

    def close(self):
        """Close Dask client."""
        if self.client:
            self.client.close()


# Global instance
parallel_analyzer = ParallelGeneticAnalysis()


def run_parallel_analyses(df: pd.DataFrame, results_dir: str) -> Dict:
    """
    Convenience function to run parallel analyses

    Args:
        df: SNP data DataFrame
        results_dir: Directory for results

    Returns:
        Dictionary with analysis results
    """
    return parallel_analyzer.run_analyses_parallel(df, results_dir)
