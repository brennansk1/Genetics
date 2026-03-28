"""
Analysis router -- handles DNA file upload, full analysis pipeline,
section-specific GET endpoints, and family comparison.

POST /analysis/process-dna          - Upload a DNA file, run all analyses, cache results.
GET  /analysis/session/{id}         - Retrieve session metadata for a given analysis_id.
GET  /analysis/results/{id}         - Retrieve full cached results.
GET  /clinical/risks/{id}           - Clinical risk variants.
GET  /clinical/carrier-status/{id}  - Carrier screening results.
GET  /clinical/cancer-risk/{id}     - Cancer-specific risk variants.
GET  /clinical/acmg-findings/{id}   - ACMG secondary findings.
GET  /pgx/report/{id}               - Pharmacogenomics report.
GET  /prs/scores/{id}               - Polygenic risk scores.
GET  /wellness/traits/{id}          - Wellness trait results.
GET  /wellness/ancestry/{id}        - Ancestry inference results.
POST /analysis/family-compare       - Compare two DNA files (family analysis).
GET  /analysis/report/{id}          - Download PDF report.
"""

import logging
import os
import sys
import tempfile
from typing import Optional

import numpy as np
import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

# ---------------------------------------------------------------------------
# Path setup so we can import from the project-root ``src/`` package.
# ---------------------------------------------------------------------------
_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from src.run_analysis import (
    analyze_clinvar_variants,
    analyze_expanded_carrier_status,
    analyze_high_impact_risks,
    analyze_pgx_and_wellness,
    process_dna_file,
)

# Lazy-import optional heavy modules -- they may fail in CI
try:
    from src.snp_data import get_prs_models, get_simple_model, get_acmg_sf_variants
except Exception:
    get_prs_models = None
    get_simple_model = None
    get_acmg_sf_variants = None

try:
    from src.genomewide_prs import GenomeWidePRS
except Exception:
    GenomeWidePRS = None

try:
    from src.ancestry_inference import AncestryInference
except Exception:
    AncestryInference = None

try:
    from src.utils import analyze_wellness_snps
except Exception:
    analyze_wellness_snps = None

try:
    from src.family_analysis import FamilyAnalyzer
except Exception:
    FamilyAnalyzer = None

try:
    from src.variant_evidence import (
        classify_variants_batch,
        get_prs_population_stats,
        query_open_targets_disease_gene,
    )
    EVIDENCE_AVAILABLE = True
except Exception:
    EVIDENCE_AVAILABLE = False

from backend.src.analysis_store import analysis_store
from backend.src.models import (
    AnalysisResponse,
    AnalysisSessionInfo,
    AnalysisSummary,
    ErrorResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Genomic Analysis"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dataframe_to_records(df: pd.DataFrame) -> list:
    """Safely convert a DataFrame (possibly empty) to a list of dicts."""
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        return []
    try:
        return df.reset_index().to_dict(orient="records")
    except Exception:
        return []


def _get_cached_data(analysis_id: str) -> dict:
    """Retrieve cached analysis data or raise 404."""
    data = analysis_store.get(analysis_id)
    if data is None:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis session '{analysis_id}' not found or has expired.",
        )
    return data


def _parse_dna_upload(content_str: str, genome_build: str) -> pd.DataFrame:
    """Write content to temp file, parse it, return DataFrame."""
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w") as tmp:
            tmp.write(content_str)
            tmp_path = tmp.name
        df = process_dna_file(tmp_path, genome_build, None)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to parse DNA file: {exc}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    if df is None or df.empty:
        raise HTTPException(status_code=400, detail="Uploaded file contained no valid genotype data.")
    return df


def _run_prs_analysis(df: pd.DataFrame) -> list:
    """Compute simple PRS for every condition that has a model in the database."""
    results = []
    if get_prs_models is None or get_simple_model is None:
        logger.warning("PRS model accessors not available; skipping PRS analysis.")
        return results

    try:
        all_models = get_prs_models()
    except Exception as exc:
        logger.error("Failed to load PRS models: %s", exc)
        return results

    if not all_models:
        return results

    prs_calculator = GenomeWidePRS() if GenomeWidePRS else None

    for condition, model_info in all_models.items():
        simple_model = model_info.get("simple_model")
        if not simple_model:
            continue
        try:
            if prs_calculator is not None:
                result = prs_calculator.calculate_simple_prs(df, simple_model)
            else:
                result = {"success": False, "error": "PRS calculator unavailable"}

            result["condition"] = condition
            result.setdefault("risk_level", _percentile_to_risk_level(result.get("percentile", 50)))
            results.append(result)
        except Exception as exc:
            logger.error("PRS calculation failed for %s: %s", condition, exc)
            results.append({
                "condition": condition,
                "success": False,
                "error": str(exc),
                "prs_score": 0.0,
                "percentile": 50.0,
                "snps_used": 0,
                "total_snps": 0,
            })

    return results


