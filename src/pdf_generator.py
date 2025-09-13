import pandas as pd
import numpy as np
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import os
from math import pi, cos, sin

from utils import analyze_wellness_snps
from snp_data import pgx_snps, prs_models, guidance_data

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
        "cancer": 5,     # Well-established cancer genes
        "cardiovascular": 4,  # Strong evidence for heart disease genes
        "pgx": 4,        # Pharmacogenomics well-studied
        "prs": 4,        # Polygenic risk scores from large GWAS
        "wellness": 3,   # Lifestyle traits, moderate evidence
        "neuro": 3,      # Neurological conditions
        "mito": 4,       # Mitochondrial disorders well-characterized
        "protective": 3, # Protective alleles, emerging data
        "ancestry": 4,   # Ancestry panels well-validated
        "default": 3     # Default moderate evidence
    }

    stars = "★" * evidence_levels.get(condition_type, 3)
    empty_stars = "☆" * (5 - len(stars))
    return stars + empty_stars

def generate_constellation_map(risk_data, title="Health Predisposition Map"):
    """
    Generate a constellation map visualization showing health categories as hubs
    with connected stars representing specific conditions.
    Size of star = magnitude of genetic risk
    Brightness of star = Strength of Evidence
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_facecolor('black')
    fig.patch.set_facecolor('black')

    # Define category hubs (central points)
    categories = {
        'Cardiovascular': (0, 0),
        'Metabolic': (3, 2),
        'Cancer': (-2, 3),
        'Neurological': (-3, -1),
        'Autoimmune': (2, -2),
        'Pharmacogenomics': (1, 3)
    }

    # Colors for different brightness levels (evidence strength)
    brightness_colors = {
        5: '#FFD700',  # Gold for ★★★★★
        4: '#FFA500',  # Orange for ★★★★☆
        3: '#FFFF00',  # Yellow for ★★★☆☆
        2: '#808080',  # Gray for ★★☆☆☆
        1: '#404040'   # Dark gray for ★☆☆☆☆
    }

    # Plot category hubs
    for cat, (x, y) in categories.items():
        ax.scatter(x, y, s=200, c='white', edgecolors='lightblue', linewidth=2, alpha=0.8)
        ax.text(x, y+0.3, cat, ha='center', va='bottom', color='white', fontsize=10, fontweight='bold')

    # Sample risk data - in real implementation, this would come from analysis
    sample_risks = {
        'Coronary Artery Disease': {'category': 'Cardiovascular', 'risk_level': 0.8, 'evidence': 4},
        'Type 2 Diabetes': {'category': 'Metabolic', 'risk_level': 0.6, 'evidence': 5},
        'Breast Cancer': {'category': 'Cancer', 'risk_level': 0.4, 'evidence': 5},
        'Alzheimer\'s': {'category': 'Neurological', 'risk_level': 0.3, 'evidence': 3},
        'Rheumatoid Arthritis': {'category': 'Autoimmune', 'risk_level': 0.5, 'evidence': 4},
        'Warfarin Response': {'category': 'Pharmacogenomics', 'risk_level': 0.7, 'evidence': 4}
    }

    # Plot condition stars
    for condition, data in sample_risks.items():
        hub_x, hub_y = categories[data['category']]
        # Position star slightly offset from hub
        angle = np.random.uniform(0, 2*np.pi)
        distance = np.random.uniform(1.5, 2.5)
        star_x = hub_x + distance * cos(angle)
        star_y = hub_y + distance * sin(angle)

        # Star size based on risk level
        size = 50 + (data['risk_level'] * 150)

        # Star color based on evidence strength
        color = brightness_colors[data['evidence']]

        # Draw connecting line
        ax.plot([hub_x, star_x], [hub_y, star_y], color='white', alpha=0.3, linewidth=1)

        # Draw star
        ax.scatter(star_x, star_y, s=size, c=color, marker='*', alpha=0.9, edgecolors='white', linewidth=0.5)

        # Add condition label
        ax.text(star_x, star_y+0.2, condition, ha='center', va='bottom', color='white', fontsize=8, rotation=0)

    ax.set_xlim(-5, 5)
    ax.set_ylim(-4, 5)
    ax.axis('off')
    ax.set_title(title, color='white', fontsize=14, fontweight='bold', pad=20)

    # Add legend
    legend_elements = [
        plt.Line2D([0], [0], marker='*', color='w', markerfacecolor='#FFD700', markersize=15, label='★★★★★ Very Strong'),
        plt.Line2D([0], [0], marker='*', color='w', markerfacecolor='#FFA500', markersize=12, label='★★★★☆ Strong'),
        plt.Line2D([0], [0], marker='*', color='w', markerfacecolor='#FFFF00', markersize=10, label='★★★☆☆ Moderate'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='white', markersize=8, label='Category Hub')
    ]
    ax.legend(handles=legend_elements, loc='upper right', facecolor='black', edgecolor='white', labelcolor='white')

    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=150, facecolor='black', edgecolor='black')
    buf.seek(0)
    plt.close(fig)
    return buf

def generate_genetics_lifestyle_balance(genetics_percent, lifestyle_percent, condition_name):
    """
    Generate a balanced scale visualization showing genetics vs. lifestyle impact.
    Returns a matplotlib figure showing the relative contributions.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))

    # Left plot: Pie chart
    labels = ['Genetics', 'Lifestyle']
    sizes = [genetics_percent, lifestyle_percent]
    colors_pie = ['#FF6B6B', '#4ECDC4']
    ax1.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%', startangle=90)
    ax1.set_title(f'{condition_name}\nGenetics vs. Lifestyle Impact', fontsize=12, fontweight='bold')
    ax1.axis('equal')

    # Right plot: Bar chart comparison
    bars = ax2.bar(['Genetics', 'Lifestyle'], [genetics_percent, lifestyle_percent],
                   color=colors_pie, alpha=0.7, width=0.6)
    ax2.set_ylabel('Impact Percentage (%)')
    ax2.set_title('Relative Contribution')
    ax2.set_ylim(0, 100)

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf

