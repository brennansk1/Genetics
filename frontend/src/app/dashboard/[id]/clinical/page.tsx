"use client";

import { use, useEffect, useState } from "react";
import {
  getClinicalRisks,
  getCarrierStatus,
  getCancerRisk,
  type ClinicalData,
  type CarrierData,
  type CancerRiskData,
} from "@/lib/api";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function RiskBadge({ level }: { level: string }) {
  const normalized = level?.toLowerCase() ?? "";
  let classes = "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ";
  if (normalized.includes("high") || normalized.includes("pathogenic")) {
    classes += "bg-red-500/20 text-red-400 ring-1 ring-red-500/30";
  } else if (normalized.includes("moderate") || normalized.includes("likely")) {
    classes += "bg-amber-500/20 text-amber-400 ring-1 ring-amber-500/30";
  } else if (normalized.includes("low") || normalized.includes("benign")) {
    classes += "bg-green-500/20 text-green-400 ring-1 ring-green-500/30";
  } else {
    classes += "bg-gray-500/20 text-gray-400 ring-1 ring-gray-500/30";
  }
  return <span className={classes}>{level ?? "Unknown"}</span>;
}

function CarrierBadge({ status }: { status: string }) {
  const normalized = status?.toLowerCase() ?? "";
  let classes = "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ";
  if (normalized.includes("carrier")) {
    classes += "bg-amber-500/20 text-amber-400 ring-1 ring-amber-500/30";
  } else if (normalized.includes("affected") || normalized.includes("homozygous")) {
    classes += "bg-red-500/20 text-red-400 ring-1 ring-red-500/30";
  } else {
    classes += "bg-green-500/20 text-green-400 ring-1 ring-green-500/30";
  }
  return <span className={classes}>{status ?? "Unknown"}</span>;
}

