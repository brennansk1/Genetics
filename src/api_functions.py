import requests
import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st
from utils import api_call_with_retry
import time
import json
import os
import logging
from functools import lru_cache
from datetime import datetime, timedelta
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global rate limiter and cache manager
class APIRateLimiter:
    """Simple rate limiter for API calls"""

    def __init__(self, calls_per_minute=30):
        self.calls_per_minute = calls_per_minute
        self.call_times = []

    def can_make_call(self):
        """Check if we can make another API call"""
        now = time.time()
        # Remove calls older than 1 minute
        self.call_times = [t for t in self.call_times if now - t < 60]

        return len(self.call_times) < self.calls_per_minute

    def record_call(self):
        """Record that a call was made"""
        self.call_times.append(time.time())

class APICache:
    """Simple file-based cache for API responses"""

    def __init__(self, cache_dir="cache/api", expiry_hours=24):
        self.cache_dir = cache_dir
        self.expiry_hours = expiry_hours
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_key(self, url, params=None):
        """Generate cache key from URL and parameters"""
        key_data = f"{url}_{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, url, params=None):
        """Get cached response if available and not expired"""
        cache_key = self._get_cache_key(url, params)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)

                # Check if cache is expired
                cached_time = datetime.fromisoformat(cached_data['timestamp'])
                if datetime.now() - cached_time < timedelta(hours=self.expiry_hours):
                    return cached_data['data']
                else:
                    # Remove expired cache
                    os.remove(cache_file)
            except (json.JSONDecodeError, KeyError, ValueError):
                # Remove corrupted cache
                if os.path.exists(cache_file):
                    os.remove(cache_file)

        return None

    def set(self, url, params=None, data=None):
        """Cache the response"""
        if data is None:
            return

        cache_key = self._get_cache_key(url, params)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'params': params,
            'data': data
        }

        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
        except Exception:
            # Silently fail if caching fails
            pass

# Global instances
rate_limiter = APIRateLimiter()
api_cache = APICache()