def generate_prs_gauge(percentile, trait_name):
    """
    Generate a speedometer-style gauge showing PRS percentile.
    """
    fig, ax = plt.subplots(figsize=(6, 4), subplot_kw={'projection': 'polar'})

    # Create gauge background
    theta = np.linspace(np.pi, 0, 100)
    r = np.ones_like(theta)

    # Color zones
    colors = []
    for t in theta:
        angle_deg = np.degrees(t)
        if angle_deg >= 135:  # Low risk (green)
            colors.append('#4CAF50')
        elif angle_deg >= 90:  # Moderate risk (yellow)
            colors.append('#FFC107')
        else:  # High risk (red)
            colors.append('#F44336')

    ax.bar(theta, r, width=0.02, color=colors, alpha=0.3)

    # Calculate needle position (percentile to angle)
    # 0th percentile = 180 degrees (left), 100th percentile = 0 degrees (right)
    needle_angle = np.radians(180 - (percentile * 1.8))

    # Draw needle
    ax.arrow(needle_angle, 0, 0, 0.8, head_width=0.1, head_length=0.1,
             fc='black', ec='black', linewidth=2)

    # Add labels
    ax.text(np.radians(180), 1.2, '0th', ha='center', va='center', fontsize=10)
    ax.text(np.radians(90), 1.2, '50th', ha='center', va='center', fontsize=10)
    ax.text(np.radians(0), 1.2, '100th', ha='center', va='center', fontsize=10)

    ax.set_title(f'{trait_name}\nPolygenic Risk Score Percentile', fontsize=14, fontweight='bold', pad=20)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.grid(False)

    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf

