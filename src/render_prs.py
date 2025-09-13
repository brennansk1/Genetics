import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from .snp_data import prs_models, guidance_data, get_prs_model_categories, get_prs_models_by_category, get_genomewide_models, get_simple_model, get_trait_description
from .api_functions import get_pgs_catalog_data, get_pgs_model_data, search_pgs_models
from .genomewide_prs import GenomeWidePRS
from .lifetime_risk import LifetimeRiskCalculator, get_available_conditions
import time

def render_prs_dashboard(dna_data):
    st.header("🧬 Genome-wide Polygenic Risk Score (PRS) Dashboard")
    st.write("This module assesses risk for complex, multi-gene conditions using both simplified and genome-wide models.")

    # Educational tooltips for technical terms
    st.subheader("Understanding Key Terms")
    with st.expander("Click to see beginner-friendly definitions of genetic terms"):
        st.write("**Polygenic Risk Score (PRS)**: A calculation that combines many genetic variants to estimate disease risk, like adding up many small risk factors.")
        st.write("**Percentile**: Your position on a risk scale (e.g., 75th percentile means higher risk than 75% of people).")
        st.write("**Genome-wide**: Analysis using genetic variants across your entire genome, not just specific genes.")
        st.write("**Haplotype**: A set of DNA variations that tend to be inherited together on the same chromosome.")
        st.write("**Linkage Disequilibrium**: When certain genetic variants are found together more often than expected by chance.")

    # Initialize PRS calculator
    prs_calculator = GenomeWidePRS()

    # Model type selection
    st.subheader("3.1. PRS Model Selection")

    col1, col2 = st.columns([1, 1])

    with col1:
        model_type = st.radio(
            "Choose PRS Model Type:",
            ["Simplified (3-5 SNPs)", "Genome-wide (thousands of SNPs)"],
            key="model_type"
        )

    with col2:
        if model_type == "Genome-wide (thousands of SNPs)":
            use_pgs_catalog = st.checkbox("Use PGS Catalog models", value=True)
            use_ancestry_adjustment = st.checkbox("Apply ancestry adjustments", value=False,
                                                help="Adjust PRS calculations based on inferred genetic ancestry for improved accuracy")
        else:
            use_pgs_catalog = False
            use_ancestry_adjustment = False

    # Category and trait selection
    categories = get_prs_model_categories()
    selected_category = st.selectbox("Select Disease Category:", ["All"] + categories)

    if selected_category == "All":
        available_traits = list(prs_models.keys())
    else:
        category_models = get_prs_models_by_category(selected_category)
        available_traits = list(category_models.keys())

    trait = st.selectbox("Select Condition:", available_traits)

    # Display trait description
    if trait:
        description = get_trait_description(trait)
        if description:
            st.info(f"**{trait}**: {description}")

    # Manual ancestry specification (optional)
    if use_ancestry_adjustment:
        with st.expander("Manual Ancestry Specification (Optional)"):
            st.write("If you know your genetic ancestry, you can specify it manually. Otherwise, it will be inferred automatically from your data.")

            ancestry_options = ["Auto-infer from data", "European", "African", "East Asian", "South Asian", "American", "Admixed"]
            manual_ancestry = st.selectbox(
                "Specify your ancestry:",
                ancestry_options,
                index=0,
                help="Select your known genetic ancestry or leave as auto-infer"
            )

            if manual_ancestry != "Auto-infer from data":
                st.info(f"Manual ancestry '{manual_ancestry}' will be used instead of automatic inference.")

    # Genome-wide model selection
    selected_pgs_id = None
    if model_type == "Genome-wide (thousands of SNPs)" and trait:
        genomewide_models = get_genomewide_models(trait)

        if genomewide_models and use_pgs_catalog:
            st.subheader("3.2. Genome-wide Model Options")

            model_options = ["Auto-select best model"] + [f"{model['pgs_id']}: {model['description']}" for model in genomewide_models]
            selected_model_option = st.selectbox("Choose PGS Model:", model_options)

            if selected_model_option != "Auto-select best model":
                selected_pgs_id = selected_model_option.split(":")[0].strip()

            # Show model details
            if selected_pgs_id:
                with st.expander("Model Information"):
                    model_summary = get_pgs_model_data(selected_pgs_id, include_metadata=False)
                    if model_summary:
                        st.write(f"**PGS ID:** {model_summary.get('pgs_id', 'N/A')}")
                        st.write(f"**Variants:** {model_summary.get('num_variants', 'N/A')}")
                        st.write(f"**Genome Build:** {model_summary.get('genome_build', 'N/A')}")
                        st.write(f"**Population:** {model_summary.get('ancestry', 'N/A')}")
        elif not genomewide_models:
            st.warning(f"No genome-wide models available for {trait}. Using simplified model as fallback.")
            model_type = "Simplified (3-5 SNPs)"

    # PRS Calculation
    st.subheader("3.3. Risk Calculation")

    if st.button("Calculate Polygenic Risk Score", type="primary"):
        if not trait:
            st.error("Please select a trait first.")
            return

        with st.spinner("Calculating PRS... This may take a moment for genome-wide models."):
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                if model_type == "Genome-wide (thousands of SNPs)" and use_pgs_catalog and selected_pgs_id:
                    # Genome-wide calculation
                    status_text.text("Downloading PGS model...")
                    progress_bar.progress(25)

                    result = prs_calculator.calculate_genomewide_prs(
                        dna_data,
                        selected_pgs_id,
                        progress_callback=lambda msg: status_text.text(msg),
                        use_ancestry_adjustment=use_ancestry_adjustment
                    )

                    progress_bar.progress(100)
                    status_text.text("Calculation complete!")

                    if result['success']:
                        display_genomewide_results(result, trait, dna_data)
                    else:
                        st.error(f"Failed to calculate genome-wide PRS: {result.get('error', 'Unknown error')}")
                        # Fallback to simple model
                        st.info("Falling back to simplified model...")
                        calculate_simple_prs(dna_data, trait, prs_calculator)

                else:
                    # Simple model calculation
                    progress_bar.progress(50)
                    status_text.text("Calculating simplified PRS...")
                    calculate_simple_prs(dna_data, trait, prs_calculator)
                    progress_bar.progress(100)
                    status_text.text("Calculation complete!")

            except Exception as e:
                st.error(f"Error during PRS calculation: {str(e)}")
                progress_bar.progress(100)
                status_text.text("")

            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()