def _percentile_to_risk_level(percentile: float) -> str:
    """Map a percentile value to a human-readable risk tier."""
    if percentile >= 95:
        return "Very High"
    elif percentile >= 80:
        return "High"
    elif percentile >= 60:
        return "Above Average"
    elif percentile >= 40:
        return "Average"
    elif percentile >= 20:
        return "Below Average"
    else:
        return "Low"


def _run_ancestry_inference(df: pd.DataFrame) -> dict:
    """Attempt ancestry inference and return a result dict."""
    if AncestryInference is None:
        return {"success": False, "error": "Ancestry inference module unavailable"}
    try:
        inference = AncestryInference()
        result = inference.infer_ancestry(df, method="pca")
        return result
    except Exception as exc:
        logger.error("Ancestry inference failed: %s", exc)
        return {"success": False, "error": str(exc)}


def _run_wellness_analysis(df: pd.DataFrame) -> list:
    """Run comprehensive wellness SNP analysis and return list of trait dicts."""
    if analyze_wellness_snps is None:
        return []
    try:
        raw = analyze_wellness_snps(df)
        traits = []
        for rsid, info in raw.items():
            genotype = info.get("genotype", "Not Found")
            interp_map = info.get("interp", {})
            sorted_gt = "".join(sorted(genotype)) if genotype and genotype != "Not Found" else genotype
            interpretation = interp_map.get(genotype) or interp_map.get(sorted_gt, "No interpretation")
            traits.append({
                "rsid": rsid,
                "trait": info.get("name", "Unknown"),
                "gene": info.get("gene", "Unknown"),
                "genotype": genotype,
                "interpretation": interpretation,
                "category": info.get("category", "General"),
            })
        return traits
    except Exception as exc:
        logger.error("Wellness analysis failed: %s", exc)
        return []


def _run_acmg_analysis(df: pd.DataFrame) -> list:
    """Screen for ACMG secondary findings."""
    if get_acmg_sf_variants is None:
        return []
    try:
        acmg_snps = get_acmg_sf_variants()
        results = []
        for rsid, info in acmg_snps.items():
            try:
                genotype = df.loc[rsid, "genotype"]
                if genotype not in ("Not in data", "00", "--"):
                    results.append({
                        "rsid": rsid,
                        "gene": info.get("gene", "Unknown"),
                        "condition": info.get("condition", "Unknown"),
                        "genotype": genotype,
                    })
            except KeyError:
                continue
        return results
    except Exception as exc:
        logger.error("ACMG analysis failed: %s", exc)
        return []


