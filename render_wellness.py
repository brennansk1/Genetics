import streamlit as st
from utils import analyze_wellness_snps

def render_wellness_profile(dna_data):
    st.header("Module 4: Holistic Wellness & Trait Profile")
    st.write("This module provides engaging insights into non-clinical traits related to lifestyle, nutrition, and fitness.")

    if st.button("Analyze Wellness & Traits"):
        with st.spinner("Analyzing your wellness SNPs..."):
            wellness_results = analyze_wellness_snps(dna_data)

        st.success("Analysis complete!")

        st.subheader("4.1. Nutritional Genetics Profile")
        for rsid, data in wellness_results.items():
            if data['name'] in ["Lactose Tolerance", "Caffeine Metabolism", "Vitamin B12", "Vitamin D"]:
                interpretation = 'Not determined'
                if 'interp' in data and data['genotype'] in data['interp']:
                    interpretation = data['interp'][data['genotype']]
                st.write(f"**{data['name']} ({data['gene']} - {rsid}):** Genotype: {data['genotype']}, Interpretation: {interpretation}")

        st.subheader("4.2. Fitness Genetics Profile")
        for rsid, data in wellness_results.items():
            if data['name'] == "Athletic Performance (Power/Sprint vs. Endurance)":
                interpretation = 'Not determined'
                if 'interp' in data and data['genotype'] in data['interp']:
                    interpretation = data['interp'][data['genotype']]
                st.write(f"**{data['name']} ({data['gene']} - {rsid}):** Genotype: {data['genotype']}, Interpretation: {interpretation}")

        st.subheader("4.3. Holistic Pathway Analysis")
        for rsid, data in wellness_results.items():
            if data['name'] == "Methylation (COMT)":
                interpretation = 'Not determined'
                if 'interp' in data and data['genotype'] in data['interp']:
                    interpretation = data['interp'][data['genotype']]
                st.write(f"**{data['name']} ({data['gene']} - {rsid}):** Genotype: {data['genotype']}, Interpretation: {interpretation}")

        st.subheader("4.4. 'Quirky' Trait Report")
        for rsid, data in wellness_results.items():
            if data['name'] in ["Bitter Taste Perception", "Photic Sneeze Reflex", "Asparagus Metabolite Detection"]:
                interpretation = 'Not determined'
                if 'interp' in data and data['genotype'] in data['interp']:
                    interpretation = data['interp'][data['genotype']]
                st.write(f"**{data['name']} ({data['gene']} - {rsid}):** Genotype: {data['genotype']}, Interpretation: {interpretation}")