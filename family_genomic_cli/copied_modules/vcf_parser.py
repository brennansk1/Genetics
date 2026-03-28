import allel
import pandas as pd
import polars as pl
import numpy as np
from io import BytesIO
import os
import tempfile
from typing import Optional
from .logging_utils import get_logger

logger = get_logger(__name__)

def parse_vcf_file(uploaded_file) -> pd.DataFrame:
    """
    Parses a VCF file using scikit-allel and converts it to the standardized DataFrame format.

    Args:
        uploaded_file: Streamlit UploadedFile object, file path (str), or bytes

    Returns:
        pd.DataFrame: DataFrame with columns ['rsid', 'chromosome', 'position', 'genotype']
                      indexed by 'rsid' if available, or just standard columns.
    """
    # scikit-allel expects a file path or a file-like object.
    # For UploadedFile, we might need to save it to a temp file if allel doesn't support stream well,
    # but allel.read_vcf accepts a file path.

    if isinstance(uploaded_file, str):
        # It's already a file path
        tmp_path = uploaded_file
    else:
        # It's a file-like object
        with tempfile.NamedTemporaryFile(delete=False, suffix=".vcf") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        
    try:
        # Read VCF
        # fields='*' reads all fields. We specifically need variants/ID, variants/CHROM, variants/POS, calldata/GT
        callset = allel.read_vcf(tmp_path, fields=['variants/ID', 'variants/CHROM', 'variants/POS', 'calldata/GT', 'variants/REF', 'variants/ALT'])

        if not callset:
            raise ValueError("Could not parse VCF file or empty file.")

        # Extract data
        rsids = callset['variants/ID']
        chroms = callset['variants/CHROM']
        positions = callset['variants/POS']
        # GT is usually shape (n_variants, n_samples, 2) for diploid
        # We assume single sample VCF for now.
        genotypes_raw = callset['calldata/GT']

        if genotypes_raw.shape[1] > 1:
            logger.warning("VCF contains multiple samples. Using the first sample.")

        # Get first sample genotypes
        gt_sample = genotypes_raw[:, 0, :] # Shape (n_variants, 2)

        # Convert numeric genotypes to alleles
        refs = callset['variants/REF']
        alts = callset['variants/ALT'] # Shape (n_variants, n_alts)

        # Helper to map 0/1 to bases
        # 0 -> REF
        # 1 -> ALT[0]
        # 2 -> ALT[1] etc.
        # -1 -> Missing

        n_variants = len(rsids)
        genotype_strs = []

        for i in range(n_variants):
            g1_idx = gt_sample[i, 0]
            g2_idx = gt_sample[i, 1]

            if g1_idx == -1 or g2_idx == -1:
                genotype_strs.append("--")
                continue

            ref = refs[i]
            # alts[i] is a tuple/array of alt alleles
            alt_alleles = alts[i]

            # Map indices to bases
            # 0 is ref
            # >0 is alt_alleles[idx-1]

            a1 = ref if g1_idx == 0 else alt_alleles[g1_idx - 1]
            a2 = ref if g2_idx == 0 else alt_alleles[g2_idx - 1]

            genotype_strs.append(f"{a1}{a2}")

        # Create DataFrame
        df = pd.DataFrame({
            'rsid': rsids,
            'chromosome': chroms,
            'position': positions,
            'genotype': genotype_strs
        })

        # Filter out entries without RSID (if strictly required, but usually we keep them)
        # The app expects 'rsid' as index or column.
        # Many VCFs have '.' for ID. We might need to annotate them or drop them if the app relies purely on RSID.
        # For now, we keep them but filter out '.' if it causes issues.
        # The app uses `dna_data.index == rsid`. If rsid is '.', it won't match anything useful.

        # Clean up RSIDs
        df['rsid'] = df['rsid'].replace('.', np.nan)
        df = df.dropna(subset=['rsid'])

        return df

    finally:
        # Only remove if we created a temp file
        if not isinstance(uploaded_file, str) and os.path.exists(tmp_path):
            os.remove(tmp_path)
