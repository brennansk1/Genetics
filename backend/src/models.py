"""
Pydantic models for the Genomic Health Dashboard API.

All request bodies, response bodies, and shared data structures are defined
here so that FastAPI can auto-generate accurate OpenAPI docs and perform
runtime validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shared / Reusable schemas
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    """Standard error envelope returned by all endpoints on failure."""

    detail: str = Field(..., description="Human-readable error message")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class VariantBase(BaseModel):
    """Core fields present on every genomic variant."""

    rsid: str = Field(..., description="The dbSNP rsID identifier (e.g. rs1801133)")
    chromosome: Optional[str] = Field(None, description="Chromosome containing the variant")
    position: Optional[int] = Field(None, description="Genomic position of the variant")
    genotype: str = Field(..., description="Observed diploid genotype (e.g. 'AG')")


class VariantInterpretation(BaseModel):
    """Interpretation of a single variant with respect to a clinical or wellness trait."""

    rsid: Optional[str] = None
    genotype: str
    interpretation: str
    condition: Optional[str] = None
    risk_level: Optional[str] = None
    trait: Optional[str] = None


# ---------------------------------------------------------------------------
# DNA upload
# ---------------------------------------------------------------------------

class DNADataUpload(BaseModel):
    """Metadata for a DNA file upload request (when not using multipart form)."""

    file_format: str = Field(
        ..., description="Format of the uploaded file (e.g. '23andMe', 'AncestryDNA')"
    )
    file_content: bytes = Field(..., description="Raw file contents")


class AnalysisSessionInfo(BaseModel):
    """Lightweight metadata returned after a successful upload."""

    analysis_id: str = Field(..., description="UUID used to retrieve cached results")
    created_at: str
    expires_at: str
    sections: List[str] = Field(
        ..., description="List of analysis section keys available"
    )


# ---------------------------------------------------------------------------
# Analysis summary
# ---------------------------------------------------------------------------

class AnalysisSummary(BaseModel):
    """High-level statistics about a completed analysis run."""

    snps_analyzed: int = Field(0, description="Total SNPs parsed from the uploaded file")
    pathogenic_variants: int = Field(
        0, description="Count of ClinVar pathogenic / likely pathogenic matches"
    )
    high_impact_variants: int = Field(
        0, description="Count of high-impact risk variants detected"
    )
    carrier_variants: int = Field(
        0, description="Count of carrier screening variants detected"
    )
    pgx_variants: int = Field(
        0, description="Count of pharmacogenomics variants analyzed"
    )
    wellness_traits: int = Field(
        0, description="Count of wellness traits analyzed"
    )
    prs_conditions: int = Field(
        0, description="Number of PRS conditions computed"
    )


# ---------------------------------------------------------------------------
# Clinical results
# ---------------------------------------------------------------------------

class ClinVarVariant(BaseModel):
    """A single ClinVar pathogenic variant match."""

    rsid: str
    chromosome: Optional[str] = None
    position: Optional[int] = None
    genotype: Optional[str] = None
    clinical_significance: Optional[str] = Field(None, alias="CLNSIG")
    gene: Optional[str] = None
    condition: Optional[str] = None


class HighImpactVariant(BaseModel):
    """A high-impact risk variant detected in the user's data."""

    rsid: str = Field(..., alias="rsID")
    gene: Optional[str] = Field(None, alias="Gene/Locus")
    associated_risk: Optional[str] = Field(None, alias="Associated Risk")
    genotype: Optional[str] = Field(None, alias="Genotype")
    interpretation: Optional[str] = Field(None, alias="Interpretation")

    model_config = {"populate_by_name": True}


class CarrierVariant(BaseModel):
    """A variant detected via expanded carrier screening."""

    rsid: str = Field(..., alias="rsID")
    gene: Optional[str] = Field(None, alias="Gene")
    condition: Optional[str] = Field(None, alias="Condition")
    genotype: Optional[str] = Field(None, alias="Genotype")
    status: Optional[str] = Field(None, alias="Status")

    model_config = {"populate_by_name": True}


class ClinicalRisksResponse(BaseModel):
    """Response payload for GET /clinical/risks/{analysis_id}."""

    analysis_id: str
    clinvar_variants: List[Dict[str, Any]] = []
    high_impact_variants: List[Dict[str, Any]] = []
    summary: Optional[AnalysisSummary] = None


class CarrierStatusResponse(BaseModel):
    """Response payload for GET /clinical/carrier-status/{analysis_id}."""

    analysis_id: str
    carrier_variants: List[Dict[str, Any]] = []
    note: str = (
        "SMA carrier status requires clinical-grade CNV analysis and cannot be "
        "reliably determined from consumer DNA tests."
    )


class CancerRiskResponse(BaseModel):
    """Response payload for GET /clinical/cancer-risk/{analysis_id}."""

    analysis_id: str
    cancer_variants: List[Dict[str, Any]] = []
    brca_note: str = (
        "BRCA mutations also significantly increase the risk of prostate cancer, "
        "pancreatic cancer, and male breast cancer."
    )


class ACMGFindingsResponse(BaseModel):
    """Response payload for GET /clinical/acmg-findings/{analysis_id}."""

    analysis_id: str
    acmg_variants: List[Dict[str, Any]] = []


