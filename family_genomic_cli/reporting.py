"""
Family Genomic Reporting Module

This module provides comprehensive reporting capabilities for family genomic analysis,
including PDF reports, JSON structured data, and CSV summaries.
"""

import json
import os
import pandas as pd
from typing import Dict, List, Optional, Any
from pathlib import Path
from copied_modules.logging_utils import get_logger

# Import the PDF generator
from copied_modules.pdf_generator import (
    generate_enhanced_pdf_report,
    add_cover_page,
    add_executive_summary,
    add_genetic_snapshot,
    add_comprehensive_carrier_status,
    add_pharmacogenomics_profile,
    add_disease_risk_assessment,
    add_polygenic_risk_scores,
    add_wellness_lifestyle_profile,
    add_advanced_analytics_dashboard,
    add_personalized_recommendations,
    add_methodology_references,
    add_appendix_raw_data,
)

from copied_modules.pdf_generator.sections import (
    add_detailed_health_chapter,
    add_medication_guide_section,
)

from copied_modules.pdf_generator.visualizations import (
    generate_constellation_map,
    generate_prs_gauge,
    generate_prs_percentile_plot,
)

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

logger = get_logger(__name__)


def generate_individual_pdf_report(analysis_results: Dict, output_dir: str, member_name: str = "Individual") -> str:
    """
    Generate a PDF report for an individual family member.

    Args:
        analysis_results: Dict containing analysis results for the individual
        output_dir: Directory to save the report
        member_name: Name of the family member

    Returns:
        Path to the generated PDF file
    """
    logger.info(f"Generating individual PDF report for {member_name}")
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, f"{member_name.lower().replace(' ', '_')}_genomic_report.pdf")

    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = []

    # Cover page
    add_cover_page(story, member_name)

    # Executive summary
    key_findings = _extract_key_findings(analysis_results)
    health_score = _calculate_health_score(analysis_results)
    add_executive_summary(story, key_findings, health_score)

    # Genetic snapshot
    dna_data = analysis_results.get('dna_data', pd.DataFrame())
    add_genetic_snapshot(story, dna_data)

    # Detailed health chapters for key conditions
    key_conditions = ["Coronary Artery Disease", "Type 2 Diabetes", "Breast Cancer", "Alzheimer's Disease"]
    for condition in key_conditions:
        prs_percentile = _get_condition_prs_percentile(analysis_results, condition)
        add_detailed_health_chapter(story, condition, dna_data, prs_percentile)

    # Medication guide
    add_medication_guide_section(story, dna_data)

    # Comprehensive sections
    add_comprehensive_carrier_status(story, dna_data)
    add_pharmacogenomics_profile(story, dna_data)
    add_disease_risk_assessment(story, dna_data)
    add_polygenic_risk_scores(story, dna_data)
    add_wellness_lifestyle_profile(story, dna_data)
    add_advanced_analytics_dashboard(story, dna_data)
    add_personalized_recommendations(story)
    add_methodology_references(story)
    add_appendix_raw_data(story, dna_data)

    try:
        doc.build(story)
        logger.info(f"Individual PDF report generated successfully: {pdf_path}")
        return pdf_path
    except Exception as e:
        logger.error(f"Error generating individual PDF for {member_name}: {e}", exc_info=True)
        return ""


