"""
PDF section functions for generating different parts of the report.
"""

import pandas as pd
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from .utils import get_evidence_stars
    from .visualizations import (
        generate_constellation_map,
        generate_genetics_lifestyle_balance,
        generate_prs_gauge,
        generate_metabolism_funnel,
        generate_risk_histogram,
        generate_prs_percentile_plot,
        generate_carrier_probability_bars
    )
except ImportError:
    # Fallback for when running as script
    from utils import get_evidence_stars
    from visualizations import (
        generate_constellation_map,
        generate_genetics_lifestyle_balance,
        generate_prs_gauge,
        generate_metabolism_funnel,
        generate_risk_histogram,
        generate_prs_percentile_plot,
        generate_carrier_probability_bars
    )

def add_cover_page(story, user_id):
    """Add personalized, professional cover page."""
    styles = getSampleStyleSheet()

    # Main title
    title_style = ParagraphStyle('Title', parent=styles['h1'], fontSize=28, alignment=1, spaceAfter=40, fontName='Helvetica-Bold')
    story.append(Paragraph("Your Guide to Personal Genetics", title_style))

    # Subtitle
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['h2'], fontSize=18, alignment=1, spaceAfter=60, textColor=colors.darkblue)
    story.append(Paragraph("Understanding Your Genetic Health Journey", subtitle_style))

    # Personalized section
    personal_style = ParagraphStyle('Personal', parent=styles['Normal'], fontSize=14, alignment=1, spaceAfter=20)
    story.append(Paragraph(f"Prepared for: {user_id}", personal_style))
    story.append(Paragraph("Date: " + pd.Timestamp.now().strftime("%B %d, %Y"), personal_style))

    story.append(Spacer(1, 2*inch))

    # Educational tagline
    tagline_style = ParagraphStyle('Tagline', parent=styles['Italic'], fontSize=12, alignment=1, spaceAfter=40, textColor=colors.darkgreen)
    story.append(Paragraph("Transforming genetic data into actionable health insights", tagline_style))

    story.append(PageBreak())

def add_how_to_read_report(story):
    """Add educational page explaining how to read the genetic report."""
    styles = getSampleStyleSheet()

    # Page title
    title_style = ParagraphStyle('SectionTitle', parent=styles['h1'], fontSize=22, alignment=0, spaceAfter=30, textColor=colors.darkblue)
    story.append(Paragraph("How to Read Your Genetic Report", title_style))

    story.append(Spacer(1, 0.5*inch))

    # Monogenic vs Polygenic explanation
    subsection_style = ParagraphStyle('Subsection', parent=styles['h2'], fontSize=16, spaceAfter=15, textColor=colors.darkgreen)
    story.append(Paragraph("Monogenic vs. Polygenic Conditions", subsection_style))

    analogy_style = ParagraphStyle('Analogy', parent=styles['Normal'], fontSize=12, spaceAfter=20, leftIndent=20)
    story.append(Paragraph("Some conditions, like Cystic Fibrosis, are strongly influenced by variants in a single gene. Think of it like a <b>light switch</b> - if you have the specific variants, the switch is flipped, and the risk is very high.", analogy_style))

    story.append(Paragraph("Most common conditions, like Type 2 Diabetes, are influenced by many genes working together, each having a small effect. Think of it as a <b>dimmer switch</b> - your genetic variants can slide the dimmer up or down, increasing or decreasing your predisposition. Your lifestyle choices are the main hand on the switch.", analogy_style))

    story.append(Spacer(1, 0.5*inch))

    # Evidence strength explanation
    story.append(Paragraph("Strength of Evidence Rating System", subsection_style))

    evidence_style = ParagraphStyle('Evidence', parent=styles['Normal'], fontSize=11, spaceAfter=10, leftIndent=20)
    story.append(Paragraph("Throughout this report, you'll see star ratings that indicate how well-studied and scientifically established a particular gene-trait connection is:", evidence_style))

    star_examples = [
        ("★★★★★", "Very strong evidence (multiple large studies, GWAS confirmed)"),
        ("★★★★☆", "Strong evidence (several studies, consistent findings)"),
        ("★★★☆☆", "Moderate evidence (some studies, emerging data)"),
        ("★★☆☆☆", "Limited evidence (few studies, preliminary data)"),
        ("★☆☆☆☆", "Very limited evidence (single study or anecdotal)")
    ]

    for stars, description in star_examples:
        star_style = ParagraphStyle('StarExample', parent=styles['Normal'], fontSize=11, spaceAfter=5, leftIndent=40)
        story.append(Paragraph(f"{stars} - {description}", star_style))

    story.append(Spacer(1, 0.5*inch))

    # Key takeaway
    takeaway_style = ParagraphStyle('Takeaway', parent=styles['Italic'], fontSize=12, spaceAfter=20, textColor=colors.darkred, leftIndent=20)
    story.append(Paragraph("Remember: Your genetics load the gun, but your lifestyle pulls the trigger. This report empowers you to make informed choices about your health journey.", takeaway_style))

    story.append(PageBreak())