def make_api_request(url, params=None, method='GET', timeout=30, use_cache=True):
    """
    Enhanced API request with caching, rate limiting, and error handling

    Args:
        url: API endpoint URL
        params: Query parameters
        method: HTTP method
        timeout: Request timeout
        use_cache: Whether to use caching

    Returns:
        Response data or None if failed
    """
    # Check cache first
    if use_cache and method == 'GET':
        cached_data = api_cache.get(url, params)
        if cached_data is not None:
            return cached_data

    # Check rate limit
    if not rate_limiter.can_make_call():
        st.warning("API rate limit reached. Please wait before making more requests.")
        return None

    try:
        rate_limiter.record_call()
        logger.info(f"Making {method} request to {url} with params: {params}")

        if method == 'GET':
            response = requests.get(url, params=params, timeout=timeout)
        elif method == 'POST':
            response = requests.post(url, json=params, timeout=timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        logger.info(f"Response status code: {response.status_code}")
        response.raise_for_status()

        # Try to parse JSON
        try:
            data = response.json()
            logger.info(f"Successfully parsed JSON response from {url}")
        except json.JSONDecodeError:
            data = response.text
            logger.info(f"Received text response from {url}: {data[:200]}...")

        # Cache successful responses
        if use_cache and method == 'GET':
            api_cache.set(url, params, data)

        return data

    except requests.exceptions.Timeout:
        logger.error(f"API request timed out for {url}")
        st.error(f"API request timed out for {url}")
        return None
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error for {url}")
        st.error(f"Connection error for {url}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error {response.status_code} for {url}: {e}")
        logger.error(f"Response content: {response.text[:500]}...")
        if response.status_code == 429:
            st.warning("API rate limit exceeded. Please try again later.")
        else:
            st.error(f"HTTP error {response.status_code} for {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error for {url}: {e}")
        st.error(f"Unexpected error for {url}: {e}")
        return None

@api_call_with_retry()
def get_clinvar_data(rsids, use_cache=True):
    """
    Fetches and parses ClinVar data for a list of rsIDs with enhanced error handling and caching.

    Args:
        rsids: List of rsIDs to query
        use_cache: Whether to use cached results

    Returns:
        Dictionary mapping rsIDs to clinical significance or None if failed
    """
    if not rsids:
        return {}

    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    # Join the rsids into a single string
    id_list = ",".join(rsids)

    params = {
        "db": "clinvar",
        "id": id_list,
        "rettype": "vcv",
        "retmode": "xml"
    }

    # Use enhanced API request
    logger.info(f"Fetching ClinVar data for rsIDs: {rsids}")
    response_text = make_api_request(base_url, params, use_cache=use_cache)

    if response_text is None:
        logger.error("ClinVar API request failed")
        return None

    try:
        # Parse the XML response
        logger.info("Parsing ClinVar XML response")
        root = ET.fromstring(response_text)

        results = {}

        for variation_archive in root.findall('.//VariationArchive'):
            rsid = variation_archive.get('VariationName')
            logger.debug(f"Processing ClinVar data for {rsid}")

            clinical_assertion = variation_archive.find('.//ClinicalAssertion/ClinicalSignificance/Description')
            if clinical_assertion is not None:
                results[rsid] = clinical_assertion.text
            else:
                results[rsid] = "Clinical significance not available"

        logger.info(f"Successfully processed ClinVar data for {len(results)} rsIDs")
        return results

    except ET.ParseError as e:
        logger.error(f"Error parsing XML from ClinVar: {e}")
        logger.error(f"Response text: {response_text[:500]}...")
        st.error(f"Error parsing XML from ClinVar: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error processing ClinVar data: {e}")
        st.error(f"Unexpected error processing ClinVar data: {e}")
        return None

@api_call_with_retry()
def get_pharmgkb_data(rsids, use_cache=True):
    """
    Fetches and parses PharmGKB data for a list of rsIDs with enhanced error handling and caching.

    Args:
        rsids: List of rsIDs to query
        use_cache: Whether to use cached results

    Returns:
        Dictionary mapping rsIDs to clinical annotations or None if failed
    """
    if not rsids:
        return {}

    base_url = "https://api.pharmgkb.org/v1/data/clinicalAnnotation"
    results = {}

    for rsid in rsids:
        logger.info(f"Fetching PharmGKB data for {rsid}")
        params = {"location.name": rsid}

        # Use enhanced API request
        data = make_api_request(base_url, params, use_cache=use_cache)

        if data is None:
            logger.error(f"PharmGKB API request failed for {rsid}")
            results[rsid] = "Error fetching data from PharmGKB."
            continue

        try:
            logger.debug(f"Processing PharmGKB response for {rsid}: {data}")
            if 'data' in data and data['data']:
                annotations = []
                for annotation in data['data']:
                    drug = annotation.get('relatedChemicals', [{}])[0].get('name', 'N/A')
                    phenotype = annotation.get('phenotype', {}).get('name', 'N/A')
                    level_of_evidence = annotation.get('levelOfEvidence', {}).get('name', 'N/A')
                    annotations.append(f"Drug: {drug}, Phenotype: {phenotype}, Evidence: {level_of_evidence}")
                results[rsid] = "; ".join(annotations)
                logger.info(f"Found {len(annotations)} annotations for {rsid}")
            else:
                logger.info(f"No significant clinical annotations found for {rsid}")
                results[rsid] = "No significant clinical annotations found."

        except Exception as e:
            logger.error(f"Error processing PharmGKB data for {rsid}: {e}")
            logger.error(f"Response data: {data}")
            st.error(f"Error processing PharmGKB data for {rsid}: {e}")
            results[rsid] = "Error processing data."

    return results

@api_call_with_retry()
def get_pgs_catalog_data(trait, max_results=50):
    """
    Fetches and parses PGS Catalog data for a given trait.

    Args:
        trait: Trait name to search for
        max_results: Maximum number of results to return

    Returns:
        List of PGS model summaries
    """
    base_url = "https://www.pgscatalog.org/rest/score/search"
    params = {
        "trait": trait,
        "limit": max_results
    }

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])

        # Add metadata to each result
        for result in results:
            result['num_variants'] = result.get('variants_number', 0)
            result['genome_build'] = result.get('genome_build', 'Unknown')
            result['ancestry'] = result.get('ancestry', 'Unknown')
            result['trait_reported'] = result.get('trait_reported', trait)

        return results

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch PGS Catalog data for trait '{trait}': {str(e)}")
        return []
    except Exception as e:
        st.error(f"Error processing PGS Catalog data: {str(e)}")
        return []