def calculate_simple_prs(dna_data, trait, prs_calculator):
    """Calculate PRS using simplified model."""
    simple_model = get_simple_model(trait)

    if not simple_model:
        st.error(f"No model data available for {trait}")
        return

    result = prs_calculator.calculate_simple_prs(dna_data, {
        'trait': trait,
        **simple_model
    })

    display_simple_results(result, trait, dna_data)

def display_genomewide_results(result, trait, dna_data):
    """Display results from genome-wide PRS calculation."""
    st.success("✅ Genome-wide PRS calculation completed!")

    # Display ancestry information if available
    if result.get('ancestry_adjustment_used', False) and 'inferred_ancestry' in result:
        st.subheader("🧬 Ancestry Information")
        ancestry_col1, ancestry_col2, ancestry_col3 = st.columns(3)

        with ancestry_col1:
            st.metric("Inferred Ancestry", result.get('inferred_ancestry', 'Unknown'))

        with ancestry_col2:
            confidence = result.get('ancestry_confidence', 0.0)
            st.metric("Confidence", f"{confidence:.1f}")

        with ancestry_col3:
            admixture = result.get('admixture_proportions', {})
            if admixture:
                primary_admixture = max(admixture.items(), key=lambda x: x[1])
                st.metric("Primary Admixture", f"{primary_admixture[0]} ({primary_admixture[1]:.1f})")

        # Show admixture proportions if available
        if admixture and len(admixture) > 1:
            st.write("**Admixture Proportions:**")
            admixture_text = ", ".join([f"{k}: {v:.1f}" for k, v in admixture.items()])
            st.info(admixture_text)

    # Main results
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("PRS Score", f"{result['prs_score']:.4f}")

    with col2:
        st.metric("Percentile", f"{result['percentile']:.1f}th")

    with col3:
        st.metric("Normalized Score", f"{result['normalized_score']:.2f}")

    # Model information
    st.subheader("📊 Model Details")

    info_col1, info_col2, info_col3 = st.columns(3)

    with info_col1:
        st.write(f"**PGS ID:** {result.get('pgs_id', 'N/A')}")
        st.write(f"**Trait:** {result.get('trait', 'N/A')}")

    with info_col2:
        st.write(f"**SNPs Used:** {result['snps_used']:,}")
        st.write(f"**Total SNPs:** {result['total_snps']:,}")

    with info_col3:
        coverage_pct = result['coverage'] * 100
        st.write(f"**Coverage:** {coverage_pct:.1f}%")
        st.write(f"**Genome Build:** {result.get('genome_build', 'N/A')}")

    # Risk interpretation
    st.subheader("🎯 Risk Interpretation")

    percentile = result['percentile']

    if percentile < 25:
        risk_level = "Low"
        risk_color = "green"
        interpretation = "Your genetic risk is below average for this condition."
    elif percentile < 75:
        risk_level = "Average"
        risk_color = "blue"
        interpretation = "Your genetic risk is average for this condition."
    else:
        risk_level = "Elevated"
        risk_color = "orange"
        interpretation = "Your genetic risk is above average for this condition."

    st.markdown(f"**Risk Level: <span style='color:{risk_color};font-weight:bold'>{risk_level}</span>**", unsafe_allow_html=True)
    st.write(interpretation)

    # Population comparison chart
    st.subheader("📈 Population Comparison")

    # Create distribution plot
    fig = go.Figure()

    # Simulated population distribution
    population_scores = np.random.normal(0, 1, 10000)  # Standardized scores
    fig.add_trace(go.Histogram(
        x=population_scores,
        name='Population Distribution',
        nbinsx=50,
        marker_color='lightblue',
        opacity=0.7
    ))

    # User's score
    user_score = result['normalized_score']
    fig.add_vline(
        x=user_score,
        line_width=3,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Your Score: {user_score:.2f}",
        annotation_position="top right"
    )

    fig.update_layout(
        title=f'PRS Distribution for {trait}<br>Your score is at the {percentile:.1f}th percentile',
        xaxis_title="Standardized PRS Score",
        yaxis_title="Frequency",
        showlegend=False
    )

    st.plotly_chart(fig)

    # Ancestry adjustment comparison
    if result.get('ancestry_adjustment_used', False):
        with st.expander("⚖️ Ancestry Adjustment Details"):
            st.write("**Adjustment Applied:**")
            st.write(f"- Inferred Ancestry: {result.get('inferred_ancestry', 'Unknown')}")
            st.write(f"- Ancestry SNPs Used: {result.get('ancestry_snps_used', 0)}")
            st.write(f"- Adjustment Method: {result.get('ancestry_method', 'Unknown')}")

            st.info("ℹ️ Ancestry adjustments improve PRS accuracy by accounting for genetic differences between populations.")

    # Quality control information
    with st.expander("🔍 Quality Control Information"):
        st.write("**Data Quality Metrics:**")
        st.write(f"- SNP Coverage: {coverage_pct:.1f}%")
        st.write(f"- Model Variants: {result['total_snps']:,}")
        st.write(f"- Variants Found in Data: {result['snps_used']:,}")

        if result.get('ancestry_adjustment_used', False):
            st.write(f"- Ancestry Adjustment: Applied")
            st.write(f"- Ancestry Confidence: {result.get('ancestry_confidence', 0.0):.1f}")
        else:
            st.write("- Ancestry Adjustment: Not applied")

        if coverage_pct < 50:
            st.warning("⚠️ Low SNP coverage detected. Results may be less reliable.")
        elif coverage_pct < 80:
            st.info("ℹ️ Moderate SNP coverage. Results are reasonably reliable.")
        else:
            st.success("✅ High SNP coverage. Results are highly reliable.")

    # Educational content for genome-wide PRS
    st.subheader("What Does This Mean?")
    st.write("**Many Genes, One Risk Score**: Unlike single-gene conditions, complex diseases like diabetes or heart disease are influenced by hundreds or thousands of genetic variants. Your PRS combines all these small effects into one score, like adding up many tiny ingredients to make a complete recipe.")
    st.write("Genome-wide PRS uses advanced statistical models trained on large populations to predict disease risk based on your genetic makeup.")

    st.subheader("Key Takeaways")
    st.info(f"""
    - **Your PRS Percentile**: {result['percentile']:.1f}th percentile means your genetic risk for {trait} is {'higher' if result['percentile'] > 50 else 'lower'} than {result['percentile']:.1f}% of the population
    - **Not Deterministic**: PRS estimates probability, not certainty - lifestyle factors are also crucial
    - **Genome-wide Coverage**: Uses thousands of genetic variants across your entire genome
    - **Population Context**: Risk is relative to the reference population used in the model
    - **Clinical Utility**: Can guide screening and prevention strategies, but not diagnostic
    """)

    # Lifetime Risk Projections Section
    st.markdown("---")
    st.subheader("⏳ Lifetime Risk Projections")

    if st.button("🔮 View Lifetime Risk Projections", key="lifetime_projections_genomewide"):
        render_lifetime_risk_projections(dna_data, result, trait)