def generate_family_pdf_report(family_analysis_results: Dict, individual_results: Dict[str, Dict],
                              output_dir: str, family_name: str = "Family") -> str:
    """
    Generate an enhanced family PDF report focused on the child with inheritance mapping.

    Args:
        family_analysis_results: Results from family analysis
        individual_results: Dict with individual analysis results for each family member
        output_dir: Directory to save the report
        family_name: Name for the family

    Returns:
        Path to the generated PDF file
    """
    logger.info(f"Generating family PDF report for {family_name}")
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, f"{family_name.lower().replace(' ', '_')}_family_genomic_report.pdf")

    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = []

    # Cover page
    add_cover_page(story, f"{family_name} Family")

    # Executive summary
    key_findings = _extract_family_key_findings(family_analysis_results, individual_results)
    health_score = _calculate_family_health_score(individual_results)
    add_executive_summary(story, key_findings, health_score)

    # Family-specific sections
    add_family_executive_summary(story, family_analysis_results, individual_results)
    add_genetic_inheritance_map(story, family_analysis_results)
    add_family_clinical_risks(story, family_analysis_results, individual_results)
    add_carrier_status_compound_risks(story, family_analysis_results)
    add_family_pharmacogenomics(story, individual_results)
    add_family_polygenic_risk_scores(story, individual_results)
    add_family_wellness_profile(story, individual_results)
    add_advanced_family_analytics(story, family_analysis_results, individual_results)

    # Appendix with QC data
    add_family_qc_appendix(story, family_analysis_results)

    try:
        doc.build(story)
        logger.info(f"Family PDF report generated successfully: {pdf_path}")
        return pdf_path
    except Exception as e:
        logger.error(f"Error generating family PDF for {family_name}: {e}", exc_info=True)
        return ""


def generate_json_report(analysis_results: Dict, family_analysis_results: Optional[Dict] = None,
                        output_dir: str = ".", filename: str = "genomic_report.json") -> str:
    """
    Generate a comprehensive JSON report with all analysis results.

    Args:
        analysis_results: Individual or family analysis results
        family_analysis_results: Optional family-specific results
        output_dir: Directory to save the report
        filename: Name of the JSON file

    Returns:
        Path to the generated JSON file
    """
    logger.info(f"Generating JSON report: {filename}")
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, filename)

    # Structure the JSON data
    json_data = {
        "report_type": "family_genomic_analysis" if family_analysis_results else "individual_genomic_analysis",
        "timestamp": pd.Timestamp.now().isoformat(),
        "individual_results": analysis_results,
    }

    if family_analysis_results:
        json_data["family_analysis_results"] = family_analysis_results

    # Convert DataFrames to dict for JSON serialization
    def convert_to_serializable(obj):
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict('index')
        elif isinstance(obj, pd.Series):
            return obj.to_dict()
        elif isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_serializable(item) for item in obj]
        else:
            return obj

    json_data = convert_to_serializable(json_data)

    try:
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=2)
        logger.info(f"JSON report generated successfully: {json_path}")
        return json_path
    except Exception as e:
        logger.error(f"Error generating JSON report: {e}", exc_info=True)
        return ""


def generate_csv_report(analysis_results: Dict, family_analysis_results: Optional[Dict] = None,
                       output_dir: str = ".", filename_prefix: str = "genomic_report") -> List[str]:
    """
    Generate CSV summaries of key findings and risks.

    Args:
        analysis_results: Individual or family analysis results
        family_analysis_results: Optional family-specific results
        output_dir: Directory to save the reports
        filename_prefix: Prefix for CSV filenames

    Returns:
        List of paths to generated CSV files
    """
    logger.info(f"Generating CSV reports with prefix: {filename_prefix}")
    os.makedirs(output_dir, exist_ok=True)
    csv_files = []

    try:
        # Key findings summary
        key_findings_csv = os.path.join(output_dir, f"{filename_prefix}_key_findings.csv")
        key_findings_data = _extract_key_findings_for_csv(analysis_results, family_analysis_results)
        if key_findings_data:
            df = pd.DataFrame(key_findings_data)
            df.to_csv(key_findings_csv, index=False)
            csv_files.append(key_findings_csv)
            logger.debug(f"Generated key findings CSV: {key_findings_csv}")

        # Risk summary
        risk_csv = os.path.join(output_dir, f"{filename_prefix}_risks.csv")
        risk_data = _extract_risks_for_csv(analysis_results, family_analysis_results)
        if risk_data:
            df = pd.DataFrame(risk_data)
            df.to_csv(risk_csv, index=False)
            csv_files.append(risk_csv)
            logger.debug(f"Generated risks CSV: {risk_csv}")

        # PRS summary
        prs_csv = os.path.join(output_dir, f"{filename_prefix}_prs.csv")
        prs_data = _extract_prs_for_csv(analysis_results, family_analysis_results)
        if prs_data:
            df = pd.DataFrame(prs_data)
            df.to_csv(prs_csv, index=False)
            csv_files.append(prs_csv)
            logger.debug(f"Generated PRS CSV: {prs_csv}")

        logger.info(f"CSV reports generated successfully: {len(csv_files)} files")
        return csv_files

    except Exception as e:
        logger.error(f"Error generating CSV reports: {e}", exc_info=True)
        return []