@api_call_with_retry()
def get_pgs_model_data(pgs_id, include_metadata=True):
    """
    Fetches detailed PGS model data including rsIDs, effect alleles, and weights.

    Args:
        pgs_id: PGS Catalog ID (e.g., 'PGS000001')
        include_metadata: Whether to include full metadata

    Returns:
        Dictionary with model data or None if failed
    """
    base_url = f"https://www.pgscatalog.org/rest/score/{pgs_id}"

    try:
        response = requests.get(base_url, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Extract scoring file URL
        if 'ftp_scoring_file' in data:
            scoring_url = data['ftp_scoring_file']

            # Download and parse the scoring file
            scoring_response = requests.get(scoring_url, timeout=60)
            scoring_response.raise_for_status()

            # Parse TSV content
            lines = scoring_response.text.strip().split('\n')
            if len(lines) < 2:
                st.warning(f"Empty scoring file for PGS ID {pgs_id}")
                return None

            header = lines[0].split('\t')

            rsids = []
            effect_alleles = []
            effect_weights = []
            chromosomes = []
            positions = []
            other_alleles = []

            for line in lines[1:]:
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 5:  # rsID, chr, pos, effect_allele, effect_weight
                        rsids.append(parts[0])
                        chromosomes.append(parts[1] if len(parts) > 1 else 'Unknown')
                        positions.append(int(parts[2]) if len(parts) > 2 else 0)
                        effect_alleles.append(parts[3])
                        effect_weights.append(float(parts[4]))

                        # Store other allele if available
                        if len(parts) > 5:
                            other_alleles.append(parts[5])
                        else:
                            other_alleles.append('Unknown')

            model_data = {
                'pgs_id': pgs_id,
                'rsid': rsids,
                'effect_allele': effect_alleles,
                'effect_weight': effect_weights,
                'chromosome': chromosomes,
                'position': positions,
                'other_allele': other_alleles,
                'num_variants': len(rsids)
            }

            if include_metadata:
                model_data.update({
                    'trait': data.get('trait_reported', 'Unknown'),
                    'genome_build': data.get('genome_build', 'Unknown'),
                    'ancestry': data.get('ancestry', 'Unknown'),
                    'citation': data.get('citation', 'Unknown'),
                    'method_name': data.get('method_name', 'Unknown'),
                    'training_samples': data.get('samples_variants_numbers', {}).get('training', 0),
                    'raw_metadata': data
                })

            return model_data
        else:
            st.warning(f"No scoring file found for PGS ID {pgs_id}")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch PGS model data for {pgs_id}: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error processing PGS model {pgs_id}: {str(e)}")
        return None

@api_call_with_retry()
def search_pgs_models(query, trait_filter=None, max_results=20):
    """
    Search for PGS models with flexible query options.

    Args:
        query: Search query (can be PGS ID, trait, or general term)
        trait_filter: Optional trait filter
        max_results: Maximum results to return

    Returns:
        List of matching PGS models
    """
    # If query looks like a PGS ID, fetch directly
    if query.upper().startswith('PGS'):
        model_data = get_pgs_model_data(query)
        if model_data:
            return [model_data]
        else:
            return []

    # Otherwise, search by trait
    base_url = "https://www.pgscatalog.org/rest/score/search"
    params = {
        "q": query,
        "limit": max_results
    }

    if trait_filter:
        params["trait"] = trait_filter

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        results = []
        for result in data.get("results", []):
            # Get full model data for each result
            pgs_id = result.get('id')
            if pgs_id:
                model_data = get_pgs_model_data(pgs_id, include_metadata=False)
                if model_data:
                    # Add metadata from search result
                    model_data.update({
                        'trait': result.get('trait_reported', 'Unknown'),
                        'genome_build': result.get('genome_build', 'Unknown'),
                        'ancestry': result.get('ancestry', 'Unknown'),
                        'citation': result.get('citation', 'Unknown')
                    })
                    results.append(model_data)

        return results

    except Exception as e:
        st.error(f"Error searching PGS models: {str(e)}")
        return []

def get_pgs_model_summary(pgs_id):
    """
    Get summary information for a PGS model without downloading full scoring file.

    Args:
        pgs_id: PGS Catalog ID

    Returns:
        Dictionary with model summary or None
    """
    base_url = f"https://www.pgscatalog.org/rest/score/{pgs_id}"

    try:
        response = requests.get(base_url, timeout=30)
        response.raise_for_status()
        data = response.json()

        return {
            'pgs_id': pgs_id,
            'trait': data.get('trait_reported', 'Unknown'),
            'num_variants': data.get('variants_number', 0),
            'genome_build': data.get('genome_build', 'Unknown'),
            'ancestry': data.get('ancestry', 'Unknown'),
            'method_name': data.get('method_name', 'Unknown'),
            'citation': data.get('citation', 'Unknown'),
            'has_scoring_file': 'ftp_scoring_file' in data,
            'training_samples': data.get('samples_variants_numbers', {}).get('training', 0),
            'raw_metadata': data
        }

    except Exception as e:
        st.error(f"Failed to get PGS model summary for {pgs_id}: {str(e)}")
        return None

@api_call_with_retry()
def get_gnomad_population_data(rsid, use_cache=True):
    """
    Fetches population frequency data for a given rsID from gnoAD with enhanced error handling and caching.

    Args:
        rsid: rsID to query
        use_cache: Whether to use cached results

    Returns:
        DataFrame with population frequencies or None if failed
    """
    if not rsid:
        return None

    logger.info(f"Fetching gnomAD data for {rsid}")

    # Try the REST API first
    rest_url = f"https://gnomad.broadinstitute.org/api/v2/variants/{rsid}"
    logger.info(f"Trying gnomAD REST API: {rest_url}")

    data = make_api_request(rest_url, use_cache=use_cache)

    if data is not None:
        try:
            logger.info("Processing gnomAD REST API response")
            population_data = []

            # Global frequencies
            if 'exome' in data:
                exome = data['exome']
                if exome.get('an', 0) > 0:
                    population_data.append({
                        "Population": "Global (Exome)",
                        "Allele": data.get('alt', 'ALT'),
                        "Frequency": exome.get('af', 0),
                        "Allele_Count": exome.get('ac', 0),
                        "Total_Count": exome.get('an', 0)
                    })

            if 'genome' in data:
                genome = data['genome']
                if genome.get('an', 0) > 0:
                    population_data.append({
                        "Population": "Global (Genome)",
                        "Allele": data.get('alt', 'ALT'),
                        "Frequency": genome.get('af', 0),
                        "Allele_Count": genome.get('ac', 0),
                        "Total_Count": genome.get('an', 0)
                    })

            # Population-specific frequencies
            if 'populations' in data:
                for pop in data['populations']:
                    if pop.get('an', 0) > 0:
                        population_data.append({
                            "Population": pop['id'],
                            "Allele": data.get('alt', 'ALT'),
                            "Frequency": pop.get('af', 0),
                            "Allele_Count": pop.get('ac', 0),
                            "Total_Count": pop.get('an', 0)
                        })

            if population_data:
                logger.info(f"Successfully processed gnomAD REST data for {rsid}")
                return pd.DataFrame(population_data)

        except Exception as e:
            logger.error(f"Error processing gnoAD REST API data for {rsid}: {e}")
            logger.error(f"Response data: {data}")
            st.error(f"Error processing gnoAD REST API data for {rsid}: {e}")

    # Fallback to GraphQL API
    logger.info(f"Trying gnomAD GraphQL API fallback for {rsid}")
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

    graphql_data = make_api_request(base_url, {"query": query, "variables": {"variantId": rsid}}, method='POST', use_cache=use_cache)

    if graphql_data is None:
        logger.error("gnomAD GraphQL API request failed")
        return None

    try:
        logger.debug(f"Processing gnomAD GraphQL response: {graphql_data}")
        if 'data' in graphql_data and 'variant' in graphql_data['data'] and graphql_data['data']['variant']:
            variant = graphql_data['data']['variant']
            population_data = []

            # Global frequencies
            if variant.get('exome'):
                exome_ac = variant['exome']['ac']
                exome_an = variant['exome']['an']
                if exome_an > 0:
                    population_data.append({
                        "Population": "Global (Exome)",
                        "Allele": variant['alt'],
                        "Frequency": exome_ac / exome_an,
                        "Allele_Count": exome_ac,
                        "Total_Count": exome_an
                    })

            if variant.get('genome'):
                genome_ac = variant['genome']['ac']
                genome_an = variant['genome']['an']
                if genome_an > 0:
                    population_data.append({
                        "Population": "Global (Genome)",
                        "Allele": variant['alt'],
                        "Frequency": genome_ac / genome_an,
                        "Allele_Count": genome_ac,
                        "Total_Count": genome_an
                    })

            # Population-specific frequencies
            if variant.get('populations'):
                for pop in variant['populations']:
                    if pop['an'] > 0:
                        population_data.append({
                            "Population": pop['id'],
                            "Allele": variant['alt'],
                            "Frequency": pop['ac'] / pop['an'],
                            "Allele_Count": pop['ac'],
                            "Total_Count": pop['an']
                        })

            if population_data:
                logger.info(f"Successfully processed gnomAD GraphQL data for {rsid}")
                return pd.DataFrame(population_data)
            else:
                logger.warning(f"No population frequency data found for {rsid}")
                st.warning(f"No population frequency data found for {rsid}")
                return None
        else:
            logger.warning(f"No gnoAD data found for {rsid}")
            st.warning(f"No gnoAD data found for {rsid}")
            return None

    except Exception as e:
        logger.error(f"Error processing gnoAD GraphQL data for {rsid}: {e}")
        logger.error(f"GraphQL response: {graphql_data}")
        st.error(f"Error processing gnoAD GraphQL data for {rsid}: {e}")
        return None

@api_call_with_retry()
def search_pubmed(query, max_results=20, search_type="general", use_cache=True):
    """
    Search PubMed for articles related to genetic variants or genes.

    Args:
        query: Search query (gene name, rsID, etc.)
        max_results: Maximum number of results to return
        search_type: Type of search ("general", "recent", "review", "clinical")
        use_cache: Whether to use cached results

    Returns:
        List of article summaries or None if failed
    """
    if not query:
        return []

    # Build search query based on type
    if search_type == "recent":
        full_query = f"{query} AND (2020:2025[dp])"
    elif search_type == "review":
        full_query = f"{query} AND review[pt]"
    elif search_type == "clinical":
        full_query = f"{query} AND clinical trial[pt]"
    else:
        full_query = query

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

    search_data = make_api_request(search_url, search_params, use_cache=use_cache)

    if search_data is None or 'esearchresult' not in search_data:
        return []

    ids = search_data['esearchresult'].get('idlist', [])

    if not ids:
        return []

    # Fetch detailed information for each article
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(ids[:max_results]),
        "retmode": "json"
    }

    fetch_data = make_api_request(fetch_url, fetch_params, use_cache=use_cache)

    if fetch_data is None or 'result' not in fetch_data:
        return []

    articles = []
    for pubmed_id in ids[:max_results]:
        if pubmed_id in fetch_data['result']:
            article = fetch_data['result'][pubmed_id]

            article_summary = {
                'pmid': pubmed_id,
                'title': article.get('title', 'No title available'),
                'authors': article.get('authors', []),
                'journal': article.get('source', 'Unknown journal'),
                'pub_date': article.get('pubdate', 'Unknown date'),
                'abstract': article.get('abstract', ''),
                'doi': article.get('elocationid', ''),
                'url': f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/"
            }

            # Format authors
            if article_summary['authors']:
                author_names = []
                for author in article_summary['authors'][:3]:  # Show first 3 authors
                    if 'name' in author:
                        author_names.append(author['name'])
                if len(article_summary['authors']) > 3:
                    author_names.append("et al.")
                article_summary['authors_formatted'] = ", ".join(author_names)
            else:
                article_summary['authors_formatted'] = "Unknown"

            articles.append(article_summary)

    return articles