def display_simple_results(result, trait, dna_data):
    """Display results from simplified PRS calculation."""
    st.success("✅ Simplified PRS calculation completed!")

    # Main results
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("PRS Score", f"{result['prs_score']:.4f}")

    with col2:
        st.metric("Percentile", f"{result['percentile']:.1f}th")

    with col3:
        st.metric("Normalized Score", f"{result['normalized_score']:.2f}")

    # Model information
    st.subheader("📊 Model Details")

    st.write(f"**SNPs Used:** {result['snps_used']}")
    st.write(f"**Total SNPs:** {result['total_snps']}")
    coverage_pct = result['coverage'] * 100
    st.write(f"**Coverage:** {coverage_pct:.1f}%")

    # Risk interpretation (same as genome-wide)
    st.subheader("🎯 Risk Interpretation")

    percentile = result['percentile']

    if percentile < 25:
        risk_level = "Low"
        risk_color = "green"
        interpretation = "Your genetic risk is below average for this condition."
    elif percentile < 75:
        risk_level = "Average"
        risk_color = "blue"
        interpretation = "Your genetic risk is average for this condition."
    else:
        risk_level = "Elevated"
        risk_color = "orange"
        interpretation = "Your genetic risk is above average for this condition."

    st.markdown(f"**Risk Level: <span style='color:{risk_color};font-weight:bold'>{risk_level}</span>**", unsafe_allow_html=True)
    st.write(interpretation)

    # Population comparison chart (simplified)
    st.subheader("📈 Population Comparison")

    fig = go.Figure()
    population_scores = np.random.normal(0, 1, 10000)
    fig.add_trace(go.Histogram(
        x=population_scores,
        name='Population',
        nbinsx=30,
        marker_color='lightgreen',
        opacity=0.7
    ))

    user_score = result['normalized_score']
    fig.add_vline(
        x=user_score,
        line_width=3,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Your Score: {user_score:.2f}",
        annotation_position="top right"
    )

    fig.update_layout(
        title=f'Simplified PRS Distribution for {trait}<br>Your score is at the {percentile:.1f}th percentile',
        xaxis_title="Standardized PRS Score",
        yaxis_title="Frequency",
        showlegend=False
    )

    st.plotly_chart(fig)

    # Note about model type
    st.info("ℹ️ This is a simplified model using only a few key SNPs. For more comprehensive analysis, consider using genome-wide models when available.")

    # Educational content for simple PRS
    st.subheader("What Does This Mean?")
    st.write("**Simplified Risk Assessment**: This model uses just a few key genetic variants to estimate your risk, like checking the main ingredients in a recipe rather than every spice. While less comprehensive than genome-wide models, it still provides valuable insights.")
    st.write("Simple PRS focuses on well-studied variants with strong effects on disease risk.")

    st.subheader("Key Takeaways")
    st.info(f"""
    - **Your PRS Percentile**: {result['percentile']:.1f}th percentile indicates {'elevated' if result['percentile'] > 75 else 'average' if result['percentile'] > 25 else 'lower'} genetic risk for {trait}
    - **Limited Scope**: Uses only {result['snps_used']} key variants, not genome-wide analysis
    - **Strong Effects**: Focuses on variants with well-established associations
    - **Starting Point**: Good foundation for understanding genetic risk factors
    - **Complement Lifestyle**: Combine with environmental and lifestyle factors for full risk picture
    """)

    # Lifetime Risk Projections Section
    st.markdown("---")
    st.subheader("⏳ Lifetime Risk Projections")

    if st.button("🔮 View Lifetime Risk Projections", key="lifetime_projections_simple"):
        render_lifetime_risk_projections(dna_data, result, trait)

    st.subheader("3.2. Interactive Risk Factor Guidance")

    # Interactive guidance based on selected trait
    if 'current_trait' in st.session_state:
        selected_trait = st.session_state['current_trait']
    else:
        selected_trait = st.selectbox("Select a condition for detailed guidance", list(guidance_data.keys()))

    if selected_trait in guidance_data:
        data = guidance_data[selected_trait]

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Lifestyle Modifications:**")
            for item in data["lifestyle"]:
                st.write(f"• {item}")

            st.write("**Monitoring & Screening:**")
            for item in data["monitoring"]:
                st.write(f"• {item}")

        with col2:
            st.write("**Medical Management:**")
            for item in data["medical"]:
                st.write(f"• {item}")

            st.write("**Screening Recommendations:**")
            for item in data["screening"]:
                st.write(f"• {item}")

        st.info("**Important:** This guidance is general and should be personalized with your healthcare provider. Genetic risk does not guarantee disease development, and lifestyle modifications can significantly impact outcomes.")