def add_genetic_snapshot(story, dna_data):
    """Add the Genetic Snapshot section with Priority Insights and Constellation Map."""
    styles = getSampleStyleSheet()

    # Section title
    title_style = ParagraphStyle('SectionTitle', parent=styles['h1'], fontSize=22, alignment=0, spaceAfter=20, textColor=colors.darkblue)
    story.append(Paragraph("Your Genetic Snapshot", title_style))

    story.append(Spacer(1, 0.3*inch))

    # Priority Insights Box
    insights_style = ParagraphStyle('InsightsTitle', parent=styles['h2'], fontSize=16, spaceAfter=15, textColor=colors.darkred)
    story.append(Paragraph("Priority Insights", insights_style))

    # Sample priority insights - in real implementation, this would be based on actual risk analysis
    insights = [
        "High genetic risk for Coronary Artery Disease - discuss with cardiologist",
        "Carrier status for Cystic Fibrosis - important for family planning",
        "Ultra-rapid metabolizer for Codeine - avoid standard doses"
    ]

    for insight in insights:
        insight_style = ParagraphStyle('Insight', parent=styles['Normal'], fontSize=11, spaceAfter=8, leftIndent=20, bulletIndent=10)
        story.append(Paragraph(f"• {insight}", insight_style))

    story.append(Spacer(1, 0.5*inch))

    # Health Predisposition Map
    map_title_style = ParagraphStyle('MapTitle', parent=styles['h2'], fontSize=16, spaceAfter=15, textColor=colors.darkgreen)
    story.append(Paragraph("Health Predisposition Map", map_title_style))

    map_desc_style = ParagraphStyle('MapDesc', parent=styles['Normal'], fontSize=10, spaceAfter=15, leftIndent=20)
    story.append(Paragraph("This constellation map shows your genetic predispositions across different health categories. Larger, brighter stars indicate higher risk with stronger scientific evidence.", map_desc_style))

    # Add constellation map visualization
    buf = generate_constellation_map({}, "Your Health Predisposition Constellation")
    story.append(Image(buf, width=6*inch, height=5*inch))

    story.append(PageBreak())

