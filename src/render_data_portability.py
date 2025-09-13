import streamlit as st
from pdf_generator import generate_pdf_report
import os

def render_data_portability(dna_data):
    st.header("Module 6: Data Portability and Utility")
    st.write("This module allows you to export your analysis results and interact with third-party tools.")

    st.subheader("6.1. Export Analysis Results")

    if st.button("Generate Comprehensive PDF Report"):
        with st.spinner("Generating PDF report..."):
            results_dir = "results"
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)
            generate_pdf_report({}, results_dir, dna_data)
        st.success("PDF report generated successfully! Check the 'results' folder.")

    st.subheader("6.2. Raw Data Export")

    export_format = st.selectbox("Select export format", ["CSV", "TSV", "JSON"])

    dna_data_reset = dna_data.reset_index()

    if export_format == "CSV":
        csv = dna_data_reset.to_csv(index=False)
        st.download_button("Download CSV", csv, "dna_data.csv", "text/csv")
    elif export_format == "TSV":
        tsv = dna_data_reset.to_csv(index=False, sep='\t')
        st.download_button("Download TSV", tsv, "dna_data.tsv", "text/tab-separated-values")
    elif export_format == "JSON":
        json_data = dna_data_reset.to_json(orient='records')
        st.download_button("Download JSON", json_data, "dna_data.json", "application/json")

    st.subheader("6.3. Third-Party Tool Integration")

    st.write("**Promethease Integration:**")
    st.info("Upload your DNA data to Promethease for additional analysis. [Learn more](https://www.promethease.com/)")

    st.write("**GEDmatch Integration:**")
    st.info("Upload your DNA data to GEDmatch for ancestry and health analysis. [Learn more](https://www.gedmatch.com/)")

    st.write("**FamilyTreeDNA Integration:**")
    st.info("If you have FamilyTreeDNA data, you can upload it here for combined analysis.")

    st.subheader("6.4. Data Privacy and Security")

    st.write("**Your data is processed locally and never sent to external servers without your explicit consent.**")
    st.write("**We recommend:**")
    st.write("- Using strong passwords for your DNA data files")
    st.write("- Storing backups in encrypted formats")
    st.write("- Being cautious about sharing genetic data online")
    st.write("- Consulting privacy policies of third-party tools")

    st.info("**Disclaimer:** This tool is for educational purposes. Always consult healthcare professionals for medical decisions.")