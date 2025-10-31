"""
Utility functions for the PDF report generator.
"""


def get_evidence_stars(rsid, condition_type="general"):
    """
    Returns star rating string based on evidence strength for a given SNP/condition.
    ★★★★★ = Very strong evidence (multiple large studies, GWAS confirmed)
    ★★★★☆ = Strong evidence (several studies, consistent findings)
    ★★★☆☆ = Moderate evidence (some studies, emerging data)
    ★★☆☆☆ = Limited evidence (few studies, preliminary data)
    ★☆☆☆☆ = Very limited evidence (single study or anecdotal)
    """
    # Define evidence strength based on SNP type and known data
    evidence_levels = {
        "monogenic": 5,  # Single gene disorders like CFTR
        "cancer": 5,  # Well-established cancer genes
        "cardiovascular": 4,  # Strong evidence for heart disease genes
        "pgx": 4,  # Pharmacogenomics well-studied
        "prs": 4,  # Polygenic risk scores from large GWAS
        "wellness": 3,  # Lifestyle traits, moderate evidence
        "neuro": 3,  # Neurological conditions
        "mito": 4,  # Mitochondrial disorders well-characterized
        "protective": 3,  # Protective alleles, emerging data
        "ancestry": 4,  # Ancestry panels well-validated
        "default": 3,  # Default moderate evidence
    }

    stars = "★" * evidence_levels.get(condition_type, 3)
    empty_stars = "☆" * (5 - len(stars))
    return stars + empty_stars