def add_detailed_health_chapter(story, condition_name, dna_data, prs_percentile=50):
    """Add a detailed health chapter for a specific condition."""
    styles = getSampleStyleSheet()

    # Title, Result & Confidence
    title_style = ParagraphStyle('ConditionTitle', parent=styles['h1'], fontSize=20, spaceAfter=10, textColor=colors.darkblue)
    story.append(Paragraph(condition_name, title_style))

    result_style = ParagraphStyle('Result', parent=styles['h2'], fontSize=14, spaceAfter=15)
    stars = get_evidence_stars("", "general")  # Would be condition-specific in real implementation
    story.append(Paragraph(f"Result: Increased Genetic Risk | Strength of Evidence: {stars}", result_style))

    # Genetics vs. Lifestyle Visual
    balance_title_style = ParagraphStyle('BalanceTitle', parent=styles['h3'], fontSize=12, spaceAfter=10, textColor=colors.darkgreen)
    story.append(Paragraph("Genetics vs. Lifestyle Impact", balance_title_style))

    # Sample balance - in real implementation, this would vary by condition
    genetics_pct = 30 if "Coronary" in condition_name else 20
    lifestyle_pct = 100 - genetics_pct

    buf = generate_genetics_lifestyle_balance(genetics_pct, lifestyle_pct, condition_name)
    story.append(Image(buf, width=5*inch, height=3*inch))

    story.append(Spacer(1, 0.3*inch))

    # The Biological Story
    bio_title_style = ParagraphStyle('BioTitle', parent=styles['h3'], fontSize=12, spaceAfter=10, textColor=colors.darkgreen)
    story.append(Paragraph("The Biological Story", bio_title_style))

    bio_style = ParagraphStyle('BioText', parent=styles['Normal'], fontSize=10, spaceAfter=15, leftIndent=20)
    if "Coronary" in condition_name:
        bio_text = "Your report shows variants near the CDKN2B-AS1 gene on chromosome 9. This gene region is involved in regulating cell growth within your arteries. Your specific variants are linked to a higher rate of plaque buildup, which is a key factor in heart disease."
    elif "Diabetes" in condition_name:
        bio_text = "Multiple genes influence your insulin production and glucose metabolism. Variants in genes like TCF7L2 affect how your body responds to insulin, while lifestyle factors like diet and exercise play a crucial role in managing blood sugar levels."
    elif "Alzheimer" in condition_name:
        bio_text = "Your genetic profile shows variations in genes associated with Alzheimer's Disease. These genetic factors interact with environmental influences to determine your overall risk level."
    elif "Breast" in condition_name:
        bio_text = "Your genetic profile shows variations in genes associated with Breast Cancer. These genetic factors interact with environmental influences to determine your overall risk level."
    else:
        bio_text = f"Your genetic profile shows variations in genes associated with {condition_name}. These genetic factors interact with environmental influences to determine your overall risk level."

    story.append(Paragraph(bio_text, bio_style))

    # The PRS Gauge
    prs_title_style = ParagraphStyle('PRSTitle', parent=styles['h3'], fontSize=12, spaceAfter=10, textColor=colors.darkgreen)
    story.append(Paragraph("The PRS Gauge", prs_title_style))

    buf = generate_prs_gauge(prs_percentile, condition_name)
    story.append(Image(buf, width=4*inch, height=3*inch))

    # Contextualized Next Steps
    steps_title_style = ParagraphStyle('StepsTitle', parent=styles['h3'], fontSize=12, spaceAfter=10, textColor=colors.darkgreen)
    story.append(Paragraph("Contextualized Next Steps", steps_title_style))

    steps_style = ParagraphStyle('StepsText', parent=styles['Normal'], fontSize=10, spaceAfter=8, leftIndent=20)

    if "Coronary" in condition_name:
        steps = [
            "Discuss cholesterol management (like checking LDL levels) and blood pressure with your doctor",
            "Consider regular cardiovascular screenings starting at age 40",
            "Focus on heart-healthy lifestyle: Mediterranean diet, regular exercise, no smoking",
            "Monitor family history of heart disease"
        ]
    elif "Diabetes" in condition_name:
        steps = [
            "Schedule regular HbA1c testing to monitor blood sugar levels",
            "Focus on maintaining healthy weight and regular physical activity",
            "Learn about carbohydrate counting and blood sugar management",
            "Discuss with your doctor about appropriate screening intervals"
        ]
    else:
        steps = [
            "Consult with a healthcare provider familiar with genetic risk factors",
            "Follow general preventive health guidelines for your age group",
            "Stay informed about advances in personalized medicine",
            "Consider discussing results with family members who may be at similar risk"
        ]

    for step in steps:
        story.append(Paragraph(f"• {step}", steps_style))

    story.append(PageBreak())

