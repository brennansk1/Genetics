import streamlit as st
import pandas as pd
from .drug_interactions import InteractionChecker

def render_drug_interactions(dna_data: pd.DataFrame):
    """
    Renders the Drug-Drug-Gene Interaction Analysis page.
    """
    st.header("💊 Drug-Drug-Gene Interaction Analysis")
    st.markdown("""
    This module analyzes potential interactions between your medications (Drug-Drug) 
    and between your medications and your genetic profile (Drug-Gene).
    """)
    
    st.info("Enter your current medications below to check for potential interactions.")
    
    # Input for medications
    # We could use a pre-defined list for auto-complete if we had a large DB, 
    # but for now free text or a small selectbox.
    # Let's use a text area for comma-separated values for flexibility, 
    # or a multiselect with common drugs.
    
    common_drugs = [
        "Warfarin", "Clopidogrel", "Simvastatin", "Codeine", "Tacrolimus", 
        "Aspirin", "Omeprazole", "Lisinopril", "Potassium", "Amiodarone"
    ]
    
    selected_meds = st.multiselect(
        "Select medications:",
        options=common_drugs,
        default=[]
    )
    
    custom_meds = st.text_input("Or enter others (comma separated):")
    
    if st.button("Analyze Interactions", type="primary"):
        meds = selected_meds.copy()
        if custom_meds:
            meds.extend([m.strip() for m in custom_meds.split(",") if m.strip()])
            
        if not meds:
            st.warning("Please select or enter at least one medication.")
            return
            
        checker = InteractionChecker(dna_data)
        results = checker.analyze(meds)
        
        # Display Drug-Drug Interactions
        st.subheader("Drug-Drug Interactions")
        ddis = results["drug_drug"]
        if ddis:
            for ddi in ddis:
                severity_color = "red" if ddi["severity"] == "Major" else "orange"
                st.markdown(f"""
                <div style="padding: 10px; border-left: 5px solid {severity_color}; background-color: #f0f2f6;">
                    <strong>{' + '.join([d.title() for d in ddi['drugs']])}</strong><br>
                    <span style="color: {severity_color}; font-weight: bold;">{ddi['severity']} Severity</span><br>
                    {ddi['description']}<br>
                    <em>Management: {ddi['management']}</em>
                </div>
                <br>
                """, unsafe_allow_html=True)
        else:
            st.success("No known drug-drug interactions found in our database for these medications.")
            
        # Display Drug-Gene Interactions
        st.subheader("Drug-Gene Interactions (PGx)")
        dgis = results["drug_gene"]
        if dgis:
            for dgi in dgis:
                is_normal = "Normal" in dgi['phenotype']
                border_color = "green" if is_normal else "purple"
                bg_color = "#e6ffe6" if is_normal else "#f0f2f6"
                
                st.markdown(f"""
                <div style="padding: 10px; border-left: 5px solid {border_color}; background-color: {bg_color};">
                    <strong>{dgi['drug'].title()}</strong> (Gene: {dgi['gene']})<br>
                    Phenotype: <strong>{dgi['phenotype']}</strong><br>
                    Recommendation: {dgi['recommendation']}
                </div>
                """, unsafe_allow_html=True)
                
                if dgi['details']:
                    with st.expander("See Genetic Details"):
                        st.table(pd.DataFrame(dgi['details']))
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.success("No specific drug-gene interactions found for your genetic profile.")
            
    st.markdown("---")
    st.caption("Disclaimer: This tool is for educational purposes only. Always consult your healthcare provider before changing medications.")