def _enrich_with_evidence(records: list, record_type: str) -> list:
    """
    Enrich variant records with evidence from MyVariant.info, Ensembl VEP,
    and gnomAD. Adds ClinVar significance, gnomAD allele frequency, CADD score,
    and proper evidence-based classification.
    """
    if not records:
        return records

    # Extract rsIDs and genotypes
    rsids = []
    genotypes = {}
    for r in records:
        rsid = r.get("rsID") or r.get("rsid") or r.get("index")
        if rsid and isinstance(rsid, str) and rsid.startswith("rs"):
            rsids.append(rsid)
            genotypes[rsid] = r.get("Genotype") or r.get("genotype", "")

    if not rsids:
        return records

    try:
        evidence = classify_variants_batch(rsids, genotypes)
    except Exception as exc:
        logger.error("Evidence enrichment failed: %s", exc)
        return records

    # Merge evidence into records
    enriched = []
    for r in records:
        rsid = r.get("rsID") or r.get("rsid") or r.get("index")
        ev = evidence.get(rsid, {})

        r["clinvar_significance"] = ev.get("clinvar_significance")
        r["clinvar_stars"] = ev.get("clinvar_stars", 0)
        r["clinvar_conditions"] = ev.get("clinvar_conditions", [])
        r["gnomad_af"] = ev.get("gnomad_af")
        r["cadd_phred"] = ev.get("cadd_phred")
        r["impact_level"] = ev.get("impact_level", "MODIFIER")
        r["sift"] = ev.get("sift")
        r["polyphen"] = ev.get("polyphen")
        r["evidence_classification"] = ev.get("classification", "unknown")
        r["evidence_level"] = ev.get("evidence_level", "insufficient")
        r["is_actionable"] = ev.get("is_actionable", False)

        # Fix carrier screening: mark as carrier only if variant is actually pathogenic/LP
        if record_type == "carrier":
            classification = ev.get("classification", "unknown")
            gnomad_af = ev.get("gnomad_af")
            if classification in ("benign", "likely_benign"):
                r["Status"] = "Normal (Benign)"
                r["is_actionable"] = False
            elif gnomad_af is not None and gnomad_af > 0.05:
                r["Status"] = "Common Variant (Not Carrier)"
                r["is_actionable"] = False

        # Fix high-impact: reclassify based on evidence
        if record_type == "high_impact":
            classification = ev.get("classification", "unknown")
            gnomad_af = ev.get("gnomad_af")
            if classification == "benign" or (gnomad_af is not None and gnomad_af > 0.05):
                r["Interpretation"] = f"Common polymorphism (AF={gnomad_af:.2%}). Likely benign."
                r["is_actionable"] = False
            elif classification == "likely_benign":
                r["Interpretation"] = "Likely benign based on ClinVar and population frequency data."
                r["is_actionable"] = False
            elif classification == "pathogenic":
                r["Interpretation"] = f"PATHOGENIC (ClinVar {ev.get('clinvar_stars', 0)}-star). Consult genetic counselor."
                r["is_actionable"] = True
            elif classification == "likely_pathogenic":
                r["Interpretation"] = "Likely pathogenic. Genetic counseling recommended."
                r["is_actionable"] = True
            elif classification == "vus":
                r["Interpretation"] = "Variant of uncertain significance (VUS). Monitor for reclassification."
                r["is_actionable"] = False

        enriched.append(r)

    return enriched


def _enrich_prs_with_real_stats(prs_results: list, df: pd.DataFrame, ancestry_result: dict) -> list:
    """
    Re-calculate PRS percentiles using real gnomAD allele frequencies
    instead of the fabricated population statistics.
    """
    if not prs_results or get_prs_models is None:
        return prs_results

    # Determine ancestry for population-specific frequencies
    ancestry = "EUR"  # default
    if isinstance(ancestry_result, dict) and ancestry_result.get("success"):
        primary = (ancestry_result.get("primary_ancestry") or "").upper()
        if primary in ("AFR", "AMR", "EAS", "EUR", "SAS"):
            ancestry = primary
        elif "EUROPEAN" in primary:
            ancestry = "EUR"
        elif "AFRICAN" in primary:
            ancestry = "AFR"
        elif "ASIAN" in primary:
            ancestry = "EAS"

    try:
        all_models = get_prs_models()
    except Exception:
        return prs_results

    enriched = []
    for result in prs_results:
        if not result.get("success"):
            enriched.append(result)
            continue

        condition = result.get("condition", "")
        model_info = all_models.get(condition, {})
        simple_model = model_info.get("simple_model")

        if simple_model:
            try:
                model_rsids = simple_model.get("rsid", [])
                effect_alleles = dict(zip(model_rsids, simple_model.get("effect_allele", [])))
                effect_weights = dict(zip(model_rsids, simple_model.get("effect_weight", [])))

                pop_mean, pop_std = get_prs_population_stats(
                    model_rsids, effect_alleles, effect_weights, ancestry
                )

                if pop_std > 0:
                    prs_score = result.get("prs_score", 0)
                    z_score = (prs_score - pop_mean) / pop_std
                    from scipy.stats import norm
                    percentile = norm.cdf(z_score) * 100
                    percentile = max(0.1, min(99.9, percentile))

                    result["percentile"] = round(percentile, 2)
                    result["normalized_score"] = round(z_score, 3)
                    result["risk_level"] = _percentile_to_risk_level(percentile)
                    result["population_stats"] = {
                        "ancestry": ancestry,
                        "population_mean": round(pop_mean, 4),
                        "population_std": round(pop_std, 4),
                        "method": "gnomad_allele_frequencies",
                    }
            except ImportError:
                # scipy not available, use existing numpy approach
                pass
            except Exception as exc:
                logger.error("PRS enrichment failed for %s: %s", condition, exc)

        enriched.append(result)

    return enriched