@api_call_with_retry()
def get_pubmed_abstract(pmid, use_cache=True):
    """
    Fetch full abstract for a specific PubMed ID.

    Args:
        pmid: PubMed ID
        use_cache: Whether to use cached results

    Returns:
        Article details with full abstract or None if failed
    """
    if not pmid:
        return None

    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    fetch_params = {
        "db": "pubmed",
        "id": pmid,
        "retmode": "xml"
    }

    response_text = make_api_request(fetch_url, fetch_params, use_cache=use_cache)

    if response_text is None:
        return None

    try:
        # Parse XML response
        root = ET.fromstring(response_text)

        article = root.find('.//PubmedArticle')
        if article is None:
            return None

        # Extract title
        title_elem = article.find('.//ArticleTitle')
        title = title_elem.text if title_elem is not None else "No title available"

        # Extract abstract
        abstract_elem = article.find('.//AbstractText')
        abstract = abstract_elem.text if abstract_elem is not None else "No abstract available"

        # Extract authors
        authors = []
        author_elems = article.findall('.//Author')
        for author_elem in author_elems[:5]:  # Limit to 5 authors
            last_name = author_elem.find('LastName')
            fore_name = author_elem.find('ForeName')
            if last_name is not None and fore_name is not None:
                authors.append(f"{fore_name.text} {last_name.text}")

        # Extract journal
        journal_elem = article.find('.//Journal/Title')
        journal = journal_elem.text if journal_elem is not None else "Unknown journal"

        # Extract publication date
        pub_date_elem = article.find('.//PubDate/Year')
        pub_date = pub_date_elem.text if pub_date_elem is not None else "Unknown date"

        return {
            'pmid': pmid,
            'title': title,
            'abstract': abstract,
            'authors': authors,
            'journal': journal,
            'pub_date': pub_date,
            'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        }

    except ET.ParseError as e:
        st.error(f"Error parsing PubMed XML for {pmid}: {e}")
        return None
    except Exception as e:
        st.error(f"Error processing PubMed data for {pmid}: {e}")
        return None

def get_api_health_status():
    """
    Check the health status of all integrated APIs.

    Returns:
        Dictionary with API health status
    """
    health_status = {
        'clinvar': {'status': 'unknown', 'last_checked': None, 'response_time': None},
        'pharmgkb': {'status': 'unknown', 'last_checked': None, 'response_time': None},
        'gnomad': {'status': 'unknown', 'last_checked': None, 'response_time': None},
        'pubmed': {'status': 'unknown', 'last_checked': None, 'response_time': None},
        'pgs_catalog': {'status': 'unknown', 'last_checked': None, 'response_time': None}
    }

    # Test ClinVar
    try:
        start_time = time.time()
        test_result = get_clinvar_data(['rs1801133'], use_cache=False)
        response_time = time.time() - start_time
        health_status['clinvar'] = {
            'status': 'healthy' if test_result is not None else 'unhealthy',
            'last_checked': datetime.now().isoformat(),
            'response_time': round(response_time, 2)
        }
    except Exception:
        health_status['clinvar'] = {
            'status': 'unhealthy',
            'last_checked': datetime.now().isoformat(),
            'response_time': None
        }

    # Test PharmGKB
    try:
        start_time = time.time()
        test_result = get_pharmgkb_data(['rs1801133'], use_cache=False)
        response_time = time.time() - start_time
        health_status['pharmgkb'] = {
            'status': 'healthy' if test_result is not None else 'unhealthy',
            'last_checked': datetime.now().isoformat(),
            'response_time': round(response_time, 2)
        }
    except Exception:
        health_status['pharmgkb'] = {
            'status': 'unhealthy',
            'last_checked': datetime.now().isoformat(),
            'response_time': None
        }

    # Test gnoAD
    try:
        start_time = time.time()
        test_result = get_gnomad_population_data('rs1801133', use_cache=False)
        response_time = time.time() - start_time
        health_status['gnomad'] = {
            'status': 'healthy' if test_result is not None else 'unhealthy',
            'last_checked': datetime.now().isoformat(),
            'response_time': round(response_time, 2)
        }
    except Exception:
        health_status['gnomad'] = {
            'status': 'unhealthy',
            'last_checked': datetime.now().isoformat(),
            'response_time': None
        }

    # Test PubMed
    try:
        start_time = time.time()
        test_result = search_pubmed('BRCA1', max_results=1, use_cache=False)
        response_time = time.time() - start_time
        health_status['pubmed'] = {
            'status': 'healthy' if test_result is not None else 'unhealthy',
            'last_checked': datetime.now().isoformat(),
            'response_time': round(response_time, 2)
        }
    except Exception:
        health_status['pubmed'] = {
            'status': 'unhealthy',
            'last_checked': datetime.now().isoformat(),
            'response_time': None
        }

    # Test PGS Catalog
    try:
        start_time = time.time()
        test_result = get_pgs_catalog_data('breast cancer', max_results=1)
        response_time = time.time() - start_time
        health_status['pgs_catalog'] = {
            'status': 'healthy' if test_result is not None else 'unhealthy',
            'last_checked': datetime.now().isoformat(),
            'response_time': round(response_time, 2)
        }
    except Exception:
        health_status['pgs_catalog'] = {
            'status': 'unhealthy',
            'last_checked': datetime.now().isoformat(),
            'response_time': None
        }

    return health_status
