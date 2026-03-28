// ---------------------------------------------------------------------------
// Genomic Health Dashboard -- Typed API Client
// ---------------------------------------------------------------------------

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ---------------------------------------------------------------------------
// Response Interfaces
// ---------------------------------------------------------------------------

export interface AnalysisResponse {
  status: string;
  analysis_id: string;
  summary: AnalysisSummary;
  data: Record<string, unknown>;
}

export interface AnalysisSummary {
  snps_analyzed: number;
  pathogenic_variants: number;
  high_impact_variants: number;
  carrier_variants: number;
  pgx_variants: number;
  wellness_traits: number;
  prs_conditions: number;
}

export interface FullResults {
  analysis_id: string;
  person_name: string;
  summary: AnalysisSummary;
  data: {
    clinvar: Record<string, unknown>[];
    high_impact: Record<string, unknown>[];
    carrier: Record<string, unknown>[];
    pharmacogenomics: Record<string, unknown>[];
    wellness_basic: Record<string, unknown>[];
    wellness_traits: WellnessTrait[];
    prs: PRSCondition[];
    ancestry: AncestryResult;
    acmg: Record<string, unknown>[];
  };
}

// -- Clinical -----------------------------------------------------------

export interface ClinicalData {
  analysis_id: string;
  variants: Record<string, unknown>[];
  summary: {
    total: number;
    high_risk: number;
    moderate_risk: number;
    low_risk: number;
  };
}

export interface CarrierData {
  analysis_id: string;
  variants: Record<string, unknown>[];
  summary: {
    total_screened: number;
    carrier_count: number;
  };
}

export interface CancerRiskData {
  analysis_id: string;
  variants: Record<string, unknown>[];
  summary: {
    total: number;
    high_risk: number;
    moderate_risk: number;
  };
}

// -- Pharmacogenomics ---------------------------------------------------

export interface PGxData {
  analysis_id: string;
  results: Record<string, unknown>[];
  summary: {
    total_genes: number;
    actionable: number;
  };
}

// -- Polygenic Risk Scores ----------------------------------------------

export interface PRSCondition {
  condition: string;
  prs_score?: number;
  percentile: number;
  snps_used?: number;
  total_snps?: number;
  risk_level?: string;
  success: boolean;
  error?: string;
}

export interface PRSData {
  analysis_id: string;
  conditions: PRSCondition[];
  summary: {
    total_conditions: number;
    high_risk: number;
    moderate_risk: number;
  };
}

// -- Wellness -----------------------------------------------------------

export interface WellnessTrait {
  rsid?: string;
  trait: string;
  gene?: string;
  genotype?: string;
  interpretation?: string;
  category?: string;
}

export interface WellnessData {
  analysis_id: string;
  traits: WellnessTrait[];
  summary: {
    total_traits: number;
    categories: string[];
  };
}

// -- Ancestry -----------------------------------------------------------

export interface AncestryResult {
  primary_ancestry?: string;
  confidence?: number;
  probabilities?: Record<string, number>;
  method?: string;
  snps_used?: number;
  success: boolean;
  error?: string;
}

export interface AncestryData {
  analysis_id: string;
  ancestry: AncestryResult;
}

// -- Family Comparison --------------------------------------------------

export interface FamilyComparisonResult {
  status: string;
  comparison_id: string;
  person1_analysis_id: string;
  person2_analysis_id: string;
  person1: {
    name: string;
    analysis_id: string;
    snps_analyzed: number;
    summary: AnalysisSummary;
  };
  person2: {
    name: string;
    analysis_id: string;
    snps_analyzed: number;
    summary: AnalysisSummary;
  };
  relationship: {
    ibs_score: number;
    ibs_percentage: number;
    predicted_relationship: string;
    common_snps: number;
  };
  mendelian_analysis: {
    total_comparisons: number;
    mendelian_errors: number;
    error_rate: number;
    error_rate_percentage: number;
    is_parent_child: boolean;
  };
  shared_variants: {
    shared_high_impact: Record<string, unknown>[];
    shared_carrier: Record<string, unknown>[];
    shared_pgx: Record<string, unknown>[];
  };
  prs_comparison: Record<string, unknown>[];
}

// ---------------------------------------------------------------------------
// API Error
// ---------------------------------------------------------------------------

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// ---------------------------------------------------------------------------
// Fetch helper
// ---------------------------------------------------------------------------

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    ...init,
    headers: {
      Accept: "application/json",
      ...init?.headers,
    },
  });

  if (!res.ok) {
    const body = await res.text().catch(() => "Unknown error");
    throw new ApiError(res.status, body);
  }

  return res.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Public API Functions
// ---------------------------------------------------------------------------

/** Upload a DNA file and start analysis. */
export async function uploadDNA(file: File, personName?: string): Promise<AnalysisResponse> {
  const form = new FormData();
  form.append("file", file);
  if (personName) form.append("person_name", personName);

  return apiFetch<AnalysisResponse>("/analysis/process-dna", {
    method: "POST",
    body: form,
  });
}

/** Get full analysis results. */
export async function getFullResults(id: string): Promise<FullResults> {
  return apiFetch<FullResults>(`/analysis/results/${id}`);
}

/** Get clinical risk variants. */
export async function getClinicalRisks(id: string): Promise<ClinicalData> {
  return apiFetch<ClinicalData>(`/clinical/risks/${id}`);
}

/** Get carrier status results. */
export async function getCarrierStatus(id: string): Promise<CarrierData> {
  return apiFetch<CarrierData>(`/clinical/carrier-status/${id}`);
}

/** Get cancer-specific risk results. */
export async function getCancerRisk(id: string): Promise<CancerRiskData> {
  return apiFetch<CancerRiskData>(`/clinical/cancer-risk/${id}`);
}

/** Get pharmacogenomics report. */
export async function getPGxReport(id: string): Promise<PGxData> {
  return apiFetch<PGxData>(`/pgx/report/${id}`);
}

/** Get polygenic risk scores. */
export async function getPRSScores(id: string): Promise<PRSData> {
  return apiFetch<PRSData>(`/prs/scores/${id}`);
}

/** Get wellness traits. */
export async function getWellnessTraits(id: string): Promise<WellnessData> {
  return apiFetch<WellnessData>(`/wellness/traits/${id}`);
}

/** Get ancestry inference. */
export async function getAncestry(id: string): Promise<AncestryData> {
  return apiFetch<AncestryData>(`/wellness/ancestry/${id}`);
}

/** Compare two DNA files for family relationship analysis. */
export async function compareFamilyDNA(
  file1: File,
  file2: File,
  person1Name: string,
  person2Name: string,
): Promise<FamilyComparisonResult> {
  const form = new FormData();
  form.append("file1", file1);
  form.append("file2", file2);
  form.append("person1_name", person1Name);
  form.append("person2_name", person2Name);

  return apiFetch<FamilyComparisonResult>("/analysis/family-compare", {
    method: "POST",
    body: form,
  });
}

/** Get PDF report download URL. */
export function getReportUrl(id: string): string {
  return `${BASE_URL}/analysis/report/${id}`;
}