# ---------------------------------------------------------------------------
# Pharmacogenomics
# ---------------------------------------------------------------------------

class PGxResult(BaseModel):
    """Single pharmacogenomics variant result."""

    rsid: Optional[str] = None
    gene: Optional[str] = None
    relevance: Optional[str] = None
    genotype: Optional[str] = None
    interpretation: Optional[str] = None
    phenotype: Optional[str] = None
    diplotype: Optional[str] = None
    recommendation: Optional[str] = None


class DrugInteraction(BaseModel):
    """A drug interaction detected through PGx analysis."""

    drug: str
    gene: str
    phenotype: str
    details: List[Dict[str, Any]] = []
    recommendation: Optional[str] = None


class PGxReportResponse(BaseModel):
    """Response payload for GET /pgx/report/{analysis_id}."""

    analysis_id: str
    pgx_variants: List[Dict[str, Any]] = []


class DrugInteractionsResponse(BaseModel):
    """Response payload for GET /pgx/drug-interactions/{analysis_id}."""

    analysis_id: str
    drug_gene_interactions: List[Dict[str, Any]] = []
    drug_drug_interactions: List[Dict[str, Any]] = []


# ---------------------------------------------------------------------------
# Polygenic Risk Scores
# ---------------------------------------------------------------------------

class PRSResult(BaseModel):
    """Polygenic risk score result for a single condition."""

    condition: str = Field(..., description="Condition name (e.g. 'Coronary Artery Disease')")
    prs_score: float = Field(0.0, description="Raw PRS score")
    normalized_score: Optional[float] = Field(None, description="Z-score normalised PRS")
    percentile: float = Field(50.0, description="Percentile rank in reference population (0-100)")
    snps_used: int = Field(0, description="Number of model SNPs present in user data")
    total_snps: int = Field(0, description="Total SNPs in the PRS model")
    coverage: float = Field(0.0, description="Fraction of model SNPs found (0.0 - 1.0)")
    risk_level: Optional[str] = Field(None, description="Qualitative risk tier")
    model_type: Optional[str] = Field(None, description="'simple' or 'genomewide'")
    success: bool = True
    error: Optional[str] = None


class PRSScoresResponse(BaseModel):
    """Response payload for GET /prs/scores/{analysis_id}."""

    analysis_id: str
    scores: List[PRSResult] = []
    conditions_available: List[str] = []


class PRSSingleScoreResponse(BaseModel):
    """Response payload for GET /prs/score/{analysis_id}/{condition}."""

    analysis_id: str
    result: Optional[PRSResult] = None


class LifetimeRiskResult(BaseModel):
    """Result of a lifetime risk projection for a condition."""

    condition: str
    current_age: Optional[int] = None
    sex: Optional[str] = None
    lifetime_risk: Optional[float] = None
    risk_level: Optional[str] = None
    interpretation: Optional[str] = None
    confidence_interval: Optional[str] = None
    scenarios: Optional[Dict[str, float]] = None
    success: bool = True
    error: Optional[str] = None


class LifetimeRiskResponse(BaseModel):
    """Response payload for GET /prs/lifetime-risk/{analysis_id}/{condition}."""

    analysis_id: str
    result: Optional[LifetimeRiskResult] = None


# ---------------------------------------------------------------------------
# Wellness & Ancestry
# ---------------------------------------------------------------------------

class WellnessTraitResult(BaseModel):
    """A single wellness / trait analysis result."""

    rsid: Optional[str] = None
    trait: Optional[str] = None
    gene: Optional[str] = None
    genotype: Optional[str] = None
    interpretation: Optional[str] = None


class WellnessTraitsResponse(BaseModel):
    """Response payload for GET /wellness/traits/{analysis_id}."""

    analysis_id: str
    traits: List[Dict[str, Any]] = []


class AncestryResult(BaseModel):
    """Ancestry inference result."""

    primary_ancestry: Optional[str] = None
    confidence: Optional[float] = None
    probabilities: Optional[Dict[str, float]] = None
    admixture_proportions: Optional[Dict[str, float]] = None
    method: Optional[str] = None
    snps_used: Optional[int] = None
    success: bool = True
    error: Optional[str] = None


class AncestryResponse(BaseModel):
    """Response payload for GET /wellness/ancestry/{analysis_id}."""

    analysis_id: str
    ancestry: Optional[AncestryResult] = None


# ---------------------------------------------------------------------------
# Top-level analysis response (returned from POST /analysis/process-dna)
# ---------------------------------------------------------------------------

class AnalysisResponse(BaseModel):
    """
    Full analysis result returned after uploading and processing a DNA file.

    Contains the analysis_id that subsequent GET endpoints use, along with a
    summary and the complete data payload.
    """

    status: str = Field("success", description="'success' or 'error'")
    analysis_id: str = Field(..., description="UUID for retrieving cached results")
    summary: AnalysisSummary
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Nested dict containing all analysis section results",
    )


# ---------------------------------------------------------------------------
# Clinical report (legacy compat)
# ---------------------------------------------------------------------------

class ClinicalReportResponse(BaseModel):
    """Legacy clinical report response format."""

    user_id: str
    recessive_carrier_findings: List[VariantInterpretation] = []
    hereditary_cancer_risk: List[VariantInterpretation] = []
    cardiovascular_risk: List[VariantInterpretation] = []