def add_medication_guide_section(story, dna_data):
    """Add the Personalized Medication Guide section with funnel graphics."""
    styles = getSampleStyleSheet()

    # Section title
    title_style = ParagraphStyle('SectionTitle', parent=styles['h1'], fontSize=22, alignment=0, spaceAfter=20, textColor=colors.darkblue)
    story.append(Paragraph("Your Personalized Medication Guide", title_style))

    story.append(Spacer(1, 0.3*inch))

    # Introduction
    intro_style = ParagraphStyle('Intro', parent=styles['Normal'], fontSize=11, spaceAfter=20, leftIndent=20)
    story.append(Paragraph("This section explains how your genetics may affect your response to common medications. The funnel graphics below illustrate your drug metabolism process.", intro_style))

    story.append(Spacer(1, 0.5*inch))

    # Sample medications - in real implementation, this would be based on actual PGx results
    medications = [
        {
            'drug': 'Codeine',
            'gene': 'CYP2D6',
            'status': 'Ultra-Rapid',
            'stars': get_evidence_stars('', 'pgx'),
            'biological_story': "Codeine itself is inactive. Your body uses the CYP2D6 enzyme to convert it into morphine for pain relief. Because you are an Ultra-Rapid Metabolizer, your body does this conversion too fast, which can lead to dangerously high levels of morphine from a standard dose.",
            'next_steps': [
                "Avoid codeine and related opioids (hydrocodone, oxycodone)",
                "Discuss alternative pain medications with your doctor",
                "Inform all healthcare providers about this result before any prescription",
                "Consider non-opioid alternatives like acetaminophen or NSAIDs"
            ]
        },
        {
            'drug': 'Clopidogrel (Plavix)',
            'gene': 'CYP2C19',
            'status': 'Poor',
            'stars': get_evidence_stars('', 'pgx'),
            'biological_story': "Clopidogrel is a pro-drug that requires activation by the CYP2C19 enzyme to be effective. As a poor metabolizer, you convert very little clopidogrel to its active form, reducing its effectiveness in preventing blood clots.",
            'next_steps': [
                "Discuss alternative antiplatelet medications with your cardiologist",
                "Consider alternatives like ticagrelor (Brilinta) or prasugrel (Effient)",
                "Regular monitoring of platelet function may be needed",
                "Inform your doctor before starting clopidogrel therapy"
            ]
        }
    ]

    for med in medications:
        # Medication title and result
        med_title_style = ParagraphStyle('MedTitle', parent=styles['h2'], fontSize=16, spaceAfter=10, textColor=colors.darkred)
        story.append(Paragraph(f"Medication: {med['drug']}", med_title_style))

        result_style = ParagraphStyle('MedResult', parent=styles['h3'], fontSize=12, spaceAfter=15)
        story.append(Paragraph(f"Gene: {med['gene']} | Result: {med['status']} Metabolizer | Strength of Evidence: {med['stars']}", result_style))

        # Metabolism funnel visual
        funnel_title_style = ParagraphStyle('FunnelTitle', parent=styles['h4'], fontSize=11, spaceAfter=10, textColor=colors.darkgreen)
        story.append(Paragraph("Your Metabolism Explained", funnel_title_style))

        buf = generate_metabolism_funnel(med['drug'], med['status'], med['gene'])
        story.append(Image(buf, width=4*inch, height=3*inch))

        story.append(Spacer(1, 0.3*inch))

        # Biological story
        bio_title_style = ParagraphStyle('BioTitle', parent=styles['h4'], fontSize=11, spaceAfter=10, textColor=colors.darkgreen)
        story.append(Paragraph("The Biological Story", bio_title_style))

        bio_style = ParagraphStyle('BioText', parent=styles['Normal'], fontSize=10, spaceAfter=15, leftIndent=20)
        story.append(Paragraph(med['biological_story'], bio_style))

        # Urgent next steps
        steps_title_style = ParagraphStyle('StepsTitle', parent=styles['h4'], fontSize=11, spaceAfter=10, textColor=colors.darkred)
        story.append(Paragraph("Urgent Next Steps", steps_title_style))

        steps_style = ParagraphStyle('StepsText', parent=styles['Normal'], fontSize=10, spaceAfter=8, leftIndent=20)
        for step in med['next_steps']:
            story.append(Paragraph(f"• {step}", steps_style))

        story.append(PageBreak())

def add_executive_summary(story, key_findings, health_score):
    """Add executive summary."""
    styles = getSampleStyleSheet()
    story.append(Paragraph("Executive Summary", styles['h1']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"Overall Health Score: {health_score}/100", styles['h2']))
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph("Key Findings:", styles['h3']))
    for finding in key_findings:
        story.append(Paragraph(f"• {finding}", styles['Normal']))
    story.append(PageBreak())

