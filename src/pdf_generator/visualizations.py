"""
Visualization functions for generating charts and graphics in the PDF report.
"""

from io import BytesIO
from math import cos, pi, sin

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def generate_constellation_map(risk_data, title="Health Predisposition Map"):
    """
    Generate a constellation map visualization showing health categories as hubs
    with connected stars representing specific conditions.
    Size of star = magnitude of genetic risk
    Brightness of star = Strength of Evidence
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_facecolor("black")
    fig.patch.set_facecolor("black")

    # Define category hubs (central points)
    categories = {
        "Cardiovascular": (0, 0),
        "Metabolic": (3, 2),
        "Cancer": (-2, 3),
        "Neurological": (-3, -1),
        "Autoimmune": (2, -2),
        "Pharmacogenomics": (1, 3),
    }

    # Colors for different brightness levels (evidence strength)
    brightness_colors = {
        5: "#FFD700",  # Gold for ★★★★★
        4: "#FFA500",  # Orange for ★★★★☆
        3: "#FFFF00",  # Yellow for ★★★☆☆
        2: "#808080",  # Gray for ★★☆☆☆
        1: "#404040",  # Dark gray for ★☆☆☆☆
    }

    # Plot category hubs
    for cat, (x, y) in categories.items():
        ax.scatter(
            x, y, s=200, c="white", edgecolors="lightblue", linewidth=2, alpha=0.8
        )
        ax.text(
            x,
            y + 0.3,
            cat,
            ha="center",
            va="bottom",
            color="white",
            fontsize=10,
            fontweight="bold",
        )

    # Sample risk data - in real implementation, this would come from analysis
    sample_risks = {
        "Coronary Artery Disease": {
            "category": "Cardiovascular",
            "risk_level": 0.8,
            "evidence": 4,
        },
        "Type 2 Diabetes": {"category": "Metabolic", "risk_level": 0.6, "evidence": 5},
        "Breast Cancer": {"category": "Cancer", "risk_level": 0.4, "evidence": 5},
        "Alzheimer's": {"category": "Neurological", "risk_level": 0.3, "evidence": 3},
        "Rheumatoid Arthritis": {
            "category": "Autoimmune",
            "risk_level": 0.5,
            "evidence": 4,
        },
        "Warfarin Response": {
            "category": "Pharmacogenomics",
            "risk_level": 0.7,
            "evidence": 4,
        },
    }

    # Plot condition stars
    for condition, data in sample_risks.items():
        hub_x, hub_y = categories[data["category"]]
        # Position star slightly offset from hub
        angle = np.random.uniform(0, 2 * np.pi)
        distance = np.random.uniform(1.5, 2.5)
        star_x = hub_x + distance * cos(angle)
        star_y = hub_y + distance * sin(angle)

        # Star size based on risk level
        size = 50 + (data["risk_level"] * 150)

        # Star color based on evidence strength
        color = brightness_colors[data["evidence"]]

        # Draw connecting line
        ax.plot([hub_x, star_x], [hub_y, star_y], color="white", alpha=0.3, linewidth=1)

        # Draw star
        ax.scatter(
            star_x,
            star_y,
            s=size,
            c=color,
            marker="*",
            alpha=0.9,
            edgecolors="white",
            linewidth=0.5,
        )

        # Add condition label
        ax.text(
            star_x,
            star_y + 0.2,
            condition,
            ha="center",
            va="bottom",
            color="white",
            fontsize=8,
            rotation=0,
        )

    ax.set_xlim(-5, 5)
    ax.set_ylim(-4, 5)
    ax.axis("off")
    ax.set_title(title, color="white", fontsize=14, fontweight="bold", pad=20)

    # Add legend
    legend_elements = [
        plt.Line2D(
            [0],
            [0],
            marker="*",
            color="w",
            markerfacecolor="#FFD700",
            markersize=15,
            label="★★★★★ Very Strong",
        ),
        plt.Line2D(
            [0],
            [0],
            marker="*",
            color="w",
            markerfacecolor="#FFA500",
            markersize=12,
            label="★★★★☆ Strong",
        ),
        plt.Line2D(
            [0],
            [0],
            marker="*",
            color="w",
            markerfacecolor="#FFFF00",
            markersize=10,
            label="★★★☆☆ Moderate",
        ),
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="white",
            markersize=8,
            label="Category Hub",
        ),
    ]
    ax.legend(
        handles=legend_elements,
        loc="upper right",
        facecolor="black",
        edgecolor="white",
        labelcolor="white",
    )

    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, facecolor="black", edgecolor="black")
    buf.seek(0)
    plt.close(fig)
    return buf


def generate_genetics_lifestyle_balance(
    genetics_percent, lifestyle_percent, condition_name
):
    """
    Generate a balanced scale visualization showing genetics vs. lifestyle impact.
    Returns a matplotlib figure showing the relative contributions.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))

    # Left plot: Pie chart
    labels = ["Genetics", "Lifestyle"]
    sizes = [genetics_percent, lifestyle_percent]
    colors_pie = ["#FF6B6B", "#4ECDC4"]
    ax1.pie(sizes, labels=labels, colors=colors_pie, autopct="%1.1f%%", startangle=90)
    ax1.set_title(
        f"{condition_name}\nGenetics vs. Lifestyle Impact",
        fontsize=12,
        fontweight="bold",
    )
    ax1.axis("equal")

    # Right plot: Bar chart comparison
    bars = ax2.bar(
        ["Genetics", "Lifestyle"],
        [genetics_percent, lifestyle_percent],
        color=colors_pie,
        alpha=0.7,
        width=0.6,
    )
    ax2.set_ylabel("Impact Percentage (%)")
    ax2.set_title("Relative Contribution")
    ax2.set_ylim(0, 100)

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 1,
            f"{height:.1f}%",
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf


def generate_metabolism_funnel(drug_name, metabolizer_status, gene_name):
    """
    Generate a funnel graphic showing drug metabolism process.
    Different widths represent different metabolizer statuses.
    """
    fig, ax = plt.subplots(figsize=(6, 4))

    # Define funnel characteristics based on metabolizer status
    status_configs = {
        "Ultra-Rapid": {
            "widths": [0.8, 0.9, 0.95],
            "color": "#FF6B6B",
            "description": "Too fast conversion",
        },
        "Rapid": {
            "widths": [0.6, 0.75, 0.85],
            "color": "#FFA500",
            "description": "Fast conversion",
        },
        "Normal": {
            "widths": [0.4, 0.55, 0.7],
            "color": "#4CAF50",
            "description": "Normal conversion",
        },
        "Intermediate": {
            "widths": [0.3, 0.4, 0.5],
            "color": "#FFC107",
            "description": "Slow conversion",
        },
        "Poor": {
            "widths": [0.2, 0.25, 0.3],
            "color": "#F44336",
            "description": "Very slow conversion",
        },
    }

    config = status_configs.get(metabolizer_status, status_configs["Normal"])

    # Draw funnel levels
    levels = ["Drug Intake", f"{gene_name} Processing", "Active Metabolite"]
    y_positions = [0, 1, 2]

    for i, (level, y) in enumerate(zip(levels, y_positions)):
        width = config["widths"][i]
        # Draw trapezoid for each level
        x_left = 0.5 - width / 2
        x_right = 0.5 + width / 2

        if i < len(levels) - 1:  # Not the last level
            next_width = config["widths"][i + 1]
            next_x_left = 0.5 - next_width / 2
            next_x_right = 0.5 + next_width / 2

            # Draw trapezoid
            ax.fill(
                [x_left, x_right, next_x_right, next_x_left],
                [y, y, y + 1, y + 1],
                color=config["color"],
                alpha=0.7,
            )
        else:
            # Draw rectangle for last level
            ax.fill(
                [x_left, x_right, x_right, x_left],
                [y, y, y + 0.8, y + 0.8],
                color=config["color"],
                alpha=0.7,
            )

        # Add level labels
        ax.text(
            0.5, y + 0.4, level, ha="center", va="center", fontsize=9, fontweight="bold"
        )

    # Add arrows showing flow
    for i in range(len(levels) - 1):
        ax.arrow(
            0.5,
            y_positions[i] + 0.8,
            0,
            0.2,
            head_width=0.05,
            head_length=0.05,
            fc="black",
            ec="black",
            alpha=0.7,
        )

    ax.set_xlim(0, 1)
    ax.set_ylim(-0.2, 2.8)
    ax.axis("off")

    # Add title and status
    ax.set_title(
        f'{drug_name} Metabolism\n{metabolizer_status} Metabolizer ({config["description"]})',
        fontsize=12,
        fontweight="bold",
        pad=20,
    )

    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf


