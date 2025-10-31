import csv
import gzip
import os
import re


def convert_vcf_gz_to_tsv(input_vcf_gz_path, output_tsv_path):
    """
    Converts a VCF.GZ file to a TSV file, extracting rsid, chromosome, position, and CLNSIG.
    Skips header lines and entries without CLNSIG information.
    """
    print(f"Converting {input_vcf_gz_path} to {output_tsv_path}...")

    with gzip.open(input_vcf_gz_path, "rt") as infile, open(
        output_tsv_path, "w", newline=""
    ) as outfile:

        writer = csv.writer(outfile, delimiter="\t")
        writer.writerow(
            ["rsid", "chromosome", "position", "CLNSIG"]
        )  # Write header for TSV

        for line in infile:
            if line.startswith("#"):
                continue  # Skip VCF header lines

            parts = line.strip().split("\t")
            if len(parts) < 8:  # VCF lines should have at least 8 fields before INFO
                continue

            rsid = parts[2]
            chrom = parts[0]
            pos = parts[1]
            info = parts[7]

            clnsig_match = re.search(r"CLNSIG=([^;]+)", info)

            if clnsig_match:
                clnsig = clnsig_match.group(1)
                # Filter for pathogenic or likely pathogenic variants
                if "Pathogenic" in clnsig or "Likely_pathogenic" in clnsig:
                    writer.writerow([rsid, chrom, pos, clnsig])

    print(f"Conversion complete. Output saved to {output_tsv_path}")


if __name__ == "__main__":
    # IMPORTANT: Update these paths as needed
    input_file = "clinvar.vcf.gz"
    output_file = "clinvar_pathogenic_variants.tsv"

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file not found at {input_file}")
    else:
        convert_vcf_gz_to_tsv(input_file, output_file)
