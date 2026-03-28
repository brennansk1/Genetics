import streamlit as st
import pandas as pd
from .family_analysis import FamilyAnalyzer
from .utils import parse_dna_file

def render_family_analysis(dna_data=None):
    """
    Renders the Family Analysis page.
    Note: dna_data argument is kept for signature consistency but we need TWO files here.
    """
    st.header("👨‍👩‍👧‍👦 Family & Relationship Analysis")
    st.markdown("""
    Compare two DNA profiles to determine genetic relatedness and analyze inheritance patterns.
    Upload two files (e.g., Parent and Child, or Siblings) to begin.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Person 1")
        file1 = st.file_uploader("Upload DNA File 1", type=["txt", "csv", "tsv", "vcf"], key="fam_file1")
        format1 = st.selectbox("Format 1", ["AncestryDNA", "23andMe", "MyHeritage", "LivingDNA", "VCF"], key="fam_fmt1")
        
    with col2:
        st.subheader("Person 2")
        file2 = st.file_uploader("Upload DNA File 2", type=["txt", "csv", "tsv", "vcf"], key="fam_file2")
        format2 = st.selectbox("Format 2", ["AncestryDNA", "23andMe", "MyHeritage", "LivingDNA", "VCF"], key="fam_fmt2")
        
    if file1 and file2:
        if st.button("Compare Profiles", type="primary"):
            try:
                with st.spinner("Parsing files and analyzing..."):
                    # Parse files
                    df1 = parse_dna_file(file1, format1)
                    df1 = df1.set_index("rsid")
                    
                    df2 = parse_dna_file(file2, format2)
                    df2 = df2.set_index("rsid")
                    
                    # Analyze
                    analyzer = FamilyAnalyzer(df1, df2, label1="Person 1", label2="Person 2")
                    
                    ibs = analyzer.calculate_identity_by_state()
                    prediction = analyzer.predict_relationship(ibs)
                    mendelian = analyzer.analyze_mendelian_errors()
                    
                    # Display Results
                    st.success("Analysis Complete!")
                    
                    st.metric("Shared DNA (IBS Score)", f"{ibs:.2%}")
                    st.info(f"Predicted Relationship: **{prediction}**")
                    
                    with st.expander("Mendelian Inheritance Details (Parent-Child Check)"):
                        st.write("Assuming Person 1 is Parent and Person 2 is Child (or vice versa):")
                        st.write(f"Total SNPs Compared: {mendelian['total_comparisons']}")
                        st.write(f"Mendelian Errors: {mendelian['mendelian_errors']}")
                        st.write(f"Error Rate: {mendelian['error_rate']:.4%}")
                        
                        if mendelian['is_parent_child']:
                            st.success("✅ Low error rate consistent with Parent-Child relationship.")
                        else:
                            st.warning("⚠️ High error rate. Unlikely to be a direct Parent-Child relationship (or high genotyping error).")
                            
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
    else:
        st.info("Please upload both files to run the comparison.")