def _run_full_analysis(df: pd.DataFrame) -> tuple:
    """Run the complete analysis pipeline and return (data_payload, summary)."""
    # 1. ClinVar pathogenic variants
    clinvar_tsv = os.path.join(_ROOT_DIR, "clinvar_pathogenic_variants.tsv")
    clinvar_records = []
    try:
        clinvar_df = analyze_clinvar_variants(df, clinvar_tsv)
        clinvar_records = _dataframe_to_records(clinvar_df)
    except Exception as exc:
        logger.error("ClinVar analysis failed: %s", exc)

    # 2. High-impact risks
    high_impact_records = []
    try:
        high_impact_df = analyze_high_impact_risks(df)
        high_impact_records = _dataframe_to_records(high_impact_df)
    except Exception as exc:
        logger.error("High-impact analysis failed: %s", exc)

    # 3. Expanded carrier screening
    carrier_records = []
    try:
        carrier_df = analyze_expanded_carrier_status(df)
        carrier_records = _dataframe_to_records(carrier_df)
    except Exception as exc:
        logger.error("Carrier status analysis failed: %s", exc)

    # 4. PGx & basic wellness
    pgx_records = []
    basic_wellness_records = []
    try:
        pgx_df, wellness_df = analyze_pgx_and_wellness(df)
        pgx_records = _dataframe_to_records(pgx_df)
        basic_wellness_records = _dataframe_to_records(wellness_df)
    except Exception as exc:
        logger.error("PGx/wellness analysis failed: %s", exc)

    # 5. Comprehensive wellness
    wellness_traits = _run_wellness_analysis(df)

    # 6. PRS
    prs_results = _run_prs_analysis(df)

    # 7. Ancestry inference
    ancestry_result = _run_ancestry_inference(df)

    # 8. ACMG secondary findings
    acmg_results = _run_acmg_analysis(df)

    # 9. Evidence-based enrichment using free APIs
    #    Annotates high-impact and carrier variants with ClinVar, gnomAD, CADD, VEP data
    if EVIDENCE_AVAILABLE:
        high_impact_records = _enrich_with_evidence(high_impact_records, "high_impact")
        carrier_records = _enrich_with_evidence(carrier_records, "carrier")
        prs_results = _enrich_prs_with_real_stats(prs_results, df, ancestry_result)

    data_payload = {
        "clinvar": clinvar_records,
        "high_impact": high_impact_records,
        "carrier": carrier_records,
        "pharmacogenomics": pgx_records,
        "wellness_basic": basic_wellness_records,
        "wellness_traits": wellness_traits,
        "prs": prs_results,
        "ancestry": ancestry_result,
        "acmg": acmg_results,
    }

    summary = AnalysisSummary(
        snps_analyzed=len(df),
        pathogenic_variants=len(clinvar_records),
        high_impact_variants=len(high_impact_records),
        carrier_variants=len(carrier_records),
        pgx_variants=len(pgx_records),
        wellness_traits=len(wellness_traits),
        prs_conditions=len([r for r in prs_results if r.get("success")]),
    )

    return data_payload, summary


# ---------------------------------------------------------------------------
# Main upload endpoint
# ---------------------------------------------------------------------------

@router.post(
    "/analysis/process-dna",
    response_model=AnalysisResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Upload and process a DNA file",
)
async def process_dna(
    file: UploadFile = File(...),
    genome_build: str = Form("GRCh37"),
    file_format: Optional[str] = Form(None),
    person_name: Optional[str] = Form(None),
):
    try:
        content = await file.read()
        content_str = content.decode("utf-8")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read uploaded file: {exc}")

    df = _parse_dna_upload(content_str, genome_build)
    logger.info("Parsed %d SNPs from uploaded file.", len(df))

    data_payload, summary = _run_full_analysis(df)

    # Include person name in stored data
    store_data = {
        "summary": summary.model_dump(),
        "person_name": person_name or file.filename or "Unknown",
        "filename": file.filename,
        **data_payload,
    }
    analysis_id = analysis_store.save(store_data)

    logger.info("Analysis complete. analysis_id=%s", analysis_id)

    return AnalysisResponse(
        status="success",
        analysis_id=analysis_id,
        summary=summary,
        data=data_payload,
    )


