"""
Ancestry Inference Module for Genetic Data Analysis

This module provides ancestry inference using ancestry-informative markers (AIMs)
to determine genetic ancestry from SNP data and support ancestry-adjusted PRS calculations.
"""

import os
import warnings
from functools import lru_cache
from typing import Dict, List, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

from .api_functions import get_api_health_status, get_gnomad_population_data
from .local_data_utils import LocalGeneticData


class AncestryInference:
    """
    Class for inferring genetic ancestry from SNP data using AIMs
    """

    def __init__(
        self, aims_file: str = "data/datasets/ancestry_informative_markers.tsv"
    ):
        """
        Initialize ancestry inference with AIMs data

        Args:
            aims_file: Path to AIMs database file
        """
        self.aims_file = aims_file
        self.aims_data = None
        self.reference_populations = {}
        self.pca_model = None
        self.knn_model = None
        self.ancestry_snps = None
        self._load_aims_data()
        self._load_ancestry_models()

    def _load_aims_data(self):
        """Load AIMs database and reference population frequencies."""
        try:
            if os.path.exists(self.aims_file):
                self.aims_data = pd.read_csv(self.aims_file, sep="\t")
                self._prepare_reference_data()
            else:
                # Use population frequencies as fallback for basic ancestry
                self._load_fallback_aims()
        except Exception as e:
            print(f"Error loading AIMs data: {e}")
            self._load_fallback_aims()

    def _load_fallback_aims(self):
        """Load basic AIMs from population frequencies as fallback."""
        try:
            local_data = LocalGeneticData()
            local_data.load_datasets()
            pop_freq = local_data._pop_freq_df

            if pop_freq is not None:
                # Select SNPs with high frequency differences between populations
                self.aims_data = self._create_basic_aims_from_pop_freq(pop_freq)
                self._prepare_reference_data()
        except Exception as e:
            print(f"Error loading fallback AIMs: {e}")

    def _create_basic_aims_from_pop_freq(self, pop_freq: pd.DataFrame) -> pd.DataFrame:
        """Create basic AIMs from population frequency data."""
        # Group by rsid and calculate frequency differences
        freq_pivot = pop_freq.pivot_table(
            index="rsid", columns="population", values="frequency", aggfunc="first"
        ).fillna(0)

        # Calculate maximum frequency difference across populations
        freq_pivot["max_diff"] = freq_pivot.max(axis=1) - freq_pivot.min(axis=1)

        # Select top 100 most informative SNPs
        top_snps = freq_pivot.nlargest(100, "max_diff").index

        # Create AIMs dataframe
        aims_list = []
        for rsid in top_snps:
            row = {"rsid": rsid}
            for pop in ["AFR", "AMR", "EAS", "EUR", "SAS"]:
                if pop in freq_pivot.columns:
                    row[f"{pop}_freq"] = freq_pivot.loc[rsid, pop]
            aims_list.append(row)

        return pd.DataFrame(aims_list)

    @lru_cache(maxsize=1)
    def _load_ancestry_models(self):
        """Load ancestry prediction models (PCA and KNN) with caching."""
        try:
            pca_path = "data/ancestry_pca_model.joblib"
            knn_path = "data/ancestry_knn_model.joblib"
            snps_path = "data/ancestry_snps.npy"

            if os.path.exists(pca_path):
                self.pca_model = joblib.load(pca_path)
            if os.path.exists(knn_path):
                self.knn_model = joblib.load(knn_path)
            if os.path.exists(snps_path):
                snp_data = np.load(snps_path, allow_pickle=True).item()
                self.ancestry_snps = snp_data["rsids"]
        except Exception as e:
            print(f"Warning: Could not load ancestry models: {e}")
            self.pca_model = None
            self.knn_model = None
            self.ancestry_snps = None

    def _prepare_reference_data(self):
        """Prepare reference population data for ancestry inference."""
        if self.aims_data is None:
            return

        # Define major population groups
        self.reference_populations = {
            "European": ["EUR"],
            "African": ["AFR"],
            "East_Asian": ["EAS"],
            "South_Asian": ["SAS"],
            "American": ["AMR"],
            "Admixed": ["EUR", "AFR", "AMR"],  # For admixed populations
        }

        # Extract frequency columns
        freq_cols = [col for col in self.aims_data.columns if col.endswith("_freq")]
        self.population_codes = [col.replace("_freq", "") for col in freq_cols]

    def infer_ancestry(self, snp_data: pd.DataFrame, method: str = "pca") -> Dict:
        """
        Infer genetic ancestry from SNP data

        Args:
            snp_data: DataFrame with columns ['rsid', 'genotype']
            method: Inference method ('frequency_based', 'pca', 'clustering')

        Returns:
            Dictionary with ancestry results
        """
        if self.aims_data is None:
            return {
                "success": False,
                "error": "AIMs data not available",
                "ancestry": "Unknown",
                "confidence": 0.0,
            }

        try:
            if method == "frequency_based":
                result = self._frequency_based_inference(snp_data)
                # Convert to new format
                return {
                    "success": result["success"],
                    "primary_ancestry": result.get("primary_ancestry", "Unknown"),
                    "probabilities": result.get("admixture_proportions", {}),
                }
            elif method == "pca":
                return self._pca_based_inference(snp_data)
            elif method == "clustering":
                result = self._clustering_based_inference(snp_data)
                # Convert to new format
                return {
                    "success": result["success"],
                    "primary_ancestry": result.get("primary_ancestry", "Unknown"),
                    "probabilities": result.get("admixture_proportions", {}),
                }
            else:
                return self._pca_based_inference(snp_data)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "ancestry": "Unknown",
                "confidence": 0.0,
            }

    def _frequency_based_inference(self, snp_data: pd.DataFrame) -> Dict:
        """Perform frequency-based ancestry inference with live gnoAD data when available."""
        # Check gnoAD API status
        health_status = get_api_health_status()
        gnomad_status = health_status.get("gnomad", {}).get("status", "unknown")
        use_live_gnomad = gnomad_status == "healthy"

        # Find common SNPs between data and AIMs
        # snp_data has rsid as index, aims_data has rsid as column
        snp_rsids = (
            set(snp_data.index) if hasattr(snp_data, "index") else set(snp_data["rsid"])
        )
        aims_rsids = (
            set(self.aims_data["rsid"]) if "rsid" in self.aims_data.columns else set()
        )
        common_snps = snp_rsids & aims_rsids

        if not common_snps:
            return {
                "success": False,
                "error": f"No AIMs found in SNP data. SNP rsids: {len(snp_rsids)}, AIMs rsids: {len(aims_rsids)}",
                "ancestry": "Unknown",
                "confidence": 0.0,
            }

        # Calculate ancestry scores for each population
        ancestry_scores = {}
        total_snps = len(common_snps)
        live_data_used = 0

        for pop in self.population_codes:
            freq_col = f"{pop}_freq"
            if freq_col not in self.aims_data.columns:
                continue

            score = 0
            snps_used = 0

            for rsid in common_snps:
                # Get user's genotype (rsid is the index)
                user_genotype = snp_data.loc[rsid, "genotype"]
                user_allele_count = self._count_effect_allele(user_genotype)

                # Try to get live gnoAD data first
                pop_freq = None
                if use_live_gnomad:
                    try:
                        gnomad_data = get_gnomad_population_data(rsid, use_cache=True)
                        if gnomad_data is not None:
                            # Map population codes to gnoAD populations
                            pop_mapping = {
                                "EUR": ["European", "EUR"],
                                "AFR": ["African", "AFR"],
                                "EAS": ["East Asian", "EAS"],
                                "SAS": ["South Asian", "SAS"],
                                "AMR": ["American", "AMR"],
                            }

                            if pop in pop_mapping:
                                for gnomad_pop in pop_mapping[pop]:
                                    pop_row = gnomad_data[
                                        gnomad_data["Population"].str.contains(
                                            gnomad_pop, case=False, na=False
                                        )
                                    ]
                                    if not pop_row.empty:
                                        pop_freq = pop_row["Frequency"].iloc[0]
                                        live_data_used += 1
                                        break
                    except Exception:
                        pass  # Fall back to local data

                # Use local data if live data not available
                if pop_freq is None:
                    pop_freq = self.aims_data.loc[
                        self.aims_data["rsid"] == rsid, freq_col
                    ].iloc[0]

                # Calculate similarity score
                expected_allele_count = 2 * pop_freq  # Expected alleles in diploid
                allele_diff = abs(user_allele_count - expected_allele_count)
                score += max(
                    0, 2 - allele_diff
                )  # Score from 0-2, higher is better match
                snps_used += 1

            if snps_used > 0:
                ancestry_scores[pop] = score / snps_used

        if not ancestry_scores:
            return {
                "success": False,
                "error": "No valid ancestry scores calculated",
                "ancestry": "Unknown",
                "confidence": 0.0,
            }

        # Determine primary ancestry
        best_pop = max(ancestry_scores, key=ancestry_scores.get)
        best_score = ancestry_scores[best_pop]

        # Calculate confidence based on score difference
        sorted_scores = sorted(ancestry_scores.values(), reverse=True)
        if len(sorted_scores) > 1:
            confidence = (
                sorted_scores[0] - sorted_scores[1]
            ) / 2.0  # Max difference is 2
        else:
            confidence = 0.5

        confidence = max(0.0, min(1.0, confidence))

        # Check for admixture
        admixture_proportions = self._calculate_admixture_proportions(ancestry_scores)

        result = {
            "success": True,
            "primary_ancestry": self._map_population_code(best_pop),
            "ancestry_code": best_pop,
            "confidence": confidence,
            "admixture_proportions": admixture_proportions,
            "snps_used": total_snps,
            "method": "frequency_based",
            "ancestry_scores": ancestry_scores,
            "live_gnomad_used": use_live_gnomad,
            "live_data_snps": live_data_used,
        }

        return result

    def _calculate_admixture_proportions(
        self, ancestry_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate admixture proportions for mixed ancestry."""
        if len(ancestry_scores) <= 1:
            best_pop = max(ancestry_scores, key=ancestry_scores.get)
            return {self._map_population_code(best_pop): 1.0}

        # Normalize scores to proportions
        total_score = sum(ancestry_scores.values())
        if total_score == 0:
            return {}

        proportions = {}
        for pop, score in ancestry_scores.items():
            proportion = score / total_score
            if proportion > 0.05:  # Only include significant proportions
                proportions[self._map_population_code(pop)] = proportion

        return proportions

    def _count_effect_allele(self, genotype: str) -> int:
        """Count effect alleles in genotype."""
        # For simplicity, assume first allele is effect allele
        # In practice, this should be based on actual effect alleles
        genotype = genotype.upper()
        if len(genotype) == 1:
            return 2 if genotype in ["A", "C", "G", "T"] else 0
        elif len(genotype) == 2:
            return genotype.count(genotype[0])  # Count major allele
        else:
            return 0

    def _map_population_code(self, code: str) -> str:
        """Map population code to readable name."""
        mapping = {
            "EUR": "European",
            "AFR": "African",
            "EAS": "East Asian",
            "SAS": "South Asian",
            "AMR": "American",
        }
        return mapping.get(code, code)

    def _pca_based_inference(self, snp_data: pd.DataFrame) -> Dict:
        """Perform PCA-based ancestry inference using pre-trained models."""
        if (
            self.pca_model is None
            or self.knn_model is None
            or self.ancestry_snps is None
        ):
            return {
                "success": False,
                "error": "Ancestry models not available. Run build_ancestry_model.py first.",
                "primary_ancestry": "Unknown",
                "probabilities": {},
            }

        try:
            # Find common SNPs between user data and model SNPs
            snp_rsids = (
                set(snp_data.index)
                if hasattr(snp_data, "index")
                else set(snp_data["rsid"])
            )
            common_snps = list(set(self.ancestry_snps) & snp_rsids)

            if not common_snps:
                return {
                    "success": False,
                    "error": f"No common SNPs found with ancestry model. Model has {len(self.ancestry_snps)} SNPs.",
                    "primary_ancestry": "Unknown",
                    "probabilities": {},
                }

            # Extract genotypes for common SNPs in model order
            model_snp_order = [snp for snp in self.ancestry_snps if snp in common_snps]
            genotypes = []

            for rsid in model_snp_order:
                genotype = snp_data.loc[rsid, "genotype"]
                # Convert genotype to numeric (0, 1, 2)
                allele_count = self._count_effect_allele(genotype)
                genotypes.append(allele_count)

            # If we don't have all SNPs, pad with mean values (simplified approach)
            if len(genotypes) < len(self.ancestry_snps):
                # Pad with zeros (mean-centered)
                genotypes.extend([0.0] * (len(self.ancestry_snps) - len(genotypes)))

            # Convert to numpy array
            genotypes = np.array(genotypes, dtype=float)

            # Apply PCA
            pca_coords = self.pca_model.transform(genotypes.reshape(1, -1))

            # Predict ancestry using KNN
            prediction = self.knn_model.predict(pca_coords)[0]
            probabilities = self.knn_model.predict_proba(pca_coords)[0]

            # Create probabilities dictionary
            pop_classes = self.knn_model.classes_
            prob_dict = {
                pop: float(prob) for pop, prob in zip(pop_classes, probabilities)
            }

            # Get primary ancestry
            primary_ancestry = self._map_population_code(prediction)

            return {
                "success": True,
                "primary_ancestry": primary_ancestry,
                "probabilities": prob_dict,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "primary_ancestry": "Unknown",
                "probabilities": {},
            }

    def _clustering_based_inference(self, snp_data: pd.DataFrame) -> Dict:
        """Perform clustering-based ancestry inference."""
        # Placeholder for clustering method
        return self._frequency_based_inference(snp_data)

    def get_ancestry_adjusted_parameters(
        self, inferred_ancestry: str, original_params: Dict
    ) -> Dict:
        """
        Get ancestry-adjusted parameters for PRS calculations

        Args:
            inferred_ancestry: Inferred ancestry group
            original_params: Original PRS parameters

        Returns:
            Adjusted parameters dictionary
        """
        adjustments = {
            "European": {
                "percentile_adjustment": 0.0,
                "effect_size_multiplier": 1.0,
                "ld_correction_factor": 1.0,
            },
            "African": {
                "percentile_adjustment": 0.05,  # Slight upward adjustment
                "effect_size_multiplier": 0.95,
                "ld_correction_factor": 0.9,
            },
            "East_Asian": {
                "percentile_adjustment": -0.03,  # Slight downward adjustment
                "effect_size_multiplier": 1.05,
                "ld_correction_factor": 1.1,
            },
            "South_Asian": {
                "percentile_adjustment": 0.02,
                "effect_size_multiplier": 0.98,
                "ld_correction_factor": 0.95,
            },
            "American": {
                "percentile_adjustment": 0.01,
                "effect_size_multiplier": 1.0,
                "ld_correction_factor": 1.0,
            },
        }

        ancestry_key = (
            inferred_ancestry.split()[0]
            if " " in inferred_ancestry
            else inferred_ancestry
        )
        adjustment = adjustments.get(ancestry_key, adjustments["European"])

        adjusted_params = original_params.copy()
        adjusted_params["ancestry_adjustment"] = adjustment
        adjusted_params["inferred_ancestry"] = inferred_ancestry

        return adjusted_params

    def validate_ancestry_inference(
        self, snp_data: pd.DataFrame, inferred_result: Dict
    ) -> Dict:
        """
        Validate ancestry inference results

        Args:
            snp_data: Original SNP data
            inferred_result: Inference results

        Returns:
            Validation metrics
        """
        validation = {
            "total_aims_available": (
                len(self.aims_data) if self.aims_data is not None else 0
            ),
            "aims_found_in_data": 0,
            "coverage_percentage": 0.0,
            "confidence_assessment": "Low",
            "warnings": [],
            "recommendations": [],
        }

        if self.aims_data is not None:
            common_snps = set(snp_data["rsid"]) & set(self.aims_data["rsid"])
            validation["aims_found_in_data"] = len(common_snps)
            validation["coverage_percentage"] = (
                len(common_snps) / len(self.aims_data) * 100
            )

        # Assess confidence
        if "confidence" in inferred_result:
            conf = inferred_result["confidence"]
            if conf > 0.8:
                validation["confidence_assessment"] = "High"
            elif conf > 0.6:
                validation["confidence_assessment"] = "Medium"
            else:
                validation["confidence_assessment"] = "Low"

        # Generate warnings and recommendations
        if validation["coverage_percentage"] < 50:
            validation["warnings"].append(
                "Low AIMs coverage - results may be unreliable"
            )
            validation["recommendations"].append(
                "Consider using more comprehensive SNP data"
            )

        if validation["confidence_assessment"] == "Low":
            validation["warnings"].append("Low confidence in ancestry inference")
            validation["recommendations"].append(
                "Manual ancestry specification recommended"
            )

        return validation


# Convenience functions
def infer_ancestry_from_snps(
    snp_data: pd.DataFrame, method: str = "frequency_based"
) -> Dict:
    """Convenience function for ancestry inference."""
    inference = AncestryInference()
    return inference.infer_ancestry(snp_data, method)


def get_ancestry_adjusted_prs_params(
    inferred_ancestry: str, original_params: Dict
) -> Dict:
    """Convenience function for ancestry-adjusted PRS parameters."""
    inference = AncestryInference()
    return inference.get_ancestry_adjusted_parameters(
        inferred_ancestry, original_params
    )
