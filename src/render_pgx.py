import streamlit as st
import pandas as pd
from snp_data import pgx_snps, adverse_reaction_snps, star_allele_definitions, cpic_guidelines
from pgx_star_alleles import star_caller, detect_cnv
from api_functions import get_pharmgkb_data, get_api_health_status

def render_pharmacogenomics(dna_data):
    st.header("Module 2: Pharmacogenomics (PGx) Report")
    st.write("This module provides comprehensive insights into potential responses to common medications using both basic SNP analysis and advanced star allele calling.")

    # Star Allele Analysis Section
    st.subheader("2.1. Star Allele Genotyping & Metabolizer Status")
    st.write("Advanced analysis using CPIC-compliant star allele calling for accurate pharmacogenomic predictions.")

    if st.button("Run Star Allele Analysis"):
        star_results = []

        # Genes to analyze with star alleles
        star_genes = ['CYP2C19', 'CYP2D6', 'CYP2C9', 'TPMT', 'DPYD']

        for gene in star_genes:
            try:
                allele_result = star_caller.call_star_alleles(gene, dna_data)

                if 'error' not in allele_result:
                    # Get CPIC recommendations
                    recommendations = star_caller.get_cpic_recommendations(
                        gene, allele_result['metabolizer_status']
                    )

                    # Check for CNV
                    cnv_status = detect_cnv(gene, dna_data)

                    # Add warning indicator if haplotype data is incomplete
                    completeness = allele_result.get('haplotype_completeness', 1.0)
                    warning_indicator = "⚠️" if completeness < 0.5 else ""

                    metabolizer_display = f"{allele_result['metabolizer_status']}{warning_indicator}"

                    star_results.append({
                        'Gene': gene,
                        'Star Allele Genotype': allele_result['genotype'],
                        'Metabolizer Status': metabolizer_display,
                        'Function': allele_result['function'],
                        'CNV Status': cnv_status if cnv_status else 'None detected',
                        'Data Completeness': '.1%',
                        'Key Drugs': ', '.join(list(recommendations.keys())[:3])  # Show first 3 drugs
                    })
                else:
                    star_results.append({
                        'Gene': gene,
                        'Star Allele Genotype': allele_result['error'],
                        'Metabolizer Status': 'Unable to determine',
                        'Function': 'Unknown',
                        'CNV Status': 'Unknown',
                        'Data Completeness': 'N/A',
                        'Key Drugs': 'N/A'
                    })

            except Exception as e:
                star_results.append({
                    'Gene': gene,
                    'Star Allele Genotype': f'Error: {str(e)}',
                    'Metabolizer Status': 'Error',
                    'Function': 'Error',
                    'CNV Status': 'Error',
                    'Key Drugs': 'N/A'
                })

        if star_results:
            star_df = pd.DataFrame(star_results)
            st.dataframe(star_df.set_index('Gene'))

            # Display detailed CPIC recommendations
            st.subheader("CPIC Dosing Recommendations")
            for result in star_results:
                if result['Metabolizer Status'] != 'Unknown' and result['Metabolizer Status'] != 'Error':
                    with st.expander(f"{result['Gene']} - {result['Metabolizer Status']}"):
                        gene = result['Gene']
                        status = result['Metabolizer Status']
                        recommendations = star_caller.get_cpic_recommendations(gene, status)

                        for drug, recommendation in recommendations.items():
                            st.write(f"**{drug.title()}:** {recommendation}")

    # Basic SNP Analysis Section (backward compatibility)
    st.subheader("2.2. Basic SNP Analysis")
    st.write("Traditional single-SNP analysis for additional pharmacogenomic markers.")

    # API Health Status
    health_status = get_api_health_status()
    pharmgkb_status = health_status.get('pharmgkb', {}).get('status', 'unknown')

    if pharmgkb_status == 'healthy':
        st.success("✅ PharmGKB API is online and responding")
    elif pharmgkb_status == 'unhealthy':
        st.warning("⚠️ PharmGKB API is currently unavailable - using local data only")
    else:
        st.info("🔄 Checking PharmGKB API status...")

    # Data source selection
    data_source = st.radio(
        "Data Source:",
        ["Live PharmGKB API + Local", "Local Data Only"],
        index=0 if pharmgkb_status == 'healthy' else 1,
        key="pharmgkb_data_source"
    )

    use_live_data = data_source == "Live PharmGKB API + Local"

    if st.button("Run Basic SNP Analysis"):
        with st.spinner("Analyzing pharmacogenomic variants..."):
            results = []

            # Get rsIDs to check
            rsids_to_check = list(pgx_snps.keys())

            # Get live PharmGKB data if available
            live_pharmgkb_data = None
            if use_live_data and pharmgkb_status == 'healthy':
                try:
                    live_pharmgkb_data = get_pharmgkb_data(rsids_to_check, use_cache=True)
                except Exception as e:
                    st.warning(f"Could not fetch live PharmGKB data: {e}")

            for rsid, info in pgx_snps.items():
                user_genotype = dna_data[dna_data.index == rsid]
                interpretation = 'Not in data'
                genotype = 'Not in data'
                data_sources = []

                if not user_genotype.empty:
                    genotype = user_genotype.iloc[0]['genotype']
                    sorted_genotype = "".join(sorted(genotype))
                    if sorted_genotype in info['interp']:
                        interpretation = info['interp'][sorted_genotype]
                        data_sources.append('Local')

                    # Add live PharmGKB data if available
                    if live_pharmgkb_data and rsid in live_pharmgkb_data:
                        live_info = live_pharmgkb_data[rsid]
                        if live_info and "No significant" not in live_info:
                            interpretation += f" | Live PharmGKB: {live_info}"
                            data_sources.append('Live PharmGKB API')

                results.append({
                    'rsID': rsid,
                    'Gene/Locus': info['gene'],
                    'Relevance': info['relevance'],
                    'Genotype': genotype,
                    'Interpretation': interpretation,
                    'Data Sources': ', '.join(data_sources) if data_sources else 'None'
                })

            pgx_df = pd.DataFrame(results).set_index('rsID')
            st.dataframe(pgx_df)

            # Show data source summary
            if live_pharmgkb_data:
                st.info(f"✅ Integrated data from {len([r for r in results if 'Live PharmGKB' in r['Data Sources']])} PharmGKB variants")

    # Adverse Drug Reaction Section
    st.subheader("2.3. Adverse Drug Reaction Sensitivity")
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

    # Educational Information
    st.subheader("Understanding Your Results")
    st.info("""
    **Metabolizer Status Categories:**
    - **Poor Metabolizer**: Two no-function alleles - significantly reduced drug metabolism
    - **Intermediate Metabolizer**: One no-function allele - moderately reduced metabolism
    - **Normal Metabolizer**: Two normal function alleles - standard metabolism
    - **Rapid/Ultrarapid Metabolizer**: Increased function alleles - enhanced metabolism

    **Clinical Action:**
    - Always consult with a healthcare provider before making medication changes
    - Share these results with your pharmacist or prescribing physician
    - CPIC guidelines provide evidence-based dosing recommendations
    """)