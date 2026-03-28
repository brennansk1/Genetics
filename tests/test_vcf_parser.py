import pandas as pd
import pytest
from io import BytesIO
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vcf_parser import parse_vcf_file

class MockUploadedFile:
    def __init__(self, content):
        self.content = content
    def getvalue(self):
        return self.content

def test_parse_vcf_simple():
    # Minimal VCF with header and 2 variants
    vcf_content = b"""##fileformat=VCFv4.2
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE1
1\t100\trs123\tA\tG\t.\t.\t.\tGT\t0/1
1\t200\trs456\tT\tC\t.\t.\t.\tGT\t1/1
"""
    uploaded_file = MockUploadedFile(vcf_content)
    df = parse_vcf_file(uploaded_file)
    
    assert len(df) == 2
    # Check first variant (Heterozygous A/G)
    row1 = df[df['rsid'] == 'rs123'].iloc[0]
    assert row1['chromosome'] == '1'
    assert row1['position'] == 100
    # 0/1 means Ref/Alt. Ref=A, Alt=G. So AG.
    # Note: The parser might sort them or keep order. My implementation keeps order: Ref if 0, Alt if >0.
    # So 0/1 -> A G.
    assert row1['genotype'] == 'AG' 

    # Check second variant (Homozygous Alt C/C)
    row2 = df[df['rsid'] == 'rs456'].iloc[0]
    assert row2['genotype'] == 'CC'

def test_parse_vcf_multiallelic():
    # VCF with multi-allelic site (though my parser might simplify it, let's see)
    # 1 300 . A G,T ... GT 1/2
    # Ref=A, Alt1=G, Alt2=T. 1/2 -> G/T.
    vcf_content = b"""##fileformat=VCFv4.2
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE1
1\t300\trs789\tA\tG,T\t.\t.\t.\tGT\t1/2
"""
    uploaded_file = MockUploadedFile(vcf_content)
    df = parse_vcf_file(uploaded_file)
    
    assert len(df) == 1
    row = df.iloc[0]
    assert row['genotype'] == 'GT'

if __name__ == "__main__":
    test_parse_vcf_simple()
    test_parse_vcf_multiallelic()
    print("All VCF tests passed!")
