import requests
import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st
from utils import api_call_with_retry

def get_clinvar_data(rsids):
    """
    Fetches and parses ClinVar data for a list of rsIDs.
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    db = "clinvar"

    # Join the rsids into a single string
    id_list = ",".join(rsids)

    params = {
        "db": db,
        "id": id_list,
        "rettype": "vcv",
        "retmode": "xml"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse the XML response
        root = ET.fromstring(response.content)

        results = {}

        for variation_archive in root.findall('.//VariationArchive'):
            rsid = variation_archive.get('VariationName')

            clinical_assertion = variation_archive.find('.//ClinicalAssertion/ClinicalSignificance/Description')
            if clinical_assertion is not None:
                results[rsid] = clinical_assertion.text

        return results

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while fetching data from ClinVar: {e}")
        return None
    except ET.ParseError as e:
        st.error(f"Error parsing XML from ClinVar: {e}")
        return None

def get_pharmgkb_data(rsids):
    """
    Fetches and parses PharmGKB data for a list of rsIDs.
    """
    base_url = "https://api.pharmgkb.org/v1/data/"
    results = {}

    for rsid in rsids:
        try:
            # Query for clinical annotations related to the variant
            response = requests.get(f"{base_url}clinicalAnnotation?location.name={rsid}")
            response.raise_for_status()
            data = response.json()

            if data['data']:
                annotations = []
                for annotation in data['data']:
                    drug = annotation.get('relatedChemicals', [{}])[0].get('name', 'N/A')
                    phenotype = annotation.get('phenotype', {}).get('name', 'N/A')
                    annotations.append(f"Drug: {drug}, Phenotype: {phenotype}")
                results[rsid] = "; ".join(annotations)
            else:
                results[rsid] = "No significant clinical annotations found."

        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred while fetching data from PharmGKB for {rsid}: {e}")
            results[rsid] = "Error fetching data."
        except Exception as e:
            st.error(f"An unexpected error occurred for {rsid}: {e}")
            results[rsid] = "An unexpected error occurred."

    return results

@api_call_with_retry()
def get_pgs_catalog_data(trait):
    """
    Fetches and parses PGS Catalog data for a given trait.
    """
    base_url = "https://www.pgscatalog.org/rest/score/search"
    params = {"trait": trait}

    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("results", [])

@api_call_with_retry()
def get_pgs_model_data(pgs_id):
    """
    Fetches detailed PGS model data including rsIDs, effect alleles, and weights.
    """
    base_url = f"https://www.pgscatalog.org/rest/score/{pgs_id}"

    response = requests.get(base_url)
    response.raise_for_status()
    data = response.json()

    # Extract scoring file URL
    if 'ftp_scoring_file' in data:
        scoring_url = data['ftp_scoring_file']
        # Download and parse the scoring file
        scoring_response = requests.get(scoring_url)
        scoring_response.raise_for_status()

        # Parse TSV content
        lines = scoring_response.text.strip().split('\n')
        header = lines[0].split('\t')

        rsids = []
        effect_alleles = []
        effect_weights = []

        for line in lines[1:]:
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 4:  # rsID, chr, pos, effect_allele, effect_weight
                    rsids.append(parts[0])
                    effect_alleles.append(parts[3])
                    effect_weights.append(float(parts[4]))

        return {
            'rsid': rsids,
            'effect_allele': effect_alleles,
            'effect_weight': effect_weights
        }
    else:
        st.warning(f"No scoring file found for PGS ID {pgs_id}")
        return None

@api_call_with_retry()
def get_gnomad_population_data(rsid):
    """
    Fetches population frequency data for a given rsID from gnoAD using REST API.
    """
    # Try the REST API first
    rest_url = f"https://gnomad.broadinstitute.org/api/v2/variants/{rsid}"

    try:
        response = requests.get(rest_url)
        response.raise_for_status()
        data = response.json()

        population_data = []

        # Global frequencies
        if 'exome' in data:
            exome = data['exome']
            if exome.get('an', 0) > 0:
                population_data.append({
                    "Population": "Global (Exome)",
                    "Allele": data.get('alt', 'ALT'),
                    "Frequency": exome.get('af', 0)
                })

        if 'genome' in data:
            genome = data['genome']
            if genome.get('an', 0) > 0:
                population_data.append({
                    "Population": "Global (Genome)",
                    "Allele": data.get('alt', 'ALT'),
                    "Frequency": genome.get('af', 0)
                })

        # Population-specific frequencies
        if 'populations' in data:
            for pop in data['populations']:
                if pop.get('an', 0) > 0:
                    population_data.append({
                        "Population": pop['id'],
                        "Allele": data.get('alt', 'ALT'),
                        "Frequency": pop.get('af', 0)
                    })

        if population_data:
            return pd.DataFrame(population_data)

    except requests.exceptions.RequestException:
        pass  # Fall back to GraphQL

    # Fallback to GraphQL API
    base_url = "https://gnomad.broadinstitute.org/api"
    query = """
    query GetVariant($variantId: String!) {
      variant(variantId: $variantId, dataset: gnomad_r4) {
        variantId
        chrom
        pos
        ref
        alt
        exome {
          ac
          an
        }
        genome {
          ac
          an
        }
        populations {
          id
          ac
          an
        }
      }
    }
    """

    response = requests.post(base_url, json={"query": query, "variables": {"variantId": rsid}})
    response.raise_for_status()
    data = response.json()

    if 'data' in data and 'variant' in data['data'] and data['data']['variant']:
        variant = data['data']['variant']
        population_data = []

        # Global frequencies
        if variant.get('exome'):
            exome_ac = variant['exome']['ac']
            exome_an = variant['exome']['an']
            if exome_an > 0:
                population_data.append({
                    "Population": "Global (Exome)",
                    "Allele": variant['alt'],
                    "Frequency": exome_ac / exome_an
                })

        if variant.get('genome'):
            genome_ac = variant['genome']['ac']
            genome_an = variant['genome']['an']
            if genome_an > 0:
                population_data.append({
                    "Population": "Global (Genome)",
                    "Allele": variant['alt'],
                    "Frequency": genome_ac / genome_an
                })

        # Population-specific frequencies
        if variant.get('populations'):
            for pop in variant['populations']:
                if pop['an'] > 0:
                    population_data.append({
                        "Population": pop['id'],
                        "Allele": variant['alt'],
                        "Frequency": pop['ac'] / pop['an']
                    })

        return pd.DataFrame(population_data)
    else:
        st.warning(f"No gnoAD data found for {rsid}")
        return None