def generate_reports(analysis_results: Dict[str, Dict], family_analysis_results: Dict,
                    output_dir: str = ".", report_formats: List[str] = None,
                    family_name: str = "Family") -> Dict[str, List[str]]:
    """
    Main function to generate reports in multiple formats.

    Args:
        analysis_results: Dict with member names as keys and their analysis results as values
        family_analysis_results: Results from family analysis
        output_dir: Directory to save reports
        report_formats: List of formats to generate ('pdf', 'json', 'csv')
        family_name: Name for the family

    Returns:
        Dict with format keys and lists of generated file paths
    """
    logger.info(f"Generating reports for {family_name} in formats: {report_formats}")
    if report_formats is None:
        report_formats = ['pdf', 'json', 'csv']

    generated_files = {fmt: [] for fmt in report_formats}

    # Generate individual PDF reports
    if 'pdf' in report_formats:
        logger.debug("Generating individual PDF reports")
        for member, results in analysis_results.items():
            pdf_path = generate_individual_pdf_report(results, output_dir, member)
            if pdf_path:
                generated_files['pdf'].append(pdf_path)

        # Generate family PDF report
        logger.debug("Generating family PDF report")
        family_pdf_path = generate_family_pdf_report(family_analysis_results, analysis_results, output_dir, family_name)
        if family_pdf_path:
            generated_files['pdf'].append(family_pdf_path)

    # Generate JSON report
    if 'json' in report_formats:
        logger.debug("Generating JSON report")
        json_path = generate_json_report(analysis_results, family_analysis_results, output_dir,
                                       f"{family_name.lower().replace(' ', '_')}_report.json")
        if json_path:
            generated_files['json'].append(json_path)

    # Generate CSV reports
    if 'csv' in report_formats:
        logger.debug("Generating CSV reports")
        csv_paths = generate_csv_report(analysis_results, family_analysis_results, output_dir,
                                      f"{family_name.lower().replace(' ', '_')}_report")
        generated_files['csv'].extend(csv_paths)

    logger.info(f"Report generation completed: {sum(len(files) for files in generated_files.values())} files generated")
    return generated_files


# Helper functions for data extraction and processing

def _extract_key_findings(analysis_results: Dict) -> List[str]:
    """Extract key findings from analysis results."""
    findings = []

    # Add PRS findings
    if 'polygenic_risk_scores' in analysis_results:
        prs_results = analysis_results['polygenic_risk_scores']
        for disease, data in prs_results.items():
            if isinstance(data, dict) and data.get('percentile', 0) > 75:
                findings.append(f"High genetic risk for {disease}")

    # Add carrier status findings
    if 'carrier_status' in analysis_results:
        carrier_data = analysis_results['carrier_status']
        if carrier_data:
            carrier_count = sum(1 for item in carrier_data if item.get('Status') in ['Carrier', 'Affected'])
            if carrier_count > 0:
                findings.append(f"Carrier status detected for {carrier_count} conditions")

    # Add PGx findings
    if 'pharmacogenomics' in analysis_results:
        pgx_data = analysis_results['pharmacogenomics']
        if pgx_data:
            findings.append("Pharmacogenomic variants detected - consult with healthcare provider for medication guidance")

    return findings or ["Analysis completed - review detailed results for personalized insights"]


def _calculate_health_score(analysis_results: Dict) -> int:
    """Calculate an overall health score from analysis results."""
    base_score = 75  # Default moderate score

    # Adjust based on PRS
    if 'polygenic_risk_scores' in analysis_results:
        prs_results = analysis_results['polygenic_risk_scores']
        high_risk_count = sum(1 for data in prs_results.values()
                            if isinstance(data, dict) and data.get('percentile', 0) > 75)
        base_score -= high_risk_count * 5

    # Adjust based on carrier status
    if 'carrier_status' in analysis_results:
        carrier_data = analysis_results['carrier_status']
        affected_count = sum(1 for item in carrier_data if item.get('Status') == 'Affected')
        base_score -= affected_count * 10

    return max(0, min(100, base_score))