# ---------------------------------------------------------------------------
# Session & full results
# ---------------------------------------------------------------------------

@router.get(
    "/analysis/session/{analysis_id}",
    response_model=AnalysisSessionInfo,
    responses={404: {"model": ErrorResponse}},
    summary="Get session metadata for an analysis",
)
async def get_session(analysis_id: str):
    info = analysis_store.get_session_info(analysis_id)
    if info is None:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis session '{analysis_id}' not found or has expired.",
        )
    return AnalysisSessionInfo(**info)


@router.get(
    "/analysis/results/{analysis_id}",
    summary="Get full cached analysis results",
)
async def get_full_results(analysis_id: str):
    data = _get_cached_data(analysis_id)
    return {
        "analysis_id": analysis_id,
        "person_name": data.get("person_name", "Unknown"),
        "summary": data.get("summary", {}),
        "data": {
            "clinvar": data.get("clinvar", []),
            "high_impact": data.get("high_impact", []),
            "carrier": data.get("carrier", []),
            "pharmacogenomics": data.get("pharmacogenomics", []),
            "wellness_basic": data.get("wellness_basic", []),
            "wellness_traits": data.get("wellness_traits", []),
            "prs": data.get("prs", []),
            "ancestry": data.get("ancestry", {}),
            "acmg": data.get("acmg", []),
        },
    }


# ---------------------------------------------------------------------------
# Clinical endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/clinical/risks/{analysis_id}",
    summary="Get clinical risk variants",
)
async def get_clinical_risks(analysis_id: str):
    data = _get_cached_data(analysis_id)
    clinvar = data.get("clinvar", [])
    high_impact = data.get("high_impact", [])

    # Categorize high-impact by risk level
    high_risk = [v for v in high_impact if "cancer" in str(v.get("Associated Risk", "")).lower()
                 or "BRCA" in str(v.get("Gene/Locus", ""))]
    moderate_risk = [v for v in high_impact if v not in high_risk]

    return {
        "analysis_id": analysis_id,
        "variants": clinvar + high_impact,
        "summary": {
            "total": len(clinvar) + len(high_impact),
            "high_risk": len(high_risk) + len(clinvar),
            "moderate_risk": len(moderate_risk),
            "low_risk": 0,
        },
    }


@router.get(
    "/clinical/carrier-status/{analysis_id}",
    summary="Get carrier screening results",
)
async def get_carrier_status(analysis_id: str):
    data = _get_cached_data(analysis_id)
    carrier = data.get("carrier", [])
    carrier_count = sum(1 for v in carrier if "detected" in str(v.get("Status", "")).lower())

    return {
        "analysis_id": analysis_id,
        "variants": carrier,
        "summary": {
            "total_screened": len(carrier),
            "carrier_count": carrier_count,
        },
    }


@router.get(
    "/clinical/cancer-risk/{analysis_id}",
    summary="Get cancer-specific risk variants",
)
async def get_cancer_risk(analysis_id: str):
    data = _get_cached_data(analysis_id)
    high_impact = data.get("high_impact", [])
    cancer_keywords = ["cancer", "melanoma", "brca", "lynch", "neoplasia", "li-fraumeni", "gastric"]
    cancer_variants = [
        v for v in high_impact
        if any(kw in str(v.get("Associated Risk", "")).lower() for kw in cancer_keywords)
        or any(kw in str(v.get("Gene/Locus", "")).lower() for kw in ["brca1", "brca2", "msh2", "tp53"])
    ]

    return {
        "analysis_id": analysis_id,
        "variants": cancer_variants,
        "summary": {
            "total": len(cancer_variants),
            "high_risk": len([v for v in cancer_variants if "brca" in str(v.get("Gene/Locus", "")).lower()]),
            "moderate_risk": len(cancer_variants) - len([v for v in cancer_variants if "brca" in str(v.get("Gene/Locus", "")).lower()]),
        },
    }


@router.get(
    "/clinical/acmg-findings/{analysis_id}",
    summary="Get ACMG secondary findings",
)
async def get_acmg_findings(analysis_id: str):
    data = _get_cached_data(analysis_id)
    return {
        "analysis_id": analysis_id,
        "acmg_variants": data.get("acmg", []),
    }


