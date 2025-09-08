import streamlit as st
import pandas as pd
from snp_data import recessive_snps, cancer_snps, cardiovascular_snps, neuro_snps, mito_snps, protective_snps, ancestry_panels, acmg_sf_variants

def render_clinical_risk(dna_data):
    st.header("Module 1: Clinical Risk & Carrier Status")
    st.write("This module will identify high-impact genetic variants with established clinical significance.")

    st.subheader("1.1. Pathogenic Variant Screener")
    clinvar_tsv_path = "clinvar_pathogenic_variants.tsv"
    if st.button("Run Pathogenic Variant Screener"):
        try:
            clinvar_df = pd.read_csv(clinvar_tsv_path, sep='\t', dtype={'rsid': str})

            # Reset index to get 'rsid' as a column and ensure it's a string
            dna_data_reset = dna_data.reset_index()
            dna_data_reset['rsid'] = dna_data_reset['rsid'].astype(str)

            merged_df = dna_data_reset.merge(clinvar_df, on='rsid')
            if not merged_df.empty:
                st.write("Pathogenic or Likely Pathogenic variants found in your data:")
                st.dataframe(merged_df[['rsid', 'chromosome', 'position', 'genotype', 'CLNSIG']])
            else:
                st.success("No pathogenic or likely pathogenic variants from the ClinVar file were found in your data.")
        except FileNotFoundError:
            st.error(f"ClinVar TSV file not found at {clinvar_tsv_path}. Please run the analysis from the command line first to generate this file.")

    st.subheader("1.2. Recessive Carrier Status Report")
    if st.button("Run Recessive Carrier Status Report"):
        results = []
        for rsid, info in recessive_snps.items():
            user_genotype = dna_data[dna_data.index == rsid]
            status = 'Not a carrier (or not tested)'
            genotype = 'Not in data'
            if not user_genotype.empty:
                genotype = user_genotype.iloc[0]['genotype']
                sorted_genotype = "".join(sorted(genotype))
                if sorted_genotype in info['interp']:
                    status = info['interp'][sorted_genotype]
            results.append({'rsID': rsid, 'Gene': info['gene'], 'Condition': info['condition'], 'Genotype': genotype, 'Status': status})
        carrier_df = pd.DataFrame(results).set_index('rsID')
        st.dataframe(carrier_df)

    st.subheader("1.3. Hereditary Cancer Syndromes")
    if st.button("Run Hereditary Cancer Syndromes Analysis"):
        results = []
        for rsid, info in cancer_snps.items():
            user_genotype = dna_data[dna_data.index == rsid]
            status = 'No risk variant detected'
            genotype = 'Not in data'
            if not user_genotype.empty:
                genotype = user_genotype.iloc[0]['genotype']
                # A simple check for presence of the variant is sufficient for this example
                status = 'Risk variant detected'
            results.append({'rsID': rsid, 'Gene': info['gene'], 'Risk': info['risk'], 'Genotype': genotype, 'Status': status})
        cancer_df = pd.DataFrame(results).set_index('rsID')
        st.dataframe(cancer_df)

    st.subheader("1.4. Cardiovascular Conditions")
    if st.button("Run Cardiovascular Conditions Analysis"):
        results = []
        for rsid, info in cardiovascular_snps.items():
            user_genotype = dna_data[dna_data.index == rsid]
            status = 'No risk variant detected'
            genotype = 'Not in data'
            if not user_genotype.empty:
                genotype = user_genotype.iloc[0]['genotype']
                # Simple check for presence of variant
                status = 'Risk variant detected'
            results.append({'rsID': rsid, 'Gene': info['gene'], 'Risk': info['risk'], 'Genotype': genotype, 'Status': status})
        cardiovascular_df = pd.DataFrame(results).set_index('rsID')
        st.dataframe(cardiovascular_df)

    st.subheader("1.5. Neurodegenerative Conditions")
    if st.button("Run Neurodegenerative Conditions Analysis"):
        results = []
        for rsid, info in neuro_snps.items():
            user_genotype = dna_data[dna_data.index == rsid]
            status = 'No risk variant detected'
            genotype = 'Not in data'
            if not user_genotype.empty:
                genotype = user_genotype.iloc[0]['genotype']
                status = 'Risk variant detected'
            results.append({'rsID': rsid, 'Gene': info['gene'], 'Risk': info['risk'], 'Genotype': genotype, 'Status': status})
        neuro_df = pd.DataFrame(results).set_index('rsID')
        st.dataframe(neuro_df)

    st.subheader("1.6. Mitochondrial Health Analysis")
    if st.button("Run Mitochondrial Health Analysis"):
        results = []
        for rsid, info in mito_snps.items():
            user_genotype = dna_data[dna_data.index == rsid]
            status = 'No risk variant detected'
            genotype = 'Not in data'
            if not user_genotype.empty:
                genotype = user_genotype.iloc[0]['genotype']
                status = 'Risk variant detected'
            results.append({'rsID': rsid, 'Gene': info['gene'], 'Risk': info['risk'], 'Genotype': genotype, 'Status': status})
        mito_df = pd.DataFrame(results).set_index('rsID')
        st.dataframe(mito_df)

    st.subheader("1.7. Protective Variant Highlights")
    if st.button("Run Protective Variant Highlights"):
        results = []
        for rsid, info in protective_snps.items():
            user_genotype = dna_data[dna_data.index == rsid]
            status = 'No protective variant detected (or not tested)'
            genotype = 'Not in data'
            if not user_genotype.empty:
                genotype = user_genotype.iloc[0]['genotype']
                sorted_genotype = "".join(sorted(genotype))
                if sorted_genotype in info['interp']:
                    status = info['interp'][sorted_genotype]
            results.append({'rsID': rsid, 'Gene': info['gene'], 'Trait': info['trait'], 'Genotype': genotype, 'Status': status})
        protective_df = pd.DataFrame(results).set_index('rsID')
        st.dataframe(protective_df)

    st.subheader("1.8. Expanded Ancestry-Aware Screening Panels")
    selected_ancestry = st.selectbox("Select your ancestry background for targeted screening", list(ancestry_panels.keys()))

    if st.button("Run Ancestry-Aware Screening"):
        results = []
        for rsid, info in ancestry_panels[selected_ancestry].items():
            user_genotype = dna_data[dna_data.index == rsid]
            status = 'No risk variant detected'
            genotype = 'Not in data'
            if not user_genotype.empty:
                genotype = user_genotype.iloc[0]['genotype']
                # For carrier screening, heterozygous variants are typically reported
                if len(set(genotype)) > 1:
                    status = 'Risk variant detected - Consider genetic counseling'
            results.append({'rsID': rsid, 'Gene': info['gene'], 'Condition': info['condition'], 'Genotype': genotype, 'Status': status})
        ancestry_df = pd.DataFrame(results).set_index('rsID')
        st.dataframe(ancestry_df)

        st.info("**Note:** This screening is ancestry-informed but not definitive. Many conditions have variants not covered here. Consult a genetic counselor for comprehensive testing.")

    st.subheader("1.9. ACMG Secondary Findings Screening")
    if st.button("Run ACMG Secondary Findings Screening"):
        results = []
        for rsid, info in acmg_sf_variants.items():
            user_genotype = dna_data[dna_data.index == rsid]
            status = 'No ACMG secondary finding detected'
            genotype = 'Not in data'
            if not user_genotype.empty:
                genotype = user_genotype.iloc[0]['genotype']
                # For ACMG secondary findings, heterozygous variants are typically reported
                if len(set(genotype)) > 1:
                    status = 'ACMG secondary finding detected - Consult genetic counselor'
            results.append({'rsID': rsid, 'Gene': info['gene'], 'Condition': info['condition'], 'Genotype': genotype, 'Status': status})
        acmg_df = pd.DataFrame(results).set_index('rsID')
        st.dataframe(acmg_df)

        st.warning("**ACMG Secondary Findings:** These are genes recommended by the American College of Medical Genetics for secondary findings analysis. Detection of variants in these genes may have significant medical implications. Professional genetic counseling is strongly recommended.")
