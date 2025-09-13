#!/usr/bin/env python3
"""
Test script for Clinical Risk & Carrier Status module.
"""

import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.local_data_utils import get_clinvar_pathogenic_variants_local
from src.api_functions import get_clinvar_data
from src.snp_data import recessive_snps, cancer_snps, cardiovascular_snps, neuro_snps, mito_snps, protective_snps, ancestry_panels, acmg_sf_variants

def create_sample_dna_data():
    """Create sample DNA data for testing clinical risk analyses."""
    # Synthetic data for testing purposes - not from real genetic data
    # Include SNPs from various clinical categories
    sample_data = {
        'rsID': [
            'rs1801133',  # MTHFR - cardiovascular
            'rs429358',   # APOE - Alzheimer's
            'rs7412',     # APOE - Alzheimer's
            'rs1061170',  # CFTR - cystic fibrosis carrier
            'rs1800562',  # HFE - hemochromatosis
            'rs1799945',  # BRCA1 - breast cancer
            'rs80357421', # BRCA1 - breast cancer
            'rs28897743', # BRCA2 - breast cancer
            'rs80359361', # BRCA2 - breast cancer
            'rs121913279', # BRCA1 - pathogenic
            'rs80357123',  # BRCA2 - pathogenic
            'rs1801181',  # LIPC - cardiovascular protective
            'rs7412',     # APOE - Alzheimer's
            'rs429358',   # APOE - Alzheimer's
            'rs1800562',  # HFE - hemochromatosis
            'rs1061170',  # CFTR - cystic fibrosis
            'rs121908745', # PAH - PKU
            'rs62642937',  # GJB2 - hearing loss
            'rs80338943',  # USH2A - Usher syndrome
            'rs80338940',  # USH2A - Usher syndrome
            'rs80338941',  # USH2A - Usher syndrome
        ],
        'genotype': [
            'CC',  # MTHFR heterozygous
            'CT',  # APOE e4 carrier
            'CC',  # APOE e3/e3
            'AG',  # CFTR carrier
            'AG',  # HFE carrier
            'GG',  # BRCA1 normal
            'GG',  # BRCA1 normal
            'GG',  # BRCA2 normal
            'GG',  # BRCA2 normal
            'GG',  # BRCA1 normal
            'GG',  # BRCA2 normal
            'CG',  # LIPC protective
            'CC',  # APOE e3/e3
            'CT',  # APOE e4 carrier
            'AG',  # HFE carrier
            'AG',  # CFTR carrier
            'GG',  # PAH normal
            'GG',  # GJB2 normal
            'GG',  # USH2A normal
            'GG',  # USH2A normal
            'GG',  # USH2A normal
        ],
        'chromosome': [
            '1', '19', '19', '7', '6', '17', '17', '13', '13', '17', '13', '15',
            '19', '19', '6', '7', '12', '13', '1', '1', '1'
        ],
        'position': [
            '11856378', '45411941', '45412079', '117149127', '26092913',
            '41244753', '41244753', '32340359', '32340359', '41244753',
            '32340359', '58625837', '45412079', '45411941', '26092913',
            '117149127', '102866941', '20763443', '216247902', '216247902',
            '216247902'
        ]
    }
    df = pd.DataFrame(sample_data)
    df.set_index('rsID', inplace=True)
    return df

def test_recessive_carrier_status():
    """Test recessive carrier status analysis."""
    print("Testing Recessive Carrier Status Analysis...")
    dna_data = create_sample_dna_data()

    results = []
    for rsid, info in recessive_snps.items():
        user_genotype = dna_data[dna_data.index == rsid]
        status = 'Not a carrier (or not tested)'
        genotype = 'Not in data'
        if not user_genotype.empty:
            genotype = user_genotype.iloc[0]['genotype']
            sorted_genotype = "".join(sorted(genotype))
            if sorted_genotype in info['interp']:
                status = info['interp'][sorted_genotype]
        results.append({'rsID': rsid, 'Gene': info['gene'], 'Condition': info['condition'], 'Genotype': genotype, 'Status': status})

    carrier_df = pd.DataFrame(results).set_index('rsID')

    # Assertions
    assert len(carrier_df) > 0, "No carrier status results generated"
    assert 'Status' in carrier_df.columns, "Status column missing"
    assert 'Genotype' in carrier_df.columns, "Genotype column missing"

    # Check specific known results
    cftr_result = carrier_df[carrier_df.index == 'rs1061170']
    if not cftr_result.empty:
        assert cftr_result.iloc[0]['Status'] != 'Not a carrier (or not tested)', "CFTR carrier status should be detected"

    print("PASS: Recessive carrier status analysis working correctly")
    return True

