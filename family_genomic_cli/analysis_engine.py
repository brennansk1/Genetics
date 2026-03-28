"""
Analysis Engine for Individual Genomic Analyses

This module orchestrates various genomic analyses for individual family members,
including clinical risk screening, pharmacogenomics, polygenic risk scores,
wellness traits, and carrier status screening.
"""

from typing import Dict, List, Optional, Union
import pandas as pd
import os

from copied_modules import snp_data, pgx_star_alleles, genomewide_prs, bioinformatics_utils
from copied_modules.logging_utils import get_logger

logger = get_logger(__name__)

# Global caches for CPIC data
_cpic_alleles = None
_cpic_pairs = None

def _load_cpic_data():
    """Load CPIC data with caching."""
    global _cpic_alleles, _cpic_pairs

    if _cpic_alleles is None:
        alleles_path = os.path.join(os.path.dirname(__file__), 'data', 'cpic_alleles.xlsx')
        try:
            _cpic_alleles = pd.read_excel(alleles_path, sheet_name='Alleles')
            logger.info("Loaded CPIC alleles data")
        except FileNotFoundError:
            logger.warning("CPIC alleles file not found at %s", alleles_path)
            _cpic_alleles = pd.DataFrame()
        except Exception as e:
            logger.error("Error loading CPIC alleles: %s", e)
            _cpic_alleles = pd.DataFrame()

    if _cpic_pairs is None:
        pairs_path = os.path.join(os.path.dirname(__file__), 'data', 'cpic_gene-drug_pairs.xlsx')
        try:
            _cpic_pairs = pd.read_excel(pairs_path, sheet_name='CPIC Gene-Drug Pairs')
            logger.info("Loaded CPIC gene-drug pairs data")
        except FileNotFoundError:
            logger.warning("CPIC pairs file not found at %s", pairs_path)
            _cpic_pairs = pd.DataFrame()
        except Exception as e:
            logger.error("Error loading CPIC pairs: %s", e)
            _cpic_pairs = pd.DataFrame()


def clinical_risk_screening(genotype_data: Union[Dict[str, str], pd.DataFrame]) -> Dict:
    """
    Screen for high-impact variants in clinical risk genes.

    Args:
        genotype_data: Dictionary or DataFrame with rsID keys/index and genotype values

    Returns:
        Dict with clinical risk findings
    """
    logger.info("Starting clinical risk screening")
    if isinstance(genotype_data, dict):
        genotype_data = pd.DataFrame.from_dict(genotype_data, orient='index', columns=['genotype'])

    results = {
        "hereditary_cancer": {},
        "cardiovascular": {},
        "neurodegenerative": {},
        "mitochondrial": {},
        "acmg_secondary_findings": {}
    }

    # Get SNP data for each category
    cancer_snps = snp_data.get_cancer_snps()
    cardio_snps = snp_data.get_cardiovascular_snps()
    neuro_snps = snp_data.get_neuro_snps()
    mito_snps = snp_data.get_mito_snps()
    acmg_snps = snp_data.get_acmg_sf_variants()

    # Screen each category
    results["hereditary_cancer"] = _screen_category(cancer_snps, genotype_data)
    results["cardiovascular"] = _screen_category(cardio_snps, genotype_data)
    results["neurodegenerative"] = _screen_category(neuro_snps, genotype_data)
    results["mitochondrial"] = _screen_category(mito_snps, genotype_data)
    results["acmg_secondary_findings"] = _screen_category(acmg_snps, genotype_data)

    logger.info("Clinical risk screening completed")
    logger.info(f"Clinical risk screening results: {results}")
    return results


def _screen_category(snp_dict: Dict, genotype_data: pd.DataFrame) -> Dict:
    """Helper to screen SNPs in a category and classify variants."""
    findings = {}

    for rsid, snp_info in snp_dict.items():
        if rsid in genotype_data.index:
            genotype = genotype_data.loc[rsid, 'genotype']
            if genotype and genotype != '--':
                # Check interpretations
                interp = snp_info.get('interp', {})
                if genotype in interp:
                    interpretation = interp[genotype]
                    if interpretation:
                        # Classify variant
                        variant_class = _classify_variant(interpretation)
                        if variant_class in ['Pathogenic', 'Likely Pathogenic', 'VUS']:
                            findings[rsid] = {
                                "gene": snp_info.get('gene', ''),
                                "genotype": genotype,
                                "interpretation": interpretation,
                                "classification": variant_class,
                                "condition": snp_info.get('condition', ''),
                                "risk_level": snp_info.get('risk', '')
                            }

    return findings


def _classify_variant(interpretation: str) -> str:
    """Classify variant based on interpretation text."""
    interp_lower = interpretation.lower()
    if 'pathogenic' in interp_lower and 'likely' in interp_lower:
        return 'Likely Pathogenic'
    elif 'pathogenic' in interp_lower:
        return 'Pathogenic'
    elif 'vus' in interp_lower or 'uncertain' in interp_lower:
        return 'VUS'
    else:
        return 'Benign'


