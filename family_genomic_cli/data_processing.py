import pandas as pd
from typing import Dict, Optional, List, Any
from copied_modules.utils import parse_dna_file
from copied_modules.logging_utils import get_logger

try:
    from pyliftover import LiftOver
    LIFTOVER_AVAILABLE = True
except ImportError:
    LIFTOVER_AVAILABLE = False

logger = get_logger(__name__)

class FamilyData:
    """Container for processed family genomic data."""

    def __init__(self, harmonized_data: pd.DataFrame, qc_results: Dict[str, Any], validation: Dict[str, Any]):
        self.harmonized_data = harmonized_data
        self.qc_results = qc_results
        self.validation = validation

def load_family_data(
    child_file: str,
    mother_file: Optional[str] = None,
    father_file: Optional[str] = None,
    file_formats: Optional[Dict[str, str]] = None
) -> Dict[str, pd.DataFrame]:
    """
    Load DNA data from family member files.

    Args:
        child_file: Path to child's DNA file
        mother_file: Path to mother's DNA file (optional)
        father_file: Path to father's DNA file (optional)
        file_formats: Dict mapping family member to file format (e.g., {'child': 'AncestryDNA'})

    Returns:
        Dict mapping family member to DataFrame with rsid as index
    """
    logger.info("Loading family DNA data")
    if file_formats is None:
        file_formats = {}

    data = {}

    # Load child data (required)
    logger.debug(f"Loading child data from {child_file}")
    data['child'] = parse_dna_file(child_file, file_formats.get('child', 'LivingDNA'))

    # Load parent data (optional)
    if mother_file:
        logger.debug(f"Loading mother data from {mother_file}")
        data['mother'] = parse_dna_file(mother_file, file_formats.get('mother', 'LivingDNA'))
    if father_file:
        logger.debug(f"Loading father data from {father_file}")
        data['father'] = parse_dna_file(father_file, file_formats.get('father', 'LivingDNA'))

    logger.info(f"Loaded data for {len(data)} family members")
    return data