# Placeholder functions for remaining sections - these would be implemented similarly
def add_comprehensive_carrier_status(story, dna_data):
    """Add comprehensive carrier status for genetic conditions."""
    styles = getSampleStyleSheet()
    story.append(Paragraph("Comprehensive Carrier Status", styles['h1']))
    story.append(Spacer(1, 0.5*inch))

    # Import SNP data
    try:
        from ..snp_data import recessive_snps, ancestry_panels
    except ImportError:
        from snp_data import recessive_snps, ancestry_panels

    # Combine all carrier conditions
    all_carrier_conditions = dict(recessive_snps)

    # Add ancestry-specific conditions
    for ancestry, conditions in ancestry_panels.items():
        for rsid, info in conditions.items():
            if rsid not in all_carrier_conditions:
                all_carrier_conditions[rsid] = {
                    'gene': info['gene'],
                    'condition': f"{info['condition']} ({ancestry})",
                    'risk_allele': 'T',  # Default, would need specific allele info
                    'interp': {'CT': 'Carrier', 'TT': 'Affected'}
                }

    results = []
    carrier_count = 0
    affected_count = 0

    for rsid, info in all_carrier_conditions.items():
        user_genotype = dna_data[dna_data.index == rsid]
        status = 'Not a carrier'
        genotype = 'Not in data'
        if not user_genotype.empty:
            genotype = user_genotype.iloc[0]['genotype']
            sorted_genotype = "".join(sorted(genotype))
            if sorted_genotype in info['interp']:
                status = info['interp'][sorted_genotype]
                if status == 'Carrier':
                    carrier_count += 1
                elif status == 'Affected':
                    affected_count += 1

        results.append({
            'rsID': rsid,
            'Gene': info['gene'],
            'Condition': info['condition'],
            'Genotype': genotype,
            'Status': status
        })

    # Summary statistics
    total_analyzed = len(results)
    story.append(Paragraph(f"Analysis Summary: {total_analyzed} conditions analyzed", styles['h3']))
    story.append(Paragraph(f"Carrier Status: {carrier_count} conditions", styles['Normal']))
    if affected_count > 0:
        story.append(Paragraph(f"Affected Status: {affected_count} conditions", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    if results:
        # Filter to show only carriers and affected for brevity
        significant_results = [r for r in results if r['Status'] in ['Carrier', 'Affected']]

        if significant_results:
            story.append(Paragraph("Significant Findings:", styles['h3']))
            data = [['rsID', 'Gene', 'Condition', 'Genotype', 'Status']]
            data.extend([[r['rsID'], r['Gene'], r['Condition'], r['Genotype'], r['Status']] for r in significant_results])

            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black)
            ]))
            story.append(table)
        else:
            story.append(Paragraph("No carrier or affected status detected for analyzed conditions.", styles['Normal']))

    story.append(PageBreak())

def add_pharmacogenomics_profile(story, dna_data):
    """Add pharmacogenomics profile for 20+ drugs."""
    styles = getSampleStyleSheet()
    story.append(Paragraph("Pharmacogenomics Profile", styles['h1']))
    story.append(Spacer(1, 0.5*inch))

    # Import PGx data
    from ..snp_data import pgx_snps

    results = []
    analyzed_count = 0

    for rsid, info in pgx_snps.items():
        user_genotype = dna_data[dna_data.index == rsid]
        interpretation = 'Not in data'
        genotype = 'Not in data'
        if not user_genotype.empty:
            genotype = user_genotype.iloc[0]['genotype']
            sorted_genotype = "".join(sorted(genotype))
            if sorted_genotype in info['interp']:
                interpretation = info['interp'][sorted_genotype]
                analyzed_count += 1

        results.append({
            'rsID': rsid,
            'Gene': info['gene'],
            'Drug': info['relevance'],
            'Genotype': genotype,
            'Metabolism': interpretation
        })

    if results:
        story.append(Paragraph(f"Analysis Summary: {analyzed_count}/{len(results)} PGx variants analyzed", styles['h3']))
        story.append(Spacer(1, 0.3*inch))

        # Filter to show only analyzed variants
        analyzed_results = [r for r in results if r['Genotype'] != 'Not in data']

        if analyzed_results:
            data = [['rsID', 'Gene', 'Drug/Relevance', 'Genotype', 'Metabolism']]
            data.extend([[r['rsID'], r['Gene'], r['Drug'], r['Genotype'], r['Metabolism']] for r in analyzed_results])

            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 8)  # Smaller font for table
            ]))
            story.append(table)
        else:
            story.append(Paragraph("No pharmacogenomic variants detected in analyzed data.", styles['Normal']))
    else:
        story.append(Paragraph("No pharmacogenomic data available.", styles['Normal']))

    story.append(PageBreak())