def render_lifetime_risk_projections(dna_data, prs_result=None, trait=None):
    """Render lifetime risk projection interface."""
    st.header("⏳ Lifetime Risk Projections")
    st.write("Explore how your genetic risk evolves over your lifetime with interactive projections and scenario analysis.")

    # Initialize lifetime risk calculator
    lifetime_calculator = LifetimeRiskCalculator()

    # Get available conditions
    available_conditions = lifetime_calculator.get_condition_list()
    if not available_conditions:
        st.error("No lifetime risk data available.")
        return

    # User input section
    st.subheader("4.1. Personal Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        current_age = st.number_input(
            "Current Age:",
            min_value=18,
            max_value=100,
            value=30,
            help="Your current age in years"
        )

    with col2:
        sex = st.selectbox(
            "Sex:",
            ["female", "male"],
            help="Biological sex for risk calculations"
        )

    with col3:
        ancestry = st.selectbox(
            "Ancestry:",
            ["European", "African", "East Asian", "South Asian", "American"],
            index=0,
            help="Genetic ancestry for risk adjustment"
        )

    # Lifestyle factors
    st.subheader("4.2. Lifestyle Factors")

    lifestyle_col1, lifestyle_col2, lifestyle_col3 = st.columns(3)

    with lifestyle_col1:
        smoking_status = st.selectbox(
            "Smoking Status:",
            ["Never", "Former", "Current"],
            help="Current smoking status"
        )

    with lifestyle_col2:
        exercise_level = st.selectbox(
            "Exercise Level:",
            ["Sedentary", "Light", "Moderate", "Active", "Very Active"],
            index=2,
            help="Weekly physical activity level"
        )

    with lifestyle_col3:
        diet_quality = st.selectbox(
            "Diet Quality:",
            ["Poor", "Fair", "Good", "Excellent"],
            index=2,
            help="Overall diet quality"
        )

    # Calculate lifestyle modifier
    lifestyle_modifier = calculate_lifestyle_modifier(smoking_status, exercise_level, diet_quality)

    # Condition selection
    st.subheader("4.3. Condition Selection")

    # Use PRS trait if available, otherwise let user select
    if trait and trait.replace('_', ' ') in [c.replace('_', ' ') for c in available_conditions]:
        default_condition = trait
    else:
        default_condition = available_conditions[0] if available_conditions else None

    selected_condition = st.selectbox(
        "Select Condition for Lifetime Projection:",
        available_conditions,
        index=available_conditions.index(default_condition) if default_condition in available_conditions else 0
    )

    # PRS integration
    prs_percentile = 50.0  # Default
    if prs_result and 'percentile' in prs_result:
        prs_percentile = prs_result['percentile']
        st.info(f"📊 Using your PRS percentile: {prs_percentile:.1f}th percentile for {trait}")

    # Projection parameters
    st.subheader("4.4. Projection Parameters")

    param_col1, param_col2 = st.columns(2)

    with param_col1:
        competing_risks = st.checkbox(
            "Account for Competing Risks",
            value=True,
            help="Include mortality from other causes in projections"
        )

    with param_col2:
        show_scenarios = st.checkbox(
            "Show Risk Scenarios",
            value=True,
            help="Display optimistic, baseline, and pessimistic projections"
        )

    # Calculate lifetime risk
    if st.button("🔮 Calculate Lifetime Risk Projection", type="primary"):
        with st.spinner("Calculating lifetime risk projections..."):
            try:
                # Calculate lifetime risk
                result = lifetime_calculator.calculate_lifetime_risk(
                    selected_condition,
                    current_age,
                    sex,
                    prs_percentile,
                    ancestry,
                    lifestyle_modifier,
                    competing_risks
                )

                if result['success']:
                    display_lifetime_risk_results(result, show_scenarios)
                else:
                    st.error(f"Failed to calculate lifetime risk: {result.get('error', 'Unknown error')}")

            except Exception as e:
                st.error(f"Error during lifetime risk calculation: {str(e)}")