def pgx_analysis(genotype_data: Union[Dict[str, str], pd.DataFrame]) -> Dict:
    """
    Perform pharmacogenomic analysis for CYP enzymes.

    Args:
        genotype_data: Dictionary or DataFrame with rsID keys/index and genotype values

    Returns:
        Dict with PGx results and drug warnings
    """
    logger.info("Starting pharmacogenomic analysis")
    if isinstance(genotype_data, dict):
        genotype_data = pd.DataFrame.from_dict(genotype_data, orient='index', columns=['genotype'])

    # Load CPIC data
    _load_cpic_data()

    results = {}

    # Key CYP genes for PGx
    pgx_genes = ['CYP2C19', 'CYP2D6', 'CYP2C9', 'CYP3A5', 'CYP2B6']

    for gene in pgx_genes:
        try:
            logger.debug(f"Analyzing PGx for gene: {gene}")
            allele_result = pgx_star_alleles.star_caller.call_star_alleles(gene, genotype_data)
            if 'error' not in allele_result:
                results[gene] = allele_result

                # Get CPIC recommendations
                metabolizer_status = allele_result.get('metabolizer_status', '')
                recommendations = pgx_star_alleles.star_caller.get_cpic_recommendations(
                    gene, metabolizer_status
                )
                if 'error' not in recommendations:
                    results[gene]['drug_recommendations'] = recommendations

                # Add phenotype_prediction field
                results[gene]['phenotype_prediction'] = metabolizer_status

                # Add pharmacogenomics field with drug interactions
                if not _cpic_pairs.empty:
                    gene_pairs = _cpic_pairs[_cpic_pairs['Gene'] == gene]
                    if not gene_pairs.empty:
                        drug_interactions = {}
                        for _, row in gene_pairs.iterrows():
                            drug = row['Drug']
                            guideline = row['Guideline']
                            level = row['CPIC Level']
                            status = row['CPIC Level Status']
                            drug_interactions[drug] = {
                                'guideline': guideline,
                                'level': level,
                                'status': status
                            }
                        results[gene]['pharmacogenomics'] = drug_interactions
                    else:
                        results[gene]['pharmacogenomics'] = {}
                else:
                    results[gene]['pharmacogenomics'] = {}
            else:
                logger.warning(f"Error in PGx analysis for {gene}: {allele_result['error']}")
        except Exception as e:
            logger.error(f"Exception in PGx analysis for {gene}: {e}", exc_info=True)
            results[gene] = {"error": f"Failed to analyze {gene}: {str(e)}"}

    logger.info("Pharmacogenomic analysis completed")
    logger.info(f"PGx analysis results: {results}")
    return results


def prs_analysis(genotype_data: Union[Dict[str, str], pd.DataFrame]) -> Dict:
    """
    Calculate polygenic risk scores for common diseases.

    Args:
        genotype_data: Dictionary or DataFrame with rsID keys/index and genotype values

    Returns:
        Dict with PRS results
    """
    logger.info("Starting polygenic risk score analysis")
    if isinstance(genotype_data, dict):
        genotype_data = pd.DataFrame.from_dict(genotype_data, orient='index', columns=['genotype'])

    results = {}

    # Key diseases for PRS
    diseases = ['Type 2 Diabetes', 'Coronary Artery Disease', 'Breast Cancer', 'Prostate Cancer']

    prs_calculator = genomewide_prs.GenomeWidePRS()

    for disease in diseases:
        try:
            logger.debug(f"Calculating PRS for {disease}")
            # Get PRS models for this disease
            models = snp_data.get_prs_models_by_category(disease.lower().replace(' ', '_'))
            if models:
                # Use the first available model
                model_id = list(models.keys())[0]
                prs_result = prs_calculator.calculate_genomewide_prs(genotype_data, model_id)
                if prs_result.get('success', False):
                    results[disease] = {
                        "score": prs_result.get('prs_score', 0),
                        "percentile": prs_result.get('percentile', 50),
                        "normalized_score": prs_result.get('normalized_score', 0),
                        "snps_used": prs_result.get('snps_used', 0),
                        "total_snps": prs_result.get('total_snps', 0),
                        "coverage": prs_result.get('coverage', 0)
                    }
                else:
                    logger.warning(f"PRS calculation failed for {disease}: {prs_result}")
            else:
                logger.debug(f"No PRS models available for {disease}")
        except Exception as e:
            logger.error(f"Exception in PRS analysis for {disease}: {e}", exc_info=True)
            results[disease] = {"error": f"Failed to calculate PRS for {disease}: {str(e)}"}

    logger.info("Polygenic risk score analysis completed")
    logger.info(f"PRS analysis results: {results}")
    return results