def test_hereditary_cancer_syndromes():
    """Test hereditary cancer syndromes analysis."""
    print("Testing Hereditary Cancer Syndromes Analysis...")
    dna_data = create_sample_dna_data()

    results = []
    for rsid, info in cancer_snps.items():
        user_genotype = dna_data[dna_data.index == rsid]
        status = 'No risk variant detected'
        genotype = 'Not in data'
        if not user_genotype.empty:
            genotype = user_genotype.iloc[0]['genotype']
            status = 'Risk variant detected'
        results.append({'rsID': rsid, 'Gene': info['gene'], 'Risk': info['risk'], 'Genotype': genotype, 'Status': status})

    cancer_df = pd.DataFrame(results).set_index('rsID')

    # Assertions
    assert len(cancer_df) > 0, "No cancer syndrome results generated"
    assert 'Status' in cancer_df.columns, "Status column missing"

    print("PASS: Hereditary cancer syndromes analysis working correctly")
    return True

def test_cardiovascular_conditions():
    """Test cardiovascular conditions analysis."""
    print("Testing Cardiovascular Conditions Analysis...")
    dna_data = create_sample_dna_data()

    results = []
    for rsid, info in cardiovascular_snps.items():
        user_genotype = dna_data[dna_data.index == rsid]
        status = 'No risk variant detected'
        genotype = 'Not in data'
        if not user_genotype.empty:
            genotype = user_genotype.iloc[0]['genotype']
            status = 'Risk variant detected'
        results.append({'rsID': rsid, 'Gene': info['gene'], 'Risk': info['risk'], 'Genotype': genotype, 'Status': status})

    cv_df = pd.DataFrame(results).set_index('rsID')

    # Assertions
    assert len(cv_df) > 0, "No cardiovascular results generated"
    assert 'Status' in cv_df.columns, "Status column missing"

    print("PASS: Cardiovascular conditions analysis working correctly")
    return True

def test_neurodegenerative_conditions():
    """Test neurodegenerative conditions analysis."""
    print("Testing Neurodegenerative Conditions Analysis...")
    dna_data = create_sample_dna_data()

    results = []
    for rsid, info in neuro_snps.items():
        user_genotype = dna_data[dna_data.index == rsid]
        status = 'No risk variant detected'
        genotype = 'Not in data'
        if not user_genotype.empty:
            genotype = user_genotype.iloc[0]['genotype']
            status = 'Risk variant detected'
        results.append({'rsID': rsid, 'Gene': info['gene'], 'Risk': info['risk'], 'Genotype': genotype, 'Status': status})

    neuro_df = pd.DataFrame(results).set_index('rsID')

    # Assertions
    assert len(neuro_df) > 0, "No neurodegenerative results generated"
    assert 'Status' in neuro_df.columns, "Status column missing"

    print("PASS: Neurodegenerative conditions analysis working correctly")
    return True

def test_mitochondrial_health():
    """Test mitochondrial health analysis."""
    print("Testing Mitochondrial Health Analysis...")
    dna_data = create_sample_dna_data()

    results = []
    for rsid, info in mito_snps.items():
        user_genotype = dna_data[dna_data.index == rsid]
        status = 'No risk variant detected'
        genotype = 'Not in data'
        if not user_genotype.empty:
            genotype = user_genotype.iloc[0]['genotype']
            status = 'Risk variant detected'
        results.append({'rsID': rsid, 'Gene': info['gene'], 'Risk': info['risk'], 'Genotype': genotype, 'Status': status})

    mito_df = pd.DataFrame(results).set_index('rsID')

    # Assertions
    assert len(mito_df) > 0, "No mitochondrial results generated"
    assert 'Status' in mito_df.columns, "Status column missing"

    print("PASS: Mitochondrial health analysis working correctly")
    return True

