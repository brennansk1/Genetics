import argparse
import csv
import os
import sys

from .logging_utils import get_logger

logger = get_logger(__name__)


def convert_vcf_gz_to_tsv(input_vcf_path, output_tsv_path):
    """
    Converts a VCF.GZ file to a TSV file, extracting rsid, chromosome, position, and CLNSIG.
    Utilizes cyvcf2 for fast parsing.
    """
    logger.info(f"Starting VCF conversion using cyvcf2: {input_vcf_path} -> {output_tsv_path}")

    try:
        from cyvcf2 import VCF
        vcf = VCF(input_vcf_path)
    except ImportError:
        logger.error("cyvcf2 not installed. Please install cyvcf2 to run this conversion.")
        raise
    except Exception as e:
        logger.error(f"Failed to open VCF file {input_vcf_path}: {e}")
        raise

    try:
        with open(output_tsv_path, "w", newline="") as outfile:
            writer = csv.writer(outfile, delimiter="\t")
            writer.writerow(["rsid", "chromosome", "position", "CLNSIG"])

            processed_lines = 0
            pathogenic_variants = 0

            for variant in vcf:
                processed_lines += 1
                
                clnsig = variant.INFO.get("CLNSIG")
                if not clnsig:
                    continue
                
                # CLNSIG can be a tuple or a single string depending on the VCF info schema
                clnsig_str = str(clnsig)
                
                if "Pathogenic" in clnsig_str or "Likely_pathogenic" in clnsig_str:
                    rsid = variant.ID if variant.ID else f"chr{variant.CHROM}_{variant.POS}"
                    writer.writerow([rsid, variant.CHROM, variant.POS, clnsig_str])
                    pathogenic_variants += 1

            logger.info(f"VCF conversion completed. Processed {processed_lines} variants, found {pathogenic_variants} pathogenic variants.")
            
    except Exception as e:
        logger.error(f"Error during VCF conversion writing: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert ClinVar VCF to simplified TSV.")
    parser.add_argument("--input", required=True, help="Path to input VCF.GZ file")
    parser.add_argument("--output", required=True, help="Path to output TSV file")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        logger.error(f"Input file not found at {args.input}")
        sys.exit(1)
        
    try:
        convert_vcf_gz_to_tsv(args.input, args.output)
        logger.info("VCF Converter completed successfully")
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        sys.exit(1)
