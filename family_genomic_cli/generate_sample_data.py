#!/usr/bin/env python3
"""
Generate sample DNA data files for testing the family-genomic-cli.

Creates realistic genotype data in AncestryDNA CSV format with known variants
for clinical risks, PGx, PRS, etc.
"""

import os
import argparse
from pathlib import Path

def create_sample_data():
    """Create sample genotype data for testing."""

    # Trio configuration (child + both parents) - realistic inheritance
    trio_data = {
        'child': [
            ('rs1801133', 'CT'),  # MTHFR - Heterozygous (inherited from mother)
            ('rs4680', 'AA'),     # COMT - Homozygous (inherited from father)
            ('rs4988235', 'TT'),  # MCM6 - Homozygous (inherited from mother)
            ('rs12785878', 'CC'), # SLC45A2 - Homozygous
            ('rs1800562', 'GG'),  # HFE - Homozygous
            ('rs11591147', 'GG'), # CYP2C19 - Homozygous
            ('rs3892097', 'TT'),  # CYP2D6 - Homozygous
            ('rs9923231', 'CC'),  # VKORC1 - Homozygous
            ('rs1799853', 'GG'),  # CYP2B6 - Homozygous
            ('rs776746', 'AA'),   # CYP3A5 - Homozygous
            ('rs1042713', 'GG'),  # ABCB1 - Homozygous
            ('rs2032582', 'AA'),  # ABCB1 - Homozygous
            ('rs1128503', 'AA'),  # ABCB1 - Homozygous
            ('rs4149056', 'TT'),  # SLCO1B1 - Homozygous
            ('rs2306283', 'AA'),  # SLCO1B1 - Homozygous
            ('rs4149032', 'GG'),  # SLCO1B1 - Homozygous
        ],
        'mother': [
            ('rs1801133', 'CT'),  # MTHFR - Heterozygous
            ('rs4680', 'AG'),     # COMT - Heterozygous
            ('rs4988235', 'TT'),  # MCM6 - Homozygous
            ('rs12785878', 'CT'), # SLC45A2 - Heterozygous
            ('rs1800562', 'GG'),  # HFE - Homozygous
            ('rs11591147', 'AG'), # CYP2C19 - Heterozygous
            ('rs3892097', 'TT'),  # CYP2D6 - Homozygous
            ('rs9923231', 'CT'),  # VKORC1 - Heterozygous
            ('rs1799853', 'GG'),  # CYP2B6 - Homozygous
            ('rs776746', 'GG'),   # CYP3A5 - Homozygous
            ('rs1042713', 'AG'),  # ABCB1 - Heterozygous
            ('rs2032582', 'AG'),  # ABCB1 - Heterozygous
            ('rs1128503', 'AG'),  # ABCB1 - Heterozygous
            ('rs4149056', 'CT'),  # SLCO1B1 - Heterozygous
            ('rs2306283', 'AG'),  # SLCO1B1 - Heterozygous
            ('rs4149032', 'AG'),  # SLCO1B1 - Heterozygous
        ],
        'father': [
            ('rs1801133', 'TT'),  # MTHFR - Homozygous
            ('rs4680', 'GG'),     # COMT - Homozygous
            ('rs4988235', 'CC'),  # MCM6 - Homozygous
            ('rs12785878', 'TT'), # SLC45A2 - Homozygous
            ('rs1800562', 'AG'),  # HFE - Heterozygous
            ('rs11591147', 'GG'), # CYP2C19 - Homozygous
            ('rs3892097', 'CC'),  # CYP2D6 - Homozygous
            ('rs9923231', 'CC'),  # VKORC1 - Homozygous
            ('rs1799853', 'GT'),  # CYP2B6 - Heterozygous
            ('rs776746', 'AA'),   # CYP3A5 - Homozygous
            ('rs1042713', 'GG'),  # ABCB1 - Homozygous
            ('rs2032582', 'AA'),  # ABCB1 - Homozygous
            ('rs1128503', 'AA'),  # ABCB1 - Homozygous
            ('rs4149056', 'TT'),  # SLCO1B1 - Homozygous
            ('rs2306283', 'AA'),  # SLCO1B1 - Homozygous
            ('rs4149032', 'GG'),  # SLCO1B1 - Homozygous
        ]
    }

    # Create output directory
    output_dir = Path("sample_data")
    output_dir.mkdir(exist_ok=True)

    # Generate trio files
    for member, genotypes in trio_data.items():
        file_path = output_dir / f'{member}_trio.csv'
        with open(file_path, 'w') as f:
            f.write('rsid,genotype\n')
            for rsid, genotype in genotypes:
                f.write(f'{rsid},{genotype}\n')
        print(f"Created {file_path}")

    # Generate duo files (child + mother)
    duo_data = {
        'child': trio_data['child'],
        'mother': trio_data['mother']
    }

    for member, genotypes in duo_data.items():
        file_path = output_dir / f'{member}_duo.csv'
        with open(file_path, 'w') as f:
            f.write('rsid,genotype\n')
            for rsid, genotype in genotypes:
                f.write(f'{rsid},{genotype}\n')
        print(f"Created {file_path}")

    # Generate singleton file (child only)
    file_path = output_dir / 'child_singleton.csv'
    with open(file_path, 'w') as f:
        f.write('rsid,genotype\n')
        for rsid, genotype in trio_data['child']:
            f.write(f'{rsid},{genotype}\n')
    print(f"Created {file_path}")

    # Create invalid data file for error testing
    file_path = output_dir / 'invalid_data.csv'
    with open(file_path, 'w') as f:
        f.write('invalid,data\n')
        f.write('no,genotype,column\n')
    print(f"Created {file_path} (for error testing)")

    # Create mismatched data for Mendelian error testing
    mismatched_data = {
        'child': [('rs1801133', 'CC')],  # Impossible genotype
        'mother': [('rs1801133', 'TT')],
        'father': [('rs1801133', 'TT')]
    }

    for member, genotypes in mismatched_data.items():
        file_path = output_dir / f'{member}_mismatched.csv'
        with open(file_path, 'w') as f:
            f.write('rsid,genotype\n')
            for rsid, genotype in genotypes:
                f.write(f'{rsid},{genotype}\n')
        print(f"Created {file_path} (for Mendelian error testing)")

    print(f"\nSample data generated in {output_dir}/")
    print("Files created:")
    print("- child_trio.csv, mother_trio.csv, father_trio.csv (trio analysis)")
    print("- child_duo.csv, mother_duo.csv (duo analysis)")
    print("- child_singleton.csv (singleton analysis)")
    print("- invalid_data.csv (error testing)")
    print("- child_mismatched.csv, mother_mismatched.csv, father_mismatched.csv (Mendelian error testing)")

if __name__ == "__main__":
    create_sample_data()