def _get_condition_prs_percentile(analysis_results: Dict, condition: str) -> int:
    """Get PRS percentile for a specific condition."""
    if 'polygenic_risk_scores' in analysis_results:
        prs_results = analysis_results['polygenic_risk_scores']
        if condition in prs_results and isinstance(prs_results[condition], dict):
            return int(prs_results[condition].get('percentile', 50))
    return 50


def _extract_family_key_findings(family_analysis_results: Dict, individual_results: Dict[str, Dict]) -> List[str]:
    """Extract key findings specific to family analysis."""
    findings = []

    # Shared risks
    if 'shared_risks' in family_analysis_results:
        shared = family_analysis_results['shared_risks']
        if shared.get('high_prs_shared'):
            findings.append(f"Shared high genetic risk detected in {len(shared['high_prs_shared'])} conditions across family members")

    # Relationship verification
    if 'relationship_verification' in family_analysis_results:
        rel_verify = family_analysis_results['relationship_verification']
        family_config = rel_verify.get('family_configuration', {})
        if family_config.get('type') == 'trio':
            findings.append("Family relationship verification confirmed")
        elif family_config.get('issues'):
            findings.append("Family relationship verification completed with some considerations")

    # Compound heterozygosity
    if 'compound_heterozygosity' in family_analysis_results:
        compound_het = family_analysis_results['compound_heterozygosity']
        if compound_het:
            findings.append(f"Compound heterozygous patterns detected in {len(compound_het)} genes")

    # Individual findings summary
    all_individual_findings = []
    for member_results in individual_results.values():
        all_individual_findings.extend(_extract_key_findings(member_results))

    # Add most critical individual findings
    unique_findings = list(set(all_individual_findings))
    findings.extend(unique_findings[:3])  # Limit to top 3

    return findings or ["Family analysis completed - review detailed results for comprehensive insights"]


def _calculate_family_health_score(individual_results: Dict[str, Dict]) -> int:
    """Calculate family health score based on individual scores."""
    if not individual_results:
        return 75

    individual_scores = []
    for results in individual_results.values():
        score = _calculate_health_score(results)
        individual_scores.append(score)

    # Average family score with slight penalty for multiple high-risk members
    avg_score = sum(individual_scores) / len(individual_scores)
    high_risk_penalty = sum(1 for score in individual_scores if score < 60) * 5

    return max(0, min(100, int(avg_score - high_risk_penalty)))


# Family-specific PDF sections

