import streamlit as st
import pandas as pd
from snp_data import pgx_snps, adverse_reaction_snps

def render_pharmacogenomics(dna_data):
    st.header("Module 2: Pharmacogenomics (PGx) Report")
    st.write("This module provides insights into potential responses to common medications.")

    st.subheader("2.1. Medication Metabolism Dashboard")
    if st.button("Run Medication Metabolism Analysis"):
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
            results.append({'rsID': rsid, 'Gene/Locus': info['gene'], 'Relevance': info['relevance'], 'Genotype': genotype, 'Interpretation': interpretation})
        pgx_df = pd.DataFrame(results).set_index('rsID')
        st.dataframe(pgx_df)

    st.subheader("2.2. Adverse Drug Reaction Sensitivity")
    if st.button("Run Adverse Drug Reaction Sensitivity Analysis"):
        results = []
        for rsid, info in adverse_reaction_snps.items():
            user_genotype = dna_data[dna_data.index == rsid]
            interpretation = 'Not in data'
            genotype = 'Not in data'
            if not user_genotype.empty:
                genotype = user_genotype.iloc[0]['genotype']
                sorted_genotype = "".join(sorted(genotype))
                if sorted_genotype in info['interp']:
                    interpretation = info['interp'][sorted_genotype]
            results.append({'rsID': rsid, 'Gene/Locus': info['gene'], 'Relevance': info['relevance'], 'Genotype': genotype, 'Interpretation': interpretation})
        adverse_df = pd.DataFrame(results).set_index('rsID')
        st.dataframe(adverse_df)