# ---------------------------------------------------------------------------
# Pharmacogenomics endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/pgx/report/{analysis_id}",
    summary="Get pharmacogenomics report",
)
async def get_pgx_report(analysis_id: str):
    data = _get_cached_data(analysis_id)
    pgx = data.get("pharmacogenomics", [])

    # Count actionable results
    actionable = sum(1 for v in pgx if v.get("Interpretation") and v.get("Interpretation") != "Normal Metabolizer")
    genes = set(v.get("Gene", "") for v in pgx if v.get("Gene"))

    return {
        "analysis_id": analysis_id,
        "results": pgx,
        "summary": {
            "total_genes": len(genes),
            "actionable": actionable,
        },
    }


# ---------------------------------------------------------------------------
# PRS endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/prs/scores/{analysis_id}",
    summary="Get polygenic risk scores",
)
async def get_prs_scores(analysis_id: str):
    data = _get_cached_data(analysis_id)
    prs = data.get("prs", [])

    successful = [r for r in prs if r.get("success", False)]
    high_risk = sum(1 for r in successful if r.get("percentile", 50) >= 80)
    moderate_risk = sum(1 for r in successful if 60 <= r.get("percentile", 50) < 80)

    return {
        "analysis_id": analysis_id,
        "conditions": prs,
        "summary": {
            "total_conditions": len(successful),
            "high_risk": high_risk,
            "moderate_risk": moderate_risk,
        },
    }


# ---------------------------------------------------------------------------
# Wellness & Ancestry endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/wellness/traits/{analysis_id}",
    summary="Get wellness trait results",
)
async def get_wellness_traits(analysis_id: str):
    data = _get_cached_data(analysis_id)
    traits = data.get("wellness_traits", [])
    basic = data.get("wellness_basic", [])

    # Merge basic wellness into traits if not already there
    all_traits = list(traits)
    existing_rsids = {t.get("rsid") for t in all_traits}
    for b in basic:
        rsid = b.get("rsID") or b.get("rsid") or b.get("index")
        if rsid and rsid not in existing_rsids:
            all_traits.append({
                "rsid": rsid,
                "trait": b.get("Trait") or b.get("trait", "Unknown"),
                "gene": b.get("Gene") or b.get("gene", ""),
                "genotype": b.get("Genotype") or b.get("genotype", ""),
                "interpretation": b.get("Interpretation") or b.get("interpretation", ""),
                "category": b.get("category", "General"),
            })

    categories = list(set(t.get("category", "General") for t in all_traits))

    return {
        "analysis_id": analysis_id,
        "traits": all_traits,
        "summary": {
            "total_traits": len(all_traits),
            "categories": categories,
        },
    }


@router.get(
    "/wellness/ancestry/{analysis_id}",
    summary="Get ancestry inference results",
)
async def get_ancestry(analysis_id: str):
    data = _get_cached_data(analysis_id)
    ancestry = data.get("ancestry", {})

    return {
        "analysis_id": analysis_id,
        "ancestry": ancestry,
    }


# ---------------------------------------------------------------------------
# Family comparison endpoint
# ---------------------------------------------------------------------------

