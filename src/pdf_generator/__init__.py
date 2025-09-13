"""
Enhanced Educational PDF Report Generator
A comprehensive system for generating personalized genetic health reports
with educational content, visualizations, and actionable insights.
"""

from .main import generate_pdf_report, generate_enhanced_pdf_report
from .utils import get_evidence_stars
from .visualizations import (
    generate_constellation_map,
    generate_genetics_lifestyle_balance,
    generate_prs_gauge,
    generate_risk_histogram,
    generate_prs_percentile_plot,
    generate_carrier_probability_bars,
    generate_heatmap_gene_disease,
    generate_lifetime_risk_timeline,
    generate_health_score_infographic
)
from .sections import (
    add_cover_page,
    add_how_to_read_report,
    add_genetic_snapshot,
    add_detailed_health_chapter,
    add_executive_summary,
    add_comprehensive_carrier_status,
    add_pharmacogenomics_profile,
    add_disease_risk_assessment,
    add_polygenic_risk_scores,
    add_wellness_lifestyle_profile,
    add_advanced_analytics_dashboard,
    add_personalized_recommendations,
    add_methodology_references,
    add_appendix_raw_data
)

__version__ = "1.0.0"
__all__ = [
    'generate_pdf_report',
    'generate_enhanced_pdf_report',
    'get_evidence_stars',
    # All visualization functions
    'generate_constellation_map',
    'generate_genetics_lifestyle_balance',
    'generate_prs_gauge',
    'generate_risk_histogram',
    'generate_prs_percentile_plot',
    'generate_carrier_probability_bars',
    'generate_heatmap_gene_disease',
    'generate_lifetime_risk_timeline',
    'generate_health_score_infographic',
    # All section functions
    'add_cover_page',
    'add_how_to_read_report',
    'add_genetic_snapshot',
    'add_detailed_health_chapter',
    'add_medication_guide_section',
    'add_executive_summary',
    'add_comprehensive_carrier_status',
    'add_pharmacogenomics_profile',
    'add_disease_risk_assessment',
    'add_polygenic_risk_scores',
    'add_wellness_lifestyle_profile',
    'add_advanced_analytics_dashboard',
    'add_personalized_recommendations',
    'add_methodology_references',
    'add_appendix_raw_data'
]