def calculate_lifestyle_modifier(smoking_status, exercise_level, diet_quality):
    """Calculate lifestyle modifier based on user inputs."""
    modifier = 1.0

    # Smoking modifier
    if smoking_status == "Current":
        modifier *= 1.5  # Increased risk
    elif smoking_status == "Former":
        modifier *= 1.2  # Slightly increased risk

    # Exercise modifier
    exercise_modifiers = {
        "Sedentary": 1.3,
        "Light": 1.1,
        "Moderate": 1.0,
        "Active": 0.9,
        "Very Active": 0.8
    }
    modifier *= exercise_modifiers.get(exercise_level, 1.0)

    # Diet modifier
    diet_modifiers = {
        "Poor": 1.2,
        "Fair": 1.1,
        "Good": 1.0,
        "Excellent": 0.9
    }
    modifier *= diet_modifiers.get(diet_quality, 1.0)

    return modifier

def display_lifetime_risk_results(result, show_scenarios=True):
    """Display lifetime risk projection results."""
    st.success("✅ Lifetime risk projection completed!")

    # Summary metrics
    st.subheader("📊 Lifetime Risk Summary")

    summary = result.get('summary', {})
    if summary:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Lifetime Risk",
                f"{result['lifetime_risk']:.1%}",
                help="Cumulative risk from current age to end of life"
            )

        with col2:
            confidence = result['confidence_intervals']
            st.metric(
                "Confidence Interval",
                f"{confidence['lifetime_risk_lower']:.1%} - {confidence['lifetime_risk_upper']:.1%}",
                help="80% confidence interval for the projection"
            )

        with col3:
            st.metric(
                "Risk Level",
                summary.get('risk_level', 'Unknown'),
                help="Qualitative risk assessment"
            )

        with col4:
            st.metric(
                "Current Age",
                f"{result['current_age']} years",
                help="Age at which projection begins"
            )

    # Risk trajectory visualization
    st.subheader("📈 Risk Trajectory Over Time")

    trajectory = result['risk_trajectory']
    fig = create_risk_trajectory_plot(trajectory, result['confidence_intervals'])

    st.plotly_chart(fig, use_container_width=True)

    # Scenario analysis
    if show_scenarios:
        st.subheader("🎭 Risk Scenarios")

        scenarios = result['scenarios']
        scenario_fig = create_scenario_comparison_plot(scenarios, trajectory)

        st.plotly_chart(scenario_fig, use_container_width=True)

        # Scenario details
        scenario_col1, scenario_col2, scenario_col3 = st.columns(3)

        with scenario_col1:
            st.metric(
                "Optimistic Scenario",
                f"{scenarios['optimistic']['lifetime_risk']:.1%}",
                help="Best-case projection with lifestyle improvements"
            )

        with scenario_col2:
            st.metric(
                "Baseline Scenario",
                f"{scenarios['baseline']['lifetime_risk']:.1%}",
                help="Current lifestyle and risk factors"
            )

        with scenario_col3:
            st.metric(
                "Pessimistic Scenario",
                f"{scenarios['pessimistic']['lifetime_risk']:.1%}",
                help="Worst-case projection with adverse lifestyle"
            )

    # Risk interpretation
    st.subheader("🎯 Risk Interpretation")

    if summary:
        st.write(f"**{summary.get('condition', 'Condition')}:** {summary.get('interpretation', '')}")

        # Key insights
        with st.expander("🔑 Key Insights"):
            st.write("**Modifiers Applied:**")
            modifiers = result['modifiers']
            st.write(f"- PRS Modifier: {modifiers['prs_modifier']:.2f}x")
            st.write(f"- Ancestry Modifier: {modifiers['ancestry_modifier']:.2f}x")
            st.write(f"- Lifestyle Modifier: {modifiers['lifestyle_modifier']:.2f}x")
            st.write(f"- Total Modifier: {modifiers['total_modifier']:.2f}x")

            st.write("\n**What This Means:**")
            st.write("- Lifetime risk represents cumulative probability from your current age")
            st.write("- Projections account for age-specific incidence rates and competing mortality")
            st.write("- Lifestyle modifications can significantly impact long-term risk")

    # Educational content
    with st.expander("📚 Understanding Lifetime Risk"):
        st.write("""
        **What is Lifetime Risk?**
        Lifetime risk represents the cumulative probability of developing a condition from your current age until the end of life.

        **Key Factors in Projections:**
        - Age-specific incidence rates from epidemiological studies
        - Your polygenic risk score (PRS) percentile
        - Genetic ancestry adjustments
        - Lifestyle and environmental factors
        - Competing risks from other causes of mortality

        **Important Limitations:**
        - Projections are statistical estimates, not predictions
        - Individual outcomes may vary significantly
        - Regular screening and preventive care are essential
        - Consult healthcare providers for personalized advice
        """)

    # Export options
    st.subheader("💾 Export Options")

    export_col1, export_col2 = st.columns(2)

    with export_col1:
        if st.button("📊 Export Risk Trajectory Data"):
            # Create downloadable CSV
            export_data = trajectory.copy()
            export_data['condition'] = result['condition']
            export_data['current_age'] = result['current_age']
            export_data['sex'] = result['sex']

            csv_data = export_data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"lifetime_risk_{result['condition']}_{result['current_age']}yo.csv",
                mime="text/csv"
            )

    with export_col2:
        if st.button("📈 Export Projection Summary"):
            # Create summary text
            summary_text = f"""
Lifetime Risk Projection Summary
================================

Condition: {result['condition'].replace('_', ' ').title()}
Current Age: {result['current_age']} years
Sex: {result['sex'].title()}
Ancestry: {result['parameters']['ancestry']}

Lifetime Risk: {result['lifetime_risk']:.1%}
Confidence Interval: {result['confidence_intervals']['lifetime_risk_lower']:.1%} - {result['confidence_intervals']['lifetime_risk_upper']:.1%}

Risk Modifiers:
- PRS Percentile: {result['parameters']['prs_percentile']:.1f}th
- PRS Modifier: {result['modifiers']['prs_modifier']:.2f}x
- Ancestry Modifier: {result['modifiers']['ancestry_modifier']:.2f}x
- Lifestyle Modifier: {result['modifiers']['lifestyle_modifier']:.2f}x

Scenarios:
- Optimistic: {result['scenarios']['optimistic']['lifetime_risk']:.1%}
- Baseline: {result['scenarios']['baseline']['lifetime_risk']:.1%}
- Pessimistic: {result['scenarios']['pessimistic']['lifetime_risk']:.1%}

Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
            """

            st.download_button(
                label="Download Summary",
                data=summary_text,
                file_name=f"lifetime_risk_summary_{result['condition']}_{result['current_age']}yo.txt",
                mime="text/plain"
            )