def add_family_executive_summary(story, family_analysis_results: Dict, individual_results: Dict[str, Dict]):
    """Add family-specific executive summary."""
    styles = getSampleStyleSheet()

    story.append(Paragraph("Family Genomic Analysis Summary", styles["h1"]))
    story.append(Spacer(1, 0.5 * inch))

    # Family configuration
    rel_verify = family_analysis_results.get('relationship_verification', {})
    family_config = rel_verify.get('family_configuration', {})

    story.append(Paragraph(f"Family Configuration: {family_config.get('type', 'Unknown').replace('_', ' ').title()}", styles["h2"]))
    story.append(Paragraph(".1f", styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    # Shared risks summary
    shared_risks = family_analysis_results.get('shared_risks', {})
    if shared_risks.get('high_prs_shared'):
        story.append(Paragraph(f"Shared High-Risk Conditions: {len(shared_risks['high_prs_shared'])}", styles["h3"]))
        for shared in shared_risks['high_prs_shared'][:3]:  # Top 3
            members_str = ", ".join(shared['members'])
            story.append(Paragraph(f"• {shared['disease']}: {members_str}", styles["Normal"]))

    story.append(PageBreak())


def add_genetic_inheritance_map(story, family_analysis_results: Dict):
    """Add genetic inheritance map visualization."""
    styles = getSampleStyleSheet()

    story.append(Paragraph("Genetic Inheritance Map", styles["h1"]))
    story.append(Spacer(1, 0.5 * inch))

    # Variant origins
    variant_origins = family_analysis_results.get('variant_origins', {})
    if variant_origins:
        story.append(Paragraph("Key Variant Inheritance Patterns:", styles["h3"]))

        data = [["Variant", "Child Genotype", "Origin", "Possible Sources"]]
        for rsid, info in list(variant_origins.items())[:20]:  # Limit for display
            data.append([
                rsid,
                info.get('child_genotype', 'N/A'),
                info.get('origin', 'unknown'),
                ", ".join(info.get('possible_sources', []))
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
        ]))
        story.append(table)

    story.append(PageBreak())


def add_family_clinical_risks(story, family_analysis_results: Dict, individual_results: Dict[str, Dict]):
    """Add family clinical risks section."""
    styles = getSampleStyleSheet()

    story.append(Paragraph("Family Clinical Risk Assessment", styles["h1"]))
    story.append(Spacer(1, 0.5 * inch))

    # Shared clinical risks
    shared_risks = family_analysis_results.get('shared_risks', {})
    if shared_risks.get('clinical_risks_shared'):
        story.append(Paragraph("Shared Clinical Risk Variants:", styles["h3"]))

        for shared in shared_risks['clinical_risks_shared'][:10]:  # Limit for display
            members_str = ", ".join(shared['members'])
            story.append(Paragraph(f"• {shared['variant']}: {members_str}", styles["Normal"]))

    story.append(PageBreak())


def add_carrier_status_compound_risks(story, family_analysis_results: Dict):
    """Add carrier status and compound risks section."""
    styles = getSampleStyleSheet()

    story.append(Paragraph("Carrier Status & Compound Risks", styles["h1"]))
    story.append(Spacer(1, 0.5 * inch))

    # Compound heterozygosity
    compound_het = family_analysis_results.get('compound_heterozygosity', {})
    if compound_het:
        story.append(Paragraph("Compound Heterozygous Patterns Detected:", styles["h3"]))

        for gene, data in compound_het.items():
            story.append(Paragraph(f"Gene: {gene}", styles["h4"]))
            if 'maternal_variants' in data:
                maternal_rsids = [v['rsid'] for v in data['maternal_variants']]
                story.append(Paragraph(f"• Maternal variants: {', '.join(maternal_rsids)}", styles["Normal"]))
            if 'paternal_variants' in data:
                paternal_rsids = [v['rsid'] for v in data['paternal_variants']]
                story.append(Paragraph(f"• Paternal variants: {', '.join(paternal_rsids)}", styles["Normal"]))

    story.append(PageBreak())


def add_family_pharmacogenomics(story, individual_results: Dict[str, Dict]):
    """Add family pharmacogenomics section."""
    styles = getSampleStyleSheet()

    story.append(Paragraph("Family Pharmacogenomics Profile", styles["h1"]))
    story.append(Spacer(1, 0.5 * inch))

    # Compare PGx across family members
    pgx_comparison = {}
    for member, results in individual_results.items():
        if 'pharmacogenomics' in results:
            pgx_comparison[member] = results['pharmacogenomics']

    if pgx_comparison:
        story.append(Paragraph("Pharmacogenomic Variants by Family Member:", styles["h3"]))

        # Create comparison table
        members = list(pgx_comparison.keys())
        if len(members) > 1:
            data = [["Gene/Drug"] + members]
            all_genes = set()
            for member_data in pgx_comparison.values():
                if isinstance(member_data, list):
                    for item in member_data:
                        if 'Gene' in item:
                            all_genes.add(item['Gene'])

            for gene in sorted(all_genes):
                row = [gene]
                for member in members:
                    member_data = pgx_comparison[member]
                    if isinstance(member_data, list):
                        gene_info = next((item for item in member_data if item.get('Gene') == gene), {})
                        genotype = gene_info.get('Genotype', 'N/A')
                        metabolism = gene_info.get('Metabolism', 'N/A')
                        row.append(f"{genotype} ({metabolism})")
                    else:
                        row.append("N/A")
                data.append(row)

            table = Table(data)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
            ]))
            story.append(table)

    story.append(PageBreak())