def harmonize_genotypes(family_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Create unified dataset by inner-joining on rsID.

    Args:
        family_data: Dict of DataFrames from load_family_data

    Returns:
        DataFrame with genotypes for each family member
    """
    logger.info("Harmonizing genotypes across family members")
    dfs = list(family_data.values())
    if not dfs:
        logger.warning("No family data provided for harmonization")
        return pd.DataFrame()

    # Start with first DataFrame
    harmonized = dfs[0][['genotype']].rename(columns={'genotype': list(family_data.keys())[0] + '_genotype'})

    # Join remaining DataFrames
    for i, df in enumerate(dfs[1:], 1):
        member = list(family_data.keys())[i]
        harmonized = harmonized.join(
            df[['genotype']].rename(columns={'genotype': member + '_genotype'}),
            how='inner'
        )

    logger.info(f"Harmonized data contains {len(harmonized)} SNPs")
    logger.debug(f"Harmonized data shape: {harmonized.shape}")
    return harmonized

def perform_qc_checks(harmonized_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform Mendelian consistency checks.

    Args:
        harmonized_data: Harmonized DataFrame from harmonize_genotypes

    Returns:
        Dict with QC results
    """
    logger.info("Performing Mendelian consistency checks")
    qc_results = {
        'total_snps': len(harmonized_data),
        'error_count': 0,
        'error_rate': 0.0,
        'errors': [],
        'available_parents': []
    }

    # Determine available parents
    has_mother = any('mother' in col for col in harmonized_data.columns)
    has_father = any('father' in col for col in harmonized_data.columns)

    if has_mother and has_father:
        qc_results['available_parents'] = ['mother', 'father']
    elif has_mother:
        qc_results['available_parents'] = ['mother']
    elif has_father:
        qc_results['available_parents'] = ['father']
    else:
        qc_results['available_parents'] = []

    logger.debug(f"Available parents for QC: {qc_results['available_parents']}")

    # Skip QC if no parents available or only one parent (duo analysis)
    if not qc_results['available_parents']:
        logger.info("No parent data available, skipping Mendelian checks")
        return qc_results
    if len(qc_results['available_parents']) < 2:
        logger.info("Only one parent available, skipping Mendelian checks for duo analysis")
        return qc_results

    # Perform checks for each SNP
    for rsid, row in harmonized_data.iterrows():
        child_geno = row.get('child_genotype')
        mother_geno = row.get('mother_genotype') if has_mother else None
        father_geno = row.get('father_genotype') if has_father else None

        if child_geno is None or child_geno in ['--', 'II', 'DD']:
            continue

        possible_genotypes = get_possible_child_genotypes(mother_geno, father_geno)

        if child_geno not in possible_genotypes:
            qc_results['error_count'] += 1
            qc_results['errors'].append({
                'rsid': rsid,
                'child_genotype': child_geno,
                'mother_genotype': mother_geno,
                'father_genotype': father_geno,
                'possible_genotypes': list(possible_genotypes)
            })

    qc_results['error_rate'] = qc_results['error_count'] / qc_results['total_snps'] if qc_results['total_snps'] > 0 else 0

    logger.info(f"QC completed: {qc_results['error_count']} Mendelian errors found ({qc_results['error_rate']:.2%})")

    # Warning threshold
    if qc_results['error_rate'] > 0.05:
        logger.warning(f"High Mendelian error rate ({qc_results['error_rate']:.2%}). "
                      "This may indicate sample mix-up or poor data quality.")

    # Structured logging of QC results
    logger.info(f"QC results summary: {qc_results}")

    return qc_results

def get_possible_child_genotypes(mother_genotype: Optional[str], father_genotype: Optional[str]) -> set:
    """
    Get possible child genotypes given parent genotypes.

    Args:
        mother_genotype: Mother's genotype string
        father_genotype: Father's genotype string

    Returns:
        Set of possible child genotypes
    """
    if mother_genotype is None and father_genotype is None:
        return set()  # No constraints

    if mother_genotype is None:
        return get_possible_from_one_parent(father_genotype)
    if father_genotype is None:
        return get_possible_from_one_parent(mother_genotype)

    # Both parents available - trio analysis
    mother_alleles = set(mother_genotype) if mother_genotype not in ['--', 'II', 'DD'] else set()
    father_alleles = set(father_genotype) if father_genotype not in ['--', 'II', 'DD'] else set()

    if not mother_alleles or not father_alleles:
        return set()  # Invalid parent data

    possible = set()
    for m_allele in mother_alleles:
        for f_allele in father_alleles:
            # Child gets one allele from each parent
            child_geno = ''.join(sorted([m_allele, f_allele]))
            possible.add(child_geno)

    return possible

def get_possible_from_one_parent(parent_genotype: str) -> set:
    """
    Get possible child genotypes from one known parent (duo analysis).

    Args:
        parent_genotype: Parent's genotype

    Returns:
        Set of possible child genotypes
    """
    if parent_genotype in ['--', 'II', 'DD']:
        return set()

    parent_alleles = set(parent_genotype)
    possible = set()

    # Child must inherit at least one allele from the known parent
    for inherited_allele in parent_alleles:
        # Homozygous child
        possible.add(inherited_allele * 2)
        # Heterozygous child (other allele unknown, so allow any valid combination)
        # For simplicity, assume standard nucleotides
        for other_allele in ['A', 'C', 'G', 'T']:
            if other_allele != inherited_allele:
                possible.add(''.join(sorted([inherited_allele, other_allele])))

    return possible

def apply_liftover(data: Dict[str, pd.DataFrame], liftover_chain_path: str) -> Dict[str, pd.DataFrame]:
    """
    Apply liftover to convert coordinates to target build.

    Args:
        data: Dict of DataFrames
        liftover_chain_path: Path to liftover chain file

    Returns:
        Dict of liftover-adjusted DataFrames
    """
    logger.info("Applying liftover to convert genomic coordinates")
    if not LIFTOVER_AVAILABLE:
        logger.warning("pyliftover not available. Skipping liftover.")
        return data

    try:
        lo = LiftOver(liftover_chain_path)
        logger.debug("Liftover initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing liftover: {e}")
        return data

    lifted_data = {}
    for member, df in data.items():
        logger.debug(f"Processing liftover for {member}")
        if 'chromosome' not in df.columns or 'position' not in df.columns:
            logger.debug(f"Skipping {member}: missing chromosome/position columns")
            lifted_data[member] = df
            continue

        converted_rows = []
        failed_count = 0
        for rsid, row in df.iterrows():
            try:
                chrom = f"chr{row['chromosome']}"
                pos = int(row['position'])
                new_coords = lo.convert_coordinate(chrom, pos)

                if new_coords:
                    converted_rows.append({
                        'rsid': rsid,
                        'chromosome': row['chromosome'],
                        'position': new_coords[0][1],  # Use first mapping
                        'genotype': row['genotype']
                    })
                else:
                    # Keep original if liftover fails
                    failed_count += 1
                    converted_rows.append({
                        'rsid': rsid,
                        'chromosome': row['chromosome'],
                        'position': row['position'],
                        'genotype': row['genotype']
                    })
            except Exception as e:
                # Keep original on error
                failed_count += 1
                logger.debug(f"Liftover failed for {rsid}: {e}")
                converted_rows.append({
                    'rsid': rsid,
                    'chromosome': row['chromosome'],
                    'position': row['position'],
                    'genotype': row['genotype']
                })

        lifted_df = pd.DataFrame(converted_rows).set_index('rsid')
        lifted_data[member] = lifted_df
        logger.debug(f"Liftover for {member}: {failed_count} SNPs failed conversion")

    logger.info("Liftover processing completed")
    return lifted_data

def validate_data(family_data: Dict[str, pd.DataFrame], harmonized_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate file formats and SNP overlap.

    Args:
        family_data: Raw family data
        harmonized_data: Harmonized data

    Returns:
        Dict with validation results
    """
    logger.info("Validating data formats and SNP overlap")
    validation = {
        'valid_formats': True,
        'sufficient_overlap': True,
        'min_overlap_threshold': 10000,
        'actual_overlap': len(harmonized_data),
        'individual_counts': {member: len(df) for member, df in family_data.items()},
        'errors': []
    }

    logger.debug(f"Individual SNP counts: {validation['individual_counts']}")
    logger.debug(f"Harmonized overlap: {validation['actual_overlap']} SNPs")

    # Check overlap
    if len(harmonized_data) < validation['min_overlap_threshold']:
        validation['sufficient_overlap'] = False
        error_msg = f"Insufficient SNP overlap: {len(harmonized_data)} < {validation['min_overlap_threshold']}"
        validation['errors'].append(error_msg)
        logger.warning(error_msg)

    # Basic format validation (already done in parse_dna_file)
    for member, df in family_data.items():
        if df.empty:
            validation['valid_formats'] = False
            error_msg = f"Empty data for {member}"
            validation['errors'].append(error_msg)
            logger.error(error_msg)
        elif 'genotype' not in df.columns:
            validation['valid_formats'] = False
            error_msg = f"Missing genotype column for {member}"
            validation['errors'].append(error_msg)
            logger.error(error_msg)

    logger.info(f"Validation completed: {'valid' if validation['valid_formats'] and validation['sufficient_overlap'] else 'issues found'}")
    return validation

def process_family_data(
    child_file: str,
    mother_file: Optional[str] = None,
    father_file: Optional[str] = None,
    file_formats: Optional[Dict[str, str]] = None,
    liftover_chain_path: Optional[str] = None
) -> FamilyData:
    """
    Main function to process family genomic data.

    Args:
        child_file: Path to child's DNA file
        mother_file: Path to mother's DNA file
        father_file: Path to father's DNA file
        file_formats: Dict of file formats
        liftover_chain_path: Path to liftover chain file

    Returns:
        FamilyData object with processed data and QC results
    """
    logger.info("Starting family data processing pipeline")
    try:
        # Load raw data
        family_data = load_family_data(child_file, mother_file, father_file, file_formats)

        # Apply liftover if requested
        if liftover_chain_path:
            family_data = apply_liftover(family_data, liftover_chain_path)

        # Harmonize genotypes
        harmonized_data = harmonize_genotypes(family_data)

        # Perform QC checks
        qc_results = perform_qc_checks(harmonized_data)

        # Validate
        validation = validate_data(family_data, harmonized_data)

        logger.info("Family data processing completed successfully")
        return FamilyData(harmonized_data, qc_results, validation)

    except Exception as e:
        logger.error(f"Error in family data processing: {e}", exc_info=True)
        raise
