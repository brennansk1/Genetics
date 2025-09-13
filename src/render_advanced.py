import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from local_data_utils import get_gene_info_local, get_snp_info_local, get_population_frequencies_local, local_data
from bioinformatics_utils import (
    analyze_genotype_quality, predict_functional_impact, calculate_maf,
    analyze_ld_patterns, identify_compound_heterozygotes, calculate_genetic_distance,
    extract_sequence_context, analyze_snp_conservation
)
from snp_data import recessive_snps, cancer_snps, cardiovascular_snps, neuro_snps, mito_snps
from api_functions import search_pubmed, get_pubmed_abstract, get_gnomad_population_data, get_api_health_status
import numpy as np

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

    # API Health Status
    health_status = get_api_health_status()
    pubmed_status = health_status.get('pubmed', {}).get('status', 'unknown')

    if pubmed_status == 'healthy':
        st.success("✅ PubMed API is online and responding")
    elif pubmed_status == 'unhealthy':
        st.warning("⚠️ PubMed API is currently unavailable - using local fallback")
    else:
        st.info("🔄 Checking PubMed API status...")

    col1, col2 = st.columns([2, 1])

    with col1:
        search_term = st.text_input("Search for a gene or SNP on PubMed (e.g., 'BRCA1', 'rs6983267')")

    with col2:
        max_results = st.selectbox("Max results", [5, 10, 20, 50], index=1)

    search_type = st.radio("Search type", ["General", "Recent (last 5 years)", "Review articles", "Clinical trials"], horizontal=True)

    # Data source selection
    data_source = st.radio(
        "Data Source:",
        ["Live PubMed API (Recommended)", "Local Data Only"],
        index=0 if pubmed_status == 'healthy' else 1,
        key="pubmed_data_source"
    )

    use_live_data = data_source == "Live PubMed API (Recommended)"

    if st.button("Search PubMed"):
        if search_term:
            with st.spinner("Searching PubMed..."):
                try:
                    if use_live_data and pubmed_status == 'healthy':
                        # Use enhanced PubMed search
                        articles = search_pubmed(
                            query=search_term,
                            max_results=max_results,
                            search_type=search_type.lower().replace(" (last 5 years)", "").replace(" articles", "").replace(" trials", ""),
                            use_cache=True
                        )

                        if articles:
                            st.success(f"Found {len(articles)} articles for '{search_term}' (Live PubMed API)")

                            # Display results
                            for article in articles:
                                title = article.get('title', 'No title available')
                                authors_formatted = article.get('authors_formatted', 'Unknown')
                                journal = article.get('journal', 'Unknown journal')
                                pub_date = article.get('pub_date', 'Unknown date')
                                pmid = article.get('pmid', 'Unknown')

                                with st.expander(f"📄 {title[:80]}..."):
                                    st.write(f"**Authors:** {authors_formatted}")
                                    st.write(f"**Journal:** {journal}")
                                    st.write(f"**Publication Date:** {pub_date}")
                                    st.write(f"**PMID:** {pmid}")
                                    st.markdown(f"[🔗 View on PubMed]({article.get('url', '#')})")

                                    # Show abstract if available
                                    abstract = article.get('abstract', '')
                                    if abstract:
                                        st.write("**Abstract:**")
                                        st.write(abstract[:300] + "..." if len(abstract) > 300 else abstract)

                                    # Option to fetch full abstract
                                    if st.button(f"Load full abstract for PMID {pmid}", key=f"abstract_{pmid}"):
                                        with st.spinner("Fetching full abstract..."):
                                            full_article = get_pubmed_abstract(pmid, use_cache=True)
                                            if full_article and full_article.get('abstract'):
                                                st.write("**Full Abstract:**")
                                                st.write(full_article['abstract'])
                        else:
                            st.warning(f"No articles found for '{search_term}'. Try different search terms or check spelling.")

                    else:
                        # Fallback to local/manual search
                        st.info("Using local search capabilities...")
                        st.warning("Live PubMed search is currently unavailable. Please try again later or use the live API when available.")

                except Exception as e:
                    st.error(f"An error occurred while searching PubMed: {e}")
                    st.info("Try switching to local data source or contact support.")
        else:
            st.warning("Please enter a search term.")

    st.subheader("6.1. Compound Heterozygote Detection")
    st.write("**Educational Note:** Compound heterozygotes occur when an individual inherits two different disease-causing variants in the same gene, one from each parent. This analysis helps identify potential recessive conditions.")

    # Gene selection for compound het analysis
    gene_options = list(recessive_snps.keys()) + list(cancer_snps.keys()) + list(cardiovascular_snps.keys())
    selected_gene = st.selectbox("Select gene for compound heterozygote analysis", gene_options, key="compound_het_gene")

    if st.button("Analyze Compound Heterozygotes"):
        if selected_gene:
            with st.spinner("Analyzing compound heterozygous patterns..."):
                # Get SNPs for the selected gene
                gene_snps = {}
                if selected_gene in recessive_snps:
                    gene_snps[selected_gene] = [selected_gene]  # Simplified for demo
                elif selected_gene in cancer_snps:
                    gene_snps[selected_gene] = [selected_gene]
                elif selected_gene in cardiovascular_snps:
                    gene_snps[selected_gene] = [selected_gene]

                # Get user's genotypes for these SNPs
                genotypes = {}
                for snp in gene_snps.get(selected_gene, []):
                    if snp in dna_data.index:
                        genotypes[snp] = dna_data.loc[snp, 'genotype']

                if genotypes:
                    compound_het_results = identify_compound_heterozygotes(gene_snps, genotypes)

                    if compound_het_results:
                        st.success(f"Found compound heterozygous patterns in {len(compound_het_results)} gene(s):")
                        for gene, het_snps in compound_het_results.items():
                            with st.expander(f"Compound Heterozygotes in {gene}"):
                                st.write(f"**Heterozygous SNPs:** {', '.join(het_snps)}")
                                st.write(f"**Pattern:** Individual carries different variants on each chromosome")
                                st.write("**Clinical Significance:** May indicate carrier status for recessive conditions")
                    else:
                        st.info("No compound heterozygous patterns detected in the selected gene.")
                else:
                    st.warning(f"No genotype data available for SNPs in {selected_gene}.")
        else:
            st.warning("Please select a gene.")

    st.subheader("6.2. Linkage Disequilibrium (LD) Analysis")
    st.write("**Educational Note:** Linkage disequilibrium measures how often genetic variants are inherited together. High LD indicates variants are linked and tend to be inherited as a block.")

    # SNP selection for LD analysis
    ld_snp_input = st.text_input("Enter comma-separated rsIDs for LD analysis (e.g., rs1801133,rs4988235)", key="ld_snps")

    if st.button("Analyze LD Patterns"):
        if ld_snp_input:
            snp_list = [s.strip() for s in ld_snp_input.split(',') if s.strip()]

            with st.spinner("Analyzing linkage disequilibrium patterns..."):
                # Get genotypes for selected SNPs
                genotypes = {}
                for snp in snp_list:
                    if snp in dna_data.index:
                        genotypes[snp] = dna_data.loc[snp, 'genotype']

                if len(genotypes) >= 2:
                    ld_results = analyze_ld_patterns(snp_list, genotypes)

                    if ld_results:
                        st.success("LD Analysis Results:")
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write("**Haplotype Frequencies:**")
                            if 'haplotypes' in ld_results:
                                for haplotype, freq in ld_results['haplotypes'].items():
                                    st.write(f"- {haplotype}: {freq} occurrences")

                        with col2:
                            if 'most_common_haplotype' in ld_results:
                                st.write(f"**Most Common Haplotype:** {ld_results['most_common_haplotype']}")
                                st.write("**Interpretation:** High frequency haplotypes may indicate conserved genetic blocks")

                        # Simple LD heatmap visualization
                        st.write("**LD Pattern Visualization:**")
                        haplotype_data = ld_results.get('haplotypes', {})
                        if haplotype_data:
                            fig = px.bar(
                                x=list(haplotype_data.keys()),
                                y=list(haplotype_data.values()),
                                title="Haplotype Frequency Distribution",
                                labels={'x': 'Haplotype', 'y': 'Frequency'}
                            )
                            st.plotly_chart(fig)
                    else:
                        st.info("No significant LD patterns detected.")
                else:
                    st.warning("Need at least 2 SNPs with genotype data for LD analysis.")
        else:
            st.warning("Please enter SNP rsIDs.")

    st.subheader("6.3. Sequence Context Analysis")
    st.write("**Educational Note:** Sequence context around genetic variants can influence their functional impact and conservation across species.")

    seq_snp_input = st.text_input("Enter rsID for sequence context analysis", key="seq_context_snp")
    flank_size = st.slider("Flanking sequence size (bp)", 10, 100, 50)

    if st.button("Analyze Sequence Context"):
        if seq_snp_input:
            with st.spinner("Extracting sequence context..."):
                # Get SNP position from local data
                snp_info = get_snp_info_local(seq_snp_input)

                if snp_info:
                    chromosome = snp_info['chromosome']
                    position = snp_info['position']

                    # Extract sequence context
                    context = extract_sequence_context(chromosome, position, flank_size)

                    if context:
                        st.success(f"Sequence context for {seq_snp_input}:")

                        # Display sequence with variant highlighted
                        variant_pos = flank_size
                        seq_before = context[:variant_pos]
                        variant_base = context[variant_pos] if variant_pos < len(context) else 'N'
                        seq_after = context[variant_pos+1:] if variant_pos+1 < len(context) else ''

                        st.code(f"{seq_before}[{variant_base}]{seq_after}", language="text")

                        # Conservation analysis
                        conservation = analyze_snp_conservation(chromosome, position)
                        if conservation:
                            col1, col2 = st.columns(2)

                            with col1:
                                st.write("**GC Content:**")
                                st.write(f"{conservation.get('gc_content', 'N/A'):.2%}")

                            with col2:
                                st.write("**Conservation Score:**")
                                st.write(conservation.get('conservation_score', 'Unknown'))

                            if conservation.get('conservation_score') == 'high':
                                st.info("High conservation suggests functional importance")
                            elif conservation.get('conservation_score') == 'moderate':
                                st.info("Moderate conservation - may have functional role")
                            else:
                                st.info("Low conservation - likely neutral variant")
                    else:
                        st.warning("Could not extract sequence context. Reference genome may not be available.")
                else:
                    st.warning(f"No position information found for {seq_snp_input}.")
        else:
            st.warning("Please enter an rsID.")

    st.subheader("6.4. Genetic Distance Calculator")
    st.write("**Educational Note:** Genetic distance measures physical separation between genetic variants, which can influence inheritance patterns and recombination.")

    col1, col2 = st.columns(2)

    with col1:
        pos1_input = st.text_input("Enter first rsID or position", key="pos1")
        chromosome = st.selectbox("Chromosome", [str(i) for i in range(1, 23)] + ['X', 'Y', 'MT'], key="chromosome")

    with col2:
        pos2_input = st.text_input("Enter second rsID or position", key="pos2")

    if st.button("Calculate Genetic Distance"):
        positions = []

        for pos_input in [pos1_input, pos2_input]:
            if pos_input.startswith('rs'):
                # Get position from SNP data
                snp_info = get_snp_info_local(pos_input)
                if snp_info:
                    positions.append(snp_info['position'])
                else:
                    st.error(f"Could not find position for {pos_input}")
                    positions = []
                    break
            else:
                # Direct position input
                try:
                    positions.append(int(pos_input))
                except ValueError:
                    st.error(f"Invalid position: {pos_input}")
                    positions = []
                    break

        if len(positions) == 2:
            distance = calculate_genetic_distance(positions[0], positions[1], chromosome)

            st.success("Genetic Distance Results:")
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Physical Distance", f"{distance:,} bp")

            with col2:
                # Rough centimorgan conversion (1 cM ≈ 1 Mb)
                cm_distance = distance / 1000000
                st.metric("Approximate cM", f"{cm_distance:.2f}")

            # Interpretation
            if distance < 1000:
                st.info("Very close variants - likely inherited together")
            elif distance < 100000:
                st.info("Close variants - may show linkage")
            elif distance < 1000000:
                st.info("Moderate distance - recombination possible")
            else:
                st.info("Distant variants - independent inheritance likely")
        else:
            st.warning("Please provide valid positions or rsIDs.")

    st.subheader("6.5. Enhanced Functional Impact Analysis")
    st.write("**Educational Note:** Functional impact analysis predicts how genetic variants may affect protein function, gene expression, or disease risk.")

    # Enhanced version of existing 5.3 section
    impact_snp = st.text_input("Enter rsID for enhanced functional impact analysis", key="enhanced_impact")

    if st.button("Analyze Enhanced Functional Impact"):
        if impact_snp:
            with st.spinner("Performing comprehensive functional impact analysis..."):
                # Get SNP info
                snp_info = get_snp_info_local(impact_snp)

                if snp_info:
                    # Get user genotype
                    user_genotype = dna_data[dna_data.index == impact_snp]
                    if not user_genotype.empty:
                        genotype = user_genotype.iloc[0]['genotype']

                        # Multiple analysis layers
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.write("**Genotype Analysis:**")
                            quality_analysis = analyze_genotype_quality(genotype)
                            st.write(f"**Your Genotype:** {genotype}")
                            st.write(f"**Zygosity:** {quality_analysis['zygosity']}")
                            st.write(f"**Alleles:** {', '.join(quality_analysis['alleles'])}")

                        with col2:
                            st.write("**Functional Impact:**")
                            impact_analysis = predict_functional_impact(impact_snp, genotype, snp_info.get('gene', ''))
                            st.write(f"**Predicted Impact:** {impact_analysis['predicted_impact']}")

                            # Show specific predictions
                            for key, value in impact_analysis.items():
                                if key not in ['rsid', 'genotype', 'gene', 'predicted_impact']:
                                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")

                        with col3:
                            st.write("**Conservation & Context:**")
                            conservation = analyze_snp_conservation(snp_info['chromosome'], snp_info['position'])
                            if conservation:
                                st.write(f"**Conservation:** {conservation.get('conservation_score', 'Unknown')}")
                                if 'gc_content' in conservation:
                                    st.write(f"**GC Content:** {conservation['gc_content']:.1%}")

                        # Population comparison
                        pop_freq = get_population_frequencies_local(impact_snp)
                        if pop_freq is not None:
                            st.write("**Population Frequency Comparison:**")
                            fig = px.bar(pop_freq, x="population", y="frequency", color="allele",
                                       title=f"Population Frequencies for {impact_snp}")
                            st.plotly_chart(fig)

                            # Compare user's allele frequency
                            user_alleles = list(genotype)
                            for allele in set(user_alleles):
                                allele_freq = pop_freq[pop_freq['allele'] == allele]
                                if not allele_freq.empty:
                                    global_freq = allele_freq['frequency'].mean()
                                    st.info(f"Your {allele} allele frequency: {global_freq:.3f} globally")
                    else:
                        st.warning(f"Your genotype data does not contain {impact_snp}.")
                else:
                    st.warning(f"No information found for SNP {impact_snp}.")
        else:
            st.warning("Please enter an rsID.")