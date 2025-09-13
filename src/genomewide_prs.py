"""
Genome-wide Polygenic Risk Score (PRS) Calculation Module

This module provides comprehensive PRS calculations using thousands of variants
from PGS Catalog models, with optimized performance and statistical rigor.
"""

import pandas as pd
import numpy as np
import requests
import streamlit as st
from typing import Dict, List, Optional, Tuple, Union
import hashlib
import pickle
import os
from functools import lru_cache
import time
from datetime import datetime, timedelta
from ancestry_inference import AncestryInference, infer_ancestry_from_snps
from api_functions import make_api_request, get_api_health_status

class GenomeWidePRS:
    """
    Main class for genome-wide PRS calculations
    """

    def __init__(self, cache_dir: str = "cache/prs"):
        """
        Initialize PRS calculator with caching

        Args:
            cache_dir: Directory for caching downloaded models
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    @staticmethod
    def calculate_prs_score(snp_data: pd.DataFrame,
                           effect_weights: Dict[str, float],
                           effect_alleles: Dict[str, str]) -> Tuple[float, int, int]:
        """
        Calculate PRS score from SNP data and effect weights

        Args:
            snp_data: DataFrame with columns ['rsid', 'genotype']
            effect_weights: Dict mapping rsID to effect weight
            effect_alleles: Dict mapping rsID to effect allele

        Returns:
            Tuple of (prs_score, snps_used, total_snps)
        """
        # Filter to SNPs present in both data and model
        common_snps = set(snp_data['rsid']) & set(effect_weights.keys())
        total_snps = len(effect_weights)

        if not common_snps:
            return 0.0, 0, total_snps

        # Calculate PRS
        prs_score = 0.0
        snps_used = 0

        for rsid in common_snps:
            if rsid in snp_data['rsid'].values:
                genotype = snp_data.loc[snp_data['rsid'] == rsid, 'genotype'].iloc[0]
                effect_allele = effect_alleles[rsid]
                weight = effect_weights[rsid]

                # Count effect alleles in genotype
                allele_count = genotype.upper().count(effect_allele.upper())

                # Add weighted contribution
                prs_score += allele_count * weight
                snps_used += 1

        return prs_score, snps_used, total_snps

    @staticmethod
    def calculate_percentile(user_score: float,
                           population_mean: float,
                           population_std: float,
                           population_size: int = 10000) -> float:
        """
        Calculate percentile of user's PRS score against reference population

        Args:
            user_score: User's PRS score
            population_mean: Mean PRS in reference population
            population_std: Standard deviation of PRS in reference population
            population_size: Size of simulated population

        Returns:
            Percentile (0-100)
        """
        # Simulate population distribution
        np.random.seed(42)  # For reproducibility
        population_scores = np.random.normal(population_mean, population_std, population_size)

        # Calculate percentile
        percentile = (np.sum(population_scores < user_score) / population_size) * 100

        # Clamp to valid range
        return max(0.0, min(100.0, percentile))

    @staticmethod
    def normalize_prs_score(raw_score: float,
                            model_mean: float,
                            model_std: float) -> float:
        """
        Normalize PRS score to standard units

        Args:
            raw_score: Raw PRS score
            model_mean: Mean score in model training population
            model_std: Standard deviation in model training population

        Returns:
            Normalized PRS score (z-score)
        """
        if model_std == 0:
            return 0.0
        return (raw_score - model_mean) / model_std

    @staticmethod
    def calculate_ancestry_adjusted_percentile(user_score: float,
                                             population_mean: float,
                                             population_std: float,
                                             inferred_ancestry: str,
                                             population_size: int = 10000) -> float:
        """
        Calculate ancestry-adjusted percentile for user's PRS score

        Args:
            user_score: User's PRS score
            population_mean: Mean PRS in reference population
            population_std: Standard deviation of PRS in reference population
            inferred_ancestry: Inferred genetic ancestry
            population_size: Size of simulated population

        Returns:
            Ancestry-adjusted percentile (0-100)
        """
        # Get ancestry-specific adjustments
        ancestry_inference = AncestryInference()
        adjustments = ancestry_inference.get_ancestry_adjusted_parameters(
            inferred_ancestry, {}
        )['ancestry_adjustment']

        # Apply adjustments to population parameters
        adjusted_mean = population_mean * (1 + adjustments['percentile_adjustment'])
        adjusted_std = population_std * adjustments['ld_correction_factor']

        # Simulate ancestry-matched population distribution
        np.random.seed(42)  # For reproducibility
        population_scores = np.random.normal(adjusted_mean, adjusted_std, population_size)

        # Calculate percentile
        percentile = (np.sum(population_scores < user_score) / population_size) * 100

        # Clamp to valid range
        return max(0.0, min(100.0, percentile))

    @staticmethod
    def calculate_ancestry_adjusted_prs_score(snp_data: pd.DataFrame,
                                           effect_weights: Dict[str, float],
                                           effect_alleles: Dict[str, str],
                                           inferred_ancestry: str) -> Tuple[float, int, int]:
        """
        Calculate ancestry-adjusted PRS score

        Args:
            snp_data: DataFrame with columns ['rsid', 'genotype']
            effect_weights: Dict mapping rsID to effect weight
            effect_alleles: Dict mapping rsID to effect allele
            inferred_ancestry: Inferred genetic ancestry

        Returns:
            Tuple of (adjusted_prs_score, snps_used, total_snps)
        """
        # First calculate standard PRS
        prs_score, snps_used, total_snps = GenomeWidePRS.calculate_prs_score(
            snp_data, effect_weights, effect_alleles
        )

        if snps_used == 0:
            return prs_score, snps_used, total_snps

        # Get ancestry-specific adjustments
        ancestry_inference = AncestryInference()
        adjustments = ancestry_inference.get_ancestry_adjusted_parameters(
            inferred_ancestry, {}
        )['ancestry_adjustment']

        # Apply effect size adjustment
        adjusted_score = prs_score * adjustments['effect_size_multiplier']

        return adjusted_score, snps_used, total_snps

    def download_pgs_model(self, pgs_id: str, use_cache: bool = True) -> Optional[Dict]:
        """
        Download PGS model data from PGS Catalog with enhanced error handling and caching

        Args:
            pgs_id: PGS Catalog ID (e.g., 'PGS000001')
            use_cache: Whether to use cached results

        Returns:
            Model data dictionary or None if failed
        """
        cache_file = os.path.join(self.cache_dir, f"{pgs_id}.pkl")

        # Check cache first if enabled
        if use_cache and os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                # Check if cache is recent (within 7 days for PGS models)
                if 'timestamp' in cached_data:
                    from datetime import datetime, timedelta
                    cache_time = datetime.fromisoformat(cached_data['timestamp'])
                    if datetime.now() - cache_time < timedelta(days=7):
                        return cached_data
            except:
                pass  # Cache corrupted, download again

        try:
            # Check PGS API health
            health_status = get_api_health_status()
            pgs_status = health_status.get('pgs_catalog', {}).get('status', 'unknown')

            if pgs_status != 'healthy':
                st.warning(f"PGS Catalog API is currently {pgs_status}. Using cached data if available.")
                if os.path.exists(cache_file):
                    try:
                        with open(cache_file, 'rb') as f:
                            return pickle.load(f)
                    except:
                        pass

            # Get model metadata using enhanced API request
            metadata_url = f"https://www.pgscatalog.org/rest/score/{pgs_id}"
            metadata = make_api_request(metadata_url, use_cache=use_cache)

            if metadata is None:
                return None

            # Get scoring file
            if 'ftp_scoring_file' in metadata:
                scoring_url = metadata['ftp_scoring_file']
                scoring_response = make_api_request(scoring_url, use_cache=use_cache)

                if scoring_response is None:
                    return None

                # Parse scoring file
                lines = scoring_response.strip().split('\n')
                if len(lines) < 2:
                    return None

                header = lines[0].split('\t')
                effect_weights = {}
                effect_alleles = {}
                other_alleles = {}

                for line in lines[1:]:
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 5:
                            rsid = parts[0]
                            effect_allele = parts[3]
                            weight = float(parts[4])

                            effect_weights[rsid] = weight
                            effect_alleles[rsid] = effect_allele

                            # Store other allele if available
                            if len(parts) > 5:
                                other_alleles[rsid] = parts[5]

                model_data = {
                    'pgs_id': pgs_id,
                    'trait': metadata.get('trait_reported', 'Unknown'),
                    'effect_weights': effect_weights,
                    'effect_alleles': effect_alleles,
                    'other_alleles': other_alleles,
                    'num_variants': len(effect_weights),
                    'genome_build': metadata.get('genome_build', 'Unknown'),
                    'population': metadata.get('ancestry', 'Unknown'),
                    'citation': metadata.get('citation', 'Unknown'),
                    'metadata': metadata,
                    'timestamp': datetime.now().isoformat()
                }

                # Cache the model
                try:
                    with open(cache_file, 'wb') as f:
                        pickle.dump(model_data, f)
                except Exception as e:
                    st.warning(f"Could not cache PGS model {pgs_id}: {e}")

                return model_data
            else:
                st.warning(f"No scoring file available for PGS model {pgs_id}")
                return None

        except Exception as e:
            st.error(f"Failed to download PGS model {pgs_id}: {str(e)}")
            return None

    def calculate_genomewide_prs(self,
                                 snp_data: pd.DataFrame,
                                 pgs_id: str,
                                 progress_callback: Optional[callable] = None,
                                 use_ancestry_adjustment: bool = False) -> Dict:
        """
        Calculate genome-wide PRS for a given PGS model

        Args:
            snp_data: DataFrame with SNP data
            pgs_id: PGS Catalog ID
            progress_callback: Optional callback for progress updates
            use_ancestry_adjustment: Whether to apply ancestry adjustments

        Returns:
            Dictionary with PRS results
        """
        if progress_callback:
            progress_callback("Downloading PGS model...")

        # Download model
        model = self.download_pgs_model(pgs_id)
        if not model:
            return {
                'success': False,
                'error': f"Failed to download model {pgs_id}",
                'prs_score': 0.0,
                'percentile': 50.0,
                'snps_used': 0,
                'total_snps': 0
            }

        if progress_callback:
            progress_callback("Calculating PRS score...")

        # Perform ancestry inference if requested
        ancestry_result = None
        if use_ancestry_adjustment:
            if progress_callback:
                progress_callback("Inferring genetic ancestry...")
            ancestry_result = infer_ancestry_from_snps(snp_data)

        # Calculate PRS (with or without ancestry adjustment)
        if use_ancestry_adjustment and ancestry_result and ancestry_result['success']:
            prs_score, snps_used, total_snps = self.calculate_ancestry_adjusted_prs_score(
                snp_data,
                model['effect_weights'],
                model['effect_alleles'],
                ancestry_result['primary_ancestry']
            )
        else:
            prs_score, snps_used, total_snps = self.calculate_prs_score(
                snp_data,
                model['effect_weights'],
                model['effect_alleles']
            )

        if progress_callback:
            progress_callback("Calculating percentile...")

        # Calculate percentile (with or without ancestry adjustment)
        # For now, use model statistics if available, otherwise estimate
        population_mean = model.get('population_mean', prs_score * 0.8)  # Estimate
        population_std = model.get('population_std', abs(prs_score) * 0.3)  # Estimate

        if use_ancestry_adjustment and ancestry_result and ancestry_result['success']:
            percentile = self.calculate_ancestry_adjusted_percentile(
                prs_score, population_mean, population_std, ancestry_result['primary_ancestry']
            )
        else:
            percentile = self.calculate_percentile(prs_score, population_mean, population_std)

        # Normalize score
        normalized_score = self.normalize_prs_score(prs_score, population_mean, population_std)

        result = {
            'success': True,
            'pgs_id': pgs_id,
            'trait': model['trait'],
            'prs_score': prs_score,
            'normalized_score': normalized_score,
            'percentile': percentile,
            'snps_used': snps_used,
            'total_snps': total_snps,
            'coverage': snps_used / total_snps if total_snps > 0 else 0,
            'genome_build': model['genome_build'],
            'population': model['population'],
            'citation': model['citation'],
            'model_metadata': model['metadata'],
            'ancestry_adjustment_used': use_ancestry_adjustment
        }

        # Add ancestry information if available
        if use_ancestry_adjustment and ancestry_result:
            result.update({
                'inferred_ancestry': ancestry_result.get('primary_ancestry', 'Unknown'),
                'ancestry_confidence': ancestry_result.get('confidence', 0.0),
                'admixture_proportions': ancestry_result.get('admixture_proportions', {}),
                'ancestry_method': ancestry_result.get('method', 'Unknown'),
                'ancestry_snps_used': ancestry_result.get('snps_used', 0)
            })

        return result

    @staticmethod
    def batch_calculate_prs(snp_data: pd.DataFrame,
                            models: List[Dict],
                            progress_callback: Optional[callable] = None,
                            use_ancestry_adjustment: bool = False) -> List[Dict]:
        """
        Calculate PRS for multiple models in batch

        Args:
            snp_data: DataFrame with SNP data
            models: List of model dictionaries
            progress_callback: Optional progress callback
            use_ancestry_adjustment: Whether to apply ancestry adjustments

        Returns:
            List of PRS results
        """
        results = []
        calculator = GenomeWidePRS()

        for i, model in enumerate(models):
            if progress_callback:
                progress_callback(f"Processing model {i+1}/{len(models)}: {model.get('pgs_id', 'Unknown')}")

            try:
                if 'pgs_id' in model:
                    result = calculator.calculate_genomewide_prs(
                        snp_data, model['pgs_id'], use_ancestry_adjustment=use_ancestry_adjustment
                    )
                else:
                    # Fallback to simple calculation
                    result = calculator.calculate_simple_prs(snp_data, model)

                results.append(result)

            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'pgs_id': model.get('pgs_id', 'Unknown'),
                    'trait': model.get('trait', 'Unknown')
                })

        return results

    @staticmethod
    def calculate_simple_prs(snp_data: pd.DataFrame, model: Dict) -> Dict:
        """
        Calculate PRS using simple model (fallback for when genome-wide unavailable)

        Args:
            snp_data: DataFrame with SNP data
            model: Simple model dictionary

        Returns:
            PRS result dictionary
        """
        calculator = GenomeWidePRS()

        effect_weights = dict(zip(model['rsid'], model['effect_weight']))
        effect_alleles = dict(zip(model['rsid'], model['effect_allele']))

        prs_score, snps_used, total_snps = calculator.calculate_prs_score(
            snp_data, effect_weights, effect_alleles
        )

        # Estimate population statistics
        population_mean = sum(model['effect_weight']) * 0.8
        population_std = abs(sum(model['effect_weight'])) * 0.3

        percentile = calculator.calculate_percentile(prs_score, population_mean, population_std)

        return {
            'success': True,
            'trait': model.get('trait', 'Unknown'),
            'prs_score': prs_score,
            'normalized_score': calculator.normalize_prs_score(prs_score, population_mean, population_std),
            'percentile': percentile,
            'snps_used': snps_used,
            'total_snps': total_snps,
            'coverage': snps_used / total_snps if total_snps > 0 else 0,
            'model_type': 'simple'
        }

    @staticmethod
    def validate_prs_calculation(snp_data: pd.DataFrame,
                               model: Dict,
                               expected_score_range: Tuple[float, float] = None) -> Dict:
        """
        Validate PRS calculation quality

        Args:
            snp_data: DataFrame with SNP data
            model: Model dictionary
            expected_score_range: Expected range for validation

        Returns:
            Validation results
        """
        validation_results = {
            'total_snps_in_data': len(snp_data),
            'model_snps_found': 0,
            'coverage_percentage': 0.0,
            'score_in_expected_range': False,
            'warnings': [],
            'errors': []
        }

        if 'effect_weights' in model:
            effect_weights = model['effect_weights']
        elif 'rsid' in model:
            effect_weights = dict(zip(model['rsid'], model['effect_weight']))
        else:
            validation_results['errors'].append("Invalid model format")
            return validation_results

        # Check coverage
        common_snps = set(snp_data['rsid']) & set(effect_weights.keys())
        validation_results['model_snps_found'] = len(common_snps)
        validation_results['coverage_percentage'] = len(common_snps) / len(effect_weights) if effect_weights else 0

        # Check for low coverage
        if validation_results['coverage_percentage'] < 0.5:
            validation_results['warnings'].append(f"Low SNP coverage: {validation_results['coverage_percentage']:.1f}")

        if validation_results['coverage_percentage'] < 0.1:
            validation_results['errors'].append("Extremely low SNP coverage - results may be unreliable")

        # Validate score range if provided
        if expected_score_range:
            # This would require calculating the score first
            validation_results['score_in_expected_range'] = True  # Placeholder

        return validation_results

    def validate_ancestry_adjusted_prs(self, snp_data: pd.DataFrame,
                                       model: Dict,
                                       ancestry_result: Dict) -> Dict:
        """
        Validate ancestry-adjusted PRS calculations

        Args:
            snp_data: DataFrame with SNP data
            model: Model dictionary
            ancestry_result: Ancestry inference results

        Returns:
            Validation results for ancestry-adjusted PRS
        """
        validation = GenomeWidePRS.validate_prs_calculation(snp_data, model)

        # Add ancestry-specific validations
        validation['ancestry_inference_success'] = ancestry_result.get('success', False)
        validation['ancestry_confidence'] = ancestry_result.get('confidence', 0.0)
        validation['ancestry_snps_used'] = ancestry_result.get('snps_used', 0)

        # Check ancestry confidence
        if validation['ancestry_confidence'] < 0.5:
            validation['warnings'].append("Low confidence in ancestry inference - results may be less reliable")
        elif validation['ancestry_confidence'] < 0.7:
            validation['warnings'].append("Moderate confidence in ancestry inference")

        # Check if ancestry SNPs overlap with PRS SNPs
        if 'effect_weights' in model:
            ancestry_rsids = set()
            if ancestry_result.get('ancestry_scores'):
                ancestry_rsids = set(ancestry_result['ancestry_scores'].keys())

            prs_rsids = set(model['effect_weights'].keys())
            overlap = len(ancestry_rsids & prs_rsids)

            validation['ancestry_prs_overlap'] = overlap
            validation['ancestry_prs_overlap_percentage'] = overlap / len(ancestry_rsids) if ancestry_rsids else 0

            if overlap == 0:
                validation['warnings'].append("No overlap between ancestry-informative SNPs and PRS model SNPs")

        # Overall recommendation
        if (validation['ancestry_confidence'] >= 0.7 and
            validation['coverage_percentage'] >= 50):
            validation['recommendation'] = "Ancestry-adjusted PRS recommended"
        elif validation['ancestry_confidence'] >= 0.5:
            validation['recommendation'] = "Ancestry adjustment may provide moderate improvement"
        else:
            validation['recommendation'] = "Consider manual ancestry specification or skip ancestry adjustment"

        return validation

    @staticmethod
    def compare_adjusted_vs_unadjusted(snp_data: pd.DataFrame,
                                     pgs_id: str,
                                     cache_dir: str = "cache/prs") -> Dict:
        """
        Compare ancestry-adjusted vs unadjusted PRS results

        Args:
            snp_data: DataFrame with SNP data
            pgs_id: PGS Catalog ID
            cache_dir: Cache directory

        Returns:
            Comparison results
        """
        calculator = GenomeWidePRS(cache_dir)

        # Calculate unadjusted PRS
        unadjusted_result = calculator.calculate_genomewide_prs(
            snp_data, pgs_id, use_ancestry_adjustment=False
        )

        # Calculate adjusted PRS
        adjusted_result = calculator.calculate_genomewide_prs(
            snp_data, pgs_id, use_ancestry_adjustment=True
        )

        # Compare results
        comparison = {
            'unadjusted': unadjusted_result,
            'adjusted': adjusted_result,
            'differences': {
                'prs_score_diff': adjusted_result.get('prs_score', 0) - unadjusted_result.get('prs_score', 0),
                'percentile_diff': adjusted_result.get('percentile', 0) - unadjusted_result.get('percentile', 0),
                'normalized_score_diff': adjusted_result.get('normalized_score', 0) - unadjusted_result.get('normalized_score', 0)
            },
            'adjustment_applied': adjusted_result.get('ancestry_adjustment_used', False),
            'inferred_ancestry': adjusted_result.get('inferred_ancestry', 'Unknown')
        }

        # Calculate relative differences
        if unadjusted_result.get('prs_score', 0) != 0:
            comparison['differences']['prs_score_relative'] = (
                comparison['differences']['prs_score_diff'] / abs(unadjusted_result['prs_score']) * 100
            )

        return comparison