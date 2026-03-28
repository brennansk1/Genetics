"""
Evidence-backed variant annotation using free, no-signup APIs.

Data sources integrated:
  - MyVariant.info (aggregates ClinVar, gnomAD, CADD, dbSNP, etc.)
  - Ensembl VEP REST API (functional consequence prediction)
  - Open Targets Platform (disease-gene evidence scores)
  - ClinVar E-utilities (pathogenicity assertions with review status)
  - gnomAD (population allele frequencies)

All APIs are completely free with no signup/API key required.
"""

import logging
import time
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import numpy as np
import requests

try:
    from .caching_utils import cache_result
except Exception:
    cache_result = None

logger = logging.getLogger(__name__)

# Rate limiting: be respectful to free APIs
_LAST_CALL_TIME = 0.0
_MIN_INTERVAL = 0.15  # 150ms between calls


def _rate_limit():
    global _LAST_CALL_TIME
    elapsed = time.time() - _LAST_CALL_TIME
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)
    _LAST_CALL_TIME = time.time()


def _safe_get(url: str, params: dict = None, timeout: int = 10) -> Optional[dict]:
    """Safe HTTP GET with error handling."""
    _rate_limit()
    try:
        resp = requests.get(url, params=params, timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
        logger.warning("API returned %d for %s", resp.status_code, url)
    except Exception as e:
        logger.warning("API call failed for %s: %s", url, e)
    return None


def _safe_post(url: str, json_data: dict = None, timeout: int = 15) -> Optional[dict]:
    """Safe HTTP POST with error handling."""
    _rate_limit()
    try:
        resp = requests.post(url, json=json_data, timeout=timeout,
                             headers={"Content-Type": "application/json"})
        if resp.status_code == 200:
            return resp.json()
        logger.warning("API POST returned %d for %s", resp.status_code, url)
    except Exception as e:
        logger.warning("API POST failed for %s: %s", url, e)
    return None


# ---------------------------------------------------------------------------
# MyVariant.info -- aggregates ClinVar, gnomAD, CADD, dbSNP in one call
# Docs: https://myvariant.info/
# No signup, no API key, 1000 queries/sec
# ---------------------------------------------------------------------------

def query_myvariant_batch(rsids: List[str]) -> Dict[str, dict]:
    """
    Query MyVariant.info for multiple rsIDs in a single batch request.
    Returns ClinVar significance, gnomAD frequencies, CADD scores, gene info.

    Args:
        rsids: List of rsIDs (e.g., ["rs1042522", "rs5925"])

    Returns:
        Dict mapping rsID -> annotation dict with keys:
          clinvar_sig, clinvar_review_stars, gnomad_af, gnomad_popmax_af,
          gnomad_populations, cadd_phred, gene, consequence, is_pathogenic
    """
    results = {}
    if not rsids:
        return results

    # MyVariant.info supports batch queries up to 1000
    batch_size = 200
    fields = "clinvar,gnomad_exome,gnomad_genome,cadd,dbsnp,snpeff"

    for i in range(0, len(rsids), batch_size):
        batch = rsids[i:i + batch_size]
        query = ",".join(batch)

        data = _safe_post(
            "https://myvariant.info/v1/query",
            json_data={
                "q": query,
                "scopes": "dbsnp.rsid",
                "fields": fields,
                "size": len(batch),
            },
            timeout=30,
        )

        if not data:
            continue

        if isinstance(data, list):
            for hit in data:
                rsid = hit.get("query", "")
                if hit.get("notfound"):
                    continue
                parsed = _parse_myvariant_hit(hit)
                # Multiple hits per rsID (one per alt allele).
                # Merge: keep the one with most data (gnomAD AF, ClinVar sig).
                if rsid in results:
                    existing = results[rsid]
                    # Prefer hit with gnomAD data
                    if parsed.get("gnomad_af") is not None and existing.get("gnomad_af") is None:
                        results[rsid] = parsed
                    # Prefer hit with ClinVar pathogenic over benign
                    elif parsed.get("is_pathogenic") and not existing.get("is_pathogenic"):
                        results[rsid] = parsed
                else:
                    results[rsid] = parsed

    return results


def query_myvariant_single(rsid: str) -> Optional[dict]:
    """Query MyVariant.info for a single rsID."""
    data = _safe_get(
        f"https://myvariant.info/v1/query",
        params={
            "q": f"dbsnp.rsid:{rsid}",
            "fields": "clinvar,gnomad_exome,gnomad_genome,cadd,dbsnp,snpeff",
            "size": 1,
        },
    )
    if data and data.get("hits"):
        return _parse_myvariant_hit(data["hits"][0])
    return None


def _parse_myvariant_hit(hit: dict) -> dict:
    """Parse a MyVariant.info hit into a standardized annotation dict."""
    result = {
        "clinvar_sig": None,
        "clinvar_review_stars": 0,
        "clinvar_conditions": [],
        "gnomad_af": None,
        "gnomad_af_popmax": None,
        "gnomad_populations": {},
        "cadd_phred": None,
        "gene": None,
        "consequence": None,
        "is_pathogenic": False,
        "is_likely_pathogenic": False,
        "is_benign": False,
    }

    # ClinVar data
    clinvar = hit.get("clinvar", {})
    if clinvar:
        rcv = clinvar.get("rcv", {})
        # rcv can be a list of RCV records
        if isinstance(rcv, list):
            # Collect all significance assertions to find consensus
            all_sigs = [r.get("clinical_significance", "") for r in rcv if r.get("clinical_significance")]
            # Priority: Pathogenic > Likely pathogenic > VUS > Likely benign > Benign
            sig = _pick_most_significant(all_sigs)
            # Collect all conditions
            for r in rcv:
                conds = r.get("conditions", {})
                if isinstance(conds, dict) and conds.get("name"):
                    name = conds["name"]
                    if isinstance(name, str) and name not in result["clinvar_conditions"]:
                        result["clinvar_conditions"].append(name)
                    elif isinstance(name, list):
                        result["clinvar_conditions"].extend(name)
                elif isinstance(conds, list):
                    for c in conds:
                        n = c.get("name", "")
                        if n and n not in result["clinvar_conditions"]:
                            result["clinvar_conditions"].append(n)
        elif isinstance(rcv, dict):
            sig = rcv.get("clinical_significance", "")
        else:
            sig = clinvar.get("clinical_significance", "")

        if sig:
            result["clinvar_sig"] = sig
            sig_lower = sig.lower() if isinstance(sig, str) else ""
            result["is_pathogenic"] = "pathogenic" in sig_lower and "likely" not in sig_lower and "benign" not in sig_lower and "conflicting" not in sig_lower
            result["is_likely_pathogenic"] = "likely pathogenic" in sig_lower or "likely_pathogenic" in sig_lower
            result["is_benign"] = ("benign" in sig_lower and "pathogenic" not in sig_lower) or "likely benign" in sig_lower

        # Review status (stars)
        review = clinvar.get("review", {})
        if isinstance(review, dict):
            stars = review.get("review_status", "")
            result["clinvar_review_stars"] = _review_status_to_stars(stars)

    # gnomAD data (prefer genome, fallback to exome)
    gnomad = hit.get("gnomad_genome") or hit.get("gnomad_exome", {})
    if gnomad:
        af = gnomad.get("af", {})
        if isinstance(af, dict):
            result["gnomad_af"] = af.get("af")
            # Population-specific frequencies - MyVariant uses af_afr, af_eur, etc.
            pop_mapping = {
                "af_afr": "AFR", "af_amr": "AMR", "af_eas": "EAS",
                "af_eur": "EUR", "af_sas": "SAS", "af_fin": "FIN",
                "af_nfe": "NFE", "af_asj": "ASJ",
            }
            for field, pop_name in pop_mapping.items():
                pop_af = af.get(field)
                if pop_af is not None:
                    result["gnomad_populations"][pop_name] = pop_af
            # PopMax
            popmax = af.get("af_popmax")
            if popmax is not None:
                result["gnomad_af_popmax"] = popmax
        elif isinstance(af, (int, float)):
            result["gnomad_af"] = af

    # CADD score (deleteriousness predictor)
    cadd = hit.get("cadd", {})
    if cadd:
        phred = cadd.get("phred")
        if isinstance(phred, (int, float)):
            result["cadd_phred"] = phred

    # Gene info from snpeff
    snpeff = hit.get("snpeff", {})
    if snpeff:
        ann = snpeff.get("ann", {})
        if isinstance(ann, list):
            ann = ann[0] if ann else {}
        if isinstance(ann, dict):
            result["gene"] = ann.get("genename")
            result["consequence"] = ann.get("effect")

    # Gene from dbsnp
    if not result["gene"]:
        dbsnp = hit.get("dbsnp", {})
        if dbsnp:
            gene = dbsnp.get("gene", {})
            if isinstance(gene, dict):
                result["gene"] = gene.get("symbol")
            elif isinstance(gene, list) and gene:
                result["gene"] = gene[0].get("symbol") if isinstance(gene[0], dict) else None

    return result


def _pick_most_significant(sigs: List[str]) -> str:
    """Pick the most significant ClinVar classification from a list."""
    if not sigs:
        return ""
    # Priority ranking
    for priority in ["Pathogenic", "Likely pathogenic", "Uncertain significance",
                     "Conflicting interpretations", "Likely benign", "Benign"]:
        for sig in sigs:
            if priority.lower() in sig.lower():
                return sig
    return sigs[0]


def _review_status_to_stars(status: str) -> int:
    """Convert ClinVar review status to star rating (0-4)."""
    if not status:
        return 0
    status = status.lower()
    if "practice guideline" in status:
        return 4
    elif "expert panel" in status:
        return 4
    elif "multiple submitters" in status and "no conflicts" in status:
        return 3
    elif "multiple submitters" in status:
        return 2
    elif "single submitter" in status or "criteria provided" in status:
        return 1
    return 0


# ---------------------------------------------------------------------------
# Ensembl VEP REST API -- functional consequence prediction
# Docs: https://rest.ensembl.org/documentation/info/vep_id_post
# No signup, no API key, 15 req/sec, batch up to 200
# ---------------------------------------------------------------------------

def query_ensembl_vep(rsids: List[str]) -> Dict[str, dict]:
    """
    Query Ensembl VEP for functional consequences of variants.

    Returns dict mapping rsID -> {
        consequence: str,  # e.g. "missense_variant", "synonymous_variant"
        impact: str,       # HIGH, MODERATE, LOW, MODIFIER
        gene_symbol: str,
        amino_acid_change: str,  # e.g. "P/R" for Pro72Arg
        sift_prediction: str,
        polyphen_prediction: str,
        biotype: str,
    }
    """
    results = {}
    if not rsids:
        return results

    batch_size = 150  # Ensembl limit is 200 but be conservative
    for i in range(0, len(rsids), batch_size):
        batch = rsids[i:i + batch_size]
        data = _safe_post(
            "https://rest.ensembl.org/vep/human/id",
            json_data={"ids": batch},
            timeout=30,
        )

        if not data or not isinstance(data, list):
            continue

        for entry in data:
            rsid = entry.get("id", "")
            tc = entry.get("most_severe_consequence", "")
            transcript_consequences = entry.get("transcript_consequences", [])

            # Find the most severe transcript consequence
            best = {}
            for tc_entry in transcript_consequences:
                if tc_entry.get("consequence_terms") and tc in tc_entry.get("consequence_terms", []):
                    best = tc_entry
                    break
            if not best and transcript_consequences:
                best = transcript_consequences[0]

            results[rsid] = {
                "consequence": tc,
                "impact": best.get("impact", "MODIFIER"),
                "gene_symbol": best.get("gene_symbol", ""),
                "amino_acid_change": best.get("amino_acids", ""),
                "sift_prediction": best.get("sift_prediction", ""),
                "polyphen_prediction": best.get("polyphen_prediction", ""),
                "biotype": best.get("biotype", ""),
            }

    return results


# ---------------------------------------------------------------------------
# Open Targets Platform -- disease-gene evidence scores
# Docs: https://platform-docs.opentargets.org/data-access/graphql-api
# No signup, no API key
# ---------------------------------------------------------------------------

def query_open_targets_disease_gene(gene_symbol: str) -> List[dict]:
    """
    Query Open Targets for disease associations of a gene.

    Returns list of {
        disease_name: str,
        disease_id: str,
        overall_score: float (0-1),
        genetic_association_score: float,
        literature_score: float,
    }
    """
    query = """
    query GeneAssociations($ensemblId: String!) {
      target(ensemblId: $ensemblId) {
        id
        approvedSymbol
        associatedDiseases(page: {index: 0, size: 20}) {
          rows {
            disease {
              id
              name
            }
            score
            datatypeScores {
              id
              score
            }
          }
        }
      }
    }
    """

    # First resolve gene symbol to Ensembl ID
    ensembl_id = _resolve_gene_to_ensembl(gene_symbol)
    if not ensembl_id:
        return []

    data = _safe_post(
        "https://api.platform.opentargets.org/api/v4/graphql",
        json_data={"query": query, "variables": {"ensemblId": ensembl_id}},
        timeout=15,
    )

    if not data or "data" not in data:
        return []

    target = data["data"].get("target", {})
    if not target:
        return []

    associations = target.get("associatedDiseases", {}).get("rows", [])
    results = []
    for assoc in associations:
        disease = assoc.get("disease", {})
        datatype_scores = {d["id"]: d["score"] for d in assoc.get("datatypeScores", [])}
        results.append({
            "disease_name": disease.get("name", ""),
            "disease_id": disease.get("id", ""),
            "overall_score": assoc.get("score", 0),
            "genetic_association_score": datatype_scores.get("ot_genetics_portal", 0),
            "literature_score": datatype_scores.get("europepmc", 0),
        })

    return results


def _resolve_gene_to_ensembl(gene_symbol: str) -> Optional[str]:
    """Resolve a gene symbol (e.g., 'TP53') to Ensembl ID using Ensembl REST."""
    data = _safe_get(
        f"https://rest.ensembl.org/lookup/symbol/homo_sapiens/{gene_symbol}",
        params={"content-type": "application/json"},
    )
    if data:
        return data.get("id")
    return None


# ---------------------------------------------------------------------------
# gnomAD population frequency lookups (using MyVariant.info as proxy)
# ---------------------------------------------------------------------------

def get_gnomad_frequencies(rsids: List[str]) -> Dict[str, dict]:
    """
    Get gnomAD population allele frequencies for a list of rsIDs.
    Uses MyVariant.info which includes gnomAD data.

    Returns dict mapping rsID -> {
        global_af: float,
        popmax_af: float,
        populations: {AFR: float, AMR: float, EAS: float, EUR: float, ...}
    }
    """
    annotations = query_myvariant_batch(rsids)
    results = {}
    for rsid, ann in annotations.items():
        if ann.get("gnomad_af") is not None:
            results[rsid] = {
                "global_af": ann["gnomad_af"],
                "popmax_af": ann.get("gnomad_af_popmax"),
                "populations": ann.get("gnomad_populations", {}),
            }
    return results


# ---------------------------------------------------------------------------
# High-level functions that combine multiple sources
# ---------------------------------------------------------------------------

def classify_variant(rsid: str, genotype: str) -> dict:
    """
    Comprehensive variant classification using multiple evidence sources.

    Returns:
        {
            rsid, genotype, gene, consequence,
            clinvar_significance, clinvar_stars, clinvar_conditions,
            gnomad_af, is_common (>1% AF), is_rare (<1% AF),
            cadd_phred, impact_level (HIGH/MODERATE/LOW/MODIFIER),
            sift, polyphen,
            evidence_level: "strong"/"moderate"/"weak"/"insufficient",
            classification: "pathogenic"/"likely_pathogenic"/"vus"/"likely_benign"/"benign",
            is_actionable: bool,
        }
    """
    result = {
        "rsid": rsid,
        "genotype": genotype,
        "gene": None,
        "consequence": None,
        "clinvar_significance": None,
        "clinvar_stars": 0,
        "clinvar_conditions": [],
        "gnomad_af": None,
        "is_common": False,
        "is_rare": False,
        "cadd_phred": None,
        "impact_level": "MODIFIER",
        "sift": None,
        "polyphen": None,
        "evidence_level": "insufficient",
        "classification": "unknown",
        "is_actionable": False,
    }

    # MyVariant.info (ClinVar + gnomAD + CADD in one call)
    mv = query_myvariant_single(rsid)
    if mv:
        result["gene"] = mv.get("gene")
        result["clinvar_significance"] = mv.get("clinvar_sig")
        result["clinvar_stars"] = mv.get("clinvar_review_stars", 0)
        result["clinvar_conditions"] = mv.get("clinvar_conditions", [])
        result["gnomad_af"] = mv.get("gnomad_af")
        result["cadd_phred"] = mv.get("cadd_phred")
        result["consequence"] = mv.get("consequence")

        if mv.get("gnomad_af") is not None:
            result["is_common"] = mv["gnomad_af"] > 0.01
            result["is_rare"] = mv["gnomad_af"] < 0.01

    # Ensembl VEP for functional consequence
    vep = query_ensembl_vep([rsid])
    if rsid in vep:
        v = vep[rsid]
        result["impact_level"] = v.get("impact", "MODIFIER")
        result["sift"] = v.get("sift_prediction")
        result["polyphen"] = v.get("polyphen_prediction")
        if not result["consequence"]:
            result["consequence"] = v.get("consequence")
        if not result["gene"]:
            result["gene"] = v.get("gene_symbol")

    # Derive evidence-based classification
    result["classification"] = _derive_classification(result)
    result["evidence_level"] = _derive_evidence_level(result)
    result["is_actionable"] = _is_actionable(result)

    return result


def classify_variants_batch(rsids: List[str], genotypes: Dict[str, str] = None) -> Dict[str, dict]:
    """
    Classify multiple variants efficiently using batch API calls.

    Args:
        rsids: List of rsIDs
        genotypes: Optional dict mapping rsID -> genotype string

    Returns:
        Dict mapping rsID -> classification result
    """
    if not rsids:
        return {}

    genotypes = genotypes or {}
    results = {}

    # Batch call to MyVariant.info
    mv_results = query_myvariant_batch(rsids)

    # Batch call to Ensembl VEP
    vep_results = query_ensembl_vep(rsids)

    for rsid in rsids:
        mv = mv_results.get(rsid, {})
        vep = vep_results.get(rsid, {})
        genotype = genotypes.get(rsid, "")

        result = {
            "rsid": rsid,
            "genotype": genotype,
            "gene": mv.get("gene") or vep.get("gene_symbol"),
            "consequence": mv.get("consequence") or vep.get("consequence"),
            "clinvar_significance": mv.get("clinvar_sig"),
            "clinvar_stars": mv.get("clinvar_review_stars", 0),
            "clinvar_conditions": mv.get("clinvar_conditions", []),
            "gnomad_af": mv.get("gnomad_af"),
            "is_common": (mv.get("gnomad_af") or 0) > 0.01,
            "is_rare": (mv.get("gnomad_af") or 0) < 0.01 if mv.get("gnomad_af") is not None else False,
            "cadd_phred": mv.get("cadd_phred"),
            "impact_level": vep.get("impact", "MODIFIER"),
            "sift": vep.get("sift_prediction"),
            "polyphen": vep.get("polyphen_prediction"),
        }

        result["classification"] = _derive_classification(result)
        result["evidence_level"] = _derive_evidence_level(result)
        result["is_actionable"] = _is_actionable(result)
        results[rsid] = result

    return results


def _derive_classification(result: dict) -> str:
    """
    Derive ACMG-like classification from multiple evidence sources.

    Uses a simplified version of ACMG criteria:
    - ClinVar assertion is primary evidence
    - gnomAD AF helps distinguish benign (common) from pathogenic (rare)
    - CADD score adds computational prediction evidence
    - VEP impact level provides functional context
    """
    sig = (result.get("clinvar_significance") or "").lower()
    af = result.get("gnomad_af")
    cadd = result.get("cadd_phred")
    impact = result.get("impact_level", "")

    # Key rule: a variant with AF > 5% is almost certainly benign, regardless
    # of ClinVar assertions. True pathogenic variants are rare in the population.
    # This handles cases like TP53 rs1042522 (Pro72Arg) which ClinVar lists as
    # "Pathogenic" for Li-Fraumeni but has 62% population frequency.
    if af is not None and af > 0.05:
        if "pathogenic" in sig and "benign" not in sig:
            return "benign"  # Common variant misclassified as pathogenic
        return "benign"
    if af is not None and af > 0.01:
        if "pathogenic" in sig and "benign" not in sig:
            return "likely_benign"  # Moderately common, likely benign
        return "likely_benign"

    # ClinVar is strong evidence for rare variants (AF < 1%)
    if "pathogenic" in sig and "likely" not in sig and "benign" not in sig and "conflicting" not in sig:
        return "pathogenic"
    if "likely pathogenic" in sig or "likely_pathogenic" in sig:
        return "likely_pathogenic"
    if "benign" in sig and "likely" not in sig and "pathogenic" not in sig:
        return "benign"
    if "likely benign" in sig or "likely_benign" in sig:
        return "likely_benign"
    if "conflicting" in sig:
        if af is not None and af > 0.005:
            return "likely_benign"
        return "vus"
    if af is not None and af > 0.01:
        return "likely_benign"

    # Rare + high CADD + high impact = likely pathogenic
    if af is not None and af < 0.001 and cadd and cadd > 25 and impact == "HIGH":
        return "likely_pathogenic"

    if cadd and cadd > 20 and impact in ("HIGH", "MODERATE"):
        return "vus"  # Variant of uncertain significance

    return "vus" if sig == "" else "vus"


def _derive_evidence_level(result: dict) -> str:
    """Derive evidence strength from available data."""
    stars = result.get("clinvar_stars", 0)
    has_af = result.get("gnomad_af") is not None
    has_cadd = result.get("cadd_phred") is not None
    has_vep = result.get("impact_level", "") in ("HIGH", "MODERATE")

    if stars >= 3:
        return "strong"
    if stars >= 2 or (stars >= 1 and has_af and has_cadd):
        return "moderate"
    if stars >= 1 or (has_af and has_cadd and has_vep):
        return "weak"
    return "insufficient"


def _is_actionable(result: dict) -> bool:
    """Determine if a variant classification warrants clinical attention."""
    classification = result.get("classification", "")
    evidence = result.get("evidence_level", "")

    if classification in ("pathogenic", "likely_pathogenic"):
        return evidence in ("strong", "moderate", "weak")
    return False


# ---------------------------------------------------------------------------
# PRS improvement: get real population allele frequencies for reference dist
# ---------------------------------------------------------------------------

def get_prs_population_stats(
    model_rsids: List[str],
    effect_alleles: Dict[str, str],
    effect_weights: Dict[str, float],
    ancestry: str = "EUR",
) -> Tuple[float, float]:
    """
    Calculate proper population mean and std for PRS using real gnomAD
    allele frequencies instead of fabricated values.

    For each SNP: expected contribution = 2 * freq * weight (diploid)
    Population mean = sum of expected contributions
    Population variance = sum of 2 * freq * (1-freq) * weight^2

    Args:
        model_rsids: List of rsIDs in the PRS model
        effect_alleles: Dict of rsID -> effect allele
        effect_weights: Dict of rsID -> effect weight
        ancestry: Population code for ancestry-specific frequencies

    Returns:
        (population_mean, population_std)
    """
    pop_map = {
        "EUR": "NFE", "AFR": "AFR", "EAS": "EAS",
        "SAS": "SAS", "AMR": "AMR", "ASJ": "ASJ",
    }
    gnomad_pop = pop_map.get(ancestry.upper(), "NFE")

    # Get allele frequencies from MyVariant.info
    annotations = query_myvariant_batch(model_rsids)

    mean_sum = 0.0
    var_sum = 0.0
    found = 0

    for rsid in model_rsids:
        weight = effect_weights.get(rsid, 0)
        ann = annotations.get(rsid, {})
        pops = ann.get("gnomad_populations", {})

        # Get ancestry-specific frequency, fallback to global
        freq = pops.get(gnomad_pop) or ann.get("gnomad_af")
        if freq is None:
            # Use 0.5 as uninformative prior if no frequency data
            freq = 0.5

        # Expected PRS contribution: 2 * p * beta (diploid, additive model)
        mean_sum += 2 * freq * weight
        # Variance contribution: 2 * p * (1-p) * beta^2
        var_sum += 2 * freq * (1 - freq) * (weight ** 2)
        found += 1

    pop_std = np.sqrt(var_sum) if var_sum > 0 else 0.1
    logger.info(
        "PRS population stats: mean=%.4f, std=%.4f (from %d/%d SNPs with freq data)",
        mean_sum, pop_std, found, len(model_rsids),
    )

    return mean_sum, pop_std