def add_disease_risk_assessment(story, dna_data):
    """Add disease risk assessment for genetic conditions."""
    styles = getSampleStyleSheet()
    story.append(Paragraph("Disease Risk Assessment", styles['h1']))
    story.append(Spacer(1, 0.5*inch))

    # Import SNP data
    try:
        from ..snp_data import cancer_snps, cardiovascular_snps, neuro_snps, mito_snps
    except ImportError:
        from snp_data import cancer_snps, cardiovascular_snps, neuro_snps, mito_snps

    # Combine all risk conditions
    all_risk_conditions = {}
    all_risk_conditions.update(cancer_snps)
    all_risk_conditions.update(cardiovascular_snps)
    all_risk_conditions.update(neuro_snps)
    all_risk_conditions.update(mito_snps)

    results = []
    high_risk_count = 0

    for rsid, info in all_risk_conditions.items():
        user_genotype = dna_data[dna_data.index == rsid]
        risk_level = 'Not detected'
        genotype = 'Not in data'
        if not user_genotype.empty:
            genotype = user_genotype.iloc[0]['genotype']
            # Simplified risk assessment - in real implementation would be more sophisticated
            risk_level = info.get('risk', 'Variant detected')
            if 'High' in risk_level or 'Hereditary' in risk_level:
                high_risk_count += 1

        results.append({
            'rsID': rsid,
            'Gene': info['gene'],
            'Condition': info.get('condition', info.get('risk', 'Unknown')),
            'Genotype': genotype,
            'Risk': risk_level
        })

    # Summary statistics
    total_analyzed = len(results)
    story.append(Paragraph(f"Analysis Summary: {total_analyzed} genetic variants analyzed", styles['h3']))
    if high_risk_count > 0:
        story.append(Paragraph(f"High Risk Variants: {high_risk_count} detected", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    if results:
        # Filter to show only detected variants for brevity
        detected_results = [r for r in results if r['Genotype'] != 'Not in data']

        if detected_results:
            story.append(Paragraph("Detected Genetic Variants:", styles['h3']))
            data = [['rsID', 'Gene', 'Condition', 'Genotype', 'Risk Level']]
            data.extend([[r['rsID'], r['Gene'], r['Condition'], r['Genotype'], r['Risk']] for r in detected_results])

            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black)
            ]))
            story.append(table)
        else:
            story.append(Paragraph("No disease-associated variants detected in analyzed regions.", styles['Normal']))

    story.append(PageBreak())