def add_family_polygenic_risk_scores(story, individual_results: Dict[str, Dict]):
    """Add family PRS comparison section."""
    styles = getSampleStyleSheet()

    story.append(Paragraph("Family Polygenic Risk Score Comparison", styles["h1"]))
    story.append(Spacer(1, 0.5 * inch))

    # Collect PRS data
    prs_data = {}
    diseases = set()
    for member, results in individual_results.items():
        if 'polygenic_risk_scores' in results:
            prs_data[member] = results['polygenic_risk_scores']
            diseases.update(results['polygenic_risk_scores'].keys())

    if prs_data and diseases:
        story.append(Paragraph("PRS Comparison Across Family Members:", styles["h3"]))

        data = [["Disease"] + list(prs_data.keys())]
        for disease in sorted(diseases):
            row = [disease]
            for member in prs_data.keys():
                member_prs = prs_data[member].get(disease, {})
                if isinstance(member_prs, dict) and 'percentile' in member_prs:
                    percentile = member_prs['percentile']
                    row.append(".1f")
                else:
                    row.append("N/A")
            data.append(row)

        table = Table(data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
        ]))
        story.append(table)

    story.append(PageBreak())


def add_family_wellness_profile(story, individual_results: Dict[str, Dict]):
    """Add family wellness profile section."""
    styles = getSampleStyleSheet()

    story.append(Paragraph("Family Wellness & Lifestyle Profile", styles["h1"]))
    story.append(Spacer(1, 0.5 * inch))

    # Aggregate wellness traits across family
    wellness_summary = {}
    for member, results in individual_results.items():
        if 'wellness_profile' in results:
            wellness_data = results['wellness_profile']
            if isinstance(wellness_data, list):
                for trait in wellness_data:
                    trait_name = trait.get('name', trait.get('Trait', 'Unknown'))
                    if trait_name not in wellness_summary:
                        wellness_summary[trait_name] = []
                    wellness_summary[trait_name].append(member)

    if wellness_summary:
        story.append(Paragraph("Shared Wellness Traits Across Family:", styles["h3"]))

        for trait, members in wellness_summary.items():
            if len(members) > 1:  # Only show shared traits
                members_str = ", ".join(members)
                story.append(Paragraph(f"• {trait}: {members_str}", styles["Normal"]))

    story.append(PageBreak())


def add_advanced_family_analytics(story, family_analysis_results: Dict, individual_results: Dict[str, Dict]):
    """Add advanced family analytics section."""
    styles = getSampleStyleSheet()

    story.append(Paragraph("Advanced Family Analytics", styles["h1"]))
    story.append(Spacer(1, 0.5 * inch))

    # Relationship verification details
    rel_verify = family_analysis_results.get('relationship_verification', {})
    if rel_verify:
        story.append(Paragraph("Relationship Verification Results:", styles["h3"]))

        for relationship, data in rel_verify.items():
            if relationship != 'family_configuration':
                confidence = data.get('confidence_score', 0)
                predicted = data.get('predicted_relationship', 'Unknown')
                story.append(Paragraph(f"• {relationship.replace('_', ' ').title()}: {predicted} (confidence: {confidence:.2f})", styles["Normal"]))

    # Uniparental disomy if detected
    upd_data = family_analysis_results.get('uniparental_disomy', {})
    if upd_data:
        story.append(Paragraph("Uniparental Disomy Detection:", styles["h3"]))

        for chr_name, regions in upd_data.items():
            for region in regions:
                story.append(Paragraph(f"• Chromosome {chr_name}: {region['type']} detected (confidence: {region['confidence']:.2f})", styles["Normal"]))

    story.append(PageBreak())


def add_family_qc_appendix(story, family_analysis_results: Dict):
    """Add family QC data appendix."""
    styles = getSampleStyleSheet()

    story.append(Paragraph("Appendix: Family Analysis Quality Control", styles["h1"]))
    story.append(Spacer(1, 0.5 * inch))

    # Relationship verification QC
    rel_verify = family_analysis_results.get('relationship_verification', {})
    if rel_verify:
        story.append(Paragraph("Relationship Verification Metrics:", styles["h3"]))

        for relationship, data in rel_verify.items():
            if relationship != 'family_configuration':
                ibs_score = data.get('ibs_score', 0)
                mendelian_errors = data.get('mendelian_errors', {})
                error_rate = mendelian_errors.get('error_rate', 0)

                story.append(Paragraph(f"{relationship.replace('_', ' ').title()}:", styles["h4"]))
                story.append(Paragraph(f"• IBS Score: {ibs_score:.3f}", styles["Normal"]))
                story.append(Paragraph(f"• Mendelian Error Rate: {error_rate:.3f}", styles["Normal"]))

    story.append(PageBreak())


