import pytest
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.family_analysis import FamilyAnalyzer

def create_mock_profile(genotypes):
    """Create mock DNA profile."""
    data = {
        "rsid": [f"rs{i}" for i in range(len(genotypes))],
        "genotype": genotypes
    }
    df = pd.DataFrame(data)
    df.set_index("rsid", inplace=True)
    return df

def test_identical_twins():
    """Test analysis of identical profiles (100% IBS)."""
    g1 = ["AA", "GG", "CC", "TT"]
    df1 = create_mock_profile(g1)
    df2 = create_mock_profile(g1) # Same
    
    analyzer = FamilyAnalyzer(df1, df2)
    ibs = analyzer.calculate_identity_by_state()
    
    assert ibs == 1.0
    assert "Identical Twins" in analyzer.predict_relationship(ibs)

def test_parent_child():
    """Test analysis of Parent-Child (approx 75-80% IBS, 50% IBD)."""
    # Parent: AA, BB, CC, DD
    # Child:  AB, BC, CD, DE (Shares 1 allele at each locus)
    # IBS: 
    # AA vs AB -> 1 shared / 2 total = 0.5 match? No, IBS counts alleles.
    # AA (A,A) vs AB (A,B) -> Share A. 1 allele shared.
    # Wait, IBS calculation in code:
    # matches / total_alleles
    # AA vs AB: A in (A,B)? Yes. A in (A,B)? Yes. -> 2 matches?
    # Let's trace the code logic:
    # l1=[A,A], l2=[A,B]
    # loop A: in l2? Yes. shared=1. l2=[B]
    # loop A: in l2? No.
    # Total shared = 1.
    # Total alleles = 4.
    # IBS = 0.25? No, that's low.
    
    # Standard IBS definition:
    # IBS2 (2 shared alleles), IBS1 (1 shared), IBS0 (0 shared).
    # My code calculates "percentage of shared alleles".
    # AA vs AA -> 2 shared. (2/2 = 1.0 per locus)
    # AA vs AB -> 1 shared. (1/2 = 0.5 per locus)
    # AA vs BB -> 0 shared. (0/2 = 0.0 per locus)
    
    # Parent-Child should have at least 1 shared allele everywhere (IBS1 or IBS2).
    # So average IBS should be >= 0.5.
    # Actually, Parent AA, Child AA -> IBS 1.0.
    # Parent AA, Child AB -> IBS 0.5.
    # Average depends on heterozygosity.
    # But usually > 0.7.
    
    g1 = ["AA", "AA", "CC", "GG"]
    g2 = ["AA", "AB", "CC", "GT"] 
    # 1: AA-AA -> 2 shared (1.0)
    # 2: AA-AB -> 1 shared (0.5)
    # 3: CC-CC -> 2 shared (1.0)
    # 4: GG-GT -> 1 shared (0.5)
    # Avg: 0.75
    
    df1 = create_mock_profile(g1)
    df2 = create_mock_profile(g2)
    
    analyzer = FamilyAnalyzer(df1, df2)
    ibs = analyzer.calculate_identity_by_state()
    
    assert ibs == pytest.approx(0.75)
    assert "Parent-Child" in analyzer.predict_relationship(ibs)

def test_unrelated():
    """Test analysis of unrelated profiles."""
    g1 = ["AA", "CC", "GG", "TT"]
    g2 = ["TT", "GG", "CC", "AA"] # Completely opposite
    # AA-TT -> 0
    # CC-GG -> 0
    # ...
    
    df1 = create_mock_profile(g1)
    df2 = create_mock_profile(g2)
    
    analyzer = FamilyAnalyzer(df1, df2)
    ibs = analyzer.calculate_identity_by_state()
    
    assert ibs == 0.0
    assert "Unrelated" in analyzer.predict_relationship(ibs)

def test_mendelian_errors():
    """Test Mendelian error detection."""
    # Parent: AA
    # Child: BB -> Error
    
    g1 = ["AA", "CC"]
    g2 = ["BB", "CC"]
    
    df1 = create_mock_profile(g1)
    df2 = create_mock_profile(g2)
    
    analyzer = FamilyAnalyzer(df1, df2)
    stats = analyzer.analyze_mendelian_errors()
    
    assert stats["mendelian_errors"] == 1
    assert stats["total_comparisons"] == 2
    assert stats["error_rate"] == 0.5
    assert not stats["is_parent_child"]