def add_polygenic_risk_scores(story, dna_data):
    """Add polygenic risk scores with ancestry adjustments."""
    styles = getSampleStyleSheet()
    story.append(Paragraph("Polygenic Risk Scores", styles['h1']))
    story.append(Spacer(1, 0.5*inch))

    # Import SNP data
    try:
        from ..snp_data import prs_models, get_simple_model
    except ImportError:
        from snp_data import prs_models, get_simple_model

    analyzed_traits = []
    high_risk_count = 0

    for trait_name in ['Coronary Artery Disease', 'Type 2 Diabetes', 'Breast Cancer', 'Alzheimer\'s Disease']:
        model = get_simple_model(trait_name)
        if model:
            prs_model_df = pd.DataFrame(model).set_index('rsid')
            merged_df = dna_data.join(prs_model_df, how='inner')

            if not merged_df.empty:
                merged_df['allele_count'] = merged_df.apply(
                    lambda row: row['genotype'].upper().count(row['effect_allele']),
                    axis=1
                )
                merged_df['score_contribution'] = merged_df['allele_count'] * merged_df['effect_weight']
                user_prs = merged_df['score_contribution'].sum()

                # Simplified percentile calculation
                percentile = min(95, max(5, 50 + (user_prs * 10)))  # Rough estimate

                risk_level = "Average"
                if percentile > 75:
                    risk_level = "Elevated"
                    high_risk_count += 1
                elif percentile < 25:
                    risk_level = "Reduced"

                analyzed_traits.append({
                    'trait': trait_name,
                    'prs_score': user_prs,
                    'percentile': percentile,
                    'risk_level': risk_level
                })

    if analyzed_traits:
        story.append(Paragraph(f"Analysis Summary: {len(analyzed_traits)} traits analyzed", styles['h3']))
        if high_risk_count > 0:
            story.append(Paragraph(f"Elevated Risk Traits: {high_risk_count}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

        # Create table
        data = [['Trait', 'PRS Score', 'Percentile', 'Risk Level']]
        for trait in analyzed_traits:
            data.append([
                trait['trait'],
                f"{trait['prs_score']:.3f}",
                f"{trait['percentile']:.1f}th",
                trait['risk_level']
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black)
        ]))
        story.append(table)

        # Add PRS gauge for first trait
        if analyzed_traits:
            first_trait = analyzed_traits[0]
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph(f"PRS Distribution for {first_trait['trait']}:", styles['h3']))
            buf = generate_prs_gauge(int(first_trait['percentile']), first_trait['trait'])
            story.append(Image(buf, width=4*inch, height=3*inch))
    else:
        story.append(Paragraph("No PRS data available for analysis.", styles['Normal']))

    story.append(PageBreak())

def add_wellness_lifestyle_profile(story, dna_data):
    """Add wellness & lifestyle profile for 30+ traits."""
    styles = getSampleStyleSheet()
    story.append(Paragraph("Wellness & Lifestyle Profile", styles['h1']))
    story.append(Spacer(1, 0.5*inch))

    # Import and analyze wellness SNPs
    try:
        from ..utils import analyze_wellness_snps
    except ImportError:
        from utils import analyze_wellness_snps

    wellness_results = analyze_wellness_snps(dna_data)

    if wellness_results:
        # Count found SNPs
        found_snps = sum(1 for result in wellness_results.values() if result['genotype'] != 'Not Found')
        total_snps = len(wellness_results)

        story.append(Paragraph(f"Analysis Summary: {found_snps}/{total_snps} wellness SNPs analyzed", styles['h3']))
        story.append(Spacer(1, 0.3*inch))

        # Group results by category
        categories = {
            'Nutrition': [],
            'Fitness': [],
            'Longevity': [],
            'Sleep': [],
            'Other': []
        }

        for rsid, result in wellness_results.items():
            if result['genotype'] != 'Not Found':
                trait_name = result['name']
                if 'Vitamin' in trait_name or 'Lactose' in trait_name or 'Caffeine' in trait_name:
                    categories['Nutrition'].append((rsid, result))
                elif 'Athletic' in trait_name or 'Performance' in trait_name:
                    categories['Fitness'].append((rsid, result))
                elif 'Longevity' in trait_name or 'Telomere' in trait_name:
                    categories['Longevity'].append((rsid, result))
                elif 'Chronotype' in trait_name or 'Insomnia' in trait_name:
                    categories['Sleep'].append((rsid, result))
                else:
                    categories['Other'].append((rsid, result))

        # Display results by category
        for category, traits in categories.items():
            if traits:
                story.append(Paragraph(f"{category} Traits:", styles['h3']))

                data = [['SNP', 'Trait', 'Gene', 'Genotype', 'Interpretation']]
                for rsid, result in traits:
                    genotype = result['genotype']
                    interpretation = result['interp'].get(genotype, 'Unknown')
                    data.append([
                        rsid,
                        result['name'],
                        result['gene'],
                        genotype,
                        interpretation
                    ])

                table = Table(data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTSIZE', (0, 0), (-1, -1), 8)  # Smaller font for table
                ]))
                story.append(table)
                story.append(Spacer(1, 0.3*inch))

    else:
        story.append(Paragraph("No wellness SNP data available for analysis.", styles['Normal']))

    story.append(PageBreak())

