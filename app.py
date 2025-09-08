import streamlit as st
import pandas as pd
from utils import parse_dna_file
from render_clinical import render_clinical_risk
from render_pgx import render_pharmacogenomics
from render_prs import render_prs_dashboard
from render_wellness import render_wellness_profile
from render_advanced import render_advanced_analytics
from render_data_portability import render_data_portability




def main():
    st.set_page_config(layout="wide")
    st.title("Comprehensive Genomic Health Dashboard")

    st.warning("""
    **Medical Disclaimer:** This application is for informational and educational purposes only. 
    It is not a medical device. The information provided is not intended to be a substitute for professional medical advice, diagnosis, or treatment. 
    Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. 
    Never disregard professional medical advice or delay in seeking it because of something you have read here.
    """)

    st.sidebar.title("Navigation")
    analysis_module = st.sidebar.radio("Go to", [
        "1: Clinical Risk & Carrier Status",
        "2: Pharmacogenomics (PGx) Report",
        "3: Polygenic Risk Score (PRS) Dashboard",
        "4: Holistic Wellness & Trait Profile",
        "5: Advanced Analytics & Exploration",
        "6: Data Portability and Utility"
    ])

    st.sidebar.title("Upload Data")
    file_format = st.sidebar.selectbox("Select DNA file format",
                                      ["AncestryDNA", "23andMe", "MyHeritage", "LivingDNA"],
                                      help="Choose the format of your DNA file")
    uploaded_file = st.sidebar.file_uploader(f"Upload your {file_format} file", type=["txt", "csv", "tsv"])

    if uploaded_file is not None:
        st.sidebar.success("File uploaded successfully!")
        try:
            dna_data = parse_dna_file(uploaded_file, file_format)
            # Set rsid as index for faster lookups
            dna_data.set_index('rsid', inplace=True)
        except Exception as e:
            st.error(f"Error parsing the file: {e}")
            return

    else:
        st.sidebar.info("Please upload a file to begin analysis.")
        st.info("Please upload your DNA data file to proceed.")
        return

    if analysis_module == "1: Clinical Risk & Carrier Status":
        render_clinical_risk(dna_data)
    elif analysis_module == "2: Pharmacogenomics (PGx) Report":
        render_pharmacogenomics(dna_data)
    elif analysis_module == "3: Polygenic Risk Score (PRS) Dashboard":
        render_prs_dashboard(dna_data)
    elif analysis_module == "4: Holistic Wellness & Trait Profile":
        render_wellness_profile(dna_data)
    elif analysis_module == "5: Advanced Analytics & Exploration":
        render_advanced_analytics(dna_data)
    elif analysis_module == "6: Data Portability and Utility":
        render_data_portability(dna_data)


if __name__ == "__main__":
    main()