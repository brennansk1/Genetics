import pytest
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.drug_interactions import InteractionChecker

def create_mock_dna_data():
    """Create mock DNA data for testing."""
    data = {
        "rsid": ["rs4244285", "rs1057910", "rs3892097"],
        "genotype": ["AA", "TT", "GG"], # CYP2C19 Poor, CYP2C9 Poor (was Normal), CYP2D6 Normal
        "chromosome": ["10", "10", "22"],
        "position": ["96541615", "96702047", "42522500"]
    }
    df = pd.DataFrame(data)
    df.set_index("rsid", inplace=True)
    return df

def test_interaction_checker_init():
    """Test initialization of InteractionChecker."""
    dna_data = create_mock_dna_data()
    checker = InteractionChecker(dna_data)
    assert checker.dna_data is not None
    assert not checker.dna_data.empty

def test_drug_drug_interactions():
    """Test detection of drug-drug interactions."""
    dna_data = create_mock_dna_data()
    checker = InteractionChecker(dna_data)
    
    # Test known interaction
    meds = ["Warfarin", "Aspirin"]
    results = checker.check_drug_drug_interactions(meds)
    assert len(results) > 0
    assert any("warfarin" in r["drugs"] and "aspirin" in r["drugs"] for r in results)
    assert results[0]["severity"] == "Major"

    # Test no interaction
    meds = ["Paracetamol", "Vitamin C"]
    results = checker.check_drug_drug_interactions(meds)
    assert len(results) == 0

def test_drug_gene_interactions():
    """Test detection of drug-gene interactions."""
    dna_data = create_mock_dna_data()
    checker = InteractionChecker(dna_data)
    
    # Test Clopidogrel (CYP2C19) - Mock data is AA (Poor Metabolizer)
    meds = ["Clopidogrel"]
    results = checker.check_drug_gene_interactions(meds)
    assert len(results) > 0
    interaction = results[0]
    assert interaction["drug"] == "clopidogrel"
    assert interaction["gene"] == "CYP2C19"
    assert "Poor" in interaction["phenotype"]
    
    # Test Warfarin (CYP2C9) - Mock data is TT (Poor Metabolizer)
    # Current implementation returns all analyzed drugs with their status.
    meds = ["Warfarin"]
    results = checker.check_drug_gene_interactions(meds)
    assert len(results) > 0
    interaction = results[0]
    assert interaction["drug"] == "warfarin"
    assert interaction["gene"] == "CYP2C9"
    
    # Test Codeine (CYP2D6) - Mock data is GG (Normal Metabolizer)
    meds = ["Codeine"]
    results = checker.check_drug_gene_interactions(meds)
    assert len(results) > 0
    interaction = results[0]
    assert interaction["drug"] == "codeine"
    assert interaction["gene"] == "CYP2D6"
    assert "Normal" in interaction["phenotype"]
    
def test_analyze_method():
    """Test the main analyze method."""
    dna_data = create_mock_dna_data()
    checker = InteractionChecker(dna_data)
    
    meds = ["Warfarin", "Aspirin", "Clopidogrel"]
    results = checker.analyze(meds)
    
    assert "drug_drug" in results
    assert "drug_gene" in results
    assert len(results["drug_drug"]) > 0
    assert len(results["drug_gene"]) > 0