def add_advanced_analytics_dashboard(story, dna_data):
    """Add advanced analytics dashboard with charts."""
    styles = getSampleStyleSheet()
    story.append(Paragraph("Advanced Analytics Dashboard", styles['h1']))
    story.append(Spacer(1, 0.5*inch))

    # Add some sample analytics visualizations
    story.append(Paragraph("Genetic Risk Distribution Analysis:", styles['h3']))

    # Generate sample risk distribution data
    import numpy as np
    risk_data = np.random.normal(0.5, 0.2, 100)
    buf = generate_risk_histogram(risk_data, 'Population Risk Distribution')
    story.append(Image(buf, width=5*inch, height=4*inch))

    story.append(Spacer(1, 0.5*inch))

    # Add carrier probability visualization if we have carrier data
    from ..snp_data import recessive_snps
    if recessive_snps:
        story.append(Paragraph("Carrier Probability Analysis:", styles['h3']))

        carrier_data = []
        for rsid, info in list(recessive_snps.items())[:5]:  # Limit to 5 for display
            carrier_data.append({
                'Condition': info['condition'],
                'Status': 'Carrier' if np.random.random() > 0.7 else 'Not a carrier'  # Sample data
            })

        if carrier_data:
            buf = generate_carrier_probability_bars(carrier_data)
            story.append(Image(buf, width=6*inch, height=4*inch))

    story.append(Spacer(1, 0.5*inch))

    # Add PRS percentile plot
    story.append(Paragraph("Polygenic Risk Score Analysis:", styles['h3']))
    buf = generate_prs_percentile_plot(65, 'Sample Trait')
    story.append(Image(buf, width=5*inch, height=3*inch))

    story.append(PageBreak())

def add_personalized_recommendations(story):
    """Add personalized recommendations."""
    styles = getSampleStyleSheet()
    story.append(Paragraph("Personalized Recommendations", styles['h1']))
    story.append(Spacer(1, 0.5*inch))
    recommendations = [
        "Consult with a genetic counselor for detailed interpretation.",
        "Maintain a healthy lifestyle to mitigate genetic risks.",
        "Regular medical screenings based on your genetic profile."
    ]
    for rec in recommendations:
        story.append(Paragraph(f"• {rec}", styles['Normal']))
    story.append(PageBreak())

def add_methodology_references(story):
    """Add methodology & references."""
    styles = getSampleStyleSheet()
    story.append(Paragraph("Methodology & References", styles['h1']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("This report is based on analysis of genetic variants from ClinVar, PharmGKB, and PGS Catalog.", styles['Normal']))
    story.append(Paragraph("References: [List of sources]", styles['Normal']))
    story.append(PageBreak())

def add_appendix_raw_data(story, dna_data):
    """Add appendix with raw data."""
    styles = getSampleStyleSheet()
    story.append(Paragraph("Appendix: Raw Data", styles['h1']))
    story.append(Spacer(1, 0.5*inch))

    if dna_data is not None and not dna_data.empty:
        story.append(Paragraph(f"Total SNPs in dataset: {len(dna_data)}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

        # Show first 20 SNPs as sample
        sample_data = dna_data.head(20).reset_index() if dna_data.index.name == 'rsid' else dna_data.head(20)

        if not sample_data.empty:
            # Prepare data for table
            columns = ['rsID'] + [col for col in sample_data.columns if col != 'index']
            data = [columns]

            for _, row in sample_data.iterrows():
                row_data = [row.get('rsid', row.get('rsID', 'N/A'))]
                for col in columns[1:]:
                    if col in row:
                        row_data.append(str(row[col]))
                    else:
                        row_data.append('N/A')
                data.append(row_data)

            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 7)  # Small font for raw data
            ]))
            story.append(table)

            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("Note: This is a sample of the first 20 SNPs. Full dataset contains all analyzed variants.", styles['Italic']))
        else:
            story.append(Paragraph("No raw data available to display.", styles['Normal']))
    else:
        story.append(Paragraph("No genetic data available.", styles['Normal']))

    story.append(PageBreak())