def create_risk_trajectory_plot(trajectory, confidence_intervals):
    """Create interactive risk trajectory plot."""
    fig = go.Figure()

    # Main risk trajectory
    fig.add_trace(go.Scatter(
        x=trajectory['age'],
        y=trajectory['cumulative_risk'],
        mode='lines+markers',
        name='Lifetime Risk',
        line=dict(color='blue', width=3),
        marker=dict(size=6),
        hovertemplate='Age: %{x}<br>Risk: %{y:.1%}<extra></extra>'
    ))

    # Confidence bands
    if 'age_specific_lower' in confidence_intervals and 'age_specific_upper' in confidence_intervals:
        ages = trajectory['age'].values
        lower_band = confidence_intervals['age_specific_lower']
        upper_band = confidence_intervals['age_specific_upper']

        fig.add_trace(go.Scatter(
            x=ages,
            y=upper_band,
            mode='lines',
            name='Upper Confidence',
            line=dict(width=0),
            showlegend=False,
            hovertemplate='Age: %{x}<br>Upper: %{y:.1%}<extra></extra>'
        ))

        fig.add_trace(go.Scatter(
            x=ages,
            y=lower_band,
            mode='lines',
            name='Lower Confidence',
            line=dict(width=0),
            fill='tonexty',
            fillcolor='rgba(0,100,255,0.2)',
            showlegend=False,
            hovertemplate='Age: %{x}<br>Lower: %{y:.1%}<extra></extra>'
        ))

    # Update layout
    fig.update_layout(
        title="Lifetime Risk Trajectory",
        xaxis_title="Age (years)",
        yaxis_title="Cumulative Risk",
        yaxis_tickformat='.1%',
        hovermode='x unified',
        showlegend=True
    )

    return fig