@router.post(
    "/analysis/family-compare",
    summary="Compare two DNA files for family relationship analysis",
)
async def family_compare(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    person1_name: str = Form("Person 1"),
    person2_name: str = Form("Person 2"),
    genome_build: str = Form("GRCh37"),
):
    if FamilyAnalyzer is None:
        raise HTTPException(status_code=500, detail="Family analysis module not available.")

    # Parse both files
    try:
        content1 = (await file1.read()).decode("utf-8")
        content2 = (await file2.read()).decode("utf-8")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read uploaded files: {exc}")

    df1 = _parse_dna_upload(content1, genome_build)
    df2 = _parse_dna_upload(content2, genome_build)

    logger.info("Parsed %d SNPs for %s, %d SNPs for %s", len(df1), person1_name, len(df2), person2_name)

    # Run family analysis
    analyzer = FamilyAnalyzer(df1, df2, label1=person1_name, label2=person2_name)
    ibs_score = analyzer.calculate_identity_by_state()
    relationship = analyzer.predict_relationship(ibs_score)
    mendelian = analyzer.analyze_mendelian_errors()

    # Run individual analyses for both
    data1, summary1 = _run_full_analysis(df1)
    data2, summary2 = _run_full_analysis(df2)

    # Find shared risk variants
    shared_variants = _find_shared_variants(data1, data2)

    # Cache person 1 results
    id1 = analysis_store.save({
        "summary": summary1.model_dump(),
        "person_name": person1_name,
        **data1,
    })
    # Cache person 2 results
    id2 = analysis_store.save({
        "summary": summary2.model_dump(),
        "person_name": person2_name,
        **data2,
    })

    # Build comparison payload
    comparison = {
        "person1": {
            "name": person1_name,
            "analysis_id": id1,
            "snps_analyzed": summary1.snps_analyzed,
            "summary": summary1.model_dump(),
        },
        "person2": {
            "name": person2_name,
            "analysis_id": id2,
            "snps_analyzed": summary2.snps_analyzed,
            "summary": summary2.model_dump(),
        },
        "relationship": {
            "ibs_score": round(ibs_score, 4),
            "ibs_percentage": round(ibs_score * 100, 2),
            "predicted_relationship": relationship,
            "common_snps": len(analyzer.common_snps),
        },
        "mendelian_analysis": {
            "total_comparisons": mendelian["total_comparisons"],
            "mendelian_errors": mendelian["mendelian_errors"],
            "error_rate": round(mendelian["error_rate"], 4),
            "error_rate_percentage": round(mendelian["error_rate"] * 100, 2),
            "is_parent_child": mendelian["is_parent_child"],
        },
        "shared_variants": shared_variants,
        "prs_comparison": _compare_prs(data1.get("prs", []), data2.get("prs", []), person1_name, person2_name),
    }

    # Cache comparison results
    comparison_id = analysis_store.save({
        "type": "family_comparison",
        "comparison": comparison,
        "person1_id": id1,
        "person2_id": id2,
    })

    return {
        "status": "success",
        "comparison_id": comparison_id,
        "person1_analysis_id": id1,
        "person2_analysis_id": id2,
        **comparison,
    }


def _find_shared_variants(data1: dict, data2: dict) -> dict:
    """Find variants that both people share."""
    shared = {
        "shared_high_impact": [],
        "shared_carrier": [],
        "shared_pgx": [],
    }

    # Shared high-impact variants
    rsids1 = {v.get("rsID") for v in data1.get("high_impact", [])}
    for v in data2.get("high_impact", []):
        if v.get("rsID") in rsids1:
            shared["shared_high_impact"].append(v)

    # Shared carrier variants
    rsids1 = {v.get("rsID") for v in data1.get("carrier", [])}
    for v in data2.get("carrier", []):
        if v.get("rsID") in rsids1:
            shared["shared_carrier"].append(v)

    # Shared PGx variants
    rsids1 = {v.get("rsID") or v.get("rsid") for v in data1.get("pharmacogenomics", [])}
    for v in data2.get("pharmacogenomics", []):
        rsid = v.get("rsID") or v.get("rsid")
        if rsid in rsids1:
            shared["shared_pgx"].append(v)

    return shared


def _compare_prs(prs1: list, prs2: list, name1: str, name2: str) -> list:
    """Compare PRS scores between two people."""
    prs_map1 = {r["condition"]: r for r in prs1 if r.get("success")}
    prs_map2 = {r["condition"]: r for r in prs2 if r.get("success")}

    comparisons = []
    all_conditions = set(list(prs_map1.keys()) + list(prs_map2.keys()))

    for condition in sorted(all_conditions):
        r1 = prs_map1.get(condition, {})
        r2 = prs_map2.get(condition, {})
        comparisons.append({
            "condition": condition,
            f"{name1}_percentile": r1.get("percentile", None),
            f"{name1}_risk_level": r1.get("risk_level", "N/A"),
            f"{name2}_percentile": r2.get("percentile", None),
            f"{name2}_risk_level": r2.get("risk_level", "N/A"),
        })

    return comparisons


# ---------------------------------------------------------------------------
# PDF Report endpoint
# ---------------------------------------------------------------------------

@router.get(
    "/analysis/report/{analysis_id}",
    summary="Generate and download PDF report",
)
async def generate_report(analysis_id: str):
    data = _get_cached_data(analysis_id)

    try:
        from src.pdf_generator.main import generate_pdf_report
        report_path = os.path.join(tempfile.gettempdir(), f"genomic_report_{analysis_id}.pdf")
        generate_pdf_report(data, report_path)
        return FileResponse(
            report_path,
            media_type="application/pdf",
            filename=f"genomic_report_{data.get('person_name', 'unknown')}.pdf",
        )
    except Exception as exc:
        logger.error("PDF generation failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {exc}")