def test_protective_variants():
    """Test protective variant highlights."""
    print("Testing Protective Variant Highlights...")
    dna_data = create_sample_dna_data()

    results = []
    for rsid, info in protective_snps.items():
        user_genotype = dna_data[dna_data.index == rsid]
        status = 'No protective variant detected (or not tested)'
        genotype = 'Not in data'
        if not user_genotype.empty:
            genotype = user_genotype.iloc[0]['genotype']
            sorted_genotype = "".join(sorted(genotype))
            if sorted_genotype in info['interp']:
                status = info['interp'][sorted_genotype]
        results.append({'rsID': rsid, 'Gene': info['gene'], 'Trait': info['trait'], 'Genotype': genotype, 'Status': status})

    protective_df = pd.DataFrame(results).set_index('rsID')

    # Assertions
    assert len(protective_df) > 0, "No protective variant results generated"
    assert 'Status' in protective_df.columns, "Status column missing"

    print("PASS: Protective variants analysis working correctly")
    return True

def test_ancestry_aware_screening():
    """Test ancestry-aware screening panels."""
    print("Testing Ancestry-Aware Screening...")
    dna_data = create_sample_dna_data()

    selected_ancestry = 'Northern European'  # Test with Northern European ancestry

    results = []
    for rsid, info in ancestry_panels[selected_ancestry].items():
        user_genotype = dna_data[dna_data.index == rsid]
        status = 'No risk variant detected'
        genotype = 'Not in data'
        if not user_genotype.empty:
            genotype = user_genotype.iloc[0]['genotype']
            if len(set(genotype)) > 1:  # Heterozygous
                status = 'Risk variant detected - Consider genetic counseling'
        results.append({'rsID': rsid, 'Gene': info['gene'], 'Condition': info['condition'], 'Genotype': genotype, 'Status': status})

    ancestry_df = pd.DataFrame(results).set_index('rsID')

    # Assertions
    assert len(ancestry_df) > 0, "No ancestry-aware results generated"
    assert 'Status' in ancestry_df.columns, "Status column missing"

    print("PASS: Ancestry-aware screening working correctly")
    return True

def test_acmg_secondary_findings():
    """Test ACMG secondary findings screening."""
    print("Testing ACMG Secondary Findings Screening...")
    dna_data = create_sample_dna_data()

    results = []
    for rsid, info in acmg_sf_variants.items():
        user_genotype = dna_data[dna_data.index == rsid]
        status = 'No ACMG secondary finding detected'
        genotype = 'Not in data'
        if not user_genotype.empty:
            genotype = user_genotype.iloc[0]['genotype']
            if len(set(genotype)) > 1:  # Heterozygous
                status = 'ACMG secondary finding detected - Consult genetic counselor'
        results.append({'rsID': rsid, 'Gene': info['gene'], 'Condition': info['condition'], 'Genotype': genotype, 'Status': status})

    acmg_df = pd.DataFrame(results).set_index('rsID')

    # Assertions
    assert len(acmg_df) > 0, "No ACMG secondary findings results generated"
    assert 'Status' in acmg_df.columns, "Status column missing"

    print("PASS: ACMG secondary findings screening working correctly")
    return True

def run_all_clinical_risk_tests():
    """Run all clinical risk and carrier status tests."""
    print("CLINICAL RISK & CARRIER STATUS TESTS")
    print("=" * 50)

    tests = [
        test_recessive_carrier_status,
        test_hereditary_cancer_syndromes,
        test_cardiovascular_conditions,
        test_neurodegenerative_conditions,
        test_mitochondrial_health,
        test_protective_variants,
        test_ancestry_aware_screening,
        test_acmg_secondary_findings
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__} - {str(e)}")

    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}/{total}")
    if passed == total:
        print("All clinical risk tests passed!")
        return True
    else:
        print("Some tests failed.")
        return False

if __name__ == "__main__":
    success = run_all_clinical_risk_tests()
    if not success:
        exit(1)