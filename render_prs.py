import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from snp_data import prs_models, guidance_data
from api_functions import get_pgs_catalog_data, get_pgs_model_data

def render_prs_dashboard(dna_data):
    st.header("Module 3: Polygenic Risk Score (PRS) Dashboard")
    st.write("This module assesses risk for complex, multi-gene conditions.")

    st.subheader("3.1. Interactive Risk Calculator")

    # Search for PGS models
    trait_search = st.text_input("Search for a trait (e.g., 'diabetes', 'cancer')", key="trait_search")
    if trait_search:
        # Placeholder for search functionality
        st.info("Search functionality would integrate with PGS Catalog API here.")

    # Fallback to hardcoded models
    if 'current_model' not in st.session_state:
        trait = st.selectbox("Select a trait to calculate your Polygenic Risk Score", list(prs_models.keys()))
        model_data = prs_models[trait]
    else:
        trait = st.session_state['current_trait']
        model_data = st.session_state['current_model']

    if st.button("Calculate PRS"):
        if 'current_model' in st.session_state or trait:
            with st.spinner(f"Calculating PRS for {trait}..."):
                prs_model_df = pd.DataFrame(model_data).set_index('rsid')
                merged_df = dna_data.join(prs_model_df, how='inner')

                if merged_df.empty:
                    st.warning(f"No overlapping SNPs found for {trait} PRS model. Skipping.")
                    return

                merged_df['allele_count'] = merged_df.apply(lambda row: row['genotype'].upper().count(row['effect_allele']), axis=1)
                merged_df['score_contribution'] = merged_df['allele_count'] * merged_df['effect_weight']
                user_prs = merged_df['score_contribution'].sum()

                np.random.seed(hash(trait) % (2**32 - 1))
                mean_prs = prs_model_df['effect_weight'].sum()
                var_prs = 0.5 * (prs_model_df['effect_weight'] ** 2).sum()
                population_scores = np.random.normal(loc=mean_prs, scale=np.sqrt(var_prs), size=10000)
                percentile = (np.sum(population_scores < user_prs) / len(population_scores)) * 100

                fig = go.Figure()
                fig.add_trace(go.Histogram(x=population_scores, name='Population', nbinsx=50, marker_color='#636EFA'))
                fig.add_vline(x=user_prs, line_width=3, line_dash="dash", line_color="red", annotation_text=f"Your Score: {user_prs:.3f}", annotation_position="top right")
                fig.update_layout(title_text=f'Polygenic Risk Score for {trait}<br>Your score is at the {percentile:.1f}th percentile.')
                st.plotly_chart(fig)

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