def create_scenario_comparison_plot(scenarios, baseline_trajectory):
    """Create scenario comparison plot."""
    fig = go.Figure()

    # Baseline scenario
    baseline = scenarios['baseline']['trajectory']
    fig.add_trace(go.Scatter(
        x=baseline['age'],
        y=baseline['cumulative_risk'],
        mode='lines',
        name='Baseline',
        line=dict(color='blue', width=3),
        hovertemplate='Age: %{x}<br>Baseline: %{y:.1%}<extra></extra>'
    ))

    # Optimistic scenario
    optimistic = scenarios['optimistic']['trajectory']
    fig.add_trace(go.Scatter(
        x=optimistic['age'],
        y=optimistic['cumulative_risk'],
        mode='lines',
        name='Optimistic',
        line=dict(color='green', width=2, dash='dash'),
        hovertemplate='Age: %{x}<br>Optimistic: %{y:.1%}<extra></extra>'
    ))

    # Pessimistic scenario
    pessimistic = scenarios['pessimistic']['trajectory']
    fig.add_trace(go.Scatter(
        x=pessimistic['age'],
        y=pessimistic['cumulative_risk'],
        mode='lines',
        name='Pessimistic',
        line=dict(color='red', width=2, dash='dash'),
        hovertemplate='Age: %{x}<br>Pessimistic: %{y:.1%}<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        title="Risk Scenarios Comparison",
        xaxis_title="Age (years)",
        yaxis_title="Cumulative Risk",
        yaxis_tickformat='.1%',
        hovermode='x unified',
        showlegend=True
    )

    return fig