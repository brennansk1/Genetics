import os

import streamlit as st

from .pdf_generator import generate_pdf_report


def render_data_portability(dna_data):
    st.header("Module 6: Data Portability and Utility")
    st.write(
        "This module allows you to export your analysis results and interact with third-party tools."
    )

    # Educational tooltips for technical terms
    st.subheader("Understanding Key Terms")
    with st.expander("Click to see beginner-friendly definitions of data terms"):
        st.write(
            "**Data Portability**: The ability to move your genetic data between different services and tools."
        )
        st.write(
            "**Export Formats**: Different file types (CSV, TSV, JSON) for sharing data with other applications."
        )
        st.write(
            "**Third-Party Tools**: External websites and services that can analyze your genetic data."
        )
        st.write(
            "**Data Privacy**: Protecting your genetic information from unauthorized access."
        )

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
        tsv = dna_data_reset.to_csv(index=False, sep="\t")
        st.download_button(
            "Download TSV", tsv, "dna_data.tsv", "text/tab-separated-values"
        )
    elif export_format == "JSON":
        json_data = dna_data_reset.to_json(orient="records")
        st.download_button(
            "Download JSON", json_data, "dna_data.json", "application/json"
        )

    st.subheader("6.3. Third-Party Tool Integration")

    st.write("**Promethease Integration:**")
    st.info(
        "Upload your DNA data to Promethease for additional analysis. [Learn more](https://www.promethease.com/)"
    )

    st.write("**GEDmatch Integration:**")
    st.info(
        "Upload your DNA data to GEDmatch for ancestry and health analysis. [Learn more](https://www.gedmatch.com/)"
    )

    st.write("**FamilyTreeDNA Integration:**")
    st.info(
        "If you have FamilyTreeDNA data, you can upload it here for combined analysis."
    )

    # Educational content for data portability
    st.subheader("What Does This Mean?")
    st.write(
        "**Owning Your Data**: Data portability gives you control over your genetic information. You can move it between services, combine insights from different tools, and keep your data secure."
    )
    st.write(
        "Third-party tools offer specialized analysis that complements this dashboard's capabilities."
    )

    st.subheader("Key Takeaways")
    st.info(
        """
    - **Data Control**: Export your data in multiple formats for use with other tools
    - **Privacy First**: Your data stays local and private - only you decide where to share it
    - **Tool Integration**: Combine insights from different genetic analysis platforms
    - **Backup Security**: Regular exports ensure you never lose access to your data
    - **Research Access**: Share anonymized data with research studies if you choose
    """
    )

    st.subheader("6.4. Data Privacy and Security")

    st.write(
        "**Your data is processed locally and never sent to external servers without your explicit consent.**"
    )
    st.write("**We recommend:**")
    st.write("- Using strong passwords for your DNA data files")
    st.write("- Storing backups in encrypted formats")
    st.write("- Being cautious about sharing genetic data online")
    st.write("- Consulting privacy policies of third-party tools")

    st.info(
        "**Disclaimer:** This tool is for educational purposes. Always consult healthcare professionals for medical decisions."
    )
