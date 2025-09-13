"""
Main PDF generation functionality for the enhanced educational report.
"""

import os
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import analyze_wellness_snps
from snp_data import pgx_snps, prs_models, guidance_data
try:
    from .sections import (
        add_cover_page,
        add_how_to_read_report,
        add_genetic_snapshot,
        add_detailed_health_chapter,
        add_medication_guide_section,
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
except ImportError:
    from sections import (
        add_cover_page,
        add_how_to_read_report,
        add_genetic_snapshot,
        add_detailed_health_chapter,
        add_medication_guide_section,
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

def generate_enhanced_pdf_report(dna_data, results_dir, user_id="User"):
    """
    Generate the enhanced educational PDF report with the new structure.
    """
    doc = SimpleDocTemplate(os.path.join(results_dir, "Enhanced_Genomic_Health_Report.pdf"), pagesize=letter)
    story = []

    # Section 1: Your Guide to Personal Genetics (Pages 1-2)
    add_cover_page(story, user_id)
    add_how_to_read_report(story)

    # Section 2: Your Genetic Snapshot (Page 3)
    add_genetic_snapshot(story, dna_data)

    # Section 3: Detailed Health Chapters
    # Add key health conditions as detailed chapters
    key_conditions = [
        "Coronary Artery Disease",
        "Type 2 Diabetes",
        "Breast Cancer",
        "Alzheimer's Disease"
    ]

    for condition in key_conditions:
        # Calculate PRS percentile (placeholder - would be based on actual PRS calculation)
        prs_percentile = 65 if "Coronary" in condition else 45
        add_detailed_health_chapter(story, condition, dna_data, prs_percentile)

    # Section 4: Your Personalized Medication Guide
    # This includes pharmacogenomics with funnel graphics
    add_medication_guide_section(story, dna_data)

    # Legacy sections (can be kept or restructured)
    key_findings = [
        "High genetic risk for Coronary Artery Disease - discuss with cardiologist",
        "Carrier status for Cystic Fibrosis - important for family planning",
        "Ultra-rapid metabolizer for Codeine - avoid standard doses"
    ]
    health_score = 75
    add_executive_summary(story, key_findings, health_score)

    add_comprehensive_carrier_status(story, dna_data)
    add_disease_risk_assessment(story, dna_data)
    add_polygenic_risk_scores(story, dna_data)
    add_wellness_lifestyle_profile(story, dna_data)
    add_advanced_analytics_dashboard(story, dna_data)
    add_personalized_recommendations(story)
    add_methodology_references(story)
    add_appendix_raw_data(story, dna_data)

    try:
        doc.build(story)
        print(f"Enhanced PDF report generated successfully: {os.path.join(results_dir, 'Enhanced_Genomic_Health_Report.pdf')}")
    except Exception as e:
        print(f"Error generating enhanced PDF: {e}")

def generate_pdf_report(report_data, results_dir, dna_data):
    """
    Legacy function for backward compatibility.
    Generates the basic PDF report structure.
    """
    doc = SimpleDocTemplate(os.path.join(results_dir, "Genomic_Health_Report.pdf"), pagesize=letter)
    story = []

    # Add cover page
    add_cover_page(story, "User123")  # Placeholder user ID

    # Add executive summary
    key_findings = ["High risk for condition X", "Carrier for condition Y"]
    health_score = 75
    add_executive_summary(story, key_findings, health_score)

    # Add comprehensive carrier status
    add_comprehensive_carrier_status(story, dna_data)

    # Add pharmacogenomics profile
    add_pharmacogenomics_profile(story, dna_data)

    # Add disease risk assessment
    add_disease_risk_assessment(story, dna_data)

    # Add polygenic risk scores
    add_polygenic_risk_scores(story, dna_data)

    # Add wellness & lifestyle profile
    add_wellness_lifestyle_profile(story, dna_data)

    # Add advanced analytics dashboard
    add_advanced_analytics_dashboard(story, dna_data)

    # Add personalized recommendations
    add_personalized_recommendations(story)

    # Add methodology & references
    add_methodology_references(story)

    # Add appendix raw data
    add_appendix_raw_data(story, dna_data)

    try:
        doc.build(story)
        print(f"PDF report generated successfully: {os.path.join(results_dir, 'Genomic_Health_Report.pdf')}")
    except Exception as e:
        print(f"Error generating PDF: {e}")