def generate_risk_histogram(data, title):
    """Generate a histogram image for risk distribution."""
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(data, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
    ax.set_title(title)
    ax.set_xlabel('Risk Score')
    ax.set_ylabel('Frequency')
    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf

def generate_prs_percentile_plot(user_percentile, trait):
    """Generate a percentile plot for PRS."""
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh([0], [user_percentile], color='red', alpha=0.7, label='Your Percentile')
    ax.barh([0], [100 - user_percentile], left=user_percentile, color='lightgray', alpha=0.7, label='Population')
    ax.set_xlim(0, 100)
    ax.set_xlabel('Percentile')
    ax.set_title(f'PRS Percentile for {trait}')
    ax.legend()
    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf

def generate_carrier_probability_bars(carrier_data):
    """Generate bar chart for carrier probabilities."""
    fig, ax = plt.subplots(figsize=(8, 6))
    conditions = [d['Condition'] for d in carrier_data]
    probs = [0.5 if d['Status'] == 'Carrier' else 0 for d in carrier_data]  # Simplified
    ax.barh(conditions, probs, color='orange')
    ax.set_xlabel('Carrier Probability')
    ax.set_title('Carrier Status Probabilities')
    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf

def generate_heatmap_gene_disease(genes, diseases, scores):
    """Generate heatmap for gene-disease interactions."""
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(scores, annot=True, xticklabels=diseases, yticklabels=genes, cmap='coolwarm', ax=ax)
    ax.set_title('Gene-Disease Interaction Heatmap')
    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf

def generate_lifetime_risk_timeline(risks_over_time):
    """Generate timeline for lifetime risk projections."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ages = list(risks_over_time.keys())
    risks = list(risks_over_time.values())
    ax.plot(ages, risks, marker='o')
    ax.set_xlabel('Age')
    ax.set_ylabel('Risk Percentage')
    ax.set_title('Lifetime Risk Projection')
    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf

def generate_health_score_infographic(score, components):
    """Generate infographic for health score dashboard."""
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(components.values(), labels=components.keys(), autopct='%1.1f%%', startangle=90)
    ax.set_title(f'Health Score: {score}')
    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf

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
    else:
        bio_text = f"Your genetic profile shows variations in genes associated with {condition_name.lower()}. These genetic factors interact with environmental influences to determine your overall risk level."

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

def add_comprehensive_carrier_status(story, dna_data):
    """Add comprehensive carrier status for 100+ conditions."""
    styles = getSampleStyleSheet()
    story.append(Paragraph("Comprehensive Carrier Status", styles['h1']))
    story.append(Spacer(1, 0.5*inch))
    # Use existing recessive_snps and expand
    recessive_snps = {
        'rs113993960': {'gene': 'CFTR', 'condition': 'Cystic Fibrosis', 'risk_allele': 'T', 'interp': {'CT': 'Carrier', 'TT': 'Affected'}},
        'rs334': {'gene': 'HBB', 'condition': 'Sickle Cell Anemia', 'risk_allele': 'A', 'interp': {'GA': 'Carrier', 'AA': 'Affected'}},
        # Add more for 100+ conditions - simplified for now
    }
    results = []
    for rsid, info in recessive_snps.items():
        user_genotype = dna_data[dna_data.index == rsid]
        status = 'Not a carrier'
        genotype = 'Not in data'
        if not user_genotype.empty:
            genotype = user_genotype.iloc[0]['genotype']
            sorted_genotype = "".join(sorted(genotype))
            if sorted_genotype in info['interp']:
                status = info['interp'][sorted_genotype]
        results.append({'rsID': rsid, 'Gene': info['gene'], 'Condition': info['condition'], 'Genotype': genotype, 'Status': status})
    if results:
        df = pd.DataFrame(results)
        data = [df.columns.tolist()] + df.values.tolist()
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
    story.append(PageBreak())

def add_pharmacogenomics_profile(story, dna_data):
    """Add pharmacogenomics profile for 20+ drugs."""
    styles = getSampleStyleSheet()
    story.append(Paragraph("Pharmacogenomics Profile", styles['h1']))
    story.append(Spacer(1, 0.5*inch))
    pgx_snps = {
        'rs4244285': {'gene': 'CYP2C19', 'drug': 'Clopidogrel', 'interp': {'GG': 'Normal', 'AG': 'Intermediate', 'AA': 'Poor'}},
        'rs1057910': {'gene': 'CYP2C9*2', 'drug': 'Warfarin', 'interp': {'CC': 'Normal', 'CT': 'Intermediate', 'TT': 'Poor'}},
        # Add more for 20+ drugs
    }
    results = []
    for rsid, info in pgx_snps.items():
        user_genotype = dna_data[dna_data.index == rsid]
        interpretation = 'Not in data'
        genotype = 'Not in data'
        if not user_genotype.empty:
            genotype = user_genotype.iloc[0]['genotype']
            sorted_genotype = "".join(sorted(genotype))
            if sorted_genotype in info['interp']:
                interpretation = info['interp'][sorted_genotype]
        results.append({'rsID': rsid, 'Gene': info['gene'], 'Drug': info['drug'], 'Genotype': genotype, 'Metabolism': interpretation})
    if results:
        df = pd.DataFrame(results)
        data = [df.columns.tolist()] + df.values.tolist()
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
    story.append(PageBreak())

def add_disease_risk_assessment(story, dna_data):
    """Add disease risk assessment for 50+ conditions."""
    styles = getSampleStyleSheet()
    story.append(Paragraph("Disease Risk Assessment", styles['h1']))
    story.append(Spacer(1, 0.5*inch))
    # Use existing cancer_snps, cardiovascular_snps, etc., and expand
    risk_snps = {
        'rs80357906': {'gene': 'BRCA1', 'condition': 'Hereditary Breast Cancer', 'risk': 'High'},
        # Add more
    }
    results = []
    for rsid, info in risk_snps.items():
        user_genotype = dna_data[dna_data.index == rsid]
        status = 'No risk variant'
        genotype = 'Not in data'
        if not user_genotype.empty:
            genotype = user_genotype.iloc[0]['genotype']
            status = 'Risk variant detected'
        results.append({'rsID': rsid, 'Gene': info['gene'], 'Condition': info['condition'], 'Genotype': genotype, 'Risk': status})
    if results:
        df = pd.DataFrame(results)
        data = [df.columns.tolist()] + df.values.tolist()
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
    story.append(PageBreak())

def add_polygenic_risk_scores(story, dna_data):
    """Add polygenic risk scores with ancestry adjustments."""
    styles = getSampleStyleSheet()
    story.append(Paragraph("Polygenic Risk Scores", styles['h1']))
    story.append(Spacer(1, 0.5*inch))
    # Use existing PRS models
    prs_models = {
        "Coronary Artery Disease": {'rsid': ['rs10757274'], 'effect_allele': ['G'], 'effect_weight': [0.177]},
        # Simplified
    }
    for trait, model in prs_models.items():
        prs_model_df = pd.DataFrame(model).set_index('rsid')
        merged_df = dna_data.join(prs_model_df, how='inner')
        if not merged_df.empty:
            merged_df['allele_count'] = merged_df.apply(lambda row: row['genotype'].upper().count(row['effect_allele']), axis=1)
            merged_df['score_contribution'] = merged_df['allele_count'] * merged_df['effect_weight']
            user_prs = merged_df['score_contribution'].sum()
            # Simplified percentile
            percentile = 50  # Placeholder
            story.append(Paragraph(f"{trait}: PRS = {user_prs:.3f}, Percentile = {percentile}th", styles['Normal']))
            # Add plot
            buf = generate_prs_percentile_plot(percentile, trait)
            story.append(Image(buf, width=4*inch, height=3*inch))
    story.append(PageBreak())

def add_wellness_lifestyle_profile(story, dna_data):
    """Add wellness & lifestyle profile for 30+ traits."""
    styles = getSampleStyleSheet()
    story.append(Paragraph("Wellness & Lifestyle Profile", styles['h1']))
    story.append(Spacer(1, 0.5*inch))
    wellness_results = analyze_wellness_snps(dna_data)
    if wellness_results:
        df = pd.DataFrame({
            'rsID': list(wellness_results.keys()),
            'Trait': [v['name'] for v in wellness_results.values()],
            'Gene': [v['gene'] for v in wellness_results.values()],
            'Genotype': [v['genotype'] for v in wellness_results.values()]
        })
        data = [df.columns.tolist()] + df.values.tolist()
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
    story.append(PageBreak())

def add_advanced_analytics_dashboard(story, dna_data):
    """Add advanced analytics dashboard with charts."""
    styles = getSampleStyleSheet()
    story.append(Paragraph("Advanced Analytics Dashboard", styles['h1']))
    story.append(Spacer(1, 0.5*inch))
    # Add some charts
    # Risk histogram
    risk_data = np.random.normal(0.5, 0.2, 100)  # Placeholder
    buf = generate_risk_histogram(risk_data, 'Risk Distribution')
    story.append(Image(buf, width=5*inch, height=4*inch))
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
    # Sample raw data
    sample_data = dna_data.head(20)
    data = [sample_data.columns.tolist()] + sample_data.values.tolist()
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(PageBreak())

def generate_pdf_report(report_data, results_dir, dna_data):
    doc = SimpleDocTemplate(os.path.join(results_dir, "Genomic_Health_Report.pdf"), pagesize=letter)
    styles = getSampleStyleSheet()
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
    except Exception as e:
        print(f"Error generating PDF: {e}")