function StatCard({
  label,
  value,
  accent,
}: {
  label: string;
  value: number;
  accent?: "red" | "amber" | "green" | "blue";
}) {
  const colorMap = {
    red: "text-red-400",
    amber: "text-amber-400",
    green: "text-green-400",
    blue: "text-blue-400",
  };
  const valueColor = accent ? colorMap[accent] : "text-white";
  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 px-5 py-4">
      <p className="text-sm text-gray-400">{label}</p>
      <p className={`mt-1 text-2xl font-bold ${valueColor}`}>{value}</p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function ClinicalRiskPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const [clinical, setClinical] = useState<ClinicalData | null>(null);
  const [carrier, setCarrier] = useState<CarrierData | null>(null);
  const [cancer, setCancer] = useState<CancerRiskData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchData() {
      try {
        const [clinicalRes, carrierRes, cancerRes] = await Promise.all([
          getClinicalRisks(id),
          getCarrierStatus(id),
          getCancerRisk(id),
        ]);
        if (cancelled) return;
        setClinical(clinicalRes);
        setCarrier(carrierRes);
        setCancer(cancerRes);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load clinical data");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchData();
    return () => {
      cancelled = true;
    };
  }, [id]);

  // -- Loading / Error states -----------------------------------------------

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-gray-700 border-t-blue-500" />
          <p className="text-sm text-gray-400">Loading clinical data&hellip;</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-6 py-4 text-red-400">
          {error}
        </div>
      </div>
    );
  }

  // -- Render ---------------------------------------------------------------

  return (
    <div className="mx-auto max-w-7xl space-y-8 px-4 py-8 text-gray-100 sm:px-6 lg:px-8">
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white">
          Clinical Risk Assessment
        </h1>
        <p className="mt-1 text-sm text-gray-400">
          Pathogenic variants, carrier screening, and cancer risk analysis
        </p>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard
          label="High-Impact Variants"
          value={clinical?.summary.high_risk ?? 0}
          accent="red"
        />
        <StatCard
          label="Moderate Risk"
          value={clinical?.summary.moderate_risk ?? 0}
          accent="amber"
        />
        <StatCard
          label="Carrier Variants"
          value={carrier?.summary.carrier_count ?? 0}
          accent="amber"
        />
        <StatCard
          label="Cancer Risk Variants"
          value={cancer?.summary.high_risk ?? 0}
          accent="red"
        />
      </div>

      {/* ----------------------------------------------------------------- */}
      {/* Section 1 -- Pathogenic & High-Impact Variants                    */}
      {/* ----------------------------------------------------------------- */}
      <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <h2 className="mb-4 text-xl font-semibold text-white">
          Pathogenic &amp; High-Impact Variants
        </h2>
        {clinical && clinical.variants.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-gray-800 text-xs uppercase tracking-wider text-gray-500">
                  <th className="px-4 py-3">rsID</th>
                  <th className="px-4 py-3">Gene</th>
                  <th className="px-4 py-3">Associated Risk</th>
                  <th className="px-4 py-3">Genotype</th>
                  <th className="px-4 py-3">Interpretation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {clinical.variants.map((v, i) => (
                  <tr
                    key={i}
                    className="transition-colors hover:bg-gray-800/60"
                  >
                    <td className="whitespace-nowrap px-4 py-3 font-mono text-blue-400">
                      {String(v.rsid ?? v.rsID ?? "-")}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 font-medium text-white">
                      {String(v.gene ?? "-")}
                    </td>
                    <td className="px-4 py-3">
                      <RiskBadge level={String(v.risk_level ?? v.significance ?? "-")} />
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 font-mono">
                      {String(v.genotype ?? "-")}
                    </td>
                    <td className="max-w-xs truncate px-4 py-3 text-gray-300">
                      {String(v.interpretation ?? v.clinical_significance ?? "-")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm text-gray-500">
            No pathogenic or high-impact variants detected.
          </p>
        )}
      </section>

      {/* ----------------------------------------------------------------- */}
      {/* Section 2 -- Carrier Screening                                    */}
      {/* ----------------------------------------------------------------- */}
      <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <h2 className="mb-4 text-xl font-semibold text-white">
          Carrier Screening
        </h2>
        {carrier && carrier.variants.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-gray-800 text-xs uppercase tracking-wider text-gray-500">
                  <th className="px-4 py-3">rsID</th>
                  <th className="px-4 py-3">Gene</th>
                  <th className="px-4 py-3">Condition</th>
                  <th className="px-4 py-3">Genotype</th>
                  <th className="px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {carrier.variants.map((v, i) => (
                  <tr
                    key={i}
                    className="transition-colors hover:bg-gray-800/60"
                  >
                    <td className="whitespace-nowrap px-4 py-3 font-mono text-blue-400">
                      {String(v.rsid ?? v.rsID ?? "-")}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 font-medium text-white">
                      {String(v.gene ?? "-")}
                    </td>
                    <td className="px-4 py-3 text-gray-300">
                      {String(v.condition ?? v.disease ?? "-")}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 font-mono">
                      {String(v.genotype ?? "-")}
                    </td>
                    <td className="px-4 py-3">
                      <CarrierBadge status={String(v.carrier_status ?? v.status ?? "-")} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm text-gray-500">
            No carrier variants detected in screened genes.
          </p>
        )}
      </section>

      {/* ----------------------------------------------------------------- */}
      {/* Section 3 -- Cancer Risk Panel                                    */}
      {/* ----------------------------------------------------------------- */}
      <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <h2 className="mb-4 text-xl font-semibold text-white">
          Cancer Risk Panel
        </h2>
        {cancer && cancer.variants.length > 0 ? (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-gray-800 text-xs uppercase tracking-wider text-gray-500">
                    <th className="px-4 py-3">rsID</th>
                    <th className="px-4 py-3">Gene</th>
                    <th className="px-4 py-3">Cancer Type</th>
                    <th className="px-4 py-3">Genotype</th>
                    <th className="px-4 py-3">Risk Level</th>
                    <th className="px-4 py-3">Interpretation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {cancer.variants.map((v, i) => (
                    <tr
                      key={i}
                      className="transition-colors hover:bg-gray-800/60"
                    >
                      <td className="whitespace-nowrap px-4 py-3 font-mono text-blue-400">
                        {String(v.rsid ?? v.rsID ?? "-")}
                      </td>
                      <td className="whitespace-nowrap px-4 py-3 font-medium text-white">
                        {String(v.gene ?? "-")}
                      </td>
                      <td className="px-4 py-3 text-gray-300">
                        {String(v.cancer_type ?? v.condition ?? "-")}
                      </td>
                      <td className="whitespace-nowrap px-4 py-3 font-mono">
                        {String(v.genotype ?? "-")}
                      </td>
                      <td className="px-4 py-3">
                        <RiskBadge level={String(v.risk_level ?? v.significance ?? "-")} />
                      </td>
                      <td className="max-w-xs truncate px-4 py-3 text-gray-300">
                        {String(v.interpretation ?? v.clinical_significance ?? "-")}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* BRCA note */}
            <div className="mt-4 rounded-lg border border-amber-500/20 bg-amber-500/5 px-4 py-3">
              <p className="text-xs leading-relaxed text-amber-300/80">
                <span className="font-semibold text-amber-300">BRCA1/BRCA2 Note:</span>{" "}
                Variants in BRCA1 and BRCA2 genes are associated with significantly
                elevated risk for breast, ovarian, prostate, and pancreatic cancers.
                Pathogenic BRCA variants may warrant referral to a genetic counselor
                for comprehensive risk assessment and management planning. This report
                is not a substitute for professional genetic counseling.
              </p>
            </div>
          </>
        ) : (
          <p className="text-sm text-gray-500">
            No cancer-associated risk variants detected in screened panels.
          </p>
        )}
      </section>

      {/* Disclaimer */}
      <footer className="rounded-xl border border-gray-800 bg-gray-900/50 px-6 py-4">
        <p className="text-xs leading-relaxed text-gray-500">
          <span className="font-semibold text-gray-400">Disclaimer:</span> This
          clinical risk report is for informational and educational purposes only.
          It does not constitute medical advice, diagnosis, or treatment
          recommendations. Always consult a qualified healthcare professional or
          certified genetic counselor before making any medical decisions based on
          genetic data.
        </p>
      </footer>
    </div>
  );
}