def generate_prs_gauge(percentile, trait_name):
    """
    Generate a speedometer-style gauge showing PRS percentile.
    """
    fig, ax = plt.subplots(figsize=(6, 4), subplot_kw={"projection": "polar"})

    # Create gauge background
    theta = np.linspace(np.pi, 0, 100)
    r = np.ones_like(theta)

    # Color zones
    colors = []
    for t in theta:
        angle_deg = np.degrees(t)
        if angle_deg >= 135:  # Low risk (green)
            colors.append("#4CAF50")
        elif angle_deg >= 90:  # Moderate risk (yellow)
            colors.append("#FFC107")
        else:  # High risk (red)
            colors.append("#F44336")

    ax.bar(theta, r, width=0.02, color=colors, alpha=0.3)

    # Calculate needle position (percentile to angle)
    # 0th percentile = 180 degrees (left), 100th percentile = 0 degrees (right)
    needle_angle = np.radians(180 - (percentile * 1.8))

    # Draw needle
    ax.arrow(
        needle_angle,
        0,
        0,
        0.8,
        head_width=0.1,
        head_length=0.1,
        fc="black",
        ec="black",
        linewidth=2,
    )

    # Add labels
    ax.text(np.radians(180), 1.2, "0th", ha="center", va="center", fontsize=10)
    ax.text(np.radians(90), 1.2, "50th", ha="center", va="center", fontsize=10)
    ax.text(np.radians(0), 1.2, "100th", ha="center", va="center", fontsize=10)

    ax.set_title(
        f"{trait_name}\nPolygenic Risk Score Percentile",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.grid(False)

    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf


def generate_risk_histogram(data, title):
    """Generate a histogram image for risk distribution."""
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(data, bins=20, alpha=0.7, color="skyblue", edgecolor="black")
    ax.set_title(title)
    ax.set_xlabel("Risk Score")
    ax.set_ylabel("Frequency")
    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf


def generate_prs_percentile_plot(user_percentile, trait):
    """Generate a percentile plot for PRS."""
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh([0], [user_percentile], color="red", alpha=0.7, label="Your Percentile")
    ax.barh(
        [0],
        [100 - user_percentile],
        left=user_percentile,
        color="lightgray",
        alpha=0.7,
        label="Population",
    )
    ax.set_xlim(0, 100)
    ax.set_xlabel("Percentile")
    ax.set_title(f"PRS Percentile for {trait}")
    ax.legend()
    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf


def generate_carrier_probability_bars(carrier_data):
    """Generate bar chart for carrier probabilities."""
    fig, ax = plt.subplots(figsize=(8, 6))
    conditions = [d["Condition"] for d in carrier_data]
    probs = [0.5 if d["Status"] == "Carrier" else 0 for d in carrier_data]  # Simplified
    ax.barh(conditions, probs, color="orange")
    ax.set_xlabel("Carrier Probability")
    ax.set_title("Carrier Status Probabilities")
    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf


def generate_heatmap_gene_disease(genes, diseases, scores):
    """Generate heatmap for gene-disease interactions."""
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        scores,
        annot=True,
        xticklabels=diseases,
        yticklabels=genes,
        cmap="coolwarm",
        ax=ax,
    )
    ax.set_title("Gene-Disease Interaction Heatmap")
    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf


def generate_lifetime_risk_timeline(risks_over_time):
    """Generate timeline for lifetime risk projections."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ages = list(risks_over_time.keys())
    risks = list(risks_over_time.values())
    ax.plot(ages, risks, marker="o")
    ax.set_xlabel("Age")
    ax.set_ylabel("Risk Percentage")
    ax.set_title("Lifetime Risk Projection")
    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf


def generate_health_score_infographic(score, components):
    """Generate infographic for health score dashboard."""
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        components.values(), labels=components.keys(), autopct="%1.1f%%", startangle=90
    )
    ax.set_title(f"Health Score: {score}")
    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf
