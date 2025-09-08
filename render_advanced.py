import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from local_data_utils import get_gene_info_local, get_snp_info_local, get_population_frequencies_local, local_data
from bioinformatics_utils import analyze_genotype_quality, predict_functional_impact, calculate_maf

def render_advanced_analytics(dna_data):
    st.header("Module 5: Advanced Analytics & Exploration Tools")
    st.write("This module provides powerful tools for 'citizen scientists' to explore their data.")

    st.subheader("5.1. Interactive Chromosome Explorer")

    # Convert chromosome to numeric for sorting, coercing errors to NaN
    dna_data_reset = dna_data.reset_index()
    dna_data_reset['chromosome_numeric'] = pd.to_numeric(dna_data_reset['chromosome'], errors='coerce')

    # Include X, Y, MT by assigning numbers
    chrom_map = {'X': 23, 'Y': 24, 'MT': 25}
    dna_data_reset['chromosome_numeric'] = dna_data_reset['chromosome_numeric'].fillna(dna_data_reset['chromosome'].map(chrom_map))

    # Drop any remaining NaN
    dna_data_numeric = dna_data_reset.dropna(subset=['chromosome_numeric'])
    dna_data_numeric['chromosome_numeric'] = dna_data_numeric['chromosome_numeric'].astype(int)

    chrom_options = sorted(dna_data_numeric['chromosome'].unique())
    chrom = st.selectbox("Select chromosome to explore", chrom_options, index=0 if '1' in chrom_options else 0)

    dna_data_filtered = dna_data_numeric[dna_data_numeric['chromosome'] == chrom]

    if not dna_data_filtered.empty:
        fig = px.scatter(dna_data_filtered, x="position", y=[0]*len(dna_data_filtered),
                          hover_data=["rsid", "genotype"],
                          title=f"Interactive Explorer for Chromosome {chrom}",
                          labels={"position": "Position"})
        fig.update_yaxes(showticklabels=False, title="")
        st.plotly_chart(fig)
    else:
        st.warning(f"No data available for chromosome {chrom}.")

    st.subheader("5.2. Global Population Frequency Viewer")
    rsid_input = st.text_input("Enter an rsID to view population frequencies (e.g., 'rs1801133')")

    if st.button("Get Population Frequencies"):
        if rsid_input:
            with st.spinner("Loading population frequency data..."):
                population_df = get_population_frequencies_local(rsid_input)

            if population_df is not None and not population_df.empty:
                st.success(f"Population frequencies for {rsid_input}:")
                fig = px.bar(population_df, x="population", y="frequency", color="allele",
                              title=f"Allele Frequencies for {rsid_input} Across Populations")
                st.plotly_chart(fig)
            else:
                st.warning(f"No population frequency data found for {rsid_input}.")
        else:
            st.warning("Please enter an rsID.")

    st.subheader("5.3. Advanced SNP Analysis")

    # Functional impact prediction
    snp_impact = st.text_input("Enter an rsID for functional impact analysis (e.g., 'rs1801133')", key="snp_impact")

    if st.button("Analyze Functional Impact"):
        if snp_impact:
            with st.spinner("Analyzing functional impact..."):
                # Get SNP info from local data
                snp_info = get_snp_info_local(snp_impact)

                if snp_info:
                    # Get user's genotype for this SNP
                    user_genotype = dna_data[dna_data.index == snp_impact]
                    if not user_genotype.empty:
                        genotype = user_genotype.iloc[0]['genotype']

                        # Analyze genotype quality
                        quality_analysis = analyze_genotype_quality(genotype)

                        # Predict functional impact
                        impact_analysis = predict_functional_impact(
                            snp_impact, genotype, snp_info['gene']
                        )

                        st.success(f"Functional Impact Analysis for {snp_impact}:")

                        col1, col2 = st.columns(2)

                        with col1:
                            st.write("**Genotype Analysis:**")
                            st.write(f"**Your Genotype:** {genotype}")
                            st.write(f"**Zygosity:** {quality_analysis['zygosity']}")
                            st.write(f"**Alleles:** {', '.join(quality_analysis['alleles'])}")

                        with col2:
                            st.write("**Functional Impact:**")
                            st.write(f"**Predicted Impact:** {impact_analysis['predicted_impact']}")

                            # Show specific predictions based on impact type
                            if 'activity_level' in impact_analysis:
                                st.write(f"**Enzyme Activity:** {impact_analysis['activity_level']}")
                            if 'lactase_status' in impact_analysis:
                                st.write(f"**Lactase Status:** {impact_analysis['lactase_status']}")
                            if 'metabolism_type' in impact_analysis:
                                st.write(f"**Metabolism Type:** {impact_analysis['metabolism_type']}")

                        # Show population frequencies
                        pop_freq = get_population_frequencies_local(snp_impact)
                        if pop_freq is not None:
                            st.write("**Population Frequencies:**")
                            fig = px.bar(pop_freq, x="population", y="frequency", color="allele",
                                       title=f"Allele Frequencies for {snp_impact} Across Populations")
                            st.plotly_chart(fig)
                    else:
                        st.warning(f"Your genotype data does not contain {snp_impact}.")
                else:
                    st.warning(f"No information found for SNP {snp_impact}.")
        else:
            st.warning("Please enter an rsID.")

    st.subheader("5.4. Enhanced Research Portal")

    col1, col2 = st.columns([2, 1])

    with col1:
        search_term = st.text_input("Search for a gene or SNP on PubMed (e.g., 'BRCA1', 'rs6983267')")

    with col2:
        max_results = st.selectbox("Max results", [5, 10, 20, 50], index=1)

    search_type = st.radio("Search type", ["General", "Recent (last 5 years)", "Review articles", "Clinical trials"], horizontal=True)

    if st.button("Search PubMed"):
        if search_term:
            with st.spinner("Searching PubMed..."):
                # Build search query based on type
                if search_type == "Recent (last 5 years)":
                    full_query = f"{search_term} AND (2020:2025[dp])"
                elif search_type == "Review articles":
                    full_query = f"{search_term} AND review[pt]"
                elif search_type == "Clinical trials":
                    full_query = f"{search_term} AND clinical trial[pt]"
                else:
                    full_query = search_term

                # Search for articles
                search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                search_params = {
                    "db": "pubmed",
                    "term": full_query,
                    "retmode": "json",
                    "retmax": max_results,
                    "retmin": 0,
                    "sort": "relevance"
                }

                try:
                    search_response = requests.get(search_url, params=search_params)
                    search_response.raise_for_status()
                    search_data = search_response.json()
                    ids = search_data['esearchresult']['idlist']

                    if ids:
                        st.success(f"Found {len(ids)} articles for '{search_term}'")

                        # Fetch detailed information for each article
                        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                        fetch_params = {
                            "db": "pubmed",
                            "id": ",".join(ids),
                            "retmode": "json"
                        }

                        fetch_response = requests.get(fetch_url, params=fetch_params)
                        fetch_response.raise_for_status()
                        fetch_data = fetch_response.json()

                        # Display results
                        for i, pubmed_id in enumerate(ids[:max_results]):
                            if pubmed_id in fetch_data['result']:
                                article = fetch_data['result'][pubmed_id]

                                title = article.get('title', 'No title available')
                                authors = article.get('authors', [])
                                author_names = []
                                if authors:
                                    for author in authors[:3]:  # Show first 3 authors
                                        if 'name' in author:
                                            author_names.append(author['name'])
                                    if len(authors) > 3:
                                        author_names.append("et al.")

                                journal = article.get('source', 'Unknown journal')
                                pub_date = article.get('pubdate', 'Unknown date')

                                with st.expander(f"📄 {title[:80]}..."):
                                    st.write(f"**Authors:** {', '.join(author_names) if author_names else 'Unknown'}")
                                    st.write(f"**Journal:** {journal}")
                                    st.write(f"**Publication Date:** {pub_date}")
                                    st.write(f"**PMID:** {pubmed_id}")
                                    st.markdown(f"[🔗 View on PubMed](https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/)")

                                    # Show abstract if available
                                    if 'abstract' in article and article['abstract']:
                                        st.write("**Abstract:**")
                                        st.write(article['abstract'][:300] + "..." if len(article['abstract']) > 300 else article['abstract'])
                    else:
                        st.warning(f"No articles found for '{search_term}'. Try different search terms or check spelling.")

                except requests.exceptions.RequestException as e:
                    st.error(f"An error occurred while searching PubMed: {e}")
        else:
            st.warning("Please enter a search term.")