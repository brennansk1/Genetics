import streamlit as st
import pandas as pd
import os
import tempfile
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import parse_dna_file
from render_clinical import render_clinical_risk
from render_pgx import render_pharmacogenomics
from render_prs import render_prs_dashboard
from render_wellness import render_wellness_profile
from render_advanced import render_advanced_analytics
from render_data_portability import render_data_portability
from src.pdf_generator.main import generate_enhanced_pdf_report

def render_pdf_generator(dna_data):
    """Render the enhanced PDF report generator interface."""
    st.header("📄 Enhanced Educational PDF Report Generator")

    st.markdown("""
    Generate a comprehensive, educational PDF report that transforms your genetic data into an engaging health journey.
    This enhanced report includes:

    - **Educational analogies** explaining genetic concepts
    - **Interactive visualizations** showing your health predispositions
    - **Personalized medication guide** with metabolism explanations
    - **Actionable health insights** based on your genetic profile
    """)

    # User information
    col1, col2 = st.columns(2)
    with col1:
        user_name = st.text_input("Your Name (for report personalization)", value="Valued User")
    with col2:
        user_id = st.text_input("User ID", value="GENOMIC001")

    # Report generation options
    st.subheader("Report Options")
    include_all_sections = st.checkbox("Include all sections", value=True)
    include_visualizations = st.checkbox("Include interactive visualizations", value=True)
    include_medication_guide = st.checkbox("Include personalized medication guide", value=True)

    # Generate report button
    if st.button("🚀 Generate Enhanced PDF Report", type="primary"):
        with st.spinner("Generating your enhanced educational report... This may take a moment."):

            # Create temporary directory for results
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    # Generate the enhanced PDF report
                    generate_enhanced_pdf_report(dna_data, temp_dir, user_id)

                    # Check if PDF was created
                    pdf_path = os.path.join(temp_dir, "Enhanced_Genomic_Health_Report.pdf")
                    if os.path.exists(pdf_path):
                        # Read the PDF file
                        with open(pdf_path, "rb") as pdf_file:
                            pdf_data = pdf_file.read()

                        # Create download button
                        st.success("✅ Enhanced PDF report generated successfully!")
                        st.download_button(
                            label="📥 Download Your Enhanced Genomic Health Report",
                            data=pdf_data,
                            file_name=f"Enhanced_Genomic_Health_Report_{user_id}.pdf",
                            mime="application/pdf",
                            help="Click to download your comprehensive educational genetic health report"
                        )

                        # Show preview info
                        st.info("Your report includes educational content about genetics, personalized health insights, and actionable recommendations based on your genetic profile.")

                    else:
                        st.error("❌ PDF generation failed. Please try again.")

                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")
                    st.info("Please ensure all required dependencies are installed and try again.")

    # Educational content preview
    st.subheader("What Makes This Report Special?")
    st.markdown("""
    **🎓 Educational Journey**: Unlike basic reports, this transforms genetic data into an engaging learning experience.

    **⭐ Evidence-Based**: Every finding includes star ratings showing scientific confidence.

    **🎯 Actionable Insights**: Clear next steps tailored to your genetic profile.

    **💊 Medication Guide**: Visual explanations of how your genetics affect drug responses.

    **🗺️ Health Constellation**: Interactive map showing your genetic predispositions across health categories.
    """)

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
        "6: Data Portability and Utility",
        "7: Generate Enhanced PDF Report"
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
    elif analysis_module == "7: Generate Enhanced PDF Report":
        render_pdf_generator(dna_data)


if __name__ == "__main__":
    main()