# CSV helper functions

def _extract_key_findings_for_csv(analysis_results: Dict, family_analysis_results: Optional[Dict] = None) -> List[Dict]:
    """Extract key findings for CSV export."""
    findings = []

    if family_analysis_results:
        # Family-level findings
        shared_risks = family_analysis_results.get('shared_risks', {})
        if shared_risks.get('high_prs_shared'):
            for shared in shared_risks['high_prs_shared']:
                findings.append({
                    'Category': 'Shared High PRS',
                    'Detail': shared['disease'],
                    'Members': ', '.join(shared['members']),
                    'Severity': 'High'
                })

        compound_het = family_analysis_results.get('compound_heterozygosity', {})
        for gene in compound_het.keys():
            findings.append({
                'Category': 'Compound Heterozygosity',
                'Detail': gene,
                'Members': 'Child',
                'Severity': 'High'
            })
    else:
        # Individual findings
        individual_findings = _extract_key_findings(analysis_results)
        for finding in individual_findings:
            findings.append({
                'Category': 'Key Finding',
                'Detail': finding,
                'Members': 'Individual',
                'Severity': 'Medium'
            })

    return findings


def _extract_risks_for_csv(analysis_results: Dict, family_analysis_results: Optional[Dict] = None) -> List[Dict]:
    """Extract risk data for CSV export."""
    risks = []

    if family_analysis_results:
        # Family risks
        shared_clinical = family_analysis_results.get('shared_risks', {}).get('clinical_risks_shared', [])
        for shared in shared_clinical:
            risks.append({
                'Type': 'Shared Clinical Risk',
                'Variant': shared['variant'],
                'Members': ', '.join(shared['members']),
                'Risk_Level': 'Shared'
            })
    else:
        # Individual risks
        if 'carrier_status' in analysis_results:
            for item in analysis_results['carrier_status']:
                if item.get('Status') in ['Carrier', 'Affected']:
                    risks.append({
                        'Type': 'Carrier Status',
                        'Variant': item.get('rsID', ''),
                        'Condition': item.get('Condition', ''),
                        'Risk_Level': item.get('Status', '')
                    })

    return risks


def _extract_prs_for_csv(analysis_results: Dict, family_analysis_results: Optional[Dict] = None) -> List[Dict]:
    """Extract PRS data for CSV export."""
    prs_data = []

    if family_analysis_results:
        # Compare PRS across family members (assuming analysis_results contains individual results)
        if isinstance(analysis_results, dict):
            diseases = set()
            for member_results in analysis_results.values():
                if 'polygenic_risk_scores' in member_results:
                    diseases.update(member_results['polygenic_risk_scores'].keys())

            for disease in diseases:
                row = {'Disease': disease}
                for member, member_results in analysis_results.items():
                    if 'polygenic_risk_scores' in member_results:
                        prs_info = member_results['polygenic_risk_scores'].get(disease, {})
                        if isinstance(prs_info, dict):
                            row[f'{member}_Percentile'] = prs_info.get('percentile', 'N/A')
                            row[f'{member}_Score'] = prs_info.get('score', 'N/A')
                prs_data.append(row)
    else:
        # Individual PRS
        if 'polygenic_risk_scores' in analysis_results:
            for disease, prs_info in analysis_results['polygenic_risk_scores'].items():
                if isinstance(prs_info, dict):
                    prs_data.append({
                        'Disease': disease,
                        'Percentile': prs_info.get('percentile', 'N/A'),
                        'Score': prs_info.get('score', 'N/A'),
                        'Risk_Level': prs_info.get('risk_level', 'N/A')
                    })

    return prs_data