def wellness_traits_analysis(genotype_data: Union[Dict[str, str], pd.DataFrame]) -> Dict:
    """
    Analyze wellness and lifestyle traits.

    Args:
        genotype_data: Dictionary or DataFrame with rsID keys/index and genotype values

    Returns:
        Dict with wellness trait results
    """
    logger.info("Starting wellness traits analysis")
    if isinstance(genotype_data, dict):
        genotype_data = pd.DataFrame.from_dict(genotype_data, orient='index', columns=['genotype'])

    results = {}

    # Key wellness SNPs
    wellness_snps = {
        "rs4988235": {"gene": "MCM6", "trait": "Lactose Tolerance"},
        "rs4680": {"gene": "COMT", "trait": "Caffeine Metabolism"},
        "rs10741657": {"gene": "CYP1A2", "trait": "Caffeine Metabolism"},
        "rs1801133": {"gene": "MTHFR", "trait": "Folate Metabolism"},
        "rs12785878": {"gene": "SLC45A2", "trait": "Vitamin D Absorption"}
    }

    for rsid, info in wellness_snps.items():
        if rsid in genotype_data.index:
            genotype = genotype_data.loc[rsid, 'genotype']
            if genotype and genotype != '--':
                try:
                    logger.debug(f"Analyzing wellness trait for {rsid} ({info['trait']})")
                    impact = bioinformatics_utils.predict_functional_impact(
                        rsid, genotype, info['gene']
                    )
                    results[info['trait']] = {
                        "rsid": rsid,
                        "gene": info['gene'],
                        "genotype": genotype,
                        "predicted_impact": impact.get('predicted_impact', 'unknown'),
                        "details": impact
                    }
                except Exception as e:
                    logger.error(f"Exception in wellness analysis for {rsid}: {e}", exc_info=True)
                    results[info['trait']] = {"error": f"Failed to analyze {rsid}: {str(e)}"}

    logger.info("Wellness traits analysis completed")
    logger.info(f"Wellness traits analysis results: {results}")
    return results


def carrier_status_screening(genotype_data: Union[Dict[str, str], pd.DataFrame]) -> Dict:
    """
    Screen for carrier status of recessive conditions.

    Args:
        genotype_data: Dictionary or DataFrame with rsID keys/index and genotype values

    Returns:
        Dict with carrier status results
    """
    logger.info("Starting carrier status screening")
    if isinstance(genotype_data, dict):
        genotype_data = pd.DataFrame.from_dict(genotype_data, orient='index', columns=['genotype'])

    results = {}

    # Get recessive carrier SNPs
    recessive_snps = snp_data.get_recessive_snps()

    for rsid, snp_info in recessive_snps.items():
        if rsid in genotype_data.index:
            genotype = genotype_data.loc[rsid, 'genotype']
            if genotype and genotype != '--':
                # Check if heterozygous (carrier)
                if len(set(genotype)) > 1:
                    interp = snp_info.get('interp', {})
                    if genotype in interp:
                        interpretation = interp[genotype]
                        if interpretation and 'carrier' in interpretation.lower():
                            results[rsid] = {
                                "condition": snp_info.get('condition', ''),
                                "gene": snp_info.get('gene', ''),
                                "genotype": genotype,
                                "interpretation": interpretation,
                                "carrier_status": "Carrier"
                            }

    logger.info("Carrier status screening completed")
    logger.info(f"Carrier status screening results: {results}")
    return results


def run_individual_analyses(genotype_data: Union[Dict[str, str], pd.DataFrame]) -> Dict:
    """
    Run all individual genomic analyses and aggregate results.

    Args:
        genotype_data: Dictionary or DataFrame with rsID keys/index and genotype values

    Returns:
        Dict with all analysis results
    """
    logger.info("Starting individual genomic analyses")
    results = {}

    try:
        results["clinical_risk_screening"] = clinical_risk_screening(genotype_data)
    except Exception as e:
        logger.error(f"Clinical risk screening failed: {e}", exc_info=True)
        results["clinical_risk_screening"] = {"error": f"Clinical risk screening failed: {str(e)}"}

    try:
        results["pharmacogenomics"] = pgx_analysis(genotype_data)
    except Exception as e:
        logger.error(f"PGx analysis failed: {e}", exc_info=True)
        results["pharmacogenomics"] = {"error": f"PGx analysis failed: {str(e)}"}

    try:
        results["polygenic_risk_scores"] = prs_analysis(genotype_data)
    except Exception as e:
        logger.error(f"PRS analysis failed: {e}", exc_info=True)
        results["polygenic_risk_scores"] = {"error": f"PRS analysis failed: {str(e)}"}

    try:
        results["wellness_traits"] = wellness_traits_analysis(genotype_data)
    except Exception as e:
        logger.error(f"Wellness traits analysis failed: {e}", exc_info=True)
        results["wellness_traits"] = {"error": f"Wellness traits analysis failed: {str(e)}"}

    try:
        results["carrier_status"] = carrier_status_screening(genotype_data)
    except Exception as e:
        logger.error(f"Carrier status screening failed: {e}", exc_info=True)
        results["carrier_status"] = {"error": f"Carrier status screening failed: {str(e)}"}

    logger.info("Individual genomic analyses completed")
    logger.info(f"Individual analyses results summary: {results}")
    return results
